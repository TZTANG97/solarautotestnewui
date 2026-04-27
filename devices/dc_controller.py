from PyQt5.QtWidgets import QMessageBox


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
        dialog.show()

    def _write_modbus_output_register(self, label, logger, is_on):
        """兼容 DC1 的 Modbus 输出控制寄存器写入。"""
        if label != 'DC1' or self.client is None:
            return
        try:
            if hasattr(self.client, 'is_connected') and not self.client.is_connected():
                return
            register_value = 0x00AA if is_on else 0x0055
            self.client.write_register(0x0BB8, register_value)
            strtimenow = self.now_to_datenow()
            logger.info(f'{label} MODBUS REG 0x0BB8 <- 0x{register_value:04X}')
            print(strtimenow + f'{label} MODBUS REG 0x0BB8 <- 0x{register_value:04X}')
        except Exception as e:
            # 保持现有逻辑：寄存器写失败不阻断后续 SCPI OUTP 命令
            strtimenow = self.now_to_datenow()
            logger.info(f'{label} MODBUS output register write failed: {e}')
            print(strtimenow + f'{label} MODBUS output register write failed: {e}')

    def _output_dc(self, label, ui_setting, logger, is_on):
        command = 'OUTP ON' if is_on else 'OUTP OFF'
        self._write_modbus_output_register(label, logger, is_on)
        if self.handle is not None:
            try:
                self.handle.write(command)
            except Exception as e:
                print(e)
                self.show_message(f'{label}输出{"开启" if is_on else "关闭"}失败：{e}', ui_setting)
            else:
                strtimenow = self.now_to_datenow()
                logger.info(f'{label} {command}')
                print(strtimenow + f'{label} {command}')
        else:
            strtimenow = self.now_to_datenow()
            logger.info(f'{label} Not Connect')
            print(strtimenow + f'{label} Not Connect')
            self.show_message(f'{label}未连接，请先连接{label}设备', ui_setting)

    def open_output(self, label, ui_setting, logger):
        self._output_dc(label, ui_setting, logger, True)

    def close_output(self, label, ui_setting, logger):
        self._output_dc(label, ui_setting, logger, False)

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
        query_message = ui_setting.textEdit_SendQueryMessage.toPlainText()
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
            client = modbus_client_cls(tcp_addr)
            client.connect()
            if client.is_connected():
                self.logger.info(f'连接成功: {tcp_addr}:502')
                self.client = client
                self._set_handle(client.inst)
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

    def connect_scpi(self, tcp_addr, ui):
        try:
            handle = self.rm.open_resource(tcp_addr)
            if self.configure_scpi_resource is not None:
                self.configure_scpi_resource(handle)
        except Exception:
            print('device not exit')
            self.logger.info('直流电源 not exit')
            print('直流电源 not exit')
            self.show_message('直流电源连接失败，请检查设备地址和连线', ui)
            self._set_handle(None)
            return None, '0'
        else:
            self.logger.info('直流电源连接成功')
            print('直流电源连接成功')
            self._set_handle(handle)
            return self.handle, '1'

    def disconnect(self, safe_close_handle):
        safe_close_handle(self.handle)
        self.handle = None
        self.client = None
        self.connected = False
        self.resource = ''
        return None, None, '0'

    def poll_syst_err(self, tcp_addr, reconnect_message_prefix):
        try:
            information = self.handle.query('SYST:ERR?')
            return self.handle, information
        except Exception as e:
            print(f'{reconnect_message_prefix} error: {e}')
            self.logger.error(f'{reconnect_message_prefix} error: {e}')
            new_handle = self.rm.open_resource(tcp_addr)
            if self.configure_scpi_resource is not None:
                self.configure_scpi_resource(new_handle)
            self._set_handle(new_handle)
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
):
    global_result = []
    DCVmp = uiDC1Setting.textEdit_Vmp.toPlainText()
    DCImp = uiDC1Setting.textEdit_Imp.toPlainText()
    DCVoc = uiDC1Setting.textEdit_Voc.toPlainText()
    DCIsc = uiDC1Setting.textEdit_Isc.toPlainText()
    DCPF = uiDC1Setting.textEdit_PF.toPlainText()

    a = DCGetIVValueFunction(DCVmp, DCImp, DCVoc, DCIsc, DCPF, dc_index)
    if a == '1':
        QMessageBox.information(None, '错误提示信息', f'{dc_label}赋值错误,请重新输入', QMessageBox.Ok, QMessageBox.Ok)
        uiDC1Setting.textEdit_ReturnMessage.append(f'{dc_label}赋值错误,请重新输入')
    elif a == '2':
        QMessageBox.information(None, '错误提示信息', f'{dc_label}Isc,Imp赋值超范围,请重新输入', QMessageBox.Ok, QMessageBox.Ok)
        uiDC1Setting.textEdit_ReturnMessage.append(f'{dc_label}Isc,Imp赋值超范围,请重新输入')
    else:
        if a is None:
            uiDC1Setting.textEdit_ReturnMessage.append(f'{dc_label}赋值结果为空，请检查输入')
            return []
        if isinstance(a, str):
            global_result.append(a)
            return global_result
        for item in a:
            global_result.append(item)
    return global_result
