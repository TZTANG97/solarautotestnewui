# -*- coding: utf-8 -*-
"""EN50530 dynamic MPPT profile model (aligned with Chroma SoftPanel)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from utils.timing_profile import TimingProfileValidationError, time_to_ticks

EN50530_TABS: Tuple[Tuple[str, str], ...] = (
    ("10_50", "10 ~ 50% Pdcn"),
    ("30_100", "30 ~ 100% Pdcn"),
    ("startup_shutdown", "Start-up & Shut-down"),
)

EN50530_TAB_LABELS: Dict[str, str] = {tab_id: label for tab_id, label in EN50530_TABS}

EN50530_ROW_DEFAULTS: Dict[str, Any] = {
    "enabled": True,
    "repetitions": 1,
    "slope_wm2_s": 10.0,
    "ramp_up_s": 70.0,
    "dwell_up_s": 10.0,
    "ramp_dn_s": 70.0,
    "dwell_dn_s": 10.0,
}


def _irr_bounds_for_tab(tab_id: str, irr_stc: float) -> Tuple[float, float]:
    """Irradiance band for SoftPanel EN50530 tabs (W/m²)."""

    if tab_id == "10_50":
        return irr_stc * 0.1, irr_stc * 0.5
    if tab_id == "30_100":
        return irr_stc * 0.3, irr_stc
    # Start-up & Shut-down: low ↔ STC
    return irr_stc * 0.1, irr_stc


def softpanel_ramp_seconds(slope_wm2_s: float, irr_min: float, irr_max: float) -> float:
    """SoftPanel Ramp = (Gmax − Gmin) / Slope."""

    span = max(0.0, float(irr_max) - float(irr_min))
    slope = float(slope_wm2_s)
    if slope <= 0:
        raise TimingProfileValidationError("Slope 必须 > 0")
    return span / slope


def apply_softpanel_ramp_times(
    row: Mapping[str, Any],
    *,
    tab_id: str,
    irr_stc_wm2: float = 1000.0,
) -> Dict[str, Any]:
    """Fill Ramp UP/DN from Slope using SoftPanel full-band rule."""

    out = dict(row)
    irr_min, irr_max = _irr_bounds_for_tab(tab_id, float(irr_stc_wm2))
    slope = float(out.get("slope_wm2_s") or 0)
    if slope <= 0:
        return out
    ramp = softpanel_ramp_seconds(slope, irr_min, irr_max)
    out["ramp_up_s"] = ramp
    out["ramp_dn_s"] = ramp
    return out


def _preset_row(
    *,
    enabled: bool,
    repetitions: int,
    slope: float,
    dwell: float,
    tab_id: str,
    irr_stc: float = 1000.0,
) -> Dict[str, Any]:
    irr_min, irr_max = _irr_bounds_for_tab(tab_id, irr_stc)
    ramp = softpanel_ramp_seconds(slope, irr_min, irr_max)
    return {
        "enabled": enabled,
        "repetitions": repetitions,
        "slope_wm2_s": slope,
        "ramp_up_s": ramp,
        "dwell_up_s": dwell,
        "ramp_dn_s": ramp,
        "dwell_dn_s": dwell,
    }


# SoftPanel EN50530 30~100% (300–1000 W/m²) — Chroma datasheet slopes / dwell / reps
EN50530_30_100_PRESET: Sequence[Dict[str, Any]] = tuple(
    _preset_row(
        enabled=True,
        repetitions=10,
        slope=slope,
        dwell=10.0,
        tab_id="30_100",
    )
    for slope in (10.0, 14.0, 20.0, 30.0, 50.0, 100.0)
)

# SoftPanel-style 10~50% (100–500 W/m²)
EN50530_10_50_PRESET: Sequence[Dict[str, Any]] = tuple(
    _preset_row(
        enabled=True,
        repetitions=10,
        slope=slope,
        dwell=10.0,
        tab_id="10_50",
    )
    for slope in (5.0, 7.0, 10.0, 14.0, 20.0, 40.0)
)

# Start-up & Shut-down: slower full-band profile
EN50530_STARTUP_PRESET: Sequence[Dict[str, Any]] = (
    _preset_row(
        enabled=True,
        repetitions=1,
        slope=1.0,
        dwell=10.0,
        tab_id="startup_shutdown",
    ),
)


@dataclass
class En50530StcParams:
    initial_setup_s: float = 300.0
    vmp: float = 100.0
    pmpp: float = 600.0
    ff: float = 0.8
    ff_label: str = "c-Si"
    irr_stc_wm2: float = 1000.0


@dataclass
class En50530ProfileBundle:
    active_tab: str = "30_100"
    stc: En50530StcParams = field(default_factory=En50530StcParams)
    tabs: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    def rows_for_active_tab(self) -> List[Dict[str, Any]]:
        return list(self.tabs.get(self.active_tab) or [])

    def enabled_rows_for_active_tab(self) -> List[Dict[str, Any]]:
        return [r for r in self.rows_for_active_tab() if r.get("enabled")]


def default_en50530_bundle() -> En50530ProfileBundle:
    return En50530ProfileBundle(
        active_tab="30_100",
        tabs={
            "10_50": [dict(r) for r in EN50530_10_50_PRESET],
            "30_100": [dict(r) for r in EN50530_30_100_PRESET],
            "startup_shutdown": [dict(r) for r in EN50530_STARTUP_PRESET],
        },
    )


def row_cycle_duration_s(row: Mapping[str, Any]) -> float:
    """SoftPanel Duration = (RampUP + DwellUP + RampDN + DwellDN) × Repetitions."""

    if not row.get("enabled", True):
        return 0.0
    reps = max(1, int(float(row.get("repetitions") or 1)))
    return (
        float(row.get("ramp_up_s") or 0)
        + float(row.get("dwell_up_s") or 0)
        + float(row.get("ramp_dn_s") or 0)
        + float(row.get("dwell_dn_s") or 0)
    ) * reps


def _float(value: Any, name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise TimingProfileValidationError("%s 必须是数字" % name) from exc
    if parsed < 0:
        raise TimingProfileValidationError("%s 不能为负" % name)
    return parsed


def validate_en50530_row(
    row: Mapping[str, Any],
    *,
    index: int,
    tab_id: str,
    irr_stc_wm2: float,
    sync_ramp_from_slope: bool = True,
) -> Dict[str, Any]:
    if not row.get("enabled", True):
        return {"enabled": False}

    out = dict(EN50530_ROW_DEFAULTS)
    out["enabled"] = True
    out["repetitions"] = max(1, int(_float(row.get("repetitions", 1), "第%d行 Repetitions" % index)))
    out["slope_wm2_s"] = _float(row.get("slope_wm2_s"), "第%d行 Slope" % index)
    out["dwell_up_s"] = _float(row.get("dwell_up_s", 10), "第%d行 Dwell UP" % index)
    out["dwell_dn_s"] = _float(row.get("dwell_dn_s", 10), "第%d行 Dwell DN" % index)
    if out["slope_wm2_s"] <= 0:
        raise TimingProfileValidationError("第%d行 Slope 必须 > 0" % index)

    irr_min, irr_max = _irr_bounds_for_tab(tab_id, irr_stc_wm2)
    if sync_ramp_from_slope:
        ramp = softpanel_ramp_seconds(out["slope_wm2_s"], irr_min, irr_max)
        out["ramp_up_s"] = ramp
        out["ramp_dn_s"] = ramp
    else:
        out["ramp_up_s"] = _float(row.get("ramp_up_s"), "第%d行 Ramp UP" % index)
        out["ramp_dn_s"] = _float(row.get("ramp_dn_s"), "第%d行 Ramp DN" % index)
    out["duration_s"] = row_cycle_duration_s(out)
    out["irr_min"] = irr_min
    out["irr_max"] = irr_max
    return out


def validate_en50530_bundle(
    bundle: Mapping[str, Any],
    *,
    sync_ramp_from_slope: bool = True,
) -> En50530ProfileBundle:
    stc_raw = bundle.get("stc") or {}
    stc = En50530StcParams(
        initial_setup_s=_float(stc_raw.get("initial_setup_s", 300), "Initial Setup Time"),
        vmp=_float(stc_raw.get("vmp", 100), "Vmp"),
        pmpp=_float(stc_raw.get("pmpp", 600), "Pmpp"),
        ff=_float(stc_raw.get("ff", 0.8), "FF"),
        ff_label=str(stc_raw.get("ff_label") or "c-Si"),
        irr_stc_wm2=_float(stc_raw.get("irr_stc_wm2", 1000), "STC 辐照度"),
    )
    if stc.vmp <= 0 or stc.pmpp <= 0:
        raise TimingProfileValidationError("Vmp 与 Pmpp 必须大于 0")
    if not 0 < stc.ff < 1:
        raise TimingProfileValidationError("FF 必须在 0~1 之间")
    active = str(bundle.get("active_tab") or "30_100")
    if active not in EN50530_TAB_LABELS:
        raise TimingProfileValidationError("未知 EN50530 页签: %s" % active)
    tabs_in = dict(bundle.get("tabs") or {})
    tabs_out: Dict[str, List[Dict[str, Any]]] = {}
    for tab_id, _label in EN50530_TABS:
        rows = []
        for index, row in enumerate(tabs_in.get(tab_id) or [], 1):
            if not row.get("enabled", True):
                rows.append({"enabled": False})
                continue
            rows.append(
                validate_en50530_row(
                    row,
                    index=index,
                    tab_id=tab_id,
                    irr_stc_wm2=stc.irr_stc_wm2,
                    sync_ramp_from_slope=sync_ramp_from_slope,
                )
            )
        tabs_out[tab_id] = rows
    active_enabled = sum(1 for r in tabs_out.get(active) or [] if r.get("enabled"))
    if active_enabled <= 0:
        label = EN50530_TAB_LABELS.get(active, active)
        raise TimingProfileValidationError(
            "当前页签「%s」至少启用一行工况（其它页签的勾选不会执行）" % label
        )
    return En50530ProfileBundle(active_tab=active, stc=stc, tabs=tabs_out)


def derive_stc_iv_baseline(stc: En50530StcParams, *, pf: float = 100.0) -> Dict[str, float]:
    """IV endpoints compatible with resolve_dynamic_dc_commands (Vmp<Voc, Imp<Isc)."""

    imp = stc.pmpp / stc.vmp if stc.vmp > 0 else 0.0
    voc_hi = stc.vmp / max(stc.ff, 0.01)
    voc = min(stc.vmp * 1.12, voc_hi * 0.95)
    if voc <= stc.vmp:
        voc = (stc.vmp + voc_hi) * 0.5
    isc = stc.pmpp / (max(stc.ff, 0.01) * voc) * 1.02
    return {"vmp": stc.vmp, "imp": imp, "voc": voc, "isc": isc, "pf": pf}


def estimate_en50530_total_duration_s(bundle: En50530ProfileBundle) -> float:
    """Wall-clock estimate: Initial Setup + SoftPanel Duration of enabled rows on active tab."""

    total = float(bundle.stc.initial_setup_s or 0)
    for row in bundle.enabled_rows_for_active_tab():
        total += row_cycle_duration_s(row)
    return total


def build_en50530_command_rows(
    bundle: En50530ProfileBundle,
    *,
    channels: Sequence[int],
    iv_for_channel_irr,
) -> Tuple[List[List[Any]], List[Dict[str, Any]]]:
    """SoftPanel sequence: STC setup → enter Gmax → for each rep: DN to Gmin → dwell → UP to Gmax → dwell."""

    from utils.timing_profile_adapters import device_write_row, wait_row

    stc = bundle.stc
    tab_id = bundle.active_tab
    irr_min, irr_max = _irr_bounds_for_tab(tab_id, stc.irr_stc_wm2)
    out_rows: List[List[Any]] = []
    metas: List[Dict[str, Any]] = []

    def _write_all(irr: float) -> None:
        for channel in channels:
            for cmd in iv_for_channel_irr(channel, irr):
                out_rows.append(device_write_row("DC%d" % channel, cmd))

    def _wait_s(seconds: float) -> None:
        if seconds > 0:
            out_rows.append(wait_row(time_to_ticks(seconds, "秒")))

    def _ramp(from_irr: float, to_irr: float, duration_s: float) -> None:
        """Approximate SoftPanel continuous ramp with 1 s IV steps spanning duration_s."""

        if duration_s <= 0 or abs(to_irr - from_irr) < 1e-9:
            _write_all(to_irr)
            return
        steps = max(1, int(round(duration_s)))
        for step in range(1, steps + 1):
            irr = from_irr + (to_irr - from_irr) * step / steps
            _write_all(irr)
            _wait_s(1.0)

    # SoftPanel: STC IV → Initial Setup wait → enter band high (Gmax)
    _write_all(stc.irr_stc_wm2)
    setup_ticks = 0
    if stc.initial_setup_s > 0:
        setup_ticks = time_to_ticks(stc.initial_setup_s, "秒")
        out_rows.append(wait_row(setup_ticks))
    if setup_ticks:
        metas.append(
            {
                "name": "InitialSetup",
                "index": 0,
                "duration_01s": int(setup_ticks),
                "initial_setup_s": stc.initial_setup_s,
            }
        )

    if abs(stc.irr_stc_wm2 - irr_max) > 1e-6:
        _write_all(irr_max)
    current_irr = irr_max

    rows = bundle.enabled_rows_for_active_tab()
    for row_index, row in enumerate(rows, 1):
        reps = int(row.get("repetitions") or 1)
        slope = float(row["slope_wm2_s"])
        ramp_up_s = float(row["ramp_up_s"])
        ramp_dn_s = float(row["ramp_dn_s"])
        dwell_up = float(row["dwell_up_s"])
        dwell_dn = float(row["dwell_dn_s"])

        for _rep in range(reps):
            # SoftPanel cycle: Ramp DN (Gmax→Gmin) → Dwell → Ramp UP (Gmin→Gmax) → Dwell
            if abs(current_irr - irr_max) > 1e-6:
                _write_all(irr_max)
                current_irr = irr_max
            _ramp(current_irr, irr_min, ramp_dn_s)
            current_irr = irr_min
            _wait_s(dwell_dn)

            _ramp(current_irr, irr_max, ramp_up_s)
            current_irr = irr_max
            _wait_s(dwell_up)

        duration_s = row_cycle_duration_s(row)
        metas.append(
            {
                "name": "EN50530_S%.0f" % slope,
                "index": row_index,
                "slope_wm2_s": slope,
                "repetitions": reps,
                "irr_min": irr_min,
                "irr_max": irr_max,
                "duration_s": duration_s,
                "duration_01s": int(round(duration_s * 10)),
            }
        )
    return out_rows, metas


__all__ = [
    "EN50530_TABS",
    "EN50530_TAB_LABELS",
    "EN50530_30_100_PRESET",
    "EN50530_10_50_PRESET",
    "EN50530_STARTUP_PRESET",
    "En50530ProfileBundle",
    "En50530StcParams",
    "apply_softpanel_ramp_times",
    "build_en50530_command_rows",
    "default_en50530_bundle",
    "derive_stc_iv_baseline",
    "estimate_en50530_total_duration_s",
    "row_cycle_duration_s",
    "softpanel_ramp_seconds",
    "validate_en50530_bundle",
    "validate_en50530_row",
]
