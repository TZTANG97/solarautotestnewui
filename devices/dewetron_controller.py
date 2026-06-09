from devices.scpi_common import _configure_scpi_resource
import re

# 未映射通道的 ChannelID
UNUSED_CHANNEL_ID = 18446744073709551615  # 0xFFFFFFFFFFFFFFFF


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
            # DEWETRON 返回的 XML 可能含中文，使用 utf-8 编码
            try:
                handle.encoding = 'utf-8'
            except Exception:
                pass
            _configure_scpi_resource(handle)
            # DEWETRON 使用 CR+LF 终止符
            try:
                handle.read_termination = '\r\n'
                handle.write_termination = '\r\n'
            except Exception:
                pass
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

    def _query(self, command):
        """发送 SCPI 查询命令并返回响应。失败返回 None。"""
        if self.handle is None:
            return None
        try:
            resp = self.handle.query(command)
            return resp.strip()
        except Exception as e:
            print(f"DEWETRON query error: {e}")
            return None

    def read_channel_id_map(self):
        """从设备当前配置中读取 ShortId -> ChannelID 映射。

        Returns:
            tuple: (dict, str) — {short_id: channel_id} 和原始 XML
        """
        xml = self._query(":SETUP:READ?")
        if not xml:
            print("[DEWETRON] read_channel_id_map: :SETUP:READ? 返回空")
            return {}, None
        decl_pos = xml.find('<?xml')
        if decl_pos > 0:
            xml = xml[decl_pos:]

        channel_map = {}
        for ch_match in re.finditer(r'<Channel id="(\d+)">(.*?)</Channel>', xml, re.DOTALL):
            ch_id = ch_match.group(1)
            ch_body = ch_match.group(2)
            sid_match = re.search(r'ShortId"><StringValue>"([^"]+)"', ch_body)
            if sid_match:
                short_id = sid_match.group(1)
                channel_map[short_id] = int(ch_id)
                if '/I' in short_id:
                    channel_map[short_id.replace('/I', '/l')] = int(ch_id)
        print("[DEWETRON] --- 设备通道 ID 映射 ---")
        for name, cid in sorted(channel_map.items()):
            if name.startswith('AI'):
                print(f"  {name} -> {cid}")
        return channel_map, xml

    def read_input_channels(self, xml):
        """从 XML 中读取 POWER/0 的 InputChannels 映射（设备原始映射）。

        Returns:
            dict: {slot_name: channel_id}
        """
        if not xml:
            return {}
        input_channels = {}
        for match in re.finditer(r'POWER/InputChannels/([A-Z]+\d+)"><ChannelID>(\d+)</ChannelID>', xml):
            slot = match.group(1)
            ch_id = int(match.group(2))
            input_channels[slot] = ch_id
        print("[DEWETRON] --- 设备 InputChannels 映射 ---")
        for slot, cid in sorted(input_channels.items()):
            print(f"  {slot} -> {cid}")
        return input_channels

    def send_apply_config(self, xml_string):
        """发送 :SETUP:APPLY 命令，使用 IEEE 488.2 定长块格式上传 XML。"""
        if self.handle is None:
            return False
        try:
            xml_bytes = xml_string.encode('utf-8')
            xml_len = len(xml_bytes)
            num_digits = len(str(xml_len))
            full_cmd = f":SETUP:APPLY #{num_digits}{xml_len}" + xml_string
            print(f"[DEWETRON] 发送 :SETUP:APPLY (XML: {xml_len} 字节, header: #{num_digits}{xml_len})")
            self.handle.write(full_cmd)
            import time
            time.sleep(2)
            try:
                err = self.handle.query(":SYSTEM:ERROR:ALL?")
                print(f"[DEWETRON] :SYSTEM:ERROR:ALL? -> {err.strip()}")
            except Exception:
                pass
            print(f"[DEWETRON] :SETUP:APPLY 发送完成")
            return True
        except Exception as e:
            strtimenow = self.now_to_datenow()
            print(f'{strtimenow} DEWETRON :SETUP:APPLY error: {e}')
            self.logger.info(f"DEWETRON :SETUP:APPLY error: {e}")
            return False

    @staticmethod
    def modify_xml(xml_string, wiring_type, channel_map, channel_id_map=None, input_channels=None):
        """根据 UI 设置修改 XML 配置字符串。

        Args:
            xml_string: 原始 XML 模板内容
            wiring_type: 接线类型 (0=1P2W, 1=1P3W, 2=2V2A, 3=3P3W, 4=3P4W)
            channel_map: dict，键为 slot_name (如 'U1', 'I1')，值为通道名 (如 'AI 1/U1')
            channel_id_map: dict，ShortId -> ChannelID 映射（从设备读取）。为 None 时跳过 InputChannels 映射。
            input_channels: dict，设备原始 InputChannels 映射 {slot: channel_id}。为 None 时跳过。
        Returns:
            修改后的 XML 字符串
        """
        WIRING_TYPE_MAP = {
            0: 'AC_1P2W', 1: 'AC_1P3W', 2: 'AC_2V2A',
            3: 'AC_3P3W', 4: 'AC_3P4W',
        }
        xml = xml_string

        # 1. 修改接线类型
        wiring_enum = WIRING_TYPE_MAP.get(wiring_type, 'AC_1P2W')
        old_wiring = re.search(
            r'(<Property name="POWER/WiringType"><EnumValue enum="PowerWiringType">)([^<]+)(</EnumValue>)',
            xml
        )
        if old_wiring:
            xml = xml[:old_wiring.start(2)] + wiring_enum + xml[old_wiring.end(2):]
            print(f"[DEWETRON] WiringType -> {wiring_enum}")

        # 2. 收集需要启用的通道 — 使用 UI 选择的通道（channel_map）
        enabled_channels = {ch for ch in channel_map.values() if ch}
        print(f"[DEWETRON] 使用用户 UI 选择: {enabled_channels}")

        # 3. 修改每个 Channel 的 Used 和 Neon/Active
        replacements = []
        for ch_name in enabled_channels:
            xml_ch_name = ch_name.replace('/l', '/I')
            short_id_pattern = f'ShortId"><StringValue>"{re.escape(xml_ch_name)}"'
            for match in re.finditer(short_id_pattern, xml):
                pos = match.start()
                before = xml[max(0, pos-5000):pos]
                used_match = re.search(r'(<Property name="Used"><BooleanValue>)(True|False)(</BooleanValue>)', before)
                if used_match:
                    start = max(0, pos-5000) + used_match.start(2)
                    end = start + len(used_match.group(2))
                    replacements.append((start, end, 'True', f'{ch_name}: Used'))
                after = xml[pos:min(len(xml), pos+6000)]
                neon_match = re.search(r'(<Property name="Neon/Active"><BooleanValue>)(True|False)(</BooleanValue>)', after)
                if neon_match:
                    start = pos + neon_match.start(2)
                    end = start + len(neon_match.group(2))
                    replacements.append((start, end, 'True', f'{ch_name}: Neon/Active'))

        replacements.sort(key=lambda x: x[0], reverse=True)
        for start, end, new_val, label in replacements:
            xml = xml[:start] + new_val + xml[end:]
            print(f"[DEWETRON] {label} -> True")

        # 4. InputChannels 映射 — 用 UI 选择的通道 + 当前设备 ChannelID 构建
        # channel_map: {'U1': 'AI 1/U2', 'I1': 'AI 1/l2'}
        # channel_id_map: {'AI 1/U2': 13800436624556818457, ...}
        if channel_id_map:
            ic_replacements = []
            for slot_name, ch_name in channel_map.items():
                if ch_name:
                    # UI 用小写 l，channel_id_map 用大写 I
                    cid = channel_id_map.get(ch_name) or channel_id_map.get(ch_name.replace('/l', '/I'))
                    if not cid:
                        print(f"[DEWETRON] InputChannels/{slot_name}: 未找到 {ch_name} 的 ChannelID")
                        continue
                    new_cid = str(cid)
                else:
                    new_cid = str(UNUSED_CHANNEL_ID)

                pattern = f'InputChannels/{slot_name}"'
                for match in re.finditer(re.escape(pattern), xml):
                    after = xml[match.end():match.end()+200]
                    cid_match = re.search(r'<ChannelID>(\d+)</ChannelID>', after)
                    if cid_match:
                        old_cid = cid_match.group(1)
                        if old_cid != new_cid:
                            start = match.end() + cid_match.start(1)
                            end = start + len(old_cid)
                            ic_replacements.append((start, end, new_cid, f'InputChannels/{slot_name}: {old_cid} -> {new_cid}'))

            # 未在 channel_map 中的槽位设为 UNUSED
            for slot_name in ['U1','U2','U3','U4','U5','U6','U7','U8','U9',
                              'I1','I2','I3','I4','I5','I6','I7','I8','I9']:
                if slot_name not in channel_map:
                    pattern = f'InputChannels/{slot_name}"'
                    for match in re.finditer(re.escape(pattern), xml):
                        after = xml[match.end():match.end()+200]
                        cid_match = re.search(r'<ChannelID>(\d+)</ChannelID>', after)
                        if cid_match:
                            old_cid = cid_match.group(1)
                            if old_cid != str(UNUSED_CHANNEL_ID):
                                start = match.end() + cid_match.start(1)
                                end = start + len(old_cid)
                                ic_replacements.append((start, end, str(UNUSED_CHANNEL_ID), f'InputChannels/{slot_name}: -> UNUSED'))

            ic_replacements.sort(key=lambda x: x[0], reverse=True)
            for start, end, new_val, label in ic_replacements:
                xml = xml[:start] + new_val + xml[end:]
                print(f"[DEWETRON] {label}")
            if not ic_replacements:
                print("[DEWETRON] InputChannels 映射无需修改（已与 UI 一致）")
        else:
            print("[DEWETRON] 无 channel_id_map，跳过 InputChannels 修改")

        return xml

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
