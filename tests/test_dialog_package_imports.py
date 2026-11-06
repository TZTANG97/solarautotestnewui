# -*- coding: utf-8 -*-
"""Dialog 实现在 dialogs/；调用方直接 from dialogs.Xxx import。"""
from __future__ import annotations

import importlib
import pkgutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import dialogs  # noqa: E402


def _dialog_module_names() -> list[str]:
    names = []
    for mod in pkgutil.iter_modules(dialogs.__path__):
        if mod.name.startswith("Dialog") or mod.name in ("Dialog", "DialogFileManager"):
            names.append(mod.name)
    return sorted(names)


@pytest.mark.parametrize("mod_name", _dialog_module_names())
def test_dialogs_package_import(mod_name: str):
    m = importlib.import_module(f"dialogs.{mod_name}")
    assert m is not None


def test_root_no_longer_has_dialog_shims():
    """根目录不再堆 Dialog_*.py 兼容壳。"""
    leftovers = [
        p.name
        for p in ROOT.glob("Dialog*.py")
        if p.is_file()
    ] + ([p.name for p in ROOT.glob("DialogFileManager.py")] if (ROOT / "DialogFileManager.py").exists() else [])
    assert leftovers == [], f"根目录仍有 Dialog 壳: {leftovers}"


def test_cross_dialog_imports():
    from dialogs.Dialog_thaiguodianyashanbian import parse_power_group_tree
    from dialogs.Dialog_thailvrt import _BaseTimingProfileDialogUi
    from dialogs.Dialog_thaidynamicmppt import Ui_Dialog_thaidynamicmppt
    from dialogs.Dialog_thaiphasejump import Ui_Dialog_thaiphasejump

    assert callable(parse_power_group_tree)
    assert _BaseTimingProfileDialogUi is not None
    assert issubclass(Ui_Dialog_thaidynamicmppt, _BaseTimingProfileDialogUi)
    assert Ui_Dialog_thaiphasejump is not None


def test_scpitestwave_dialog_imports_subset():
    from dialogs.Dialog_AC_Setting import Ui_Dialog_AC_Setting
    from dialogs.Dialog_thaantibackflow import Ui_Dialog_thaantibackflow
    from dialogs.Dialog_thaioverloads import Ui_Dialog_thaioverloads

    assert Ui_Dialog_AC_Setting is not None
    assert Ui_Dialog_thaantibackflow is not None
    assert Ui_Dialog_thaioverloads is not None
