# -*- coding: utf-8 -*-
"""对齐谐波电流 Web schema 与桌面 Dialog_thaixiebodianliu 可见控件。"""
from __future__ import annotations

import json
from pathlib import Path

IOT = Path(r"E:/IOT/iot/app/services/solar_test_schemas/harmonic_fields.json")
SW = Path(r"E:/solarautotestnewui/utils/iot_harmonic_schema_data.json")

# 与 Dialog_thaixiebodianliu._HARMONIC_SPECS 一致
_HARMONIC_SPECS = [
    {
        "title": "谐波 1次",
        "step_cb": "checkBox_S3",
        "dc1_cb": "checkBox_S1_DC1_2",
        "dc2_cb": "checkBox_S1_DC2_2",
        "dc3_cb": "checkBox_S1_DC3_2",
        "dc4_cb": "checkBox_S1_DC4_2",
        "pf_te": "textEdit_S1_DC1_PF_2",
    },
    {
        "title": "谐波 2次",
        "step_cb": "checkBox_S3_2",
        "dc1_cb": "checkBox_S1_DC1_3",
        "dc2_cb": "checkBox_S1_DC2_3",
        "dc3_cb": "checkBox_S1_DC3_3",
        "dc4_cb": "checkBox_S1_DC4_3",
        "pf_te": "textEdit_S1_DC1_PF_3",
    },
    {
        "title": "谐波 3次",
        "step_cb": "checkBox_S3_3",
        "dc1_cb": "checkBox_S1_DC1_4",
        "dc2_cb": "checkBox_S1_DC2_4",
        "dc3_cb": "checkBox_S1_DC3_4",
        "dc4_cb": "checkBox_S1_DC4_4",
        "pf_te": "textEdit_S1_DC1_PF_4",
    },
    {
        "title": "谐波 4次",
        "step_cb": "checkBox_S3_4",
        "dc1_cb": "checkBox_S1_DC1_5",
        "dc2_cb": "checkBox_S1_DC2_5",
        "dc3_cb": "checkBox_S1_DC3_5",
        "dc4_cb": "checkBox_S1_DC4_5",
        "pf_te": "textEdit_S1_DC1_PF_5",
    },
    {
        "title": "谐波 5次",
        "step_cb": "checkBox_S3_5",
        "dc1_cb": "checkBox_S1_DC1_6",
        "dc2_cb": "checkBox_S1_DC2_6",
        "dc3_cb": "checkBox_S1_DC3_6",
        "dc4_cb": "checkBox_S1_DC4_6",
        "pf_te": "textEdit_S1_DC1_PF_6",
    },
    {
        "title": "谐波 6次",
        "step_cb": "checkBox_S3_10",
        "dc1_cb": "checkBox_S1_DC1_10",
        "dc2_cb": "checkBox_S1_DC2_11",
        "dc3_cb": "checkBox_S1_DC3_10",
        "dc4_cb": "checkBox_S1_DC4_7",
        "pf_te": "textEdit_S1_DC1_PF_10",
    },
    {
        "title": "谐波 7次",
        "step_cb": "checkBox_S3_6",
        "dc1_cb": "checkBox_S1_DC1_11",
        "dc2_cb": "checkBox_S1_DC2_8",
        "dc3_cb": "checkBox_S1_DC3_11",
        "dc4_cb": "checkBox_S1_DC3_15",
        "pf_te": "textEdit_S1_DC1_PF_9",
    },
    {
        "title": "谐波 8次",
        "step_cb": "checkBox_S3_7",
        "dc1_cb": "checkBox_S1_DC1_7",
        "dc2_cb": "checkBox_S1_DC2_9",
        "dc3_cb": "checkBox_S1_DC3_8",
        "dc4_cb": "checkBox_S1_DC3_14",
        "pf_te": "textEdit_S1_DC1_PF_7",
    },
    {
        "title": "谐波 9次",
        "step_cb": "checkBox_S3_9",
        "dc1_cb": "checkBox_S1_DC1_9",
        "dc2_cb": "checkBox_S1_DC2_10",
        "dc3_cb": "checkBox_S1_DC3_9",
        "dc4_cb": "checkBox_S1_DC3_16",
        "pf_te": "textEdit_S1_DC1_PF_11",
    },
    {
        "title": "谐波 10次",
        "step_cb": "checkBox_S3_8",
        "dc1_cb": "checkBox_S1_DC1_8",
        "dc2_cb": "checkBox_S1_DC2_7",
        "dc3_cb": "checkBox_S1_DC3_7",
        "dc4_cb": "checkBox_S1_DC3_17",
        "pf_te": "textEdit_S1_DC1_PF_8",
    },
    {
        "title": "谐波 11次",
        "step_cb": "checkBox_S3_11",
        "dc1_cb": "checkBox_S1_DC1_12",
        "dc2_cb": "checkBox_S1_DC2_12",
        "dc3_cb": "checkBox_S1_DC3_12",
        "dc4_cb": "checkBox_S1_DC3_13",
        "pf_te": "textEdit_S1_DC1_PF_12",
    },
]

_TIMING = {
    "textEdit_S3_TIME_2": {
        "label": "数据采集",
        "default": "10",
        "type": "text",
        "group": "step3_harm",
    },
    "comboBox_S3_TIME_2": {
        "label": "数据采集单位",
        "default": "分钟",
        "type": "select",
        "group": "step3_harm",
        "options": ["分钟", "秒", "毫秒"],
    },
    "textEdit_S3_TIME_3": {
        "label": "等待时间",
        "default": "1",
        "type": "text",
        "group": "step3_harm",
    },
    "comboBox_S3_TIME_3": {
        "label": "等待时间单位",
        "default": "秒",
        "type": "select",
        "group": "step3_harm",
        "options": ["秒", "分钟", "毫秒"],
    },
    "comboBox_S3_record_mode": {
        "label": "录波方式",
        "default": "分开录（多文件/逐点存盘）",
        "type": "select",
        "group": "step3_harm",
        "options": [
            "一条线连续录（单文件）",
            "分开录（多文件/逐点存盘）",
        ],
    },
}

_OFF = {
    "checkBox_S5": {"label": "启用关机", "default": True, "group": "step4_off", "type": "checkbox"},
    "comboBox_S5_AC": {
        "label": "交流电源",
        "default": "关闭",
        "group": "step4_off",
        "type": "select",
        "options": ["关闭", "开启"],
    },
    "checkBox_S5_DC1": {"label": "直流电源1", "default": True, "group": "step4_off", "type": "checkbox"},
    "checkBox_S5_DC2": {"label": "直流电源2", "default": False, "group": "step4_off", "type": "checkbox"},
    "checkBox_S5_DC3": {"label": "直流电源3", "default": False, "group": "step4_off", "type": "checkbox"},
    "checkBox_S5_DC4": {"label": "直流电源4", "default": False, "group": "step4_off", "type": "checkbox"},
    "comboBox_S5_DC1": {
        "label": "直流1关机",
        "default": "关闭",
        "group": "step4_off",
        "type": "select",
        "options": ["关闭", "开启"],
    },
    "comboBox_S5_DC2": {
        "label": "直流2关机",
        "default": "关闭",
        "group": "step4_off",
        "type": "select",
        "options": ["关闭", "开启"],
    },
    "comboBox_S5_DC3": {
        "label": "直流3关机",
        "default": "关闭",
        "group": "step4_off",
        "type": "select",
        "options": ["关闭", "开启"],
    },
    "comboBox_S5_DC4": {
        "label": "直流4关机",
        "default": "关闭",
        "group": "step4_off",
        "type": "select",
        "options": ["关闭", "开启"],
    },
}


def _ensure(fields: dict, name: str, **kw):
    base = {
        "name": name,
        "label": name,
        "type": "text",
        "group": "other",
        "default": None,
        "options": [],
    }
    if name not in fields:
        fields[name] = dict(base)
    fields[name].update({k: v for k, v in kw.items() if v is not None})


def _patch(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    by = {f["name"]: f for f in data.get("fields") or []}

    # 分组标题
    for g in data.get("groups") or []:
        if g.get("id") == "step3_harm":
            g["title"] = "③ 谐波设置"
        if g.get("id") == "step4_off":
            g["title"] = "④ 关机设置"

    # 谐波卡片字段：从 step1 误分到 step3，补中文标签与默认
    for spec in _HARMONIC_SPECS:
        title = spec["title"]
        _ensure(
            by,
            spec["step_cb"],
            label=title,
            type="checkbox",
            group="step3_harm",
            default=True,
            options=[],
        )
        for key, zh in (
            ("dc1_cb", "直流电源1"),
            ("dc2_cb", "直流电源2"),
            ("dc3_cb", "直流电源3"),
            ("dc4_cb", "直流电源4"),
        ):
            _ensure(
                by,
                spec[key],
                label=f"{title}·{zh}",
                type="checkbox",
                group="step3_harm",
                default=False,
                options=[],
            )
        _ensure(
            by,
            spec["pf_te"],
            label=f"{title}·功率%",
            type="text",
            group="step3_harm",
            default="100",
            options=[],
        )

    for name, meta in _TIMING.items():
        _ensure(by, name, **meta)

    for name, meta in _OFF.items():
        _ensure(by, name, **meta)

    # 启机 DC 勾选（step1）不要与谐波卡片 DC 混淆：仅保留 checkBox_S1_DC1..4
    step1_dc_keep = {
        "checkBox_S1_DC1",
        "checkBox_S1_DC2",
        "checkBox_S1_DC3",
        "checkBox_S1_DC4",
    }
    for name, f in list(by.items()):
        if name.startswith("checkBox_S1_DC") and name not in step1_dc_keep:
            # 已作为谐波卡片控件处理
            if f.get("group") == "step1_ac":
                f["group"] = "step3_harm"
        if name.startswith("textEdit_S1_DC1_PF_") and f.get("group") == "step1_ac":
            f["group"] = "step3_harm"
        if name.startswith("textEdit_S1_DC") and "_PF_" not in name and name.count("_") >= 3:
            # 启机 Vmp/Imp 等仍属 step1_dc
            pass

    data["fields"] = sorted(by.values(), key=lambda x: (x.get("group") or "", x["name"]))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"patched {path} fields={len(data['fields'])}")


def main() -> None:
    _patch(IOT)
    if SW.is_file():
        _patch(SW)


if __name__ == "__main__":
    main()
