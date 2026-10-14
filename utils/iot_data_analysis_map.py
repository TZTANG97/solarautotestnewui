# -*- coding: utf-8 -*-
"""IOT solarStandard / testType → SolarTestDataAnalysisApp 标准包与试验码。"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

# IOT 国家标准 id → 分析软件标准目录名
STANDARD_PACK: Dict[str, str] = {
    "thai": "CEI_Nbis_NanDe",
    "br_ord140": "BRAZIL_140",
    "de_vde": "CEI_Nbis_BeiDe",  # 过渡：德系先走北德包；真 VDE 目录后续再挂
    "en50549": "CEI_Nbis_BeiDe",
    # 意大利 CEI → 南德包（含 TDS 总体 Word + 各条款 Excel 模板）
    "it_cei": "CEI_Nbis_NanDe",
    "as_nzs": "CEI_Nbis_NanDe",
    "uk_g99": "CEI_Nbis_NanDe",
    "iec61727": "CEI_Nbis_NanDe",
}

# (testType, standard_pack) → 分析试验码；缺省用 DEFAULT_TEST_CODE[testType]
TEST_CODE_BY_PACK: Dict[Tuple[str, str], str] = {
    ("overload", "BRAZIL_140"): "5.4.2",
    ("overload", "CEI_Nbis_BeiDe"): "A.4.9",
    ("overload", "CEI_Nbis_DeKai"): "A.4.9",
    ("flicker", "CEI_Nbis_NanDe"): "voltage.fluctuation",
    ("flicker", "CEI_Nbis_BeiDe"): "21.3",
    ("flicker", "CEI_Nbis_DeKai"): "21.3",
    ("harmonic", "BRAZIL_140"): "5.10",
    ("harmonic", "CEI_Nbis_NanDe"): "harmonic",
    ("dccomponent", "BRAZIL_140"): "5.9",
    ("dccomponent", "CEI_Nbis_NanDe"): "dc.injection",
    ("fixedpf", "BRAZIL_140"): "5.4.11",
    ("fixedpf", "CEI_Nbis_NanDe"): "fixed.displacement.factor",
    ("reconnect", "CEI_Nbis_NanDe"): "response.to.utility.recover",
    ("ovuf", "BRAZIL_140"): "5.4.15",
    ("ovuf", "CEI_Nbis_NanDe"): "under.over.frequency",
    ("rocof", "CEI_Nbis_BeiDe"): "A.4.3.4",
    ("rocof", "CEI_Nbis_DeKai"): "A.4.3.4",
}

DEFAULT_TEST_CODE: Dict[str, str] = {
    "overload": "5.4.2",
    "flicker": "voltage.fluctuation",
    "harmonic": "harmonic",
    "dccomponent": "dc.injection",
    "fixedpf": "fixed.displacement.factor",
    "reconnect": "response.to.utility.recover",
    "ovuf": "under.over.frequency",
    "rocof": "A.4.3.4",
}

# 结案自动处理：巴西过载正式 Excel + 南德有完整模板的试验
PHASE1_AUTO_TESTS = frozenset(
    {
        "overload",
        "flicker",
        "harmonic",
        "dccomponent",
        "fixedpf",
        "reconnect",
        "ovuf",
    }
)
# 仅这些分析标准包会真跑（避免北德过渡映射误触发）
PHASE1_AUTO_PACKS = frozenset({"BRAZIL_140", "CEI_Nbis_NanDe"})

# 试点标准：巴西 Ordinance 140（过载）
PHASE1_PILOT = {
    "test_type": "overload",
    "solar_standard": "br_ord140",
    "standard_pack": "BRAZIL_140",
    "test_code": "5.4.2",
}

# 南德完整报告试点（谐波：Excel 模板 + 可进 TDS 总体 Word）
PHASE1_NANDE_PILOT = {
    "test_type": "harmonic",
    "solar_standard": "it_cei",
    "standard_pack": "CEI_Nbis_NanDe",
    "test_code": "harmonic",
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
    code = TEST_CODE_BY_PACK.get((tt, pack)) or DEFAULT_TEST_CODE.get(tt)
    if not code:
        return None
    return {
        "solar_standard": sid,
        "standard_pack": pack,
        "test_code": code,
        "test_type": tt,
    }
