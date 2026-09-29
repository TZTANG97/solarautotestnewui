# -*- coding: utf-8 -*-
"""对齐序15 ROCOF保护：Web schema ↔ Dialog_thairocof。"""
from __future__ import annotations

import json
from pathlib import Path

IOT = Path(r"E:/IOT/iot/app/services/solar_test_schemas")
SW = Path(r"E:/solarautotestnewui/utils")

# Dialog 默认：ROCOF1~4 勾选并填值；5~6 取消勾选
_ROCOF_DEFAULTS = {
    3: ("50", "52", "2"),
    4: ("50", "48", "2"),
    5: ("50", "52", "1"),
    6: ("50", "48", "1"),
}


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _save(p: Path, data: dict) -> None:
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _by(data: dict) -> dict:
    return {f["name"]: f for f in data.get("fields") or []}


def _put(by: dict, name: str, **kw):
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
    if "options" in kw and kw["options"] is not None:
        by[name]["options"] = list(kw["options"])


def _finish(data: dict, by: dict) -> dict:
    data["fields"] = sorted(by.values(), key=lambda x: (x.get("group") or "", x["name"]))
    return data


def patch_rocof(data: dict) -> dict:
    by = _by(data)

    _put(by, "checkBox_S1", label="启用步骤1 AC/DC", default=True, type="checkbox", group="step1_ac")
    _put(
        by,
        "comboBox_S1_AC",
        label="交流电源",
        default="开启",
        type="select",
        group="step1_ac",
        options=["开启", "关闭"],
    )
    _put(
        by,
        "comboBox_S1_AC_2",
        label="相数",
        default="单相",
        type="select",
        group="step1_ac",
        options=["单相", "三相"],
    )
    _put(by, "textEdit_S1_AC_VOLT", label="交流电压1", default="230", type="text", group="step1_ac")
    _put(by, "textEdit_S1_AC_VOLT_2", label="交流电压2", default="230", type="text", group="step1_ac")
    _put(by, "textEdit_S1_AC_VOLT_3", label="交流电压3", default="230", type="text", group="step1_ac")
    _put(by, "textEdit_S1_AC_FR", label="交流频率", default="50", type="text", group="step1_ac")
    for i in range(1, 5):
        _put(
            by,
            f"checkBox_S1_DC{i}",
            label=f"直流电源{i}",
            default=(i == 1),
            type="checkbox",
            group="step1_dc",
        )
        _put(
            by,
            f"comboBox_S1_DC{i}",
            label="开关",
            default="开启",
            type="select",
            group="step1_dc",
            options=["开启", "关闭"],
        )

    _put(by, "checkBox_S2", label="启用功率分析仪", default=True, type="checkbox", group="step2_wt")
    _put(
        by,
        "checkBox_rocof_page",
        label="启用ROCOF设置",
        default=True,
        type="checkbox",
        group="step3_rocof",
    )

    for i in range(6):
        step = 3 + i
        n = i + 1
        enabled = step <= 6 and step in _ROCOF_DEFAULTS
        # cards 5-6 (step 7-8) unchecked; 1-4 (step 3-6) checked with defaults
        if step >= 7:
            enabled_cb = False
            start = end = rate = None
        else:
            enabled_cb = True
            start, end, rate = _ROCOF_DEFAULTS[step]
        _put(
            by,
            f"checkBox_S{step}",
            label=f"启用ROCOF{n}",
            default=enabled_cb,
            type="checkbox",
            group="step3_rocof",
        )
        _put(
            by,
            f"checkBox_S{step}_RATE",
            label=f"ROCOF{n} 更新率",
            default=True,
            type="checkbox",
            group="step3_rocof",
        )
        _put(
            by,
            f"textEdit_S{step}_freq_start_rocof",
            label=f"ROCOF{n} 起点(Hz)",
            default=start,
            type="text",
            group="step3_rocof",
        )
        _put(
            by,
            f"textEdit_S{step}_freq_end_rocof",
            label=f"ROCOF{n} 终点(Hz)",
            default=end,
            type="text",
            group="step3_rocof",
        )
        _put(
            by,
            f"textEdit_S{step}_rocof_hz_s_rocof",
            label=f"ROCOF{n} (Hz/s)",
            default=rate,
            type="text",
            group="step3_rocof",
        )
        _put(
            by,
            f"textEdit_S{step}_test_duration_rocof",
            label=f"ROCOF{n} 数据采集",
            default="2",
            type="text",
            group="step3_rocof",
        )
        _put(
            by,
            f"comboBox_S{step}_test_time_unit_rocof",
            label=f"ROCOF{n} 单位",
            default="秒",
            type="select",
            group="step3_rocof",
            options=["秒", "分钟", "小时"],
        )

    _put(by, "checkBox_S_End", label="启用关机", default=True, type="checkbox", group="step4_off")
    _put(
        by,
        "comboBox_S_End_AC",
        label="交流电源",
        default="关闭",
        type="select",
        group="step4_off",
        options=["关闭", "开启"],
    )
    for i in range(1, 5):
        _put(
            by,
            f"checkBox_S_End_DC{i}",
            label=f"直流电源{i}",
            default=True,
            type="checkbox",
            group="step4_off",
        )
        _put(
            by,
            f"comboBox_S_End_DC{i}",
            label=f"直流电源{i}关机",
            default="关闭",
            type="select",
            group="step4_off",
            options=["关闭", "开启"],
        )

    for g in data.get("groups") or []:
        if g.get("id") == "step3_rocof":
            g["title"] = "③ ROCOF设置"
        elif g.get("id") == "step4_off":
            g["title"] = "④ 关机设置"

    data["title"] = "ROCOF保护"
    data["testType"] = "rocof"
    return _finish(data, by)


def main() -> None:
    iot = IOT / "rocof_fields.json"
    data = patch_rocof(_load(iot))
    _save(iot, data)
    sw = SW / "iot_rocof_schema_data.json"
    if sw.is_file():
        _save(sw, patch_rocof(_load(sw)))
    print(f"ok rocof fields={len(data['fields'])}")


if __name__ == "__main__":
    main()
