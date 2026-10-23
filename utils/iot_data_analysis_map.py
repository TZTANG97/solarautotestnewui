# -*- coding: utf-8 -*-
"""IOT solarStandard / testType → SolarTestDataAnalysisApp 标准包与试验码。"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

# IOT 国家标准 id → 分析软件标准目录名
STANDARD_PACK: Dict[str, str] = {
    # 泰国 PEA/MEA → 南德包（PEA TDS 总体 Word）
    "thai": "CEI_Nbis_NanDe",
    "br_ord140": "BRAZIL_140",
    "de_vde": "CEI_Nbis_BeiDe",  # 过渡：德系先走北德包；真 VDE 目录后续再挂
    "en50549": "CEI_Nbis_BeiDe",
    # 意大利 CEI 0-16 → 北德包（图喆/麦田式 TEST REPORT，非南德 PEA TDS）
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
    # 北德包默认走 0-21（de_vde / en50549）；CEI 0-16 见 TEST_CODE_BY_STANDARD
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
    ("rocof", "CEI_Nbis_BeiDe"): "A.4.3.4",
    ("rocof", "CEI_Nbis_DeKai"): "A.4.3.4",
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
    "rocof": "A.4.3.4",
    "cosphibrazil": "5.4.12",
    "fixedq": "5.24",
    "activep": "5.4.23",
    "frequencyadaptability": "5.4.20",
    "voltageadaptability": "5.4.21",
    "guopinjiangzai": "5.4.19",
    "guoqianpin_immun": "5.4.18",
    "qianpinshengzai": "5.4.18",
    "staticmppt": "5.4.26",
}

# 结案自动处理：巴西 Ordinance + 南德 PEA + 北德 CEI 0-16（含二期扩面）
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
    }
)
# 巴西 / 南德 PEA TDS / 北德 CEI 0-16（图喆麦田报告）会真跑
PHASE1_AUTO_PACKS = frozenset({"BRAZIL_140", "CEI_Nbis_NanDe", "CEI_Nbis_BeiDe"})

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


def normalize_solar_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    return aliases.get(s, s)


def resolve_analysis_target(
    *,
    test_type: str,
    solar_standard: str = "",
) -> Optional[Dict[str, str]]:
    """
    返回 {standard_pack, test_code, solar_standard}；无法映射则 None。
    """
    tt = str(test_type or "").strip().lower()
    sid = normalize_solar_standard_id(solar_standard) or "thai"
    pack = STANDARD_PACK.get(sid)
    if not pack:
        return None
    code = (
        TEST_CODE_BY_STANDARD.get((tt, sid))
        or TEST_CODE_BY_PACK.get((tt, pack))
        or DEFAULT_TEST_CODE.get(tt)
    )
    if not code:
        return None
    return {
        "solar_standard": sid,
        "standard_pack": pack,
        "test_code": code,
        "test_type": tt,
    }
