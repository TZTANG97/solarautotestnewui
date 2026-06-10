"""
DEWETRON 测试界面构造模块（独立补丁，不修改现有代码）。

功能：根据用户在 UI 中的接线设置，自动在 XML 中构造电力组测试页面（MeasurementScreen）。
"""

import re


# PowerModule InstrumentChannel 模板（静态部分）
_INSTRUMENT_CHANNEL_TEMPLATE = '''<InstrumentChannel channel_id="{channel_id}"><InstrumentChannelProperties><Property name="thresholds"><PropertyListValue><Property name="baseColor"><ColorValue>#6e6e6e</ColorValue></Property><Property name="topThreshold"><PropertyListValue><Property name="value"><DoubleValue>0</DoubleValue></Property><Property name="color"><ColorValue>#ff0000</ColorValue></Property><Property name="active"><BooleanValue>False</BooleanValue></Property></PropertyListValue></Property><Property name="bottomThreshold"><PropertyListValue><Property name="value"><DoubleValue>0</DoubleValue></Property><Property name="color"><ColorValue>#ff0000</ColorValue></Property><Property name="active"><BooleanValue>False</BooleanValue></Property></PropertyListValue></Property></PropertyListValue></Property><Property name="displayedValue"><PropertyListValue><Property name="mode"><SignedValue>1</SignedValue></Property><Property name="window"><DoubleValue>0.20000000000000001</DoubleValue></Property></PropertyListValue></Property><Property name="captionVisible"><BooleanValue>True</BooleanValue></Property><Property name="borderVisible"><BooleanValue>True</BooleanValue></Property><Property name="colorTheme"><SignedValue>0</SignedValue></Property><Property name="activeInstrument"><SignedValue>0</SignedValue></Property><Property name="activePhase"><SignedValue>0</SignedValue></Property><Property name="cursorPosition"><SignedValue>1</SignedValue></Property><Property name="cursorPositionType"><SignedValue>0</SignedValue></Property><Property name="llChannelsVisible"><BooleanValue>False</BooleanValue></Property><Property name="spectrumHFVisible"><BooleanValue>False</BooleanValue></Property><Property name="spectrumCursorVisible"><BooleanValue>False</BooleanValue></Property><Property name="rmsLevelVisible"><BooleanValue>True</BooleanValue></Property><Property name="percentFundamentalVisible"><BooleanValue>True</BooleanValue></Property><Property name="phaseAngleVisible"><BooleanValue>True</BooleanValue></Property><Property name="orderFilter"><SignedValue>0</SignedValue></Property></InstrumentChannelProperties></InstrumentChannel>'''

# CommonInstrumentProperties 模板（电力组通用属性）
_COMMON_INSTRUMENT_PROPERTIES = '''<CommonInstrumentProperties type="oxy::power_group"><Property name="thresholds"><PropertyListValue><Property name="baseColor"><ColorValue>#6e6e6e</ColorValue></Property><Property name="topThreshold"><PropertyListValue><Property name="value"><DoubleValue>0</DoubleValue></Property><Property name="color"><ColorValue>#ff0000</ColorValue></Property><Property name="active"><BooleanValue>False</BooleanValue></Property></PropertyListValue></Property><Property name="bottomThreshold"><PropertyListValue><Property name="value"><DoubleValue>0</DoubleValue></Property><Property name="color"><ColorValue>#ff0000</ColorValue></Property><Property name="active"><BooleanValue>False</BooleanValue></Property></PropertyListValue></Property></PropertyListValue></Property><Property name="displayedValue"><PropertyListValue><Property name="mode"><SignedValue>1</SignedValue></Property><Property name="window"><DoubleValue>0.20000000000000001</DoubleValue></Property></PropertyListValue></Property><Property name="captionVisible"><BooleanValue>True</BooleanValue></Property><Property name="borderVisible"><BooleanValue>True</BooleanValue></Property><Property name="colorTheme"><SignedValue>0</SignedValue></Property><Property name="activeInstrument"><SignedValue>0</SignedValue></Property><Property name="activePhase"><SignedValue>0</SignedValue></Property><Property name="cursorPosition"><SignedValue>1</SignedValue></Property><Property name="cursorPositionType"><SignedValue>0</SignedValue></Property><Property name="llChannelsVisible"><BooleanValue>False</BooleanValue></Property><Property name="spectrumHFVisible"><BooleanValue>False</BooleanValue></Property><Property name="spectrumCursorVisible"><BooleanValue>False</BooleanValue></Property><Property name="rmsLevelVisible"><BooleanValue>True</BooleanValue></Property><Property name="percentFundamentalVisible"><BooleanValue>True</BooleanValue></Property><Property name="phaseAngleVisible"><BooleanValue>True</BooleanValue></Property><Property name="orderFilter"><SignedValue>0</SignedValue></Property></CommonInstrumentProperties>'''


def find_power_group_channel_id(xml):
    """从 XML 中查找 PowerGroup (PowerModule) 的 ChannelID。

    PowerModule 的 Channel 体很大（~10K chars），ShortId 在末尾附近，
    所以需要用较大的回看窗口。

    Returns:
        str: ChannelID 字符串，未找到返回 None
    """
    LOOKBACK = 15000  # PowerModule Channel 体可达 ~10K chars
    for m in re.finditer(r'ShortId"><StringValue>"PowerGroup"', xml):
        back = xml[max(0, m.start() - LOOKBACK):m.start()]
        ch = re.search(r'<Channel id="(\d+)">', back)
        if ch:
            return ch.group(1)
    return None


def build_power_group_screen(channel_id):
    """构造电力组测试页面的 XML 片段。

    Args:
        channel_id: PowerModule 的 ChannelID（动态值）

    Returns:
        str: 完整的 <MeasurementScreen> XML 字符串
    """
    instrument_channel = _INSTRUMENT_CHANNEL_TEMPLATE.format(channel_id=channel_id)
    return (
        '<MeasurementScreen>'
        '<InstrumentGrid type="oxy::power_group" columns="0">'
        '<InstrumentLocation x="0" y="0" w="1" h="1"/>'
        '<InstrumentProperties>'
        '<Property name="backgroundVisible"><BooleanValue>False</BooleanValue></Property>'
        '</InstrumentProperties>'
        '<Instrument>'
        f'{instrument_channel}'
        '</Instrument>'
        f'{_COMMON_INSTRUMENT_PROPERTIES}'
        '</InstrumentGrid>'
        '</MeasurementScreen>'
    )


def inject_power_group_screen(xml, channel_id):
    """将电力组测试页面注入到 XML 的 MeasurementScreens 中。

    如果已存在电力组页面，先删除旧的，再注入新的（用最新配置替换）。
    如果 MeasurementScreens 不存在，则创建。

    Args:
        xml: 完整的设备 XML 字符串
        channel_id: PowerModule 的 ChannelID

    Returns:
        tuple: (修改后的 XML, 是否修改, 日志消息)
    """
    screen_xml = build_power_group_screen(channel_id)

    # 先删除已有的电力组页面（InstrumentGrid type="oxy::power_group"）
    old_pattern = re.compile(
        r'<MeasurementScreen><InstrumentGrid type="oxy::power_group".*?</InstrumentGrid></MeasurementScreen>',
        re.DOTALL
    )
    old_matches = old_pattern.findall(xml)
    if old_matches:
        xml = old_pattern.sub('', xml)
        print(f"[BuildTestPage] 已删除 {len(old_matches)} 个旧电力组页面")

    # 查找 MeasurementScreens 标签
    ms_match = re.search(r'(<MeasurementScreens[^>]*>)', xml)
    if ms_match:
        insert_pos = ms_match.end()
        xml = xml[:insert_pos] + screen_xml + xml[insert_pos:]
        return xml, True, f"已注入电力组测试页面（channel_id={channel_id}）"
    else:
        channels_end = xml.find('</Channels>')
        if channels_end >= 0:
            insert_pos = channels_end + len('</Channels>')
            new_screens = f'<MeasurementScreens active_screen="0">{screen_xml}</MeasurementScreens>'
            xml = xml[:insert_pos] + new_screens + xml[insert_pos:]
            return xml, True, f"已创建 MeasurementScreens 并注入电力组测试页面（channel_id={channel_id}）"
        else:
            return xml, False, "找不到 </Channels> 标记，无法注入测试页面"


def build_test_page_from_device(controller, log_fn=None):
    """主入口：从设备读取 XML，构造电力组测试页面，发送回设备。

    Args:
        controller: DewetronController 实例（需已连接）
        log_fn: 日志回调函数，接收字符串参数

    Returns:
        bool: 是否成功
    """
    def _log(msg):
        print(f"[BuildTestPage] {msg}")
        if log_fn:
            log_fn(msg)

    _log("=== 开始构造测试界面 ===")

    # 1. 从设备读取 XML
    xml = controller._query(":SETUP:READ?")
    if not xml:
        _log("读取设备 XML 失败")
        return False
    idx = xml.find('<?xml')
    if idx > 0:
        xml = xml[idx:]
    _log(f"读取 XML: {len(xml)} 字符")

    # 2. 查找 PowerGroup ChannelID
    channel_id = find_power_group_channel_id(xml)
    if not channel_id:
        _log("未找到 PowerGroup 通道，请先创建电力组")
        return False
    _log(f"PowerGroup ChannelID: {channel_id}")

    # 3. 注入测试页面
    xml, modified, msg = inject_power_group_screen(xml, channel_id)
    _log(msg)
    if not modified:
        return True

    # 4. 发送到设备
    _log(f"发送修改后的 XML: {len(xml)} 字符")
    if controller.send_apply_config(xml):
        _log("测试界面构造完成")
        return True
    else:
        _log("发送失败")
        return False
