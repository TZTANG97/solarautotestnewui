# -*- coding: utf-8 -*-
"""SolarAutoTest UI theme — lab console look (shared by shell + dialogs).

Light content + dark nav; high contrast; no business logic here.
"""

from __future__ import annotations

from typing import Optional

from PyQt5 import QtGui, QtWidgets

# ── Palette ──
BG = "#f4f6f9"
PANEL = "#ffffff"
SIDEBAR = "#0f172a"
SIDEBAR_ELEVATED = "#1e293b"
INK = "#0f172a"
MUTED = "#64748b"
LINE = "#e2e8f0"
LINE_STRONG = "#cbd5e1"
ACCENT = "#0d9488"
ACCENT_HOVER = "#0f766e"
ACCENT_PRESSED = "#115e59"
ACCENT_SOFT = "#ccfbf1"
ACCENT_SOFT_HOVER = "#99f6e4"
NEUTRAL = "#e2e8f0"
NEUTRAL_HOVER = "#cbd5e1"
SUCCESS = "#059669"
SUCCESS_HOVER = "#047857"
WARNING = "#d97706"
DANGER = "#dc2626"
DANGER_HOVER = "#b91c1c"
LOG_BG = "#0b1220"
LOG_FG = "#e2e8f0"
LOG_BORDER = "#1e293b"
NAV_TEXT = "#f1f5f9"
NAV_MUTED = "#cbd5e1"

# ── UI scale (window size → font / padding). Design canvas 1600×900. ──
_UI_SCALE = 1.0


def ui_scale() -> float:
    return _UI_SCALE


def px(n: float, scale: Optional[float] = None) -> int:
    """Scale a design-pixel value; minimum 1."""
    s = _UI_SCALE if scale is None else float(scale)
    return max(1, int(round(float(n) * s)))


def set_ui_scale(scale: float) -> float:
    """Keep design scale 1.0 — do not grow fonts/padding with the window."""
    global _UI_SCALE
    _UI_SCALE = 1.0
    _rebuild_style_exports()
    return _UI_SCALE


def app_shell_qss() -> str:
    return f"""
        QMainWindow {{ background-color: {BG}; }}
        QWidget#centralWidget {{ background-color: {BG}; }}
    """


def sidebar_qss() -> str:
    return f"""
        QWidget#sidebar {{
            background-color: {SIDEBAR};
            border-right: 1px solid {SIDEBAR_ELEVATED};
        }}
    """


def sidebar_scroll_qss() -> str:
    sw = px(8)
    return f"""
        QScrollArea {{ border: none; background: {SIDEBAR}; }}
        QScrollBar:vertical {{
            background: {SIDEBAR}; width: {sw}px; margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: #334155; border-radius: {px(4)}px; min-height: {px(30)}px;
        }}
        QScrollBar::handle:vertical:hover {{ background: #475569; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """


def _rebuild_style_exports() -> None:
    """Rebuild module-level QSS aliases used across shell / timeline / dialogs."""
    global HEADER_STYLE, SUBHEADER_STYLE, ITEM_STYLE, ITEM_ACTIVE_STYLE
    global NESTED_ITEM_STYLE, NESTED_ITEM_ACTIVE_STYLE, PAGE_STYLE, CARD_STYLE
    global LOG_STYLE, BTN_QSS, INPUT_QSS, CONNECT_BTN_QSS, LABEL_QSS, LOG_QSS
    global DIALOG_TOPBAR_QSS, DIALOG_APPEND_BTN_QSS, DIALOG_SECONDARY_BTN_QSS
    global DIALOG_NEUTRAL_BTN_QSS, DIALOG_DANGER_BTN_QSS, DIALOG_GROUPBOX_QSS

    HEADER_STYLE = f"""
    QPushButton {{
        background-color: {SIDEBAR_ELEVATED}; color: {NAV_MUTED}; border: none;
        border-bottom: 1px solid #1e293b;
        text-align: left; padding: {px(12)}px {px(14)}px;
        font-size: {px(13)}px; font-weight: 700; letter-spacing: 0.4px;
    }}
    QPushButton:hover {{ background-color: #243044; color: #f8fafc; }}
"""
    SUBHEADER_STYLE = f"""
    QPushButton {{
        background-color: #152033; color: {NAV_MUTED}; border: none;
        border-bottom: 1px solid #1e293b;
        text-align: left; padding: {px(8)}px {px(10)}px {px(8)}px {px(16)}px;
        font-size: {px(12)}px; font-weight: 700;
    }}
    QPushButton:hover {{ background-color: #1e293b; color: #f8fafc; }}
"""
    ITEM_STYLE = f"""
    QPushButton {{
        background-color: {SIDEBAR}; color: {NAV_TEXT}; border: none;
        border-left: 3px solid transparent;
        text-align: left; padding: {px(10)}px {px(14)}px {px(10)}px {px(22)}px;
        font-size: {px(13)}px;
    }}
    QPushButton:hover {{ background-color: {SIDEBAR_ELEVATED}; color: #ffffff; }}
"""
    ITEM_ACTIVE_STYLE = f"""
    QPushButton {{
        background-color: #134e4a; color: #99f6e4; border: none;
        border-left: 3px solid {ACCENT};
        text-align: left; padding: {px(10)}px {px(14)}px {px(10)}px {px(22)}px;
        font-size: {px(13)}px; font-weight: 700;
    }}
    QPushButton:hover {{ background-color: #115e59; color: #ccfbf1; }}
"""
    NESTED_ITEM_STYLE = f"""
    QPushButton {{
        background-color: {SIDEBAR}; color: {NAV_TEXT}; border: none;
        border-left: 3px solid transparent;
        text-align: left; padding: {px(8)}px {px(12)}px {px(8)}px {px(30)}px;
        font-size: {px(12)}px;
    }}
    QPushButton:hover {{ background-color: {SIDEBAR_ELEVATED}; color: #ffffff; }}
"""
    NESTED_ITEM_ACTIVE_STYLE = f"""
    QPushButton {{
        background-color: #134e4a; color: #99f6e4; border: none;
        border-left: 3px solid {ACCENT};
        text-align: left; padding: {px(8)}px {px(12)}px {px(8)}px {px(30)}px;
        font-size: {px(12)}px; font-weight: 700;
    }}
    QPushButton:hover {{ background-color: #115e59; color: #ccfbf1; }}
"""
    PAGE_STYLE = f"""
    QWidget {{ background-color: {BG}; }}
    QLabel {{ color: #334155; background: transparent; }}
    QPushButton {{
        background-color: {ACCENT}; color: white; border: none;
        border-radius: {px(8)}px; padding: {px(8)}px {px(16)}px;
        font-weight: 700;
    }}
    QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
    QPushButton:pressed {{ background-color: {ACCENT_PRESSED}; }}
    QPushButton:disabled {{ background-color: #94a3b8; color: {NEUTRAL}; }}
    QComboBox {{
        background-color: {PANEL}; border: 1px solid {LINE_STRONG};
        border-radius: {px(8)}px;
        padding: {px(6)}px {px(28)}px {px(6)}px {px(10)}px;
        color: {INK};
        min-height: {px(28)}px;
    }}
    QComboBox:hover {{ border-color: {ACCENT}; }}
    QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: center right;
        width: {px(24)}px; border: none; }}
    QComboBox::down-arrow {{ image: none; border-left: 5px solid transparent;
        border-right: 5px solid transparent; border-top: 6px solid #334155; }}
    QComboBox QAbstractItemView {{
        background-color: {PANEL}; color: #111827;
        border: 1px solid {LINE_STRONG}; selection-background-color: {ACCENT};
        selection-color: #ffffff; outline: none;
    }}
    QComboBox QAbstractItemView::item {{ padding: {px(8)}px {px(12)}px;
        min-height: {px(28)}px; border-bottom: 1px solid {LINE}; }}
"""
    CARD_STYLE = f"""
    QWidget#card, QWidget#deviceCard {{
        background-color: {PANEL}; border: 1px solid {LINE};
        border-radius: {px(12)}px;
    }}
    QWidget#deviceCard:hover {{
        border-color: {ACCENT}; background-color: #f0fdfa;
    }}
"""
    LOG_STYLE = f"""
    QTextEdit {{
        background-color: {LOG_BG}; color: {LOG_FG};
        border: 1px solid {LOG_BORDER}; border-radius: {px(10)}px;
        font-family: Consolas, "Cascadia Mono", monospace;
        padding: {px(10)}px;
    }}
"""
    BTN_QSS = f"""
    QPushButton {{ color: {INK}; background-color: {PANEL}; border: 1px solid {LINE_STRONG};
        border-radius: {px(8)}px; padding: {px(7)}px {px(14)}px; }}
    QPushButton:hover {{ background-color: {NEUTRAL}; border-color: {MUTED}; }}
"""
    INPUT_QSS = f"""
    QTextEdit {{ color: {INK}; background-color: {PANEL};
        border: 1px solid {LINE_STRONG}; border-radius: {px(8)}px;
        padding: {px(6)}px; }}
    QLineEdit {{ color: {INK}; background-color: {PANEL};
        border: 1px solid {LINE_STRONG}; border-radius: {px(8)}px;
        padding: {px(6)}px {px(10)}px;
        min-height: {px(28)}px; }}
    QComboBox {{ color: {INK}; background-color: {PANEL};
        border: 1px solid {LINE_STRONG}; border-radius: {px(8)}px;
        padding: {px(6)}px {px(28)}px {px(6)}px {px(10)}px;
        min-height: {px(28)}px; }}
    QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: center right;
        width: {px(24)}px; border: none; }}
    QComboBox::down-arrow {{ image: none; border-left: 5px solid transparent;
        border-right: 5px solid transparent; border-top: 6px solid #334155; }}
    QComboBox QAbstractItemView {{ background-color: {PANEL}; color: #111827;
        border: 1px solid {LINE_STRONG}; selection-background-color: {ACCENT};
        selection-color: #ffffff; outline: none; }}
    QComboBox QAbstractItemView::item {{ padding: {px(8)}px {px(12)}px;
        min-height: {px(28)}px; border-bottom: 1px solid {LINE}; }}
"""
    CONNECT_BTN_QSS = f"""
    QPushButton {{ color: #ffffff; background-color: {ACCENT}; border: none;
        border-radius: {px(8)}px; padding: {px(7)}px {px(16)}px;
        font-weight: 700; }}
    QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
    QPushButton:pressed {{ background-color: {ACCENT_PRESSED}; }}
"""
    LABEL_QSS = f"color: {INK}; font-size: {px(13)}px; font-weight: 500; background: transparent;"
    LOG_QSS = (
        f"QTextEdit {{ background-color: {LOG_BG}; color: #94a3b8; "
        f"border: 1px solid {LOG_BORDER}; border-radius: {px(10)}px; "
        f"font-family: Consolas, Cascadia Mono, monospace; "
        f"padding: {px(8)}px; }}"
    )
    DIALOG_TOPBAR_QSS = (
        f"QWidget {{ background-color: {PANEL}; border-bottom: 1px solid {LINE}; }}"
    )
    DIALOG_APPEND_BTN_QSS = f"""
    QPushButton {{ background-color: {ACCENT}; color: white; border: none;
        border-radius: {px(8)}px; padding: {px(7)}px {px(14)}px;
        font-weight: 700; }}
    QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
"""
    DIALOG_SECONDARY_BTN_QSS = f"""
    QPushButton {{ background-color: {SUCCESS}; color: white; border: none;
        border-radius: {px(8)}px; padding: {px(7)}px {px(14)}px;
        font-weight: 600; }}
    QPushButton:hover {{ background-color: {SUCCESS_HOVER}; }}
"""
    DIALOG_NEUTRAL_BTN_QSS = f"""
    QPushButton {{ background-color: #475569; color: white; border: none;
        border-radius: {px(8)}px; padding: {px(7)}px {px(14)}px;
        }}
    QPushButton:hover {{ background-color: #334155; }}
"""
    DIALOG_DANGER_BTN_QSS = f"""
    QPushButton {{ background-color: {DANGER}; color: white; border: none;
        border-radius: {px(8)}px; padding: {px(7)}px {px(14)}px;
        }}
    QPushButton:hover {{ background-color: {DANGER_HOVER}; }}
"""
    DIALOG_GROUPBOX_QSS = (
        f"QGroupBox {{ border: 1px solid {LINE}; border-radius: {px(10)}px; "
        f"padding-top: {px(14)}px; margin-top: {px(8)}px; font-weight: 700; color: {INK}; "
        f"background-color: {PANEL}; }}"
        f"QGroupBox::title {{ subcontrol-origin: margin; left: {px(12)}px; padding: 0 {px(6)}px; }}"
    )


# Placeholder names so "from components.ui_theme import BTN_QSS" works before rebuild.
HEADER_STYLE = ""
SUBHEADER_STYLE = ""
ITEM_STYLE = ""
ITEM_ACTIVE_STYLE = ""
NESTED_ITEM_STYLE = ""
NESTED_ITEM_ACTIVE_STYLE = ""
PAGE_STYLE = ""
CARD_STYLE = ""
LOG_STYLE = ""
BTN_QSS = ""
INPUT_QSS = ""
CONNECT_BTN_QSS = ""
LABEL_QSS = ""
LOG_QSS = ""
DIALOG_TOPBAR_QSS = ""
DIALOG_APPEND_BTN_QSS = ""
DIALOG_SECONDARY_BTN_QSS = ""
DIALOG_NEUTRAL_BTN_QSS = ""
DIALOG_DANGER_BTN_QSS = ""
DIALOG_GROUPBOX_QSS = ""
_rebuild_style_exports()


def step_label_inactive_qss() -> str:
    return f"""
        QLabel {{
            padding: {px(8)}px {px(14)}px; color: {MUTED};
            border-bottom: 3px solid transparent; border-radius: 0;
            background: transparent;
        }}
        QLabel:hover {{ background-color: {NEUTRAL}; color: {INK}; }}
    """


def step_label_active_qss() -> str:
    return f"""
        QLabel {{
            padding: {px(8)}px {px(14)}px; font-weight: 700;
            color: {ACCENT_HOVER};
            border-bottom: 3px solid {ACCENT}; border-radius: 0;
            background-color: {ACCENT_SOFT};
        }}
    """


def global_app_qss() -> str:
    """App-wide stylesheet — lifts default Qt look; sizes follow ui_scale()."""
    return f"""
    * {{
        font-family: "Segoe UI", "Microsoft YaHei UI", "PingFang SC", sans-serif;
    }}
    QMainWindow, QDialog {{
        background-color: {BG};
        color: {INK};
    }}
    QToolTip {{
        background-color: {SIDEBAR_ELEVATED}; color: #f8fafc;
        border: 1px solid #334155; padding: {px(6)}px {px(8)}px;
        border-radius: {px(6)}px;
    }}
    QGroupBox {{
        background-color: {PANEL};
        border: 1px solid {LINE};
        border-radius: {px(12)}px;
        margin-top: {px(12)}px;
        padding: {px(14)}px {px(12)}px {px(12)}px {px(12)}px;
        font-weight: 700;
        color: {INK};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: {px(14)}px;
        padding: 0 {px(6)}px;
        color: {INK};
    }}
    QLabel {{
        color: #334155;
        background: transparent;
    }}
    QPushButton {{
        background-color: {PANEL};
        color: {INK};
        border: 1px solid {LINE_STRONG};
        border-radius: {px(8)}px;
        padding: {px(7)}px {px(14)}px;
        min-height: {px(28)}px;
    }}
    QPushButton:hover {{
        background-color: {NEUTRAL};
        border-color: {MUTED};
    }}
    QPushButton:pressed {{
        background-color: {NEUTRAL_HOVER};
    }}
    QPushButton:disabled {{
        color: #94a3b8;
        background-color: #f1f5f9;
        border-color: {LINE};
    }}
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
        background-color: {PANEL};
        color: {INK};
        border: 1px solid {LINE_STRONG};
        border-radius: {px(8)}px;
        padding: {min(px(6), 6)}px {px(8)}px;
        selection-background-color: {ACCENT};
        selection-color: #ffffff;
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
    QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
        border: 1px solid {ACCENT};
    }}
    QComboBox {{
        background-color: {PANEL};
        color: {INK};
        border: 1px solid {LINE_STRONG};
        border-radius: {px(8)}px;
        padding: {px(6)}px {px(28)}px {px(6)}px {px(10)}px;
        min-height: {px(28)}px;
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: {px(26)}px;
        border: none;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #475569;
        margin-right: {px(8)}px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {PANEL};
        color: {INK};
        border: 1px solid {LINE_STRONG};
        selection-background-color: {ACCENT};
        selection-color: #ffffff;
        outline: 0;
    }}
    QAbstractItemView {{
        background-color: {PANEL};
        color: {INK};
        border: 1px solid {LINE_STRONG};
        selection-background-color: {ACCENT_SOFT};
        selection-color: {INK};
        outline: 0;
    }}
    QListView {{
        background-color: {PANEL};
        color: {INK};
        border: 1px solid {LINE_STRONG};
        outline: 0;
    }}
    QMenu {{
        background-color: {PANEL};
        color: {INK};
        border: 1px solid {LINE_STRONG};
        padding: {px(4)}px;
    }}
    QMenu::item {{
        padding: {px(8)}px {px(16)}px;
        background-color: transparent;
        color: {INK};
    }}
    QMenu::item:selected {{
        background-color: {ACCENT_SOFT};
        color: {INK};
    }}
    QMenu::separator {{
        height: 1px;
        background: {LINE};
        margin: {px(4)}px {px(8)}px;
    }}
    QCheckBox, QRadioButton {{
        color: #334155;
        spacing: {px(8)}px;
        background: transparent;
    }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: {px(16)}px; height: {px(16)}px;
    }}
    QTabWidget::pane {{
        border: 1px solid {LINE};
        border-radius: {px(10)}px;
        background: {PANEL};
        top: -1px;
    }}
    QTabBar::tab {{
        background: #eef2f7;
        color: {MUTED};
        border: 1px solid {LINE};
        border-bottom: none;
        border-top-left-radius: {px(8)}px;
        border-top-right-radius: {px(8)}px;
        padding: {px(8)}px {px(14)}px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background: {PANEL};
        color: {ACCENT_HOVER};
        font-weight: 700;
    }}
    QTabBar::tab:hover {{
        color: {INK};
    }}
    QTableWidget, QTableView, QTreeWidget, QListWidget {{
        background: {PANEL};
        border: 1px solid {LINE};
        border-radius: {px(10)}px;
        gridline-color: {LINE};
        selection-background-color: {ACCENT_SOFT};
        selection-color: {INK};
        alternate-background-color: #f8fafc;
    }}
    QHeaderView::section {{
        background: #f1f5f9;
        color: #334155;
        padding: {px(8)}px;
        border: none;
        border-right: 1px solid {LINE};
        border-bottom: 1px solid {LINE_STRONG};
        font-weight: 700;
    }}
    QScrollBar:vertical {{
        background: transparent; width: {px(10)}px; margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: #cbd5e1; border-radius: {px(5)}px; min-height: {px(28)}px;
    }}
    QScrollBar::handle:vertical:hover {{ background: #94a3b8; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar:horizontal {{
        background: transparent; height: {px(10)}px; margin: 2px;
    }}
    QScrollBar::handle:horizontal {{
        background: #cbd5e1; border-radius: {px(5)}px; min-width: {px(28)}px;
    }}
    QProgressBar {{
        border: 1px solid {LINE};
        border-radius: {px(8)}px;
        background: #eef2f7;
        text-align: center;
        color: {INK};
        min-height: {px(16)}px;
    }}
    QProgressBar::chunk {{
        background-color: {ACCENT};
        border-radius: {px(7)}px;
    }}
    QStatusBar {{
        background: {PANEL};
        border-top: 1px solid {LINE};
        color: {MUTED};
    }}
    """


def apply_app_theme(
    app: Optional[QtWidgets.QApplication] = None,
    scale: Optional[float] = None,
) -> None:
    """Apply Fusion + global QSS + default font. Optionally set ui scale first."""
    if scale is not None:
        set_ui_scale(scale)
    application = app or QtWidgets.QApplication.instance()
    if application is None:
        return
    # Skip identical re-apply (setStyleSheet re-polishes entire UI — freezes on maximize)
    if (
        getattr(apply_app_theme, "_done", False)
        and abs(float(_UI_SCALE) - float(getattr(apply_app_theme, "_scale", -1.0))) < 1e-6
        and application.styleSheet()
    ):
        return
    try:
        if application.style().objectName().lower() != "fusion":
            application.setStyle("Fusion")
    except Exception:
        pass
    point = max(9, min(20, int(round(11 * _UI_SCALE))))
    font = QtGui.QFont("Segoe UI", point)
    try:
        db = QtGui.QFontDatabase()
        for name in ("Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI"):
            if name in db.families():
                font = QtGui.QFont(name, point)
                break
    except Exception:
        pass
    application.setFont(font)
    application.setStyleSheet(global_app_qss())
    apply_app_theme._done = True  # type: ignore[attr-defined]
    apply_app_theme._scale = float(_UI_SCALE)  # type: ignore[attr-defined]
