from PyQt5 import QtWidgets, QtCore, QtGui


class ButtonStyle:
    DEFAULT = "default"
    PRIMARY = "primary"
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"


_STYLES = {
    ButtonStyle.DEFAULT: {
        "normal_bg": "#ffffff",
        "normal_border": "#dee2e6",
        "normal_color": "#212529",
        "hover_bg": "#e9ecef",
        "hover_border": "#adb5bd",
        "pressed_bg": "#dee2e6",
    },
    ButtonStyle.PRIMARY: {
        "normal_bg": "#0d6efd",
        "normal_border": "#0d6efd",
        "normal_color": "#ffffff",
        "hover_bg": "#0b5ed7",
        "hover_border": "#0a58ca",
        "pressed_bg": "#0a58ca",
    },
    ButtonStyle.SUCCESS: {
        "normal_bg": "#198754",
        "normal_border": "#198754",
        "normal_color": "#ffffff",
        "hover_bg": "#157347",
        "hover_border": "#146c43",
        "pressed_bg": "#146c43",
    },
    ButtonStyle.INFO: {
        "normal_bg": "#6c757d",
        "normal_border": "#6c757d",
        "normal_color": "#ffffff",
        "hover_bg": "#5c636a",
        "hover_border": "#565e64",
        "pressed_bg": "#565e64",
    },
    ButtonStyle.WARNING: {
        "normal_bg": "#ffc107",
        "normal_border": "#ffc107",
        "normal_color": "#212529",
        "hover_bg": "#ffca2c",
        "hover_border": "#ffbf36",
        "pressed_bg": "#ffbf36",
    },
    ButtonStyle.DANGER: {
        "normal_bg": "#dc3545",
        "normal_border": "#dc3545",
        "normal_color": "#ffffff",
        "hover_bg": "#bb2d3b",
        "hover_border": "#b02a37",
        "pressed_bg": "#b02a37",
    },
}


def apply_button_style(button, style, font_size=14, padding="6px 16px",
                       min_width=60):
    """将预设样式应用到已有的 QPushButton 上（不替换控件，保留信号连接）。"""
    button.setStyleSheet(
        _build_qss(_STYLES[style], font_size=font_size,
                   padding=padding, min_width=min_width)
    )
    button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))


def _build_qss(s: dict, font_size: int = 14, padding: str = "6px 16px",
               min_width: int = 60) -> str:
    return f"""
    QPushButton {{
        background-color: {s['normal_bg']};
        color: {s['normal_color']};
        border: 1px solid {s['normal_border']};
        border-radius: 4px;
        padding: {padding};
        font-size: {font_size}px;
        min-width: {min_width}px;
    }}
    QPushButton:hover {{
        background-color: {s['hover_bg']};
        border-color: {s['hover_border']};
    }}
    QPushButton:pressed {{
        background-color: {s['pressed_bg']};
    }}
    QPushButton:disabled {{
        background-color: #e9ecef;
        color: #adb5bd;
        border-color: #dee2e6;
    }}
    """


class StyledButton(QtWidgets.QPushButton):
    """通用样式按钮，支持 6 种预设风格 + 自定义大小。

    Parameters
    ----------
    text : str
        按钮文字
    style : str
        预设样式，使用 ButtonStyle 常量
    icon : QIcon, optional
        图标
    width : int, optional
        固定宽度（像素）
    height : int, optional
        固定高度（像素）
    min_width : int, optional
        最小宽度，默认 60
    font_size : int, optional
        字体大小，默认 14
    padding : str, optional
        内边距，默认 "6px 16px"
    parent : QWidget, optional
        父控件
    """

    def __init__(self, text="", style=ButtonStyle.DEFAULT, icon=None,
                 width=None, height=None, min_width=60, font_size=14,
                 padding="6px 16px", parent=None):
        super().__init__(text, parent)
        self._btn_style = style
        self.setStyleSheet(
            _build_qss(_STYLES[style], font_size=font_size,
                       padding=padding, min_width=min_width)
        )
        if icon is not None:
            self.setIcon(icon)
        if width is not None:
            self.setFixedWidth(width)
        if height is not None:
            self.setFixedHeight(height)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def set_button_style(self, style: str):
        self._btn_style = style
        self.setStyleSheet(_build_qss(_STYLES[style]))
