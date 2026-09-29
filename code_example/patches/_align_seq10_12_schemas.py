# -*- coding: utf-8 -*-
"""对齐 过频降载/欠频升载 关机标签 + 审计 10min过压保护。"""
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


def _finish(data: dict, by: dict) -> dict:
    data["fields"] = sorted(by.values(), key=lambda x: (x.get("group") or "", x["name"]))
    return data


def patch_freq_ladder(data: dict, off_gid: str = "step4_off") -> dict:
    by = _by(data)
    _put(by, "checkBox_S_End", label="启用关机", default=True, type="checkbox", group=off_gid)
    _put(
        by,
        "comboBox_S_End_AC",
        label="交流电源",
        default="关闭",
        type="select",
        group=off_gid,
        options=["关闭", "开启"],
    )
    for i in range(1, 5):
        _put(
            by,
            f"checkBox_S_End_DC{i}",
            label=f"直流电源{i}",
            default=True,
            type="checkbox",
            group=off_gid,
        )
        _put(
            by,
            f"comboBox_S_End_DC{i}",
            label=f"直流电源{i}关机",
            default="关闭",
            type="select",
            group=off_gid,
            options=["关闭", "开启"],
        )
    return _finish(data, by)


def patch_voltprotect(data: dict) -> dict:
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
    _put(by, "textEdit_S1_AC_FR", label="频率", default="50", type="text", group="step1_ac")

    _put(by, "checkBox_S3", label="启用过压保护", default=True, type="checkbox", group="step3_protect")
    _put(by, "textEdit_S3_AC_VOLT", label="交流电压L1", default="230", type="text", group="step3_protect")
    _put(by, "textEdit_S3_AC_VOLT_2", label="交流电压L2", default="230", type="text", group="step3_protect")
    _put(by, "textEdit_S3_AC_VOLT_3", label="交流电压L3", default="230", type="text", group="step3_protect")
    _put(by, "textEdit_S3_TIME", label="数据采集", default="10", type="text", group="step3_protect")
    _put(
        by,
        "comboBox_S3_TIME",
        label="数据采集单位",
        default="分钟",
        type="select",
        group="step3_protect",
        options=["分钟", "秒", "毫秒"],
    )

    _put(by, "checkBox_S4", label="启用保护后恢复", default=True, type="checkbox", group="step4_recover")
    _put(by, "textEdit_S4_AC_VOLT", label="交流电压L1", default="230", type="text", group="step4_recover")
    _put(by, "textEdit_S4_AC_VOLT_2", label="交流电压L2", default="230", type="text", group="step4_recover")
    _put(by, "textEdit_S4_AC_VOLT_3", label="交流电压L3", default="230", type="text", group="step4_recover")
    _put(by, "textEdit_S4_TIME", label="数据采集", default="3", type="text", group="step4_recover")
    _put(
        by,
        "comboBox_S4_TIME",
        label="数据采集单位",
        default="分钟",
        type="select",
        group="step4_recover",
        options=["分钟", "秒", "毫秒"],
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
    for gid, title in (
        ("step3_protect", "③ 过压保护"),
        ("step4_recover", "④ 保护后恢复"),
        ("step5_off", "⑤ 关机设置"),
    ):
        for g in data.get("groups") or []:
            if g.get("id") == gid:
                g["title"] = title
    return _finish(data, by)


def main() -> None:
    for tt, sw in (
        ("guopinjiangzai", "iot_guopinjiangzai_schema_data.json"),
        ("qianpinshengzai", "iot_qianpinshengzai_schema_data.json"),
    ):
        iot = IOT / f"{tt}_fields.json"
        data = patch_freq_ladder(_load(iot))
        _save(iot, data)
        swp = SW / sw
        if swp.is_file():
            _save(swp, patch_freq_ladder(_load(swp)))
        print("patched", tt)

    iot = IOT / "voltprotect10min_fields.json"
    data = patch_voltprotect(_load(iot))
    _save(iot, data)
    swp = SW / "iot_voltprotect10min_schema_data.json"
    if swp.is_file():
        _save(swp, patch_voltprotect(_load(swp)))
    print("patched voltprotect10min fields=", len(data["fields"]))


if __name__ == "__main__":
    main()
