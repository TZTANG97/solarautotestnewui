# -*- coding: utf-8 -*-
"""Capture real UI screenshots for 过载能力测试 process sample PDF."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QDialog

from Dialog_thaioverloads import Ui_Dialog_thaioverloads

OUT_DIR = ROOT / "code_example" / "media" / "overload_flow_shots"
STEP_TITLES = [
    "01_step_ac_dc_timing",
    "02_step_analyzer",
    "03_step_overload_params",
    "04_step_shutdown",
]


def grab(widget, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pix = widget.grab()
    if pix.isNull():
        raise RuntimeError(f"empty grab: {path}")
    if not pix.save(str(path), "PNG"):
        raise RuntimeError(f"save failed: {path}")
    print(f"saved {path} ({pix.width()}x{pix.height()})")


def main() -> int:
    # Prefer on-screen window so styles render; auto-close after grabs.
    app = QApplication(sys.argv)
    dlg = QDialog()
    dlg.setWindowTitle("过载能力测试 — 项目设置（截图）")
    ui = Ui_Dialog_thaioverloads()
    ui.setupUi(dlg)
    dlg.resize(1280, 820)
    dlg.show()
    app.processEvents()

    # Let layout settle
    QTimer.singleShot(200, lambda: None)
    app.processEvents()

    for idx, name in enumerate(STEP_TITLES):
        ui._switch_step(idx)
        app.processEvents()
        QTimer.singleShot(80, lambda: None)
        app.processEvents()
        grab(dlg, OUT_DIR / f"{name}.png")

    # Full dialog overview on step1
    ui._switch_step(0)
    app.processEvents()
    grab(dlg, OUT_DIR / "00_dialog_overview.png")

    dlg.close()
    print(f"ALL_SHOTS -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
