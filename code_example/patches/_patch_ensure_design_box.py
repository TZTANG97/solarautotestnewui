# -*- coding: utf-8 -*-
from pathlib import Path

p = Path("utils/ui_scale.py")
t = p.read_text(encoding="utf-8")
old = '''def _ensure_design_box_props(w: QtWidgets.QWidget) -> None:
    """Capture fixed width/height once so maximize can scale compact Dialog inputs."""
    if bool(w.property("_ui_design_captured")):
        return
    try:
        min_w, max_w = int(w.minimumWidth()), int(w.maximumWidth())
        min_h, max_h = int(w.minimumHeight()), int(w.maximumHeight())
        # Fixed square / compact editors (typical Dialog 70~100 x 26~32)
        fixed_w = min_w > 0 and max_w > 0 and min_w == max_w and min_w <= 420
        fixed_h = min_h > 0 and max_h > 0 and min_h == max_h and min_h <= 72
        if not fixed_w and not fixed_h:
            # Do NOT mark captured — widget may get setFixedSize later
            return
        if fixed_w and w.property("_ui_design_w") in (None, ""):
            # Numeric fields need ~96 design px to show 5–6 digits
            w.setProperty("_ui_design_w", max(min_w, 96) if min_w <= 120 else min_w)
        if fixed_h and w.property("_ui_design_max_h") in (None, ""):
            design_h = max(min_h, 36)
            w.setProperty("_ui_design_min_h", design_h)
            w.setProperty("_ui_design_max_h", design_h)
        w.setProperty("_ui_design_captured", True)
    except Exception:
        pass
'''
new = '''def _ensure_design_box_props(w: QtWidgets.QWidget) -> None:
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
'''
if old not in t:
    raise SystemExit("old block not found")
p.write_text(t.replace(old, new), encoding="utf-8")
print("ok")
