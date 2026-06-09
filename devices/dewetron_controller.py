from devices.scpi_common import _configure_scpi_resource


class DewetronController:
    """DEWETRON 功率分析仪控制器，统一管理连接、断开和命令发送。"""

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
        """连接 DEWETRON 设备。

        连接参数（参考 DEWETRON 文档）：
        - 协议：TCP
        - 端口号：10001
        - 编码：ASCII
        - 消息终止符：LF (\\n) 或 CR LF (\\r\\n)
        - 连接限制：只允许 1 个客户端连接
        """
        # 如果用户输入的是裸 IP（如 192.168.40.11），构造标准 VISA TCPIP 资源字符串
        if tcp_addr and not tcp_addr.upper().startswith('TCPIP'):
            ip = tcp_addr.strip()
            # 去掉可能带的端口后缀（如 192.168.40.11:10001）
            if ':' in ip:
                ip = ip.split(':')[0]
            visa_addr = f"TCPIP0::{ip}::10001::SOCKET"
        else:
            visa_addr = tcp_addr

        try:
            handle = self.rm.open_resource(visa_addr)
            # 强制设置 ASCII 编码
            try:
                handle.encoding = 'ascii'
            except Exception:
                pass
            _configure_scpi_resource(handle)
        except Exception as e:
            print(f"DEWETRON连接失败: {e}")
            self.logger.info(f"DEWETRON连接失败: {e}")
            self.show_message("DEWETRON连接失败，请检查设备地址和连线", self.ui)
            self.handle = None
            self.connected = False
            self.resource = ''
            return None, '0'
        self.logger.info("DEWETRON连接成功")
        print("DEWETRON连接成功")
        self.handle = handle
        self.connected = True
        self.resource = visa_addr
        return self.handle, '1'

    def disconnect(self, safe_close_handle):
        """断开 DEWETRON 设备。"""
        safe_close_handle(self.handle)
        self.handle = None
        self.connected = False
        self.resource = ''
        return None, '0'

    def _send(self, command, success_log, error_prefix):
        """发送 SCPI 命令。"""
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
        """发送 START 命令（暂未实现具体 SCPI 命令）。"""
        # TODO: 替换为 DEWETRON 实际 SCPI 命令
        return self._send("START", "SendMessageStartToDEWETRON:START", "Send start message to DEWETRON")

    def send_stop(self):
        """发送 STOP 命令（暂未实现具体 SCPI 命令）。"""
        # TODO: 替换为 DEWETRON 实际 SCPI 命令
        return self._send("STOP", "SendMessageStopToDEWETRON:STOP", "Send stop message to DEWETRON")

    def send_configure(self, wiring_type, v_channel, i_channel, v_ratio, i_ratio, sampling_rate, test_channels):
        """发送配置命令（暂未实现具体 SCPI 命令）。"""
        # TODO: 替换为 DEWETRON 实际 SCPI 配置命令
        self.logger.info(f"DEWETRON configure: wiring={wiring_type}, v={v_channel}, i={i_channel}")
        return True

    def send_load_config(self, config_path):
        """发送 :SETUP:LOAD 命令，让设备重新加载配置文件。"""
        cmd = f':SETUP:LOAD "{config_path}"'
        return self._send(cmd, f"DEWETRON load config: {config_path}", "Send load config to DEWETRON")


def connect_dewetron(tcp_addr, rm, ui, logger, show_message):
    """便捷连接函数。"""
    controller = DewetronController(logger, show_message, lambda: '', rm=rm, ui=ui)
    return controller.connect(tcp_addr)


def disconnect_dewetron(handle, safe_close_handle):
    """便捷断开函数。"""
    safe_close_handle(handle)
    return None, '0'
