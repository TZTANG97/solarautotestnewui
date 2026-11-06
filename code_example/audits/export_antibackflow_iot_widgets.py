# -*- coding: utf-8 -*-
"""Export antibackflow dialog widgets to iot_templates/antibackflow_default.json.

Usage:
  uv run python code_example/export_antibackflow_iot_widgets.py
  uv run python code_example/export_antibackflow_iot_widgets.py --from-running

Without --from-running, writes/keeps a starter template (empty widgets).
With --from-running, expects the app UI object available (call from UI / REPL).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TEMPLATE = ROOT / "iot_templates" / "antibackflow_default.json"


def write_starter() -> Path:
    payload = {
        "widgets": {},
        "auto_append": True,
        "auto_start": False,
        "_template": "antibackflow_default",
        "_note": "空 widgets 用本机防逆流页当前默认值；可用 export 覆盖",
    }
    TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
    TEMPLATE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return TEMPLATE


def export_from_ui(ui_obj) -> Path:
    from utils.iot_widget_export import export_widgets_json

    real = ui_obj
    if hasattr(ui_obj, "ui"):
        try:
            real = ui_obj.ui
        except Exception:
            real = ui_obj
    if hasattr(ui_obj, "ensure"):
        try:
            ui_obj.ensure()
            real = getattr(ui_obj, "_real_ui", None) or real
        except Exception:
            pass
    export_widgets_json(
        real,
        TEMPLATE,
        meta={
            "auto_append": True,
            "auto_start": False,
            "_template": "antibackflow_default",
            "_note": "由本机防逆流页控件导出",
        },
    )
    return TEMPLATE


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Export antibackflow IOT widget template")
    parser.add_argument(
        "--from-running",
        action="store_true",
        help="Export from running app uiThaiAntiBackflow (must be called inside app)",
    )
    args = parser.parse_args(argv)
    if args.from_running:
        ui_obj = globals().get("uiThaiAntiBackflow")
        if ui_obj is None:
            try:
                import SCPITestWave as app  # type: ignore

                ui_obj = getattr(app, "uiThaiAntiBackflow", None)
            except Exception:
                ui_obj = None
        if ui_obj is None:
            print("未找到 uiThaiAntiBackflow；请在 SolarAutoTest 运行中调用，或先写 starter")
            p = write_starter()
            print("已写入 starter:", p)
            return 1
        p = export_from_ui(ui_obj)
        print("已导出:", p)
        return 0
    p = write_starter()
    print("用法: 默认写 starter 模板；本机有防逆流页时用 --from-running 覆盖 widgets")
    print("已写入:", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
