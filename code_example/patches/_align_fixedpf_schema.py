# -*- coding: utf-8 -*-
"""对齐固定PF=1 Web schema 与 Dialog_thaifixedPF 可见控件。"""
from __future__ import annotations

import json
from pathlib import Path

IOT = Path(r"E:/IOT/iot/app/services/solar_test_schemas/fixedpf_fields.json")
SW = Path(r"E:/solarautotestnewui/utils/iot_fixedpf_schema_data.json")

MODE_CONT = "一条线连续录（单文件）"
MODE_SPLIT = "分开录（多文件/逐点存盘）"

# 测量步骤 1~5 → checkBox_S4..S8，功率默认 100/75/50/30/20，DC 控件 checkBox_S1_DCx_{4..8}
_STEPS = [
    (4, 1, "100", True),
    (5, 2, "75", True),
    (6, 3, "50", True),
    (7, 4, "30", True),
    (8, 5, "20", True),
]


def _ensure(by: dict, name: str, **kw):
    if name not in by:
        by[name] = {
            "name": name,
            "label": name,
            "type": "text",
            "group": "other",
            "default": None,
            "options": [],
        }
    by[name].update({k: v for k, v in kw.items() if v is not None})


def _patch(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    by = {f["name"]: f for f in data.get("fields") or []}

    for g in data.get("groups") or []:
        if g.get("id") == "step3_measure":
            g["title"] = "③ 测量步骤"
        if g.get("id") == "step4_off":
            g["title"] = "④ 关机设置"

    # 启机 DC 仅保留 checkBox_S1_DC1..4
    for name, f in list(by.items()):
        if name.startswith("checkBox_S1_DC") and name not in {
            "checkBox_S1_DC1",
            "checkBox_S1_DC2",
            "checkBox_S1_DC3",
            "checkBox_S1_DC4",
        }:
            if f.get("group") == "step1_ac":
                f["group"] = "step3_measure"

    # 采集 / 录波
    _ensure(
        by,
        "textEdit_S3_TIME_2",
        label="数据采集",
        default="10",
        type="text",
        group="step3_measure",
    )
    _ensure(
        by,
        "comboBox_S3_TIME_2",
        label="数据采集单位",
        default="分钟",
        type="select",
        group="step3_measure",
        options=["分钟", "秒", "毫秒"],
    )
    _ensure(
        by,
        "textEdit_S3_TIME_3",
        label="等待时间",
        default="1",
        type="text",
        group="step3_measure",
    )
    _ensure(
        by,
        "comboBox_S3_TIME_3",
        label="等待时间单位",
        default="秒",
        type="select",
        group="step3_measure",
        options=["秒", "分钟", "毫秒"],
    )
    _ensure(
        by,
        "comboBox_S3_record_mode",
        label="录波方式",
        default=MODE_CONT,
        type="select",
        group="step3_measure",
        options=[MODE_CONT, MODE_SPLIT],
    )

    for step_num, disp, pf, enabled in _STEPS:
        _ensure(
            by,
            f"checkBox_S{step_num}",
            label=f"启用步骤{disp} ({pf}%)",
            default=enabled,
            type="checkbox",
            group="step3_measure",
            options=[],
        )
        for j in range(1, 5):
            _ensure(
                by,
                f"checkBox_S1_DC{j}_{step_num}",
                label=f"步骤{disp}·直流电源{j}",
                default=False,
                type="checkbox",
                group="step3_measure",
                options=[],
            )
        _ensure(
            by,
            f"textEdit_S1_DC1_PF_{step_num}",
            label=f"步骤{disp}·功率%",
            default=pf,
            type="text",
            group="step3_measure",
            options=[],
        )

    # 关机
    _ensure(
        by,
        "checkBox_S14",
        label="启用关机",
        default=True,
        type="checkbox",
        group="step4_off",
        options=[],
    )
    _ensure(
        by,
        "comboBox_S5_AC",
        label="交流电源",
        default="关闭",
        type="select",
        group="step4_off",
        options=["关闭", "开启"],
    )
    for j in range(1, 5):
        _ensure(
            by,
            f"checkBox_S5_DC{j}",
            label=f"直流电源{j}",
            default=True,
            type="checkbox",
            group="step4_off",
            options=[],
        )
        _ensure(
            by,
            f"comboBox_S5_DC{j}",
            label=f"直流{j}关机",
            default="关闭",
            type="select",
            group="step4_off",
            options=["关闭", "开启"],
        )

    data["fields"] = sorted(by.values(), key=lambda x: (x.get("group") or "", x["name"]))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"patched {path.name} fields={len(data['fields'])}")


def main() -> None:
    _patch(IOT)
    if SW.is_file():
        _patch(SW)


if __name__ == "__main__":
    main()
