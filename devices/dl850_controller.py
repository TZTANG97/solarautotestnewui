from devices.scpi_common import _configure_scpi_resource


class DL850Controller:
    """DL850 控制器，统一管理连接、断开和命令发送。"""

    def __init__(self, logger, show_message, now_to_datenow, rm=None, ui=None):
        self.logger = logger
        self.show_message = show_message
        self.now_to_datenow = now_to_datenow
        self.rm = rm
        self.ui = ui
        self.handle = None
        self.connected = False
        self.resource = ''

    def connect(self, tcp_addr):
        """连接 DL850 设备。"""
        try:
            handle = self.rm.open_resource(tcp_addr)
            _configure_scpi_resource(handle)
        except Exception:
            print("device not exit")
            self.logger.info("DL850 not exit")
            print("DL850 not exit")
            self.show_message("DL850连接失败，请检查设备地址和连线", self.ui)
            self.handle = None
            self.connected = False
            self.resource = ''
            return None, '0'
        self.logger.info("DL850连接成功")
        print("DL850连接成功")
        self.handle = handle
        self.connected = True
        self.resource = tcp_addr
        return self.handle, '1'

    def disconnect(self, safe_close_handle):
        """断开 DL850 设备。"""
        safe_close_handle(self.handle)
        self.handle = None
        self.connected = False
        self.resource = ''
        return None, '0'

    def _send(self, command, success_log, error_prefix):
        if self.handle is None:
            return False
        try:
            self.handle.write(command)
        except Exception as e:
            strtimenow = self.now_to_datenow()
            self.logger.info(f"{error_prefix} error :{e}")
            print(f'{strtimenow} {error_prefix} error :{e}')
            return False
        self.logger.info(success_log)
        print(self.now_to_datenow() + success_log)
        return True

    def send_start(self):
        return self._send("START", "SendMessageStartToDL850:START", "Send start message to DL850")

    def send_stop(self):
        return self._send("STOP", "SendMessageStartToDL850:STOP", "Send stop message to DL850")

    def send_save_picture(self):
        return self._send(":IMAGe:EXECute", "SendMessageStartToDL850::IMAGe:EXECute", "Image save message to DL850")


def connect_dl850(tcp_addr, rm, ui, logger, show_message):
    controller = DL850Controller(logger, show_message, lambda: '', rm=rm, ui=ui)
    return controller.connect(tcp_addr)


def disconnect_dl850(handle, safe_close_handle):
    safe_close_handle(handle)
    return None, '0'


def send_dl850_start(handle, logger, now_to_datenow):
    controller = DL850Controller(logger, lambda *_: None, now_to_datenow)
    controller.handle = handle
    return controller.send_start()


def send_dl850_stop(handle, logger, now_to_datenow):
    controller = DL850Controller(logger, lambda *_: None, now_to_datenow)
    controller.handle = handle
    return controller.send_stop()


def send_dl850_save_picture(handle, logger, now_to_datenow):
    controller = DL850Controller(logger, lambda *_: None, now_to_datenow)
    controller.handle = handle
    return controller.send_save_picture()
