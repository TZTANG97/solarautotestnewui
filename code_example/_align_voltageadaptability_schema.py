# -*- coding: utf-8 -*-
"""对齐序14 电压适应性：Web schema ↔ Dialog_thaivoltageadaptability。"""
from __future__ import annotations

import json
from pathlib import Path

IOT = Path(r"E:/IOT/iot/app/services/solar_test_schemas")
SW = Path(r"E:/solarautotestnewui/utils")


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


def _title(data: dict, gid: str, title: str) -> None:
    for g in data.get("groups") or []:
        if g.get("id") == gid:
            g["title"] = title


def _ensure_groups(data: dict) -> None:
    want = [
        ("step1_ac", "① AC 电源"),
        ("step1_dc", "① DC 电源"),
        ("step2_wt", "② 功率分析仪"),
        ("step2_dew", "② 德威创"),
        ("step2_wt_cfg", "② 功率分析仪 · 测量/存盘"),
        ("step3_ov", "③ 过压设置"),
        ("step4_uv", "④ 欠压设置"),
        ("step5_off", "⑤ 关机设置"),
        ("other", "其它"),
    ]
    have = {g.get("id"): g for g in (data.get("groups") or [])}
    groups = []
    for gid, title in want:
        if gid in have:
            have[gid]["title"] = title
            groups.append(have[gid])
        else:
            groups.append({"id": gid, "title": title})
    for gid, g in have.items():
        if gid not in {x[0] for x in want}:
            groups.append(g)
    data["groups"] = groups


def _finish(data: dict, by: dict) -> dict:
    data["fields"] = sorted(by.values(), key=lambda x: (x.get("group") or "", x["name"]))
    return data


def patch_voltageadaptability(data: dict) -> dict:
    by = _by(data)
    _ensure_groups(data)

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
    _put(by, "textEdit_S1_ACWaitTIME", label="等待时间", default="3", type="text", group="step1_ac")
    _put(
        by,
        "comboBox_S1_ACWaitTIME",
        label="等待时间单位",
        default="秒",
        type="select",
        group="step1_ac",
        options=["秒", "分钟", "毫秒"],
    )
    _put(by, "textEdit_S1_TIME", label="启机时间", default="1", type="text", group="step1_ac")
    _put(
        by,
        "comboBox_S1_TIME",
        label="启机时间单位",
        default="分钟",
        type="select",
        group="step1_ac",
        options=["分钟", "秒", "毫秒"],
    )
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
        for key, lab in (
            ("VOLT", "Vmp"),
            ("CURR", "Imp"),
            ("Voc", "Voc"),
            ("Isc", "Isc"),
            ("PF", "功率%"),
        ):
            _put(by, f"textEdit_S1_DC{i}_{key}", label=lab, type="text", group="step1_dc")

    _put(by, "checkBox_S2", label="启用功率分析仪", default=True, type="checkbox", group="step2_wt")
    _put(by, "radio_wt", label="功率分析仪", type="radio", group="step2_wt")
    _put(by, "radio_dewetron", label="德威创", type="radio", group="step2_dew")
    _put(
        by,
        "checkBox_S2_split_ov_uv_files",
        label="过压/欠压分开录波文件",
        default=False,
        type="checkbox",
        group="step2_wt",
    )

    # 过压：list 优先；卡片作清空 list 时的回退
    _put(by, "checkBox_guoya_page", label="启用过压设置", default=True, type="checkbox", group="step3_ov")
    _put(
        by,
        "textEdit_VoltageLadder_guoya",
        label="过压 list (V@s)",
        default="230-253@30\n253-230@30",
        type="text",
        group="step3_ov",
    )
    for i in range(9):
        step = 3 + i
        n = i + 1
        _put(
            by,
            f"checkBox_S{step}",
            label=f"启用过压{n}",
            default=(i == 0),
            type="checkbox",
            group="step3_ov",
        )
        _put(
            by,
            f"checkBox_S{step}_RATE",
            label=f"过压{n} 更新率",
            default=True,
            type="checkbox",
            group="step3_ov",
        )
        _put(
            by,
            f"textEdit_S{step}_volt_start_guoya",
            label=f"过压{n} 起点(V)",
            default=("230" if i == 0 else None),
            type="text",
            group="step3_ov",
        )
        _put(
            by,
            f"textEdit_S{step}_volt_end_guoya",
            label=f"过压{n} 终点(V)",
            default=("253" if i == 0 else None),
            type="text",
            group="step3_ov",
        )
        _put(
            by,
            f"textEdit_S{step}_test_duration_guoya",
            label=f"过压{n} 数据采集",
            default=("30" if i == 0 else None),
            type="text",
            group="step3_ov",
        )
        _put(
            by,
            f"comboBox_S{step}_test_time_unit_guoya",
            label=f"过压{n} 单位",
            default="秒",
            type="select",
            group="step3_ov",
            options=["秒", "分钟", "小时"],
        )

    _put(by, "checkBox_qianya_page", label="启用欠压设置", default=False, type="checkbox", group="step4_uv")
    _put(
        by,
        "textEdit_VoltageLadder_qianya",
        label="欠压 list (V@s)",
        default="",
        type="text",
        group="step4_uv",
    )
    for i in range(9):
        step = 12 + i
        n = i + 1
        _put(
            by,
            f"checkBox_S{step}",
            label=f"启用欠压{n}",
            default=False,
            type="checkbox",
            group="step4_uv",
        )
        _put(
            by,
            f"checkBox_S{step}_RATE",
            label=f"欠压{n} 更新率",
            default=True,
            type="checkbox",
            group="step4_uv",
        )
        _put(
            by,
            f"textEdit_S{step}_volt_start_qianya",
            label=f"欠压{n} 起点(V)",
            default=("230" if i == 0 else None),
            type="text",
            group="step4_uv",
        )
        _put(
            by,
            f"textEdit_S{step}_volt_end_qianya",
            label=f"欠压{n} 终点(V)",
            default=("195" if i == 0 else None),
            type="text",
            group="step4_uv",
        )
        _put(
            by,
            f"textEdit_S{step}_test_duration_qianya",
            label=f"欠压{n} 数据采集",
            default=("30" if i == 0 else None),
            type="text",
            group="step4_uv",
        )
        _put(
            by,
            f"comboBox_S{step}_test_time_unit_qianya",
            label=f"欠压{n} 单位",
            default="秒",
            type="select",
            group="step4_uv",
            options=["秒", "分钟", "小时"],
        )

    _put(by, "checkBox_S_End", label="启用关机", default=True, type="checkbox", group="step5_off")
    _put(
        by,
        "comboBox_S_End_AC",
        label="交流电源",
        default="关闭",
        type="select",
        group="step5_off",
        options=["关闭", "开启"],
    )
    for i in range(1, 5):
        _put(
            by,
            f"checkBox_S_End_DC{i}",
            label=f"直流电源{i}",
            default=True,
            type="checkbox",
            group="step5_off",
        )
        _put(
            by,
            f"comboBox_S_End_DC{i}",
            label=f"直流电源{i}关机",
            default="关闭",
            type="select",
            group="step5_off",
            options=["关闭", "开启"],
        )

    data["title"] = "电压适应性"
    data["testType"] = "voltageadaptability"
    return _finish(data, by)


def main() -> None:
    iot = IOT / "voltageadaptability_fields.json"
    data = patch_voltageadaptability(_load(iot))
    _save(iot, data)
    sw = SW / "iot_voltageadaptability_schema_data.json"
    if sw.is_file():
        _save(sw, patch_voltageadaptability(_load(sw)))
    print(f"ok voltageadaptability fields={len(data['fields'])}")


if __name__ == "__main__":
    main()
