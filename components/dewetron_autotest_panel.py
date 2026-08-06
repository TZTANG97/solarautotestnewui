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

    def __init__(
        self,
        rate_text: str = "Default",
        decimal_places: int = 3,
        realtime_waveform: bool = False,
        export_fields: Optional[Iterable[Any]] = None,
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
        if aliases:
            unknown = ", ".join(sorted(aliases))
            raise TypeError(f"Unknown DewetronUiConfig arguments: {unknown}")

        self.rate_text = str(rate_text).strip()
        self.decimal_places = int(decimal_places)
        self.realtime_waveform = bool(realtime_waveform)
        self.export_fields = _normalise_fields(export_fields)

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


def parse_power_group_tree(xml_string: str) -> Optional[PowerGroupTree]:
    """Parse DEWETRON ``Power Groups`` XML into category/subcategory leaves.

    The returned structure is ``{category: {subcategory: [field, ...]}}``.
    ``Advanced`` groups are intentionally omitted, matching the export choices
    presented by the existing DEWETRON dialogs.  ``None`` means no valid Power
    Groups section was found.
    """
    root = _find_power_group_element(xml_string)
    if root is None:
        return None

    result: PowerGroupTree = {}

    # Firmware normally nests categories below POWER/0 Channel nodes.  Iterate
    # their direct ChannelGroup children first, while also tolerating a direct
    # category layout used by small test fixtures.
    category_groups: List[ElementTree.Element] = []
    for child in list(root):
        if _local_name(child.tag) == "Channel":
            category_groups.extend(
                item
                for item in list(child)
                if _local_name(item.tag) == "ChannelGroup"
            )
        elif _local_name(child.tag) == "ChannelGroup":
            category_groups.append(child)

    for category in category_groups:
        category_name = (category.get("Type") or category.get("Name") or "").strip()
        if not category_name or category_name == "Advanced":
            continue
        subcategories = result.setdefault(category_name, {})

        for child in list(category):
            tag = _local_name(child.tag)
            if tag == "Channel":
                name = _channel_name(child)
                if name:
                    subcategories.setdefault("_default_", []).append(name)
                continue
            if tag != "ChannelGroup":
                continue

            sub_name = (child.get("Type") or child.get("Name") or "").strip()
            if not sub_name or sub_name == "Advanced":
                continue
            names = [
                _channel_name(channel)
                for channel in list(child)
                if _local_name(channel.tag) == "Channel"
            ]
            names = _normalise_fields(names)
            if names:
                existing = subcategories.setdefault(sub_name, [])
                existing.extend(name for name in names if name not in existing)

        if not subcategories:
            result.pop(category_name, None)

    return result or None


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
            # ``None`` means no saved selection exists yet; on the first device
            # refresh follow the established dialogs and select every field.
            self._desired_export_fields = None
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
        form.addRow("最大刷新率 (ms):", self.comboBox_DEW_MaxRefreshRate)

        self.spinBox_DEW_DecimalPlaces = QtWidgets.QSpinBox()
        self.spinBox_DEW_DecimalPlaces.setObjectName(
            "spinBox_DEW_DecimalPlaces"
        )
        self.spinBox_DEW_DecimalPlaces.setRange(0, 6)
        form.addRow("保留小数位数:", self.spinBox_DEW_DecimalPlaces)

        self.checkBox_DEW_RealtimeWaveform = QtWidgets.QCheckBox(
            "启用实时波形显示"
        )
        self.checkBox_DEW_RealtimeWaveform.setObjectName(
            "checkBox_DEW_RealtimeWaveform"
        )
        form.addRow("实时波形:", self.checkBox_DEW_RealtimeWaveform)
        group_layout.addLayout(form)

        tree_header = QtWidgets.QHBoxLayout()
        tree_header.addWidget(QtWidgets.QLabel("导出字段选择"))
        tree_header.addStretch()
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
        self.treeWidget_DEW_ExportFields.setMinimumHeight(220)
        group_layout.addWidget(self.treeWidget_DEW_ExportFields, 1)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch()
        self.pushButton_DEW_DataViewer = QtWidgets.QPushButton("数据查看")
        self.pushButton_DEW_DataViewer.setObjectName("pushButton_DEW_DataViewer")
        buttons.addWidget(self.pushButton_DEW_DataViewer)
        self.pushButton_DEW_TestApply = QtWidgets.QPushButton("测试生效")
        self.pushButton_DEW_TestApply.setObjectName("pushButton_DEW_TestApply")
        buttons.addWidget(self.pushButton_DEW_TestApply)
        group_layout.addLayout(buttons)

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

    def _connect_signals(self) -> None:
        self.pushButton_DEW_TestApply.clicked.connect(self._request_apply)
        self.pushButton_DEW_RefreshFields.clicked.connect(
            self.refresh_requested.emit
        )
        self.pushButton_DEW_DataViewer.clicked.connect(self.viewer_requested.emit)
        self.comboBox_DEW_MaxRefreshRate.currentTextChanged.connect(
            self._emit_config_changed
        )
        self.spinBox_DEW_DecimalPlaces.valueChanged.connect(
            self._emit_config_changed
        )
        self.checkBox_DEW_RealtimeWaveform.toggled.connect(
            self._emit_config_changed
        )
        self.treeWidget_DEW_ExportFields.itemChanged.connect(
            self._on_tree_item_changed
        )

    def _request_apply(self) -> None:
        config = self.get_config()
        self.apply_requested.emit()
        self.apply_config_requested.emit(config)

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
                        leaf = QtWidgets.QTreeWidgetItem(sub_item, [field])
                        leaf.setData(0, self.FIELD_ROLE, field)
                        leaf.setFlags(leaf.flags() | QtCore.Qt.ItemIsUserCheckable)
                        checked = desired_set is None or field in desired_set
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
        self.checkBox_DEW_RealtimeWaveform.setChecked(value.realtime_waveform)
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
        layout.addWidget(self.mode_row)

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
        self._sync_step_enabled(self.step_checkbox.isChecked())

    def _on_mode_toggled(
        self, button: QtWidgets.QAbstractButton, checked: bool
    ) -> None:
        if not checked:
            return
        if button is self.radio_dewetron:
            self._mode = self.DEWETRON_MODE
            self.analyzer_stack.setCurrentIndex(1)
        else:
            self._mode = self.WT_MODE
            self.analyzer_stack.setCurrentIndex(0)
        self.mode_changed.emit(self._mode)

    def _sync_step_enabled(self, checked: bool) -> None:
        """Keep the common checkbox active while disabling both mode pages."""
        enabled = bool(checked)
        self.radio_wt.setEnabled(enabled)
        self.radio_dewetron.setEnabled(enabled)
        self.analyzer_stack.setEnabled(enabled)

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
