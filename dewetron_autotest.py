# -*- coding: utf-8 -*-
"""Shared, dependency-light DEWETRON AutoTest integration services.

The module contains project metadata, persistence helpers, command rewriting and
an in-memory UI registry.  It intentionally does not import ``SCPITestWave`` or
any device module so dialogs and the application bootstrap can adopt it in
small, testable steps.

Command row schema
------------------
Every normalized row is a mutable list with exactly ten columns::

    [0] device      device/adapter key (``AC``, ``DC1``, ``DEWETRON``...)
    [1] action      operation (``write``, ``query``, ``wait``...)
    [2] command     SCPI command or command payload
    [3] meta_key    optional project-specific discriminator
    [4] meta_value  optional project-specific/config payload
    [5] auxiliary   project-specific field
    [6] wt_trigger  WT automatic-measurement trigger/first wait (branch-specific)
    [7] wt_trigger  WT trigger or WT-macro wait (branch-specific)
    [8] wait/meta   branch-specific wait, generally in 0.1-second ticks
    [9] wait/meta   branch-specific wait/sample period, generally in 0.1s ticks

Columns 6--9 are deliberately *not* treated as globally interchangeable waits.
The normalizer operates on one newly generated append segment and requires
caller-supplied acquisition insertion indexes.  A caller can optionally provide
an executor-specific replacement policy for each removed WT-only row; the core
module never invents an unsupported pseudo-device command.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
import hashlib
import json
import re
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableSequence, Optional, Sequence, Tuple

from components.dewetron_autotest_panel import DewetronUiConfig


MODE_WT = "wt3000"
MODE_DEWETRON = "dewetron"
PROFILE_GENERIC = "generic"
PROFILE_HARMONIC = "harmonic"

COMMAND_ROW_LENGTH = 10
COMMAND_DEVICE_COLUMN = 0
COMMAND_ACTION_COLUMN = 1
COMMAND_TEXT_COLUMN = 2
COMMAND_WT_TRIGGER_COLUMNS: Tuple[int, ...] = (6, 7)
COMMAND_BRANCH_WAIT_COLUMNS: Tuple[int, ...] = (8, 9)
WT_ONLY_DEVICES = frozenset({"UPPER_WT_CONFIG", "WT", "WT3000"})
DEWETRON_DEVICE = "DEWETRON"
DEWETRON_START_COMMAND = ":ACQUISITION:START"
DEWETRON_STOP_COMMAND = ":ACQUISITION:STOP"
# The current executor implements a neutral wait as ``AC`` + ``wait`` with the
# 0.1-second duration in column 9.  The policy is injectable because a future
# executor may add a dedicated wait target.
WAIT_DEVICE = "AC"
WAIT_ACTION = "wait"

# Named columns are intended to be appended to each project's existing CSV
# header/values.  One JSON column is the preferred current format; the other
# names are understood by the parser for transition and legacy files.
DEWETRON_CONFIG_COLUMN = "DEWETRON_AUTOTEST_CONFIG"
DEWETRON_MODE_COLUMN = "DEWETRON_ANALYZER_MODE"
DEWETRON_RATE_COLUMN = "DEWETRON_RATE"
DEWETRON_PRECISION_COLUMN = "DEWETRON_PRECISION"
DEWETRON_WAVEFORM_COLUMN = "DEWETRON_WAVEFORM"
DEWETRON_EXPORT_FIELDS_COLUMN = "DEWETRON_EXPORT_FIELDS"
DEWETRON_PROFILE_COLUMN = "DEWETRON_PROFILE"
DEWETRON_TEST_TYPE_COLUMN = "DEWETRON_TEST_TYPE"
DEWETRON_TAIL_COLUMNS: Tuple[str, ...] = (DEWETRON_CONFIG_COLUMN,)


def _slug_key(text: Any) -> str:
    return re.sub(r"[\s_\-()（）φΦ]", "", str(text)).casefold()


@dataclass(frozen=True)
class DewetronProjectSpec:
    """Stable metadata for one AutoTest project's DEWETRON integration."""

    project_name: str
    test_type: str
    profile: str = PROFILE_GENERIC
    aliases: Tuple[str, ...] = ()
    compatibility: bool = False

    @property
    def name(self) -> str:
        return self.project_name

    @property
    def slug(self) -> str:
        return self.test_type

    @property
    def default_rate(self) -> str:
        return "SYNC to HARMONIC" if self.profile == PROFILE_HARMONIC else "Default"


# Entries without ``compatibility=True`` are eligible migration targets.
# Harmonic and flicker remain compatibility/reference registrations.
_PROJECT_SPECS: Tuple[DewetronProjectSpec, ...] = (
    DewetronProjectSpec("重连", "reconnection", aliases=("chonglian",)),
    DewetronProjectSpec(
        "过载能力测试", "overload-capability", aliases=("overloads", "90min过载")
    ),
    DewetronProjectSpec("直流分量", "dc-component", aliases=("zhiliufenliang",)),
    DewetronProjectSpec("静态QU", "static-qu", aliases=("staticQU",)),
    DewetronProjectSpec(
        "无功能力范围",
        "reactive-qcap",
        aliases=("reactiveQcap", "reactiveqcap", "无功能力"),
    ),
    DewetronProjectSpec(
        "定无功",
        "fixed-q",
        aliases=("fixedQ", "dingwugong", "固定无功"),
    ),
    DewetronProjectSpec(
        "无功注入",
        "reactive-qin",
        aliases=("reactiveQin", "wugongzhuru", "无功需求"),
    ),
    DewetronProjectSpec(
        "无功精度",
        "reactive-qacc",
        aliases=("reactiveQacc", "wugongjingdu", "无功设定精度"),
    ),
    DewetronProjectSpec(
        "有功调度",
        "active-p",
        aliases=("activeP", "yougongdiaodu", "有功控制", "有功调度测试"),
    ),
    DewetronProjectSpec(
        "防逆流测试",
        "anti-backflow",
        aliases=("antibackflow", "antiBackflow", "防逆流", "anti-vertido"),
    ),
    DewetronProjectSpec("Test_PU", "test-pu", aliases=("testPU",)),
    DewetronProjectSpec(
        "静态Cos(φ)", "static-cos-phi", aliases=("staticcosphi", "静态CosPhi")
    ),
    DewetronProjectSpec(
        "动态Cos(φ)",
        "dynamic-cos-phi",
        aliases=("dynamiccosphi", "动态CosPhi", "cosPhiP_dynamic"),
    ),
    DewetronProjectSpec(
        "动态QU",
        "dynamic-qu",
        aliases=("dynamicqu", "dynamicQU", "Q(U)动态"),
    ),
    DewetronProjectSpec(
        "Cos(φ)_Brazil",
        "cos-phi-brazil",
        aliases=("cosPhiBrazil", "CosPhi_Brazil"),
    ),
    DewetronProjectSpec(
        "10min过压保护", "overvoltage-protection-10min", aliases=("voltprotect10min",)
    ),
    DewetronProjectSpec(
        "过频降载", "overfrequency-derating", aliases=("guopinjiangzai",)
    ),
    DewetronProjectSpec(
        "欠频升载", "underfrequency-loading", aliases=("qianpinshengzai",)
    ),
    DewetronProjectSpec(
        "过欠压_过欠频",
        "voltage-frequency-protection",
        aliases=("guoqianya_pin",),
    ),
    DewetronProjectSpec(
        "巴西过欠频稳定性",
        "brazil-frequency-immunity",
        aliases=("guoqianpin_immun",),
    ),
    DewetronProjectSpec(
        "频率适应性",
        "frequency-adaptability",
        aliases=("frequencyadaptability", "电压、频率适应性"),
    ),
    DewetronProjectSpec(
        "电压适应性",
        "voltage-adaptability",
        aliases=("voltageadaptability", "dianya shiyingxing"),
    ),
    DewetronProjectSpec(
        "ROCOF保护",
        "rocof-protection",
        aliases=("rocof", "ROCOF保护测试", "频率变化率保护"),
    ),
    DewetronProjectSpec(
        "快速电压变化",
        "rapid-voltage-change",
        aliases=("rapidvolt", "快速电压变化测试", "rvc"),
    ),
    DewetronProjectSpec(
        "低电压穿越",
        "lvrt",
        aliases=("LVRT", "lvrt", "thailvrt"),
    ),
    DewetronProjectSpec(
        "相角突变",
        "phase-jump",
        aliases=("phasejump", "PhaseJump", "thaiphasejump"),
    ),
    DewetronProjectSpec(
        "动态MPPT",
        "dynamic-mppt",
        aliases=("dynamicmppt", "DynamicMPPT", "thaidynamicmppt"),
    ),
    DewetronProjectSpec(
        "固定PF=1",
        "fixed-pf",
        aliases=("fixedPF", "fixedpf", "固定PF", "固定PF_1"),
    ),
    DewetronProjectSpec(
        "静态MPPT测试",
        "static-mppt",
        aliases=("staticMPPT", "staticmppttest", "MPPT", "静态MPPT"),
    ),
    DewetronProjectSpec(
        "谐波电流",
        "harmonic",
        profile=PROFILE_HARMONIC,
        aliases=("harmonic", "xiebodianliu"),
        compatibility=True,
    ),
    DewetronProjectSpec(
        "电压闪变",
        "flicker",
        aliases=("flicker", "dianyashanbian"),
        compatibility=True,
    ),
)

PROJECT_SPECS: "OrderedDict[str, DewetronProjectSpec]" = OrderedDict(
    (spec.project_name, spec) for spec in _PROJECT_SPECS
)
PROJECT_SPECS_BY_TEST_TYPE: Dict[str, DewetronProjectSpec] = {
    spec.test_type: spec for spec in _PROJECT_SPECS
}
ELIGIBLE_PROJECT_NAMES: Tuple[str, ...] = tuple(
    spec.project_name for spec in _PROJECT_SPECS if not spec.compatibility
)

_PROJECT_LOOKUP: Dict[str, DewetronProjectSpec] = {}
for _spec in _PROJECT_SPECS:
    for _value in (_spec.project_name, _spec.test_type, *_spec.aliases):
        _PROJECT_LOOKUP[_slug_key(_value)] = _spec


def get_project_spec(project: Any) -> Optional[DewetronProjectSpec]:
    """Resolve a Chinese name, stable test_type slug, or documented alias."""
    if isinstance(project, DewetronProjectSpec):
        return project
    if project is None:
        return None
    return _PROJECT_LOOKUP.get(_slug_key(project))


def require_project_spec(project: Any) -> DewetronProjectSpec:
    """Resolve a project or raise a useful error."""
    spec = get_project_spec(project)
    if spec is None:
        raise KeyError(f"Unsupported DEWETRON AutoTest project: {project}")
    return spec


def list_project_specs(include_compatibility: bool = True) -> Tuple[DewetronProjectSpec, ...]:
    """Return specs in stable UI order."""
    if include_compatibility:
        return _PROJECT_SPECS
    return tuple(spec for spec in _PROJECT_SPECS if not spec.compatibility)


def _normalize_mode(mode: Any) -> str:
    value = str(mode or MODE_WT).strip().casefold().replace("-", "_")
    if value in {"dew", "dewetron", "dewetron_mode"}:
        return MODE_DEWETRON
    if value in {"wt", "wt3000", "power_analyzer", "analyzer", ""}:
        return MODE_WT
    raise ValueError(f"Unknown analyzer mode: {mode}")


def config_to_payload(
    config: Any,
    *,
    mode: str = MODE_DEWETRON,
    test_type: str = "",
    profile: str = PROFILE_GENERIC,
) -> Dict[str, Any]:
    """Build a stable JSON/persistence payload."""
    value = DewetronUiConfig.coerce(config)
    return {
        "version": 1,
        "mode": _normalize_mode(mode),
        "test_type": str(test_type or ""),
        "profile": str(profile or PROFILE_GENERIC),
        **value.to_dict(),
    }


def serialize_dewetron_config(
    config: Any,
    *,
    mode: str = MODE_DEWETRON,
    test_type: str = "",
    profile: str = PROFILE_GENERIC,
) -> str:
    """Serialize the preferred named-tail JSON value deterministically."""
    payload = config_to_payload(
        config, mode=mode, test_type=test_type, profile=profile
    )
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _parse_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or str(value).strip() == "":
        return default
    text = str(value).strip().casefold()
    if text in {"1", "true", "yes", "on", "checked", "是"}:
        return True
    if text in {"0", "false", "no", "off", "unchecked", "否"}:
        return False
    return default


def _parse_fields(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        parts = value
    else:
        text = str(value).strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                parsed = json.loads(text)
            except (TypeError, ValueError, json.JSONDecodeError):
                parsed = None
            if isinstance(parsed, list):
                parts = parsed
            else:
                parts = re.split(r"[|;]", text)
        else:
            parts = re.split(r"[|;]", text)
    result: List[str] = []
    seen = set()
    for item in parts:
        field = str(item).strip()
        if field and field not in seen:
            seen.add(field)
            result.append(field)
    return result


def _mapping_value(values: Mapping[str, Any], *names: str, default: Any = None) -> Any:
    lowered = {str(key).casefold(): value for key, value in values.items()}
    for name in names:
        if name in values:
            return values[name]
        if name.casefold() in lowered:
            return lowered[name.casefold()]
    return default


def parse_dewetron_config(
    value: Any,
    *,
    default: Optional[DewetronUiConfig] = None,
) -> DewetronUiConfig:
    """Parse JSON, named mappings, or legacy ``|``-delimited fields.

    Legacy accepted orders are:

    - ``rate|precision|waveform|field1|field2|...``
    - ``mode|rate|precision|waveform|field1|field2|...``

    A mapping may contain either the current JSON payload keys or the historical
    UI object names used by the flicker/harmonic dialogs.
    """
    fallback = default.copy() if default is not None else DewetronUiConfig()
    if value is None or value == "":
        return fallback
    if isinstance(value, DewetronUiConfig):
        return value.copy()

    if isinstance(value, Mapping):
        nested = _mapping_value(value, DEWETRON_CONFIG_COLUMN)
        if nested not in (None, ""):
            return parse_dewetron_config(nested, default=fallback)
        rate = _mapping_value(
            value,
            "rate_text",
            "rate",
            DEWETRON_RATE_COLUMN,
            "comboBox_DEW_MaxRefreshRate",
            default=fallback.rate_text,
        )
        precision = _mapping_value(
            value,
            "decimal_places",
            "precision",
            DEWETRON_PRECISION_COLUMN,
            "spinBox_DEW_DecimalPlaces",
            default=fallback.decimal_places,
        )
        waveform = _mapping_value(
            value,
            "realtime_waveform",
            "waveform",
            DEWETRON_WAVEFORM_COLUMN,
            "checkBox_DEW_RealtimeWaveform",
            default=fallback.realtime_waveform,
        )
        fields = _mapping_value(
            value,
            "export_fields",
            "fields",
            DEWETRON_EXPORT_FIELDS_COLUMN,
            "DEW_ExportFields",
            "treeWidget_DEW_ExportFields",
            default=fallback.export_fields,
        )
        abs_time = _mapping_value(
            value,
            "export_abs_time",
            "abs_time",
            "checkBox_DEW_ExportAbsTime",
            default=fallback.export_abs_time,
        )
        keep_dmd = _mapping_value(
            value,
            "keep_oxygen_dmd",
            "keep_dmd",
            "checkBox_DEW_KeepOxygenDmd",
            default=fallback.keep_oxygen_dmd,
        )
        try:
            precision_value = int(precision)
        except (TypeError, ValueError):
            precision_value = fallback.decimal_places
        return DewetronUiConfig(
            rate_text=str(rate),
            decimal_places=precision_value,
            realtime_waveform=_parse_bool(waveform, fallback.realtime_waveform),
            export_fields=_parse_fields(fields),
            export_abs_time=_parse_bool(abs_time, fallback.export_abs_time),
            keep_oxygen_dmd=_parse_bool(keep_dmd, fallback.keep_oxygen_dmd),
        )

    if isinstance(value, (list, tuple)):
        parts = [str(part).strip() for part in value]
    else:
        text = str(value).strip()
        if not text:
            return fallback
        try:
            parsed = json.loads(text)
        except (TypeError, ValueError, json.JSONDecodeError):
            parsed = None
        if isinstance(parsed, Mapping):
            return parse_dewetron_config(parsed, default=fallback)
        if isinstance(parsed, list):
            parts = [str(part).strip() for part in parsed]
        else:
            parts = [part.strip() for part in text.split("|")]

    if parts and parts[0].casefold() in {
        "wt",
        "wt3000",
        "dew",
        "dewetron",
    }:
        parts = parts[1:]
    if not parts:
        return fallback

    rate = parts[0] or fallback.rate_text
    try:
        precision = int(parts[1]) if len(parts) > 1 and parts[1] != "" else fallback.decimal_places
    except ValueError:
        precision = fallback.decimal_places
    waveform = (
        _parse_bool(parts[2], fallback.realtime_waveform)
        if len(parts) > 2
        else fallback.realtime_waveform
    )
    fields = _parse_fields(parts[3:]) if len(parts) > 3 else list(fallback.export_fields)
    return DewetronUiConfig(rate, precision, waveform, fields)


def parse_dewetron_mode(value: Any, default: str = MODE_WT) -> str:
    """Extract the analyzer mode from JSON, named columns, or legacy text."""
    if value is None or value == "":
        return _normalize_mode(default)
    if isinstance(value, Mapping):
        nested = _mapping_value(value, DEWETRON_CONFIG_COLUMN)
        if nested not in (None, ""):
            return parse_dewetron_mode(nested, default)
        mode = _mapping_value(
            value, "mode", "dew_mode", DEWETRON_MODE_COLUMN, default=default
        )
        return _normalize_mode(mode)
    if isinstance(value, str):
        text = value.strip()
        try:
            parsed = json.loads(text)
        except (TypeError, ValueError, json.JSONDecodeError):
            parsed = None
        if isinstance(parsed, Mapping):
            return parse_dewetron_mode(parsed, default)
        first = text.split("|", 1)[0]
        try:
            return _normalize_mode(first)
        except ValueError:
            return _normalize_mode(default)
    return _normalize_mode(default)


def append_dewetron_tail_columns(
    headers: MutableSequence[Any],
    values: MutableSequence[Any],
    config: Any,
    *,
    mode: str = MODE_DEWETRON,
    test_type: str = "",
    profile: str = PROFILE_GENERIC,
    preserve_extra_values: bool = True,
) -> Tuple[MutableSequence[Any], MutableSequence[Any]]:
    """Append/update the named JSON tail column without positional coupling.

    Some legacy files have value rows longer than their header row.  Their
    trailing values (and separate WT rows managed by the caller) must not be
    displaced.  Such extras are temporarily removed, the named tail is aligned
    with its header, then extras are appended unchanged.
    """
    extras: List[Any] = []
    if len(values) > len(headers):
        if not preserve_extra_values:
            raise ValueError("value row is longer than its header row")
        extras = list(values[len(headers) :])
        del values[len(headers) :]
    while len(values) < len(headers):
        values.append("")
    payload = serialize_dewetron_config(
        config, mode=mode, test_type=test_type, profile=profile
    )
    if DEWETRON_CONFIG_COLUMN in headers:
        index = list(headers).index(DEWETRON_CONFIG_COLUMN)
        values[index] = payload
    else:
        headers.append(DEWETRON_CONFIG_COLUMN)
        values.append(payload)
    values.extend(extras)
    return headers, values


# Alternate verbs help future Open_Save adapters read naturally.
write_named_tail_columns = append_dewetron_tail_columns


def read_dewetron_tail_columns(
    headers: Sequence[Any],
    values: Sequence[Any],
    *,
    default: Optional[DewetronUiConfig] = None,
) -> Tuple[str, DewetronUiConfig]:
    """Read DEWETRON values by header name; missing tail columns are harmless."""
    row = {
        str(header): values[index] if index < len(values) else ""
        for index, header in enumerate(headers)
    }
    return parse_dewetron_mode(row, MODE_WT), parse_dewetron_config(
        row, default=default
    )


read_named_tail_columns = read_dewetron_tail_columns


def config_fingerprint(
    config: Any,
    *,
    test_type: str = "",
    profile: str = PROFILE_GENERIC,
) -> str:
    """Return a deterministic SHA-256 append/preflight fingerprint."""
    value = DewetronUiConfig.coerce(config)
    payload = {
        "test_type": str(test_type or ""),
        "profile": str(profile or PROFILE_GENERIC),
        "rate_text": value.rate_text.strip(),
        "decimal_places": value.decimal_places,
        "realtime_waveform": bool(value.realtime_waveform),
        "export_abs_time": bool(getattr(value, "export_abs_time", False)),
        "keep_oxygen_dmd": bool(getattr(value, "keep_oxygen_dmd", False)),
        # Export order has no device semantic and must not create false changes.
        "export_fields": sorted(set(value.export_fields)),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


fingerprint_config = config_fingerprint


def _read_widget_value(widget: Any) -> Any:
    if widget is None:
        return None
    if hasattr(widget, "currentText"):
        return widget.currentText()
    if hasattr(widget, "value"):
        return widget.value()
    if hasattr(widget, "isChecked"):
        return widget.isChecked()
    if hasattr(widget, "toPlainText"):
        return widget.toPlainText()
    if hasattr(widget, "text"):
        return widget.text()
    return None


def extract_ui_config(ui: Any) -> DewetronUiConfig:
    """Extract generic DEWETRON values from a panel, section, or legacy UI."""
    if isinstance(ui, DewetronUiConfig):
        return ui.copy()
    for method_name in ("get_dewetron_config", "get_config", "snapshot_config"):
        method = getattr(ui, method_name, None)
        if callable(method):
            value = method()
            if isinstance(value, DewetronUiConfig):
                return value.copy()
            if isinstance(value, Mapping):
                return DewetronUiConfig.from_mapping(value)

    rate = _read_widget_value(
        getattr(ui, "comboBox_DEW_MaxRefreshRate", getattr(ui, "rate_combo", None))
    )
    precision = _read_widget_value(
        getattr(ui, "spinBox_DEW_DecimalPlaces", getattr(ui, "precision_spin", None))
    )
    waveform = _read_widget_value(
        getattr(
            ui,
            "checkBox_DEW_RealtimeWaveform",
            getattr(ui, "waveform_checkbox", None),
        )
    )
    abs_time = _read_widget_value(getattr(ui, "checkBox_DEW_ExportAbsTime", None))
    keep_dmd = _read_widget_value(getattr(ui, "checkBox_DEW_KeepOxygenDmd", None))
    fields: List[str] = []
    getter = getattr(ui, "get_checked_export_fields", None)
    if callable(getter):
        fields = _parse_fields(getter())
    elif hasattr(ui, "dewetron_panel"):
        fields = extract_ui_config(ui.dewetron_panel).export_fields

    return DewetronUiConfig(
        rate_text="Default" if rate is None else str(rate),
        decimal_places=3 if precision is None else int(precision),
        realtime_waveform=False if waveform is None else bool(waveform),
        export_fields=fields,
        export_abs_time=False if abs_time is None else bool(abs_time),
        keep_oxygen_dmd=False if keep_dmd is None else bool(keep_dmd),
    )


extract_dewetron_ui_config = extract_ui_config


def extract_ui_mode(ui: Any) -> str:
    """Read a practical ``mode``/``_mode`` or DEWETRON radio state."""
    for name in ("current_mode",):
        value = getattr(ui, name, None)
        if callable(value):
            return _normalize_mode(value())
    for name in ("mode", "analyzer_mode", "_mode"):
        value = getattr(ui, name, None)
        if value is not None and not callable(value):
            return _normalize_mode(value)
    radio = getattr(ui, "radio_dewetron", None)
    if radio is not None and hasattr(radio, "isChecked") and radio.isChecked():
        return MODE_DEWETRON
    return MODE_WT


def make_command_row(
    device: Any = "",
    action: Any = "",
    command: Any = "",
    *,
    meta_key: Any = "",
    meta_value: Any = "",
    wait_01s: Any = "",
) -> List[Any]:
    """Create one command row using the exact ten-column schema above."""
    row: List[Any] = ["" for _ in range(COMMAND_ROW_LENGTH)]
    row[0] = device
    row[1] = action
    row[2] = command
    row[3] = meta_key
    row[4] = meta_value
    row[9] = wait_01s
    return row


def coerce_command_row(row: Any) -> List[Any]:
    """Copy a sequence/mapping into an exact ten-column command row.

    Short legacy rows are padded.  Longer rows are rejected rather than
    silently losing project-specific data.
    """
    if isinstance(row, Mapping):
        values = [
            row.get("device", ""),
            row.get("action", ""),
            row.get("command", ""),
            row.get("meta_key", ""),
            row.get("meta_value", ""),
            row.get("auxiliary", row.get("auxiliary_1", "")),
            row.get("wt_trigger_1", row.get("auxiliary_2", "")),
            row.get("wt_trigger_2", ""),
            row.get("wait_or_meta_1", ""),
            row.get("wait_or_meta_2", row.get("wait_01s", "")),
        ]
    elif isinstance(row, (str, bytes)) or not isinstance(row, Sequence):
        raise TypeError("command row must be a non-string sequence or mapping")
    else:
        values = list(row)
    if len(values) < COMMAND_ROW_LENGTH:
        values.extend([""] * (COMMAND_ROW_LENGTH - len(values)))
    elif len(values) > COMMAND_ROW_LENGTH:
        raise ValueError(
            f"command row has {len(values)} columns; expected at most "
            f"{COMMAND_ROW_LENGTH}"
        )
    return values


def make_wait_row(wait_01s: Any) -> List[Any]:
    """Create the current executor-compatible neutral wait representation."""
    return make_command_row(WAIT_DEVICE, WAIT_ACTION, "", wait_01s=wait_01s)


def _is_wt_only(row: Sequence[Any]) -> bool:
    return str(row[COMMAND_DEVICE_COLUMN]).strip().upper() in WT_ONLY_DEVICES


@dataclass(frozen=True)
class RemovedWtCommand:
    """WT-only command removed from a newly generated append segment."""

    source_index: int
    row: Tuple[Any, ...]

    @property
    def device(self) -> str:
        return str(self.row[COMMAND_DEVICE_COLUMN])


@dataclass
class CommandSegmentNormalization:
    """Normalized rows plus audit metadata needed by future integrations."""

    rows: List[List[Any]]
    removed_wt_rows: List[RemovedWtCommand] = field(default_factory=list)
    start_index: Optional[int] = None
    stop_index: Optional[int] = None


def _normalize_insertion_index(index: int, length: int, name: str) -> int:
    if isinstance(index, bool) or not isinstance(index, int):
        raise TypeError(f"{name} must be an integer")
    if index < 0:
        index += length + 1
    if not 0 <= index <= length:
        raise IndexError(f"{name} {index} is outside segment length {length}")
    return index


def _coerce_replacement_rows(value: Any) -> List[List[Any]]:
    if value is None:
        return []
    if isinstance(value, Mapping):
        return [coerce_command_row(value)]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        if not value:
            return []
        if isinstance(value[0], (Sequence, Mapping)) and not isinstance(
            value[0], (str, bytes)
        ):
            return [coerce_command_row(row) for row in value]
        return [coerce_command_row(value)]
    raise TypeError("WT replacement policy must return a row, rows, or None")


def normalize_dewetron_command_segment(
    rows: Iterable[Any],
    *,
    enabled: bool = True,
    start_index: Optional[int] = None,
    stop_index: Optional[int] = None,
    wt_row_policy: Optional[Callable[[RemovedWtCommand], Any]] = None,
    clear_wt_triggers: bool = True,
    return_metadata: bool = False,
) -> Any:
    """Rewrite one *new append segment* for DEWETRON execution.

    ``start_index`` and ``stop_index`` are boundaries in the retained segment
    after WT-only row replacement and before acquisition rows are inserted.
    Both are mandatory in DEWETRON mode, and ``start_index <= stop_index``.
    This prevents a utility from guessing where acquisition belongs in a
    project's AC/DC lifecycle.

    WT-only rows are removed.  ``wt_row_policy`` may return one executor-
    compatible replacement row (or several rows) for a removed command; it can,
    for example, turn a *known* WT macro dwell into :func:`make_wait_row`.
    Without a policy no ambiguous column 6--9 timing is invented.  Removed rows
    are available through ``return_metadata=True`` for logging/audit.

    Existing acquisition START/STOP rows are rejected: normalization owns one
    newly generated append segment and must not silently deduplicate boundaries
    from an already-normalized or combined command list.
    """
    source = [coerce_command_row(row) for row in rows]
    if not enabled:
        result = CommandSegmentNormalization(rows=source)
        return result if return_metadata else result.rows
    if start_index is None or stop_index is None:
        raise ValueError(
            "start_index and stop_index are required for a DEWETRON append segment"
        )

    retained: List[List[Any]] = []
    removed: List[RemovedWtCommand] = []
    for source_index, row in enumerate(source):
        if (
            str(row[0]).strip().upper() == DEWETRON_DEVICE
            and str(row[2]).strip().upper()
            in {DEWETRON_START_COMMAND, DEWETRON_STOP_COMMAND}
        ):
            raise ValueError(
                "segment already contains a DEWETRON acquisition boundary"
            )
        if _is_wt_only(row):
            removed_row = RemovedWtCommand(source_index, tuple(row))
            removed.append(removed_row)
            if wt_row_policy is not None:
                retained.extend(_coerce_replacement_rows(wt_row_policy(removed_row)))
            continue

        clean = list(row)
        if clear_wt_triggers:
            for column in COMMAND_WT_TRIGGER_COLUMNS:
                clean[column] = ""
        retained.append(clean)

    start = _normalize_insertion_index(start_index, len(retained), "start_index")
    stop = _normalize_insertion_index(stop_index, len(retained), "stop_index")
    if start > stop:
        raise ValueError("start_index must be less than or equal to stop_index")

    start_row = make_command_row(
        DEWETRON_DEVICE, "write", DEWETRON_START_COMMAND
    )
    stop_row = make_command_row(
        DEWETRON_DEVICE, "write", DEWETRON_STOP_COMMAND
    )
    normalized = [
        *retained[:start],
        start_row,
        *retained[start:stop],
        stop_row,
        *retained[stop:],
    ]
    result = CommandSegmentNormalization(
        rows=normalized,
        removed_wt_rows=removed,
        start_index=start,
        stop_index=stop + 1,
    )
    return result if return_metadata else result.rows


# Practical aliases for future Send adapters.
normalize_command_segment = normalize_dewetron_command_segment
normalize_commands_for_dewetron = normalize_dewetron_command_segment


@dataclass
class _RegisteredSection:
    project_name: str
    spec: DewetronProjectSpec
    section: Any
    apply_handler: Optional[Callable[..., Any]] = None
    preflight_handler: Optional[Callable[..., Any]] = None
    append_fingerprint: Optional[str] = None


@dataclass
class AppendConfigCheck:
    """Result of comparing a section snapshot with an append baseline."""

    valid: bool
    fingerprint: str
    errors: List[str] = field(default_factory=list)
    changed: bool = False
    previous_fingerprint: Optional[str] = None

    def __bool__(self) -> bool:
        return self.valid


class DewetronAutoTestCoordinator:
    """Registry/facade for dialog sections with no main-module globals."""

    def __init__(self, collector: Any = None) -> None:
        self.collector = collector
        self._sections: "OrderedDict[str, _RegisteredSection]" = OrderedDict()
        self._current_project: Optional[str] = None

    def set_collector(self, collector: Any) -> None:
        self.collector = collector

    @staticmethod
    def _set_section_rate(section: Any, rate_text: str) -> bool:
        """Set only the rate control, preserving pending export-tree state."""
        target = getattr(section, "dewetron_panel", section)
        combo = getattr(
            target,
            "comboBox_DEW_MaxRefreshRate",
            getattr(target, "rate_combo", None),
        )
        if combo is None or not hasattr(combo, "setCurrentText"):
            return False
        if hasattr(combo, "findText") and combo.findText(rate_text) < 0:
            combo.addItem(rate_text)
        combo.setCurrentText(rate_text)
        return True

    def register_section(
        self,
        project: Any,
        section: Any,
        *,
        apply_handler: Optional[Callable[..., Any]] = None,
        preflight_handler: Optional[Callable[..., Any]] = None,
        make_current: bool = False,
        apply_profile_defaults: bool = True,
    ) -> Any:
        """Register a panel/section/UI against a stable project spec.

        The harmonic profile adopts ``SYNC to HARMONIC`` only when the section
        still has the generic untouched ``Default`` rate. Explicit user/saved
        values are never overwritten.
        """
        spec = require_project_spec(project)
        if apply_profile_defaults and spec.profile == PROFILE_HARMONIC:
            current = extract_ui_config(section)
            if current.rate_text == "Default":
                if not self._set_section_rate(section, spec.default_rate):
                    current.rate_text = spec.default_rate
                    self._restore_section_config(section, current)
        self._sections[spec.project_name] = _RegisteredSection(
            project_name=spec.project_name,
            spec=spec,
            section=section,
            apply_handler=apply_handler,
            preflight_handler=preflight_handler,
        )
        if self._current_project is None or make_current:
            self._current_project = spec.project_name
        return section

    # Concise API aliases used by bootstrap/dialog adapters.
    register = register_section

    def unregister_section(self, project: Any) -> Optional[Any]:
        spec = get_project_spec(project)
        if spec is None:
            return None
        entry = self._sections.pop(spec.project_name, None)
        if self._current_project == spec.project_name:
            self._current_project = next(iter(self._sections), None)
        return entry.section if entry else None

    unregister = unregister_section

    def section(self, project: Any = None) -> Optional[Any]:
        name = self._resolve_registered_name(project)
        entry = self._sections.get(name) if name else None
        return entry.section if entry else None

    get_section = section

    def registered_projects(self) -> Tuple[str, ...]:
        return tuple(self._sections)

    def set_current_project(self, project: Any) -> None:
        spec = require_project_spec(project)
        if spec.project_name not in self._sections:
            raise KeyError(f"Project is not registered: {spec.project_name}")
        self._current_project = spec.project_name

    def current_project(self) -> Optional[str]:
        return self._current_project

    def _resolve_registered_name(self, project: Any = None) -> Optional[str]:
        if project is None:
            return self._current_project
        spec = get_project_spec(project)
        return spec.project_name if spec else None

    def _entry(self, project: Any = None) -> _RegisteredSection:
        name = self._resolve_registered_name(project)
        if not name or name not in self._sections:
            raise KeyError(f"DEWETRON AutoTest section is not registered: {project}")
        return self._sections[name]

    def current_mode(self, project: Any = None) -> str:
        return extract_ui_mode(self._entry(project).section)

    mode = current_mode

    def current_test_type(self, project: Any = None) -> str:
        return self._entry(project).spec.test_type

    test_type = current_test_type

    def snapshot_config(self, project: Any = None) -> DewetronUiConfig:
        return extract_ui_config(self._entry(project).section)

    snapshot = snapshot_config

    @staticmethod
    def _restore_section_config(section: Any, value: DewetronUiConfig) -> None:
        for method_name in ("set_dewetron_config", "set_config", "restore_config"):
            method = getattr(section, method_name, None)
            if callable(method):
                method(value)
                return
        raise TypeError("Registered section does not expose a config restore API")

    def restore_config(self, project: Any, config: Any = None) -> None:
        """Restore a project snapshot.

        For convenience, ``restore_config(config)`` targets the current project,
        while ``restore_config(project, config)`` targets an explicit project.
        """
        if config is None:
            config = project
            project = None
        section = self._entry(project).section
        value = DewetronUiConfig.coerce(config)
        self._restore_section_config(section, value)

    restore = restore_config

    def validate_config(
        self,
        project: Any = None,
        *,
        require_export_fields: bool = True,
    ) -> List[str]:
        return self.snapshot_config(project).validation_errors(require_export_fields)

    validate = validate_config

    def fingerprint(self, project: Any = None) -> str:
        entry = self._entry(project)
        return config_fingerprint(
            self.snapshot_config(project),
            test_type=entry.spec.test_type,
            profile=entry.spec.profile,
        )

    def validate_append_config(
        self,
        project: Any = None,
        *,
        expected_fingerprint: Optional[str] = None,
        remember: bool = False,
        require_export_fields: bool = True,
    ) -> AppendConfigCheck:
        """Validate and compare an append configuration without side effects."""
        entry = self._entry(project)
        errors = self.validate_config(
            project, require_export_fields=require_export_fields
        )
        fingerprint = self.fingerprint(project)
        previous = (
            expected_fingerprint
            if expected_fingerprint is not None
            else entry.append_fingerprint
        )
        result = AppendConfigCheck(
            valid=not errors,
            fingerprint=fingerprint,
            errors=errors,
            changed=previous is not None and previous != fingerprint,
            previous_fingerprint=previous,
        )
        if remember and result.valid:
            entry.append_fingerprint = fingerprint
        return result

    validate_append = validate_append_config

    def remember_append_config(self, project: Any = None) -> str:
        result = self.validate_append_config(project, remember=True)
        if not result.valid:
            raise ValueError("; ".join(result.errors))
        return result.fingerprint

    def bind_handlers(
        self,
        project: Any,
        *,
        apply_handler: Optional[Callable[..., Any]] = None,
        preflight_handler: Optional[Callable[..., Any]] = None,
    ) -> None:
        """Store future apply/preflight hooks without importing application globals."""
        entry = self._entry(project)
        if apply_handler is not None:
            entry.apply_handler = apply_handler
        if preflight_handler is not None:
            entry.preflight_handler = preflight_handler

    def run_apply(self, project: Any = None, *args: Any, **kwargs: Any) -> Any:
        entry = self._entry(project)
        if entry.apply_handler is None:
            raise RuntimeError(f"No apply handler bound for {entry.project_name}")
        return entry.apply_handler(
            entry.spec, self.snapshot_config(project), *args, **kwargs
        )

    def run_preflight(self, project: Any = None, *args: Any, **kwargs: Any) -> Any:
        entry = self._entry(project)
        if entry.preflight_handler is None:
            return self.validate_append_config(project)
        return entry.preflight_handler(
            entry.spec, self.snapshot_config(project), *args, **kwargs
        )

    def normalize_segment(
        self,
        rows: Iterable[Any],
        project: Any = None,
        **policy: Any,
    ) -> Any:
        """Normalize one append segment using caller-owned boundary policy."""
        return normalize_dewetron_command_segment(
            rows,
            enabled=self.current_mode(project) == MODE_DEWETRON,
            **policy,
        )


# Shorter registry name for callers that only need registration/state features.
DewetronAutoTestRegistry = DewetronAutoTestCoordinator


__all__ = [
    "AppendConfigCheck",
    "CommandSegmentNormalization",
    "COMMAND_ACTION_COLUMN",
    "COMMAND_BRANCH_WAIT_COLUMNS",
    "COMMAND_DEVICE_COLUMN",
    "COMMAND_ROW_LENGTH",
    "COMMAND_TEXT_COLUMN",
    "COMMAND_WT_TRIGGER_COLUMNS",
    "DEWETRON_CONFIG_COLUMN",
    "DEWETRON_DEVICE",
    "DEWETRON_EXPORT_FIELDS_COLUMN",
    "DEWETRON_MODE_COLUMN",
    "DEWETRON_PRECISION_COLUMN",
    "DEWETRON_PROFILE_COLUMN",
    "DEWETRON_RATE_COLUMN",
    "DEWETRON_START_COMMAND",
    "DEWETRON_STOP_COMMAND",
    "DEWETRON_TAIL_COLUMNS",
    "DEWETRON_TEST_TYPE_COLUMN",
    "DEWETRON_WAVEFORM_COLUMN",
    "DewetronAutoTestCoordinator",
    "DewetronAutoTestRegistry",
    "DewetronProjectSpec",
    "ELIGIBLE_PROJECT_NAMES",
    "MODE_DEWETRON",
    "MODE_WT",
    "PROFILE_GENERIC",
    "PROFILE_HARMONIC",
    "PROJECT_SPECS",
    "PROJECT_SPECS_BY_TEST_TYPE",
    "RemovedWtCommand",
    "WAIT_ACTION",
    "WAIT_DEVICE",
    "WT_ONLY_DEVICES",
    "append_dewetron_tail_columns",
    "coerce_command_row",
    "config_fingerprint",
    "config_to_payload",
    "extract_dewetron_ui_config",
    "extract_ui_config",
    "extract_ui_mode",
    "fingerprint_config",
    "get_project_spec",
    "list_project_specs",
    "make_command_row",
    "make_wait_row",
    "normalize_command_segment",
    "normalize_commands_for_dewetron",
    "normalize_dewetron_command_segment",
    "parse_dewetron_config",
    "parse_dewetron_mode",
    "read_dewetron_tail_columns",
    "read_named_tail_columns",
    "require_project_spec",
    "serialize_dewetron_config",
    "write_named_tail_columns",
]
