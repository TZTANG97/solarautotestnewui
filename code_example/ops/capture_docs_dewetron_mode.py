# -*- coding: utf-8 -*-
"""Capture analyzer step in DEWETRON mode for each test dialog."""
from __future__ import annotations

import importlib
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QDialog

OUT = ROOT / "code_example" / "media" / "autotest_docs_shots"
UTOO = Path(r"E:\utoo\utoo-pydjango\utoo-web-front\public\autotest-docs\media")

# Same list as capture_autotest_docs_shots.py; analyzer step index (0-based in _switch_step)
TESTS = [
    ("overload", "Dialog_thaioverloads", "Ui_Dialog_thaioverloads", 1),
    ("flicker", "Dialog_thaiguodianyashanbian", "Ui_Dialog_thaiguodianyashanbian", 1),
    ("harmonic", "Dialog_thaixiebodianliu", "Ui_Dialog_thaixiebodianliu", 1),
    ("fixedpf", "Dialog_thaifixedPF", "Ui_Dialog_thaifixedPF", 1),
    ("dcinj", "Dialog_thaizhiliufenliang", "Ui_Dialog_thaizhiliufenliang", 1),
    ("reconnect", "Dialog_thaichonglian", "Ui_Dialog_thaichonglian", 1),
    ("ovuf", "Dialog_thaiguoqianya_pin", "Ui_Dialog_thaiguoqianya_pin", 1),
    ("static-cos", "Dialog_thaistaticcosPhi", "Ui_Dialog_thaistaticcosPhi", 1),
    ("static-qu", "Dialog_thaistaticQU", "Ui_Dialog_thaiStaticQU", 1),
    ("active-p", "Dialog_thaiactiveP", "Ui_Dialog_thaiactiveP", 1),
    ("overfreq", "Dialog_thaiguopinjiangzai", "Ui_Dialog_thaiguopinjiangzai", 1),
    ("underfreq", "Dialog_thaiqianpinshengzai", "Ui_Dialog_thaiqianpinshengzai", 1),
    ("fixed-q", "Dialog_thaifixedQ", "Ui_Dialog_thaifixedQ", 1),
    ("qin", "Dialog_thaireactiveQin", "Ui_Dialog_thaireactiveQin", 1),
    ("qacc", "Dialog_thaireactiveQacc", "Ui_Dialog_thaireactiveQacc", 1),
    ("qcap", "Dialog_thaireactiveQcap", "Ui_Dialog_thaireactiveQcap", 1),
    ("dyn-cos", "Dialog_thaidynamiccosPhi", "Ui_Dialog_thaidynamiccosPhi", 1),
    ("dyn-qu", "Dialog_thaidynamicQU", "Ui_Dialog_thaidynamicQU", 1),
    ("pu", "Dialog_thaitestPU", "Ui_Dialog_thaitestPU", 1),
    ("rocof", "Dialog_thairocof", "Ui_Dialog_thairocof", 1),
    ("freq-adapt", "Dialog_thaifrequencyadaptability", "Ui_Dialog_thaifrequencyadaptability", 1),
    ("volt-adapt", "Dialog_thaivoltageadaptability", "Ui_Dialog_thaivoltageadaptability", 1),
    ("rapid-volt", "Dialog_thairapidvolt", "Ui_Dialog_thairapidvolt", 1),
    ("volt10min", "Dialog_thaivoltprotect10min", "Ui_Dialog_thaivoltprotect10min", 1),
    ("immun", "Dialog_thaiguoqianpin_immun", "Ui_Dialog_thaiguoqianpin_immun", 1),
    ("static-mppt", "Dialog_thaistaticmppttest", "Ui_Dialog_thaistaticmppttest", 1),
    ("antibackflow", "Dialog_thaantibackflow", "Ui_Dialog_thaantibackflow", 1),
]


def settle(app, ms=150):
    app.processEvents()
    QTimer.singleShot(ms, lambda: None)
    app.processEvents()


def grab(widget, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pix = widget.grab()
    if pix.isNull():
        raise RuntimeError("empty")
    pix.save(str(path), "PNG")
    UTOO.mkdir(parents=True, exist_ok=True)
    pix.save(str(UTOO / path.name), "PNG")
    print(f"  {path.name}")


def select_dewetron(ui) -> bool:
    # Shared AnalyzerModeSection
    radio = getattr(ui, "radio_dewetron", None)
    if radio is not None:
        radio.setChecked(True)
        return True
    # Flicker / harmonic top radios
    radio = getattr(ui, "radio_dewetron", None)
    if hasattr(ui, "radio_wt3000") and hasattr(ui, "radio_dewetron"):
        ui.radio_dewetron.setChecked(True)
        return True
    ams = getattr(ui, "analyzerModeSection", None)
    if ams is not None and hasattr(ams, "radio_dewetron"):
        ams.radio_dewetron.setChecked(True)
        return True
    return False


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    app = QApplication(sys.argv)
    ok = fail = 0
    for slug, module, cls_name, step_idx in TESTS:
        print("====", slug)
        try:
            mod = importlib.import_module(f"dialogs.{module}")
            ui_cls = getattr(mod, cls_name)
            dlg = QDialog()
            ui = ui_cls()
            ui.setupUi(dlg)
            dlg.resize(1280, 900)
            dlg.show()
            settle(app, 200)
            switch = getattr(ui, "_switch_step", None)
            if switch:
                switch(step_idx)
            settle(app, 120)
            if not select_dewetron(ui):
                print("  NO dewetron radio")
                fail += 1
                dlg.close()
                continue
            settle(app, 200)
            grab(dlg, OUT / f"T_{slug}_02b_dewetron.png")
            dlg.close()
            ok += 1
        except Exception:
            fail += 1
            traceback.print_exc()
    print(f"DONE ok={ok} fail={fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
