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


def build_power_group_screen(channel_id, *, harmonics=True):
    """构造电力组测试页面的 XML 片段。

    Args:
        channel_id: PowerModule 的 ChannelID（动态值）
        harmonics: 谐波未开启时，谐波表的 RMS / 基波百分比 / 相角列也不显示。

    Returns:
        str: 完整的 <MeasurementScreen> XML 字符串
    """
    instrument_channel = _INSTRUMENT_CHANNEL_TEMPLATE.format(channel_id=channel_id)
    if not harmonics:
        hidden = "False"
        for prop in ("rmsLevelVisible", "percentFundamentalVisible", "phaseAngleVisible"):
            instrument_channel = re.sub(
                r'(<Property name="%s"><BooleanValue>)(True|False)(</BooleanValue>)' % prop,
                r"\g<1>%s\g<3>" % hidden,
                instrument_channel,
                count=1,
            )
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


def inject_power_group_screen(xml, channel_id, *, harmonics=True):
    """将电力组测试页面注入到 XML 的 MeasurementScreens 中。

    如果已存在电力组页面，先删除旧的，再注入新的（用最新配置替换）。
    如果 MeasurementScreens 不存在，则创建。

    Args:
        xml: 完整的设备 XML 字符串
        channel_id: PowerModule 的 ChannelID

    Returns:
        tuple: (修改后的 XML, 是否修改, 日志消息)
    """
    screen_xml = build_power_group_screen(channel_id, harmonics=harmonics)

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


# 需要启用的通道 ShortId 前缀（本体 + 子字段全部启用）
_CHANNEL_PREFIXES = [
    # Voltage (U)
    'U1_', 'U2_', 'U3_', 'U_', 'U12_', 'U23_', 'U31_',
    # Current (I)
    'I1_', 'I2_', 'I3_', 'I_', 'I4_',
    # Active Power (P)
    'P1_', 'P2_', 'P3_', 'P_',
    # Reactive Power (Q)
    'Q1_', 'Q2_', 'Q3_', 'Q_',
    # Apparent Power (S)
    'S1_', 'S2_', 'S3_', 'S_',
    # Power Factor (PF)
    'PF1_', 'PF2_', 'PF3_', 'PF_',
    # Energy (W)
    'W1_', 'W2_', 'W3_', 'W_',
]
# 需要单独启用的特殊通道
_SPECIAL_CHANNELS = ['F_fund']

# 这三类是可选计算。原生 Oxygen 关掉后，对应测量项不再显示。
# 命名见 OXYGEN Power 通道表：U1_fluc_Pst、U1_h1RMS / U1_THD、U1_tRMS_rc。
_OPTIONAL_FEATURE_RES = (
    ("flicker", re.compile(r"(?i)_fluc(?:_|$)")),
    ("rolling", re.compile(r"(?i)_rc$")),
    ("harmonics", re.compile(r"(?i)(?:_THD|_THV|_h\d|_ih\d|_hf\d|_sh\d)")),
)


def optional_power_feature(short_id: str):
    """闪变 / 滚动计算 / 谐波通道。基本量（U1_tRMS、U1_fundRMS）返回 None。"""
    text = str(short_id or "")
    for name, pattern in _OPTIONAL_FEATURE_RES:
        if pattern.search(text):
            return name
    return None


def _queue_channel_bool(xml, pos, prop_name, target, label, replacements, *, before):
    window = xml[max(0, pos - 5000):pos] if before else xml[pos:min(len(xml), pos + 6000)]
    matches = list(re.finditer(
        r'(<Property name="%s"><BooleanValue>)(True|False)(</BooleanValue>)' % re.escape(prop_name),
        window,
    ))
    if not matches:
        return
    # 往前找离 ShortId 最近的 Used，往后找最近的 Neon/Active，避免改到上一条通道。
    found = matches[-1] if before else matches[0]
    if found.group(2) == target:
        return
    base = max(0, pos - 5000) if before else pos
    start = base + found.start(2)
    replacements.append((start, start + len(found.group(2)), target, label))


def _apply_channel_bools(xml, replacements):
    replacements.sort(key=lambda item: item[0], reverse=True)
    for start, end, new_val, label in replacements:
        xml = xml[:start] + new_val + xml[end:]
        print(f"[BuildTestPage] {label} -> {new_val}")
    return xml


def apply_optional_feature_channels(xml, *, flicker=False, harmonics=False, rolling=False):
    """按三个开关显示或隐藏闪变、谐波、滚动计算测量项。

    关闭时把对应通道 Used / Neon/Active 写成 False。只改功能布尔时，
    这些通道仍是 Used=True，Oxygen 里测量项还会留着。
    """
    wanted = {
        "flicker": "True" if flicker else "False",
        "harmonics": "True" if harmonics else "False",
        "rolling": "True" if rolling else "False",
    }
    replacements = []
    for match in re.finditer(r'ShortId"><StringValue>"([^"]+)"', xml):
        kind = optional_power_feature(match.group(1))
        if kind is None:
            continue
        target = wanted[kind]
        pos = match.start()
        short_id = match.group(1)
        _queue_channel_bool(
            xml, pos, "Used", target, f"{short_id}: Used", replacements, before=True
        )
        _queue_channel_bool(
            xml, pos, "Neon/Active", target, f"{short_id}: Neon/Active", replacements, before=False
        )
    return _apply_channel_bools(xml, replacements), [item[3] for item in replacements]


def enable_power_group_channels(xml):
    """启用电力组基本量（U/I/P/Q/S/PF/W/F）。

    闪变、谐波、滚动计算通道不在这里打开，交给三个开关决定。
    通过匹配 ShortId 前缀来定位通道，设置 Used=True 和 Neon/Active=True。

    Returns:
        tuple: (修改后的xml, 启用数量)
    """
    replacements = []

    for m in re.finditer(r'ShortId"><StringValue>"([^"]+)"', xml):
        short_id = m.group(1)
        pos = m.start()
        if optional_power_feature(short_id):
            continue

        # 判断是否是需要启用的通道
        is_prefix = any(short_id.startswith(pfx) for pfx in _CHANNEL_PREFIXES)
        is_special = short_id in _SPECIAL_CHANNELS
        if not (is_prefix or is_special):
            continue

        # 设置 Used=True
        before = xml[max(0, pos - 5000):pos]
        used_match = re.search(r'(<Property name="Used"><BooleanValue>)(True|False)(</BooleanValue>)', before)
        if used_match and used_match.group(2) == 'False':
            start = max(0, pos - 5000) + used_match.start(2)
            end = start + len(used_match.group(2))
            replacements.append((start, end, 'True', f'{short_id}: Used'))

        # 设置 Neon/Active=True
        after = xml[pos:min(len(xml), pos + 6000)]
        neon_match = re.search(r'(<Property name="Neon/Active"><BooleanValue>)(True|False)(</BooleanValue>)', after)
        if neon_match and neon_match.group(2) == 'False':
            start = pos + neon_match.start(2)
            end = start + len(neon_match.group(2))
            replacements.append((start, end, 'True', f'{short_id}: Neon/Active'))

    # 从后往前替换（避免位置偏移）
    replacements.sort(key=lambda x: x[0], reverse=True)
    for start, end, new_val, label in replacements:
        xml = xml[:start] + new_val + xml[end:]
        print(f"[BuildTestPage] {label} -> True")

    return xml, len(replacements)


# 构造测试页时不要顺手打开这三项。设备侧默认经常是全开，
# 闪变/谐波/滚动计算会拖慢刷新，只有对应试验自己去开。
_FEATURES_OFF_ON_BUILD = (
    "POWER/Features/Flicker",
    "POWER/Features/Harmonics",
    "POWER/Features/Rolling",
)


def feature_flags_from_ui(ui) -> dict:
    """德威创设备页三个勾选。没有控件时按关闭。"""
    def _on(name: str) -> bool:
        box = getattr(ui, name, None) if ui is not None else None
        try:
            return bool(box.isChecked())
        except Exception:
            return False

    return {
        "flicker": _on("checkBox_DEW_EnableFlicker"),
        "harmonics": _on("checkBox_DEW_EnableHarmonics"),
        "rolling": _on("checkBox_DEW_EnableRolling"),
    }


def set_power_features(xml, *, flicker=False, harmonics=False, rolling=False):
    """按勾选把闪变、谐波、滚动计算写成 True 或 False。

    Returns:
        tuple: (修改后的 xml, 实际改过值的属性名列表)
    """
    wanted = {
        "POWER/Features/Flicker": "True" if flicker else "False",
        "POWER/Features/Harmonics": "True" if harmonics else "False",
        "POWER/Features/Rolling": "True" if rolling else "False",
    }
    changed = []

    def _apply(match, feature_name, target):
        if match.group(2) != target:
            changed.append(feature_name)
        return match.group(1) + target + match.group(3)

    for feature_name, target in wanted.items():
        pattern = (
            r'(<Property name="'
            + re.escape(feature_name)
            + r'">\s*<BooleanValue>)(True|False)(</BooleanValue>)'
        )
        xml = re.sub(
            pattern,
            lambda match, name=feature_name, value=target: _apply(match, name, value),
            xml,
        )
    return xml, changed


def disable_heavy_power_features(xml):
    """把闪变、谐波、滚动计算写成 False。"""
    return set_power_features(xml, flicker=False, harmonics=False, rolling=False)


def build_test_page_from_device(controller, log_fn=None, features=None):
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

    # 3. 启用电力组基本量。闪变 / 谐波 / 滚动计算不在这一步打开。
    xml, enabled_count = enable_power_group_channels(xml)
    _log(f"启用了 {enabled_count} 个电力组基本量（Used + Neon/Active）")

    # 3b. 三个开关：功能布尔 + 对应测量通道是否显示
    flags = features or {}
    flicker_on = bool(flags.get("flicker"))
    harmonics_on = bool(flags.get("harmonics"))
    rolling_on = bool(flags.get("rolling"))
    xml, hidden = apply_optional_feature_channels(
        xml, flicker=flicker_on, harmonics=harmonics_on, rolling=rolling_on
    )
    if hidden:
        _log("可选测量项已按开关更新 %s 处" % len(hidden))
    xml, changed = set_power_features(
        xml,
        flicker=flicker_on,
        harmonics=harmonics_on,
        rolling=rolling_on,
    )
    opened = [
        name for name, key in (
            ("闪变", "flicker"),
            ("谐波", "harmonics"),
            ("滚动计算", "rolling"),
        ) if flags.get(key)
    ]
    if opened:
        _log("已按勾选打开: " + "、".join(opened))
    else:
        _log("闪变、谐波、滚动计算未勾选，保持关闭")
    if changed:
        _log("功能开关已改: " + "、".join(changed))

    # 4. 注入测试页面
    xml, modified, msg = inject_power_group_screen(
        xml, channel_id, harmonics=harmonics_on
    )
    _log(msg)
    if not modified:
        return True

    # 5. 发送到设备
    _log(f"发送修改后的 XML: {len(xml)} 字符")
    if controller.send_apply_config(xml):
        _log("测试界面构造完成")
        return True
    else:
        _log("发送失败")
        return False
