# -*- coding: utf-8 -*-
"""对齐直流分量 Web schema 与 Dialog_thaizhiliufenliang 可见控件。"""
from __future__ import annotations

import json
from pathlib import Path

IOT = Path(r"E:/IOT/iot/app/services/solar_test_schemas/dccomponent_fields.json")
SW = Path(r"E:/solarautotestnewui/utils/iot_dccomponent_schema_data.json")

MODE_CONT = "一条线连续录（单文件）"
MODE_SPLIT = "分开录（多文件/逐点存盘）"

PATCHES = {
    # ③ 100%Pn
    "checkBox_S3": {
        "label": "启用 100%Pn",
        "default": True,
        "group": "step3_pn100",
        "type": "checkbox",
    },
    "checkBox_S3_DC1": {
        "label": "100%Pn·直流电源1",
        "default": True,
        "group": "step3_pn100",
        "type": "checkbox",
    },
    "checkBox_S3_DC2": {
        "label": "100%Pn·直流电源2",
        "default": True,
        "group": "step3_pn100",
        "type": "checkbox",
    },
    "checkBox_S3_DC3": {
        "label": "100%Pn·直流电源3",
        "default": True,
        "group": "step3_pn100",
        "type": "checkbox",
    },
    "checkBox_S3_DC4": {
        "label": "100%Pn·直流电源4",
        "default": True,
        "group": "step3_pn100",
        "type": "checkbox",
    },
    "textEdit_S3_DC_PF": {
        "label": "功率%",
        "default": "100",
        "group": "step3_pn100",
        "type": "text",
    },
    "textEdit_S3_TIME_2": {
        "label": "数据采集",
        "default": "5",
        "group": "step3_pn100",
        "type": "text",
    },
    "comboBox_S3_TIME_2": {
        "label": "数据采集单位",
        "default": "分钟",
        "group": "step3_pn100",
        "type": "select",
        "options": ["分钟", "秒", "毫秒"],
    },
    "textEdit_S3_TIME_3": {
        "label": "等待时间",
        "default": "1",
        "group": "step3_pn100",
        "type": "text",
    },
    "comboBox_S3_TIME_3": {
        "label": "等待时间单位",
        "default": "分钟",
        "group": "step3_pn100",
        "type": "select",
        "options": ["分钟", "秒", "毫秒"],
    },
    "comboBox_S3_record_mode": {
        "label": "录波方式",
        "default": MODE_CONT,
        "group": "step3_pn100",
        "type": "select",
        "options": [MODE_CONT, MODE_SPLIT],
    },
    # ④ 66%
    "checkBox_S4": {
        "label": "启用 66%Pn",
        "default": True,
        "group": "step4_pn66",
        "type": "checkbox",
    },
    "checkBox_S4_DC1": {
        "label": "66%Pn·直流电源1",
        "default": True,
        "group": "step4_pn66",
        "type": "checkbox",
    },
    "checkBox_S4_DC2": {
        "label": "66%Pn·直流电源2",
        "default": True,
        "group": "step4_pn66",
        "type": "checkbox",
    },
    "checkBox_S4_DC3": {
        "label": "66%Pn·直流电源3",
        "default": True,
        "group": "step4_pn66",
        "type": "checkbox",
    },
    "checkBox_S4_DC4": {
        "label": "66%Pn·直流电源4",
        "default": True,
        "group": "step4_pn66",
        "type": "checkbox",
    },
    "textEdit_S4_DC_PF": {
        "label": "功率%",
        "default": "66",
        "group": "step4_pn66",
        "type": "text",
    },
    # ⑤ 33%
    "checkBox_S5": {
        "label": "启用 33%Pn",
        "default": True,
        "group": "step5_pn33",
        "type": "checkbox",
    },
    "checkBox_S5_DC1": {
        "label": "33%Pn·直流电源1",
        "default": True,
        "group": "step5_pn33",
        "type": "checkbox",
    },
    "checkBox_S5_DC2": {
        "label": "33%Pn·直流电源2",
        "default": True,
        "group": "step5_pn33",
        "type": "checkbox",
    },
    "checkBox_S5_DC3": {
        "label": "33%Pn·直流电源3",
        "default": True,
        "group": "step5_pn33",
        "type": "checkbox",
    },
    "checkBox_S5_DC4": {
        "label": "33%Pn·直流电源4",
        "default": True,
        "group": "step5_pn33",
        "type": "checkbox",
    },
    "textEdit_S5_DC_PF": {
        "label": "功率%",
        "default": "33",
        "group": "step5_pn33",
        "type": "text",
    },
    # ⑥ 可选
    "checkBox_S6": {
        "label": "启用可选功率点",
        "default": False,
        "group": "step6_optional",
        "type": "checkbox",
    },
    "checkBox_S6_DC1": {
        "label": "可选·直流电源1",
        "default": True,
        "group": "step6_optional",
        "type": "checkbox",
    },
    "checkBox_S6_DC2": {
        "label": "可选·直流电源2",
        "default": True,
        "group": "step6_optional",
        "type": "checkbox",
    },
    "checkBox_S6_DC3": {
        "label": "可选·直流电源3",
        "default": True,
        "group": "step6_optional",
        "type": "checkbox",
    },
    "checkBox_S6_DC4": {
        "label": "可选·直流电源4",
        "default": True,
        "group": "step6_optional",
        "type": "checkbox",
    },
    "textEdit_S6_DC_PF": {
        "label": "功率%",
        "default": "20",
        "group": "step6_optional",
        "type": "text",
    },
    # ⑦ 关机
    "checkBox_S7": {
        "label": "启用关机",
        "default": True,
        "group": "step7_off",
        "type": "checkbox",
    },
    "comboBox_S7_AC": {
        "label": "交流电源",
        "default": "关闭",
        "group": "step7_off",
        "type": "select",
        "options": ["关闭", "开启"],
    },
    "checkBox_S7_DC1": {
        "label": "直流电源1",
        "default": True,
        "group": "step7_off",
        "type": "checkbox",
    },
    "checkBox_S7_DC2": {
        "label": "直流电源2",
        "default": True,
        "group": "step7_off",
        "type": "checkbox",
    },
    "checkBox_S7_DC3": {
        "label": "直流电源3",
        "default": True,
        "group": "step7_off",
        "type": "checkbox",
    },
    "checkBox_S7_DC4": {
        "label": "直流电源4",
        "default": True,
        "group": "step7_off",
        "type": "checkbox",
    },
    "comboBox_S7_DC1": {
        "label": "直流1关机",
        "default": "关闭",
        "group": "step7_off",
        "type": "select",
        "options": ["关闭", "开启"],
    },
    "comboBox_S7_DC2": {
        "label": "直流2关机",
        "default": "关闭",
        "group": "step7_off",
        "type": "select",
        "options": ["关闭", "开启"],
    },
    "comboBox_S7_DC3": {
        "label": "直流3关机",
        "default": "关闭",
        "group": "step7_off",
        "type": "select",
        "options": ["关闭", "开启"],
    },
    "comboBox_S7_DC4": {
        "label": "直流4关机",
        "default": "关闭",
        "group": "step7_off",
        "type": "select",
        "options": ["关闭", "开启"],
    },
}

GROUP_TITLES = {
    "step3_pn100": "③ 100%Pn",
    "step4_pn66": "④ 66%Pn",
    "step5_pn33": "⑤ 33%Pn",
    "step6_optional": "⑥ 可选功率点",
    "step7_off": "⑦ 关机设置",
}


def _patch(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    by = {f["name"]: f for f in data.get("fields") or []}
    for g in data.get("groups") or []:
        gid = g.get("id")
        if gid in GROUP_TITLES:
            g["title"] = GROUP_TITLES[gid]
    for name, meta in PATCHES.items():
        if name not in by:
            by[name] = {
                "name": name,
                "label": name,
                "type": "text",
                "group": "other",
                "default": None,
                "options": [],
            }
        by[name].update(meta)
        if "options" in meta:
            by[name]["options"] = list(meta["options"])
    data["fields"] = sorted(by.values(), key=lambda x: (x.get("group") or "", x["name"]))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"patched {path.name} fields={len(data['fields'])}")


def main() -> None:
    _patch(IOT)
    if SW.is_file():
        _patch(SW)


if __name__ == "__main__":
    main()
