from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QGridLayout, QScrollArea)
from components.buttons import apply_button_style

# ── 样式常量 ──

_BTN_QSS = """
    QPushButton { color: #1e293b; background-color: #d1d5db; border: 1px solid #9ca3af;
        border-radius: 4px; padding: 6px 14px; font-size: 13px; }
    QPushButton:hover { background-color: #bcc3ce; }
"""
_INPUT_QSS = """
    QTextEdit { color: #1e293b; background-color: #ffffff;
        border: 1px solid #d1d5db; border-radius: 4px; padding: 4px; font-size: 13px; }
    QComboBox { color: #1e293b; background-color: #ffffff;
        border: 1px solid #9ca3af; border-radius: 4px; padding: 4px 24px 4px 8px;
        font-size: 13px; }
    QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: center right;
        width: 24px; border: none; }
    QComboBox::down-arrow { image: none; border-left: 5px solid transparent;
        border-right: 5px solid transparent; border-top: 6px solid #374151; }
    QComboBox QAbstractItemView { background-color: #ffffff; color: #111827;
        border: 2px solid #3b82f6; selection-background-color: #3b82f6;
        selection-color: #ffffff; outline: none; }
    QComboBox QAbstractItemView::item { padding: 6px 12px; min-height: 28px;
        border-bottom: 1px solid #e5e7eb; }
"""
_CONNECT_BTN_QSS = """
    QPushButton { color: #1e293b; background-color: #d1d5db; border: 1px solid #9ca3af;
        border-radius: 4px; padding: 6px 14px; font-size: 13px; }
    QPushButton:hover { background-color: #bcc3ce; }
"""
_LABEL_QSS = "color: #1e293b; font-size: 13px; background: transparent;"

_LOG_QSS = (
    "QTextEdit { background-color: #1e293b; color: #a0aec0; "
    "border: 1px solid #4a5568; border-radius: 4px; "
    "font-family: Consolas; font-size: 12px; padding: 4px; }"
)


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
        dot_r = 5
        cx = 14
        if not self._is_last:
            p.setPen(QPen(QColor('#b0b8c4'), 2))
            p.drawLine(cx, dot_r * 2 + 4, cx, self.height())
        p.setBrush(QBrush(QColor('#10b981')))
        p.setPen(Qt.NoPen)
        p.drawEllipse(cx - dot_r, 6, dot_r * 2, dot_r * 2)


class _TimelineStep(QWidget):
    """一个步骤：左列(圆点+线) + 右列(标题+内容)。"""

    def __init__(self, title, content_widget, is_last=False, stretch=False, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 16)
        outer.setSpacing(0)

        self._dot = _TimelineDot(is_last)
        outer.addWidget(self._dot)

        right = QWidget()
        right.setStyleSheet("background: transparent;")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(8, 4, 0, 0)
        right_lay.setSpacing(4)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #1e293b; background: transparent;"
        )
        right_lay.addWidget(title_lbl)
        right_lay.addWidget(content_widget, 1 if stretch else 0)

        outer.addWidget(right, 1)


# ── 公开 API ──

class TimelineWidget(QWidget):
    """垂直时间线容器，包含多个步骤。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
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
    if cls == 'QPushButton':
        w.setStyleSheet(_BTN_QSS)
        w.setCursor(QtCore.Qt.PointingHandCursor)
    elif cls in ('QTextEdit', 'QComboBox', 'QLineEdit'):
        w.setStyleSheet(_INPUT_QSS)
    elif cls == 'QLabel':
        w.setStyleSheet(_LABEL_QSS)


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
    lay.setSpacing(8)
    for item in fields:
        lbl_text = item[0]
        widget = item[1]
        unit_text = item[2] if len(item) > 2 else None
        lbl = QLabel(lbl_text)
        lbl.setStyleSheet(_LABEL_QSS)
        lay.addWidget(lbl)
        _style_widget(widget)
        if type(widget).__name__ == 'QTextEdit':
            widget.setMaximumHeight(36)
        lay.addWidget(widget)
        if unit_text:
            ulbl = QLabel(unit_text)
            ulbl.setStyleSheet(_LABEL_QSS)
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
            interfaceLabel = QLabel("接口:")
            interfaceLabel.setStyleSheet(_LABEL_QSS)
            content_lay.addWidget(interfaceLabel)
            combo.setStyleSheet(_INPUT_QSS)
            content_lay.addWidget(combo, 1)
            connectBtn.setStyleSheet(_CONNECT_BTN_QSS)
            connectBtn.setCursor(Qt.PointingHandCursor)
            content_lay.addWidget(connectBtn)
            if widgets_spec == "__connect__":
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
                    if type(w).__name__ == 'QTextEdit':
                        w.setMaximumHeight(36)
                    content_lay.addWidget(w)
            if not has_log:
                content_lay.addStretch(1)

        is_log = (widgets_spec in ("__log__", "__log_widget__") or
                  (isinstance(widgets_spec, list) and "__log__" in widgets_spec))
        timeline.addStep(title, content, stretch=is_log)

    # 按钮样式
    if btn_styles:
        for obj_name, btn_style in btn_styles.items():
            btn = all_widgets.get(obj_name)
            if btn is not None:
                apply_button_style(btn, btn_style)

    timeline.finalize()
    return timeline
