# -*- coding: utf-8 -*-
"""Offscreen check: compact WT inputs must fully show text after ui scale."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt5 import QtGui, QtWidgets


def _visible_text_height(te: QtWidgets.QTextEdit) -> int:
    """Pixels needed to show one line without clipping."""
    fm = te.fontMetrics()
    doc = te.document()
    margin = 0.0
    if doc is not None:
        margin = float(doc.documentMargin())
    # frame + padding approx from stylesheet is hard; use contentsRect vs font
    return int(fm.height() + 2 * margin + 8)


def main() -> int:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    from components.ui_theme import apply_app_theme
    from components.wt_config_content import build_wt3000_content
    from utils.ui_scale import apply_font_scale, scale_for_size

    apply_app_theme(app, scale=1.0)

    class Host:
        pass

    host = Host()
    win = QtWidgets.QMainWindow()
    win.resize(1920, 1080)
    scroll = build_wt3000_content(host)
    win.setCentralWidget(scroll)
    win.show()
    app.processEvents()

    s = scale_for_size(1920, 1080)
    apply_font_scale(s, window=win)
    app.processEvents()

    failures = []
    checks = [
        ("textEdit_StopTime", getattr(host, "textEdit_StopTime", None)),
        ("textEdit_SavePath", getattr(host, "textEdit_SavePath", None)),
        ("textEdit_FileNameList", getattr(host, "textEdit_FileNameList", None)),
    ]
    print(f"scale={s:.2f} app_pt={app.font().pointSize()}")
    for name, te in checks:
        if te is None:
            failures.append(f"{name}: missing")
            continue
        need = _visible_text_height(te)
        h = te.height()
        mh = te.maximumHeight()
        plain = te.toPlainText().replace("\n", "\\n")
        ok = h >= need and mh >= need
        print(
            f"{name}: h={h} maxH={mh} need>={need} w={te.width()} "
            f"minW={te.minimumWidth()} text={plain!r} ok={ok}"
        )
        if not ok:
            failures.append(f"{name}: height {h}/{mh} < need {need}")
        if name == "textEdit_SavePath" and te.minimumWidth() < 200:
            failures.append(f"{name}: minWidth {te.minimumWidth()} too narrow")
        if name == "textEdit_StopTime" and len(te.toPlainText()) >= 8 and te.width() < 100:
            failures.append(f"{name}: width {te.width()} too narrow for time")

    # Sidebar contrast / font
    from components import ui_theme as theme

    print(f"NAV_TEXT={theme.NAV_TEXT} ITEM font sample scale={theme.ui_scale():.2f}")

    if failures:
        print("FAIL:")
        for f in failures:
            print(" -", f)
        return 1
    print("PASS: compact WT inputs fit text at maximize scale")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
