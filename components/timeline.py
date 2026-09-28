# -*- coding: utf-8 -*-
"""Vertical step timeline used by device setup pages (AC/DC/WT/…)."""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
)
from components.buttons import apply_button_style
from components import ui_theme as theme

# ── 样式常量（与全局主题对齐；保留 _ 前缀供 SCPITestWave / 抓图脚本导入）──

_BTN_QSS = theme.BTN_QSS
_INPUT_QSS = theme.INPUT_QSS
_CONNECT_BTN_QSS = theme.CONNECT_BTN_QSS
_LABEL_QSS = theme.LABEL_QSS
_LOG_QSS = theme.LOG_QSS

_LABEL_QSS_LOCAL = (
    f"color: {theme.INK}; font-size: 13px; font-weight: 500; background: transparent;"
)
_STEP_TITLE_QSS = (
    f"font-size: 13px; font-weight: 600; color: {theme.INK}; background: transparent;"
)
_STEP_CARD_QSS = f"""
    QWidget#timelineStepCard {{
        background-color: {theme.PANEL};
        border: 1px solid {theme.LINE};
        border-radius: 12px;
    }}
"""
_DOT_COLOR = theme.ACCENT
_LINE_COLOR = "#cbd5e1"


# ── 内部 widget ──

class _TimelineDot(QWidget):
    """左侧圆点 + 竖线，由 paintEvent 绘制。"""

    def __init__(self, is_last=False, parent=None):
        super().__init__(parent)
        self._is_last = is_last
        self.setFixedWidth(28)
        self.setStyleSheet("background: transparent;")

    def set_last(self, v):
        self._is_last = v
        self.update()

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
        from PyQt5.QtCore import Qt

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        dot_r = 6
        cx = 14
        if not self._is_last:
            p.setPen(QPen(QColor(_LINE_COLOR), 2))
            p.drawLine(cx, dot_r * 2 + 6, cx, self.height())
        # soft outer ring
        p.setBrush(QBrush(QColor(theme.ACCENT_SOFT)))
        p.setPen(Qt.NoPen)
        p.drawEllipse(cx - dot_r - 3, 4, (dot_r + 3) * 2, (dot_r + 3) * 2)
        p.setBrush(QBrush(QColor(_DOT_COLOR)))
        p.drawEllipse(cx - dot_r, 7, dot_r * 2, dot_r * 2)


class _TimelineStep(QWidget):
    """一个步骤：左列(圆点+线) + 右列卡片(标题+内容)。"""

    def __init__(self, title, content_widget, is_last=False, stretch=False, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 12)
        outer.setSpacing(0)

        self._dot = _TimelineDot(is_last)
        outer.addWidget(self._dot)

        card = QWidget()
        card.setObjectName("timelineStepCard")
        card.setStyleSheet(_STEP_CARD_QSS)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(14, 12, 14, 12)
        card_lay.setSpacing(8)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(_STEP_TITLE_QSS)
        card_lay.addWidget(title_lbl)
        card_lay.addWidget(content_widget, 1 if stretch else 0)

        outer.addWidget(card, 1)


# ── 公开 API ──

class TimelineWidget(QWidget):
    """垂直时间线容器，包含多个步骤。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 4, 0, 4)
        self._lay.setSpacing(0)
        self._steps = []

    def addStep(self, title, content_widget, stretch=False):
        step = _TimelineStep(title, content_widget, is_last=False, stretch=stretch)
        self._steps.append(step)
        self._lay.addWidget(step, 1 if stretch else 0)

    def finalize(self):
        if self._steps:
            self._steps[-1]._dot.set_last(True)


def _style_widget(w):
    """对单个控件应用标准 QSS 样式。"""
    from PyQt5 import QtCore

    cls = type(w).__name__
    if cls == "QPushButton":
        w.setStyleSheet(_BTN_QSS)
        w.setCursor(QtCore.Qt.PointingHandCursor)
    elif cls in ("QTextEdit", "QComboBox", "QLineEdit"):
        w.setStyleSheet(_INPUT_QSS)
        if cls == "QLineEdit":
            w.setMinimumHeight(theme.px(32))
            w.setMinimumWidth(theme.px(72))
        elif cls == "QComboBox":
            w.setMinimumHeight(theme.px(32))
            w.setMinimumWidth(theme.px(100))
        elif cls == "QTextEdit":
            w.setMinimumHeight(theme.px(32))
            w.setMaximumHeight(theme.px(36))
            w.setMinimumWidth(theme.px(72))
    elif cls == "QLabel":
        w.setStyleSheet(_LABEL_QSS_LOCAL)


def _is_unit_field(name: str, w) -> bool:
    """「%」「V」等单位框，禁止拉宽。"""
    n = (name or "").lower()
    if n in ("lineedit_2", "lineedit_unit", "lineedit_percent"):
        return True
    cls = type(w).__name__
    if cls == "QLineEdit":
        t = (w.text() or "").strip()
        if t in ("%", "V", "A", "Hz", "W", "kW", "var", "°", "s", "ms"):
            return True
        if w.isReadOnly() and len(t) <= 3:
            return True
    return False


def _should_expand_field(name: str, w) -> bool:
    """仅长命令/地址可略宽；端口下拉与按钮绝不拉满整行。"""
    if _is_unit_field(name, w):
        return False
    n = name or ""
    compact_keys = (
        "Vmp", "Voc", "Imp", "Isc", "_PF", "textEdit_PF",
        "_VOLT", "_CURR", "_FR", "BaudRate",
        "comboBox_AC", "comboBox_DC", "comboBox_DL", "comboBox_WT",
        "comboBox_DEW", "comboBox_Baud",
    )
    if any(k in n for k in compact_keys):
        return False
    expand_keys = (
        "SendMessage", "SendQuery", "lineEdit_WT",
        "Address", "Host", "textEdit_SavePath", "FileNameList",
    )
    if any(k in n for k in expand_keys):
        return True
    if n in ("lineEdit", "lineEdit_cmd") or n.startswith("lineEdit_Send"):
        return True
    return False


def param_row(fields):
    """构建参数行：label + widget [+ unit] 的水平排列。

    Parameters
    ----------
    fields : list[tuple]
        每项为 (label_text, widget) 或 (label_text, widget, unit_text)。

    Returns
    -------
    QWidget
        包含所有字段的水平布局 widget。
    """
    row = QWidget()
    row.setStyleSheet("background: transparent;")
    lay = QHBoxLayout(row)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(10)
    for item in fields:
        lbl_text = item[0]
        widget = item[1]
        unit_text = item[2] if len(item) > 2 else None
        lbl = QLabel(lbl_text)
        lbl.setStyleSheet(_LABEL_QSS_LOCAL)
        lbl.setMinimumWidth(40)
        lay.addWidget(lbl)
        _style_widget(widget)
        if type(widget).__name__ == "QTextEdit":
            widget.setMaximumHeight(36)
            widget.setMaximumWidth(theme.px(120))
            widget.setMinimumWidth(theme.px(80))
        lay.addWidget(widget)
        if unit_text:
            ulbl = QLabel(unit_text)
            ulbl.setStyleSheet(
                f"color: {theme.MUTED}; font-size: 12px; font-weight: 500; background: transparent;"
            )
            lay.addWidget(ulbl)
    lay.addStretch(1)
    return row


def build_timeline(
    layout_spec,
    all_widgets,
    *,
    connect_widgets=None,
    log_widget=None,
    log_widget_name=None,
    btn_styles=None,
):
    """根据布局规格构建完整的 TimelineWidget。

    Parameters
    ----------
    layout_spec : list[dict]
        每个 dict 含 "title" (str) 和 "widgets" (str 或 list[str])。
        特殊值："__connect_clean__"、"__connect__"、"__log__"、"__log_widget__"。
    all_widgets : dict
        objectName -> QWidget 映射（dialog 的直接子控件）。
    connect_widgets : tuple, optional
        (combo, connectBtn, setBtn)，__connect__ 标记需要。
    log_widget : QWidget, optional
        日志 QTextEdit，__log__ 标记需要（AC 专用）。
    log_widget_name : str, optional
        日志控件的 objectName，__log_widget__ 标记需要（DC/DL850 通用）。
    btn_styles : dict, optional
        {objectName: ButtonStyle}，构建完成后原地改样式。

    Returns
    -------
    TimelineWidget
    """
    from PyQt5.QtCore import Qt

    timeline = TimelineWidget()

    # 预解析 __log_widget__ 引用的控件
    _log_widget_ref = None
    if log_widget_name:
        _log_widget_ref = all_widgets.get(log_widget_name)
        if _log_widget_ref is not None:
            _log_widget_ref.setReadOnly(True)
            _log_widget_ref.setStyleSheet(_LOG_QSS)

    for section in layout_spec:
        title = section["title"]
        widgets_spec = section["widgets"]

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_lay = QHBoxLayout(content)
        content_lay.setContentsMargins(0, 0, 0, 0)
        content_lay.setSpacing(10)

        if widgets_spec in ("__connect__", "__connect_clean__") and connect_widgets is not None:
            combo, connectBtn, setBtn = connect_widgets
            interfaceLabel = QLabel("接口")
            interfaceLabel.setObjectName("timelineConnectIfaceLabel")
            interfaceLabel.setStyleSheet(_LABEL_QSS_LOCAL)
            content_lay.addWidget(interfaceLabel)
            combo.setStyleSheet(_INPUT_QSS)
            combo.setMinimumHeight(32)
            combo.setMinimumWidth(160)
            combo.setMaximumWidth(360)
            combo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            content_lay.addWidget(combo)
            content_lay.addStretch(1)
            connectBtn.setStyleSheet(_CONNECT_BTN_QSS)
            connectBtn.setCursor(Qt.PointingHandCursor)
            connectBtn.setMinimumHeight(32)
            try:
                connectBtn.setMinimumWidth(
                    max(int(connectBtn.minimumWidth() or 0), int(connectBtn.sizeHint().width()) + 20)
                )
            except Exception:
                connectBtn.setMinimumWidth(108)
            connectBtn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            content_lay.addWidget(connectBtn)
            if widgets_spec == "__connect__":
                if setBtn is not None:
                    try:
                        setBtn.setMinimumWidth(
                            max(int(setBtn.minimumWidth() or 0), int(setBtn.sizeHint().width()) + 16)
                        )
                    except Exception:
                        pass
                    setBtn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
                content_lay.addWidget(setBtn)
        elif widgets_spec == "__log__":
            content_lay.addWidget(log_widget, 1)
        elif widgets_spec == "__log_widget__":
            if _log_widget_ref is not None:
                content_lay.addWidget(_log_widget_ref, 1)
        else:
            has_log = isinstance(widgets_spec, list) and "__log__" in widgets_spec
            for name in widgets_spec:
                if name == "__log__":
                    if log_widget is not None:
                        content_lay.addWidget(log_widget, 1)
                    continue
                w = all_widgets.get(name)
                if w is not None and w is not log_widget and w is not _log_widget_ref:
                    _style_widget(w)
                    cls = type(w).__name__
                    if cls == "QTextEdit":
                        w.setMaximumHeight(theme.px(36))
                    if cls == "QPushButton":
                        w.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
                        content_lay.addWidget(w)
                    elif _is_unit_field(name, w):
                        try:
                            w.setReadOnly(True)
                        except Exception:
                            pass
                        w.setFixedWidth(theme.px(28))
                        w.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                        content_lay.addWidget(w)
                    elif _should_expand_field(name, w):
                        # 命令框可宽一点，但有上限，避免整行被撑满
                        w.setMinimumWidth(theme.px(120))
                        w.setMaximumWidth(theme.px(420))
                        w.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
                        content_lay.addWidget(w)
                    elif cls in ("QTextEdit", "QLineEdit", "QComboBox"):
                        w.setMaximumWidth(theme.px(160))
                        w.setMinimumWidth(theme.px(72))
                        w.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
                        content_lay.addWidget(w)
                    else:
                        content_lay.addWidget(w)
            if not has_log:
                content_lay.addStretch(1)

        is_log = widgets_spec in ("__log__", "__log_widget__") or (
            isinstance(widgets_spec, list) and "__log__" in widgets_spec
        )
        timeline.addStep(title, content, stretch=is_log)

    # 按钮样式
    if btn_styles:
        for obj_name, btn_style in btn_styles.items():
            btn = all_widgets.get(obj_name)
            if btn is not None:
                apply_button_style(btn, btn_style)

    timeline.finalize()
    return timeline
