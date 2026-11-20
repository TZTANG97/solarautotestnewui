# -*- coding: utf-8 -*-
"""按 dc_channels 给已经建好的试验页补上缺少的直流路。"""
from __future__ import annotations

import re
from typing import List

from PyQt5 import QtCore, QtWidgets

from utils.dc_channels import channel_numbers, dc_token

_KNOWN_UIS: List[object] = []
_FAMILIES = (
    "checkBox_S1_DC%d",
    "checkBox_S3_DC%d",
    "checkBox_S_End_DC%d",
    "checkBox_S_END_DC%d",
    "checkBox_DC%d",
)


def remember_ui(ui) -> None:
    if ui is None or ui in _KNOWN_UIS:
        return
    _KNOWN_UIS.append(ui)


def ensure_dc_channels(ui) -> None:
    """试验页创建后调用：配置里有、界面上还没有的路，按第 1 路的样子补一行。新路默认不勾。"""
    if ui is None:
        return
    remember_ui(ui)
    _fill_dc_select(getattr(ui, "comboBox_DC_Select", None))
    for n in channel_numbers():
        if n <= 1:
            continue
        for fmt in _FAMILIES:
            _ensure_family(ui, fmt, n)


def refresh_known_uis() -> None:
    for ui in list(_KNOWN_UIS):
        try:
            ensure_dc_channels(ui)
            _hide_removed_channels(ui)
        except Exception as exc:
            print("[直流路] 刷新试验页失败: %s" % exc, flush=True)


def _hide_removed_channels(ui) -> None:
    """配置里已删的路：试验页对应控件隐藏并取消勾选。"""
    keep = set(channel_numbers())
    for fmt in _FAMILIES:
        for attr, widget in list(vars(ui).items()):
            if not re.fullmatch(r".*DC\d+$", str(attr or "")):
                continue
            m = re.search(r"DC(\d+)$", str(attr))
            if not m:
                continue
            n = int(m.group(1))
            if n <= 4 or n in keep:
                continue
            if not isinstance(widget, QtWidgets.QWidget):
                continue
            try:
                if isinstance(widget, QtWidgets.QCheckBox):
                    widget.setChecked(False)
                widget.hide()
            except Exception:
                pass
            # 同排克隆出来的输入框也藏掉
            parent = widget.parentWidget()
            layout = parent.layout() if parent is not None else None
            if not isinstance(layout, QtWidgets.QGridLayout):
                continue
            row = None
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item is not None and item.widget() is widget:
                    row = layout.getItemPosition(i)[0]
                    break
            if row is None:
                continue
            for i in range(layout.count()):
                item = layout.itemAt(i)
                w = item.widget() if item is not None else None
                if w is None:
                    continue
                if layout.getItemPosition(i)[0] == row:
                    try:
                        w.hide()
                    except Exception:
                        pass


def _fill_dc_select(combo) -> None:
    if combo is None or not hasattr(combo, "clear"):
        return
    current = ""
    try:
        current = str(combo.currentText() or "").strip()
    except Exception:
        current = ""
    combo.blockSignals(True)
    try:
        combo.clear()
        for n in channel_numbers():
            combo.addItem(dc_token(n))
        if current:
            idx = combo.findText(current)
            if idx >= 0:
                combo.setCurrentIndex(idx)
    finally:
        combo.blockSignals(False)


def _ensure_family(ui, fmt: str, channel: int) -> None:
    name = fmt % channel
    if getattr(ui, name, None) is not None:
        return
    template = getattr(ui, fmt % 1, None)
    if template is None:
        return
    parent = template.parentWidget()
    layout = parent.layout() if parent is not None else None
    if isinstance(layout, QtWidgets.QGridLayout):
        _clone_grid_row(ui, layout, template, channel)
        return
    if isinstance(layout, (QtWidgets.QHBoxLayout, QtWidgets.QVBoxLayout)):
        _clone_loose_checkbox(ui, layout, template, channel)


def _clone_grid_row(ui, grid, template, channel: int) -> None:
    src_row = None
    for i in range(grid.count()):
        item = grid.itemAt(i)
        if item is None or item.widget() is not template:
            continue
        src_row = grid.getItemPosition(i)[0]
        break
    if src_row is None:
        return
    cells = []
    for i in range(grid.count()):
        item = grid.itemAt(i)
        widget = item.widget() if item is not None else None
        if widget is None:
            continue
        row, col, row_span, col_span = grid.getItemPosition(i)
        if row == src_row and row_span == 1 and col_span == 1:
            cells.append((col, widget))
    if not cells:
        return
    dest = 0
    for i in range(grid.count()):
        row = grid.getItemPosition(i)[0]
        if row >= dest:
            dest = row + 1
    for col, widget in cells:
        created = _clone_widget(ui, widget, channel)
        if created is None:
            continue
        grid.addWidget(created, dest, col)


def _clone_loose_checkbox(ui, layout, template, channel: int) -> None:
    created = _clone_widget(ui, template, channel)
    if created is None:
        return
    # 插在弹簧前面，避免新路被挤出可视区域
    insert_at = layout.count()
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item is not None and item.spacerItem() is not None:
            insert_at = i
            break
    layout.insertWidget(insert_at, created)


def _clone_widget(ui, widget, channel: int):
    name = _rename(str(widget.objectName() or ""), 1, channel)
    if not name or getattr(ui, name, None) is not None:
        return None
    if isinstance(widget, QtWidgets.QCheckBox):
        created = QtWidgets.QCheckBox(_rename(widget.text(), 1, channel))
        created.setChecked(False)
    elif isinstance(widget, QtWidgets.QComboBox):
        created = QtWidgets.QComboBox()
        for i in range(widget.count()):
            created.addItem(widget.itemText(i))
        close_at = created.findText("关闭")
        if close_at >= 0:
            created.setCurrentIndex(close_at)
        created.setFixedWidth(widget.width() or 100)
    elif isinstance(widget, QtWidgets.QTextEdit):
        created = QtWidgets.QTextEdit()
        try:
            created.setPlainText(widget.toPlainText())
        except Exception:
            pass
        # 跟模板一样压成单行高，否则会变成大块 textarea
        max_h = int(widget.maximumHeight() or 0)
        min_h = int(widget.minimumHeight() or 0)
        if 0 < max_h < 16_000_000:
            created.setMaximumHeight(max_h)
        else:
            created.setMaximumHeight(40)
        if min_h > 0:
            created.setMinimumHeight(min_h)
        else:
            created.setMinimumHeight(36)
        created.setFixedWidth(max(int(widget.width() or 0), int(widget.minimumWidth() or 0), 70))
        created.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        created.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        try:
            created.setTabChangesFocus(True)
        except Exception:
            pass
        if widget.styleSheet():
            created.setStyleSheet(widget.styleSheet())
        for prop in ("_ui_design_max_h", "_ui_design_min_h", "_ui_design_w", "_ui_ss_orig"):
            val = widget.property(prop)
            if val not in (None, ""):
                created.setProperty(prop, val)
        if created.property("_ui_design_max_h") in (None, ""):
            created.setProperty("_ui_design_max_h", 40)
            created.setProperty("_ui_design_min_h", 40)
    else:
        return None
    created.setObjectName(name)
    setattr(ui, name, created)
    try:
        from utils.ui_field_helpers import polish_input_widgets

        polish_input_widgets(created)
    except Exception:
        pass
    return created


def _rename(text: str, src: int, dst: int) -> str:
    """只改路号。checkBox_S1_DC1 里步骤号 S1 不动，变成 checkBox_S1_DC5。"""
    s = str(text or "")
    s = re.sub(r"DC%d(?!\d)" % src, "DC%d" % dst, s)
    if not re.search(r"DC%d(?!\d)" % dst, s):
        s = re.sub(r"%d$" % src, str(dst), s)
    return s
