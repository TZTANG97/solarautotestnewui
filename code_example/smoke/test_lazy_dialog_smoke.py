# -*- coding: utf-8 -*-
"""Smoke test: LazyDialog on_create does not create until ensure()."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QVBoxLayout

app = QApplication.instance() or QApplication([])

from setup.main_setup import LazyDialog


class _FakeUi:
    def setupUi(self, dialog):
        lay = QVBoxLayout(dialog)
        self.pushButton_TestAppend = QPushButton("append")
        lay.addWidget(self.pushButton_TestAppend)


created_hooks = []
lazy = LazyDialog(_FakeUi, "smoke")
assert not lazy.is_created


def _hook():
    created_hooks.append("ok")
    assert lazy._real_ui is not None
    lazy._real_ui.pushButton_TestAppend.clicked.connect(lambda: None)


lazy.on_create(_hook)
assert not lazy.is_created
assert created_hooks == []

dlg, ui = lazy.ensure()
assert lazy.is_created
assert created_hooks == ["ok"]
assert isinstance(dlg, QDialog)
assert hasattr(ui, "pushButton_TestAppend")

# late on_create runs immediately
late = []
lazy.on_create(lambda: late.append(1))
assert late == [1]

print("LazyDialog smoke OK")
