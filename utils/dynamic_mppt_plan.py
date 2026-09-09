# -*- coding: utf-8 -*-
"""Dynamic MPPT plan: EN50530 UI data -> SCPI IV commands (no SoftPanel clicking)."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from utils.en50530_dynamic_mppt import (
    build_en50530_command_rows,
    derive_stc_iv_baseline,
    validate_en50530_bundle,
)
from utils.timing_profile import TimingProfileValidationError
from utils.timing_profile_adapters import (
    append_acquisition_end,
    append_acquisition_start,
    baseline_dc_values,
    build_plan_context,
    ensure_ten_column_rows,
    finalize_plan,
    make_guarded_dc_iv_resolver,
    resolve_dynamic_dc_commands,
    selected_profile_dc_channels,
)


def _read_en50530_bundle(ui: Any) -> Dict[str, Any]:
    panel = getattr(ui, "en50530Panel", None)
    if panel is not None and hasattr(panel, "get_bundle_dict"):
        return panel.get_bundle_dict()
    if hasattr(ui, "timingProfileTable") and hasattr(ui.timingProfileTable, "get_bundle_dict"):
        return ui.timingProfileTable.get_bundle_dict()
    raise TimingProfileValidationError("未找到 EN50530 参数面板")


def _set_plain(ui: Any, name: str, value: Any) -> None:
    widget = getattr(ui, name, None)
    if widget is None:
        return
    text = str(value)
    if hasattr(widget, "setPlainText"):
        widget.setPlainText(text)
    elif hasattr(widget, "setText"):
        widget.setText(text)


def _sync_s1_dc_from_stc(ui: Any, channels: Sequence[int], baseline: Mapping[str, float]) -> None:
    """Step1 启机 IV 与 Test Setup（STC）对齐，避免双套参数打架。"""

    for channel in channels:
        _set_plain(ui, "textEdit_S1_DC%d_VOLT" % channel, "%.4g" % baseline["vmp"])
        _set_plain(ui, "textEdit_S1_DC%d_CURR" % channel, "%.4g" % baseline["imp"])
        _set_plain(ui, "textEdit_S1_DC%d_Voc" % channel, "%.4g" % baseline["voc"])
        _set_plain(ui, "textEdit_S1_DC%d_Isc" % channel, "%.4g" % baseline["isc"])


def build_dynamic_mppt_plan(
    ui: Any,
    *,
    get_iv_fn: Any = None,
    per_dc_factor: Optional[Mapping[str, str]] = None,
    command_list_dc: Optional[Mapping[str, Sequence[str]]] = None,
    wt_config_dict: Optional[Mapping[str, Any]] = None,
    str_add_flag: str = "0",
    project_change: str = "0",
    existing_commands: Optional[Iterable[Sequence[Any]]] = None,
    dc_iv_resolver: Any = None,
) -> Dict[str, Any]:
    factors = dict(per_dc_factor or {})
    command_modes = dict(command_list_dc or {})
    try:
        bundle = None
        channels: List[int] = []
        stc_baseline: Optional[Dict[str, float]] = None
        if getattr(ui, "checkBox_S3", None) is not None and ui.checkBox_S3.isChecked():
            bundle = validate_en50530_bundle(_read_en50530_bundle(ui))
            channels = selected_profile_dc_channels(ui)
            if not channels:
                raise TimingProfileValidationError(
                    "动态 MPPT 至少需要一个同时被 S1 与 step3 启用的 DC 通道"
                )
            pf = 100.0
            try:
                pf = float(baseline_dc_values(ui, channels[0]).get("pf", 100.0))
            except Exception:
                pf = 100.0
            stc_baseline = derive_stc_iv_baseline(bundle.stc, pf=pf)
            _sync_s1_dc_from_stc(ui, channels, stc_baseline)

        if dc_iv_resolver is None and get_iv_fn is not None:
            dc_iv_resolver = make_guarded_dc_iv_resolver(
                get_iv_fn, factors, command_modes
            )
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
        file_names: List[str] = ["DynamicMPPT_BR"]

        if bundle is not None:
            panel = getattr(ui, "en50530Panel", None)
            if panel is not None and hasattr(panel, "textEdit_S3_wt_filename"):
                name = panel.textEdit_S3_wt_filename.text().strip()
                if name:
                    file_names = [name]

            if get_iv_fn is None:
                raise TimingProfileValidationError(
                    "未接入 DCGetIVValueFunction，无法生成 IV 命令"
                )

            stc = bundle.stc
            baselines = {channel: dict(stc_baseline or {}) for channel in channels}

            def iv_for_channel_irr(channel: int, irr_wm2: float):
                baseline = baselines[channel]
                scale = max(0.0, min(1.0, irr_wm2 / stc.irr_stc_wm2))
                pmpp = stc.pmpp * scale
                point = {"pmpp": pmpp, "umpp": stc.vmp, "ff": stc.ff}
                code, commands, message = resolve_dynamic_dc_commands(
                    point,
                    baseline,
                    channel - 1,
                    get_iv_fn=get_iv_fn,
                    per_dc_factor=factors,
                    command_list_dc=command_modes,
                )
                if code != "ok" or not commands:
                    raise TimingProfileValidationError(
                        message or "DC%d EN50530 IV 命令失败" % channel
                    )
                return list(commands)

            started = append_acquisition_start(context, profile_rows)
            rows, row_metas = build_en50530_command_rows(
                bundle,
                channels=channels,
                iv_for_channel_irr=iv_for_channel_irr,
            )
            profile_rows.extend(rows)
            metas.extend(row_metas)
            append_acquisition_end(started, profile_rows)

        plan = finalize_plan(
            context,
            profile_rows,
            profile_metas=metas,
            file_names=file_names,
        )
        # StopTime 取 SoftPanel Duration 与实际 wait tick 的较大值，避免早停
        wait_01s = 0
        for row in profile_rows:
            for slot in (8, 9):
                if len(row) <= slot:
                    continue
                raw = row[slot]
                if raw in ("", None, 0, "0"):
                    continue
                try:
                    wait_01s += int(raw)
                except (TypeError, ValueError):
                    continue
        duration = max(int(plan.get("band_duration_01s") or 0), wait_01s)
        plan["band_duration_01s"] = duration
        plan["max_band_duration_01s"] = duration
        return plan
    except (AttributeError, TypeError, ValueError, TimingProfileValidationError) as exc:
        commands = ensure_ten_column_rows(existing_commands or [])
        return {
            "ok": False,
            "error": "动态 MPPT 计划生成失败: %s" % exc,
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


build_thai_dynamic_mppt_plan = build_dynamic_mppt_plan

__all__ = ["build_dynamic_mppt_plan", "build_thai_dynamic_mppt_plan"]
