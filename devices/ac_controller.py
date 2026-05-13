import time

from PyQt5.QtWidgets import QMessageBox

from .handle_release import release_resource_handle
from modbus_visa import ModbusVISA
from scpi_to_modbustcp import ItechTranslator

# 爱科 REG_CONTROL(0x0909)：连续两条控制命令（RUN→吸合、OUTP 断开→待机）同一寄存器不同值，
# 设备内部状态机需时间切换；for 循环若几乎无间隔，后一条可能覆盖前一条仅生效最后一次。
_AC_CONTROL_REG_INTER_CMD_DELAY_SEC = 2


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

    def _set_handle(self, handle):
        self.handle = handle
        self.connected = handle is not None

    def show_setting(self, dialog_windowACSetting):
        """显示 AC 设置窗口。"""
        dialog_windowACSetting.show()

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
            if self.configure_scpi_resource is not None:
                self.configure_scpi_resource(handle)
        except Exception:
            print('device not exit')
            self.logger.info('交流电源 not exit')
            print('交流电源 not exit')
            self.show_message('交流电源连接失败，请检查设备地址和连线', ui)
            self._set_handle(None)
            return None, '0'
        else:
            self.logger.info('交流电源连接成功')
            print('交流电源连接成功')
            self._set_handle(handle)
            self._itech = None
            self.resource = tcp_addr
            return self.handle, '1'

    def disconnect(self, safe_close_handle):
        """断开交流电源并重置状态。"""
        self._itech = None
        safe_close_handle(self.handle)
        self.handle = None
        self.client = None
        self.connected = False
        self.resource = ''
        return None, None, '0'

    def poll_syst_err(self, tcp_addr):
        """轮询交流电源 SYST:ERR?，失败时先释放旧会话再 ``open_resource`` 重连。"""
        try:
            information = self.handle.query('SYST:ERR?')
            return self.handle, information
        except Exception as e:
            print(e)
            self.logger.error(e)
            release_resource_handle(self.handle)
            self._set_handle(None)
            time.sleep(0.12)
            try:
                new_handle = self.rm.open_resource(tcp_addr)
            except Exception as e2:
                self.logger.error(e2)
                return None, None
            if self.configure_scpi_resource is not None:
                self.configure_scpi_resource(new_handle)
            self._set_handle(new_handle)
            self.resource = tcp_addr
            print(f'HandleEquAC---reconnect---{new_handle}')
            self.logger.info(f'HandleEquAC---reconnect---{new_handle}')
            return new_handle, None

    def open_output(self):
        """打开交流电源输出。"""
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
            else:
                strArraySetting = 'OUTP ON'
                try:
                    try:
                        self.handle.write('SYST:RUN')
                        self.logger.info('SYST:RUN')
                    except Exception:
                        pass
                    self.handle.write(strArraySetting)
                except Exception as e:
                    strtimenow = self.now_to_datenow()
                    self.logger.info(f'AC OUTP ON error--1: {e}')
                    print(f'{strtimenow} AC OUTP ON error--1: {e}')
                    if self.ui_setting is not None:
                        self.show_message(f'交流电源输出开启失败：{e}', self.ui_setting)
                else:
                    strtimenow = self.now_to_datenow()
                    self.logger.info(strArraySetting)
                    print(f'{strtimenow} {strArraySetting}')
        else:
            strtimenow = self.now_to_datenow()
            self.logger.info('AC Not Connect')
            print(f'{strtimenow} AC Not Connect')
            if self.ui_setting is not None:
                self.show_message('交流电源未连接，请先连接AC设备', self.ui_setting)
                self.show_message('交流电源未连接，请先连接AC设备')

    def send_message(self, uiACSetting):
        """向交流电源发送电压、频率和相位设置命令。"""
        uiACSetting.textEdit_AC.clear()
        if self.handle is not None:
            ac_voltage = uiACSetting.textEdit_AC_VOLT.toPlainText()
            ac_frequency = uiACSetting.textEdit_AC_FR.toPlainText()
            ac_phase = uiACSetting.comboBox_Phase.currentText()
            if ac_voltage != '' and ac_frequency != '':
                # 爱科 Modbus：电压/频率走寄存器；单相勿发 INST:EDIT ALL（Itech 在 SINGLE 下会拒绝）
                if self._itech is not None:
                    if ac_phase == '单相':
                        command_list = [
                            'INST:PHASE SINGLE',
                            'VOLT ' + ac_voltage,
                            'FREQ ' + ac_frequency,
                        ]
                    elif ac_phase == '三相':
                        command_list = [
                            'INST:PHASE THREE',
                            'INST:EDIT EACH',
                            'INST:NSEL 1',
                            'VOLT ' + ac_voltage,
                            'FREQ ' + ac_frequency,
                            'INST:NSEL 2',
                            'VOLT ' + ac_voltage,
                            'FREQ ' + ac_frequency,
                            'INST:NSEL 3',
                            'VOLT ' + ac_voltage,
                            'FREQ ' + ac_frequency,
                        ]
                    else:
                        command_list = []
                else:
                    if ac_phase == '单相':
                        command_list = ['INST:PHAS SINGLE', 'INST:EDIT ALL', 'VOLT ' + ac_voltage, 'FREQ ' + ac_frequency]
                    elif ac_phase == '三相':
                        command_list = ['INST:PHAS THREE', 'INST:EDIT EACH', 'INST:NSEL 1', 'VOLT ' + ac_voltage, 'FREQ ' + ac_frequency, 'INST:NSEL 2', 'VOLT ' + ac_voltage, 'FREQ ' + ac_frequency, 'INST:NSEL 3', 'VOLT ' + ac_voltage, 'FREQ ' + ac_frequency]
                    else:
                        command_list = []
                for command in command_list:
                    if self._itech is not None:
                        ok, _ = self._itech.translate(command)
                        strtimenow = self.now_to_datenow()
                        if ok:
                            self.logger.info('SendCommandToAC:' + command)
                            print(strtimenow + 'SendCommandToAC:' + command)
                        else:
                            self.logger.info(f'Send command {command} to AC failed (Modbus)')
                            print(f'{strtimenow} Send command {command} to AC failed (Modbus)')
                            uiACSetting.textEdit_AC.append(f'Send command {command} to AC error (Modbus)')
                    else:
                        try:
                            self.handle.write(command)
                        except Exception as e:
                            strtimenow = self.now_to_datenow()
                            self.logger.info(f'Send command {command} to AC error :{e}')
                            print(f'{strtimenow} Send command {command} to AC error :{e}')
                            uiACSetting.textEdit_AC.append(f'Send command {command} to AC error')
                        else:
                            strtimenow = self.now_to_datenow()
                            self.logger.info('SendCommandToAC:' + command)
                            print(strtimenow + 'SendCommandToAC:' + command)
            else:
                QMessageBox.information(uiACSetting, '错误提示信息', '交流源电压or电流输入有误，请确认', QMessageBox.Ok, QMessageBox.Ok)
        else:
            strtimenow = self.now_to_datenow()
            self.logger.info('AC Not Connect')
            print(strtimenow + ' AC Not Connect')
            self.show_message('交流电源未连接，请先连接AC设备', uiACSetting)

    def close_output(self):
        """关闭交流电源输出。"""
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
            else:
                strArraySetting = 'OUTP OFF'
                try:
                    self.handle.write(strArraySetting)
                    try:
                        self.handle.write('SYST:STANDBY')
                        self.logger.info('SYST:STANDBY')
                    except Exception:
                        pass
                except Exception as e:
                    strtimenow = self.now_to_datenow()
                    self.logger.info(f'AC OUTP OFF error--1: {e}')
                    print(f'{strtimenow} AC OUTP OFF error--1: {e}')
                else:
                    strtimenow = self.now_to_datenow()
                    self.logger.info(strArraySetting)
                    print(f'{strtimenow} {strArraySetting}')
        else:
            strtimenow = self.now_to_datenow()
            self.logger.info('AC Not Connect')
            print(f'{strtimenow} AC Not Connect')
            if self.ui_setting is not None:
                self.show_message('交流电源未连接，请先连接AC设备', self.ui_setting)
