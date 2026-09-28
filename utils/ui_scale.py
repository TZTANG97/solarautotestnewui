# -*- coding: utf-8 -*-
"""UI scale helpers.

Fonts and input sizes stay at design scale (1.0). Window resize only
changes layout stretch — never live-rewrites font-size / min-height.
"""

from __future__ import annotations

import re
from typing import Optional

from PyQt5 import QtCore, QtGui, QtWidgets

DESIGN_W = 1600
DESIGN_H = 900
SIDEBAR_W = 280
# Locked: window size must not change fonts / input boxes.
_MIN_SCALE = 1.0
_MAX_SCALE = 1.0
_STEP = 0.05
_FIXED_SCALE = 1.0
_BASE_POINT = 12
_BODY_REF_PX = 13.0
_FONT_SIZE_RE = re.compile(
    r"(font-size\s*:\s*)(\d+(?:\.\d+)?)(\s*(?:px|pt))",
    re.IGNORECASE,
)
_PX_LEN_RE = re.compile(r"(\d+(?:\.\d+)?)px", re.IGNORECASE)
_theme_done = False


def clamp_scale(scale: float) -> float:
    return _FIXED_SCALE


def quantize_scale(scale: float) -> float:
    return _FIXED_SCALE


def scale_for_size(
    width: int,
    height: int,
    *,
    design_w: int = DESIGN_W,
    design_h: int = DESIGN_H,
) -> float:
    """Always 1.0 — layout may stretch; fonts/inputs stay design size."""
    return _FIXED_SCALE


def _make_font(scale: float) -> QtGui.QFont:
    point = max(9, min(15, int(round(_BASE_POINT * float(scale)))))
    font = QtGui.QFont("Segoe UI", point)
    try:
        db = QtGui.QFontDatabase()
        for name in ("Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI"):
            if name in db.families():
                font = QtGui.QFont(name, point)
                break
    except Exception:
        pass
    return font


def scale_qss_metrics(ss: str, scale: float) -> str:
    """Scale design-time font-size and px lengths in a stylesheet string."""
    if not ss:
        return ss
    s = float(scale)

    def _font_repl(m: re.Match) -> str:
        n = float(m.group(2))
        unit = m.group(3)
        scaled = max(8, int(round(n * s)))
        return f"{m.group(1)}{scaled}{unit}"

    out = _FONT_SIZE_RE.sub(_font_repl, ss)

    def _px_repl(m: re.Match) -> str:
        # Skip if this match is inside a font-size we already rewrote as pt
        n = float(m.group(1))
        # Keep hairline borders readable but thin
        if n <= 1.0:
            return f"{max(1, int(round(n * s)))}px"
        return f"{max(1, int(round(n * s)))}px"

    # Avoid double-scaling font-size px: temporarily protect them
    protected: list[str] = []

    def _protect(m: re.Match) -> str:
        protected.append(m.group(0))
        return f"__FONTSIZE_{len(protected) - 1}__"

    out = _FONT_SIZE_RE.sub(_protect, ss)
    out = _PX_LEN_RE.sub(_px_repl, out)

    def _font_from_orig(m: re.Match) -> str:
        return _font_repl(m)

    # Restore font-size tokens from original matches (scaled once)
    restored = []
    for i, token in enumerate(protected):
        restored.append(_FONT_SIZE_RE.sub(_font_from_orig, token))
        out = out.replace(f"__FONTSIZE_{i}__", restored[-1])
    return out


def _ensure_design_box_props(w: QtWidgets.QWidget) -> None:
    """Capture fixed width/height once so maximize can scale compact Dialog inputs.

    Only QTextEdit / QLineEdit / QComboBox. Never touch status dots (10×10) or
    other chrome — those were blown into huge red rectangles on the home page.
    """
    if bool(w.property("_ui_design_captured")):
        return
    if not isinstance(w, (QtWidgets.QTextEdit, QtWidgets.QLineEdit, QtWidgets.QComboBox)):
        return
    try:
        min_w, max_w = int(w.minimumWidth()), int(w.maximumWidth())
        min_h, max_h = int(w.minimumHeight()), int(w.maximumHeight())
        # Ignore indicator-sized widgets
        if (0 < min_w <= 24 and 0 < min_h <= 24) or (0 < max_w <= 24 and 0 < max_h <= 24):
            w.setProperty("_ui_design_captured", True)
            return
        fixed_w = min_w > 0 and max_w > 0 and min_w == max_w and 24 < min_w <= 420
        fixed_h = min_h > 0 and max_h > 0 and min_h == max_h and 24 < min_h <= 72
        if not fixed_w and not fixed_h:
            # Do NOT mark captured — widget may get setFixedSize later
            return
        if fixed_w and w.property("_ui_design_w") in (None, ""):
            w.setProperty("_ui_design_w", max(min_w, 96) if min_w <= 120 else min_w)
        if fixed_h and w.property("_ui_design_max_h") in (None, ""):
            design_h = max(min_h, 36)
            w.setProperty("_ui_design_min_h", design_h)
            w.setProperty("_ui_design_max_h", design_h)
        w.setProperty("_ui_design_captured", True)
    except Exception:
        pass


def _apply_design_box(w: QtWidgets.QWidget, scale: float) -> bool:
    """Apply cached design width/height properties. Returns True if changed."""
    _ensure_design_box_props(w)
    changed = False
    try:
        dw = w.property("_ui_design_w")
        dmax_h = w.property("_ui_design_max_h")
        dmin_h = w.property("_ui_design_min_h")
        dmin_w = w.property("_ui_design_min_w")

        if dw not in (None, ""):
            target_w = max(40, int(round(int(dw) * scale)))
            if dmax_h not in (None, ""):
                target_h = max(28, int(round(int(dmax_h) * scale)))
                if w.minimumWidth() != target_w or w.maximumHeight() != target_h:
                    w.setFixedSize(target_w, target_h)
                    changed = True
            else:
                if w.minimumWidth() != target_w or w.maximumWidth() != target_w:
                    w.setFixedWidth(target_w)
                    changed = True
        elif dmin_w not in (None, ""):
            target = max(40, int(round(int(dmin_w) * scale)))
            if int(w.minimumWidth()) != target:
                w.setMinimumWidth(target)
                changed = True

        if dw in (None, "") and dmax_h not in (None, ""):
            max_h = max(24, int(round(int(dmax_h) * scale)))
            if dmin_h not in (None, ""):
                min_h = max(24, int(round(int(dmin_h) * scale)))
            else:
                min_h = max_h if int(dmax_h) <= 48 else min(max_h, max(32, max_h // 2))
            if w.maximumHeight() != max_h or w.minimumHeight() != min_h:
                w.setMinimumHeight(min_h)
                w.setMaximumHeight(max_h)
                changed = True
    except Exception:
        return changed
    return changed


_QSS_SCALE_TYPES = (
    QtWidgets.QTextEdit,
    QtWidgets.QPlainTextEdit,
    QtWidgets.QLineEdit,
    QtWidgets.QComboBox,
    QtWidgets.QGroupBox,
    QtWidgets.QCheckBox,
    QtWidgets.QRadioButton,
    QtWidgets.QProgressBar,
    QtWidgets.QSpinBox,
    QtWidgets.QDoubleSpinBox,
)


def _propagate_scaled_fonts(
    root: QtWidgets.QWidget,
    scale: float,
    base_font: QtGui.QFont,
) -> int:
    """Update widget fonts, local QSS metrics, and design box sizes.

    Avoid setStyleSheet on every QLabel/QPushButton (sidebar thrash → multi-second
    freeze on maximize). Those inherit app font; only input-like widgets rewrite QSS.
    """
    touched = 0
    try:
        widgets = [root] + list(root.findChildren(QtWidgets.QWidget))
    except RuntimeError:
        return 0
    for w in widgets:
        try:
            if w is None:
                continue
            if _apply_design_box(w, scale):
                touched += 1

            # Opt-in QSS scale: explicit _ui_ss_orig, or input-like widgets
            orig = w.property("_ui_ss_orig")
            has_orig = orig not in (None, "")
            scale_qss = has_orig or isinstance(w, _QSS_SCALE_TYPES)

            if scale_qss:
                if orig is None:
                    ss0 = w.styleSheet() or ""
                    w.setProperty("_ui_ss_orig", ss0)
                    orig = ss0
                else:
                    orig = str(orig)
                if orig and (
                    "font-size" in orig.lower()
                    or "min-height" in orig.lower()
                    or "px" in orig.lower()
                ):
                    new_ss = scale_qss_metrics(orig, scale)
                    if new_ss != w.styleSheet():
                        w.setStyleSheet(new_ss)
                        touched += 1
                else:
                    cur = w.font()
                    if (
                        cur.pointSize() != base_font.pointSize()
                        or cur.family() != base_font.family()
                    ):
                        f = QtGui.QFont(base_font)
                        if cur.bold():
                            f.setBold(True)
                        w.setFont(f)
                        touched += 1
            else:
                # Labels / buttons / chrome: font only (no stylesheet thrash)
                cur = w.font()
                if (
                    cur.pointSize() != base_font.pointSize()
                    or cur.family() != base_font.family()
                ):
                    f = QtGui.QFont(base_font)
                    if cur.bold():
                        f.setBold(True)
                    w.setFont(f)
                    touched += 1
        except RuntimeError:
            continue
        except Exception:
            continue
    return touched


def refresh_sidebar_styles(window: Optional[QtWidgets.QWidget]) -> int:
    """Re-apply sidebar nav QSS after ui_scale change (readable on maximize).

    Only touches sidebar QPushButtons — not the whole app (avoids freeze).
    """
    if window is None:
        return 0
    from components import ui_theme as theme

    sidebar = window.findChild(QtWidgets.QWidget, "sidebar")
    if sidebar is None:
        return 0
    n = 0
    try:
        target = int(theme.px(SIDEBAR_W))
        collapsed = bool(sidebar.property("collapsed"))
        if collapsed:
            target = int(theme.px(64))
        if abs(int(sidebar.width()) - target) >= 4:
            sidebar.setFixedWidth(target)
        for btn in sidebar.findChildren(QtWidgets.QPushButton):
            role = str(btn.property("navRole") or "")
            kind = str(btn.property("navKind") or "item")
            active = bool(btn.property("navActive"))
            if role == "header":
                btn.setStyleSheet(theme.HEADER_STYLE)
            elif role == "subheader":
                btn.setStyleSheet(theme.SUBHEADER_STYLE)
            elif active:
                btn.setStyleSheet(
                    theme.NESTED_ITEM_ACTIVE_STYLE
                    if kind == "nested"
                    else theme.ITEM_ACTIVE_STYLE
                )
            else:
                btn.setStyleSheet(
                    theme.NESTED_ITEM_STYLE if kind == "nested" else theme.ITEM_STYLE
                )
            if not btn.icon().isNull():
                btn.setIconSize(QtCore.QSize(theme.px(16), theme.px(16)))
            n += 1
    except Exception as exc:
        print(f"[ui_scale] sidebar refresh skip: {exc}", flush=True)
    return n


def apply_font_scale(
    scale: float,
    *,
    app: Optional[QtWidgets.QApplication] = None,
    window: Optional[QtWidgets.QWidget] = None,
) -> float:
    """Apply fixed design scale (always 1.0). ``scale`` arg ignored."""
    from components import ui_theme as theme

    s = _FIXED_SCALE
    theme.set_ui_scale(s)
    application = app or QtWidgets.QApplication.instance()
    if application is None:
        return s
    font = _make_font(s)
    cur = application.font()
    if cur.pointSize() != font.pointSize() or cur.family() != font.family():
        application.setFont(font)
    if window is not None:
        _propagate_scaled_fonts(window, s, font)
        refresh_sidebar_styles(window)
        try:
            for te in window.findChildren(QtWidgets.QTextEdit):
                if te.isReadOnly():
                    continue
                doc = te.document()
                if doc is not None:
                    df = QtGui.QFont(font)
                    if te.font().bold():
                        df.setBold(True)
                    doc.setDefaultFont(df)
        except Exception:
            pass
    return s


def apply_ui_scale(
    scale: float,
    *,
    window: Optional[QtWidgets.QWidget] = None,
    app: Optional[QtWidgets.QApplication] = None,
) -> float:
    """Full theme apply (startup). Prefer apply_font_scale for live resize."""
    global _theme_done
    from components import ui_theme as theme

    s = theme.set_ui_scale(quantize_scale(scale))
    application = app or QtWidgets.QApplication.instance()
    theme.apply_app_theme(application, scale=s)
    application.setFont(_make_font(s))

    try:
        from components import timeline as tl

        tl._BTN_QSS = theme.BTN_QSS
        tl._INPUT_QSS = theme.INPUT_QSS
        tl._CONNECT_BTN_QSS = theme.CONNECT_BTN_QSS
        tl._LABEL_QSS = theme.LABEL_QSS
        tl._LOG_QSS = theme.LOG_QSS
    except Exception:
        pass

    if window is not None:
        _propagate_scaled_fonts(window, s, _make_font(s))
        refresh_sidebar_styles(window)
    _theme_done = True
    return s


def apply_startup_ui_scale(
    window: QtWidgets.QWidget,
    *,
    design_w: int = DESIGN_W,
    design_h: int = DESIGN_H,
    app: Optional[QtWidgets.QApplication] = None,
) -> float:
    """After first show/fit: sync font to window size; theme QSS already applied."""
    global _theme_done
    w = max(int(window.width()), 1)
    h = max(int(window.height()), 1)
    s = scale_for_size(w, h, design_w=design_w, design_h=design_h)
    if _theme_done or bool(
        getattr(
            __import__("components.ui_theme", fromlist=["apply_app_theme"]).apply_app_theme,
            "_done",
            False,
        )
    ):
        return apply_font_scale(s, app=app, window=window)
    return apply_ui_scale(s, window=window, app=app)


class _FontScaleWatcher(QtCore.QObject):
    """No-op stub kept for callers; does not listen to resize."""

    def __init__(
        self,
        window: QtWidgets.QWidget,
        *,
        design_w: int = DESIGN_W,
        design_h: int = DESIGN_H,
        parent: Optional[QtCore.QObject] = None,
    ):
        super().__init__(parent or window)
        self._window = window
        self._design_w = design_w
        self._design_h = design_h
        self._last = _FIXED_SCALE
        self._busy = False

    def eventFilter(self, obj, event):
        return False

    def apply_now(self) -> float:
        """Re-apply fixed scale=1.0 (e.g. after embedding a new page)."""
        w = self._window
        if w is None:
            return self._last
        self._busy = True
        try:
            apply_font_scale(_FIXED_SCALE, window=w)
            self._last = _FIXED_SCALE
        except Exception as exc:
            print(f"[ui_scale] fixed scale skip: {exc}", flush=True)
        finally:
            self._busy = False
        return self._last


def install_ui_scale_watcher(
    window: QtWidgets.QWidget,
    *,
    design_w: int = DESIGN_W,
    design_h: int = DESIGN_H,
    apply_immediately: bool = True,
) -> _FontScaleWatcher:
    """Keep API; does not install live resize font scaling."""
    watcher = _FontScaleWatcher(
        window, design_w=design_w, design_h=design_h, parent=window
    )
    window._ui_scale_watcher = watcher  # type: ignore[attr-defined]
    if apply_immediately:
        watcher.apply_now()
        print("[ui_scale] fixed scale=1.00 (no live resize scaling)", flush=True)
    return watcher


def _reset_applied_for_tests() -> None:
    global _theme_done
    _theme_done = False
