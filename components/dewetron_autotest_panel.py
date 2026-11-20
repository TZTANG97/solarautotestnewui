# -*- coding: utf-8 -*-
"""Reusable DEWETRON controls for AutoTest analyzer steps.

This module deliberately depends only on PyQt5 and the Python standard library.
It does not import a project dialog, a device controller, or ``SCPITestWave``.
That keeps the widgets reusable while the existing dialogs are migrated one at a
 time.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from xml.etree import ElementTree

from PyQt5 import QtCore, QtGui, QtWidgets


DEFAULT_RATE_OPTIONS: Tuple[str, ...] = (
    "Default",
    "1000",
    "500",
    "200",
    "100",
    "50",
    "20",
    "10",
    "5",
    "2",
    "1",
)
HARMONIC_RATE_OPTION = "SYNC to HARMONIC"


def _normalise_fields(fields: Optional[Iterable[Any]]) -> List[str]:
    """Return stripped, de-duplicated field names in their original order."""
    result: List[str] = []
    seen = set()
    for value in fields or ():
        field = str(value).strip()
        if field and field not in seen:
            seen.add(field)
            result.append(field)
    return result


def _coerce_lead_seconds(value: Any) -> float:
    """Seconds to start recording before the test action. Negative stays negative."""
    if isinstance(value, bool) or value in ("", None):
        return 0.0
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number != number or number in (float("inf"), float("-inf")):
        return 0.0
    return number


@dataclass(init=False)
class DewetronUiConfig:
    """Device-independent values exposed by :class:`DewetronAutoTestPanel`.

    The long field names match the existing DEWETRON dialog controls.  The
    shorter aliases ``rate``, ``precision`` and ``waveform`` are accepted by
    the constructor and are also available as properties.
    """

    rate_text: str
    decimal_places: int
    realtime_waveform: bool
    export_fields: List[str]
    save_dir: str
    export_abs_time: bool
    keep_oxygen_dmd: bool
    record_lead_s: float

    def __init__(
        self,
        rate_text: str = "Default",
        decimal_places: int = 3,
        realtime_waveform: bool = False,
        export_fields: Optional[Iterable[Any]] = None,
        save_dir: str = "",
        export_abs_time: bool = False,
        keep_oxygen_dmd: bool = False,
        record_lead_s: float = 0.0,
        **aliases: Any,
    ) -> None:
        if "rate" in aliases:
            rate_text = aliases.pop("rate")
        if "precision" in aliases:
            decimal_places = aliases.pop("precision")
        if "waveform" in aliases:
            realtime_waveform = aliases.pop("waveform")
        if "fields" in aliases:
            export_fields = aliases.pop("fields")
        if "save_path" in aliases:
            save_dir = aliases.pop("save_path")
        if "abs_time" in aliases:
            export_abs_time = aliases.pop("abs_time")
        if "keep_dmd" in aliases:
            keep_oxygen_dmd = aliases.pop("keep_dmd")
        if "record_lead" in aliases:
            record_lead_s = aliases.pop("record_lead")
        if "lead_s" in aliases:
            record_lead_s = aliases.pop("lead_s")
        if aliases:
            unknown = ", ".join(sorted(aliases))
            raise TypeError(f"Unknown DewetronUiConfig arguments: {unknown}")

        self.rate_text = str(rate_text).strip()
        self.decimal_places = int(decimal_places)
        self.realtime_waveform = bool(realtime_waveform)
        self.export_fields = _normalise_fields(export_fields)
        self.save_dir = str(save_dir or "").strip()
        self.export_abs_time = bool(export_abs_time)
        self.keep_oxygen_dmd = bool(keep_oxygen_dmd)
        self.record_lead_s = _coerce_lead_seconds(record_lead_s)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DewetronUiConfig):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    @property
    def rate(self) -> str:
        """Short alias for ``rate_text``."""
        return self.rate_text

    @rate.setter
    def rate(self, value: str) -> None:
        self.rate_text = str(value).strip()

    @property
    def precision(self) -> int:
        """Short alias for ``decimal_places``."""
        return self.decimal_places

    @precision.setter
    def precision(self, value: int) -> None:
        self.decimal_places = int(value)

    @property
    def waveform(self) -> bool:
        """Short alias for ``realtime_waveform``."""
        return self.realtime_waveform

    @waveform.setter
    def waveform(self, value: bool) -> None:
        self.realtime_waveform = bool(value)

    def copy(self) -> "DewetronUiConfig":
        """Return an independent normalized copy."""
        return DewetronUiConfig(**self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-safe mapping with stable key names."""
        return {
            "rate_text": self.rate_text,
            "decimal_places": self.decimal_places,
            "realtime_waveform": self.realtime_waveform,
            "export_fields": list(self.export_fields),
            "save_dir": self.save_dir,
            "export_abs_time": bool(self.export_abs_time),
            "keep_oxygen_dmd": bool(self.keep_oxygen_dmd),
            "record_lead_s": self.record_lead_s,
        }

    @classmethod
    def from_mapping(cls, values: Optional[Mapping[str, Any]]) -> "DewetronUiConfig":
        """Build a config from canonical or short mapping keys."""
        if values is None:
            return cls()
        if isinstance(values, DewetronUiConfig):
            return values.copy()
        data = dict(values)
        return cls(
            rate_text=data.get("rate_text", data.get("rate", "Default")),
            decimal_places=data.get("decimal_places", data.get("precision", 3)),
            realtime_waveform=data.get(
                "realtime_waveform", data.get("waveform", False)
            ),
            export_fields=data.get("export_fields", data.get("fields", ())),
            save_dir=data.get("save_dir", data.get("save_path", "")),
            export_abs_time=data.get(
                "export_abs_time", data.get("abs_time", False)
            ),
            keep_oxygen_dmd=data.get(
                "keep_oxygen_dmd", data.get("keep_dmd", False)
            ),
            record_lead_s=data.get(
                "record_lead_s", data.get("record_lead", data.get("lead_s", 0))
            ),
        )

    @classmethod
    def coerce(cls, value: Any) -> "DewetronUiConfig":
        """Coerce a config instance or mapping to ``DewetronUiConfig``."""
        if isinstance(value, cls):
            return value.copy()
        if isinstance(value, Mapping):
            return cls.from_mapping(value)
        raise TypeError("DEWETRON config must be DewetronUiConfig or a mapping")

    def validation_errors(self, require_export_fields: bool = True) -> List[str]:
        """Return validation messages without interacting with a device."""
        errors: List[str] = []
        rate = self.rate_text.strip()
        if not rate:
            errors.append("采集刷新率不能为空")
        elif rate.upper().replace(" ", "_") not in {
            "DEFAULT",
            "SYNC_TO_HARMONIC",
        }:
            match = re.fullmatch(r"(\d+)\s*(?:MS)?", rate, re.IGNORECASE)
            if not match or int(match.group(1)) <= 0:
                errors.append(f"无效的采集刷新率: {self.rate_text}")

        if isinstance(self.decimal_places, bool) or not isinstance(
            self.decimal_places, int
        ):
            errors.append("保留小数位数必须是整数")
        elif not 0 <= self.decimal_places <= 6:
            errors.append("保留小数位数必须在 0 到 6 之间")

        if self.record_lead_s < 0:
            errors.append("提前录制秒数不能为负数")

        if require_export_fields and not _normalise_fields(self.export_fields):
            errors.append("至少选择一个 DEWETRON 导出字段")
        return errors

    def validate(self, require_export_fields: bool = True) -> List[str]:
        """Compatibility alias for :meth:`validation_errors`."""
        return self.validation_errors(require_export_fields=require_export_fields)


PowerGroupTree = Dict[str, Dict[str, List[str]]]


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _find_power_group_fragment(xml_string: str) -> Optional[str]:
    """Extract a balanced ``Power Groups`` ChannelGroup XML fragment."""
    start_match = re.search(
        r"<ChannelGroup\b[^>]*\bType\s*=\s*(['\"])Power Groups\1[^>]*>",
        xml_string,
        re.IGNORECASE,
    )
    if not start_match:
        return None

    token_re = re.compile(r"</?ChannelGroup\b[^>]*>", re.IGNORECASE)
    depth = 0
    for token in token_re.finditer(xml_string, start_match.start()):
        text = token.group(0)
        if text.startswith("</"):
            depth -= 1
            if depth == 0:
                return xml_string[start_match.start() : token.end()]
        elif not text.rstrip().endswith("/>"):
            depth += 1
    return None


def _find_power_group_element(xml_string: str) -> Optional[ElementTree.Element]:
    """Parse a response that may include an SCPI prefix or trailing data."""
    if not xml_string:
        return None

    raw = str(xml_string).lstrip("﻿\x00\r\n ")
    first_xml = raw.find("<?xml")
    first_tag = raw.find("<")
    if first_xml >= 0:
        candidate = raw[first_xml:]
    elif first_tag >= 0:
        candidate = raw[first_tag:]
    else:
        return None

    try:
        root = ElementTree.fromstring(candidate)
    except ElementTree.ParseError:
        root = None

    if root is not None:
        for element in root.iter():
            if (
                _local_name(element.tag) == "ChannelGroup"
                and element.get("Type") == "Power Groups"
            ):
                return element

    fragment = _find_power_group_fragment(raw)
    if not fragment:
        return None
    try:
        return ElementTree.fromstring(fragment)
    except ElementTree.ParseError:
        return None


def _channel_name(channel: ElementTree.Element) -> str:
    """Read the export field name used by DEWETRON Power Groups."""
    name = (channel.get("Name") or "").strip()
    if name:
        return name

    # Some firmware exports ShortId only as a channel property.
    for element in channel.iter():
        if element.get("name") == "ShortId" or element.get("Name") == "ShortId":
            value = "".join(element.itertext()).strip().strip('"')
            if value:
                return value
    return ""


def _is_frequency_channel(name: str) -> bool:
    """True for Dewetron frequency channels (F_fund / f__fund / Freq …).

    Oxygen 导出名偶发双下划线 ``f__fund``；勿把 ``PF_fund`` 当成频率。
    """
    text = str(name or "").strip()
    if not text:
        return False
    # 去掉单位/后缀：F_fund [Hz] / F_fund@POWER/0
    base = text.split("@", 1)[0].split("[", 1)[0].strip()
    low = base.casefold().replace(" ", "")
    # 折叠连续下划线：f__fund → f_fund
    while "__" in low:
        low = low.replace("__", "_")
    if low in {"f_fund", "freq", "frequency", "f"}:
        return True
    if low.startswith("f_fund") or low.startswith("freq"):
        return True
    return False


_CATEGORY_ORDER = (
    "Voltage (U)",
    "Current (I)",
    "Active Power (P)",
    "Reactive Power (Q)",
    "Apparent Power (S)",
    "Power Factor (PF)",
    "Energy (W)",
    "Frequency (F)",
    "Capacity",
)
_SUBCATEGORY_ORDER = (
    "Total RMS",
    "Fundamental",
    "Total",
    "Average / PP",
    "Symmetrical Components",
    "_default_",
    "其他",
)


def _order_rank(name: str, order: Sequence[str]) -> tuple:
    text = str(name or "")
    try:
        return (order.index(text), text.casefold())
    except ValueError:
        return (len(order), text.casefold())


def _field_sort_key(name: str) -> tuple:
    """U_、U1、U2、U3、U12，同一相再按后缀排。避免 U12 插在 U1 和 U2 中间。"""
    text = str(name or "")
    match = re.match(r"^([A-Za-z]+)(\d*)(.*)$", text)
    if not match:
        return (text.casefold(), 0, "")
    letters, digits, rest = match.group(1), match.group(2), match.group(3)
    number = int(digits) if digits else -1
    return (letters.casefold(), number, rest.casefold())


def sort_power_group_tree(tree: Optional[PowerGroupTree]) -> Optional[PowerGroupTree]:
    """测量勾选树：类别、子类、通道都按固定顺序，不再沿用设备 XML 的乱序。"""
    if not tree:
        return tree
    ordered: PowerGroupTree = {}
    for category in sorted(tree, key=lambda name: _order_rank(name, _CATEGORY_ORDER)):
        subs = tree[category] or {}
        ordered[category] = {
            sub: sorted(list(subs[sub] or []), key=_field_sort_key)
            for sub in sorted(subs, key=lambda name: _order_rank(name, _SUBCATEGORY_ORDER))
        }
    return ordered


def parse_power_group_tree(xml_string: str) -> Optional[PowerGroupTree]:
    """Parse DEWETRON ``Power Groups`` XML into category/subcategory leaves.

    The returned structure is ``{category: {subcategory: [field, ...]}}``.
    ``Advanced`` groups are omitted except frequency channels (``F_fund`` 等)，
    避免频率被藏在 Advanced 里导致勾选树看不到。

    真机 XML 中 ``F_fund`` 常作为 ``POWER/0`` 的直接子 Channel（与 Voltage/Current
    分组同级），必须单独收集，否则测量项目树没有频率项。
    ``None`` means no valid Power Groups section was found.
    """
    root = _find_power_group_element(xml_string)
    if root is None:
        return None

    result: PowerGroupTree = {}
    freq_names: List[str] = []

    category_groups: List[ElementTree.Element] = []
    for child in list(root):
        if _local_name(child.tag) == "Channel":
            # POWER/0（或其它功率组）下：分组 + 直接挂着的频率通道
            for item in list(child):
                tag = _local_name(item.tag)
                if tag == "ChannelGroup":
                    category_groups.append(item)
                elif tag == "Channel":
                    name = _channel_name(item)
                    if name and _is_frequency_channel(name) and name not in freq_names:
                        freq_names.append(name)
        elif _local_name(child.tag) == "ChannelGroup":
            category_groups.append(child)

    def _collect_freq(node: ElementTree.Element) -> None:
        for channel in node.iter():
            if _local_name(channel.tag) != "Channel":
                continue
            name = _channel_name(channel)
            if name and _is_frequency_channel(name) and name not in freq_names:
                freq_names.append(name)

    for category in category_groups:
        category_name = (category.get("Type") or category.get("Name") or "").strip()
        if not category_name:
            continue
        if category_name == "Advanced":
            _collect_freq(category)
            continue
        subcategories = result.setdefault(category_name, {})

        for child in list(category):
            tag = _local_name(child.tag)
            if tag == "Channel":
                name = _channel_name(child)
                if name:
                    if _is_frequency_channel(name):
                        if name not in freq_names:
                            freq_names.append(name)
                    else:
                        subcategories.setdefault("_default_", []).append(name)
                continue
            if tag != "ChannelGroup":
                continue

            sub_name = (child.get("Type") or child.get("Name") or "").strip()
            if not sub_name:
                continue
            if sub_name == "Advanced":
                _collect_freq(child)
                continue
            names = [
                _channel_name(channel)
                for channel in list(child)
                if _local_name(channel.tag) == "Channel"
            ]
            names = _normalise_fields(names)
            # Advanced 外也可能夹着频率通道
            plain = []
            for name in names:
                if _is_frequency_channel(name):
                    if name not in freq_names:
                        freq_names.append(name)
                else:
                    plain.append(name)
            if plain:
                existing = subcategories.setdefault(sub_name, [])
                existing.extend(name for name in plain if name not in existing)

        if not subcategories:
            result.pop(category_name, None)

    if freq_names:
        freq_cat = result.setdefault("Frequency (F)", {})
        bucket = freq_cat.setdefault("Fundamental", [])
        for name in freq_names:
            if name not in bucket:
                bucket.append(name)

    return sort_power_group_tree(result) or None


# Descriptive alias for callers that do not need compatibility with the old
# dialog function name.
parse_power_groups_xml = parse_power_group_tree


class DewetronAutoTestPanel(QtWidgets.QWidget):
    """Generic DEWETRON rate/export configuration panel."""

    apply_requested = QtCore.pyqtSignal()
    refresh_requested = QtCore.pyqtSignal()
    viewer_requested = QtCore.pyqtSignal()
    apply_config_requested = QtCore.pyqtSignal(object)
    config_changed = QtCore.pyqtSignal(object)
    unavailable_fields_changed = QtCore.pyqtSignal(object)

    FIELD_ROLE = QtCore.Qt.UserRole + 1

    def __init__(
        self,
        config: Optional[DewetronUiConfig] = None,
        parent: Optional[QtWidgets.QWidget] = None,
        rate_options: Optional[Sequence[str]] = None,
        default_rate: Optional[str] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("dewetronAutoTestPanel")
        self._building_tree = False
        self._desired_export_fields: Optional[List[str]] = None
        self._unavailable_export_fields: List[str] = []
        self._preset_name = "default"
        self._rate_options = list(rate_options or DEFAULT_RATE_OPTIONS)
        if HARMONIC_RATE_OPTION in self._rate_options:
            pass
        elif default_rate == HARMONIC_RATE_OPTION:
            self._rate_options.append(HARMONIC_RATE_OPTION)

        initial = config.copy() if isinstance(config, DewetronUiConfig) else config
        has_explicit_config = initial is not None
        if initial is None:
            initial = DewetronUiConfig(rate_text=default_rate or "Default")
        else:
            initial = DewetronUiConfig.coerce(initial)
            if default_rate and not initial.rate_text:
                initial.rate_text = default_rate

        self._build_ui()
        self.set_config(initial)
        if not has_explicit_config:
            # 无显式配置：尝试加载上次保存的勾选；没有则全部不勾选
            self._desired_export_fields = []
            self._try_load_export_preset(apply_rate=True)
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        settings_group = QtWidgets.QGroupBox("DEWETRON 采集与导出设置")
        settings_group.setObjectName("groupBox_DEW_AutoTest")
        group_layout = QtWidgets.QVBoxLayout(settings_group)

        form = QtWidgets.QFormLayout()
        form.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        self.comboBox_DEW_MaxRefreshRate = QtWidgets.QComboBox()
        self.comboBox_DEW_MaxRefreshRate.setObjectName(
            "comboBox_DEW_MaxRefreshRate"
        )
        self.comboBox_DEW_MaxRefreshRate.setEditable(True)
        self.comboBox_DEW_MaxRefreshRate.addItems(self._rate_options)
        self.comboBox_DEW_MaxRefreshRate.setToolTip(
            "最大刷新率（ms）。10min 过压等长试验可选 200/500/1000；也可直接输入数值。"
        )
        form.addRow("最大刷新率 (ms):", self.comboBox_DEW_MaxRefreshRate)

        self.spinBox_DEW_DecimalPlaces = QtWidgets.QSpinBox()
        self.spinBox_DEW_DecimalPlaces.setObjectName(
            "spinBox_DEW_DecimalPlaces"
        )
        self.spinBox_DEW_DecimalPlaces.setRange(0, 6)
        form.addRow("保留小数位数:", self.spinBox_DEW_DecimalPlaces)

        self.spinBox_DEW_RecordLead = QtWidgets.QSpinBox()
        self.spinBox_DEW_RecordLead.setObjectName("spinBox_DEW_RecordLead")
        self.spinBox_DEW_RecordLead.setRange(0, 3600)
        self.spinBox_DEW_RecordLead.setSuffix(" 秒")
        self.spinBox_DEW_RecordLead.setToolTip(
            "开录比试验动作提前的秒数，用来录下逆变器已经并网的一段时间。"
            "不能大于本试验的启机时间，超出时按启机时间提前，不会早于启机开始。"
            "也可在设备管理→德威创页统一设置。"
        )
        try:
            from utils.dewetron_channel_scale import load_saved_record_lead_s

            self.spinBox_DEW_RecordLead.setValue(
                int(round(load_saved_record_lead_s()))
            )
        except Exception:
            self.spinBox_DEW_RecordLead.setValue(0)
        form.addRow("提前录制:", self.spinBox_DEW_RecordLead)

        self.checkBox_DEW_RealtimeWaveform = QtWidgets.QCheckBox(
            "启用实时波形显示"
        )
        self.checkBox_DEW_RealtimeWaveform.setObjectName(
            "checkBox_DEW_RealtimeWaveform"
        )
        form.addRow("实时波形:", self.checkBox_DEW_RealtimeWaveform)

        self.checkBox_DEW_ExportAbsTime = QtWidgets.QCheckBox(
            "CSV 增加绝对时间戳列（设备 ABS-TIME）"
        )
        self.checkBox_DEW_ExportAbsTime.setObjectName("checkBox_DEW_ExportAbsTime")
        self.checkBox_DEW_ExportAbsTime.setToolTip(
            "导出时在 Time [s] 前增加 Abs Time 列，来自 Oxygen NUMERIC 的 ABS-TIME。"
        )
        form.addRow("绝对时间:", self.checkBox_DEW_ExportAbsTime)

        self.checkBox_DEW_KeepOxygenDmd = QtWidgets.QCheckBox(
            "保留 Oxygen 原始 .dmd 录波到保存目录"
        )
        self.checkBox_DEW_KeepOxygenDmd.setObjectName("checkBox_DEW_KeepOxygenDmd")
        self.checkBox_DEW_KeepOxygenDmd.setToolTip(
            "试验过程中启动 :STORE 录波；结束后把 .dmd 复制/保留到与 CSV 相同的保存目录，"
            "可用 Oxygen 打开原始波形。"
        )
        form.addRow("原始录波:", self.checkBox_DEW_KeepOxygenDmd)

        path_row = QtWidgets.QHBoxLayout()
        self.lineEdit_DEW_SaveDir = QtWidgets.QLineEdit()
        self.lineEdit_DEW_SaveDir.setObjectName("lineEdit_DEW_SaveDir")
        try:
            from utils.wt_save_path import ensure_dewetron_save_dir

            self.lineEdit_DEW_SaveDir.setText(ensure_dewetron_save_dir())
        except Exception:
            self.lineEdit_DEW_SaveDir.setText("")
        self.lineEdit_DEW_SaveDir.setPlaceholderText(
            r"%LOCALAPPDATA%\SolarAutoTest\dewetron_save"
        )
        self.lineEdit_DEW_SaveDir.setToolTip(
            "德威创 CSV / 可选 .dmd 录波保存目录。目录不存在会自动创建。"
        )
        path_row.addWidget(self.lineEdit_DEW_SaveDir, 1)
        self.pushButton_DEW_BrowseSaveDir = QtWidgets.QPushButton("浏览…")
        self.pushButton_DEW_BrowseSaveDir.setObjectName("pushButton_DEW_BrowseSaveDir")
        self.pushButton_DEW_BrowseSaveDir.clicked.connect(self._browse_save_dir)
        path_row.addWidget(self.pushButton_DEW_BrowseSaveDir)
        form.addRow("保存路径:", path_row)
        group_layout.addLayout(form)

        # Action buttons sit above the tree so they stay visible even when the
        # export list is tall / the dialog clips the bottom. AnalyzerModeSection
        # may reparent them into the mode row next to the DEWETRON radio.
        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch()
        self.pushButton_DEW_DataViewer = QtWidgets.QPushButton("数据查看")
        self.pushButton_DEW_DataViewer.setObjectName("pushButton_DEW_DataViewer")
        buttons.addWidget(self.pushButton_DEW_DataViewer)
        self.pushButton_DEW_TestApply = QtWidgets.QPushButton("测试生效")
        self.pushButton_DEW_TestApply.setObjectName("pushButton_DEW_TestApply")
        self.pushButton_DEW_TestApply.setStyleSheet(
            "QPushButton { background-color: #8b5cf6; color: white; border: none; "
            "border-radius: 4px; padding: 6px 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #7c3aed; }"
        )
        buttons.addWidget(self.pushButton_DEW_TestApply)
        group_layout.addLayout(buttons)

        tree_header = QtWidgets.QHBoxLayout()
        tree_header.addWidget(QtWidgets.QLabel("导出字段选择"))
        tree_header.addStretch()
        self.comboBox_DEW_Presets = QtWidgets.QComboBox()
        self.comboBox_DEW_Presets.setObjectName("comboBox_DEW_Presets")
        self.comboBox_DEW_Presets.setMinimumWidth(120)
        self.comboBox_DEW_Presets.setToolTip(
            "本机已保存的测量勾选配置；选中后点「加载勾选」应用"
        )
        tree_header.addWidget(self.comboBox_DEW_Presets)
        self.pushButton_DEW_SaveFields = QtWidgets.QPushButton("保存勾选")
        self.pushButton_DEW_SaveFields.setObjectName("pushButton_DEW_SaveFields")
        self.pushButton_DEW_SaveFields.setToolTip(
            "把当前勾选保存到当前配置名（下次打开该试验自动加载）"
        )
        tree_header.addWidget(self.pushButton_DEW_SaveFields)
        self.pushButton_DEW_SaveFieldsAs = QtWidgets.QPushButton("另存为…")
        self.pushButton_DEW_SaveFieldsAs.setObjectName("pushButton_DEW_SaveFieldsAs")
        self.pushButton_DEW_SaveFieldsAs.setToolTip(
            "另存为一套命名配置，之后可从下拉框选用"
        )
        tree_header.addWidget(self.pushButton_DEW_SaveFieldsAs)
        self.pushButton_DEW_LoadFields = QtWidgets.QPushButton("加载勾选")
        self.pushButton_DEW_LoadFields.setObjectName("pushButton_DEW_LoadFields")
        self.pushButton_DEW_LoadFields.setToolTip("加载下拉框选中的配置到勾选树")
        tree_header.addWidget(self.pushButton_DEW_LoadFields)
        self.pushButton_DEW_RefreshFields = QtWidgets.QPushButton("刷新字段")
        self.pushButton_DEW_RefreshFields.setObjectName(
            "pushButton_DEW_RefreshFields"
        )
        tree_header.addWidget(self.pushButton_DEW_RefreshFields)
        group_layout.addLayout(tree_header)

        self.treeWidget_DEW_ExportFields = QtWidgets.QTreeWidget()
        self.treeWidget_DEW_ExportFields.setObjectName(
            "treeWidget_DEW_ExportFields"
        )
        self.treeWidget_DEW_ExportFields.setHeaderHidden(True)
        self.treeWidget_DEW_ExportFields.setRootIsDecorated(True)
        self.treeWidget_DEW_ExportFields.setAlternatingRowColors(True)
        self.treeWidget_DEW_ExportFields.setMinimumHeight(160)
        group_layout.addWidget(self.treeWidget_DEW_ExportFields, 1)

        layout.addWidget(settings_group, 1)
        self._build_export_field_tree(None)

        # Short, generic aliases make future dialog integrations less coupled
        # to the historic object names.
        self.rate_combo = self.comboBox_DEW_MaxRefreshRate
        self.precision_spin = self.spinBox_DEW_DecimalPlaces
        self.waveform_checkbox = self.checkBox_DEW_RealtimeWaveform
        self.export_tree = self.treeWidget_DEW_ExportFields
        self.apply_button = self.pushButton_DEW_TestApply
        self.refresh_button = self.pushButton_DEW_RefreshFields
        self.viewer_button = self.pushButton_DEW_DataViewer
        self.save_dir_edit = self.lineEdit_DEW_SaveDir

    def _browse_save_dir(self) -> None:
        start = (self.lineEdit_DEW_SaveDir.text() or "").strip()
        chosen = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择德威创保存目录", start or ""
        )
        if not chosen:
            return
        try:
            from utils.wt_save_path import ensure_dewetron_save_dir

            chosen = ensure_dewetron_save_dir(chosen)
        except Exception:
            pass
        self.lineEdit_DEW_SaveDir.setText(chosen)
        self._emit_config_changed()

    def _connect_signals(self) -> None:
        self.pushButton_DEW_TestApply.clicked.connect(self._request_apply)
        self.pushButton_DEW_RefreshFields.clicked.connect(
            self.refresh_requested.emit
        )
        self.pushButton_DEW_SaveFields.clicked.connect(self.save_export_preset)
        self.pushButton_DEW_SaveFieldsAs.clicked.connect(self.save_export_preset_as)
        self.pushButton_DEW_LoadFields.clicked.connect(self._load_selected_preset)
        self._reload_preset_combo()
        self.pushButton_DEW_DataViewer.clicked.connect(self.viewer_requested.emit)
        self.comboBox_DEW_MaxRefreshRate.currentTextChanged.connect(
            self._emit_config_changed
        )
        self.spinBox_DEW_DecimalPlaces.valueChanged.connect(
            self._emit_config_changed
        )
        self.spinBox_DEW_RecordLead.valueChanged.connect(self._emit_config_changed)
        self.checkBox_DEW_RealtimeWaveform.toggled.connect(
            self._emit_config_changed
        )
        self.checkBox_DEW_ExportAbsTime.toggled.connect(self._emit_config_changed)
        self.checkBox_DEW_KeepOxygenDmd.toggled.connect(self._emit_config_changed)
        self.lineEdit_DEW_SaveDir.textChanged.connect(self._emit_config_changed)
        self.treeWidget_DEW_ExportFields.itemChanged.connect(
            self._on_tree_item_changed
        )

    def _request_apply(self) -> None:
        config = self.get_config()
        # 测试生效时顺便记住勾选，下次默认带上
        try:
            self.save_export_preset(silent=True)
        except Exception:
            pass
        self.apply_requested.emit()
        self.apply_config_requested.emit(config)

    def set_preset_name(self, name: str) -> None:
        """Bind Dewetron export preset to a test project (isolates勾选 across trials)."""
        self._preset_name = (str(name or "").strip() or "default")
        self._reload_preset_combo(select=self._preset_name)

    def preset_name(self) -> str:
        return getattr(self, "_preset_name", None) or "default"

    def _reload_preset_combo(self, select: Optional[str] = None) -> None:
        combo = getattr(self, "comboBox_DEW_Presets", None)
        if combo is None:
            return
        from utils.dewetron_export_preset import list_export_presets

        want = (select or self.preset_name() or "default").strip() or "default"
        names = list_export_presets()
        if want not in names:
            names = [want] + [n for n in names if n != want]
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(names)
        idx = combo.findText(want)
        combo.setCurrentIndex(idx if idx >= 0 else 0)
        combo.blockSignals(False)

    def _selected_preset_name(self) -> str:
        combo = getattr(self, "comboBox_DEW_Presets", None)
        if combo is not None and combo.currentText().strip():
            return combo.currentText().strip()
        return self.preset_name()

    def _load_selected_preset(self) -> None:
        name = self._selected_preset_name()
        self.set_preset_name(name)
        self.load_export_preset(show_message=True)

    def save_export_preset_as(self) -> None:
        """弹窗输入配置名后另存。"""
        name, ok = QtWidgets.QInputDialog.getText(
            self,
            "另存测量勾选配置",
            "配置名称（本机保存，可在下拉框选用）：",
            text=self._selected_preset_name() or "my_fields",
        )
        if not ok:
            return
        name = (name or "").strip()
        if not name:
            QtWidgets.QMessageBox.warning(self, "无效名称", "请输入配置名称。")
            return
        self.set_preset_name(name)
        self.save_export_preset(silent=False)
        self._reload_preset_combo(select=name)

    def save_export_preset(self, silent: bool = False) -> str:
        """保存当前勾选为该试验的配置。"""
        from utils.dewetron_export_preset import save_export_preset

        # 若下拉框有选中名，优先用它（便于覆盖某套命名配置）
        if not silent:
            picked = self._selected_preset_name()
            if picked:
                self._preset_name = picked

        cfg = self.get_config()
        path = save_export_preset(
            export_fields=cfg.export_fields,
            rate_text=cfg.rate_text,
            decimal_places=cfg.decimal_places,
            realtime_waveform=cfg.realtime_waveform,
            preset_name=self.preset_name(),
        )
        self._desired_export_fields = list(cfg.export_fields)
        # Also mirror into per-test UI preset bundle when name is a real trial
        try:
            from utils.test_ui_preset import save_test_preset

            if self.preset_name() != "default":
                save_test_preset(
                    self.preset_name(),
                    dew_export={
                        "export_fields": list(cfg.export_fields),
                        "rate_text": str(cfg.rate_text or "Default"),
                        "decimal_places": int(cfg.decimal_places or 4),
                        "realtime_waveform": bool(cfg.realtime_waveform),
                    },
                )
        except Exception:
            pass
        self._reload_preset_combo(select=self.preset_name())
        if not silent:
            QtWidgets.QMessageBox.information(
                self,
                "已保存",
                f"勾选配置已保存为「{self.preset_name()}」，下次可从下拉框选用。\n{path}",
            )
        return path

    def load_export_preset(self, show_message: bool = False) -> bool:
        """加载该试验的勾选配置到树。"""
        ok = self._try_load_export_preset(apply_rate=True)
        if show_message:
            if ok:
                QtWidgets.QMessageBox.information(
                    self, "已加载", f"已加载「{self.preset_name()}」的勾选配置。"
                )
            else:
                QtWidgets.QMessageBox.information(
                    self,
                    "无配置",
                    "还没有这套勾选配置，请先勾选后点「保存勾选」或「另存为…」。",
                )
        return ok

    def _try_load_export_preset(self, *, apply_rate: bool = False) -> bool:
        from utils.dewetron_export_preset import load_export_preset

        data = load_export_preset(self.preset_name())
        # Fallback: legacy shared default once, then caller should re-save per test
        if not data and self.preset_name() != "default":
            data = load_export_preset("default")
        if not data:
            return False
        fields = list(data.get("export_fields") or [])
        self._desired_export_fields = fields
        if apply_rate:
            rate = str(data.get("rate_text") or "").strip()
            if rate:
                idx = self.comboBox_DEW_MaxRefreshRate.findText(rate)
                if idx >= 0:
                    self.comboBox_DEW_MaxRefreshRate.setCurrentIndex(idx)
                else:
                    self.comboBox_DEW_MaxRefreshRate.setEditText(rate)
            try:
                self.spinBox_DEW_DecimalPlaces.setValue(
                    int(data.get("decimal_places") or 4)
                )
            except (TypeError, ValueError):
                pass
            self.checkBox_DEW_RealtimeWaveform.setChecked(
                bool(data.get("realtime_waveform"))
            )
        # 若字段树已有数据，立刻重刷勾选
        tree_data = self._current_tree_data()
        if tree_data:
            self._build_export_field_tree(tree_data, fields)
        return True

    def _current_tree_data(self) -> Optional[PowerGroupTree]:
        """从当前树反推 category 结构（仅用于重刷勾选）。"""
        tree = self.treeWidget_DEW_ExportFields
        result: PowerGroupTree = {}
        for i in range(tree.topLevelItemCount()):
            cat_item = tree.topLevelItem(i)
            cat_name = cat_item.text(0)
            subs = result.setdefault(cat_name, {})
            for j in range(cat_item.childCount()):
                sub_item = cat_item.child(j)
                sub_name = sub_item.text(0)
                if sub_name == "其他":
                    sub_name = "_default_"
                names = []
                for k in range(sub_item.childCount()):
                    leaf = sub_item.child(k)
                    field = leaf.data(0, self.FIELD_ROLE)
                    if field:
                        names.append(str(field))
                if names:
                    subs[sub_name] = names
        return result or None

    def _emit_config_changed(self, *_args: Any) -> None:
        if not self._building_tree:
            self.config_changed.emit(self.get_config())

    def _placeholder(self, text: str) -> None:
        item = QtWidgets.QTreeWidgetItem(
            self.treeWidget_DEW_ExportFields, [text]
        )
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
        item.setForeground(0, QtGui.QColor("#64748b"))

    def _build_export_field_tree(
        self,
        tree_data: Optional[PowerGroupTree],
        checked_fields: Optional[Iterable[str]] = None,
    ) -> None:
        tree = self.treeWidget_DEW_ExportFields
        self._building_tree = True
        tree.blockSignals(True)
        try:
            tree.clear()
            if not tree_data:
                self._placeholder("请连接 DEWETRON 后刷新电力组字段")
                return

            desired = (
                _normalise_fields(checked_fields)
                if checked_fields is not None
                else self._desired_export_fields
            )
            desired_set = set(desired) if desired is not None else None
            tree_data = sort_power_group_tree(tree_data) or {}

            for category, subcategories in tree_data.items():
                category_item = QtWidgets.QTreeWidgetItem(tree, [str(category)])
                category_item.setFlags(
                    category_item.flags()
                    | QtCore.Qt.ItemIsUserCheckable
                    | QtCore.Qt.ItemIsAutoTristate
                )
                category_item.setForeground(0, QtGui.QColor("#5b21b6"))
                category_font = category_item.font(0)
                category_font.setBold(True)
                category_item.setFont(0, category_font)

                for subcategory, fields in subcategories.items():
                    label = "其他" if subcategory == "_default_" else str(subcategory)
                    sub_item = QtWidgets.QTreeWidgetItem(category_item, [label])
                    sub_item.setFlags(
                        sub_item.flags()
                        | QtCore.Qt.ItemIsUserCheckable
                        | QtCore.Qt.ItemIsAutoTristate
                    )
                    for field in _normalise_fields(fields):
                        display = (
                            f"{field}（频率）"
                            if _is_frequency_channel(field)
                            else field
                        )
                        leaf = QtWidgets.QTreeWidgetItem(sub_item, [display])
                        leaf.setData(0, self.FIELD_ROLE, field)
                        leaf.setFlags(leaf.flags() | QtCore.Qt.ItemIsUserCheckable)
                        # None/空：默认不勾选；有列表：只勾选列表内
                        checked = bool(desired_set) and field in desired_set
                        leaf.setCheckState(
                            0, QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked
                        )
                    self._refresh_parent_state(sub_item)
                self._refresh_parent_state(category_item)
            tree.expandToDepth(1)
            selected = self.get_checked_export_fields()
            available = set(self.available_export_fields())
            self._unavailable_export_fields = (
                [field for field in desired if field not in available]
                if desired is not None
                else []
            )
            # Keep explicitly requested but temporarily unavailable fields
            # pending, so a later device refresh can restore them.
            self._desired_export_fields = (
                list(desired) if desired is not None else selected
            )
        finally:
            tree.blockSignals(False)
            self._building_tree = False

    @staticmethod
    def _refresh_parent_state(item: QtWidgets.QTreeWidgetItem) -> None:
        if item.childCount() == 0:
            return
        states = [item.child(index).checkState(0) for index in range(item.childCount())]
        if all(state == QtCore.Qt.Checked for state in states):
            state = QtCore.Qt.Checked
        elif all(state == QtCore.Qt.Unchecked for state in states):
            state = QtCore.Qt.Unchecked
        else:
            state = QtCore.Qt.PartiallyChecked
        item.setCheckState(0, state)

    def _on_tree_item_changed(
        self, _item: QtWidgets.QTreeWidgetItem, _column: int
    ) -> None:
        if self._building_tree:
            return
        self._desired_export_fields = self.get_checked_export_fields()
        self._emit_config_changed()

    def refresh_power_groups(
        self,
        xml_string: str,
        checked_fields: Optional[Iterable[str]] = None,
    ) -> Optional[PowerGroupTree]:
        """Parse device XML and rebuild the field tree.

        When ``set_config`` or ``set_checked_export_fields`` ran before XML was
        available, its selection is kept in ``_desired_export_fields`` and is
        restored here automatically.
        """
        tree_data = parse_power_group_tree(xml_string)
        self._build_export_field_tree(tree_data, checked_fields)
        self.unavailable_fields_changed.emit(self.unavailable_export_fields())
        return tree_data

    def refresh_export_field_tree(
        self,
        xml_string: str,
        checked_fields: Optional[Iterable[str]] = None,
    ) -> Optional[PowerGroupTree]:
        """Compatibility alias used by the existing project dialogs."""
        return self.refresh_power_groups(xml_string, checked_fields)

    def unavailable_export_fields(self) -> List[str]:
        """Return restored field names absent from the latest device XML."""
        return list(self._unavailable_export_fields)

    def available_export_fields(self) -> List[str]:
        """Return all leaf field names currently shown in the tree."""
        fields: List[str] = []
        iterator = QtWidgets.QTreeWidgetItemIterator(
            self.treeWidget_DEW_ExportFields
        )
        while iterator.value():
            item = iterator.value()
            field = item.data(0, self.FIELD_ROLE)
            if field:
                fields.append(str(field))
            iterator += 1
        return fields

    def get_checked_export_fields(self) -> List[str]:
        """Return checked leaf names, or pending names before XML is loaded."""
        checked: List[str] = []
        iterator = QtWidgets.QTreeWidgetItemIterator(
            self.treeWidget_DEW_ExportFields
        )
        while iterator.value():
            item = iterator.value()
            field = item.data(0, self.FIELD_ROLE)
            if field and item.checkState(0) == QtCore.Qt.Checked:
                checked.append(str(field))
            iterator += 1
        if not self.available_export_fields() and self._desired_export_fields is not None:
            return list(self._desired_export_fields)
        return checked

    def set_checked_export_fields(self, fields: Iterable[str]) -> None:
        """Select named leaves now, or remember them until XML is refreshed."""
        desired = _normalise_fields(fields)
        self._desired_export_fields = desired
        if not self.available_export_fields():
            return

        desired_set = set(desired)
        self._building_tree = True
        tree = self.treeWidget_DEW_ExportFields
        tree.blockSignals(True)
        try:
            iterator = QtWidgets.QTreeWidgetItemIterator(tree)
            parents: List[QtWidgets.QTreeWidgetItem] = []
            while iterator.value():
                item = iterator.value()
                field = item.data(0, self.FIELD_ROLE)
                if field:
                    item.setCheckState(
                        0,
                        QtCore.Qt.Checked
                        if str(field) in desired_set
                        else QtCore.Qt.Unchecked,
                    )
                elif item.childCount():
                    parents.append(item)
                iterator += 1
            for parent in reversed(parents):
                self._refresh_parent_state(parent)
        finally:
            tree.blockSignals(False)
            self._building_tree = False
        self.config_changed.emit(self.get_config())

    def get_config(self) -> DewetronUiConfig:
        """Snapshot the current controls into a value object."""
        return DewetronUiConfig(
            rate_text=self.comboBox_DEW_MaxRefreshRate.currentText(),
            decimal_places=self.spinBox_DEW_DecimalPlaces.value(),
            realtime_waveform=self.checkBox_DEW_RealtimeWaveform.isChecked(),
            export_fields=self.get_checked_export_fields(),
            save_dir=(self.lineEdit_DEW_SaveDir.text() or "").strip(),
            export_abs_time=self.checkBox_DEW_ExportAbsTime.isChecked(),
            keep_oxygen_dmd=self.checkBox_DEW_KeepOxygenDmd.isChecked(),
            record_lead_s=self.spinBox_DEW_RecordLead.value(),
        )

    # Common short aliases used by coordinator and persistence helpers.
    config = get_config
    snapshot_config = get_config

    def set_config(self, config: Any) -> None:
        """Restore controls without requiring the field tree to exist yet."""
        value = DewetronUiConfig.coerce(config)
        rate = value.rate_text
        if self.comboBox_DEW_MaxRefreshRate.findText(rate) < 0:
            self.comboBox_DEW_MaxRefreshRate.addItem(rate)
        self.comboBox_DEW_MaxRefreshRate.setCurrentText(rate)
        self.spinBox_DEW_DecimalPlaces.setValue(value.decimal_places)
        self.spinBox_DEW_RecordLead.setValue(
            max(0, min(3600, int(round(value.record_lead_s))))
        )
        self.checkBox_DEW_RealtimeWaveform.setChecked(value.realtime_waveform)
        self.checkBox_DEW_ExportAbsTime.setChecked(bool(value.export_abs_time))
        self.checkBox_DEW_KeepOxygenDmd.setChecked(bool(value.keep_oxygen_dmd))
        if value.save_dir:
            try:
                from utils.wt_save_path import ensure_dewetron_save_dir

                self.lineEdit_DEW_SaveDir.setText(
                    ensure_dewetron_save_dir(value.save_dir)
                )
            except Exception:
                self.lineEdit_DEW_SaveDir.setText(value.save_dir)
        self.set_checked_export_fields(value.export_fields)

    restore_config = set_config

    def validate_config(self, require_export_fields: bool = True) -> List[str]:
        """Validate the current controls and return all messages."""
        return self.get_config().validation_errors(require_export_fields)


# Concise compatibility alias for integrations that use a generic panel name.
DewetronPanel = DewetronAutoTestPanel


class AnalyzerModeSection(QtWidgets.QWidget):
    """Wrap an existing analyzer UI with a WT/DEWETRON mode selector.

    ``primary_wt_widget`` and ``step_checkbox`` are existing widgets owned by a
    project dialog.  Qt removes them from their old layouts when they are added
    here.  The step checkbox is deliberately placed outside the stacked pages,
    so it remains visible in both analyzer modes.
    """

    mode_changed = QtCore.pyqtSignal(str)
    apply_requested = QtCore.pyqtSignal()
    refresh_requested = QtCore.pyqtSignal()
    viewer_requested = QtCore.pyqtSignal()

    WT_MODE = "wt3000"
    DEWETRON_MODE = "dewetron"

    def __init__(
        self,
        primary_wt_widget: QtWidgets.QWidget,
        step_checkbox: QtWidgets.QAbstractButton,
        dewetron_panel: Optional[DewetronAutoTestPanel] = None,
        parent: Optional[QtWidgets.QWidget] = None,
        wt_label: str = "功率分析仪 (WT)",
        dewetron_label: str = "DEWETRON",
    ) -> None:
        if not isinstance(primary_wt_widget, QtWidgets.QWidget):
            raise TypeError("primary_wt_widget must be a QWidget")
        if not isinstance(step_checkbox, QtWidgets.QAbstractButton):
            raise TypeError("step_checkbox must be a QAbstractButton")
        super().__init__(parent)
        self.setObjectName("analyzerModeSection")
        self.primary_wt_widget = primary_wt_widget
        self.step_checkbox = step_checkbox
        self.dewetron_panel = dewetron_panel or DewetronAutoTestPanel()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.mode_row = QtWidgets.QWidget()
        self.mode_row.setObjectName("analyzerModeRow")
        mode_layout = QtWidgets.QHBoxLayout(self.mode_row)
        mode_layout.setContentsMargins(4, 4, 4, 4)
        mode_layout.setSpacing(12)

        # addWidget reparents and removes the checkbox from its previous layout.
        step_checkbox.show()
        mode_layout.addWidget(step_checkbox)
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        mode_layout.addWidget(separator)

        self.radio_wt = QtWidgets.QRadioButton(wt_label)
        self.radio_wt.setObjectName("radio_wt")
        self.radio_dewetron = QtWidgets.QRadioButton(dewetron_label)
        self.radio_dewetron.setObjectName("radio_dewetron")
        self._mode_group = QtWidgets.QButtonGroup(self)
        self._mode_group.setExclusive(True)
        self._mode_group.addButton(self.radio_wt, 0)
        self._mode_group.addButton(self.radio_dewetron, 1)
        mode_layout.addWidget(self.radio_wt)
        mode_layout.addWidget(self.radio_dewetron)
        mode_layout.addStretch()
        # Keep Apply/Viewer on the mode row so they are never clipped under the
        # export-field tree (common on the ②功率分析仪 step).
        mode_layout.addWidget(self.dewetron_panel.pushButton_DEW_DataViewer)
        mode_layout.addWidget(self.dewetron_panel.pushButton_DEW_TestApply)
        layout.addWidget(self.mode_row)

        # Shared continuous/split selector — visible for WT and DEWETRON alike.
        from components.wt_recording_mode_row import WtRecordingModeRow

        self.recordingModeRow = WtRecordingModeRow(self)
        self.recordingModeRow.setObjectName("analyzerRecordingModeRow")
        # Distinct objectName so WT page combos stay unique; get_record_mode
        # prefers this shared combo when present.
        self.recordingModeRow.comboBox_recording_mode.setObjectName(
            "comboBox_analyzer_recording_mode"
        )
        self.comboBox_analyzer_recording_mode = (
            self.recordingModeRow.comboBox_recording_mode
        )
        self.recordingModeRow.mode_changed.connect(self._on_shared_record_mode)
        self.recordingModeRow.pushButton_fill_recommended_names.setVisible(False)
        layout.addWidget(self.recordingModeRow)

        self.analyzer_stack = QtWidgets.QStackedWidget()
        self.analyzer_stack.setObjectName("analyzerModeStack")
        self.analyzer_stack.addWidget(primary_wt_widget)
        self.analyzer_stack.addWidget(self.dewetron_panel)
        layout.addWidget(self.analyzer_stack, 1)

        # Compatibility names used by the already-integrated dialogs.
        self.radio_wt3000 = self.radio_wt
        self._step2Stacked = self.analyzer_stack
        self._analyzerStacked = self.analyzer_stack

        self._mode = self.WT_MODE
        self.radio_wt.setChecked(True)
        self._mode_group.buttonToggled.connect(self._on_mode_toggled)
        self.step_checkbox.toggled.connect(self._sync_step_enabled)
        self.dewetron_panel.apply_requested.connect(self.apply_requested.emit)
        self.dewetron_panel.refresh_requested.connect(self.refresh_requested.emit)
        self.dewetron_panel.viewer_requested.connect(self.viewer_requested.emit)
        self._sync_dew_action_visibility(False)
        self._sync_step_enabled(self.step_checkbox.isChecked())
        QtCore.QTimer.singleShot(0, self._sync_record_mode_from_wt_pages)

    def _on_mode_toggled(
        self, button: QtWidgets.QAbstractButton, checked: bool
    ) -> None:
        if not checked:
            return
        if button is self.radio_dewetron:
            self._mode = self.DEWETRON_MODE
            self.analyzer_stack.setCurrentIndex(1)
            self._sync_dew_action_visibility(True)
        else:
            self._mode = self.WT_MODE
            self.analyzer_stack.setCurrentIndex(0)
            self._sync_dew_action_visibility(False)
        self.mode_changed.emit(self._mode)

    def _sync_dew_action_visibility(self, visible: bool) -> None:
        """Show Apply/Viewer only while DEWETRON mode is selected."""
        self.dewetron_panel.pushButton_DEW_DataViewer.setVisible(visible)
        self.dewetron_panel.pushButton_DEW_TestApply.setVisible(visible)

    def _on_shared_record_mode(self, mode: str) -> None:
        """Mirror shared continuous/split choice onto WT page combos."""
        from utils.wt_recording_mode import mode_to_combo_index

        idx = mode_to_combo_index(mode)
        for combo in self._iter_wt_recording_combos():
            if combo.currentIndex() != idx:
                combo.blockSignals(True)
                combo.setCurrentIndex(idx)
                combo.blockSignals(False)

    def _iter_wt_recording_combos(self):
        try:
            for combo in self.primary_wt_widget.findChildren(
                QtWidgets.QComboBox, "comboBox_recording_mode"
            ):
                yield combo
        except Exception:
            return

    def _sync_record_mode_from_wt_pages(self) -> None:
        """Initialize shared combo from the first WT page recording mode."""
        from utils.wt_recording_mode import combo_index_to_mode

        for combo in self._iter_wt_recording_combos():
            mode = combo_index_to_mode(combo.currentIndex())
            self.recordingModeRow.blockSignals(True)
            self.recordingModeRow.set_mode(mode)
            self.recordingModeRow.blockSignals(False)
            return

    def _sync_step_enabled(self, checked: bool) -> None:
        """Keep the common checkbox active while disabling both mode pages."""
        enabled = bool(checked)
        self.radio_wt.setEnabled(enabled)
        self.radio_dewetron.setEnabled(enabled)
        self.analyzer_stack.setEnabled(enabled)
        self.recordingModeRow.setEnabled(enabled)
        self.dewetron_panel.pushButton_DEW_DataViewer.setEnabled(enabled)
        self.dewetron_panel.pushButton_DEW_TestApply.setEnabled(enabled)
        self._sync_dew_action_visibility(
            enabled and self._mode == self.DEWETRON_MODE
        )

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        self.set_mode(value)

    @property
    def analyzer_mode(self) -> str:
        return self._mode

    def current_mode(self) -> str:
        """Return ``wt3000`` or ``dewetron``."""
        return self._mode

    def set_mode(self, mode: str) -> None:
        """Select a mode, accepting common WT aliases."""
        normalized = str(mode).strip().lower().replace("-", "_")
        if normalized in {"dewetron", "dew", "dewetron_mode"}:
            self.radio_dewetron.setChecked(True)
        elif normalized in {"wt", "wt3000", "power_analyzer", "analyzer"}:
            self.radio_wt.setChecked(True)
        else:
            raise ValueError(f"Unknown analyzer mode: {mode}")

    def is_dewetron_mode(self) -> bool:
        return self._mode == self.DEWETRON_MODE

    def get_dewetron_config(self) -> DewetronUiConfig:
        return self.dewetron_panel.get_config()

    get_config = get_dewetron_config
    snapshot_config = get_dewetron_config

    def set_dewetron_config(self, config: Any) -> None:
        self.dewetron_panel.set_config(config)

    set_config = set_dewetron_config
    restore_config = set_dewetron_config

    def validate_dewetron_config(
        self, require_export_fields: bool = True
    ) -> List[str]:
        return self.dewetron_panel.validate_config(require_export_fields)

    validate_config = validate_dewetron_config


__all__ = [
    "AnalyzerModeSection",
    "DEFAULT_RATE_OPTIONS",
    "DewetronAutoTestPanel",
    "DewetronPanel",
    "DewetronUiConfig",
    "HARMONIC_RATE_OPTION",
    "PowerGroupTree",
    "parse_power_group_tree",
    "parse_power_groups_xml",
]
