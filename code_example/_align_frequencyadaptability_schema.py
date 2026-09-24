# -*- coding: utf-8 -*-
"""对齐序13 频率适应性：Web schema ↔ Dialog_thaifrequencyadaptability。"""
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


def _finish(data: dict, by: dict) -> dict:
    data["fields"] = sorted(by.values(), key=lambda x: (x.get("group") or "", x["name"]))
    return data


def patch_frequencyadaptability(data: dict) -> dict:
    by = _by(data)

    # ① AC/DC（与已验收项一致）
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
            _put(
                by,
                f"textEdit_S1_DC{i}_{key}",
                label=lab,
                type="text",
                group="step1_dc",
            )

    # ② 分析仪
    _put(by, "checkBox_S2", label="启用功率分析仪", default=True, type="checkbox", group="step2_wt")
    _put(by, "radio_wt", label="功率分析仪", type="radio", group="step2_wt")
    _put(by, "radio_dewetron", label="德威创", type="radio", group="step2_dew")

    # ③ 过频：页开关 + 9 卡片（Dialog 默认仅第1卡启用，50~51.5Hz / 30s）
    _put(
        by,
        "checkBox_guopin_page",
        label="启用过频设置",
        default=True,
        type="checkbox",
        group="step3_of",
    )
    for i in range(9):
        step = 3 + i
        n = i + 1
        _put(
            by,
            f"checkBox_S{step}",
            label=f"启用过频{n}",
            default=(i == 0),
            type="checkbox",
            group="step3_of",
        )
        _put(
            by,
            f"checkBox_S{step}_RATE",
            label=f"过频{n} 更新率",
            default=True,
            type="checkbox",
            group="step3_of",
        )
        _put(
            by,
            f"textEdit_S{step}_freq_start_guopin",
            label=f"过频{n} 起点(Hz)",
            default=("50" if i == 0 else None),
            type="text",
            group="step3_of",
        )
        _put(
            by,
            f"textEdit_S{step}_freq_end_guopin",
            label=f"过频{n} 终点(Hz)",
            default=("51.5" if i == 0 else None),
            type="text",
            group="step3_of",
        )
        _put(
            by,
            f"textEdit_S{step}_test_duration_guopin",
            label=f"过频{n} 数据采集",
            default=("30" if i == 0 else None),
            type="text",
            group="step3_of",
        )
        _put(
            by,
            f"comboBox_S{step}_test_time_unit_guopin",
            label=f"过频{n} 单位",
            default="秒",
            type="select",
            group="step3_of",
            options=["秒", "分钟", "小时"],
        )

    # ④ 欠频：页默认关；第1卡预填 50~47.5 / 30s（页关时不跑）
    _put(
        by,
        "checkBox_qianpin_page",
        label="启用欠频设置",
        default=False,
        type="checkbox",
        group="step4_uf",
    )
    for i in range(9):
        step = 12 + i
        n = i + 1
        _put(
            by,
            f"checkBox_S{step}",
            label=f"启用欠频{n}",
            default=False,
            type="checkbox",
            group="step4_uf",
        )
        _put(
            by,
            f"checkBox_S{step}_RATE",
            label=f"欠频{n} 更新率",
            default=True,
            type="checkbox",
            group="step4_uf",
        )
        _put(
            by,
            f"textEdit_S{step}_freq_start_qianpin",
            label=f"欠频{n} 起点(Hz)",
            default=("50" if i == 0 else None),
            type="text",
            group="step4_uf",
        )
        _put(
            by,
            f"textEdit_S{step}_freq_end_qianpin",
            label=f"欠频{n} 终点(Hz)",
            default=("47.5" if i == 0 else None),
            type="text",
            group="step4_uf",
        )
        _put(
            by,
            f"textEdit_S{step}_test_duration_qianpin",
            label=f"欠频{n} 数据采集",
            default=("30" if i == 0 else None),
            type="text",
            group="step4_uf",
        )
        _put(
            by,
            f"comboBox_S{step}_test_time_unit_qianpin",
            label=f"欠频{n} 单位",
            default="秒",
            type="select",
            group="step4_uf",
            options=["秒", "分钟", "小时"],
        )

    # ⑤ 关机
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

    for gid, title in (
        ("step1_ac", "① AC 电源"),
        ("step1_dc", "① DC 电源"),
        ("step2_wt", "② 功率分析仪"),
        ("step2_dew", "② 德威创"),
        ("step3_of", "③ 过频设置"),
        ("step4_uf", "④ 欠频设置"),
        ("step5_off", "⑤ 关机设置"),
    ):
        _title(data, gid, title)

    data["title"] = "频率适应性"
    data["testType"] = "frequencyadaptability"
    return _finish(data, by)


def main() -> None:
    iot = IOT / "frequencyadaptability_fields.json"
    data = patch_frequencyadaptability(_load(iot))
    _save(iot, data)
    sw = SW / "iot_frequencyadaptability_schema_data.json"
    if sw.is_file():
        _save(sw, patch_frequencyadaptability(_load(sw)))
    print(f"ok frequencyadaptability fields={len(data['fields'])}")


if __name__ == "__main__":
    main()
