# -*- coding: utf-8 -*-
"""LVRT plan generation using direct, documented VOLT steps only."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from utils.timing_profile import LVRT_SCHEMA, TimingProfileValidationError, time_to_ticks
from utils.timing_profile_adapters import (
    append_ac_voltage,
    append_acquisition_end,
    append_acquisition_start,
    baseline_ac_voltages,
    build_plan_context,
    ensure_ten_column_rows,
    finalize_plan,
    format_number,
    read_ui_profile,
    wait_row,
)


def _scaled_voltages(nominal: Sequence[float], u_pu: float) -> List[float]:
    return [float(value) * float(u_pu) for value in nominal]


def _phase_flags(point: Mapping[str, Any]) -> List[bool]:
    """Per-row L1/L2/L3; missing keys default True (symmetric)."""
    return [
        bool(point.get("l1", True)),
        bool(point.get("l2", True)),
        bool(point.get("l3", True)),
    ]


def _phase_tag(flags: Sequence[bool]) -> str:
    letters = []
    for i, ch in enumerate(("1", "2", "3")):
        if i < len(flags) and flags[i]:
            letters.append(ch)
    return ("L" + "".join(letters)) if letters else "L123"


def phase_masked_voltages(
    nominal: Sequence[float],
    u_pu: float,
    *,
    l1: bool = True,
    l2: bool = True,
    l3: bool = True,
) -> List[float]:
    """Apply u_pu to selected phases; unselected phases stay at nominal.

    All selected → three-phase same scaled values (legacy).
    None selected → raise (validate_profile should already reject this).
    """
    nom = [float(v) for v in nominal]
    while len(nom) < 3:
        nom.append(nom[0] if nom else 230.0)
    nom = nom[:3]
    scaled = _scaled_voltages(nom, u_pu)
    flags = [bool(l1), bool(l2), bool(l3)]
    if not any(flags):
        raise TimingProfileValidationError("LVRT 工况请至少勾选 L1/L2/L3 中的一相")
    if all(flags):
        return scaled
    return [scaled[i] if flags[i] else nom[i] for i in range(3)]


def pea_lvrt_template_profile() -> List[Dict[str, Any]]:
    """PEA VFRT-style rows in LVRT timing-profile shape (p.u. + phase mask)."""

    def _row(
        label: str,
        u_pu: float,
        dwell: float,
        *,
        l1: bool = True,
        l2: bool = True,
        l3: bool = True,
        t_pre: float = 1.0,
        t_post: float = 3.0,
    ) -> Dict[str, Any]:
        return {
            "enabled": True,
            "label": label,
            "t_pre": t_pre,
            "t_pre_unit": "秒",
            "t_dwell": dwell,
            "t_dwell_unit": "秒",
            "t_post": t_post,
            "t_post_unit": "秒",
            "u_pu": u_pu,
            "l1": l1,
            "l2": l2,
            "l3": l3,
            "repeats": 1,
        }

    rows: List[Dict[str, Any]] = []
    for ratio, dwell in (
        (0.90, 120.0),
        (0.85, 120.0),
        (0.50, 10.0),
        (0.00, 0.16),
        (1.10, 120.0),
        (1.15, 120.0),
        (1.20, 0.16),
    ):
        rows.append(_row("三相 %.2f p.u." % ratio, ratio, dwell))
    for ratio, dwell in ((0.90, 120.0), (0.85, 120.0), (0.50, 10.0)):
        rows.append(
            _row("A-B %.2f p.u." % ratio, ratio, dwell, l1=True, l2=True, l3=False)
        )
    return rows


def append_lvrt_profile(
    out_rows: List[List[Any]],
    profile: Iterable[Mapping[str, Any]],
    *,
    phase_mode: str,
    nominal_voltages: Sequence[float],
    chroma_61800: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """Append nominal→dip→nominal events with optional per-row phase mask.

    This adapter intentionally has no LIST path.  Every disturbance is a direct
    ``VOLT`` write plus executor waits; three-phase channel-selection writes are
    emitted when phase voltages differ (partial L1/L2/L3 or unequal nominal).
    """

    metas: List[Dict[str, Any]] = []
    for index, point in enumerate(profile, 1):
        if not point.get("enabled", True):
            continue
        u_pu = float(point["u_pu"])
        pre = time_to_ticks(point["t_pre"], point["t_pre_unit"])
        dwell = time_to_ticks(point["t_dwell"], point["t_dwell_unit"])
        post = time_to_ticks(point["t_post"], point["t_post_unit"])
        repeats = int(point.get("repeats", 1))
        label = str(point.get("label") or "LVRT_%d" % index)
        flags = _phase_flags(point)
        dip = phase_masked_voltages(
            nominal_voltages,
            u_pu,
            l1=flags[0],
            l2=flags[1],
            l3=flags[2],
        )
        if phase_mode == "单相":
            dip = dip[:1]
            recover = list(nominal_voltages)[:1]
        else:
            recover = list(nominal_voltages)
            while len(recover) < 3:
                recover.append(recover[0] if recover else 230.0)
            recover = recover[:3]
        for _repeat in range(repeats):
            if pre:
                out_rows.append(wait_row(pre))
            append_ac_voltage(
                out_rows, phase_mode, dip, chroma_61800=chroma_61800
            )
            if dwell:
                out_rows.append(wait_row(dwell))
            append_ac_voltage(
                out_rows, phase_mode, recover, chroma_61800=chroma_61800
            )
            if post:
                out_rows.append(wait_row(post))
        metas.append(
            {
                "name": label,
                "index": index,
                "u_pu": u_pu,
                "l1": flags[0],
                "l2": flags[1],
                "l3": flags[2],
                "phase_tag": _phase_tag(flags),
                "repeats": repeats,
                "duration_01s": (pre + dwell + post) * repeats,
            }
        )
    if any("LIST" in str(row[2]).upper() for row in out_rows):
        raise TimingProfileValidationError("LVRT 禁止生成 LIST 命令")
    return metas


def _error_result(message: str, existing_commands: Optional[Iterable[Sequence[Any]]]) -> Dict[str, Any]:
    try:
        commands = ensure_ten_column_rows(existing_commands or [])
    except Exception:
        commands = []
    return {
        "ok": False,
        "error": message,
        "dc_errors": [],
        "commands": commands,
        "steps": [],
        "test_program": [],
        "wt_is_checked": "0",
        "wt_type": None,
        "analyzer_mode": "wt3000",
        "profile_metas": [],
        "band_metas": [],
        "file_names": [],
        "wt_rounds": 0,
        "wt_continuous": False,
        "band_duration_01s": 0,
        "max_band_duration_01s": 0,
    }


def build_lvrt_plan(
    ui: Any,
    *,
    wt_config_dict: Optional[Mapping[str, Any]] = None,
    str_add_flag: str = "0",
    project_change: str = "0",
    existing_commands: Optional[Iterable[Sequence[Any]]] = None,
    dc_iv_resolver: Any = None,
    chroma_61800: Optional[bool] = None,
) -> Dict[str, Any]:
    """Build a ten-column LVRT command plan from the timing profile table."""

    try:
        context = build_plan_context(
            ui,
            wt_config_dict=wt_config_dict,
            str_add_flag=str_add_flag,
            project_change=project_change,
            existing_commands=existing_commands,
            dc_iv_resolver=dc_iv_resolver,
        )
        profile_rows: List[List[Any]] = []
        metas: List[Dict[str, Any]] = []
        if getattr(ui, "checkBox_S3").isChecked():
            profile = read_ui_profile(ui, LVRT_SCHEMA)
            phase_mode, nominal = baseline_ac_voltages(ui)
            started = append_acquisition_start(context, profile_rows)
            metas = append_lvrt_profile(
                profile_rows,
                profile,
                phase_mode=phase_mode,
                nominal_voltages=nominal,
                chroma_61800=chroma_61800,
            )
            append_acquisition_end(started, profile_rows)
        if any("LIST" in str(row[2]).upper() for row in profile_rows):
            raise TimingProfileValidationError("LVRT 禁止生成 LIST 命令")
        names = [
            "LVRT_%s_%s"
            % (format_number(meta["u_pu"]), meta.get("phase_tag") or "L123")
            for meta in metas
        ]
        return finalize_plan(
            context,
            profile_rows,
            profile_metas=metas,
            file_names=names or ["LVRT"],
        )
    except (AttributeError, TypeError, ValueError, TimingProfileValidationError) as exc:
        return _error_result("LVRT 计划生成失败: %s" % exc, existing_commands)


# Integration branches have used both spellings.
build_thai_lvrt_plan = build_lvrt_plan


__all__ = [
    "append_lvrt_profile",
    "build_lvrt_plan",
    "build_thai_lvrt_plan",
    "pea_lvrt_template_profile",
    "phase_masked_voltages",
]
