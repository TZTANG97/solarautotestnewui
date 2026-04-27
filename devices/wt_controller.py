from devices.scpi_common import _configure_scpi_resource


class WT3000Controller:
    """WT3000 控制器，统一管理连接、断开和基础命令。"""

    def __init__(self, logger, show_message, rm, baud_rate="9600"):
        self.logger = logger
        self.show_message = show_message
        self.rm = rm
        self.baud_rate = baud_rate
        self.handle = None
        self.connected = False
        self.resource = ''

    def _candidate_resources(self, tcp_addr):
        if not tcp_addr:
            return []
        resources = []
        if tcp_addr.startswith("TCPIP") or tcp_addr.startswith("GPIB") or tcp_addr.startswith("ASRL"):
            resources.append(tcp_addr)
        if ":" in tcp_addr and not tcp_addr.startswith("TCPIP"):
            ip, port = tcp_addr.split(":", 1)
            resources.extend([
                f"TCPIP0::{ip}::{port}::SOCKET",
                f"TCPIP::{ip}::{port}::INSTR",
                f"TCPIP0::{ip}::inst0::INSTR",
            ])
        elif tcp_addr.count(".") == 3:
            ip = tcp_addr
            resources.extend([
                f"TCPIP0::{ip}::inst0::INSTR",
                f"TCPIP::{ip}::INSTR",
                f"TCPIP0::{ip}::5025::SOCKET",
                f"TCPIP0::{ip}::10001::SOCKET",
            ])
        else:
            resources.append(tcp_addr)
        # 去重但保持顺序
        seen = set()
        ordered = []
        for item in resources:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered

    def connect(self, tcp_addr):
        """连接 WT3000，并应用串口参数。"""
        last_error = None
        handle = None
        for resource_string in self._candidate_resources(tcp_addr):
            try:
                self.logger.info(f"WT3000尝试连接: {resource_string}")
                print(f"WT3000尝试连接: {resource_string}")
                handle = self.rm.open_resource(resource_string)
                _configure_scpi_resource(handle)
                handle.timeout = 10000
                try:
                    handle.baud_rate = int(self.baud_rate)
                    handle.data_bits = 8
                    handle.parity = __import__('pyvisa').constants.Parity.none
                    handle.stop_bits = __import__('pyvisa').constants.StopBits.one
                    handle.flow_control = __import__('pyvisa').constants.VI_ASRL_FLOW_NONE
                except Exception as serial_cfg_err:
                    self.logger.info(f"WT3000串口参数设置失败: {serial_cfg_err}")
                    print(f"WT3000串口参数设置失败: {serial_cfg_err}")
                break
            except Exception as e:
                last_error = e
                self.logger.info(f"WT3000 connect error {e}")
                print(f"WT3000 connect error {e}")
                handle = None
        if handle is None:
            try:
                raise last_error if last_error is not None else Exception("WT3000连接失败")
            except Exception as e:
                self.logger.info(f"WT3000 connect error {e}")
                print(f"WT3000 connect error {e}")
                self.show_message(f"WT3000连接失败：{e}", None)
                self.connected = False
                self.handle = None
                self.resource = ''
                return None, '0'
        try:
            handle.write(":NUMERIC:FORMAT ASCII")
        except Exception as e:
            self.logger.info("command :NUMERIC:FORMAT ASCII send failed")
            print(f"command :NUMERIC:FORMAT ASCII send failed: {e}")
        else:
            self.logger.info("WT3000 发送ASCII 命令连接成功")
            print("WT3000 发送ASCII 命令连接成功")
        self.handle = handle
        self.connected = True
        self.resource = tcp_addr
        return self.handle, '1'

    def disconnect(self, safe_close_handle):
        """断开 WT3000 连接。"""
        safe_close_handle(self.handle)
        self.handle = None
        self.connected = False
        self.resource = ''
        return None, '0'


def connect_wt3000(tcp_addr, rm, logger, show_message, baud_rate):
    controller = WT3000Controller(logger, show_message, rm, baud_rate)
    return controller.connect(tcp_addr)


def disconnect_wt3000(handle, safe_close_handle):
    safe_close_handle(handle)
    return None, '0'
