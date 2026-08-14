# -*- coding: utf-8 -*-
"""DC 品牌 × 曲线命令一致性校验（生成阶段拦截混用）。

致茂 IVC/TABLE 不得进入蓝点/爱科命令表；反之亦然。
厂家未识别时禁止下发致茂 IVC，避免误发到 Modbus 国产源。
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

# 致茂 PV 模拟器曲线/模式
_CHROMA_MARKERS = (
    "IVC:",
    "IVCURVE:",
    "OUTP:MODE TABLE",
)
# Keysight SAS 表格模式
_KEYSIGHT_MARKERS = (
    "SAS:MODE",
    "SAS:TABL",
)
# 爱科
_ITECH_MARKERS = (
    "SOL:USER",
    "SOL 0",
    "SOL 1",
)
# 蓝点
_BLUESIGHT_MARKERS = (
    "BLUESIGHT:",
    "SYST:MODE SAS",
)

_CANONICAL_BRANDS = {
    "chroma": "Chroma",
    "keysight": "Keysight",
    "itech": "Itech",
    "bluesight": "Bluesight",
}


def _joined_upper(cmds: Iterable[str]) -> str:
    return " ".join(str(c) for c in cmds).upper()


def has_chroma_iv_cmds(cmds: Sequence[str]) -> bool:
    u = _joined_upper(cmds)
    return any(m in u for m in _CHROMA_MARKERS)


def has_keysight_iv_cmds(cmds: Sequence[str]) -> bool:
    u = _joined_upper(cmds)
    return any(m in u for m in _KEYSIGHT_MARKERS)


def has_itech_iv_cmds(cmds: Sequence[str]) -> bool:
    u = _joined_upper(cmds)
    return any(m in u for m in _ITECH_MARKERS)


def has_bluesight_iv_cmds(cmds: Sequence[str]) -> bool:
    u = _joined_upper(cmds)
    return any(m in u for m in _BLUESIGHT_MARKERS)


def _canonical_brand(factor: Optional[str]) -> Optional[str]:
    return _CANONICAL_BRANDS.get(str(factor or "").strip().casefold())


def validate_dc_cmds_for_brand(
    factor: Optional[str], cmds: Optional[Sequence[str]]
) -> Tuple[bool, str]:
    """校验命令列表是否与 per_dc_factor 一致。

    Returns:
        (True, "") 通过；(False, 中文原因) 应拦截。
    """
    if not cmds:
        return True, ""
    cmds_list = [str(c) for c in cmds]
    factor_s = (factor or "").strip()
    brand = _canonical_brand(factor_s)
    if brand is None:
        return (
            False,
            "DC厂家未识别或不受支持，已按 fail-closed 拦截命令下发；请先完成厂家识别",
        )

    detected = {
        name
        for name, present in (
            ("Chroma", has_chroma_iv_cmds(cmds_list)),
            ("Keysight", has_keysight_iv_cmds(cmds_list)),
            ("Itech", has_itech_iv_cmds(cmds_list)),
            ("Bluesight", has_bluesight_iv_cmds(cmds_list)),
        )
        if present
    }
    foreign = sorted(detected - {brand})
    if foreign:
        return (
            False,
            "%s DC 命令含其他厂家曲线/模式命令（%s），已拦截"
            % (brand, ", ".join(foreign)),
        )
    return True, ""


def resolve_dc_iv_with_bridge(
    vmp,
    imp,
    voc,
    isc,
    pf,
    dc_num,
    *,
    get_iv_fn,
    per_dc_factor: dict,
    command_list_dc: dict,
) -> Tuple[str, Optional[List[str]]]:
    """生产用：DCGetIVValueFunction + 模式前缀 + 品牌校验。

    Returns:
        ("ok", cmds) | ("err1"|"err2"|"err_brand", None)
    """
    a = get_iv_fn(vmp, imp, voc, isc, pf, dc_num)
    if a == "1":
        return "err1", None
    if a == "2":
        return "err2", None
    if a is None:
        return "err1", None
    if a == "3":
        return "err_brand", None

    iv_cmds = list(a)
    dc_factor = per_dc_factor.get(str(dc_num), "") or ""
    canonical_factor = _canonical_brand(dc_factor)
    # bridge 历史行为：未识别时曾默认 Chroma 前缀；现改为空前缀，并靠校验拦截 IVC
    mode_cmds = list(
        command_list_dc.get(dc_factor)
        or (command_list_dc.get(canonical_factor) if canonical_factor else [])
        or []
    )
    if not mode_cmds:
        wrapped = iv_cmds
    else:
        joined = " ".join(iv_cmds)
        if any(k in joined for k in ("MODE", "SELect", "SAS:MODE", "SOL ", "SOL:")):
            wrapped = iv_cmds
        else:
            wrapped = []
            if len(mode_cmds) >= 1:
                wrapped.append(mode_cmds[0])
            wrapped.extend(iv_cmds)
            if len(mode_cmds) >= 2:
                wrapped.append(mode_cmds[1])

    ok, msg = validate_dc_cmds_for_brand(dc_factor, wrapped)
    if not ok:
        return "err_brand", None
    return "ok", wrapped
