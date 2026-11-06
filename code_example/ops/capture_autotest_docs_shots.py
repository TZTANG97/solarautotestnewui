# -*- coding: utf-8 -*-
"""Batch-capture Auto_Test dialog step screenshots for autotest-docs."""
from __future__ import annotations

import importlib
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QDialog

OUT = ROOT / "code_example" / "media" / "autotest_docs_shots"
UTOO = Path(r"E:\utoo\utoo-pydjango\utoo-web-front\public\autotest-docs\media")

# slug -> (module, Ui class, max steps to grab; None = stackedWidget.count())
TESTS = [
    ("overload", "Dialog_thaioverloads", "Ui_Dialog_thaioverloads", None),
    ("flicker", "Dialog_thaiguodianyashanbian", "Ui_Dialog_thaiguodianyashanbian", None),
    ("harmonic", "Dialog_thaixiebodianliu", "Ui_Dialog_thaixiebodianliu", None),
    ("fixedpf", "Dialog_thaifixedPF", "Ui_Dialog_thaifixedPF", None),
    ("dcinj", "Dialog_thaizhiliufenliang", "Ui_Dialog_thaizhiliufenliang", None),
    ("reconnect", "Dialog_thaichonglian", "Ui_Dialog_thaichonglian", None),
    ("ovuf", "Dialog_thaiguoqianya_pin", "Ui_Dialog_thaiguoqianya_pin", None),
    ("static-cos", "Dialog_thaistaticcosPhi", "Ui_Dialog_thaistaticcosPhi", None),
    ("static-qu", "Dialog_thaistaticQU", "Ui_Dialog_thaiStaticQU", None),
    ("active-p", "Dialog_thaiactiveP", "Ui_Dialog_thaiactiveP", None),
    ("overfreq", "Dialog_thaiguopinjiangzai", "Ui_Dialog_thaiguopinjiangzai", None),
    ("underfreq", "Dialog_thaiqianpinshengzai", "Ui_Dialog_thaiqianpinshengzai", None),
    ("fixed-q", "Dialog_thaifixedQ", "Ui_Dialog_thaifixedQ", None),
    ("qin", "Dialog_thaireactiveQin", "Ui_Dialog_thaireactiveQin", None),
    ("qacc", "Dialog_thaireactiveQacc", "Ui_Dialog_thaireactiveQacc", None),
    ("qcap", "Dialog_thaireactiveQcap", "Ui_Dialog_thaireactiveQcap", None),
    ("dyn-cos", "Dialog_thaidynamiccosPhi", "Ui_Dialog_thaidynamiccosPhi", None),
    ("dyn-qu", "Dialog_thaidynamicQU", "Ui_Dialog_thaidynamicQU", None),
    ("pu", "Dialog_thaitestPU", "Ui_Dialog_thaitestPU", None),
    ("rocof", "Dialog_thairocof", "Ui_Dialog_thairocof", None),
    ("freq-adapt", "Dialog_thaifrequencyadaptability", "Ui_Dialog_thaifrequencyadaptability", None),
    ("volt-adapt", "Dialog_thaivoltageadaptability", "Ui_Dialog_thaivoltageadaptability", None),
    ("rapid-volt", "Dialog_thairapidvolt", "Ui_Dialog_thairapidvolt", None),
    ("volt10min", "Dialog_thaivoltprotect10min", "Ui_Dialog_thaivoltprotect10min", None),
    ("immun", "Dialog_thaiguoqianpin_immun", "Ui_Dialog_thaiguoqianpin_immun", None),
    ("static-mppt", "Dialog_thaistaticmppttest", "Ui_Dialog_thaistaticmppttest", None),
]


def grab(widget, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pix = widget.grab()
    if pix.isNull():
        raise RuntimeError(f"empty {path}")
    if not pix.save(str(path), "PNG"):
        raise RuntimeError(f"save fail {path}")
    UTOO.mkdir(parents=True, exist_ok=True)
    pix.save(str(UTOO / path.name), "PNG")
    print(f"  saved {path.name} ({pix.width()}x{pix.height()})")


def settle(app: QApplication, ms: int = 120) -> None:
    app.processEvents()
    QTimer.singleShot(ms, lambda: None)
    app.processEvents()


def capture_one(app: QApplication, slug: str, module: str, cls_name: str, max_steps) -> None:
    print(f"==== {slug}")
    mod = importlib.import_module(module)
    ui_cls = getattr(mod, cls_name)
    dlg = QDialog()
    dlg.setWindowTitle(f"docs shot · {slug}")
    ui = ui_cls()
    ui.setupUi(dlg)
    dlg.resize(1280, 860)
    dlg.show()
    settle(app, 200)

    sw = getattr(ui, "stackedWidget", None)
    n = sw.count() if sw is not None else 1
    if max_steps is not None:
        n = min(n, max_steps)
    # Cap very long dialogs (e.g. reconnect 8 steps) — still grab all but OK
    switch = getattr(ui, "_switch_step", None)

    # overview = step 0
    if switch:
        switch(0)
        settle(app, 100)
    grab(dlg, OUT / f"T_{slug}_00_overview.png")

    for i in range(n):
        if switch:
            try:
                switch(i)
            except Exception as exc:
                print(f"  switch {i} fail: {exc}")
                continue
        elif sw is not None:
            sw.setCurrentIndex(i)
        settle(app, 80)
        grab(dlg, OUT / f"T_{slug}_{i+1:02d}_step.png")

    dlg.close()
    settle(app, 50)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    UTOO.mkdir(parents=True, exist_ok=True)
    app = QApplication(sys.argv)
    ok, fail = 0, 0
    for slug, module, cls_name, max_steps in TESTS:
        try:
            capture_one(app, slug, module, cls_name, max_steps)
            ok += 1
        except Exception:
            fail += 1
            print(f"FAIL {slug}:")
            traceback.print_exc()
    print(f"DONE ok={ok} fail={fail} -> {OUT} & {UTOO}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
