# -*- coding: utf-8 -*-
"""Dialog 迁入 dialogs/ 后的兼容导入冒烟。"""
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


@pytest.mark.parametrize("mod_name", _dialog_module_names())
def test_root_shim_reexports(mod_name: str):
    """根目录同名模块仍可 import；透出实现模块 __all__（或 Ui_ 符号）。"""
    shim = importlib.import_module(mod_name)
    real = importlib.import_module(f"dialogs.{mod_name}")
    all_names = getattr(real, "__all__", None)
    if isinstance(all_names, (list, tuple)) and all_names:
        expected = list(all_names)
    else:
        expected = [
            n
            for n in dir(real)
            if n.startswith("Ui_") or n.startswith("Dialog")
        ]
        if not expected:
            expected = [n for n in dir(real) if n[:1].isupper()][:8]
    assert expected, f"{mod_name} 无可检查符号"
    for name in expected:
        assert hasattr(shim, name), f"根 shim {mod_name} 缺少 {name}"


def test_cross_dialog_imports():
    """Dialog 之间旧绝对导入仍可用（含 __all__ 中的私有基类）。"""
    from Dialog_thaiguodianyashanbian import parse_power_group_tree
    from Dialog_thailvrt import _BaseTimingProfileDialogUi
    from Dialog_thaidynamicmppt import Ui_Dialog_thaidynamicmppt
    from Dialog_thaiphasejump import Ui_Dialog_thaiphasejump

    assert callable(parse_power_group_tree)
    assert _BaseTimingProfileDialogUi is not None
    assert issubclass(Ui_Dialog_thaidynamicmppt, _BaseTimingProfileDialogUi)
    assert Ui_Dialog_thaiphasejump is not None


def test_scpitestwave_dialog_imports_subset():
    """主程序顶部常用 Dialog 导入不炸（不执行主逻辑）。"""
    from Dialog_AC_Setting import Ui_Dialog_AC_Setting
    from Dialog_thaantibackflow import Ui_Dialog_thaantibackflow
    from Dialog_thaioverloads import Ui_Dialog_thaioverloads

    assert Ui_Dialog_AC_Setting is not None
    assert Ui_Dialog_thaantibackflow is not None
    assert Ui_Dialog_thaioverloads is not None
