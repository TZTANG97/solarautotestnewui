import time

from PyQt5.QtWidgets import QMessageBox

from .handle_release import release_resource_handle
from modbus_visa import ModbusVISA


class DCController:
    """直流电源控制器，封装连接、断开、输出、查询与轮询逻辑。"""

    def __init__(self, logger, show_message, now_to_datenow, ui_setting=None, rm=None, configure_scpi_resource=None):
        self.logger = logger
        self.show_message = show_message
        self.now_to_datenow = now_to_datenow
        self.ui_setting = ui_setting
        self.rm = rm
        self.configure_scpi_resource = configure_scpi_resource
        self.handle = None
        self.client = None
        self.connected = False
        self.resource = ''

    def _set_handle(self, handle):
        self.handle = handle
        self.connected = handle is not None

    def show_setting(self, dialog):
        """设置已嵌入设备页面，无需弹窗。"""
        pass

    def query_output_limits(self, brand=None):
        """读回保护类输出上限（OVP/OCP/OPP）；失败返回 {_unread, detail}。"""
        from utils.iot_brand_limit_read import read_dc_output_limits

        return read_dc_output_limits(self, brand=brand)

    def _write_modbus_output_register(self, label, logger, is_on):
        """蓝点等 Modbus TCP：保持寄存器 0x0BB8 控制输出（与 BluesightTranslator 一致）。

        返回: True 写成功；False 写失败/未连；None 无 Modbus client（走 SCPI）。
        """
        if self.client is None:
            return None
        try:
            if hasattr(self.client, 'is_connected') and not self.client.is_connected():
                return False
            register_value = 0x00AA if is_on else 0x0055
            self.client.write_register(0x0BB8, register_value)
            strtimenow = self.now_to_datenow()
            logger.info(f'{label} MODBUS REG 0x0BB8 <- 0x{register_value:04X}')
            print(strtimenow + f'{label} MODBUS REG 0x0BB8 <- 0x{register_value:04X}')
            return True
        except Exception as e:
            strtimenow = self.now_to_datenow()
            logger.info(f'{label} MODBUS output register write failed: {e}')
            print(strtimenow + f'{label} MODBUS output register write failed: {e}')
            return False

    def _output_dc(self, label, ui_setting, logger, is_on, *, silent_if_disconnected=False):
        """开/关直流输出。返回 True/False，供 IOT bool 判定（勿 void→None）。"""
        command = 'OUTP ON' if is_on else 'OUTP OFF'
        mb_ok = self._write_modbus_output_register(label, logger, is_on)
        # Modbus 路径（ModbusVISA 无 SCPI write）：仅寄存器控制，禁止走 handle.write
        if self.client is not None:
            strtimenow = self.now_to_datenow()
            logger.info(f'{label} {command} (Modbus)')
            print(strtimenow + f'{label} {command} (Modbus)')
            return bool(mb_ok)
        if self.handle is not None:
            try:
                self.handle.write(command)
            except Exception as e:
                print(e)
                self.show_message(f'{label}输出{"开启" if is_on else "关闭"}失败：{e}', ui_setting)
                return False
            strtimenow = self.now_to_datenow()
            logger.info(f'{label} {command}')
            print(strtimenow + f'{label} {command}')
            return True
        strtimenow = self.now_to_datenow()
        logger.info(f'{label} Not Connect')
        print(strtimenow + f'{label} Not Connect')
        # 结束试验强制关断：未连接的 DC2/3/4 静默跳过，避免弹窗打断
        if not silent_if_disconnected:
            self.show_message(f'{label}未连接，请先连接{label}设备', ui_setting)
            return False
        return True

    def open_output(self, label, ui_setting, logger):
        return self._output_dc(label, ui_setting, logger, True)

    def close_output(self, label, ui_setting, logger, *, silent_if_disconnected=False):
        return self._output_dc(
            label, ui_setting, logger, False, silent_if_disconnected=silent_if_disconnected
        )

    def send_message(self, ui_setting, label, logger):
        if self.handle is None:
            strtimenow = self.now_to_datenow()
            logger.info(f'{label} Not Connect')
            print(strtimenow + f' {label} Not Connect')
            self.show_message(f'{label}未连接，请先连接{label}设备', ui_setting)
            return
        message = ui_setting.textEdit_SendMessage.toPlainText()
        if message == '':
            return
        try:
            self.handle.write(message)
        except Exception as e:
            strtimenow = self.now_to_datenow()
            logger.info(f'Send message to {label} error :{e}')
            print(f'{strtimenow} Send message to {label} error :{e}')
        else:
            strtimenow = self.now_to_datenow()
            logger.info(f'SendMessageTo{label}:{message}')
            print(strtimenow + f'SendMessageTo{label}:{message}')

    def query_message(self, ui_setting, label, logger):
        if self.handle is None:
            strtimenow = self.now_to_datenow()
            logger.info(f'{label} Not Connect')
            print(strtimenow + f' {label} Not Connect')
            self.show_message(f'{label}未连接，请先连接{label}设备', ui_setting)
            return
        # DL850 使用 textEdit_SendQueryMessage，DC1-4 使用 lineEdit
        if hasattr(ui_setting, 'textEdit_SendQueryMessage'):
            query_message = ui_setting.textEdit_SendQueryMessage.toPlainText()
        else:
            query_message = ui_setting.lineEdit.text()
        if query_message == '':
            return
        try:
            response = self.handle.query(query_message)
        except Exception as e:
            strtimenow = self.now_to_datenow()
            logger.info(f'Query message from {label} error :{e}')
            print(f'{strtimenow} Query message from {label} error :{e}')
        else:
            strtimenow = self.now_to_datenow()
            ui_setting.textEdit_ReturnMessage.append(strtimenow + f' ReturnMessageForm{label} :{response}')

    def connect_modbus(self, tcp_addr, ui, modbus_client_cls, fail_label):
        try:
            # 解析 ip:port 格式，分离主机和端口
            host, port = tcp_addr, 502
            if ':' in str(tcp_addr):
                parts = tcp_addr.rsplit(':', 1)
                if len(parts) == 2 and parts[1].isdigit():
                    host, port = parts[0], int(parts[1])
            if modbus_client_cls is ModbusVISA:
                # 与 test_guochan / 蓝点联调一致：原生 TCP 避免 PyVISA SOCKET 读不到应答、半断
                client = modbus_client_cls(
                    host,
                    port=port,
                    on_session_renewed=self._set_handle,
                    use_plain_socket=True,
                )
            else:
                client = modbus_client_cls(host, port=port)
            client.connect()
            if client.is_connected():
                self.logger.info(f'连接成功: {tcp_addr}:502')
                self.client = client
                self._set_handle(client.inst or client)
                self.resource = tcp_addr
                return self.client, self.handle, '1'
            self.logger.error('连接失败')
            self.show_message(f'{fail_label}连接失败，请检查IP和端口', ui)
            return None, None, '0'
        except ValueError:
            self.logger.error('地址格式错误，应为 IP:端口')
            self.show_message(f'{fail_label}地址格式错误，应为 IP:端口', ui)
            return None, None, '0'
        except Exception as e:
            self.logger.error(f'连接异常: {e}')
            self.show_message(f'{fail_label}连接异常：{e}', ui)
            return None, None, '0'

    @staticmethod
    def _normalize_visa_resource(addr: str) -> str:
        """USB/ASRL/GPIB 缺 ::INSTR 时补全，避免 open_resource 失败却只报「会话未建立」。"""
        text = (addr or "").strip()
        if not text:
            return text
        upper = text.upper()
        if upper.startswith(("USB", "ASRL", "GPIB")) and not upper.endswith("::INSTR"):
            if text.endswith("::"):
                return text + "INSTR"
            if text.endswith(":"):
                return text + ":INSTR"
            return text + "::INSTR"
        return text

    def connect_scpi(self, tcp_addr, ui):
        addr = self._normalize_visa_resource(tcp_addr)
        if self.rm is None:
            msg = "直流电源连接失败：VISA 资源管理器未初始化"
            self.logger.error(msg)
            self.show_message(msg, ui)
            self._set_handle(None)
            return None, "0"
        try:
            handle = self.rm.open_resource(addr)
        except Exception as e:
            msg = f"直流电源连接失败：open_resource({addr}) → {e}"
            self.logger.info(msg)
            print(msg)
            self.show_message(msg, ui)
            self._set_handle(None)
            return None, "0"
        try:
            if self.configure_scpi_resource is not None:
                self.configure_scpi_resource(handle)
        except Exception as e:
            msg = f"直流电源连接失败：配置会话失败（{addr}）→ {e}"
            self.logger.info(msg)
            print(msg)
            self.show_message(msg, ui)
            release_resource_handle(handle)
            self._set_handle(None)
            return None, "0"
        self.logger.info("直流电源连接成功")
        print("直流电源连接成功")
        self._set_handle(handle)
        self.resource = addr
        return self.handle, "1"

    def disconnect(self, safe_close_handle):
        safe_close_handle(self.handle)
        self.handle = None
        self.client = None
        self.connected = False
        self.resource = ''
        return None, None, '0'

    def write_command(self, command, label="DC"):
        """发送命令；Modbus 路径自动翻译 BLUESIGHT:STC 为曲线块写入。"""
        if self.client is not None and hasattr(self.client, 'is_connected'):
            cmd = command.strip()
            if cmd.upper().startswith("BLUESIGHT:STC"):
                parts = cmd.split()
                if len(parts) == 4:
                    try:
                        pmpp_kw = float(parts[1])
                        umpp_v = float(parts[2])
                        ff = float(parts[3])
                    except ValueError:
                        self.logger.warning(f"{label} BLUESIGHT:STC 参数解析失败: {command}")
                        return False
                    return self._send_stc_curve(label, pmpp_kw, umpp_v, ff)
                return self._send_stc_curve(label)
            from scpi_to_modbustcp import BluesightTranslator
            tr = BluesightTranslator(self.client, device_id=1)
            # 生成阶段已拦截；运行期再挡一层致茂 IVC，避免旧命令表误发
            u = cmd.upper()
            if u.startswith("IVC:") or u.startswith("IVCURVE:") or "OUTP:MODE TABLE" in u:
                self.logger.warning(
                    f"{label} Modbus(蓝点)拒绝致茂曲线命令: {command}"
                )
                print(f"{label} Modbus(蓝点)拒绝致茂曲线命令: {command}")
                return False
            ok, msg = tr.translate(command)
            if not ok:
                self.logger.warning(f"{label} Modbus 翻译失败: {msg}")
                print(f"{label} Modbus 翻译失败: {msg}")
            return ok
        if self.handle is not None:
            cmd = str(command or "")
            # 仅长表加 timeout/sleep；短令如 SAS:TABL:ACT 不拖
            u = cmd.upper()
            long_sas = ("SAS:TABL" in u) and (len(cmd) > 200 or cmd.count(",") >= 32)
            old_timeout = None
            try:
                if long_sas and hasattr(self.handle, "timeout"):
                    try:
                        old_timeout = self.handle.timeout
                        self.handle.timeout = max(float(old_timeout or 2000), 30000.0)
                    except Exception:
                        old_timeout = None
                # 优先 write_raw，避免部分 PyVISA 路径对超长 write 在 DLL 内崩进程
                payload = (cmd + "\n").encode("ascii", errors="ignore")
                try:
                    if hasattr(self.handle, "write_raw"):
                        self.handle.write_raw(payload)
                    else:
                        self.handle.write(cmd)
                except Exception as exc:
                    self.logger.warning(f"{label} SCPI 写失败 ({len(cmd)}B): {exc}")
                    print(f"{label} SCPI 写失败 ({len(cmd)}B): {exc}")
                    return False
                if long_sas:
                    import time as _time

                    _time.sleep(0.8)
            finally:
                if old_timeout is not None:
                    try:
                        self.handle.timeout = old_timeout
                    except Exception:
                        pass
            return True
        return False

    def _send_stc_curve(self, label="DC", pmpp_kw=0, umpp_v=0, ff=0.8):
        """用 UI 传入的 Pmpp/Umpp/FF 写入 STC 曲线块（仅 SAS 模式）。"""
        from scpi_to_modbustcp import BluesightTranslator, BluesightCurveSTC
        tr = BluesightTranslator(self.client, device_id=1)
        # 检查是否在 SAS 模式（寄存器 0x0F95 = 1）
        try:
            mode_val = self.client.read_holding_register(0x0F95, quantity=1)
            if hasattr(mode_val, 'registers') and mode_val.registers:
                current_mode = mode_val.registers[0]
                if current_mode != 0x0001:
                    self.logger.warning(f"{label} 蓝点当前模式={current_mode}，非SAS(1)，跳过曲线写入")
                    print(f"{label} 蓝点当前模式={current_mode}，非SAS(1)，跳过曲线写入")
                    return True
        except Exception as e:
            self.logger.warning(f"{label} 读取蓝点模式寄存器失败: {e}，继续尝试写入曲线")
            print(f"{label} 读取蓝点模式寄存器失败: {e}，继续尝试写入曲线")
        if pmpp_kw <= 0 or umpp_v <= 0:
            self.logger.warning(f"{label} 蓝点 STC 参数无效: Pmpp={pmpp_kw}, Umpp={umpp_v}")
            print(f"{label} 蓝点 STC 参数无效: Pmpp={pmpp_kw}, Umpp={umpp_v}")
            return False
        self.logger.info(f"{label} STC 写入: Pmpp={pmpp_kw}kW, Umpp={umpp_v}V, FF={ff}")
        print(f"{label} STC 写入: Pmpp={pmpp_kw}kW, Umpp={umpp_v}V, FF={ff}")
        try:
            stc = BluesightCurveSTC(
                pmpp_stc_kw=pmpp_kw,
                umpp_stc_v=umpp_v,
                fill_factor=ff,
            )
            ok, msg = tr.write_curve_block(stc=stc)
            self.logger.info(f"{label} STC 曲线块: {'OK' if ok else 'FAIL'} - {msg}")
            print(f"{label} STC 曲线块: {'OK' if ok else 'FAIL'} - {msg}")
            return ok
        except Exception as e:
            self.logger.error(f"{label} STC 曲线块异常: {e}")
            print(f"{label} STC 曲线块异常: {e}")
            return False

    def poll_syst_err(self, tcp_addr, reconnect_message_prefix):
        """轮询 SYST:ERR?；USB/VISA 失败时先释放旧句柄再重连。Modbus TCP 无 SCPI，不重连。"""
        if self.client is not None:
            return self.handle, None
        try:
            information = self.handle.query('SYST:ERR?')
            return self.handle, information
        except Exception as e:
            print(f'{reconnect_message_prefix} error: {e}')
            self.logger.error(f'{reconnect_message_prefix} error: {e}')
            release_resource_handle(self.handle)
            self._set_handle(None)
            time.sleep(0.12)
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
            print(f'{reconnect_message_prefix}---reconnect---{new_handle}')
            self.logger.info(f'{reconnect_message_prefix}---reconnect---{new_handle}')
            return new_handle, None


def send_dc_test_message(
    handle,
    uiDC1Setting,
    per_dc_factor,
    command_list_DC,
    DCGetIVValueFunction,
    logger,
    now_to_datenow,
    dc_index=0,
    dc_label='DC1',
    silent=False,
):
    global_result = []
    DCVmp = uiDC1Setting.textEdit_Vmp.toPlainText().strip()
    DCImp = uiDC1Setting.textEdit_Imp.toPlainText().strip()
    DCVoc = uiDC1Setting.textEdit_Voc.toPlainText().strip()
    DCIsc = uiDC1Setting.textEdit_Isc.toPlainText().strip()
    DCPF = uiDC1Setting.textEdit_PF.toPlainText().strip()

    if not all([DCVmp, DCImp, DCVoc, DCIsc]):
        uiDC1Setting.textEdit_ReturnMessage.append(
            f'{dc_label} IV 参数未填写，已跳过曲线下发（填写后点击「发送曲线」）'
        )
        return []

    a = DCGetIVValueFunction(DCVmp, DCImp, DCVoc, DCIsc, DCPF, dc_index)
    if a == '1':
        uiDC1Setting.textEdit_ReturnMessage.append(f'{dc_label}赋值错误,请重新输入')
        if not silent:
            QMessageBox.information(None, '错误提示信息', f'{dc_label}赋值错误,请重新输入', QMessageBox.Ok, QMessageBox.Ok)
        return []
    if a == '2':
        uiDC1Setting.textEdit_ReturnMessage.append(f'{dc_label}Isc,Imp赋值超范围,请重新输入')
        if not silent:
            QMessageBox.information(None, '错误提示信息', f'{dc_label}Isc,Imp赋值超范围,请重新输入', QMessageBox.Ok, QMessageBox.Ok)
        return []
    if a == '3':
        uiDC1Setting.textEdit_ReturnMessage.append(
            f'{dc_label}厂家未识别或参数未就绪，已跳过IV下发'
        )
        return []
    if a is None:
        uiDC1Setting.textEdit_ReturnMessage.append(f'{dc_label}赋值结果为空，请检查输入')
        return []
    if isinstance(a, str):
        global_result.append(a)
        return global_result
    for item in a:
        global_result.append(item)
    return global_result
