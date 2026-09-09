# -*- coding: utf-8 -*-
"""本机字段记忆、Tab 跳焦点、输入框旁单位等 UI 辅助。"""
from __future__ import annotations

from typing import List, Optional

from PyQt5.QtCore import QEvent, QObject, QSettings, Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QCompleter,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QTextEdit,
    QToolButton,
    QWidget,
)

_ORG = "SolarAutoTest"
_APP = "FieldMemory"
_MAX_HISTORY = 16

# objectName 片段 → 记忆键（同键跨页面共享历史）
_KEY_HINTS = (
    ("WT3000_IP", "wt.ip"),
    ("WT3000_Port", "wt.port"),
    ("itech_AC_IP", "ac.ip"),
    ("itech_AC_Port", "ac.port"),
    ("chroma_AC_IP", "chroma.ac.ip"),
    ("chroma_AC_Port", "chroma.ac.port"),
    ("bluesight_DC1_IP", "dc.ip"),
    ("bluesight_DC1_Port", "dc.port"),
    ("itech_DC1_IP", "itech.dc.ip"),
    ("itech_DC1_Port", "itech.dc.port"),
    ("lineEdit_IP", "dewetron.ip"),
    ("lineEdit_Port", "dewetron.port"),
    ("textEdit_AC_VOLT", "ac.volt"),
    ("textEdit_AC_FR", "ac.freq"),
    ("textEdit_VOLT", "ac.volt"),
    ("textEdit_FR", "ac.freq"),
    ("textEdit_Vmp", "dc.vmp"),
    ("textEdit_Voc", "dc.voc"),
    ("textEdit_Imp", "dc.imp"),
    ("textEdit_Isc", "dc.isc"),
    ("textEdit_PF", "dc.pf"),
    ("_AC_VOLT", "test.ac.volt"),
    ("_AC_FR", "test.ac.freq"),
    ("_DC1_VOLT", "test.dc.vmp"),
    ("_DC1_CURR", "test.dc.imp"),
    ("_DC1_Voc", "test.dc.voc"),
    ("_DC1_Isc", "test.dc.isc"),
    ("_DC1_PF", "test.dc.pf"),
    ("_DC2_VOLT", "test.dc.vmp"),
    ("_DC2_CURR", "test.dc.imp"),
    ("_DC2_Voc", "test.dc.voc"),
    ("_DC2_Isc", "test.dc.isc"),
    ("_DC2_PF", "test.dc.pf"),
    ("_DC3_VOLT", "test.dc.vmp"),
    ("_DC3_CURR", "test.dc.imp"),
    ("_DC3_Voc", "test.dc.voc"),
    ("_DC3_Isc", "test.dc.isc"),
    ("_DC3_PF", "test.dc.pf"),
    ("_DC4_VOLT", "test.dc.vmp"),
    ("_DC4_CURR", "test.dc.imp"),
    ("_DC4_Voc", "test.dc.voc"),
    ("_DC4_Isc", "test.dc.isc"),
    ("_DC4_PF", "test.dc.pf"),
)


def _settings() -> QSettings:
    return QSettings(_ORG, _APP)


def history_key_for_object_name(object_name: str) -> Optional[str]:
    name = object_name or ""
    for hint, key in _KEY_HINTS:
        if hint in name:
            return key
    return None


def load_history(key: str) -> List[str]:
    raw = _settings().value(f"history/{key}", [])
    if isinstance(raw, str):
        items = [raw] if raw.strip() else []
    elif isinstance(raw, (list, tuple)):
        items = [str(x).strip() for x in raw if str(x).strip()]
    else:
        items = []
    # 去重保序
    out: List[str] = []
    seen = set()
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out[:_MAX_HISTORY]


def remember_value(key: str, value: str) -> None:
    value = (value or "").strip()
    if not value:
        return
    items = load_history(key)
    if value in items:
        items.remove(value)
    items.insert(0, value)
    _settings().setValue(f"history/{key}", items[:_MAX_HISTORY])
    _settings().sync()


def last_value(key: str, default: str = "") -> str:
    items = load_history(key)
    return items[0] if items else default


def _widget_text(w: QWidget) -> str:
    if isinstance(w, QLineEdit):
        return w.text().strip()
    if isinstance(w, QTextEdit):
        return w.toPlainText().strip()
    if isinstance(w, QComboBox):
        return w.currentText().strip()
    return ""


def _set_widget_text(w: QWidget, text: str) -> None:
    if isinstance(w, QLineEdit):
        w.setText(text)
    elif isinstance(w, QTextEdit):
        w.setPlainText(text)
    elif isinstance(w, QComboBox):
        w.setCurrentText(text)
        if w.isEditable() and w.lineEdit() is not None:
            w.lineEdit().setText(text)


class _TabFocusFilter(QObject):
    """QTextEdit 默认 Tab 插入制表符；改为跳到下一/上一焦点。"""

    def eventFilter(self, obj, event):
        if event.type() != QEvent.KeyPress:
            return False
        if not isinstance(event, QKeyEvent):
            return False
        if event.key() != Qt.Key_Tab:
            return False
        # Ctrl/Alt+Tab 交给系统
        if event.modifiers() & (Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier):
            return False
        widget = obj
        if isinstance(widget, QTextEdit) and widget.isReadOnly():
            return False
        if event.modifiers() & Qt.ShiftModifier:
            QApplication.focusPreviousChild()
        else:
            QApplication.focusNextChild()
        return True


_TAB_FILTER = _TabFocusFilter()


def enable_tab_changes_focus(widget: QWidget) -> None:
    if widget is None:
        return
    if isinstance(widget, QTextEdit):
        if hasattr(widget, "setTabChangesFocus"):
            try:
                widget.setTabChangesFocus(True)
                return
            except Exception:
                pass
        widget.installEventFilter(_TAB_FILTER)
    elif isinstance(widget, QLineEdit):
        # QLineEdit 默认 Tab 已跳焦点
        pass


class _MemoryFocusFilter(QObject):
    """失焦时写入历史。"""

    def __init__(self, key: str, widget: QWidget, completer: Optional[QCompleter] = None):
        super().__init__(widget)
        self._key = key
        self._widget = widget
        self._completer = completer

    def eventFilter(self, obj, event):
        if obj is self._widget and event.type() == QEvent.FocusOut:
            remember_value(self._key, _widget_text(self._widget))
            if self._completer is not None:
                model = self._completer.model()
                if model is not None and hasattr(model, "setStringList"):
                    model.setStringList(load_history(self._key))
        return False


def enable_field_memory(widget: QWidget, key: Optional[str] = None) -> None:
    """为输入框挂历史补全 + 失焦保存；双击或 ▾ 下拉选历史。"""
    if widget is None:
        return
    if getattr(widget, "_field_memory_enabled", False):
        return
    obj_name = widget.objectName() or ""
    key = key or history_key_for_object_name(obj_name)
    if not key:
        return

    history = load_history(key)
    completer = QCompleter(history, widget)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    completer.setFilterMode(Qt.MatchContains)
    completer.setCompletionMode(QCompleter.PopupCompletion)

    # 工况点功率（_PF_4 等）保持界面默认，不覆盖
    _skip_restore = any(
        tag in obj_name for tag in ("_PF_4", "_PF_5", "_PF_6", "_PF_7", "_PF_8", "_PF_2")
    )
    if history and not _skip_restore:
        _set_widget_text(widget, history[0])

    if isinstance(widget, QLineEdit):
        widget.setCompleter(completer)
        widget.editingFinished.connect(lambda w=widget, k=key: remember_value(k, w.text()))
    elif isinstance(widget, QComboBox) and widget.isEditable():
        widget.setCompleter(completer)
        for item in history:
            if widget.findText(item) < 0:
                widget.addItem(item)
    elif not isinstance(widget, QTextEdit):
        return

    mem_filter = _MemoryFocusFilter(key, widget, completer)
    widget.installEventFilter(mem_filter)
    widget._field_memory_filter = mem_filter  # type: ignore

    def _pick_from_menu():
        items = load_history(key)
        if not items:
            return
        menu = QMenu(widget)
        for it in items:
            act = menu.addAction(it)
            act.triggered.connect(lambda _=False, t=it: _set_widget_text(widget, t))
        pos = widget.mapToGlobal(widget.rect().bottomLeft())
        menu.exec_(pos)

    widget._field_memory_key = key  # type: ignore
    widget._field_memory_pick = _pick_from_menu  # type: ignore
    widget._field_memory_enabled = True  # type: ignore

    class _DblFilter(QObject):
        def eventFilter(self, obj, event):
            if obj is widget and event.type() == QEvent.MouseButtonDblClick:
                _pick_from_menu()
                return False
            return False

    dbl = _DblFilter(widget)
    widget.installEventFilter(dbl)
    widget._field_memory_dbl = dbl  # type: ignore


def attach_history_dropdown_button(widget: QWidget) -> Optional[QWidget]:
    """把输入框包成 [输入框][▼]，▼ 弹出历史。返回容器；失败返回 None。"""
    if widget is None or not getattr(widget, "_field_memory_enabled", False):
        return None
    if getattr(widget, "_field_memory_wrapped", False):
        return None
    parent = widget.parentWidget()
    if parent is None:
        return None
    layout = parent.layout()
    # 仅当父布局可替换时包装；Timeline/Grid 里较复杂，改为工具按钮覆盖右上角
    btn = QToolButton(widget)
    btn.setText("▾")
    btn.setToolTip("选择本机历史输入")
    btn.setCursor(Qt.PointingHandCursor)
    btn.setFixedSize(18, 18)
    btn.setStyleSheet(
        "QToolButton { border: none; color: #64748b; background: transparent; font-size: 11px; }"
        "QToolButton:hover { color: #0f172a; }"
    )
    pick = getattr(widget, "_field_memory_pick", None)
    if callable(pick):
        btn.clicked.connect(pick)

    def _reposition():
        btn.move(max(0, widget.width() - btn.width() - 2), 2)
        btn.raise_()

    widget.resizeEvent = _wrap_resize(widget, widget.resizeEvent, _reposition)  # type: ignore
    _reposition()
    btn.show()
    widget._field_memory_wrapped = True  # type: ignore
    widget._field_memory_btn = btn  # type: ignore
    return widget


def _wrap_resize(widget, original, on_resize):
    def _handler(event):
        if original is not None:
            original(event)
        else:
            QWidget.resizeEvent(widget, event)
        try:
            on_resize()
        except Exception:
            pass

    return _handler


def wrap_with_unit(widget: QWidget, unit_text: str) -> QWidget:
    """输入框后面跟单位标签。"""
    container = QWidget()
    h = QHBoxLayout(container)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(4)
    h.addWidget(widget)
    lbl = QLabel(unit_text)
    lbl.setStyleSheet("color: #64748b; background: transparent;")
    h.addWidget(lbl)
    h.addStretch(1)
    return container


def polish_input_widgets(root: QWidget, *, with_memory: bool = True) -> int:
    """对 root 下常见输入框启用 Tab 跳转 + 本机历史。返回处理数量。"""
    if root is None:
        return 0
    if not hasattr(root, "findChildren"):
        stacked = getattr(root, "stackedWidget", None)
        if stacked is not None and hasattr(stacked, "findChildren"):
            root = stacked.window() if hasattr(stacked, "window") else stacked
        else:
            return 0
    n = 0
    widgets: List[QWidget] = []
    if isinstance(root, (QTextEdit, QLineEdit, QComboBox)):
        widgets.append(root)
    widgets.extend(root.findChildren(QTextEdit))
    widgets.extend(root.findChildren(QLineEdit))
    widgets.extend(root.findChildren(QComboBox))
    # 去重保序
    seen = set()
    uniq: List[QWidget] = []
    for w in widgets:
        wid = id(w)
        if wid in seen:
            continue
        seen.add(wid)
        uniq.append(w)
    for w in uniq:
        obj = w.objectName() or ""
        # 跳过只读日志
        if isinstance(w, QTextEdit) and w.isReadOnly():
            continue
        if obj.startswith("log_") or "ReturnMessage" in obj or obj == "textEdit_AC":
            # textEdit_AC 是日志大框
            if obj == "textEdit_AC" and isinstance(w, QTextEdit) and w.isReadOnly():
                continue
            if "ReturnMessage" in obj or obj.startswith("log_"):
                continue
        enable_tab_changes_focus(w)
        if with_memory and history_key_for_object_name(obj):
            enable_field_memory(w)
            attach_history_dropdown_button(w)
            n += 1
        elif isinstance(w, QTextEdit) and w.maximumHeight() <= 48:
            # 单行高的试验输入框：至少 Tab 跳转
            n += 1
    return n
