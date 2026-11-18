# -*- coding: utf-8 -*-
"""Reusable editor for strict timing-profile rows."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from utils.timing_profile import (
    TIME_UNITS,
    TimingProfileSchema,
    TimingProfileValidationError,
    default_profile_row,
    get_schema,
    profile_from_json,
    profile_to_json,
    validate_profile,
)


_BASE_COLUMNS = (
    ("enabled", "启用"),
    ("label", "标签"),
    ("t_pre", "前置时间"),
    ("t_pre_unit", "单位"),
    ("t_dwell", "保持时间"),
    ("t_dwell_unit", "单位"),
    ("t_post", "后置时间"),
    ("t_post_unit", "单位"),
)


class TimingProfileTable(QtWidgets.QWidget):
    """Table widget with schema-aware rows and strict extraction.

    ``get_profile()`` is the validation boundary.  Incomplete text can remain in
    an editor while the operator is typing, but it cannot enter persistence or a
    command plan.
    """

    profile_changed = QtCore.pyqtSignal()
    profileChanged = profile_changed

    def __init__(
        self,
        schema: Any,
        rows: Optional[Iterable[Mapping[str, Any]]] = None,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("timingProfileTable")
        self.schema: TimingProfileSchema = get_schema(schema)
        self._loading = False
        self._columns = list(_BASE_COLUMNS)
        self._columns.extend(
            (name, self.schema.labels.get(name, name)) for name in self.schema.fields
        )
        self._columns.append(("repeats", "重复次数"))
        self._column_index = {
            field_name: index
            for index, (field_name, _label) in enumerate(self._columns)
        }

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        toolbar_host = QtWidgets.QWidget()
        toolbar_host.setObjectName("timingProfileToolbar")
        toolbar_host.setMinimumHeight(40)
        toolbar_host.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        toolbar = QtWidgets.QHBoxLayout(toolbar_host)
        toolbar.setContentsMargins(0, 2, 0, 6)
        toolbar.setSpacing(8)
        self.pushButton_ProfileAdd = self._button("pushButton_ProfileAdd", "新增工况")
        self.pushButton_ProfileDelete = self._button(
            "pushButton_ProfileDelete", "删除工况"
        )
        self.pushButton_ProfileUp = self._button("pushButton_ProfileUp", "上移")
        self.pushButton_ProfileDown = self._button("pushButton_ProfileDown", "下移")
        self.pushButton_ProfileClear = self._button("pushButton_ProfileClear", "清空")
        # Soft Panel 主题下默认按钮易「白底白字」看不见；强制对比度
        _btn_ss = (
            "QPushButton { padding: 6px 12px; font-size: 13px; font-weight: bold; "
            "color: #0f172a; background: #e2e8f0; border: 1px solid #64748b; "
            "border-radius: 4px; min-height: 28px; min-width: 72px; }"
            "QPushButton:hover { background: #cbd5e1; }"
            "QPushButton:pressed { background: #94a3b8; }"
        )
        for button in (
            self.pushButton_ProfileAdd,
            self.pushButton_ProfileDelete,
            self.pushButton_ProfileUp,
            self.pushButton_ProfileDown,
            self.pushButton_ProfileClear,
        ):
            button.setStyleSheet(_btn_ss)
            toolbar.addWidget(button)
        toolbar.addStretch()
        root.addWidget(toolbar_host)

        self.table = QtWidgets.QTableWidget(0, len(self._columns))
        self.table.setObjectName("tableWidget_TimingProfile")
        self.table.setHorizontalHeaderLabels([label for _name, label in self._columns])
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        label_col = self._column_index["label"]
        header.setSectionResizeMode(label_col, QtWidgets.QHeaderView.Stretch)
        self.tableWidget = self.table
        self.tableWidget_TimingProfile = self.table
        self.profileTable = self.table
        root.addWidget(self.table, 1)

        self.pushButton_ProfileAdd.clicked.connect(self.add_row)
        self.pushButton_ProfileDelete.clicked.connect(self.remove_selected_row)
        self.pushButton_ProfileUp.clicked.connect(lambda: self.move_selected_row(-1))
        self.pushButton_ProfileDown.clicked.connect(lambda: self.move_selected_row(1))
        self.pushButton_ProfileClear.clicked.connect(self.clear)
        self.table.itemChanged.connect(self._emit_changed)

        initial = list(rows) if rows is not None else [
            default_profile_row(self.schema, label="工况 1")
        ]
        self.set_profile(initial)

    @staticmethod
    def _button(name: str, text: str) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton(text)
        button.setObjectName(name)
        button.setMinimumWidth(70)
        return button

    def _emit_changed(self, *_args: Any) -> None:
        if not self._loading:
            self.profile_changed.emit()

    def _unit_combo(self, value: Any) -> QtWidgets.QComboBox:
        combo = QtWidgets.QComboBox()
        combo.addItems(list(TIME_UNITS))
        index = combo.findText(str(value or "秒"))
        combo.setCurrentIndex(index if index >= 0 else combo.findText("秒"))
        combo.currentIndexChanged.connect(self._emit_changed)
        return combo

    @staticmethod
    def _text(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    def _is_bool_field(self, field_name: str) -> bool:
        if field_name == "enabled":
            return True
        return field_name in getattr(self.schema, "bool_fields", ())

    def _populate_row(self, row_index: int, row: Mapping[str, Any]) -> None:
        for field_name, _label in self._columns:
            column = self._column_index[field_name]
            if self._is_bool_field(field_name):
                item = QtWidgets.QTableWidgetItem()
                item.setFlags(
                    QtCore.Qt.ItemIsEnabled
                    | QtCore.Qt.ItemIsSelectable
                    | QtCore.Qt.ItemIsUserCheckable
                )
                default = True
                if field_name != "enabled":
                    default = bool(self.schema.defaults.get(field_name, True))
                item.setCheckState(
                    QtCore.Qt.Checked
                    if bool(row.get(field_name, default))
                    else QtCore.Qt.Unchecked
                )
                self.table.setItem(row_index, column, item)
            elif field_name.endswith("_unit"):
                self.table.setCellWidget(
                    row_index, column, self._unit_combo(row.get(field_name, "秒"))
                )
            else:
                item = QtWidgets.QTableWidgetItem(self._text(row.get(field_name)))
                if field_name not in {"label"}:
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(row_index, column, item)

    def set_profile(
        self,
        rows: Iterable[Mapping[str, Any]],
        *,
        validate: bool = True,
        allow_empty: bool = True,
    ) -> None:
        values = list(rows)
        if validate:
            values = validate_profile(values, self.schema, allow_empty=allow_empty)
        self._loading = True
        try:
            self.table.setRowCount(0)
            for row in values:
                row_index = self.table.rowCount()
                self.table.insertRow(row_index)
                self._populate_row(row_index, row)
        finally:
            self._loading = False
        self.profile_changed.emit()

    set_rows = set_profile

    def _raw_row(self, row_index: int) -> Dict[str, Any]:
        row: Dict[str, Any] = {}
        for field_name, _label in self._columns:
            column = self._column_index[field_name]
            if self._is_bool_field(field_name):
                item = self.table.item(row_index, column)
                row[field_name] = bool(
                    item and item.checkState() == QtCore.Qt.Checked
                )
            elif field_name.endswith("_unit"):
                combo = self.table.cellWidget(row_index, column)
                row[field_name] = combo.currentText() if combo is not None else "秒"
            else:
                item = self.table.item(row_index, column)
                row[field_name] = item.text().strip() if item is not None else ""
        return row

    def get_profile(
        self,
        *,
        validate: bool = True,
        allow_empty: bool = False,
    ) -> List[Dict[str, Any]]:
        rows = [self._raw_row(index) for index in range(self.table.rowCount())]
        if validate:
            return validate_profile(rows, self.schema, allow_empty=allow_empty)
        return rows

    get_rows = get_profile

    def validate_profile(self, *, allow_empty: bool = False) -> List[Dict[str, Any]]:
        return self.get_profile(validate=True, allow_empty=allow_empty)

    def add_row(self, row: Optional[Mapping[str, Any]] = None) -> int:
        if isinstance(row, bool):
            # ``clicked`` emits a checked bool.
            row = None
        row_index = self.table.rowCount()
        value = dict(
            row
            or default_profile_row(
                self.schema,
                label="工况 %d" % (row_index + 1),
            )
        )
        self._loading = True
        try:
            self.table.insertRow(row_index)
            self._populate_row(row_index, value)
            self.table.selectRow(row_index)
        finally:
            self._loading = False
        self.profile_changed.emit()
        return row_index

    def remove_selected_row(self) -> None:
        row = self.table.currentRow()
        if row < 0 and self.table.rowCount():
            row = self.table.rowCount() - 1
        if row >= 0:
            self.table.removeRow(row)
            self.profile_changed.emit()

    def clear(self) -> None:
        self.table.setRowCount(0)
        self.profile_changed.emit()

    def move_selected_row(self, delta: int) -> None:
        source = self.table.currentRow()
        target = source + int(delta)
        if source < 0 or target < 0 or target >= self.table.rowCount():
            return
        rows = self.get_profile(validate=False, allow_empty=True)
        rows[source], rows[target] = rows[target], rows[source]
        self.set_profile(rows, validate=False, allow_empty=True)
        self.table.selectRow(target)

    def to_json(self, *, allow_empty: bool = False) -> str:
        return profile_to_json(
            self.get_profile(allow_empty=allow_empty),
            self.schema,
            allow_empty=allow_empty,
        )

    def from_json(self, value: Any, *, allow_empty: bool = True) -> None:
        self.set_profile(
            profile_from_json(value, self.schema, allow_empty=allow_empty),
            validate=False,
            allow_empty=allow_empty,
        )


__all__ = [
    "TimingProfileTable",
    "TimingProfileValidationError",
]
