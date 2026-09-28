from PyQt5 import QtWidgets, QtCore, QtGui

from components import ui_theme as theme


class ButtonStyle:
    DEFAULT = "default"
    PRIMARY = "primary"
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"


_STYLES = {
    ButtonStyle.DEFAULT: {
        "normal_bg": theme.PANEL,
        "normal_border": theme.LINE_STRONG,
        "normal_color": theme.INK,
        "hover_bg": theme.NEUTRAL,
        "hover_border": theme.MUTED,
        "pressed_bg": theme.NEUTRAL_HOVER,
    },
    ButtonStyle.PRIMARY: {
        "normal_bg": theme.ACCENT,
        "normal_border": theme.ACCENT,
        "normal_color": "#ffffff",
        "hover_bg": theme.ACCENT_HOVER,
        "hover_border": theme.ACCENT_HOVER,
        "pressed_bg": theme.ACCENT_PRESSED,
    },
    ButtonStyle.SUCCESS: {
        "normal_bg": theme.SUCCESS,
        "normal_border": theme.SUCCESS,
        "normal_color": "#ffffff",
        "hover_bg": theme.SUCCESS_HOVER,
        "hover_border": theme.SUCCESS_HOVER,
        "pressed_bg": theme.SUCCESS_HOVER,
    },
    ButtonStyle.INFO: {
        "normal_bg": "#475569",
        "normal_border": "#475569",
        "normal_color": "#ffffff",
        "hover_bg": "#334155",
        "hover_border": "#334155",
        "pressed_bg": "#1e293b",
    },
    ButtonStyle.WARNING: {
        "normal_bg": theme.WARNING,
        "normal_border": theme.WARNING,
        "normal_color": "#ffffff",
        "hover_bg": "#b45309",
        "hover_border": "#b45309",
        "pressed_bg": "#92400e",
    },
    ButtonStyle.DANGER: {
        "normal_bg": theme.DANGER,
        "normal_border": theme.DANGER,
        "normal_color": "#ffffff",
        "hover_bg": theme.DANGER_HOVER,
        "hover_border": theme.DANGER_HOVER,
        "pressed_bg": theme.DANGER_HOVER,
    },
}


def apply_button_style(button, style, font_size=14, padding="6px 16px",
                       min_width=60):
    """将预设样式应用到已有的 QPushButton 上（不替换控件，保留信号连接）。"""
    try:
        from components import ui_theme as theme

        scale = theme.ui_scale()
        font_size = max(8, int(round(font_size * scale)))
        min_width = max(40, int(round(min_width * scale)))
        # Scale "6px 16px" style paddings when given in the default form
        if padding == "6px 16px":
            padding = f"{theme.px(6)}px {theme.px(16)}px"
    except Exception:
        pass
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
        border-radius: 8px;
        padding: {padding};
        font-size: {font_size}px;
        min-width: {min_width}px;
        font-weight: 600;
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
