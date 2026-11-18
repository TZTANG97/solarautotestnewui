# -*- coding: utf-8 -*-
"""Adapters between timing profiles, existing UI controls and 10-column plans."""

from __future__ import annotations

import csv
import importlib
import math
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableSequence, Optional, Sequence, Tuple

from PyQt5.QtWidgets import (
    QAbstractButton,
    QCheckBox,
    QComboBox,
    QLineEdit,
    QRadioButton,
    QTextEdit,
)

from dewetron_autotest import (
    DEWETRON_CONFIG_COLUMN,
    MODE_DEWETRON,
    MODE_WT,
    PROFILE_GENERIC,
    append_dewetron_tail_columns,
    extract_ui_config,
    extract_ui_mode,
    read_dewetron_tail_columns,
)
from utils.ac_scpi_commands import append_ac_startup_setpoints, append_volt_set, resolve_chroma_61800
from utils.dc_brand_cmd_guard import (
    has_bluesight_iv_cmds,
    has_chroma_iv_cmds,
    has_itech_iv_cmds,
    resolve_dc_iv_with_bridge,
    validate_dc_cmds_for_brand,
)
from utils.timing_profile import (
    TIMING_PROFILE_JSON_COLUMN,
    SchemaLike,
    TimingProfileValidationError,
    get_schema,
    profile_from_json,
    profile_to_json,
    time_to_ticks,
)


COMMAND_ROW_LENGTH = 10
SAFE_SHUTDOWN_HELPER_CONTRACT = (
    "utils.safe_shutdown.append_safe_shutdown(ui, out_rows, "
    "row_factory=device_write_row, wait_factory=wait_row)"
)
SAFE_SHUTDOWN_PARENT_WIRING = (
    "父代理接入中央安全关机模块时，请提供 " + SAFE_SHUTDOWN_HELPER_CONTRACT
)


def empty_command_row() -> List[Any]:
    return ["" for _ in range(COMMAND_ROW_LENGTH)]


def command_row(
    device: Any = "",
    action: Any = "",
    command: Any = "",
    *,
    meta_key: Any = "",
    meta_value: Any = "",
    slot6: Any = "",
    slot7: Any = "",
    slot8: Any = "",
    slot9: Any = "",
) -> List[Any]:
    row = empty_command_row()
    row[0] = device
    row[1] = action
    row[2] = command
    row[3] = meta_key
    row[4] = meta_value
    row[6] = slot6
    row[7] = slot7
    row[8] = slot8
    row[9] = slot9
    return row


def ac_write_row(command: Any) -> List[Any]:
    return command_row("AC", "write", command)


def device_write_row(device: Any, command: Any) -> List[Any]:
    return command_row(device, "write", command)


def wait_row(wait_01s: Any, *, slot: int = 9) -> List[Any]:
    if slot not in (8, 9):
        raise ValueError("wait slot must be 8 or 9")
    row = command_row("AC", "query", "*IDN?")
    row[slot] = wait_01s
    return row


def acquisition_marker_row(marker: str) -> List[Any]:
    return command_row("AC", "query", "*IDN?", slot6=str(marker).upper())


def ensure_ten_column_rows(rows: Iterable[Sequence[Any]]) -> List[List[Any]]:
    normalized: List[List[Any]] = []
    for index, row in enumerate(rows, 1):
        if not isinstance(row, (list, tuple)):
            raise TimingProfileValidationError("第 %d 条命令不是数组" % index)
        if len(row) != COMMAND_ROW_LENGTH:
            raise TimingProfileValidationError(
                "第 %d 条命令必须正好有 10 列，实际 %d 列" % (index, len(row))
            )
        normalized.append(list(row))
    return normalized


def format_number(value: Any, places: int = 6) -> str:
    number = float(value)
    if not math.isfinite(number):
        raise TimingProfileValidationError("命令参数必须是有限数字")
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return (("%%.%df" % places) % number).rstrip("0").rstrip(".")


def profile_table_from_ui(ui: Any) -> Any:
    for name in (
        "timingProfileTable",
        "timing_profile_table",
        "profileTableWidget",
    ):
        table = getattr(ui, name, None)
        if table is not None:
            return table
    raise TimingProfileValidationError("缺少 TimingProfileTable 控件")


def read_ui_profile(ui: Any, schema: SchemaLike) -> List[Dict[str, Any]]:
    table = profile_table_from_ui(ui)
    getter = getattr(table, "get_profile", None) or getattr(table, "get_rows", None)
    if not callable(getter):
        raise TimingProfileValidationError("TimingProfileTable 不支持 get_profile")
    rows = getter()
    # Revalidate against the command adapter's schema, not only the UI's schema.
    return profile_from_json(profile_to_json(rows, schema), schema)


def analyzer_mode_from_ui(ui: Any) -> str:
    section = getattr(ui, "analyzerModeSection", None)
    source = section if section is not None else ui
    try:
        return extract_ui_mode(source)
    except (TypeError, ValueError):
        return MODE_WT


def wt_type_from_ui(ui: Any) -> Optional[str]:
    for attr, name in (
        ("radioButton_S2_WT3000", "WT3000"),
        ("radioButton_S2_WT1800", "WT1800"),
        ("radioButton_S2_WT1806E", "WT1806E"),
        ("radioButton_S2_WT5000", "WT5000"),
    ):
        widget = getattr(ui, attr, None)
        if widget is not None and widget.isChecked():
            return name
    return None


def _text(widget: Any, *, name: str) -> str:
    if widget is None:
        raise TimingProfileValidationError("缺少控件 %s" % name)
    if hasattr(widget, "toPlainText"):
        return str(widget.toPlainText()).strip()
    if hasattr(widget, "text"):
        return str(widget.text()).strip()
    raise TimingProfileValidationError("控件 %s 不支持文本读取" % name)


def _checked(ui: Any, name: str, default: bool = False) -> bool:
    widget = getattr(ui, name, None)
    return bool(widget.isChecked()) if widget is not None else bool(default)


def _combo_text(ui: Any, name: str, default: str = "") -> str:
    widget = getattr(ui, name, None)
    return str(widget.currentText()).strip() if widget is not None else str(default)


def baseline_ac_voltages(ui: Any) -> Tuple[str, List[float]]:
    phase_mode = _combo_text(ui, "comboBox_S1_AC_2", "单相")
    count = 1 if phase_mode == "单相" else 3
    voltages: List[float] = []
    for channel in range(1, count + 1):
        attr = "textEdit_S1_AC_VOLT" if channel == 1 else "textEdit_S1_AC_VOLT_%d" % channel
        raw = _text(getattr(ui, attr, None), name=attr)
        try:
            value = float(raw)
        except (TypeError, ValueError) as exc:
            raise TimingProfileValidationError("%s 电压格式错误" % attr) from exc
        if not math.isfinite(value) or value <= 0:
            raise TimingProfileValidationError("%s 电压必须大于 0" % attr)
        voltages.append(value)
    return phase_mode, voltages


def append_ac_voltage(
    out_rows: MutableSequence[List[Any]],
    phase_mode: str,
    voltages: Sequence[Any],
    *,
    chroma_61800=None,
) -> None:
    if chroma_61800 is None:
        chroma_61800 = resolve_chroma_61800()
    if phase_mode == "单相":
        v = format_number(voltages[0])
        volt_cmd = ("VOLT:AC " + v) if chroma_61800 else ("VOLT " + v)
        out_rows.append(ac_write_row(volt_cmd))
        return
    if len(voltages) != 3:
        raise TimingProfileValidationError("三相电压必须提供 3 个值")
    va = format_number(voltages[0])
    vb = format_number(voltages[1])
    vc = format_number(voltages[2])
    if va == vb == vc:
        append_volt_set(out_rows, phase_mode, voltages[0], chroma_61800=chroma_61800)
        return
    if chroma_61800:
        # 异压必须切 INDEPEND，否则 NSEL+VOLT:AC 无法真正分相
        from utils.ac_scpi_commands import append_chroma_phase_volts

        append_chroma_phase_volts(out_rows, voltages[0], voltages[1], voltages[2])
        return
    out_rows.append(ac_write_row("INST:EDIT EACH"))
    for index, voltage in enumerate(voltages, 1):
        out_rows.append(ac_write_row("INST:NSEL %d" % index))
        v = format_number(voltage)
        out_rows.append(ac_write_row("VOLT " + v))
    out_rows.append(ac_write_row("INST:EDIT ALL"))


def baseline_dc_values(ui: Any, channel: int) -> Dict[str, float]:
    names = {
        "vmp": "textEdit_S1_DC%d_VOLT" % channel,
        "imp": "textEdit_S1_DC%d_CURR" % channel,
        "voc": "textEdit_S1_DC%d_Voc" % channel,
        "isc": "textEdit_S1_DC%d_Isc" % channel,
        "pf": "textEdit_S1_DC%d_PF" % channel,
    }
    values: Dict[str, float] = {}
    for key, attr in names.items():
        raw = _text(getattr(ui, attr, None), name=attr).rstrip("%").strip()
        try:
            value = float(raw)
        except (TypeError, ValueError) as exc:
            raise TimingProfileValidationError("%s 格式错误" % attr) from exc
        if not math.isfinite(value):
            raise TimingProfileValidationError("%s 必须是有限数字" % attr)
        values[key] = value
    if min(values["vmp"], values["imp"], values["voc"], values["isc"]) <= 0:
        raise TimingProfileValidationError("DC%d IV 参数必须大于 0" % channel)
    if values["vmp"] >= values["voc"] or values["imp"] >= values["isc"]:
        raise TimingProfileValidationError(
            "DC%d 必须满足 Vmp < Voc 且 Imp < Isc" % channel
        )
    return values


def selected_profile_dc_channels(ui: Any) -> List[int]:
    selected: List[int] = []
    for channel in range(1, 5):
        if _checked(ui, "checkBox_S1_DC%d" % channel) and _checked(
            ui, "checkBox_S3_DC%d" % channel
        ):
            selected.append(channel)
    return selected


def make_guarded_dc_iv_resolver(
    get_iv_fn: Callable[..., Any],
    per_dc_factor: Mapping[str, str],
    command_list_dc: Mapping[str, Sequence[str]],
) -> Callable[..., Tuple[str, Optional[List[str]]]]:
    """Bind the repository's bridge and brand guard to the plan-builder API."""

    def resolver(vmp: Any, imp: Any, voc: Any, isc: Any, pf: Any, dc_num: int):
        return resolve_dc_iv_with_bridge(
            vmp,
            imp,
            voc,
            isc,
            pf,
            dc_num,
            get_iv_fn=get_iv_fn,
            per_dc_factor=dict(per_dc_factor),
            command_list_dc=dict(command_list_dc),
        )

    return resolver


def _parse_startup_time(ui: Any, value_name: str, unit_name: str) -> int:
    raw = _text(getattr(ui, value_name, None), name=value_name)
    unit = _combo_text(ui, unit_name, "秒")
    return time_to_ticks(raw, unit)


def prepare_plan_context(
    ui: Any,
    *,
    wt_config_dict: Optional[Mapping[str, Any]] = None,
    str_add_flag: str = "0",
    project_change: str = "0",
    existing_commands: Optional[Iterable[Sequence[Any]]] = None,
    dc_iv_resolver: Optional[Callable[..., Tuple[str, Optional[List[str]]]]] = None,
) -> Dict[str, Any]:
    """Generate common analyzer + S1 AC/DC rows without guessing a DC brand."""

    commands = ensure_ten_column_rows(existing_commands or [])
    if str(str_add_flag) == "0":
        commands = []
    steps: List[List[List[Any]]] = []
    dc_errors: List[str] = []
    test_program: List[List[str]] = []
    analyzer_mode = analyzer_mode_from_ui(ui)
    wt_type = wt_type_from_ui(ui)
    analyzer_enabled = _checked(ui, "checkBox_S2", True)
    need_analyzer = str(str_add_flag) == "0" or (
        str(str_add_flag) == "1" and str(project_change) == "1"
    )
    if need_analyzer:
        commands.append(
            command_row(
                "Upper_WT_Config",
                "",
                "",
                meta_key="config_dict",
                meta_value=dict(wt_config_dict or {}),
            )
        )
    if str(str_add_flag) == "1" and str(project_change) == "1":
        commands.append(command_row("AC", "wait", "", slot9=3000))

    if analyzer_enabled and analyzer_mode == MODE_WT and wt_type:
        test_program.append(["12", wt_type])

    if _checked(ui, "checkBox_S1", True):
        step_rows: List[List[Any]] = []
        phase_mode, voltages = baseline_ac_voltages(ui)
        frequency = _text(
            getattr(ui, "textEdit_S1_AC_FR", None), name="textEdit_S1_AC_FR"
        )
        try:
            frequency_value = float(frequency)
        except (TypeError, ValueError) as exc:
            raise TimingProfileValidationError("交流频率格式错误") from exc
        if not math.isfinite(frequency_value) or frequency_value <= 0:
            raise TimingProfileValidationError("交流频率必须大于 0")

        append_rows: List[List[Any]] = []
        va = format_number(voltages[0])
        vb = format_number(voltages[1]) if phase_mode == "三相" else None
        vc = format_number(voltages[2]) if phase_mode == "三相" else None
        append_ac_startup_setpoints(
            append_rows,
            phase_mode,
            va,
            vb,
            vc,
            format_number(frequency_value),
        )
        for row in append_rows:
            commands.append(row)
            step_rows.append(row)
        ac_wait = _parse_startup_time(
            ui, "textEdit_S1_ACWaitTIME", "comboBox_S1_ACWaitTIME"
        )
        ac_on = _combo_text(ui, "comboBox_S1_AC", "开启") == "开启"
        row = ac_write_row("OUTP ON" if ac_on else "OUTP OFF")
        row[9] = ac_wait
        commands.append(row)
        step_rows.append(row)

        for channel in range(1, 5):
            if not _checked(ui, "checkBox_S1_DC%d" % channel):
                continue
            label = "DC电源%d" % channel
            if dc_iv_resolver is None:
                dc_errors.append(
                    "%s未接入 resolve_dc_iv_with_bridge，已拒绝猜测厂家命令" % label
                )
                continue
            try:
                baseline = baseline_dc_values(ui, channel)
                code, iv_commands = dc_iv_resolver(
                    baseline["vmp"],
                    baseline["imp"],
                    baseline["voc"],
                    baseline["isc"],
                    baseline["pf"],
                    channel - 1,
                )
            except Exception as exc:
                dc_errors.append("%s IV 解析失败: %s" % (label, exc))
                continue
            if code != "ok" or not iv_commands:
                messages = {
                    "err1": "赋值错误",
                    "err2": "Isc/Imp 超出设备范围",
                    "err_brand": "厂家未识别或命令与品牌不匹配",
                }
                dc_errors.append("%s%s" % (label, messages.get(code, "命令解析失败")))
                continue
            wait = wait_row(2, slot=8)
            commands.append(wait)
            step_rows.append(wait)
            for iv_command in iv_commands:
                row = device_write_row("DC%d" % channel, iv_command)
                commands.append(row)
                step_rows.append(row)
            status_on = _combo_text(ui, "comboBox_S1_DC%d" % channel, "开启") == "开启"
            row = device_write_row(
                "DC%d" % channel, "OUTP ON" if status_on else "OUTP OFF"
            )
            commands.append(row)
            step_rows.append(row)
            wait = wait_row(2, slot=8)
            commands.append(wait)
            step_rows.append(wait)

        startup_wait = _parse_startup_time(ui, "textEdit_S1_TIME", "comboBox_S1_TIME")
        if startup_wait:
            row = wait_row(startup_wait)
            commands.append(row)
            step_rows.append(row)
        steps.append(step_rows)

    return {
        "commands": commands,
        "steps": steps,
        "dc_errors": dc_errors,
        "test_program": test_program,
        "analyzer_mode": analyzer_mode,
        "analyzer_enabled": analyzer_enabled,
        "wt_type": wt_type,
        "wt_is_checked": "1" if analyzer_enabled and analyzer_mode == MODE_WT else "0",
        "need_analyzer": need_analyzer,
    }


def append_acquisition_start(context: Dict[str, Any], out_rows: MutableSequence[List[Any]]) -> bool:
    if not context.get("analyzer_enabled"):
        return False
    out_rows.append(acquisition_marker_row("ASYNC_START"))
    return True


def append_acquisition_end(
    started: bool, out_rows: MutableSequence[List[Any]]
) -> None:
    if started:
        out_rows.append(acquisition_marker_row("WAIT_END"))


def _load_external_shutdown_helper() -> Optional[Callable[..., Any]]:
    try:
        module = importlib.import_module("utils.safe_shutdown")
    except (ImportError, ModuleNotFoundError):
        return None
    helper = getattr(module, "append_safe_shutdown", None)
    return helper if callable(helper) else None


def safe_shutdown_helper_available() -> bool:
    return _load_external_shutdown_helper() is not None


def _fallback_safe_shutdown(ui: Any, out_rows: MutableSequence[List[Any]]) -> None:
    """Compatibility fallback: DC channels first, then AC, all with settle waits."""

    if not _checked(ui, "checkBox_S_End", True):
        return
    for channel in range(1, 5):
        if not (
            _checked(ui, "checkBox_S1_DC%d" % channel)
            and _checked(ui, "checkBox_S_End_DC%d" % channel)
        ):
            continue
        status_on = (
            _combo_text(ui, "comboBox_S_End_DC%d" % channel, "关闭") == "开启"
        )
        out_rows.append(
            device_write_row(
                "DC%d" % channel, "OUTP ON" if status_on else "OUTP OFF"
            )
        )
        out_rows.append(wait_row(5, slot=8))
    ac_on = _combo_text(ui, "comboBox_S_End_AC", "关闭") == "开启"
    out_rows.append(ac_write_row("OUTP ON" if ac_on else "OUTP OFF"))
    out_rows.append(wait_row(5, slot=8))


def append_safe_shutdown(
    ui: Any, out_rows: MutableSequence[List[Any]]
) -> str:
    """Use the central helper when present, otherwise the documented contract."""

    helper = _load_external_shutdown_helper()
    if helper is None:
        _fallback_safe_shutdown(ui, out_rows)
        return "compat"
    try:
        helper(
            ui,
            out_rows,
            row_factory=device_write_row,
            wait_factory=wait_row,
        )
    except TypeError as exc:
        raise RuntimeError(
            "中央安全关机 helper 接口不兼容；期望 " + SAFE_SHUTDOWN_HELPER_CONTRACT
        ) from exc
    return "central"


append_safe_shutdown_rows = append_safe_shutdown


def finalize_plan(
    context: Dict[str, Any],
    profile_rows: Sequence[List[Any]],
    *,
    profile_metas: Optional[List[Dict[str, Any]]] = None,
    file_names: Optional[List[str]] = None,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    commands = context["commands"]
    if profile_rows:
        commands.extend(profile_rows)
        context["steps"].append(list(profile_rows))
    shutdown_rows: List[List[Any]] = []
    shutdown_backend = append_safe_shutdown(context["ui"], shutdown_rows)
    if shutdown_rows:
        commands.extend(shutdown_rows)
        context["steps"].append(shutdown_rows)
    ensure_ten_column_rows(commands)
    metas = list(profile_metas or [])
    duration = sum(int(meta.get("duration_01s") or 0) for meta in metas)
    return {
        "ok": error is None and not context.get("dc_errors"),
        "error": error or (
            "；".join(context.get("dc_errors") or []) if context.get("dc_errors") else None
        ),
        "dc_errors": list(context.get("dc_errors") or []),
        "commands": commands,
        "steps": context["steps"],
        "wt_type": context.get("wt_type"),
        "test_program": context.get("test_program", []),
        "wt_is_checked": context.get("wt_is_checked", "0"),
        "analyzer_mode": context.get("analyzer_mode", MODE_WT),
        "profile_metas": metas,
        "band_metas": metas,
        "file_names": list(file_names or []),
        "wt_rounds": 1 if context.get("analyzer_enabled") and metas else 0,
        "wt_continuous": bool(context.get("analyzer_enabled") and metas),
        "band_duration_01s": duration,
        "max_band_duration_01s": duration,
        "safe_shutdown_backend": shutdown_backend,
    }


def build_plan_context(ui: Any, **kwargs: Any) -> Dict[str, Any]:
    context = prepare_plan_context(ui, **kwargs)
    context["ui"] = ui
    return context


def resolve_dynamic_dc_commands(
    point: Mapping[str, Any],
    baseline: Mapping[str, float],
    dc_num: int,
    *,
    get_iv_fn: Optional[Callable[..., Any]],
    per_dc_factor: Mapping[str, str],
    command_list_dc: Mapping[str, Sequence[str]],
) -> Tuple[str, Optional[List[str]], str]:
    """Resolve one dynamic-MPPT point through the existing guarded bridge."""

    raw_brand = per_dc_factor.get(str(dc_num), "") or ""
    canonical = {
        "chroma": "Chroma",
        "itech": "Itech",
        "bluesight": "Bluesight",
    }.get(str(raw_brand).strip().casefold())
    if canonical is None:
        return (
            "err_unsupported",
            None,
            "DC%d 品牌 %r 不支持动态 MPPT；仅支持 Chroma/Itech/Bluesight"
            % (dc_num + 1, raw_brand),
        )

    pmpp = point.get("pmpp")
    if pmpp is None:
        p_pct = point.get("p_pct")
        if p_pct is None:
            return "err1", None, "动态 MPPT 工况缺少 pmpp 或 p_pct"
        pmpp = baseline["vmp"] * baseline["imp"] * float(p_pct) / 100.0
    umpp = point.get("umpp")
    if umpp is None:
        umpp = baseline["vmp"]
    ff = point.get("ff")
    if ff is None:
        ff = (
            baseline["vmp"]
            * baseline["imp"]
            / (baseline["voc"] * baseline["isc"])
        )
    pmpp_f, umpp_f, ff_f = float(pmpp), float(umpp), float(ff)
    if not all(math.isfinite(value) for value in (pmpp_f, umpp_f, ff_f)):
        return "err1", None, "动态 MPPT Pmpp/Umpp/FF 必须是有限数字"
    if pmpp_f <= 0 or umpp_f <= 0 or not 0 < ff_f < 1:
        return "err1", None, "动态 MPPT 必须满足 Pmpp>0、Umpp>0、0<FF<1"

    factor_map = dict(per_dc_factor)
    factor_map[str(dc_num)] = canonical
    mode_map = dict(command_list_dc)

    if canonical == "Bluesight":
        stc = "BLUESIGHT:STC %s %s %s" % (
            format_number(pmpp_f),
            format_number(umpp_f),
            format_number(ff_f),
        )

        def bluesight_iv(*_args: Any) -> List[str]:
            return [stc]

        code, commands = resolve_dc_iv_with_bridge(
            umpp_f,
            pmpp_f / umpp_f,
            baseline["voc"],
            baseline["isc"],
            100,
            dc_num,
            get_iv_fn=bluesight_iv,
            per_dc_factor=factor_map,
            command_list_dc=mode_map,
        )
    else:
        if get_iv_fn is None:
            return (
                "err_brand",
                None,
                "DC%d 未接入 DCGetIVValueFunction，不能生成 %s 曲线"
                % (dc_num + 1, canonical),
            )
        voltage_ratio = baseline["vmp"] / baseline["voc"]
        voc = umpp_f / voltage_ratio
        imp = pmpp_f / umpp_f
        isc = pmpp_f / (ff_f * voc)
        if imp >= isc or umpp_f >= voc:
            return "err1", None, "动态 MPPT 工况推导出的 IV 点不满足 Vmp<Voc、Imp<Isc"
        code, commands = resolve_dc_iv_with_bridge(
            umpp_f,
            imp,
            voc,
            isc,
            100,
            dc_num,
            get_iv_fn=get_iv_fn,
            per_dc_factor=factor_map,
            command_list_dc=mode_map,
        )

    if code != "ok" or not commands:
        return code, None, "DC%d 动态 MPPT 曲线生成失败: %s" % (dc_num + 1, code)
    commands = list(commands)
    if canonical == "Itech":
        core = [cmd for cmd in commands if str(cmd).upper().startswith("SOL:USER")]
        if not core:
            return "err_brand", None, "Itech 动态 MPPT 未生成 SOL:USER 命令"
        modes = list(mode_map.get("Itech") or mode_map.get(raw_brand) or ["SOL 0", "SOL 1"])
        commands = ([modes[0]] if modes else ["SOL 0"]) + core
        commands += [modes[1] if len(modes) > 1 else "SOL 1"]
    marker_ok = {
        "Chroma": has_chroma_iv_cmds(commands),
        "Itech": has_itech_iv_cmds(commands),
        "Bluesight": has_bluesight_iv_cmds(commands),
    }[canonical]
    if not marker_ok:
        return (
            "err_brand",
            None,
            "%s 动态 MPPT 命令缺少已证实的品牌曲线语句" % canonical,
        )
    valid, message = validate_dc_cmds_for_brand(canonical, commands)
    if not valid:
        return "err_brand", None, message
    return "ok", commands, ""


COMMON_SETTINGS_HEADERS: Tuple[str, ...] = (
    "Style",
    "checkBox_S1",
    "comboBox_S1_AC",
    "textEdit_S1_AC_VOLT",
    "textEdit_S1_AC_VOLT_2",
    "textEdit_S1_AC_VOLT_3",
    "textEdit_S1_AC_FR",
    "comboBox_S1_AC_2",
    "checkBox_S1_DC1",
    "comboBox_S1_DC1",
    "textEdit_S1_DC1_VOLT",
    "textEdit_S1_DC1_CURR",
    "textEdit_S1_DC1_Voc",
    "textEdit_S1_DC1_Isc",
    "textEdit_S1_DC1_PF",
    "checkBox_S1_DC2",
    "comboBox_S1_DC2",
    "textEdit_S1_DC2_VOLT",
    "textEdit_S1_DC2_CURR",
    "textEdit_S1_DC2_Voc",
    "textEdit_S1_DC2_Isc",
    "textEdit_S1_DC2_PF",
    "checkBox_S1_DC3",
    "comboBox_S1_DC3",
    "textEdit_S1_DC3_VOLT",
    "textEdit_S1_DC3_CURR",
    "textEdit_S1_DC3_Voc",
    "textEdit_S1_DC3_Isc",
    "textEdit_S1_DC3_PF",
    "checkBox_S1_DC4",
    "comboBox_S1_DC4",
    "textEdit_S1_DC4_VOLT",
    "textEdit_S1_DC4_CURR",
    "textEdit_S1_DC4_Voc",
    "textEdit_S1_DC4_Isc",
    "textEdit_S1_DC4_PF",
    "textEdit_S1_ACWaitTIME",
    "comboBox_S1_ACWaitTIME",
    "textEdit_S1_TIME",
    "comboBox_S1_TIME",
    "checkBox_S2",
    "radioButton_S2_WT3000",
    "radioButton_S2_WT1800",
    "radioButton_S2_WT1806E",
    "radioButton_S2_WT5000",
    "checkBox_S3",
    "checkBox_S3_DC1",
    "checkBox_S3_DC2",
    "checkBox_S3_DC3",
    "checkBox_S3_DC4",
    "checkBox_S_End",
    "comboBox_S_End_AC",
    "checkBox_S_End_DC1",
    "comboBox_S_End_DC1",
    "checkBox_S_End_DC2",
    "comboBox_S_End_DC2",
    "checkBox_S_End_DC3",
    "comboBox_S_End_DC3",
    "checkBox_S_End_DC4",
    "comboBox_S_End_DC4",
    TIMING_PROFILE_JSON_COLUMN,
    DEWETRON_CONFIG_COLUMN,
)


def build_settings_headers() -> List[str]:
    return list(COMMON_SETTINGS_HEADERS)


def _resolve_widget(ui: Any, name: str) -> Any:
    widget = getattr(ui, name, None)
    if widget is not None:
        return widget
    finder = getattr(ui, "findChild", None)
    if not callable(finder):
        return None
    widget_type = {
        "checkBox": QCheckBox,
        "comboBox": QComboBox,
        "radioButton": QRadioButton,
        "textEdit": QTextEdit,
        "lineEdit": QLineEdit,
    }
    for prefix, cls in widget_type.items():
        if name.startswith(prefix):
            return finder(cls, name)
    return None


def widget_to_csv(ui: Any, name: str) -> str:
    widget = _resolve_widget(ui, name)
    if widget is None:
        return ""
    if isinstance(widget, QAbstractButton):
        return "1" if widget.isChecked() else "0"
    if isinstance(widget, QComboBox):
        return str(widget.currentIndex())
    if isinstance(widget, QTextEdit):
        return widget.toPlainText()
    if isinstance(widget, QLineEdit):
        return widget.text()
    return ""


def apply_csv_widget_value(ui: Any, name: str, value: Any) -> None:
    widget = _resolve_widget(ui, name)
    if widget is None:
        return
    text = "" if value is None else str(value)
    if isinstance(widget, QAbstractButton):
        widget.setChecked(text.strip().casefold() in {"1", "true", "yes", "on", "是"})
    elif isinstance(widget, QComboBox):
        try:
            widget.setCurrentIndex(int(text))
        except (TypeError, ValueError):
            candidates = [text]
            if "grid_wait" in str(name) or str(name).endswith("_TIME"):
                try:
                    from utils.iot_ovuf_apply import time_unit_aliases

                    candidates = time_unit_aliases(text) or candidates
                except Exception:
                    pass
            index = -1
            for cand in candidates:
                index = widget.findText(str(cand))
                if index >= 0:
                    break
            if index >= 0:
                widget.setCurrentIndex(index)
    elif isinstance(widget, QTextEdit):
        widget.setPlainText(text)
    elif isinstance(widget, QLineEdit):
        widget.setText(text)


def append_dewetron_settings_tail(
    headers: MutableSequence[Any],
    values: MutableSequence[Any],
    ui: Any,
    *,
    test_type: str,
) -> Tuple[MutableSequence[Any], MutableSequence[Any]]:
    section = getattr(ui, "analyzerModeSection", None)
    source = section if section is not None else ui
    return append_dewetron_tail_columns(
        headers,
        values,
        extract_ui_config(source),
        mode=extract_ui_mode(source),
        test_type=test_type,
        profile=PROFILE_GENERIC,
    )


def restore_dewetron_settings_tail(
    headers: Sequence[Any], values: Sequence[Any], ui: Any
) -> Tuple[str, Any]:
    mode, config = read_dewetron_tail_columns(headers, values)
    section = getattr(ui, "analyzerModeSection", None)
    if section is not None:
        setter = getattr(section, "set_dewetron_config", None) or getattr(
            section, "set_config", None
        )
        if callable(setter):
            setter(config)
        mode_setter = getattr(section, "set_mode", None)
        if callable(mode_setter):
            mode_setter(mode)
    return mode, config


def _save_wt_rows(ui: Any) -> List[List[Any]]:
    try:
        from utils.Open_Save_ThaiWT3000_Config import Save_File_ThaiWT3000_Config
        from utils.Open_Save_ThaiWT1800_Config import Save_File_ThaiWT1800_Config
        from utils.Open_Save_ThaiWT1806E_Config import Save_File_ThaiWT1806E_Config
        from utils.Open_Save_ThaiWT5000_Config import Save_File_ThaiWT5000_Config
        from utils.Open_Save_ThaiXieBoDianLiu import _PageWidgetFinder
    except ImportError:
        return []
    choices = (
        ("radioButton_S2_WT3000", 0, Save_File_ThaiWT3000_Config),
        ("radioButton_S2_WT1800", 1, Save_File_ThaiWT1800_Config),
        ("radioButton_S2_WT1806E", 2, Save_File_ThaiWT1806E_Config),
        ("radioButton_S2_WT5000", 3, Save_File_ThaiWT5000_Config),
    )
    for attr, index, save_fn in choices:
        radio = getattr(ui, attr, None)
        if radio is not None and radio.isChecked():
            result = save_fn(_PageWidgetFinder(ui._wtStacked.widget(index)))
            return [list(row) for row in result] if result else []
    return []


def _restore_wt_rows(ui: Any, rows: Sequence[Sequence[Any]]) -> None:
    if len(rows) < 2:
        return
    try:
        from utils.Open_Save_ThaiWT3000_Config import Open_File_ThaiWT3000_Config
        from utils.Open_Save_ThaiWT1800_Config import Open_File_ThaiWT1800_Config
        from utils.Open_Save_ThaiWT1806E_Config import Open_File_ThaiWT1806E_Config
        from utils.Open_Save_ThaiWT5000_Config import Open_File_ThaiWT5000_Config
        from utils.Open_Save_ThaiXieBoDianLiu import _PageWidgetFinder
    except ImportError:
        return
    headers, values = list(rows[0]), list(rows[1])
    if len(values) < len(headers):
        values.extend([""] * (len(headers) - len(values)))
    config = dict(zip(headers, values))
    choices = (
        ("radioButton_S2_WT3000", 0, Open_File_ThaiWT3000_Config),
        ("radioButton_S2_WT1800", 1, Open_File_ThaiWT1800_Config),
        ("radioButton_S2_WT1806E", 2, Open_File_ThaiWT1806E_Config),
        ("radioButton_S2_WT5000", 3, Open_File_ThaiWT5000_Config),
    )
    for attr, index, open_fn in choices:
        radio = getattr(ui, attr, None)
        if radio is not None and radio.isChecked():
            open_fn(_PageWidgetFinder(ui._wtStacked.widget(index)), config)
            return


def settings_row_from_ui(
    ui: Any,
    headers: MutableSequence[Any],
    *,
    file_tag: str,
    schema: SchemaLike,
    test_type: str,
) -> List[Any]:
    schema_obj = get_schema(schema)
    values: List[Any] = []
    for header in headers:
        if header == "Style":
            values.append(file_tag)
        elif header == TIMING_PROFILE_JSON_COLUMN:
            values.append(profile_table_from_ui(ui).to_json())
        elif header == DEWETRON_CONFIG_COLUMN:
            values.append("")
        else:
            values.append(widget_to_csv(ui, str(header)))
    append_dewetron_settings_tail(headers, values, ui, test_type=test_type)
    # Ensure persisted profile uses the caller's schema even if a custom table
    # exposes a looser ``to_json`` implementation.
    index = list(headers).index(TIMING_PROFILE_JSON_COLUMN)
    values[index] = profile_to_json(read_ui_profile(ui, schema_obj), schema_obj)
    return values


def write_settings_csv(
    path: Any,
    ui: Any,
    headers: MutableSequence[Any],
    *,
    file_tag: str,
    schema: SchemaLike,
    test_type: str,
) -> Path:
    target = Path(path)
    values = settings_row_from_ui(
        ui,
        headers,
        file_tag=file_tag,
        schema=schema,
        test_type=test_type,
    )
    wt_rows = _save_wt_rows(ui)
    with target.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(list(headers))
        writer.writerow(values)
        writer.writerows(wt_rows)
    return target


def read_csv_rows_with_fallback(path: Any) -> List[List[str]]:
    target = Path(path)
    try:
        with target.open("r", newline="", encoding="utf-8-sig") as handle:
            return list(csv.reader(handle))
    except UnicodeDecodeError:
        with target.open("r", newline="", encoding="gbk") as handle:
            return list(csv.reader(handle))


def apply_settings_rows(
    rows: Sequence[Sequence[Any]],
    ui: Any,
    *,
    file_tag: str,
    schema: SchemaLike,
) -> Tuple[str, Any]:
    if len(rows) < 2:
        raise TimingProfileValidationError("设定文件内容不完整")
    headers, values = list(rows[0]), list(rows[1])
    if len(values) < len(headers):
        values.extend([""] * (len(headers) - len(values)))
    config = dict(zip(headers, values))
    if config.get("Style") != file_tag:
        raise TimingProfileValidationError(
            "文件类型不匹配，需要 %s 格式" % file_tag
        )
    for header, value in config.items():
        if header not in {
            "Style",
            TIMING_PROFILE_JSON_COLUMN,
            DEWETRON_CONFIG_COLUMN,
        }:
            apply_csv_widget_value(ui, header, value)
    profile_json = config.get(TIMING_PROFILE_JSON_COLUMN)
    if profile_json:
        profile_table_from_ui(ui).set_profile(
            profile_from_json(profile_json, schema)
        )
    _restore_wt_rows(ui, rows[2:4])
    return restore_dewetron_settings_tail(headers, values, ui)


def read_settings_csv(
    path: Any,
    ui: Any,
    *,
    file_tag: str,
    schema: SchemaLike,
) -> Tuple[str, Any]:
    return apply_settings_rows(
        read_csv_rows_with_fallback(path),
        ui,
        file_tag=file_tag,
        schema=schema,
    )


__all__ = [
    "COMMAND_ROW_LENGTH",
    "COMMON_SETTINGS_HEADERS",
    "SAFE_SHUTDOWN_HELPER_CONTRACT",
    "SAFE_SHUTDOWN_PARENT_WIRING",
    "ac_write_row",
    "acquisition_marker_row",
    "analyzer_mode_from_ui",
    "append_ac_voltage",
    "append_acquisition_end",
    "append_acquisition_start",
    "append_dewetron_settings_tail",
    "append_safe_shutdown",
    "append_safe_shutdown_rows",
    "apply_csv_widget_value",
    "apply_settings_rows",
    "baseline_ac_voltages",
    "baseline_dc_values",
    "build_plan_context",
    "build_settings_headers",
    "command_row",
    "device_write_row",
    "empty_command_row",
    "ensure_ten_column_rows",
    "finalize_plan",
    "format_number",
    "make_guarded_dc_iv_resolver",
    "prepare_plan_context",
    "profile_table_from_ui",
    "read_csv_rows_with_fallback",
    "read_settings_csv",
    "read_ui_profile",
    "resolve_dynamic_dc_commands",
    "restore_dewetron_settings_tail",
    "safe_shutdown_helper_available",
    "selected_profile_dc_channels",
    "settings_row_from_ui",
    "wait_row",
    "widget_to_csv",
    "write_settings_csv",
    "wt_type_from_ui",
]
