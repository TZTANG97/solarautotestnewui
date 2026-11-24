import re
import time

from PyQt5.QtWidgets import QMessageBox

from .handle_release import release_resource_handle
from .scpi_socket import ScpiSocket
from modbus_visa import ModbusVISA
from scpi_to_modbustcp import ItechTranslator

# 爱科 REG_CONTROL(0x0909)：连续两条控制命令（RUN→吸合、OUTP 断开→待机）同一寄存器不同值，
# 设备内部状态机需时间切换；for 循环若几乎无间隔，后一条可能覆盖前一条仅生效最后一次。
_AC_CONTROL_REG_INTER_CMD_DELAY_SEC = 2

# Chroma 61800 电压设定分辨率约 0.1 V；更细会进错误队列 -222 Data out of range。
_AC_VOLT_RESOLUTION = 0.1


def _normalize_ac_volt_command(command):
    """将 VOLT x.xx 量化到 0.1 V；非 VOLT 命令原样返回。"""
    s = str(command or "").strip()
    m = re.match(r"^(VOLT)\s+(.+)$", s, re.I)
    if not m:
        return s
    v = _fmt_ac_volt_value(m.group(2))
    return "VOLT %s" % v


def _normalize_chroma_ac_write(command):
    """Chroma 61800：裸 VOLT 转 VOLT:AC 并量化到 0.1 V（手册示例 VOLT:AC 110）。"""
    s = str(command or "").strip()
    m = re.match(r"^VOLT(?::AC)?\s+(.+)$", s, re.I)
    if not m:
        return s
    v = _fmt_ac_volt_value(m.group(1))
    return "VOLT:AC %s" % v


def _chroma_volt_write(volt):
    return "VOLT:AC %s" % _fmt_ac_volt_value(volt)


def _chroma_ac_preamble():
    """61800 真机：交流幅值须 CONF:COUP AC，勿用 DC_LEVEL。"""
    return ["CONF:COUP AC"]


def _fmt_ac_volt_value(ac_voltage):
    """UI/设定电压字符串 → 0.1 V 量化后的字符串。"""
    try:
        v = round(float(str(ac_voltage).strip()) / _AC_VOLT_RESOLUTION) * _AC_VOLT_RESOLUTION
        v = round(v, 1)
    except (TypeError, ValueError):
        return str(ac_voltage or "").strip()
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return "%.1f" % v


def _resolve_three_phase_volts(volt_a, volt_b=None, volt_c=None):
    """三相电压：任一相有值则其余空相用该值回填（避免仅填 2/3 相时 NSEL1=0V）。"""
    a = str(volt_a or "").strip()
    b = str(volt_b or "").strip()
    c = str(volt_c or "").strip()
    fallback = a or b or c
    if not fallback:
        return None, None, None
    return a or fallback, b or fallback, c or fallback


def _is_chroma_61800_idn(idn):
    """Chroma 61800 系列（61800/61815/61830/61845/61860 等）走 0.1V 量化与 VOLT:AC 路径。"""
    s = (idn or "").upper()
    if "CHROMA" not in s:
        return False
    return bool(re.search(r"618\d{2}", s))


def _generic_scpi_three_phase_command_list(volt_a, freq, volt_b=None, volt_c=None):
    """非 61800 通用 SCPI 三相（设备页单框）：INST:EDIT ALL + 一次 VOLT/FREQ。"""
    v = str(volt_a or "").strip()
    fr = str(freq or "").strip()
    if not v:
        return []
    return [
        "INST:PHAS THREE",
        "INST:EDIT ALL",
        f"VOLT {v}",
        f"FREQ {fr}",
    ]


def _chroma_three_phase_command_list(volt_a, volt_b, volt_c, freq):
    """Chroma 61800 三相：SAMEFREQ/INDEPEND + EDIT EACH + NSEL + VOLT:AC（真机验证路径）。"""
    ra, rb, rc = _resolve_three_phase_volts(volt_a, volt_b, volt_c)
    if not ra:
        return []
    va = _fmt_ac_volt_value(ra)
    vb = _fmt_ac_volt_value(rb)
    vc = _fmt_ac_volt_value(rc)
    fr = (freq or "").strip()
    mode = "PHAS:THREE SAMEFREQ" if va == vb == vc else "PHAS:THREE INDEPEND"
    out = list(_chroma_ac_preamble())
    out.extend(["INST:PHAS THREE", mode, "INST:EDIT EACH"])
    for nsel, v in ((1, va), (2, vb), (3, vc)):
        out.extend([f"INST:NSEL {nsel}", _chroma_volt_write(v), f"FREQ {fr}"])
    if va == vb == vc:
        out.extend(["INST:EDIT ALL", _chroma_volt_write(va), f"FREQ {fr}"])
    return out


class ACController:
    """交流电源控制器，封装连接、断开、输出和命令发送逻辑。"""

    def __init__(self, logger, show_message, now_to_datenow, ui_setting=None, rm=None, modbus_client_cls=None, configure_scpi_resource=None):
        self.logger = logger
        self.show_message = show_message
        self.now_to_datenow = now_to_datenow
        self.ui_setting = ui_setting
        self.rm = rm
        self.modbus_client_cls = modbus_client_cls
        self.configure_scpi_resource = configure_scpi_resource
        self.handle = None
        self.client = None
        self._itech = None  # 爱科 IP/Modbus：SCPI→寄存器
        self.connected = False
        self.resource = ''
        self._idn = ''

    def _set_handle(self, handle):
        self.handle = handle
        self.connected = handle is not None

    def _store_idn(self, idn):
        self._idn = str(idn or "").strip()

    def _query_and_store_idn(self):
        if self.handle is None or self._itech is not None:
            self._idn = ""
            return
        try:
            idn = self.handle.query('*IDN?')
            self._store_idn(idn)
            self.logger.info(f'AC *IDN? = {self._idn}')
            print(f'AC *IDN? = {self._idn}')
        except Exception as e:
            self.logger.warning(f'AC *IDN? 失败: {e}')
            print(f'AC *IDN? 失败: {e}')

    def is_chroma_61800(self):
        """连接后根据 *IDN? 判断是否为 Chroma 61800 系列。"""
        return _is_chroma_61800_idn(self._idn)

    def query_output_limits(self, brand=None):
        """读回保护类输出上限（OVP/OCP/OPP）；失败返回 {_unread, detail}。"""
        from utils.iot_brand_limit_read import read_ac_output_limits

        return read_ac_output_limits(self, brand=brand)

    def show_setting(self, dialog_windowACSetting):
        """设置已嵌入设备页面，无需弹窗。"""
        pass

    def connect_modbus(self, tcp_addr, port, ui):
        """通过 Modbus 客户端连接交流电源。"""
        try:
            # 勿默认 fresh_socket_each_send：True 会在每次 send 开头 disconnect+connect，看起来像「发一条就断」
            kw = {'on_session_renewed': self._set_handle}
            # 爱科 8080：PyVISA SOCKET 易半断，首包丢失；与直流一致可用原生 TCP（API 仍为 ModbusVISA）
            if self.modbus_client_cls is ModbusVISA:
                kw['use_plain_socket'] = True
            client = self.modbus_client_cls(tcp_addr, port, **kw)
            client.connect()
            if client.is_connected():
                self.logger.info(f'连接成功: {tcp_addr}:{port}')
                self.client = client
                self._set_handle(client.inst or client)
                self._itech = ItechTranslator(client)
                self.resource = tcp_addr
                self._idn = ""
                return self.client, self.handle, '1'
            self.logger.error('连接失败')
            self.show_message('交流电源连接失败，请检查IP和端口', ui)
            return None, None, '0'
        except ValueError:
            self.logger.error('地址格式错误，应为 IP:端口')
            self.show_message('交流电源地址格式错误，应为 IP:端口', ui)
            return None, None, '0'
        except Exception as e:
            self.logger.error(f'连接异常: {e}')
            self.show_message(f'交流电源连接异常：{e}', ui)
            return None, None, '0'

    def connect_scpi(self, tcp_addr, ui):
        """通过 VISA/SCPI 连接交流电源。"""
        try:
            handle = self.rm.open_resource(tcp_addr)
        except Exception:
            print('device not exit')
            self.logger.info('交流电源 not exit')
            print('交流电源 not exit')
            self.show_message('交流电源连接失败，请检查设备地址和连线', ui)
            self._set_handle(None)
            return None, '0'
        try:
            if self.configure_scpi_resource is not None:
                self.configure_scpi_resource(handle)
        except Exception:
            self.logger.info('交流电源 not exit')
            print('交流电源 not exit')
            self.show_message('交流电源连接失败，请检查设备地址和连线', ui)
            release_resource_handle(handle)
            self._set_handle(None)
            return None, '0'
        self.logger.info('交流电源连接成功')
        print('交流电源连接成功')
        self._set_handle(handle)
        self._itech = None
        self.resource = tcp_addr
        self._query_and_store_idn()
        return self.handle, '1'

    def connect_scpi_tcp(self, host, port, ui):
        """通过原生 TCP Socket 连接交流电源（绕过 PyVISA/NI-VISA）。"""
        try:
            scpi = ScpiSocket(host, port, timeout=10)
            scpi.connect()
        except Exception as e:
            self.logger.error(f'AC TCP 连接异常: {e}')
            self.show_message(f'交流电源 TCP 连接失败：{e}', ui)
            self._set_handle(None)
            return None, '0'
        # 测试连接：发 *IDN?
        try:
            idn = scpi.query('*IDN?')
            self._store_idn(idn)
            self.logger.info(f'AC *IDN? = {self._idn}')
            print(f'AC *IDN? = {self._idn}')
        except Exception as e:
            self.logger.warning(f'AC *IDN? 失败（继续连接）: {e}')
            print(f'AC *IDN? 失败: {e}')
            self._idn = ''
        self.logger.info('交流电源连接成功(TCP)')
        print('交流电源连接成功(TCP)')
        self._set_handle(scpi)
        self._itech = None
        self.resource = f"TCPIP::{host}::{scpi.port}"
        return self.handle, '1'

    def reconnect_scpi_tcp(self, host, port=None):
        """后台重连 ScpiSocket（无 UI 弹窗）。成功返回 True。"""
        try:
            release_resource_handle(self.handle)
        except Exception:
            pass
        self._itech = None
        self.client = None
        self._set_handle(None)
        try:
            scpi = ScpiSocket(host, port, timeout=10)
            scpi.connect()
            self._set_handle(scpi)
            try:
                self._store_idn(scpi.query('*IDN?'))
            except Exception:
                self._idn = ''
            self.resource = f"TCPIP::{host}::{scpi.port}"
            self.logger.info(f'AC---reconnect(scpi_tcp)---{self.resource}')
            print(f'AC---reconnect(scpi_tcp)---{self.resource}')
            return True
        except Exception as e:
            self.logger.error(f'AC ScpiSocket 重连失败: {e}')
            print(f'AC ScpiSocket 重连失败: {e}')
            self._set_handle(None)
            return False

    def uses_scpi_socket(self):
        """当前句柄是否为原生 TCP ScpiSocket（Chroma IP 模式）。"""
        return isinstance(self.handle, ScpiSocket)

    def disconnect(self, safe_close_handle):
        """断开交流电源并重置状态。"""
        self._itech = None
        safe_close_handle(self.handle)
        self.handle = None
        self.client = None
        self.connected = False
        self.resource = ''
        self._idn = ''
        return None, None, '0'

    def poll_syst_err(self, tcp_addr):
        """轮询交流电源 SYST:ERR?，失败时按原连接类型重连（ScpiSocket 勿走 VISA）。"""
        try:
            information = self.handle.query('SYST:ERR?')
            return self.handle, information
        except Exception as e:
            print(e)
            self.logger.error(e)
            prefer_socket = self.uses_scpi_socket() or str(self.resource or "").startswith("TCPIP::")
            host, port = self._parse_scpi_tcp_endpoint(tcp_addr, self.resource)
            release_resource_handle(self.handle)
            self._set_handle(None)
            time.sleep(0.12)
            if prefer_socket and host:
                if self.reconnect_scpi_tcp(host, port):
                    return self.handle, None
                return None, None
            try:
                new_handle = self.rm.open_resource(tcp_addr)
            except Exception as e2:
                self.logger.error(e2)
                return None, None
            try:
                if self.configure_scpi_resource is not None:
                    self.configure_scpi_resource(new_handle)
            except Exception as e3:
                self.logger.error(e3)
                release_resource_handle(new_handle)
                return None, None
            self._set_handle(new_handle)
            self.resource = tcp_addr
            print(f'HandleEquAC---reconnect---{new_handle}')
            self.logger.info(f'HandleEquAC---reconnect---{new_handle}')
            return new_handle, None

    @staticmethod
    def _parse_scpi_tcp_endpoint(tcp_addr, resource=""):
        """从 combo/resource 解析 Chroma TCP (host, port|None)。"""
        for candidate in (resource, tcp_addr):
            if not candidate:
                continue
            s = str(candidate).strip()
            m = re.match(r'^TCPIP::(\d+\.\d+\.\d+\.\d+)::(\d+)$', s, re.I)
            if m:
                return m.group(1), int(m.group(2))
            m = re.match(r'^TCPIP\d*::(\d+\.\d+\.\d+\.\d+)::', s, re.I)
            if m:
                return m.group(1), None
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', s):
                return s, None
        return None, None
    def apply_setpoints(self, ac_voltage, ac_frequency, ac_phase, log_sink=None, volt_b=None, volt_c=None):
        """按 UI 设定下发相位/电压/频率（不断开、不开输出）。

        设备断电重启或 STANDBY 后设定会丢失；连接成功 / 开输出前应调用本方法。
        volt_b / volt_c：三相时 B/C 相电压，空则与 A 相同。
        返回 True 表示已尝试下发（字段齐全），False 表示电压/频率为空跳过。
        """
        chroma = self.is_chroma_61800()
        if chroma:
            ac_voltage = _fmt_ac_volt_value(ac_voltage)
        else:
            ac_voltage = (ac_voltage or "").strip()
        ac_frequency = (ac_frequency or "").strip()
        ac_phase = (ac_phase or "").strip()
        if not ac_voltage or not ac_frequency:
            return False
        if self.handle is None:
            return False

        def _log(msg):
            self.logger.info(msg)
            print(f'{self.now_to_datenow()} {msg}')
            if log_sink is not None:
                try:
                    log_sink.append(msg)
                except Exception:
                    pass

        if self._itech is not None:
            # 与页面「下发参数」一致：用 INST:PHAS（爱科 Modbus 映射键）
            if ac_phase == '单相':
                command_list = [
                    'INST:PHAS SINGLE',
                    'INST:EDIT ALL',
                    'VOLT ' + ac_voltage,
                    'FREQ ' + ac_frequency,
                ]
            elif ac_phase == '三相':
                command_list = [
                    'INST:PHAS THREE',
                    'INST:EDIT ALL',
                    'VOLT ' + ac_voltage,
                    'FREQ ' + ac_frequency,
                ]
            else:
                command_list = []
        else:
            if ac_phase == '单相':
                if chroma:
                    command_list = list(_chroma_ac_preamble()) + [
                        'INST:PHAS SINGLE',
                        'INST:EDIT ALL',
                        _chroma_volt_write(ac_voltage),
                        'FREQ ' + ac_frequency,
                    ]
                else:
                    command_list = [
                        'INST:PHAS SINGLE',
                        'INST:EDIT ALL',
                        'VOLT ' + ac_voltage,
                        'FREQ ' + ac_frequency,
                    ]
            elif ac_phase == '三相':
                if chroma:
                    command_list = _chroma_three_phase_command_list(
                        ac_voltage, volt_b, volt_c, ac_frequency
                    )
                else:
                    command_list = _generic_scpi_three_phase_command_list(
                        ac_voltage, ac_frequency, volt_b, volt_c
                    )
            else:
                command_list = []

        for command in command_list:
            if self._itech is not None:
                ok, _ = self._itech.translate(command)
                if ok:
                    _log('SendCommandToAC:' + command)
                else:
                    _log(f'Send command {command} to AC failed (Modbus)')
            else:
                try:
                    self.handle.write(command)
                    if self.uses_scpi_socket():
                        time.sleep(0.05)
                except Exception as e:
                    _log(f'Send command {command} to AC error :{e}')
                else:
                    _log('SendCommandToAC:' + command)
        if chroma and self._itech is None:
            self._log_chroma_setpoint_verify(_log)
        return True

    def _log_chroma_setpoint_verify(self, log_sink=None):
        """下发后读回 VOLT:AC? / OUTP?，便于真机日志对照。"""
        if self.handle is None:
            return
        for query in ('VOLT:AC?', 'VOLT?', 'OUTP?'):
            try:
                ans = str(self.handle.query(query) or '').strip()
                msg = f'AC verify {query} = {ans}'
                self.logger.info(msg)
                print(f'{self.now_to_datenow()} {msg}')
                if log_sink is not None:
                    try:
                        log_sink.append(msg)
                    except Exception:
                        pass
            except Exception as exc:
                self.logger.warning(f'AC verify {query} failed: {exc}')

    def _clear_syst_err_queue(self, max_n=10):
        """读空 SYST:ERR?，避免面板/日志反复显示上次 -222。"""
        if self.handle is None or self._itech is not None:
            return
        for _ in range(max_n):
            try:
                err = str(self.handle.query('SYST:ERR?') or '').strip()
            except Exception:
                break
            if not err or err.startswith('0') or 'No error' in err:
                break

    def open_output(self, setpoints=None):
        """打开交流电源输出。

        setpoints: 可选 (volt, freq, phase)。提供时会在开输出前（爱科在 RUN 之后）
        重新下发设定，避免设备重启/待机后参数回到出厂值。

        返回 True/False。IOT 侧用 bool(结果) 判断成败；勿再 void 返回 None
        （bool(None) 会被当成打开失败）。
        """
        if self.handle is not None:
            if self._itech is not None:
                # 爱科寄存器：先运行/输出使能(0x0909=RUN)，再输出吸合(0x0909=OUTPUT_ON)；勿只发吸合
                steps = (
                    ('SYST:RUN', '运行/输出使能'),
                    ('OUTP ON', '输出吸合'),
                )
                strtimenow = self.now_to_datenow()
                all_ok = True
                for cmd, desc in steps:
                    if cmd == 'OUTP ON' and setpoints is not None:
                        volt, freq, phase = setpoints
                        self.apply_setpoints(volt, freq, phase)
                        time.sleep(0.2)
                    ok, trace = self._itech.translate(cmd)
                    print(f'{strtimenow} [AC Modbus] {cmd} ({desc}) translate_ok={ok}')
                    for line in trace:
                        print(f'{strtimenow} [AC Modbus]   trace: {line}')
                    if not ok:
                        all_ok = False
                        self.logger.info(f'AC {cmd} error (Modbus translate failed)')
                        break
                    self.logger.info(cmd)
                    print(f'{strtimenow} {cmd}')
                    if ok and cmd == 'SYST:RUN':
                        time.sleep(_AC_CONTROL_REG_INTER_CMD_DELAY_SEC)
                if not all_ok and self.ui_setting is not None:
                    self.show_message('交流电源输出开启失败（Modbus）', self.ui_setting)
                return bool(all_ok)
            # Chroma 等纯 SCPI：仅 OUTP ON。SYST:RUN 是爱科寄存器语义，
            # 发给 61800 会进 -102 Syntax error，面板/日志像“非法字符/语法错”。
            if setpoints is not None:
                volt, freq, phase = setpoints
                self.apply_setpoints(volt, freq, phase)
                time.sleep(0.2)
            strArraySetting = 'OUTP ON'
            try:
                self.handle.write(strArraySetting)
            except Exception as e:
                strtimenow = self.now_to_datenow()
                self.logger.info(f'AC OUTP ON error--1: {e}')
                print(f'{strtimenow} AC OUTP ON error--1: {e}')
                if self.ui_setting is not None:
                    self.show_message(f'交流电源输出开启失败：{e}', self.ui_setting)
                return False
            strtimenow = self.now_to_datenow()
            self.logger.info(strArraySetting)
            print(f'{strtimenow} {strArraySetting}')
            self._clear_syst_err_queue()
            return True
        strtimenow = self.now_to_datenow()
        self.logger.info('AC Not Connect')
        print(f'{strtimenow} AC Not Connect')
        if self.ui_setting is not None:
            self.show_message('交流电源未连接，请先连接AC设备', self.ui_setting)
            self.show_message('交流电源未连接，请先连接AC设备')
        return False

    def send_message(self, uiACSetting):
        """向交流电源发送电压、频率和相位设置命令。"""
        uiACSetting.textEdit_AC.clear()
        if self.handle is not None:
            ac_voltage = uiACSetting.textEdit_AC_VOLT.toPlainText()
            ac_frequency = uiACSetting.textEdit_AC_FR.toPlainText()
            ac_phase = uiACSetting.comboBox_Phase.currentText()
            if ac_voltage != '' and ac_frequency != '':
                self.apply_setpoints(
                    ac_voltage,
                    ac_frequency,
                    ac_phase,
                    log_sink=uiACSetting.textEdit_AC,
                )
            else:
                QMessageBox.information(
                    uiACSetting,
                    '错误提示信息',
                    '交流源电压or电流输入有误，请确认',
                    QMessageBox.Ok,
                    QMessageBox.Ok,
                )
        else:
            strtimenow = self.now_to_datenow()
            self.logger.info('AC Not Connect')
            print(strtimenow + ' AC Not Connect')
            self.show_message('交流电源未连接，请先连接AC设备', uiACSetting)

    def close_output(self):
        """关闭交流电源输出。返回 True/False（供 IOT bool 判定，勿 void）。"""
        if self.handle is not None:
            if self._itech is not None:
                # TCP 半连接时第一条 FC06 常丢失，第二条待机帧反而成功 → 第一次点关不掉、第二次才像生效。
                # 关断前先静默换新 TCP，保证 OUTP OFF 落在干净连接上。
                try:
                    if self.client is not None and hasattr(self.client, '_silent_recover'):
                        self.client._silent_recover()
                except Exception as ex:
                    self.logger.warning(f'AC 关输出前 TCP 刷新失败: {ex}')
                # 爱科：先释放输出吸合，再待机退出运行（与 open_output 的 RUN→吸合 顺序相反）
                steps = (
                    ('OUTP OFF', '输出断开/释放吸合'),
                    ('SYST:STANDBY', '待机/关闭输出回路'),
                )
                strtimenow = self.now_to_datenow()
                all_ok = True
                for cmd, desc in steps:
                    ok, trace = self._itech.translate(cmd)
                    print(f'{strtimenow} [AC Modbus] {cmd} ({desc}) translate_ok={ok}')
                    for line in trace:
                        print(f'{strtimenow} [AC Modbus]   trace: {line}')
                    if not ok:
                        all_ok = False
                        self.logger.info(f'AC {cmd} error (Modbus translate failed)')
                        break
                    self.logger.info(cmd)
                    print(f'{strtimenow} {cmd}')
                    # 同上寄存器连写，须留出间隔再发待机。
                    if ok and cmd == 'OUTP OFF':
                        time.sleep(_AC_CONTROL_REG_INTER_CMD_DELAY_SEC)
                if not all_ok and self.ui_setting is not None:
                    self.show_message('交流电源输出关闭失败（Modbus）', self.ui_setting)
                return bool(all_ok)
            # Chroma：仅 OUTP OFF（勿发 SYST:STANDBY）
            strArraySetting = 'OUTP OFF'
            try:
                self.handle.write(strArraySetting)
            except Exception as e:
                strtimenow = self.now_to_datenow()
                self.logger.info(f'AC OUTP OFF error--1: {e}')
                print(f'{strtimenow} AC OUTP OFF error--1: {e}')
                return False
            strtimenow = self.now_to_datenow()
            self.logger.info(strArraySetting)
            print(f'{strtimenow} {strArraySetting}')
            return True
        strtimenow = self.now_to_datenow()
        self.logger.info('AC Not Connect')
        print(f'{strtimenow} AC Not Connect')
        if self.ui_setting is not None:
            self.show_message('交流电源未连接，请先连接AC设备', self.ui_setting)
        return False
