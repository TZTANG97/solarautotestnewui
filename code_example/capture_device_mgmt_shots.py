# -*- coding: utf-8 -*-
"""Capture device-management UI screenshots for process PDF (AC/DC/DEWETRON/DL850/WT)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QTimer

from Dialog_AC_Setting import Ui_Dialog_AC_Setting
from Dialog_DC1_Setting import Ui_Dialog_DC1_Setting
from Dialog_DEWETRON_Setting import Ui_Dialog_DEWETRON_Setting
from Dialog_DL850_Setting import Ui_Dialog_DL850_Setting

OUT = ROOT / "code_example" / "media" / "overload_flow_shots"


def grab(widget, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pix = widget.grab()
    if pix.isNull():
        raise RuntimeError(f"empty grab: {path}")
    if not pix.save(str(path), "PNG"):
        raise RuntimeError(f"save failed: {path}")
    print(f"saved {path.name} ({pix.width()}x{pix.height()})")


def show_ui(ui_cls, title: str, size=(1100, 720)):
    dlg = QDialog()
    dlg.setWindowTitle(title)
    ui = ui_cls()
    ui.setupUi(dlg)
    dlg.resize(*size)
    dlg.show()
    QApplication.instance().processEvents()
    QTimer.singleShot(120, lambda: None)
    QApplication.instance().processEvents()
    return dlg, ui


def main() -> int:
    app = QApplication(sys.argv)

    shots = [
        (Ui_Dialog_AC_Setting, "设备管理 · 交流电源", "D01_device_ac.png", (1000, 700)),
        (Ui_Dialog_DC1_Setting, "设备管理 · 直流电源", "D02_device_dc.png", (1000, 700)),
        (Ui_Dialog_DEWETRON_Setting, "设备管理 · 德威创 DEWETRON", "D03_device_dewetron.png", (1100, 780)),
        (Ui_Dialog_DL850_Setting, "设备管理 · 示波器 DL850", "D04_device_dl850.png", (900, 560)),
    ]

    # WT3000E setting if available
    try:
        from Dialog_thaiWT3000E import Ui_Dialog_thai_WT3000E

        shots.append(
            (Ui_Dialog_thai_WT3000E, "设备管理 · 功率分析仪 WT3000E", "D05_device_wt3000e.png", (1100, 780))
        )
    except Exception as exc:
        print(f"skip WT3000E: {exc}")

    for cls, title, name, size in shots:
        try:
            dlg, _ui = show_ui(cls, title, size)
            grab(dlg, OUT / name)
            dlg.close()
        except Exception as exc:
            print(f"FAIL {name}: {exc}")

    print(f"DEVICE_SHOTS -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
