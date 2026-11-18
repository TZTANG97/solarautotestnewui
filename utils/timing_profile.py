# -*- coding: utf-8 -*-
"""Shared, strict timing-profile model and JSON-in-CSV serialization.

The CSV integration stores the complete profile in one named JSON column.  New
fields can therefore be added inside ``extensions`` without changing the
positional CSV layout used by older project settings files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union


PROFILE_VERSION = 1
TIMING_PROFILE_JSON_COLUMN = "TIMING_PROFILE_JSON"

TIME_UNITS: Tuple[str, ...] = ("毫秒", "秒", "分钟", "小时")
TIME_UNIT_SECONDS = {
    "毫秒": 0.001,
    "ms": 0.001,
    "millisecond": 0.001,
    "milliseconds": 0.001,
    "秒": 1.0,
    "s": 1.0,
    "sec": 1.0,
    "second": 1.0,
    "seconds": 1.0,
    "分钟": 60.0,
    "分": 60.0,
    "min": 60.0,
    "minute": 60.0,
    "minutes": 60.0,
    "小时": 3600.0,
    "时": 3600.0,
    "h": 3600.0,
    "hour": 3600.0,
    "hours": 3600.0,
}

COMMON_FIELDS: Tuple[str, ...] = (
    "enabled",
    "label",
    "t_pre",
    "t_pre_unit",
    "t_dwell",
    "t_dwell_unit",
    "t_post",
    "t_post_unit",
    "repeats",
    "extensions",
)

SUPPORTED_VALUE_FIELDS: Tuple[str, ...] = (
    "u_pu",
    "l1",
    "l2",
    "l3",
    "phase_deg",
    "p_pct",
    "irr_wm2",
    "temp_c",
    "pmpp",
    "umpp",
    "ff",
)

# Schema fields stored/edited as booleans (checkbox columns).
SUPPORTED_BOOL_FIELDS: Tuple[str, ...] = ("l1", "l2", "l3")


class TimingProfileValidationError(ValueError):
    """Raised when a profile would produce an ambiguous or unsafe sequence."""


@dataclass(frozen=True)
class TimingProfileSchema:
    """Schema for the project-specific value columns in a timing profile."""

    key: str
    fields: Tuple[str, ...]
    required: Tuple[str, ...] = ()
    required_any: Tuple[Tuple[str, ...], ...] = ()
    ranges: Mapping[str, Tuple[Optional[float], Optional[float]]] = field(
        default_factory=dict
    )
    defaults: Mapping[str, Any] = field(default_factory=dict)
    labels: Mapping[str, str] = field(default_factory=dict)
    bool_fields: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.key or not str(self.key).strip():
            raise ValueError("schema key must not be empty")
        unknown = set(self.fields) - set(SUPPORTED_VALUE_FIELDS)
        if unknown:
            raise ValueError("unsupported schema fields: %s" % sorted(unknown))
        bad_bool = set(self.bool_fields) - set(self.fields)
        if bad_bool:
            raise ValueError("bool_fields not in schema.fields: %s" % sorted(bad_bool))
        bad_bool_support = set(self.bool_fields) - set(SUPPORTED_BOOL_FIELDS)
        if bad_bool_support:
            raise ValueError(
                "unsupported bool fields: %s" % sorted(bad_bool_support)
            )
        missing = set(self.required) - set(self.fields)
        if missing:
            raise ValueError("required fields not present in schema: %s" % sorted(missing))
        for group in self.required_any:
            group_missing = set(group) - set(self.fields)
            if group_missing:
                raise ValueError(
                    "required-any fields not present in schema: %s"
                    % sorted(group_missing)
                )


LVRT_SCHEMA = TimingProfileSchema(
    key="lvrt",
    fields=("u_pu", "l1", "l2", "l3"),
    required=("u_pu",),
    ranges={"u_pu": (0.0, 2.0)},
    defaults={"u_pu": 0.2, "l1": True, "l2": True, "l3": True},
    labels={"u_pu": "电压(p.u.)", "l1": "L1", "l2": "L2", "l3": "L3"},
    bool_fields=("l1", "l2", "l3"),
)

PHASE_JUMP_SCHEMA = TimingProfileSchema(
    key="phase_jump",
    fields=("phase_deg",),
    required=("phase_deg",),
    ranges={"phase_deg": (-180.0, 180.0)},
    defaults={"phase_deg": 10.0},
    labels={"phase_deg": "相角突变(°)"},
)

DYNAMIC_MPPT_SCHEMA = TimingProfileSchema(
    key="dynamic_mppt",
    fields=("p_pct", "irr_wm2", "temp_c", "pmpp", "umpp", "ff"),
    required_any=(("p_pct", "pmpp"),),
    ranges={
        "p_pct": (0.0, 100.0),
        "irr_wm2": (0.0, 2000.0),
        "temp_c": (-100.0, 200.0),
        "pmpp": (0.0, None),
        "umpp": (0.0, None),
        "ff": (0.0, 1.0),
    },
    defaults={
        "p_pct": 100.0,
        "irr_wm2": 1000.0,
        "temp_c": 25.0,
        "pmpp": 8000.0,
        "umpp": 650.0,
        "ff": 0.8,
    },
    labels={
        "p_pct": "功率(%)",
        "irr_wm2": "辐照度(W/m²)",
        "temp_c": "温度(°C)",
        "pmpp": "Pmpp(W)",
        "umpp": "Umpp(V)",
        "ff": "填充因子",
    },
)

SCHEMAS: Dict[str, TimingProfileSchema] = {
    LVRT_SCHEMA.key: LVRT_SCHEMA,
    PHASE_JUMP_SCHEMA.key: PHASE_JUMP_SCHEMA,
    DYNAMIC_MPPT_SCHEMA.key: DYNAMIC_MPPT_SCHEMA,
}

SchemaLike = Union[str, TimingProfileSchema]


def get_schema(schema: SchemaLike) -> TimingProfileSchema:
    """Resolve a schema object or a stable schema key."""

    if isinstance(schema, TimingProfileSchema):
        return schema
    key = str(schema or "").strip().lower().replace("-", "_")
    aliases = {
        "phasejump": "phase_jump",
        "dynamicmppt": "dynamic_mppt",
        "mppt": "dynamic_mppt",
    }
    key = aliases.get(key, key)
    try:
        return SCHEMAS[key]
    except KeyError as exc:
        raise TimingProfileValidationError("未知时序 schema: %s" % schema) from exc


def _finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise TimingProfileValidationError("%s 不能是布尔值" % name)
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise TimingProfileValidationError("%s 必须是数字" % name) from exc
    if not math.isfinite(number):
        raise TimingProfileValidationError("%s 必须是有限数字" % name)
    return number


def _strict_bool(value: Any, name: str = "enabled") -> bool:
    if isinstance(value, bool):
        return value
    if value in (0, 1):
        return bool(value)
    text = str(value).strip().casefold()
    if text in {"1", "true", "yes", "on", "是"}:
        return True
    if text in {"0", "false", "no", "off", "否"}:
        return False
    raise TimingProfileValidationError("%s 必须是布尔值" % name)


def normalize_time_unit(unit: Any) -> str:
    """Return one of the four stable Chinese unit names."""

    text = str(unit or "").strip()
    if not text:
        return "秒"
    key = text.casefold()
    if key not in TIME_UNIT_SECONDS:
        raise TimingProfileValidationError("不支持的时间单位: %s" % unit)
    factor = TIME_UNIT_SECONDS[key]
    for canonical in TIME_UNITS:
        if TIME_UNIT_SECONDS[canonical] == factor:
            return canonical
    raise TimingProfileValidationError("不支持的时间单位: %s" % unit)


def time_to_seconds(value: Any, unit: Any = "秒") -> float:
    number = _finite_number(value, "时间")
    if number < 0:
        raise TimingProfileValidationError("时间不能小于 0")
    canonical = normalize_time_unit(unit)
    return number * TIME_UNIT_SECONDS[canonical]


def time_to_ticks(value: Any, unit: Any = "秒") -> int:
    """Convert to the executor's 0.1-second ticks without truncating positives."""

    seconds = time_to_seconds(value, unit)
    if seconds == 0:
        return 0
    return max(1, int(round(seconds * 10.0)))


def default_profile_row(
    schema: SchemaLike,
    *,
    label: str = "",
    enabled: bool = True,
) -> Dict[str, Any]:
    schema_obj = get_schema(schema)
    row: Dict[str, Any] = {
        "enabled": bool(enabled),
        "label": str(label),
        "t_pre": 1.0,
        "t_pre_unit": "秒",
        "t_dwell": 1.0,
        "t_dwell_unit": "秒",
        "t_post": 1.0,
        "t_post_unit": "秒",
        "repeats": 1,
    }
    for name in schema_obj.fields:
        row[name] = schema_obj.defaults.get(name)
    return row


def _normalize_extensions(value: Any, row_number: int) -> Dict[str, Any]:
    if value in (None, ""):
        return {}
    if not isinstance(value, Mapping):
        raise TimingProfileValidationError(
            "第 %d 行 extensions 必须是 JSON 对象" % row_number
        )
    extensions = {str(key): val for key, val in value.items()}
    try:
        json.dumps(extensions, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise TimingProfileValidationError(
            "第 %d 行 extensions 不是合法 JSON" % row_number
        ) from exc
    return extensions


def validate_profile_row(
    row: Mapping[str, Any],
    schema: SchemaLike,
    *,
    row_number: int = 1,
) -> Dict[str, Any]:
    """Validate and normalize one profile row.

    Unknown keys are rejected.  Future/project-private values must be placed in
    the explicit ``extensions`` object so accidental misspellings cannot become
    silently ignored commands.
    """

    schema_obj = get_schema(schema)
    if not isinstance(row, Mapping):
        raise TimingProfileValidationError("第 %d 行必须是对象" % row_number)
    allowed = set(COMMON_FIELDS) | set(schema_obj.fields)
    unknown = set(str(key) for key in row) - allowed
    if unknown:
        raise TimingProfileValidationError(
            "第 %d 行包含未知字段: %s；扩展字段请放入 extensions"
            % (row_number, ", ".join(sorted(unknown)))
        )

    normalized: Dict[str, Any] = {}
    normalized["enabled"] = _strict_bool(row.get("enabled", True))
    label = str(row.get("label", "") or "").strip()
    if len(label) > 128:
        raise TimingProfileValidationError("第 %d 行 label 超过 128 字符" % row_number)
    normalized["label"] = label

    common_unit = row.get("time_unit", "秒")
    for time_name in ("t_pre", "t_dwell", "t_post"):
        value = _finite_number(row.get(time_name, 0), "第 %d 行 %s" % (row_number, time_name))
        if value < 0:
            raise TimingProfileValidationError(
                "第 %d 行 %s 不能小于 0" % (row_number, time_name)
            )
        unit_name = "%s_unit" % time_name
        unit = normalize_time_unit(row.get(unit_name, common_unit))
        # Conversion also guards values which overflow to infinity.
        seconds = value * TIME_UNIT_SECONDS[unit]
        if not math.isfinite(seconds):
            raise TimingProfileValidationError(
                "第 %d 行 %s 超出范围" % (row_number, time_name)
            )
        normalized[time_name] = value
        normalized[unit_name] = unit

    repeats_raw = row.get("repeats", 1)
    repeats_number = _finite_number(repeats_raw, "第 %d 行 repeats" % row_number)
    if repeats_number != int(repeats_number):
        raise TimingProfileValidationError("第 %d 行 repeats 必须是整数" % row_number)
    repeats = int(repeats_number)
    if repeats < 1 or repeats > 10000:
        raise TimingProfileValidationError(
            "第 %d 行 repeats 必须在 1..10000" % row_number
        )
    normalized["repeats"] = repeats

    bool_names = set(schema_obj.bool_fields)
    for name in schema_obj.fields:
        raw = row.get(name, schema_obj.defaults.get(name))
        if name in bool_names:
            if raw in (None, ""):
                default_bool = schema_obj.defaults.get(name, True)
                normalized[name] = _strict_bool(
                    default_bool, "第 %d 行 %s" % (row_number, name)
                )
            else:
                normalized[name] = _strict_bool(
                    raw, "第 %d 行 %s" % (row_number, name)
                )
            continue
        if raw in (None, ""):
            normalized[name] = None
            continue
        value = _finite_number(raw, "第 %d 行 %s" % (row_number, name))
        lower, upper = schema_obj.ranges.get(name, (None, None))
        if lower is not None and value < lower:
            raise TimingProfileValidationError(
                "第 %d 行 %s 不能小于 %s" % (row_number, name, lower)
            )
        if upper is not None and value > upper:
            raise TimingProfileValidationError(
                "第 %d 行 %s 不能大于 %s" % (row_number, name, upper)
            )
        # Pmpp/Umpp/FF must be strictly positive when supplied.
        if name in {"pmpp", "umpp", "ff"} and value <= 0:
            raise TimingProfileValidationError(
                "第 %d 行 %s 必须大于 0" % (row_number, name)
            )
        normalized[name] = value

    if normalized["enabled"]:
        for name in schema_obj.required:
            if normalized.get(name) is None:
                raise TimingProfileValidationError(
                    "第 %d 行缺少必填字段 %s" % (row_number, name)
                )
        for group in schema_obj.required_any:
            if not any(normalized.get(name) is not None for name in group):
                raise TimingProfileValidationError(
                    "第 %d 行至少需要填写一个字段: %s"
                    % (row_number, ", ".join(group))
                )
        # LVRT phase mask: enabled rows must select at least one of L1/L2/L3
        if {"l1", "l2", "l3"} <= set(schema_obj.bool_fields):
            if not any(bool(normalized.get(name)) for name in ("l1", "l2", "l3")):
                raise TimingProfileValidationError(
                    "第 %d 行请至少勾选 L1/L2/L3 中的一相" % row_number
                )

    extensions = _normalize_extensions(row.get("extensions"), row_number)
    if extensions:
        normalized["extensions"] = extensions
    return normalized


def validate_profile(
    rows: Iterable[Mapping[str, Any]],
    schema: SchemaLike,
    *,
    allow_empty: bool = False,
) -> List[Dict[str, Any]]:
    """Validate a sequence and return normalized, independent dictionaries."""

    if isinstance(rows, (str, bytes, Mapping)):
        raise TimingProfileValidationError("时序工况必须是行数组")
    normalized = [
        validate_profile_row(row, schema, row_number=index)
        for index, row in enumerate(rows, 1)
    ]
    if not normalized and not allow_empty:
        raise TimingProfileValidationError("时序工况不能为空")
    if normalized and not any(row["enabled"] for row in normalized) and not allow_empty:
        raise TimingProfileValidationError("至少启用一个时序工况")
    return normalized


@dataclass
class TimingProfile:
    """Validated profile envelope used by persistence and command adapters."""

    schema: str
    rows: List[Dict[str, Any]]
    extensions: Dict[str, Any] = field(default_factory=dict)
    version: int = PROFILE_VERSION

    @classmethod
    def create(
        cls,
        schema: SchemaLike,
        rows: Iterable[Mapping[str, Any]],
        *,
        extensions: Optional[Mapping[str, Any]] = None,
        allow_empty: bool = False,
    ) -> "TimingProfile":
        schema_obj = get_schema(schema)
        normalized = validate_profile(rows, schema_obj, allow_empty=allow_empty)
        envelope_extensions = _normalize_extensions(extensions, 0)
        return cls(
            schema=schema_obj.key,
            rows=normalized,
            extensions=envelope_extensions,
            version=PROFILE_VERSION,
        )

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "version": self.version,
            "schema": self.schema,
            "rows": self.rows,
        }
        if self.extensions:
            payload["extensions"] = self.extensions
        return payload


def serialize_profile(
    rows: Union[TimingProfile, Iterable[Mapping[str, Any]]],
    schema: Optional[SchemaLike] = None,
    *,
    extensions: Optional[Mapping[str, Any]] = None,
    allow_empty: bool = False,
) -> str:
    """Serialize a deterministic JSON envelope suitable for one CSV cell."""

    if isinstance(rows, TimingProfile):
        profile = TimingProfile.create(
            schema or rows.schema,
            rows.rows,
            extensions=extensions if extensions is not None else rows.extensions,
            allow_empty=allow_empty,
        )
    else:
        if schema is None:
            raise TimingProfileValidationError("序列化时必须指定 schema")
        profile = TimingProfile.create(
            schema,
            rows,
            extensions=extensions,
            allow_empty=allow_empty,
        )
    return json.dumps(
        profile.to_payload(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def deserialize_profile(
    value: Any,
    schema: Optional[SchemaLike] = None,
    *,
    allow_empty: bool = False,
) -> TimingProfile:
    """Parse current envelopes plus the legacy bare-list JSON form."""

    if isinstance(value, TimingProfile):
        expected = get_schema(schema or value.schema)
        return TimingProfile.create(
            expected,
            value.rows,
            extensions=value.extensions,
            allow_empty=allow_empty,
        )
    if isinstance(value, str):
        text = value.strip()
        if not text:
            if schema is None:
                raise TimingProfileValidationError("空时序工况缺少 schema")
            return TimingProfile.create(schema, [], allow_empty=True)
        try:
            parsed = json.loads(text)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise TimingProfileValidationError("时序工况 JSON 格式错误") from exc
    else:
        parsed = value

    if isinstance(parsed, Sequence) and not isinstance(parsed, (str, bytes)):
        if schema is None:
            raise TimingProfileValidationError("旧版工况数组必须由调用方指定 schema")
        return TimingProfile.create(schema, parsed, allow_empty=allow_empty)
    if not isinstance(parsed, Mapping):
        raise TimingProfileValidationError("时序工况 JSON 顶层必须是对象")

    allowed_envelope = {"version", "schema", "rows", "profile", "extensions"}
    unknown = set(str(key) for key in parsed) - allowed_envelope
    if unknown:
        raise TimingProfileValidationError(
            "时序工况顶层包含未知字段: %s；扩展字段请放入 extensions"
            % ", ".join(sorted(unknown))
        )
    version = parsed.get("version", PROFILE_VERSION)
    try:
        version_int = int(version)
    except (TypeError, ValueError) as exc:
        raise TimingProfileValidationError("时序工况 version 必须是整数") from exc
    if version_int < 1 or version_int > PROFILE_VERSION:
        raise TimingProfileValidationError(
            "不支持的时序工况版本 %s（当前支持 %s）"
            % (version_int, PROFILE_VERSION)
        )

    stored_schema = parsed.get("schema")
    expected_schema = get_schema(schema or stored_schema)
    if stored_schema and get_schema(stored_schema).key != expected_schema.key:
        raise TimingProfileValidationError(
            "时序 schema 不匹配: 文件为 %s，当前为 %s"
            % (stored_schema, expected_schema.key)
        )
    profile_rows = parsed.get("rows", parsed.get("profile"))
    if profile_rows is None:
        raise TimingProfileValidationError("时序工况 JSON 缺少 rows")
    profile = TimingProfile.create(
        expected_schema,
        profile_rows,
        extensions=parsed.get("extensions"),
        allow_empty=allow_empty,
    )
    profile.version = version_int
    return profile


def profile_to_json(
    rows: Union[TimingProfile, Iterable[Mapping[str, Any]]],
    schema: Optional[SchemaLike] = None,
    **kwargs: Any,
) -> str:
    return serialize_profile(rows, schema, **kwargs)


def profile_from_json(
    value: Any,
    schema: Optional[SchemaLike] = None,
    **kwargs: Any,
) -> List[Dict[str, Any]]:
    return deserialize_profile(value, schema, **kwargs).rows


dumps_profile = profile_to_json
loads_profile = profile_from_json


__all__ = [
    "COMMON_FIELDS",
    "DYNAMIC_MPPT_SCHEMA",
    "LVRT_SCHEMA",
    "PHASE_JUMP_SCHEMA",
    "PROFILE_VERSION",
    "SCHEMAS",
    "SUPPORTED_VALUE_FIELDS",
    "TIME_UNITS",
    "TIMING_PROFILE_JSON_COLUMN",
    "TimingProfile",
    "TimingProfileSchema",
    "TimingProfileValidationError",
    "default_profile_row",
    "deserialize_profile",
    "dumps_profile",
    "get_schema",
    "loads_profile",
    "normalize_time_unit",
    "profile_from_json",
    "profile_to_json",
    "serialize_profile",
    "time_to_seconds",
    "time_to_ticks",
    "validate_profile",
    "validate_profile_row",
]
