from PyQt5.QtWidgets import QMessageBox


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
        self.connected = False
        self.resource = ''

    def _set_handle(self, handle):
        self.handle = handle
        self.connected = handle is not None

    def show_setting(self, dialog_windowACSetting):
        """显示 AC 设置窗口。"""
        dialog_windowACSetting.show()

    def connect_modbus(self, tcp_addr, ui):
        """通过 Modbus 客户端连接交流电源。"""
        try:
            client = self.modbus_client_cls(tcp_addr)
            client.connect()
            if client.is_connected():
                self.logger.info(f'连接成功: {tcp_addr}:502')
                self.client = client
                self._set_handle(client.inst)
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
            self.resource = tcp_addr
            return self.handle, '1'

    def disconnect(self, safe_close_handle):
        """断开交流电源并重置状态。"""
        safe_close_handle(self.handle)
        self.handle = None
        self.client = None
        self.connected = False
        self.resource = ''
        return None, None, '0'

    def poll_syst_err(self, tcp_addr):
        """轮询交流电源 SYST:ERR?，失败时尝试重新连接。"""
        try:
            information = self.handle.query('SYST:ERR?')
            return self.handle, information
        except Exception as e:
            print(e)
            self.logger.error(e)
            new_handle = self.rm.open_resource(tcp_addr)
            if self.configure_scpi_resource is not None:
                self.configure_scpi_resource(new_handle)
            self._set_handle(new_handle)
            print(f'HandleEquAC---reconnect---{new_handle}')
            self.logger.info(f'HandleEquAC---reconnect---{new_handle}')
            return new_handle, None

    def open_output(self):
        """打开交流电源输出。"""
        if self.handle is not None:
            strArraySetting = 'OUTP ON'
            try:
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
                if ac_phase == '单相':
                    command_list = ['INST:PHAS SINGLE', 'INST:EDIT ALL', 'VOLT ' + ac_voltage, 'FREQ ' + ac_frequency]
                elif ac_phase == '三相':
                    command_list = ['INST:PHAS THREE', 'INST:EDIT EACH', 'INST:NSEL 1', 'VOLT ' + ac_voltage, 'FREQ ' + ac_frequency, 'INST:NSEL 2', 'VOLT ' + ac_voltage, 'FREQ ' + ac_frequency, 'INST:NSEL 3', 'VOLT ' + ac_voltage, 'FREQ ' + ac_frequency]
                else:
                    command_list = []
                for command in command_list:
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
            strArraySetting = 'OUTP OFF'
            try:
                self.handle.write(strArraySetting)
            except Exception as e:
                strtimenow = self.now_to_datenow()
                self.logger.info(f'AC OUTP OFF error--1: {e}')
                print(f'{strtimenow} AC OUTP OFF error--1: {e}')
            else:
                strtimenow = self.now_to_datenow()
                self.logger.info(strArraySetting)
                print(f'{strtimenow} {strArraySetting}')
