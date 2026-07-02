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

    def _reconnect(self):
        """尝试重新连接 DEWETRON 设备。成功返回 True。"""
        saved_resource = self.resource
        self.handle = None
        self.connected = False
        if not saved_resource:
            return False
        print(f"[DEWETRON] 尝试重连: {saved_resource}")
        self.logger.info(f"DEWETRON 尝试重连: {saved_resource}")
        handle, status = self.connect(saved_resource)
        if status == '1':
            print("[DEWETRON] 重连成功")
            self.logger.info("DEWETRON 重连成功")
            return True
        print("[DEWETRON] 重连失败")
        self.logger.info("DEWETRON 重连失败")
        return False

    def _send(self, command, success_log, error_prefix, timeout_ms=None):
        """发送 SCPI 命令。连接丢失时自动重连并重试一次。"""
        if self.handle is None:
            return False
        try:
            if timeout_ms is not None:
                self.handle.timeout = timeout_ms
            self.handle.write(command)
        except Exception as e:
            err_str = str(e)
            if 'CONN_LOST' in err_str or '1073807194' in err_str:
                print(f"[DEWETRON] 连接丢失: {e}")
                self.logger.info(f"DEWETRON 连接丢失: {e}")
                self.connected = False
                if self._reconnect():
                    try:
                        if timeout_ms is not None:
                            self.handle.timeout = timeout_ms
                        self.handle.write(command)
                    except Exception as e2:
                        strtimenow = self.now_to_datenow()
                        self.logger.info(f"{error_prefix} (重试) error :{e2}")
                        print(f'{strtimenow} {error_prefix} (重试) error :{e2}')
                        return False
                else:
                    return False
            else:
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

    def _query(self, command, timeout_ms=30000):
        """发送 SCPI 查询命令并返回响应。连接丢失时自动重连并重试一次。"""
        if self.handle is None:
            return None
        try:
            self.handle.timeout = timeout_ms
            resp = self.handle.query(command)
            return resp.strip()
        except Exception as e:
            err_str = str(e)
            if 'CONN_LOST' in err_str or '1073807194' in err_str:
                print(f"[DEWETRON] query 连接丢失: {e}")
                self.logger.info(f"DEWETRON query 连接丢失: {e}")
                self.connected = False
                if self._reconnect():
                    try:
                        self.handle.timeout = timeout_ms
                        resp = self.handle.query(command)
                        return resp.strip()
                    except Exception as e2:
                        print(f"DEWETRON query error (重试): {e2}")
                        return None
                return None
            print(f"DEWETRON query error: {e}")
            self.logger.info(f"DEWETRON query error: {e}")
            return None

    def read_channel_id_map(self):
        """从设备当前配置中读取 ShortId -> ChannelID 映射。

        Returns:
            tuple: (dict, str) — {short_id: channel_id} 和原始 XML
        """
        xml = self._query(":SETUP:READ?", timeout_ms=30000)
        if not xml:
            print("[DEWETRON] read_channel_id_map: :SETUP:READ? 返回空")
            return {}, None
        decl_pos = xml.find('<?xml')
        if decl_pos > 0:
            xml = xml[decl_pos:]
        elif decl_pos < 0:
            # 没有 <?xml 声明，检查是否是有效 XML
            if '<MeasurementConfig' not in xml:
                print(f"[DEWETRON] read_channel_id_map: 返回内容不是有效 XML (前100字节: {xml[:100]})")
                return {}, None

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
        print(f"[DEWETRON] --- 设备通道 ID 映射 ({len(channel_map)} 个) ---")
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
            # 大文件写入需要更长超时（默认 10s 对 750K+ 数据不够）
            return self._send(full_cmd, "[DEWETRON] :SETUP:APPLY 发送完成", "DEWETRON :SETUP:APPLY", timeout_ms=60000)
        except Exception as e:
            strtimenow = self.now_to_datenow()
            print(f'{strtimenow} DEWETRON :SETUP:APPLY error: {e}')
            self.logger.info(f"DEWETRON :SETUP:APPLY error: {e}")
            return False

    @staticmethod
    def modify_xml(xml_string, wiring_type, channel_map, channel_id_map=None, input_channels=None,
                   acquisition_rate=None, downsampling=None, frequency_channel=None,
                   flicker_type=None, nominal_voltage=None, pst_time=None, plt_time=None,
                   short_circuit_power=None, flicker_enabled=None, rolling_enabled=None,
                   export_fields=None, decimal_places=None, realtime_waveform=None):
        """根据 UI 设置修改 XML 配置字符串。

        Args:
            xml_string: 原始 XML 模板内容
            wiring_type: 接线类型 (0=1P2W, 1=1P3W, 2=2V2A, 3=3P3W, 4=3P4W)
            channel_map: dict，键为 slot_name (如 'U1', 'I1')，值为通道名 (如 'AI 1/U1')
            channel_id_map: dict，ShortId -> ChannelID 映射（从设备读取）。为 None 时跳过 InputChannels 映射。
            input_channels: dict，设备原始 InputChannels 映射 {slot: channel_id}。为 None 时跳过。
            acquisition_rate: 最大刷新率 (如 '100', 'Default')，为 None 时不修改。
            downsampling: 通道二次采样 (如 'Auto', '2', '关')，为 None 时不修改。
            frequency_channel: 输入通道 (如 'AI 1/U1')，为 None 时不修改。映射到 POWER/FrequencyChannel。
            flicker_type: 加权类型 (如 'AUTO', '230V50Hz')，为 None 时不修改。
            nominal_voltage: 标称电压 (如 '230')，为 None 时不修改。
            pst_time: 短时闪变计算时间 (如 '10')，为 None 时不修改。
            plt_time: 长时闪变计算时间 (如 '120')，为 None 时不修改。
            short_circuit_power: 短路视在功率 (如 '50')，为 None 时不修改。
            flicker_enabled: 闪变功能开关 (True/False)，为 None 时不修改。
            rolling_enabled: 滚动计算开关 (True/False)，为 None 时不修改。
            export_fields: 导出字段列表 (如 ['U1_tRMS', 'I1_fundRMS'])，为 None 时不修改。
                          修改 XML 中 ExportSetup/ExportChannels 部分，仅保留选中的通道。
                          需要 channel_id_map 来将 ShortId 映射到 ChannelID。
            decimal_places: 导出小数位数 (如 3, 6)，为 None 时不修改。对应 EXPORT_VALUE_PRECISION。
            realtime_waveform: 实时波形开关 (True/False)，为 None 时不修改。对应 WAVEFORM。
        Returns:
            修改后的 XML 字符串
        """
        WIRING_TYPE_MAP = {
            0: 'AC_1P2W', 1: 'AC_1P3W', 2: 'AC_2V2A',
            3: 'AC_3P3W', 4: 'AC_3P4W',
        }
        xml = xml_string

        # 1. 修改接线类型（wiring_type 为 None 时跳过）
        wiring_enum = WIRING_TYPE_MAP.get(wiring_type, 'AC_1P2W') if wiring_type is not None else None
        old_wiring = re.search(
            r'(<Property name="POWER/WiringType">\s*<EnumValue enum="PowerWiringType">)([^<]+)(</EnumValue>)',
            xml
        )
        if wiring_enum is not None and old_wiring:
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

        # 3.5 修改导出设置的 ExportChannels（export_fields 不为 None 时）
        # 导出设置页面的勾选通道存储在 ExportSetup/ExportChannels 中
        if export_fields is not None:
            export_set = set(export_fields)
            print(f"[DEWETRON] 导出字段选择: {len(export_set)} 个字段")

            # 构建 ShortId -> ChannelID 反向映射（从 XML 中读取）
            short_to_cid = {}
            for m in re.finditer(r'<Channel id="(\d+)">(.*?)</Channel>', xml, re.DOTALL):
                ch_id = m.group(1)
                ch_body = m.group(2)
                sid_m = re.search(r'ShortId"><StringValue>"([^"]+)"', ch_body)
                if sid_m:
                    short_to_cid[sid_m.group(1)] = ch_id

            # 收集选中字段的 ChannelID
            export_channel_ids = []
            for field in export_set:
                cid = short_to_cid.get(field)
                if cid:
                    export_channel_ids.append(cid)
                else:
                    print(f"[DEWETRON] 导出字段 {field}: 未找到 ChannelID，跳过")

            # 构建新的 ExportChannels XML
            new_export_channels = '<ExportChannels>'
            for cid in export_channel_ids:
                new_export_channels += f'<ExportChannel channel_id="{cid}"/>'
            new_export_channels += '</ExportChannels>'

            # 替换旧的 ExportChannels
            ec_match = re.search(r'<ExportChannels>.*?</ExportChannels>', xml, re.DOTALL)
            if ec_match:
                old_len = ec_match.end() - ec_match.start()
                xml = xml[:ec_match.start()] + new_export_channels + xml[ec_match.end():]
                print(f"[DEWETRON] ExportChannels 已替换: {len(export_channel_ids)} 个通道 (原 {old_len} 字节 -> 新 {len(new_export_channels)} 字节)")
            else:
                # 如果没有 ExportChannels，找 ExportSettings 并在其中插入
                es_match = re.search(r'<ExportSettings[^>]*>', xml)
                if es_match:
                    insert_pos = es_match.end()
                    xml = xml[:insert_pos] + new_export_channels + xml[insert_pos:]
                    print(f"[DEWETRON] 新增 ExportChannels: {len(export_channel_ids)} 个通道")
                else:
                    print("[DEWETRON] 未找到 ExportSettings，无法修改导出通道")
        else:
            print("[DEWETRON] 无 export_fields，跳过导出字段修改")

        # 3.6 修改导出属性（ExportProperties）
        # EXPORT_VALUE_PRECISION: 小数位数 (UnsignedInt64)
        # WAVEFORM: 实时波形 (BooleanValue)
        ep_match = re.search(r'<ExportProperties>(.*?)</ExportProperties>', xml, re.DOTALL)
        if ep_match:
            ep_xml = ep_match.group(0)
            ep_start = ep_match.start()
            ep_replacements = []

            if decimal_places is not None:
                old_prec = re.search(r'<Property name="EXPORT_VALUE_PRECISION"><UnsignedInt64>(\d+)</UnsignedInt64>', ep_xml)
                if old_prec and int(old_prec.group(1)) != decimal_places:
                    s = ep_start + old_prec.start(1)
                    e = s + len(old_prec.group(1))
                    ep_replacements.append((s, e, str(decimal_places), f'EXPORT_VALUE_PRECISION -> {decimal_places}'))

            if realtime_waveform is not None:
                old_wf = re.search(r'<Property name="WAVEFORM"><BooleanValue>(True|False)</BooleanValue>', ep_xml)
                if old_wf:
                    new_wf = 'True' if realtime_waveform else 'False'
                    if old_wf.group(1) != new_wf:
                        s = ep_start + old_wf.start(1)
                        e = s + len(old_wf.group(1))
                        ep_replacements.append((s, e, new_wf, f'WAVEFORM -> {new_wf}'))

            ep_replacements.sort(key=lambda x: x[0], reverse=True)
            for start, end, val, label in ep_replacements:
                xml = xml[:start] + val + xml[end:]
                print(f"[DEWETRON] {label}")
            if not ep_replacements:
                print("[DEWETRON] ExportProperties 无需修改（已与 UI 一致）")
        else:
            print("[DEWETRON] 未找到 ExportProperties，跳过导出属性修改")

        # 4. InputChannels 映射 — 用 UI 选择的通道 + 当前设备 ChannelID 构建
        # channel_map: {'U1': 'AI 1/U2', 'I1': 'AI 1/l2'}
        # channel_id_map: {'AI 1/U2': 13800436624556818457, ...}
        # channel_map 为空时跳过（避免将所有通道误设为 UNUSED）
        if channel_id_map and channel_map:
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

        # 6. 最大刷新率 (POWER/MaxUpdateRate) — PowerModule 全局属性，单位 ms
        if acquisition_rate is not None and acquisition_rate != 'Default':
            mu_replacements = []
            for m in re.finditer(r'(<Property name="POWER/MaxUpdateRate">\s*<StringValue>)"?([^"<]+)"?(</StringValue>)', xml):
                old_val = m.group(2).strip('"')
                if old_val != acquisition_rate:
                    mu_replacements.append((m.start(2), m.end(2), acquisition_rate, 'POWER/MaxUpdateRate'))
            mu_replacements.sort(key=lambda x: x[0], reverse=True)
            for start, end, val, label in mu_replacements:
                xml = xml[:start] + val + xml[end:]
                print(f"[DEWETRON] {label} -> {val} ms")
            if not mu_replacements:
                print("[DEWETRON] POWER/MaxUpdateRate 无需修改（已与 UI 一致）")

        # 7. 通道二次采样 (POWER/DataSubsampling) — PowerModule 全局属性
        # UI 显示 "关"，设备 XML 需要 "Off"
        DS_VALUE_MAP = {'关': 'Off', 'Auto': 'Auto'}
        if downsampling is not None:
            xml_value = DS_VALUE_MAP.get(downsampling, downsampling)
            ds_replacements = []
            for m in re.finditer(r'(<Property name="POWER/DataSubsampling">\s*<StringValue>)"?([^"<]+)"?(</StringValue>)', xml):
                if m.group(2) != xml_value:
                    ds_replacements.append((m.start(2), m.end(2), xml_value, 'POWER/DataSubsampling'))
            ds_replacements.sort(key=lambda x: x[0], reverse=True)
            for start, end, val, label in ds_replacements:
                xml = xml[:start] + val + xml[end:]
                print(f"[DEWETRON] {label} -> {val}")
            if not ds_replacements:
                print("[DEWETRON] POWER/DataSubsampling 无需修改（已与 UI 一致）")

        # 8. 输入通道 (POWER/FrequencyChannel) — 频率测量通道，存储 ChannelID
        if frequency_channel is not None and channel_id_map:
            fc_cid = channel_id_map.get(frequency_channel) or channel_id_map.get(frequency_channel.replace('/l', '/I'))
            if fc_cid:
                fc_replacements = []
                for m in re.finditer(r'(<Property name="POWER/FrequencyChannel">\s*<ChannelID>)(\d+)(</ChannelID>)', xml):
                    if m.group(2) != str(fc_cid):
                        fc_replacements.append((m.start(2), m.end(2), str(fc_cid), 'POWER/FrequencyChannel'))
                fc_replacements.sort(key=lambda x: x[0], reverse=True)
                for start, end, val, label in fc_replacements:
                    xml = xml[:start] + val + xml[end:]
                    print(f"[DEWETRON] {label} -> {val}")
                if not fc_replacements:
                    print("[DEWETRON] POWER/FrequencyChannel 无需修改（已与 UI 一致）")
            else:
                print(f"[DEWETRON] 输入通道 {frequency_channel}: 未找到 ChannelID，跳过")

        # ── 9. 闪变参数 ──
        # XML 中标签可能跨多行，用 \s* 匹配标签间的空白（含换行）
        flicker_replacements = []

        # 9a. FlickerType (EnumValue)
        if flicker_type is not None:
            for m in re.finditer(
                r'(<Property name="POWER/FlickerType">\s*<EnumValue enum="FlickerType">)([^<]+)(</EnumValue>)',
                xml
            ):
                if m.group(2) != flicker_type:
                    flicker_replacements.append((m.start(2), m.end(2), flicker_type, 'POWER/FlickerType'))

        # 9b. NominalVoltage (ScalarValue)
        if nominal_voltage is not None:
            for m in re.finditer(
                r'(<Property name="POWER/Flicker/NominalVoltage">\s*<ScalarValue>\s*<Value>)([^<]+)(</Value>)',
                xml
            ):
                if m.group(2) != nominal_voltage:
                    flicker_replacements.append((m.start(2), m.end(2), nominal_voltage, 'POWER/Flicker/NominalVoltage'))

        # 9c. PstAggregationTime (ScalarValue)
        if pst_time is not None:
            for m in re.finditer(
                r'(<Property name="POWER/Flicker/PstAggregationTime">\s*<ScalarValue>\s*<Value>)([^<]+)(</Value>)',
                xml
            ):
                if m.group(2) != pst_time:
                    flicker_replacements.append((m.start(2), m.end(2), pst_time, 'POWER/Flicker/PstAggregationTime'))

        # 9d. PltAggregationTime (ScalarValue)
        if plt_time is not None:
            for m in re.finditer(
                r'(<Property name="POWER/Flicker/PltAggregationTime">\s*<ScalarValue>\s*<Value>)([^<]+)(</Value>)',
                xml
            ):
                if m.group(2) != plt_time:
                    flicker_replacements.append((m.start(2), m.end(2), plt_time, 'POWER/Flicker/PltAggregationTime'))

        # 9e. ShortCircuitPower (ScalarValue)
        if short_circuit_power is not None:
            for m in re.finditer(
                r'(<Property name="POWER/Flicker/ShortCircuitPower">\s*<ScalarValue>\s*<Value>)([^<]+)(</Value>)',
                xml
            ):
                if m.group(2) != short_circuit_power:
                    flicker_replacements.append((m.start(2), m.end(2), short_circuit_power, 'POWER/Flicker/ShortCircuitPower'))

        # 9f. Features/Flicker (BooleanValue)
        if flicker_enabled is not None:
            bool_str = 'True' if flicker_enabled else 'False'
            for m in re.finditer(
                r'(<Property name="POWER/Features/Flicker">\s*<BooleanValue>)(True|False)(</BooleanValue>)',
                xml
            ):
                if m.group(2) != bool_str:
                    flicker_replacements.append((m.start(2), m.end(2), bool_str, 'POWER/Features/Flicker'))

        # 9g. Features/Rolling (BooleanValue)
        if rolling_enabled is not None:
            bool_str = 'True' if rolling_enabled else 'False'
            for m in re.finditer(
                r'(<Property name="POWER/Features/Rolling">\s*<BooleanValue>)(True|False)(</BooleanValue>)',
                xml
            ):
                if m.group(2) != bool_str:
                    flicker_replacements.append((m.start(2), m.end(2), bool_str, 'POWER/Features/Rolling'))

        flicker_replacements.sort(key=lambda x: x[0], reverse=True)
        for start, end, val, label in flicker_replacements:
            xml = xml[:start] + val + xml[end:]
            print(f"[DEWETRON] {label} -> {val}")
        if not flicker_replacements:
            print("[DEWETRON] 闪变参数无需修改（已与 UI 一致）")

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
