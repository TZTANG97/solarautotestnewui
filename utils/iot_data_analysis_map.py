# -*- coding: utf-8 -*-
"""IOT solarStandard / testType → SolarTestDataAnalysisApp 标准包与试验码。"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

# IOT 国家标准 id → 分析软件标准目录名
STANDARD_PACK: Dict[str, str] = {
    # 泰国 PEA/MEA → 南德包（PEA TDS 总体 Word）
    "thai": "CEI_Nbis_NanDe",
    "br_ord140": "BRAZIL_140",
    # 德系 VDE：暂走北德 0-21 / A.x（真 VDE 目录后续再挂）
    "de_vde": "CEI_Nbis_BeiDe",
    # 欧洲 EN 50549 → 专用 50549 处理器包（非 CEI 0-16）
    "en50549": "CEI_Nbis_BeiDe_50549",
    # 意大利 CEI 0-16 → 北德包（图喆/麦田式 TEST REPORT）
    "it_cei": "CEI_Nbis_BeiDe",
    "as_nzs": "CEI_Nbis_NanDe",
    "uk_g99": "CEI_Nbis_NanDe",
    "iec61727": "CEI_Nbis_NanDe",
}

# (testType, standard_pack) → 分析试验码；缺省用 DEFAULT_TEST_CODE[testType]
TEST_CODE_BY_PACK: Dict[Tuple[str, str], str] = {
    ("overload", "BRAZIL_140"): "5.4.2",
    ("overload", "CEI_Nbis_BeiDe"): "A.4.9",
    ("overload", "CEI_Nbis_DeKai"): "A.4.9",
    ("flicker", "BRAZIL_140"): "5.4.16",
    ("flicker", "CEI_Nbis_NanDe"): "voltage.fluctuation",
    # 北德包默认走 0-21（de_vde）；CEI 0-16 见 TEST_CODE_BY_STANDARD
    ("flicker", "CEI_Nbis_BeiDe"): "21.3",
    ("flicker", "CEI_Nbis_DeKai"): "21.3",
    ("harmonic", "BRAZIL_140"): "5.10",
    ("harmonic", "CEI_Nbis_NanDe"): "harmonic",
    ("dccomponent", "BRAZIL_140"): "5.9",
    ("dccomponent", "CEI_Nbis_NanDe"): "dc.injection",
    ("fixedpf", "BRAZIL_140"): "5.4.11",
    ("fixedpf", "CEI_Nbis_NanDe"): "fixed.displacement.factor",
    ("reconnect", "BRAZIL_140"): "5.4.22",
    ("reconnect", "CEI_Nbis_NanDe"): "response.to.utility.recover",
    ("ovuf", "BRAZIL_140"): "5.4.15",
    ("ovuf", "CEI_Nbis_NanDe"): "under.over.frequency",
    ("reactiveqin", "BRAZIL_140"): "5.4.13",
    ("reactiveqin", "CEI_Nbis_NanDe"): "reactive.power",
    # rocof 北德条款仅挂 it_cei（见 TEST_CODE_BY_STANDARD），避免 de_vde 误吃 CEI0-16 码
    # —— 二期扩面：巴西已有处理器、IOT 已开测的试验 ——
    ("cosphibrazil", "BRAZIL_140"): "5.4.12",
    ("fixedq", "BRAZIL_140"): "5.24",
    ("activep", "BRAZIL_140"): "5.4.23",
    ("frequencyadaptability", "BRAZIL_140"): "5.4.20",
    ("voltageadaptability", "BRAZIL_140"): "5.4.21",
    ("guopinjiangzai", "BRAZIL_140"): "5.4.19",
    ("guoqianpin_immun", "BRAZIL_140"): "5.4.18",
    ("qianpinshengzai", "BRAZIL_140"): "5.4.18",
    ("staticmppt", "BRAZIL_140"): "5.4.26",
    # 南德补映：有功控制 / 运行电压范围
    ("activep", "CEI_Nbis_NanDe"): "active.power.control",
    ("voltageadaptability", "CEI_Nbis_NanDe"): "operating.voltage.range",
    # —— EN 50549（CEI_Nbis_BeiDe_50549）——
    ("voltageadaptability", "CEI_Nbis_BeiDe_50549"): "5.2",
    # IOT「ROCOF保护」对应 5.8.3.4.1（设定值精度与动作时间）；抗扰度 5.3.1 暂无独立 testType
    ("rocof", "CEI_Nbis_BeiDe_50549"): "5.8.3.4.1",
    ("rocofprotect", "CEI_Nbis_BeiDe_50549"): "5.8.3.4.1",
    ("rocofreset", "CEI_Nbis_BeiDe_50549"): "5.8.3.4.2",
    ("phasejump", "CEI_Nbis_BeiDe_50549"): "5.3.2",
    ("lvrt", "CEI_Nbis_BeiDe_50549"): "5.3.3",
    ("frequencyadaptability", "CEI_Nbis_BeiDe_50549"): "5.4.3",
    ("guopinjiangzai", "CEI_Nbis_BeiDe_50549"): "5.4.3.2",
    ("qianpinshengzai", "CEI_Nbis_BeiDe_50549"): "5.4.3.3",
    ("guoqianpin_immun", "CEI_Nbis_BeiDe_50549"): "5.4.3.3",
    ("reactiveqcap", "CEI_Nbis_BeiDe_50549"): "5.5.1.3",
    ("reactiveqacc", "CEI_Nbis_BeiDe_50549"): "5.5.2.3.2",
    ("fixedq", "CEI_Nbis_BeiDe_50549"): "5.5.2.3.2",
    ("flicker", "CEI_Nbis_BeiDe_50549"): "5.7.2.3.3",
    ("dccomponent", "CEI_Nbis_BeiDe_50549"): "5.7.2.4",
    ("ovuf", "CEI_Nbis_BeiDe_50549"): "5.8.3.2",
    ("voltprotect10min", "CEI_Nbis_BeiDe_50549"): "5.8.3.3",
    ("reconnect", "CEI_Nbis_BeiDe_50549"): "5.9",
    ("activep", "CEI_Nbis_BeiDe_50549"): "5.10.3.2",
    # 静态 Q(U)：北德/德凯有 6.8；南德 NanDe 暂无处理器（resolve 会 None）
    # EN50549 的 5.5.2.4.2（Q(U) 稳态）处理器尚未交付，暂不挂 staticqu
    ("staticqu", "CEI_Nbis_BeiDe"): "6.8",
    ("staticqu", "CEI_Nbis_DeKai"): "6.8",
}

# (testType, solar_standard) 覆盖 pack 默认码——意大利 CEI 0-16（图喆/麦田）
TEST_CODE_BY_STANDARD: Dict[Tuple[str, str], str] = {
    ("harmonic", "it_cei"): "3.1",
    ("flicker", "it_cei"): "3.3",
    ("dccomponent", "it_cei"): "8.1",
    ("fixedpf", "it_cei"): "6.7",
    ("reconnect", "it_cei"): "5",
    ("ovuf", "it_cei"): "4",
    ("reactiveqin", "it_cei"): "6.1",
    ("rocof", "it_cei"): "A.4.3.4",
    ("overload", "it_cei"): "A.4.9",
}

DEFAULT_TEST_CODE: Dict[str, str] = {
    "overload": "5.4.2",
    "flicker": "voltage.fluctuation",
    "harmonic": "harmonic",
    "dccomponent": "dc.injection",
    "fixedpf": "fixed.displacement.factor",
    "reconnect": "response.to.utility.recover",
    "ovuf": "under.over.frequency",
    "reactiveqin": "reactive.power",
    # 巴西二期默认码（仅当 STANDARD_PACK 指向 BRAZIL_140 且无更具体映射时使用）
    "cosphibrazil": "5.4.12",
    "fixedq": "5.24",
    "activep": "5.4.23",
    "frequencyadaptability": "5.4.20",
    "voltageadaptability": "5.4.21",
    "guopinjiangzai": "5.4.19",
    "guoqianpin_immun": "5.4.18",
    "qianpinshengzai": "5.4.18",
    "staticmppt": "5.4.26",
    # 注意：rocof / phasejump / lvrt / voltprotect10min 禁止放默认码——
    # 否则 thai/br_ord140 等会落到不存在的处理器。仅走 TEST_CODE_BY_PACK / BY_STANDARD。
}

# 结案自动处理：巴西 + 南德 PEA + 北德 CEI0-16 + EN50549
PHASE1_AUTO_TESTS = frozenset(
    {
        "overload",
        "flicker",
        "harmonic",
        "dccomponent",
        "fixedpf",
        "reconnect",
        "ovuf",
        "reactiveqin",
        # 二期巴西扩面
        "cosphibrazil",
        "fixedq",
        "activep",
        "frequencyadaptability",
        "voltageadaptability",
        "guopinjiangzai",
        "guoqianpin_immun",
        "qianpinshengzai",
        "staticmppt",
        # EN50549 / 北德补充
        "voltprotect10min",
        "phasejump",
        "lvrt",
        "rocof",
        "rocofprotect",
        "rocofreset",
        "reactiveqcap",
        "reactiveqacc",
        "staticqu",
    }
)
# 巴西 / 南德 PEA TDS / 北德 CEI 0-16 / EN 50549
PHASE1_AUTO_PACKS = frozenset(
    {
        "BRAZIL_140",
        "CEI_Nbis_NanDe",
        "CEI_Nbis_BeiDe",
        "CEI_Nbis_BeiDe_50549",
    }
)

# 试点标准：巴西 Ordinance 140（过载）
PHASE1_PILOT = {
    "test_type": "overload",
    "solar_standard": "br_ord140",
    "standard_pack": "BRAZIL_140",
    "test_code": "5.4.2",
}

# 南德完整报告试点（泰国 PEA：Excel + TDS 总体 Word）
PHASE1_NANDE_PILOT = {
    "test_type": "harmonic",
    "solar_standard": "thai",
    "standard_pack": "CEI_Nbis_NanDe",
    "test_code": "harmonic",
}

# 北德 / CEI 0-16 完整报告试点（意大利：Excel + 图喆麦田式总体 Word）
PHASE1_BEIDE_PILOT = {
    "test_type": "harmonic",
    "solar_standard": "it_cei",
    "standard_pack": "CEI_Nbis_BeiDe",
    "test_code": "3.1",
}

# EN 50549 试点：10min 过压保护
PHASE1_EN50549_PILOT = {
    "test_type": "voltprotect10min",
    "solar_standard": "en50549",
    "standard_pack": "CEI_Nbis_BeiDe_50549",
    "test_code": "5.8.3.3",
}


def normalize_solar_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {
        "iec": "iec61727",
        "cn_gb": "en50549",
        "en_50549": "en50549",
        "50549": "en50549",
    }
    return aliases.get(s, s)


# testType 别名 → 规范名（bridge PHASE1 判断与 resolve 共用）
TEST_TYPE_ALIASES: Dict[str, str] = {
    "voltprotect": "voltprotect10min",
    "10min过压保护": "voltprotect10min",
    "过压保护10min": "voltprotect10min",
    "phase_jump": "phasejump",
    "lowvoltage_ride_through": "lvrt",
    # ROCOF保护：EN50549 下 rocof / rocofprotect → 5.8.3.4.1；复位单独 rocofreset
    "rocof_protect": "rocofprotect",
    "rocof保护": "rocofprotect",
    "rocof复位": "rocofreset",
    "rocof_reset": "rocofreset",
    "无功能力范围": "reactiveqcap",
    "reactive_qcap": "reactiveqcap",
    "无功精度": "reactiveqacc",
    "reactive_qacc": "reactiveqacc",
    "静态qu": "staticqu",
    "动态qu": "dynamicqu",
}


def normalize_test_type_for_analysis(raw: Optional[str]) -> str:
    tt = str(raw or "").strip().lower()
    return TEST_TYPE_ALIASES.get(tt, tt)


def _default_code_fits_pack(code: str, pack: str) -> bool:
    """DEFAULT_TEST_CODE 不得跨包乱用（巴西 5.x ≠ 南德点号码 ≠ 北德条款）。"""
    if pack == "BRAZIL_140":
        return code[:1].isdigit()  # 5.4.2 / 5.10 / 5.24
    if pack == "CEI_Nbis_NanDe":
        # harmonic / voltage.fluctuation / dc.injection …
        return (not code[:1].isdigit()) and ("." in code or code == "harmonic")
    # 北德 / 50549 / 德凯：禁止吃 DEFAULT，必须 BY_PACK / BY_STANDARD
    return False


def resolve_analysis_target(
    *,
    test_type: str,
    solar_standard: str = "",
) -> Optional[Dict[str, str]]:
    """
    返回 {standard_pack, test_code, solar_standard}；无法映射则 None。
    """
    tt = normalize_test_type_for_analysis(test_type)

    sid = normalize_solar_standard_id(solar_standard) or "thai"
    pack = STANDARD_PACK.get(sid)
    if not pack:
        return None

    code = TEST_CODE_BY_STANDARD.get((tt, sid)) or TEST_CODE_BY_PACK.get((tt, pack))
    if not code:
        default = DEFAULT_TEST_CODE.get(tt)
        if default and _default_code_fits_pack(default, pack):
            code = default
    if not code:
        return None
    return {
        "solar_standard": sid,
        "standard_pack": pack,
        "test_code": code,
        "test_type": tt,
    }
