# -*- coding: utf-8 -*-
"""本机字段记忆、Tab 跳焦点、输入框旁单位等 UI 辅助。"""
from __future__ import annotations

from typing import Dict, List, Optional

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

# 设备页：必须精确 objectName，禁止子串匹配（否则试验步骤控件会串到 AC/DC 设置）
_DEVICE_EXACT_KEYS = {
    "textEdit_AC_VOLT": "ac.volt",
    "textEdit_AC_FR": "ac.freq",
    "comboBox_Phase": "ac.phase",
    "combo_phase": "ac.phase",
    "textEdit_VOLT": "ac.volt",
    "textEdit_FR": "ac.freq",
    "textEdit_Vmp": "dc.vmp",
    "textEdit_Voc": "dc.voc",
    "textEdit_Imp": "dc.imp",
    "textEdit_Isc": "dc.isc",
    "textEdit_PF": "dc.pf",
    "lineEdit_WT3000_IP": "wt.ip",
    "lineEdit_WT3000_Port": "wt.port",
    "lineEdit_itech_AC_IP": "ac.ip",
    "lineEdit_itech_AC_Port": "ac.port",
    "lineEdit_chroma_AC_IP": "chroma.ac.ip",
    "lineEdit_chroma_AC_Port": "chroma.ac.port",
    "lineEdit_bluesight_DC1_IP": "dc.ip",
    "lineEdit_bluesight_DC1_Port": "dc.port",
    "lineEdit_itech_DC1_IP": "itech.dc.ip",
    "lineEdit_itech_DC1_Port": "itech.dc.port",
    "lineEdit_IP": "dewetron.ip",
    "lineEdit_Port": "dewetron.port",
}


def _settings() -> QSettings:
    return QSettings(_ORG, _APP)


def _safe_scope_id(scope: str) -> str:
    import re

    raw = scope[5:] if scope.startswith("test:") else scope
    safe = re.sub(r"[^\w\-]+", "_", str(raw or "unknown"), flags=re.UNICODE)
    return (safe.strip("_") or "unknown")[:120]


def history_key_for_object_name(
    object_name: str, *, memory_scope: str = "device"
) -> Optional[str]:
    """Resolve memory key.

    - device scope: exact device-page objectNames only
    - test:<name> scope: per-test keys ``test.<id>.<objectName>`` (never share with device)
    """
    name = object_name or ""
    if not name:
        return None
    scope = memory_scope or "device"
    if scope.startswith("test:"):
        # 试验页：整名隔离，绝不落入 ac.volt / dc.vmp
        return f"test.{_safe_scope_id(scope)}.{name}"
    # device / default
    return _DEVICE_EXACT_KEYS.get(name)


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
    # IP 历史只记完整 IPv4，避免「上次」出现 192.10 这类半截输入
    if str(key).endswith(".ip") or str(key) in {"ac.ip", "dc.ip", "wt.ip", "dewetron.ip", "itech.dc.ip", "chroma.ac.ip"}:
        from utils.device_discovery import _looks_ipv4, parse_host_port

        host, _port = parse_host_port(value)
        if not host or not _looks_ipv4(host):
            return
    items = load_history(key)
    if value in items:
        items.remove(value)
    items.insert(0, value)
    _settings().setValue(f"history/{key}", items[:_MAX_HISTORY])
    _settings().sync()


def is_phase_combo_name(object_name: str) -> bool:
    name = object_name or ""
    return name in {"comboBox_Phase", "combo_phase"} or name.endswith("_AC_2")


def capture_phase_memory(root: QWidget, *, memory_scope: str = "device") -> Dict[str, str]:
    """记下各相位下拉上次选的「三相/单相」，供试验预设回放之后再盖回去。"""
    out: Dict[str, str] = {}
    if root is None or not hasattr(root, "findChildren"):
        return out
    for combo in root.findChildren(QComboBox):
        name = combo.objectName() or ""
        if not is_phase_combo_name(name):
            continue
        key = history_key_for_object_name(name, memory_scope=memory_scope)
        if not key:
            continue
        saved = last_value(key)
        if saved:
            out[name] = saved
    return out


def restore_phase_memory(root: QWidget, saved: Dict[str, str]) -> int:
    if root is None or not saved or not hasattr(root, "findChildren"):
        return 0
    n = 0
    for combo in root.findChildren(QComboBox):
        name = combo.objectName() or ""
        text = saved.get(name) or ""
        if not text:
            continue
        idx = combo.findText(text)
        if idx >= 0 and combo.currentIndex() != idx:
            combo.setCurrentIndex(idx)
            n += 1
        elif idx >= 0:
            n += 1
    return n


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


def enable_field_memory(
    widget: QWidget, key: Optional[str] = None, *, memory_scope: str = "device"
) -> None:
    """为输入框挂历史补全 + 失焦保存；双击或 ▾ 下拉选历史。"""
    if widget is None:
        return
    if getattr(widget, "_field_memory_enabled", False):
        return
    obj_name = widget.objectName() or ""
    key = key or history_key_for_object_name(obj_name, memory_scope=memory_scope)
    if not key:
        return

    history = load_history(key)
    completer = QCompleter(history, widget)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    completer.setFilterMode(Qt.MatchContains)
    completer.setCompletionMode(QCompleter.PopupCompletion)
    try:
        from components import ui_theme as _theme

        _popup = completer.popup()
        if _popup is not None:
            _popup.setStyleSheet(
                f"QListView {{ background-color: {_theme.PANEL}; color: {_theme.INK}; "
                f"border: 1px solid {_theme.LINE_STRONG}; outline: 0; padding: 2px; }}"
                f"QListView::item {{ padding: 6px 10px; min-height: 24px; }}"
                f"QListView::item:selected {{ background-color: {_theme.ACCENT_SOFT}; "
                f"color: {_theme.INK}; }}"
            )
    except Exception:
        pass

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
    elif isinstance(widget, QComboBox):
        # 单相/三相这种不可编辑下拉：改选项就记住，重启才不会回到第一项。
        def _remember_combo(_text: str = "", w: QWidget = widget, k: str = key) -> None:
            remember_value(k, _widget_text(w))

        try:
            widget.currentTextChanged.connect(_remember_combo)
        except Exception:
            widget.currentIndexChanged.connect(
                lambda _i, w=widget, k=key: remember_value(k, _widget_text(w))
            )
        widget._field_memory_enabled = True  # type: ignore
        return
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
        try:
            from components import ui_theme as _theme

            menu.setStyleSheet(
                f"QMenu {{ background-color: {_theme.PANEL}; color: {_theme.INK}; "
                f"border: 1px solid {_theme.LINE_STRONG}; padding: 4px; }}"
                f"QMenu::item {{ padding: 8px 16px; color: {_theme.INK}; }}"
                f"QMenu::item:selected {{ background-color: {_theme.ACCENT_SOFT}; "
                f"color: {_theme.INK}; }}"
            )
        except Exception:
            pass
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


def _fit_compact_input(widget: QWidget) -> None:
    """Grow fixed single-line editors with ui_scale; never crush tall multi-line boxes.

    WT FileNameList / similar (design max height > 56) must be skipped — earlier
    polish forced them to 100×40 and clipped path/filename text.
    """
    try:
        from components import ui_theme as theme
    except Exception:
        return
    if isinstance(widget, QTextEdit) and widget.isReadOnly():
        return

    design_max = widget.property("_ui_design_max_h")
    max_h = int(widget.maximumHeight())
    min_h = int(widget.minimumHeight())
    # Tall editors (filename list, notes): leave layout-managed size alone
    if design_max not in (None, "") and int(design_max) > 56:
        try:
            if isinstance(widget, QTextEdit) and widget.document() is not None:
                widget.document().setDocumentMargin(2)
        except Exception:
            pass
        return
    if 56 < max_h < 16_000_000:
        return

    fixed_square = min_h > 0 and max_h > 0 and min_h == max_h and min_h <= 72
    compact = fixed_square or (0 < max_h <= 56)
    if not compact:
        return

    scale = float(theme.ui_scale() or 1.0)

    # Prefer props from _make_te / dialog builders
    if widget.property("_ui_design_max_h") in (None, ""):
        oh = min_h if fixed_square else 40
        widget.setProperty("_ui_design_min_h", max(int(oh), 40))
        widget.setProperty("_ui_design_max_h", max(int(oh), 40))
    if (
        widget.property("_ui_design_w") in (None, "")
        and widget.minimumWidth() == widget.maximumWidth() > 0
        and widget.minimumWidth() <= 420
    ):
        widget.setProperty("_ui_design_w", max(int(widget.minimumWidth()), 100))

    hh = max(36, int(round(int(widget.property("_ui_design_max_h")) * scale)))
    # Ensure room for font + padding + frame
    try:
        fm = widget.fontMetrics()
        hh = max(hh, int(fm.height()) + 18)
    except Exception:
        pass

    design_ss = (
        f"QTextEdit {{ color: {theme.INK}; background-color: {theme.PANEL}; "
        f"border: 1px solid {theme.LINE_STRONG}; border-radius: 6px; "
        f"padding: 4px 8px; }}"
        if isinstance(widget, QTextEdit)
        else (
            f"QLineEdit {{ color: {theme.INK}; background-color: {theme.PANEL}; "
            f"border: 1px solid {theme.LINE_STRONG}; border-radius: 6px; "
            f"padding: 4px 8px; }}"
        )
    )
    widget.setProperty("_ui_ss_orig", design_ss)
    try:
        from utils.ui_scale import scale_qss_metrics

        widget.setStyleSheet(scale_qss_metrics(design_ss, scale))
    except Exception:
        widget.setStyleSheet(design_ss)

    if isinstance(widget, QTextEdit):
        widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        try:
            widget.setTabChangesFocus(True)
        except Exception:
            pass
        try:
            if widget.document() is not None:
                widget.document().setDocumentMargin(2)
        except Exception:
            pass

    dw = widget.property("_ui_design_w")
    dmin_w = widget.property("_ui_design_min_w")
    if dw not in (None, ""):
        ww = max(48, int(round(int(dw) * scale)))
        widget.setFixedSize(ww, hh)
    elif dmin_w not in (None, ""):
        # Expanding path fields: lock height only, keep min width
        widget.setMinimumWidth(max(48, int(round(int(dmin_w) * scale))))
        widget.setMaximumWidth(16777215)
        widget.setMinimumHeight(hh)
        widget.setMaximumHeight(hh)
    else:
        ww = max(48, int(round(100 * scale)))
        widget.setFixedSize(ww, hh)


def polish_input_widgets(
    root: QWidget, *, with_memory: bool = True, memory_scope: str = "device"
) -> int:
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
        _fit_compact_input(w)
        # Fixed-width combos (开启/关闭、秒/分) also need to track design width
        if isinstance(w, QComboBox):
            try:
                from components import ui_theme as theme

                min_w, max_w = int(w.minimumWidth()), int(w.maximumWidth())
                if min_w > 0 and max_w > 0 and min_w == max_w and min_w <= 420:
                    if w.property("_ui_design_w") in (None, ""):
                        w.setProperty("_ui_design_w", max(min_w, 100))
                        w.setProperty("_ui_design_captured", True)
                    tw = max(40, int(round(int(w.property("_ui_design_w")) * float(theme.ui_scale() or 1.0))))
                    w.setFixedWidth(tw)
            except Exception:
                pass
        if with_memory and history_key_for_object_name(obj, memory_scope=memory_scope):
            enable_field_memory(w, memory_scope=memory_scope)
            attach_history_dropdown_button(w)
            n += 1
        elif isinstance(w, QTextEdit) and w.maximumHeight() <= 64:
            # 单行高的试验输入框：至少 Tab 跳转
            n += 1
    return n
