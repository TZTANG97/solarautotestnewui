# -*- coding: utf-8 -*-
"""命令库覆盖：同勾选、不同型号 com_content → ITEM 分离。"""
from __future__ import annotations

from utils.wt_scpi_items import (
    base_token_for_checkbox,
    catalog_seed_rows,
    clear_catalog_token_overrides,
    items_from_wt_config,
    set_catalog_token_overrides,
)


def setup_function():
    clear_catalog_token_overrides()


def teardown_function():
    clear_catalog_token_overrides()


def test_seed_setu_differs_3000_vs_1806():
    rows = catalog_seed_rows()
    by = {(r["model"], r["blockly_name"]): r["com_content"] for r in rows}
    assert by[("3000", "checkBox_SetU")] == "U"
    assert by[("1806", "checkBox_SetU")] == "URMS"


def test_override_changes_items_for_one_model_only():
    cfg3000 = {
        "Style": "Thai_WT3000E_Config",
        "checkBox_SetElement1": "1",
        "checkBox_SetU": "1",
    }
    cfg1806 = {
        "Style": "Thai_WT1806E_Config",
        "checkBox_SetElement1": "1",
        "checkBox_SetU": "1",
    }
    # 默认：3000→U,TOTAL；1806→URMS
    items_a = items_from_wt_config(cfg3000)
    items_b = items_from_wt_config(cfg1806)
    assert any(i.startswith("U,1") for i in items_a)
    assert any(i.startswith("URMS,1") for i in items_b)

    # 模拟命令管理把 1806 的 checkBox_SetU 改成 CUSTOMU
    set_catalog_token_overrides("1806", {"checkBox_SetU": "CUSTOMU"})
    items_b2 = items_from_wt_config(cfg1806)
    items_a2 = items_from_wt_config(cfg3000)
    assert any(i.startswith("CUSTOMU,1") for i in items_b2)
    assert any(i.startswith("U,1") for i in items_a2)
    assert not any(i.startswith("CUSTOMU") for i in items_a2)


def test_base_token_respects_override():
    assert base_token_for_checkbox("3000", "checkBox_SetU") == "U"
    set_catalog_token_overrides("3000", {"checkBox_SetU": "URMS"})
    assert base_token_for_checkbox("3000", "checkBox_SetU") == "URMS"
