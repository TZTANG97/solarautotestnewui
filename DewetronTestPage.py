"""
DEWETRON 测试界面构造模块（独立补丁，不修改现有代码）。

功能：根据用户在 UI 中的接线设置，自动在 XML 中构造电力组测试页面（MeasurementScreen）。
"""

import re


# PowerModule InstrumentChannel 模板（静态部分）
_INSTRUMENT_CHANNEL_TEMPLATE = '''<InstrumentChannel channel_id="{channel_id}"><InstrumentChannelProperties><Property name="thresholds"><PropertyListValue><Property name="baseColor"><ColorValue>#6e6e6e</ColorValue></Property><Property name="topThreshold"><PropertyListValue><Property name="value"><DoubleValue>0</DoubleValue></Property><Property name="color"><ColorValue>#ff0000</ColorValue></Property><Property name="active"><BooleanValue>False</BooleanValue></Property></PropertyListValue></Property><Property name="bottomThreshold"><PropertyListValue><Property name="value"><DoubleValue>0</DoubleValue></Property><Property name="color"><ColorValue>#ff0000</ColorValue></Property><Property name="active"><BooleanValue>False</BooleanValue></Property></PropertyListValue></Property></PropertyListValue></Property><Property name="displayedValue"><PropertyListValue><Property name="mode"><SignedValue>1</SignedValue></Property><Property name="window"><DoubleValue>0.20000000000000001</DoubleValue></Property></PropertyListValue></Property><Property name="captionVisible"><BooleanValue>True</BooleanValue></Property><Property name="borderVisible"><BooleanValue>True</BooleanValue></Property><Property name="colorTheme"><SignedValue>0</SignedValue></Property><Property name="activeInstrument"><SignedValue>0</SignedValue></Property><Property name="activePhase"><SignedValue>0</SignedValue></Property><Property name="cursorPosition"><SignedValue>1</SignedValue></Property><Property name="cursorPositionType"><SignedValue>0</SignedValue></Property><Property name="llChannelsVisible"><BooleanValue>False</BooleanValue></Property><Property name="spectrumHFVisible"><BooleanValue>False</BooleanValue></Property><Property name="spectrumCursorVisible"><BooleanValue>False</BooleanValue></Property><Property name="rmsLevelVisible"><BooleanValue>True</BooleanValue></Property><Property name="percentFundamentalVisible"><BooleanValue>True</BooleanValue></Property><Property name="phaseAngleVisible"><BooleanValue>True</BooleanValue></Property><Property name="orderFilter"><SignedValue>0</SignedValue></Property></InstrumentChannelProperties></InstrumentChannel>'''

# CommonInstrumentProperties 模板（电力组通用属性）
_COMMON_INSTRUMENT_PROPERTIES = '''<CommonInstrumentProperties type="oxy::power_group"><Property name="thresholds"><PropertyListValue><Property name="baseColor"><ColorValue>#6e6e6e</ColorValue></Property><Property name="topThreshold"><PropertyListValue><Property name="value"><DoubleValue>0</DoubleValue></Property><Property name="color"><ColorValue>#ff0000</ColorValue></Property><Property name="active"><BooleanValue>False</BooleanValue></Property></PropertyListValue></Property><Property name="bottomThreshold"><PropertyListValue><Property name="value"><DoubleValue>0</DoubleValue></Property><Property name="color"><ColorValue>#ff0000</ColorValue></Property><Property name="active"><BooleanValue>False</BooleanValue></Property></PropertyListValue></Property></PropertyListValue></Property><Property name="displayedValue"><PropertyListValue><Property name="mode"><SignedValue>1</SignedValue></Property><Property name="window"><DoubleValue>0.20000000000000001</DoubleValue></Property></PropertyListValue></Property><Property name="captionVisible"><BooleanValue>True</BooleanValue></Property><Property name="borderVisible"><BooleanValue>True</BooleanValue></Property><Property name="colorTheme"><SignedValue>0</SignedValue></Property><Property name="activeInstrument"><SignedValue>0</SignedValue></Property><Property name="activePhase"><SignedValue>0</SignedValue></Property><Property name="cursorPosition"><SignedValue>1</SignedValue></Property><Property name="cursorPositionType"><SignedValue>0</SignedValue></Property><Property name="llChannelsVisible"><BooleanValue>False</BooleanValue></Property><Property name="spectrumHFVisible"><BooleanValue>False</BooleanValue></Property><Property name="spectrumCursorVisible"><BooleanValue>False</BooleanValue></Property><Property name="rmsLevelVisible"><BooleanValue>True</BooleanValue></Property><Property name="percentFundamentalVisible"><BooleanValue>True</BooleanValue></Property><Property name="phaseAngleVisible"><BooleanValue>True</BooleanValue></Property><Property name="orderFilter"><SignedValue>0</SignedValue></Property></CommonInstrumentProperties>'''


_CHANNEL_TOKEN = re.compile(
    r'<Channel id="(\d+)">|</Channel>|ShortId"><StringValue>"([^"]*)"'
)


def _owning_channel_id(stack):
    return stack[-1] if stack else None


def find_power_group_channel_id(xml):
    """从 XML 中查找 PowerGroup (PowerModule) 的 ChannelID。

    用通道标签栈定位，不靠固定回看长度。电力组一大，15KB 窗口会抓到内层通道，
    Oxygen 整页报错且测试界面出不来。

    Returns:
        str: ChannelID 字符串，未找到返回 None
    """
    stack = []
    for match in _CHANNEL_TOKEN.finditer(xml or ""):
        if match.group(1):
            stack.append(match.group(1))
            continue
        if match.group(0).startswith("</Channel"):
            if stack:
                stack.pop()
            continue
        short_id = str(match.group(2) or "").replace(" ", "")
        if short_id.lower() == "powergroup" and stack:
            return stack[-1]
    return None


def _channel_spans(xml):
    """每个 Channel 元素的 [start, end)。内层通道也列出来。"""
    spans = []
    stack = []
    for match in re.finditer(r'<Channel id="(\d+)">|</Channel>', xml or ""):
        if match.group(1):
            stack.append(match.start())
            continue
        if stack:
            start = stack.pop()
            spans.append((start, match.end()))
    return spans


def _innermost_span(spans, pos):
    hit = None
    for start, end in spans:
        if start <= pos < end and (hit is None or end - start < hit[1] - hit[0]):
            hit = (start, end)
    return hit


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


_MEASUREMENT_SCREEN_RE = re.compile(
    r"<MeasurementScreen\b[^>]*>.*?</MeasurementScreen>",
    re.DOTALL,
)


def _is_power_screen(screen_xml):
    return "oxy::power_group" in (screen_xml or "")


def _set_active_screen(xml, index):
    """让 Oxygen 打开指定屏。插到第 1 屏却留着原来的 active_screen 时，另一台机器仍停在旧页。"""

    def repl(match):
        tag = match.group(0)
        if re.search(r'\bactive_screen\s*=\s*"', tag):
            return re.sub(
                r'\bactive_screen\s*=\s*"[^"]*"',
                'active_screen="%s"' % index,
                tag,
                count=1,
            )
        return tag[:-1] + ' active_screen="%s">' % index

    return re.sub(r"<MeasurementScreens\b[^>]*>", repl, xml, count=1)


def inject_power_group_screen(xml, channel_id, *, harmonics=True):
    """将电力组测试页面注入到 XML 的 MeasurementScreens 中。

    已有电力页时就地替换，并切到这一屏。不要删掉后再插到最前面：
    当前屏不是第 1 屏的机器，插完仍停在原来的页，看起来就是没有测试界面。

    Args:
        xml: 完整的设备 XML 字符串
        channel_id: PowerModule 的 ChannelID

    Returns:
        tuple: (修改后的 XML, 是否修改, 日志消息)
    """
    screen_xml = build_power_group_screen(channel_id, harmonics=harmonics)
    matches = list(_MEASUREMENT_SCREEN_RE.finditer(xml or ""))
    power_at = [i for i, match in enumerate(matches) if _is_power_screen(match.group(0))]
    if power_at:
        keep = power_at[0]
        for index in reversed(power_at[1:]):
            extra = matches[index]
            xml = xml[:extra.start()] + xml[extra.end():]
        matches = list(_MEASUREMENT_SCREEN_RE.finditer(xml))
        kept = matches[keep]
        xml = xml[:kept.start()] + screen_xml + xml[kept.end():]
        xml = _set_active_screen(xml, keep)
        if len(power_at) > 1:
            print(f"[BuildTestPage] 已去掉 {len(power_at) - 1} 个多余电力组页面")
        return xml, True, f"已更新电力组测试页面，并切到第 {keep + 1} 屏（channel_id={channel_id}）"

    ms_match = re.search(r"(<MeasurementScreens\b[^>]*>)", xml or "")
    if ms_match:
        insert_pos = ms_match.end()
        xml = xml[:insert_pos] + screen_xml + xml[insert_pos:]
        xml = _set_active_screen(xml, 0)
        return xml, True, f"已注入电力组测试页面，并切到第 1 屏（channel_id={channel_id}）"

    channels_end = (xml or "").find("</Channels>")
    if channels_end >= 0:
        insert_pos = channels_end + len("</Channels>")
        new_screens = f'<MeasurementScreens active_screen="0">{screen_xml}</MeasurementScreens>'
        xml = xml[:insert_pos] + new_screens + xml[insert_pos:]
        return xml, True, f"已创建 MeasurementScreens 并注入电力组测试页面（channel_id={channel_id}）"
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
    # _hRMS / _hPHI / _UNBAL 不是基本量。设成有效时，没接相的电力组会整页报错。
    ("harmonics", re.compile(r"(?i)(?:_THD|_THV|UNBAL|_h\d|_ih\d|_hf\d|_sh\d|_h[A-Za-z])")),
)

_UNUSED_INPUT_ID = "18446744073709551615"
_LINE_PAIRS = (("U12_", (1, 2)), ("U23_", (2, 3)), ("U31_", (3, 1)))
_TOTAL_PREFIXES = ("U_", "I_", "P_", "Q_", "S_", "PF_", "W_")
_PHASE_KINDS = ("U", "I", "P", "Q", "S", "PF", "W")
_DEFAULT_PHASES = {
    0: (1,),
    1: (1, 2),
    2: (1, 3),
    3: (1, 2, 3),
    4: (1, 2, 3),
}


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


def _queue_channel_bool_in(xml, start, end, prop_name, target, label, replacements, *, first=False):
    """只在本通道片段里改布尔。Used 取片段内最后一个，Neon 取第一个。"""
    window = xml[max(0, start):max(0, end)]
    matches = list(re.finditer(
        r'(<Property name="%s"><BooleanValue>)(True|False)(</BooleanValue>)' % re.escape(prop_name),
        window,
    ))
    if not matches:
        return
    found = matches[0] if first else matches[-1]
    if found.group(2) == target:
        return
    base = max(0, start)
    at = base + found.start(2)
    replacements.append((at, at + len(found.group(2)), target, label))


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
    spans = _channel_spans(xml)
    for match in re.finditer(r'ShortId"><StringValue>"([^"]+)"', xml):
        kind = optional_power_feature(match.group(1))
        if kind is None:
            continue
        target = wanted[kind]
        pos = match.start()
        short_id = match.group(1)
        _queue_bool_near(xml, pos, spans, "Used", target, f"{short_id}: Used", replacements)
        _queue_bool_near(
            xml, pos, spans, "Neon/Active", target, f"{short_id}: Neon/Active", replacements
        )
    return _apply_channel_bools(xml, replacements), [item[3] for item in replacements]


def map_short_ids(xml):
    """ShortId -> 所属 Channel id。用通道栈，不把外层 id 套到内层通道上。"""
    found = {}
    stack = []
    for match in _CHANNEL_TOKEN.finditer(xml or ""):
        if match.group(1):
            stack.append(match.group(1))
            continue
        if match.group(0).startswith("</Channel"):
            if stack:
                stack.pop()
            continue
        short_id = str(match.group(2) or "")
        if short_id and stack:
            found[short_id] = stack[-1]
    return found


def _paired_phases(present):
    """present: {相号: {'U','I'}}。电压和电流都有才算一相。"""
    return {phase for phase, kinds in present.items() if "U" in kinds and "I" in kinds}


def phases_from_xml(xml, analog_ids=None):
    """电压、电流都接上的相。全 F 的槽位是空的。

    analog_ids 给出时，槽位必须指向真实采样通道。指到别的 id 不算已接线。
    """
    present = {}
    allowed = {str(item) for item in analog_ids} if analog_ids else None
    for match in re.finditer(
        r'POWER/InputChannels/([UI])(\d+)"><ChannelID>(\d+)</ChannelID>',
        xml or "",
    ):
        if match.group(3) == _UNUSED_INPUT_ID:
            continue
        if allowed is not None and match.group(3) not in allowed:
            continue
        present.setdefault(int(match.group(2)), set()).add(match.group(1))
    return _paired_phases(present)


def phases_from_slots(channel_map):
    present = {}
    for slot, name in (channel_map or {}).items():
        if not str(name or "").strip():
            continue
        match = re.fullmatch(r"([UI])(\d+)", str(slot))
        if match:
            present.setdefault(int(match.group(2)), set()).add(match.group(1))
    return _paired_phases(present)


def _analog_names(slot):
    match = re.fullmatch(r"([UI])(\d+)", str(slot or ""))
    if not match:
        return []
    kind, number = match.group(1), match.group(2)
    if kind == "U":
        return ["AI 1/U%s" % number, "AI 1/u%s" % number]
    return ["AI 1/I%s" % number, "AI 1/l%s" % number, "AI 1/L%s" % number]


_AI_VOLT = re.compile(r"^AI\s*(\d+)\s*/\s*U(\d+)$", re.I)
_AI_CURR = re.compile(r"^AI\s*(\d+)\s*/\s*[IlL](\d+)$")
_AI_NUM = re.compile(r"^AI\s*(\d+)\s*/\s*(\d+)(?:\s|$)", re.I)


def parse_channel_list_names(text):
    """:CHANNELLIST:NAMES? 的 ("通道id","通道名") 列表。"""
    found = {}
    for match in re.finditer(r'\(\s*"(\d+)"\s*,\s*"([^"]*)"\s*\)', text or ""):
        name = match.group(2).strip()
        if name:
            found[name] = match.group(1)
    return found


_MODE_RE = re.compile(r'Property name="Mode"><StringValue>"([^"]*)"')
_UNIT_RE = re.compile(r'Property name="Unit"><StringValue>"([^"]*)"')
_BOARD_ID_RE = re.compile(r'Property name="ID:TRION/BoardId"><UnsignedValue>(\d+)')
_SLOT_NO_RE = re.compile(r'Property name="ID:TRION/SlotNumber"><UnsignedValue>(\d+)')
_INDEX_RE = re.compile(r'Property name="ID:TRION/ChannelIndex"><UnsignedValue>(\d+)')
_BOARD_NAME_RE = re.compile(r'Property name="ID:TRION/BoardName"><StringValue>"([^"]*)"')
_CHANNEL_OPEN_RE = re.compile(r'<Channel id="(\d+)">')


def _kind_from_body(body):
    mode = _MODE_RE.search(body or "")
    if mode:
        token = mode.group(1).strip().lower()
        if token.startswith("volt") or token in ("u", "v"):
            return "U"
        if token.startswith("curr") or token in ("i", "a"):
            return "I"
    if ">Analog<" not in (body or ""):
        return ""
    unit = _UNIT_RE.search(body)
    if not unit:
        return ""
    token = unit.group(1).strip().upper()
    if token in ("V", "VOLT", "VOLTS"):
        return "U"
    if token in ("A", "AMP", "AMPS"):
        return "I"
    return ""


def analog_sources(xml):
    """硬件采样通道。按板上的电压/电流模式认，不依赖 AI 1/U1 这种名字。"""
    spans = _channel_spans(xml or "")
    sources = []
    for match in re.finditer(r'ShortId"><StringValue>"([^"]+)"', xml or ""):
        start, end = _channel_local_bounds(xml, match.start(), spans)
        body = xml[start:end]
        kind = _kind_from_body(body)
        if not kind:
            continue
        opened = None
        for opened in _CHANNEL_OPEN_RE.finditer(xml[start:match.start()]):
            pass
        board_name = _BOARD_NAME_RE.search(body)
        sources.append({
            "name": match.group(1),
            "id": opened.group(1) if opened else "",
            "mode": kind,
            "board": int(_BOARD_ID_RE.search(body).group(1)) if _BOARD_ID_RE.search(body) else 0,
            "slot": int(_SLOT_NO_RE.search(body).group(1)) if _SLOT_NO_RE.search(body) else 0,
            "index": int(_INDEX_RE.search(body).group(1)) if _INDEX_RE.search(body) else 0,
            "board_name": board_name.group(1) if board_name and board_name.group(1) else "",
        })
    return sources


def discover_from_modes(xml):
    """只在同一块板上把电压和电流配成对。不把 A 板的电压和 B 板的电流接成一相。"""
    by_board = {}
    for source in analog_sources(xml):
        by_board.setdefault(source["board"], {"U": [], "I": []})[source["mode"]].append(source)
    best = {}
    best_count = 0
    for board, grouped in sorted(by_board.items()):
        volts = sorted(grouped["U"], key=lambda item: (item["slot"], item["index"], item["name"]))
        currs = sorted(grouped["I"], key=lambda item: (item["slot"], item["index"], item["name"]))
        count = min(len(volts), len(currs))
        if count < 1 or count < best_count:
            continue
        if count == best_count and best:
            continue
        found = {}
        for number in range(count):
            found["U%s" % (number + 1)] = volts[number]["name"]
            found["I%s" % (number + 1)] = currs[number]["name"]
        best = found
        best_count = count
    return best


def discover_named_slots(short_to_id):
    """AI 1/U1、AI 1/I1 这种名字里已经写了相号，按名字接，不按板上序号重排。"""
    named = {}
    for name in short_to_id or {}:
        volt = _AI_VOLT.match(name)
        curr = _AI_CURR.match(name)
        if volt:
            named["U%s" % int(volt.group(2))] = name
        elif curr:
            named["I%s" % int(curr.group(2))] = name
    return named


def discover_analog_slots(short_to_id):
    """从设备通道名找出 U/I。没有 U1/I1 这种名字时，按板上的序号对半：前一半电压，后一半电流。"""
    named = {}
    numbered = []
    for name in short_to_id or {}:
        volt = _AI_VOLT.match(name)
        curr = _AI_CURR.match(name)
        generic = _AI_NUM.match(name)
        if volt:
            named["U%s" % int(volt.group(2))] = name
        elif curr:
            named["I%s" % int(curr.group(2))] = name
        elif generic:
            numbered.append((int(generic.group(1)), int(generic.group(2)), name))
    if named:
        return named
    if len(numbered) < 2:
        return {}
    numbered.sort()
    # 同一块板通道最多的那组
    boards = {}
    for board, index, name in numbered:
        boards.setdefault(board, []).append((index, name))
    group = max(boards.values(), key=len)
    group.sort()
    half = len(group) // 2
    if half < 1:
        return {}
    found = {}
    for offset, (_index, name) in enumerate(group[:half]):
        found["U%s" % (offset + 1)] = name
    for offset, (_index, name) in enumerate(group[half:half * 2]):
        found["I%s" % (offset + 1)] = name
    return found


def _resolve_analog_name(slot, short_to_id):
    ids = short_to_id or {}
    for name in _analog_names(slot):
        if name in ids or name.replace("/l", "/I") in ids or name.replace("/I", "/l") in ids:
            return name
    return ""


def _slots_for_wiring(discovered, wiring_type):
    slots = {}
    for phase in _DEFAULT_PHASES.get(int(wiring_type or 0), (1,)):
        found = {}
        for kind in ("U", "I"):
            slot = "%s%s" % (kind, phase)
            name = (discovered or {}).get(slot)
            if name:
                found[slot] = name
        if len(found) == 2:
            slots.update(found)
    return slots


_WIRING_FROM_ENUM = {
    "AC_1P2W": 0,
    "AC_1P3W": 1,
    "AC_2V2A": 2,
    "AC_3P3W": 3,
    "AC_3P4W": 4,
}


def wiring_type_from_xml(xml):
    match = re.search(
        r'POWER/WiringType">\s*<EnumValue enum="PowerWiringType">([^<]+)',
        xml or "",
    )
    if not match:
        return None
    return _WIRING_FROM_ENUM.get(match.group(1).strip())


def totals_ready(phases, wiring_type):
    """总量要等接线类型要求的相都接上。三相组只接了一相时，打开总功率会被 Oxygen 拒绝。"""
    needed = set(_DEFAULT_PHASES.get(int(0 if wiring_type is None else wiring_type), (1,)))
    return needed.issubset(set(phases or ()))


def default_power_inputs(wiring_type, short_to_id, xml=None):
    """界面和设备都没接成对的相时，按接线类型接电压和电流。缺一个就不接这一相。

    先用通道名里的相号。没有这种名字时，再用同一块板上的电压/电流标记。最后才按序号对半。
    """
    named = _slots_for_wiring(discover_named_slots(short_to_id), wiring_type)
    if named:
        return named
    if xml:
        by_mode = _slots_for_wiring(discover_from_modes(xml), wiring_type)
        if by_mode:
            return by_mode
    return _slots_for_wiring(discover_analog_slots(short_to_id), wiring_type)


def _analog_channel_pos(xml, name, short_to_id=None):
    token = 'ShortId"><StringValue>"%s"' % name
    pos = (xml or "").find(token)
    if pos < 0 and "/l" in name:
        pos = xml.find('ShortId"><StringValue>"%s"' % name.replace("/l", "/I"))
    if pos < 0 and "/I" in name:
        pos = xml.find('ShortId"><StringValue>"%s"' % name.replace("/I", "/l"))
    if pos >= 0:
        return pos
    cid = str((short_to_id or {}).get(name) or "")
    if not cid:
        return -1
    open_tag = '<Channel id="%s">' % cid
    at = (xml or "").find(open_tag)
    if at < 0:
        return -1
    return at + len(open_tag)


def activate_analog_channels(xml, names, short_to_id=None):
    """把接到电力组的模拟通道打开。停在 NEVER 的通道不会出数，功率页上就是 NULL。"""
    spans = _channel_spans(xml)
    replacements = []
    opened = []
    for raw in names or []:
        name = str(raw or "").strip()
        if not name:
            continue
        pos = _analog_channel_pos(xml, name, short_to_id)
        if pos < 0:
            continue
        _queue_bool_near(xml, pos, spans, "Used", "True", "%s: Used" % name, replacements)
        start, end = _channel_local_bounds(xml, pos, spans)
        never = xml.find('frequency="NEVER"', start, end)
        if never >= 0:
            replacements.append((never, never + len('frequency="NEVER"'), 'frequency="SYNC"', name))
        sample = re.search(r'(SampleOccurrenceType">)NEVER(<)', xml[start:end])
        if sample:
            at = start + sample.end(1)
            replacements.append((at, at + len("NEVER"), "SYNC", name))
        opened.append(name)
    updated = _apply_channel_bools(xml, replacements)
    return updated, opened


def set_frequency_channel(xml, channel_id):
    """功率计算的同步电压。没接上时，整页数值都是 NULL。"""
    pattern = r'(<Property name="POWER/FrequencyChannel">\s*<ChannelID>)(\d+)(</ChannelID>)'

    def repl(match):
        if match.group(2) == str(channel_id):
            return match.group(0)
        return match.group(1) + str(channel_id) + match.group(3)

    updated, count = re.subn(pattern, repl, xml or "", count=1)
    return updated, count > 0 and updated != xml


def _channel_local_bounds(xml, pos, spans):
    """ShortId 所在通道里、不跨进子通道的范围。Used 在真实设备上写在 ShortId 后面。"""
    span = _innermost_span(spans, pos)
    start = span[0] if span else max(0, pos - 5000)
    end = span[1] if span else min(len(xml), pos + 6000)
    prev_close = xml.rfind("</Channel>", start, pos)
    if prev_close >= 0:
        start = max(start, prev_close + len("</Channel>"))
    forward_end = end
    for marker in ("<Channel", "</Channel>"):
        found = xml.find(marker, pos)
        if found >= 0:
            forward_end = min(forward_end, found)
    return start, forward_end


def _queue_bool_near(xml, pos, spans, prop_name, target, label, replacements):
    start, end = _channel_local_bounds(xml, pos, spans)
    _queue_channel_bool_in(
        xml, start, end, prop_name, target, label, replacements, first=True
    )


def _basic_channel_allowed(short_id, phases, totals=True):
    if not phases:
        return False
    for prefix, pair in _LINE_PAIRS:
        if short_id.startswith(prefix):
            return pair[0] in phases and pair[1] in phases
    for phase in phases:
        for kind in _PHASE_KINDS:
            if short_id.startswith("%s%s_" % (kind, phase)):
                return True
    if short_id in _SPECIAL_CHANNELS or any(short_id.startswith(prefix) for prefix in _TOTAL_PREFIXES):
        return bool(totals)
    return False


def _channel_should_be_used(short_id, phases, features, totals=True):
    """True/False 表示要改；None 表示这个通道不归构造测试页管。"""
    kind = optional_power_feature(short_id)
    if kind is not None:
        if not phases or not (features or {}).get(kind):
            return False
        return _basic_channel_allowed(short_id, phases, totals=totals) or _basic_channel_allowed(
            re.sub(r"(?i)(_fluc.*|_rc$|_THD.*|_THV.*|_UNBAL.*|_h.*)$", "_", short_id),
            phases,
            totals=totals,
        )
    if short_id in _SPECIAL_CHANNELS or any(short_id.startswith(prefix) for prefix in _CHANNEL_PREFIXES):
        if phases is None:
            return True
        return _basic_channel_allowed(short_id, phases, totals=totals)
    return None


def apply_power_input_channels(xml, channel_map, short_to_id):
    """把界面选的电压电流写进电力组 InputChannels。"""
    notes = []
    replacements = []
    ids = short_to_id or {}
    for slot, raw_name in (channel_map or {}).items():
        name = str(raw_name or "").strip()
        if not name:
            continue
        cid = ids.get(name) or ids.get(name.replace("/l", "/I")) or ids.get(name.replace("/I", "/l"))
        if not cid:
            notes.append("%s <- %s 没有对应通道，跳过" % (slot, name))
            continue
        pattern = 'InputChannels/%s"' % slot
        wrote = False
        for match in re.finditer(re.escape(pattern), xml or ""):
            after = xml[match.end():match.end() + 200]
            cid_match = re.search(r"<ChannelID>(\d+)</ChannelID>", after)
            if not cid_match:
                continue
            if cid_match.group(1) == str(cid):
                wrote = True
                continue
            start = match.end() + cid_match.start(1)
            replacements.append((start, start + len(cid_match.group(1)), str(cid)))
            wrote = True
        if wrote:
            notes.append("%s <- %s" % (slot, name))
        else:
            notes.append("设备里没有 %s 槽位" % slot)
    replacements.sort(key=lambda item: item[0], reverse=True)
    for start, end, value in replacements:
        xml = xml[:start] + value + xml[end:]
    return xml, notes


def clamp_power_channels(xml, phases, features=None, totals=True):
    """只保留有输入的相的基本量。其余电力通道设为无效，避免 Oxygen 整页报「无法将设置有效的更改为 1」。"""
    replacements = []
    spans = _channel_spans(xml)
    flags = features or {}
    for match in re.finditer(r'ShortId"><StringValue>"([^"]+)"', xml or ""):
        short_id = match.group(1)
        target_on = _channel_should_be_used(short_id, phases, flags, totals=totals)
        if target_on is None:
            continue
        target = "True" if target_on else "False"
        pos = match.start()
        _queue_bool_near(xml, pos, spans, "Used", target, "%s: Used" % short_id, replacements)
        _queue_bool_near(
            xml, pos, spans, "Neon/Active", target, "%s: Neon/Active" % short_id, replacements
        )
    updated = _apply_channel_bools(xml, replacements)
    return updated, [item[3] for item in replacements]


def enable_power_group_channels(xml, phases=None, totals=True):
    """启用电力组基本量（U/I/P/Q/S/PF/W/F）。

    闪变、谐波、滚动计算通道不在这里打开，交给三个开关决定。
    phases 给出时，只打开这些相；没接的相保持不动，后面再统一关掉。
    只改本通道标签内的 Used / Neon/Active，避免大工程改到隔壁通道把整份 XML 改坏。

    Returns:
        tuple: (修改后的xml, 启用数量)
    """
    replacements = []
    spans = _channel_spans(xml)

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
        if phases is not None and not _basic_channel_allowed(short_id, phases, totals=totals):
            continue

        _queue_bool_near(xml, pos, spans, "Used", "True", f"{short_id}: Used", replacements)
        _queue_bool_near(
            xml, pos, spans, "Neon/Active", "True", f"{short_id}: Neon/Active", replacements
        )

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


def build_test_page_from_device(controller, log_fn=None, features=None, channel_map=None, wiring_type=0):
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
    model = re.search(r"DEWE\d-A\d", xml)
    if model:
        _log(f"机型: {model.group(0)}")

    short_to_id = map_short_ids(xml)
    listed = parse_channel_list_names(controller._query(":CHANNELLIST:NAMES?") or "")
    for name, cid in listed.items():
        short_to_id.setdefault(name, cid)
    if listed:
        _log("通道表 %d 个" % len(listed))

    sources = analog_sources(xml)
    boards = []
    for source in sources:
        if source["board_name"] and source["board_name"] not in boards:
            boards.append(source["board_name"])
    if sources:
        _log("采样通道 %d 个%s" % (len(sources), ("，板卡: " + "，".join(boards)) if boards else ""))
    analog_ids = {source["id"] for source in sources if source["id"]}

    requested = {
        slot: name
        for slot, name in (channel_map or {}).items()
        if str(name or "").strip()
    }
    known = set(short_to_id)
    filled = {}
    missing = []
    for slot, name in requested.items():
        if name in known or name.replace("/l", "/I") in known or name.replace("/I", "/l") in known:
            filled[slot] = name
        else:
            missing.append("%s <- %s" % (slot, name))
    if missing:
        _log("界面上的通道设备里没有，未采用: " + "，".join(missing))
    if filled:
        xml, notes = apply_power_input_channels(xml, filled, short_to_id)
        _log("按界面接线: " + "，".join(notes))
    phases = phases_from_xml(xml, analog_ids or None)
    if phases:
        _log("已接成对的相: " + ",".join(str(n) for n in sorted(phases)))
    else:
        defaults = default_power_inputs(wiring_type, short_to_id, xml)
        if defaults:
            xml, notes = apply_power_input_channels(xml, defaults, short_to_id)
            phases = phases_from_xml(xml, analog_ids or None)
            if phases:
                _log("电力组没有成对的相，已按设备通道接上: " + "，".join(notes))
            else:
                _log("默认通道没有写进电力组: " + "，".join(notes))
        else:
            phases = set()
            preview = []
            for source in sources[:12]:
                preview.append("%s(%s)" % (source["name"], "电压" if source["mode"] == "U" else "电流"))
            if preview:
                _log("没有接成对的相。设备采样通道: " + "，".join(preview))
            else:
                _log("电力组没有成对的电压和电流，测试页会是空的")

    device_wiring = wiring_type_from_xml(xml)
    effective_wiring = device_wiring if device_wiring is not None else int(wiring_type or 0)
    use_totals = totals_ready(phases, effective_wiring)

    if phases:
        id_to_names = {}
        for name, cid in short_to_id.items():
            id_to_names.setdefault(str(cid), []).append(name)
        source_names = []
        voltage_id = ""
        for match in re.finditer(
            r'POWER/InputChannels/([UI])(\d+)"><ChannelID>(\d+)</ChannelID>',
            xml,
        ):
            if match.group(3) == _UNUSED_INPUT_ID or int(match.group(2)) not in phases:
                continue
            source_names.extend(id_to_names.get(match.group(3), []))
            if match.group(1) == "U" and not voltage_id:
                voltage_id = match.group(3)
        xml, opened = activate_analog_channels(xml, source_names, short_to_id)
        if opened:
            _log("已打开采样: " + "，".join(opened))
        if voltage_id:
            xml, changed_freq = set_frequency_channel(xml, voltage_id)
            if changed_freq:
                _log("频率通道已接到相电压")

    # 2. 查找 PowerGroup ChannelID
    channel_id = find_power_group_channel_id(xml)
    if not channel_id:
        _log("未找到 PowerGroup 通道，请先创建电力组")
        return False
    _log(f"PowerGroup ChannelID: {channel_id}")

    # 3. 启用电力组基本量。闪变 / 谐波 / 滚动计算不在这一步打开。
    xml, enabled_count = enable_power_group_channels(xml, phases=phases, totals=use_totals)
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
    xml, clamped = clamp_power_channels(xml, phases, flags, totals=use_totals)
    if clamped:
        _log("未接线的电力通道已关掉 %s 处" % len(clamped))

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
