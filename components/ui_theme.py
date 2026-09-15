# -*- coding: utf-8 -*-
"""SolarAutoTest 台架风 UI 主题（仅样式常量，不改业务逻辑）。

浅色、高对比、按钮分区明确；Dialog / 主界面 / 设备页共用同一套色板。
"""

from __future__ import annotations

# ── 色板 ──
BG = "#f1f5f9"
PANEL = "#ffffff"
SIDEBAR = "#f8fafc"
INK = "#0f172a"
MUTED = "#64748b"
LINE = "#e2e8f0"
LINE_STRONG = "#cbd5e1"
ACCENT = "#2563eb"
ACCENT_HOVER = "#1d4ed8"
ACCENT_PRESSED = "#1e40af"
ACCENT_SOFT = "#dbeafe"
ACCENT_SOFT_HOVER = "#bfdbfe"
NEUTRAL = "#e2e8f0"
NEUTRAL_HOVER = "#cbd5e1"
SUCCESS = "#059669"
SUCCESS_HOVER = "#047857"
WARNING = "#d97706"
DANGER = "#dc2626"
DANGER_HOVER = "#b91c1c"
LOG_BG = "#0f172a"
LOG_FG = "#e2e8f0"
LOG_BORDER = "#334155"


def app_shell_qss() -> str:
    return f"""
        QMainWindow {{ background-color: {BG}; }}
        QWidget#centralWidget {{ background-color: {BG}; }}
    """


def sidebar_qss() -> str:
    return f"""
        QWidget#sidebar {{
            background-color: {SIDEBAR};
            border-right: 1px solid {LINE_STRONG};
        }}
    """


def sidebar_scroll_qss() -> str:
    return f"""
        QScrollArea {{ border: none; background: {SIDEBAR}; }}
        QScrollBar:vertical {{
            background: {SIDEBAR}; width: 8px; margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {LINE_STRONG}; border-radius: 4px; min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{ background: {MUTED}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """


HEADER_STYLE = f"""
    QPushButton {{
        background-color: {NEUTRAL}; color: {INK}; border: none;
        border-bottom: 1px solid {LINE_STRONG};
        text-align: left; padding: 11px 14px;
        font-size: 12px; font-weight: bold;
    }}
    QPushButton:hover {{ background-color: {NEUTRAL_HOVER}; color: {INK}; }}
"""

SUBHEADER_STYLE = f"""
    QPushButton {{
        background-color: #eef2f7; color: {MUTED}; border: none;
        border-bottom: 1px solid {LINE};
        text-align: left; padding: 8px 10px 8px 16px;
        font-size: 11px; font-weight: bold;
    }}
    QPushButton:hover {{ background-color: {NEUTRAL}; color: {INK}; }}
"""

ITEM_STYLE = f"""
    QPushButton {{
        background-color: {SIDEBAR}; color: #334155; border: none;
        border-left: 3px solid transparent;
        text-align: left; padding: 10px 14px 10px 22px;
        font-size: 13px;
    }}
    QPushButton:hover {{ background-color: {NEUTRAL}; color: {INK}; }}
"""

ITEM_ACTIVE_STYLE = f"""
    QPushButton {{
        background-color: {ACCENT_SOFT}; color: {ACCENT_HOVER}; border: none;
        border-left: 3px solid {ACCENT};
        text-align: left; padding: 10px 14px 10px 22px;
        font-size: 13px; font-weight: bold;
    }}
    QPushButton:hover {{ background-color: {ACCENT_SOFT_HOVER}; color: {ACCENT_PRESSED}; }}
"""

NESTED_ITEM_STYLE = f"""
    QPushButton {{
        background-color: {SIDEBAR}; color: #334155; border: none;
        border-left: 3px solid transparent;
        text-align: left; padding: 8px 12px 8px 30px;
        font-size: 12px;
    }}
    QPushButton:hover {{ background-color: {NEUTRAL}; color: {INK}; }}
"""

NESTED_ITEM_ACTIVE_STYLE = f"""
    QPushButton {{
        background-color: {ACCENT_SOFT}; color: {ACCENT_HOVER}; border: none;
        border-left: 3px solid {ACCENT};
        text-align: left; padding: 8px 12px 8px 30px;
        font-size: 12px; font-weight: bold;
    }}
    QPushButton:hover {{ background-color: {ACCENT_SOFT_HOVER}; color: {ACCENT_PRESSED}; }}
"""

PAGE_STYLE = f"""
    QWidget {{ background-color: {BG}; }}
    QLabel {{ color: #334155; font-size: 13px; background: transparent; }}
    QPushButton {{
        background-color: {ACCENT}; color: white; border: none;
        border-radius: 6px; padding: 8px 16px; font-size: 13px; font-weight: bold;
    }}
    QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
    QPushButton:pressed {{ background-color: {ACCENT_PRESSED}; }}
    QPushButton:disabled {{ background-color: #94a3b8; color: {NEUTRAL}; }}
    QComboBox {{
        background-color: {PANEL}; border: 1px solid #94a3b8; border-radius: 4px;
        padding: 4px 24px 4px 8px; font-size: 13px; color: {INK};
    }}
    QComboBox:hover {{ border-color: {ACCENT}; }}
    QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: center right;
        width: 24px; border: none; }}
    QComboBox::down-arrow {{ image: none; border-left: 5px solid transparent;
        border-right: 5px solid transparent; border-top: 6px solid #334155; }}
    QComboBox QAbstractItemView {{
        background-color: {PANEL}; color: #111827;
        border: 2px solid {ACCENT}; selection-background-color: {ACCENT};
        selection-color: #ffffff; outline: none;
    }}
    QComboBox QAbstractItemView::item {{ padding: 6px 12px; min-height: 28px;
        border-bottom: 1px solid {LINE}; }}
"""

CARD_STYLE = f"""
    QWidget#card {{
        background-color: {PANEL}; border: 1px solid {LINE_STRONG};
        border-radius: 10px; padding: 16px;
    }}
"""

LOG_STYLE = f"""
    QTextEdit {{
        background-color: {LOG_BG}; color: {LOG_FG};
        border: 1px solid {LOG_BORDER}; border-radius: 6px;
        font-family: Consolas, monospace; font-size: 12px; padding: 8px;
    }}
"""

BTN_QSS = f"""
    QPushButton {{ color: {INK}; background-color: {NEUTRAL}; border: 1px solid #94a3b8;
        border-radius: 4px; padding: 6px 14px; font-size: 13px; }}
    QPushButton:hover {{ background-color: {NEUTRAL_HOVER}; }}
"""

INPUT_QSS = f"""
    QTextEdit {{ color: {INK}; background-color: {PANEL};
        border: 1px solid #94a3b8; border-radius: 4px; padding: 4px; font-size: 13px; }}
    QLineEdit {{ color: {INK}; background-color: {PANEL};
        border: 1px solid #94a3b8; border-radius: 4px; padding: 4px 8px; font-size: 13px; }}
    QComboBox {{ color: {INK}; background-color: {PANEL};
        border: 1px solid #94a3b8; border-radius: 4px; padding: 4px 24px 4px 8px;
        font-size: 13px; }}
    QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: center right;
        width: 24px; border: none; }}
    QComboBox::down-arrow {{ image: none; border-left: 5px solid transparent;
        border-right: 5px solid transparent; border-top: 6px solid #334155; }}
    QComboBox QAbstractItemView {{ background-color: {PANEL}; color: #111827;
        border: 2px solid {ACCENT}; selection-background-color: {ACCENT};
        selection-color: #ffffff; outline: none; }}
    QComboBox QAbstractItemView::item {{ padding: 6px 12px; min-height: 28px;
        border-bottom: 1px solid {LINE}; }}
"""

CONNECT_BTN_QSS = f"""
    QPushButton {{ color: #ffffff; background-color: {ACCENT}; border: 1px solid {ACCENT_HOVER};
        border-radius: 4px; padding: 6px 14px; font-size: 13px; font-weight: bold; }}
    QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
    QPushButton:pressed {{ background-color: {ACCENT_PRESSED}; }}
"""

LABEL_QSS = f"color: {INK}; font-size: 13px; background: transparent;"

LOG_QSS = (
    f"QTextEdit {{ background-color: {LOG_BG}; color: #94a3b8; "
    f"border: 1px solid {LOG_BORDER}; border-radius: 4px; "
    f"font-family: Consolas; font-size: 12px; padding: 4px; }}"
)

# 试验对话框顶栏 / 主操作
DIALOG_TOPBAR_QSS = (
    f"QWidget {{ background-color: {SIDEBAR}; border-bottom: 1px solid {LINE}; }}"
)

DIALOG_APPEND_BTN_QSS = f"""
    QPushButton {{ background-color: {ACCENT}; color: white; border: none; border-radius: 4px;
                  padding: 6px 14px; font-size: 12px; font-weight: bold; }}
    QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
"""

DIALOG_SECONDARY_BTN_QSS = f"""
    QPushButton {{ background-color: {SUCCESS}; color: white; border: none; border-radius: 4px;
                  padding: 6px 14px; font-size: 12px; }}
    QPushButton:hover {{ background-color: {SUCCESS_HOVER}; }}
"""

DIALOG_NEUTRAL_BTN_QSS = f"""
    QPushButton {{ background-color: #475569; color: white; border: none; border-radius: 4px;
                  padding: 6px 14px; font-size: 12px; }}
    QPushButton:hover {{ background-color: #334155; }}
"""

DIALOG_DANGER_BTN_QSS = f"""
    QPushButton {{ background-color: {DANGER}; color: white; border: none; border-radius: 4px;
                  padding: 6px 14px; font-size: 12px; }}
    QPushButton:hover {{ background-color: {DANGER_HOVER}; }}
"""

DIALOG_GROUPBOX_QSS = (
    f"QGroupBox {{ border: 1px solid {LINE}; border-radius: 6px; "
    f"padding-top: 10px; margin-top: 6px; font-weight: bold; color: {INK}; "
    f"background-color: {PANEL}; }}"
    f"QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; }}"
)


def step_label_inactive_qss() -> str:
    return f"""
        QLabel {{
            padding: 6px 12px; font-size: 12px; color: {MUTED};
            border-bottom: 3px solid transparent; border-radius: 0;
            background: transparent;
        }}
        QLabel:hover {{ background-color: {NEUTRAL}; }}
    """


def step_label_active_qss() -> str:
    return f"""
        QLabel {{
            padding: 6px 12px; font-size: 12px; font-weight: bold; color: {ACCENT_HOVER};
            border-bottom: 3px solid {ACCENT}; border-radius: 0;
            background-color: {ACCENT_SOFT};
        }}
    """
