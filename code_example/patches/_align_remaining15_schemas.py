# -*- coding: utf-8 -*-
"""批量对齐剩余 Web 接入：序16/28–30 + 序17–27 功率族。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, List, Optional, Tuple

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
    # 保持原 schema 字段顺序，新增字段追加；并强制 AC 电压在频率前
    orig_names = [f["name"] for f in data.get("fields") or []]
    out_names = []
    seen = set()
    for name in orig_names:
        if name in by and name not in seen:
            out_names.append(name)
            seen.add(name)
    for name in by:
        if name not in seen:
            out_names.append(name)
            seen.add(name)

    ac_order = [
        "checkBox_S1",
        "comboBox_S1_AC",
        "comboBox_S1_AC_2",
        "textEdit_S1_AC_VOLT",
        "textEdit_S1_AC_VOLT_2",
        "textEdit_S1_AC_VOLT_3",
        "textEdit_S1_AC_FR",
    ]
    present = [n for n in ac_order if n in by]
    if present:
        # 抽出这些名字，按 ac_order 插回首次出现位置
        first = min(out_names.index(n) for n in present if n in out_names)
        out_names = [n for n in out_names if n not in present]
        for i, n in enumerate(present):
            out_names.insert(first + i, n)

    data["fields"] = [by[n] for n in out_names if n in by]
    return data


def _common_ac_dc(by: dict, *, dc_group: str = "step1_dc", time_group: str = "step1_ac") -> None:
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
    # 顺序：电压 → 频率（与桌面启机一致）
    _put(by, "textEdit_S1_AC_VOLT", label="交流电压1", default="230", type="text", group="step1_ac")
    _put(by, "textEdit_S1_AC_VOLT_2", label="交流电压2", default="230", type="text", group="step1_ac")
    _put(by, "textEdit_S1_AC_VOLT_3", label="交流电压3", default="230", type="text", group="step1_ac")
    _put(by, "textEdit_S1_AC_FR", label="交流频率", default="50", type="text", group="step1_ac")
    _put(by, "textEdit_S1_ACWaitTIME", label="等待时间", default="3", type="text", group=time_group)
    _put(
        by,
        "comboBox_S1_ACWaitTIME",
        label="等待时间单位",
        default="秒",
        type="select",
        group=time_group,
        options=["秒", "分钟", "毫秒"],
    )
    _put(by, "textEdit_S1_TIME", label="启机时间", default="1", type="text", group=time_group)
    _put(
        by,
        "comboBox_S1_TIME",
        label="启机时间单位",
        default="分钟",
        type="select",
        group=time_group,
        options=["分钟", "秒", "毫秒"],
    )
    for i in range(1, 5):
        _put(
            by,
            f"checkBox_S1_DC{i}",
            label=f"直流电源{i}",
            default=(i == 1),
            type="checkbox",
            group=dc_group,
        )
        _put(
            by,
            f"comboBox_S1_DC{i}",
            label="开关",
            default="开启",
            type="select",
            group=dc_group,
            options=["开启", "关闭"],
        )
        for key, lab in (
            ("VOLT", "Vmp"),
            ("CURR", "Imp"),
            ("Voc", "Voc"),
            ("Isc", "Isc"),
            ("PF", "功率%"),
        ):
            _put(by, f"textEdit_S1_DC{i}_{key}", label=lab, type="text", group=dc_group)


def _common_shutdown(by: dict, off_gid: str) -> None:
    # 兼容 S_End / S_END
    for end in ("S_End", "S_END"):
        if f"checkBox_{end}" in by or end == "S_End":
            _put(by, f"checkBox_{end}", label="启用关机", default=True, type="checkbox", group=off_gid)
            _put(
                by,
                f"comboBox_{end}_AC",
                label="交流电源",
                default="关闭",
                type="select",
                group=off_gid,
                options=["关闭", "开启"],
            )
            for i in range(1, 5):
                _put(
                    by,
                    f"checkBox_{end}_DC{i}",
                    label=f"直流电源{i}",
                    default=True,
                    type="checkbox",
                    group=off_gid,
                )
                _put(
                    by,
                    f"comboBox_{end}_DC{i}",
                    label=f"直流电源{i}关机",
                    default="关闭",
                    type="select",
                    group=off_gid,
                    options=["关闭", "开启"],
                )


def patch_rapidvolt(data: dict) -> dict:
    by = _by(data)
    _common_ac_dc(by)
    _put(by, "checkBox_S2", label="启用功率分析仪", default=True, type="checkbox", group="step2_wt")
    _put(
        by,
        "checkBox_rapidvolt_page",
        label="启用快速电压变化",
        default=True,
        type="checkbox",
        group="step3_rvc",
    )
    defaults = {3: ("230", "207"), 4: ("230", "253"), 5: ("230", "184"), 6: ("230", "276")}
    for i in range(6):
        step = 3 + i
        n = i + 1
        enabled = step in defaults
        start, end = defaults.get(step, (None, None))
        _put(
            by,
            f"checkBox_S{step}",
            label=f"启用阶跃{n}",
            default=enabled,
            type="checkbox",
            group="step3_rvc",
        )
        _put(
            by,
            f"checkBox_S{step}_return_rvc",
            label=f"阶跃{n} 回起点",
            default=True,
            type="checkbox",
            group="step3_rvc",
        )
        _put(
            by,
            f"textEdit_S{step}_volt_start_rvc",
            label=f"阶跃{n} 起点(V)",
            default=start,
            type="text",
            group="step3_rvc",
        )
        _put(
            by,
            f"textEdit_S{step}_volt_end_rvc",
            label=f"阶跃{n} 终点(V)",
            default=end,
            type="text",
            group="step3_rvc",
        )
        _put(
            by,
            f"textEdit_S{step}_pre_hold_rvc",
            label=f"阶跃{n} 起点保持",
            default="1",
            type="text",
            group="step3_rvc",
        )
        _put(
            by,
            f"textEdit_S{step}_post_hold_rvc",
            label=f"阶跃{n} 终点保持",
            default="3",
            type="text",
            group="step3_rvc",
        )
        for unit_name, lab in (
            (f"comboBox_S{step}_pre_hold_unit_rvc", f"阶跃{n} 起点单位"),
            (f"comboBox_S{step}_post_hold_unit_rvc", f"阶跃{n} 终点单位"),
        ):
            _put(
                by,
                unit_name,
                label=lab,
                default="秒",
                type="select",
                group="step3_rvc",
                options=["秒", "分钟", "小时"],
            )
    _common_shutdown(by, "step4_off")
    _title(data, "step3_rvc", "③ 快速电压变化")
    _title(data, "step4_off", "④ 关机设置")
    data["title"] = "快速电压变化"
    data["testType"] = "rapidvolt"
    return _finish(data, by)


def patch_timing_profile(data: dict, *, test_type: str, title: str, profile_title: str) -> dict:
    by = _by(data)
    _common_ac_dc(by)
    _put(by, "checkBox_S2", label="启用功率分析仪", default=True, type="checkbox", group="step2_wt")
    _put(by, "checkBox_S3", label="启用时序工况", default=True, type="checkbox", group="step3_profile")
    for i in range(1, 5):
        _put(
            by,
            f"checkBox_S3_DC{i}",
            label=f"工况 DC{i}",
            default=True,
            type="checkbox",
            group="step3_profile",
        )
    if "TIMING_PROFILE_JSON" in by:
        _put(by, "TIMING_PROFILE_JSON", label="时序工况 JSON", type="text", group="step3_profile")
    _common_shutdown(by, "step4_off")
    _title(data, "step3_profile", profile_title)
    _title(data, "step4_off", "④ 关机设置")
    data["title"] = title
    data["testType"] = test_type
    return _finish(data, by)


def patch_dynamicmppt(data: dict) -> dict:
    by = _by(data)
    _common_ac_dc(by)
    _put(by, "checkBox_S2", label="启用功率分析仪", default=True, type="checkbox", group="step2_wt")
    _put(by, "checkBox_S3", label="启用动态MPPT", default=True, type="checkbox", group="step3_profile")
    for i in range(1, 5):
        _put(
            by,
            f"checkBox_S3_DC{i}",
            label=f"工况 DC{i}",
            default=(i == 1),
            type="checkbox",
            group="step3_profile",
        )
    _put(by, "comboBox_S3_ff", label="填充因子", default="c-Si", type="select", group="step3_profile")
    _put(by, "textEdit_S3_pmpp", label="STC Pmpp", default="600", type="text", group="step3_profile")
    _put(by, "textEdit_S3_vmp", label="STC Vmp", default="100", type="text", group="step3_profile")
    _put(
        by,
        "textEdit_S3_initial_setup_s",
        label="初始稳定(s)",
        default="300",
        type="text",
        group="step3_profile",
    )
    _put(
        by,
        "textEdit_S3_wt_filename",
        label="录波文件名",
        default="DynamicMPPT_BR",
        type="text",
        group="step3_profile",
    )
    _put(by, "EN50530_BUNDLE_JSON", label="EN50530 工况包 JSON", type="text", group="step3_profile")
    _common_shutdown(by, "step4_off")
    _title(data, "step3_profile", "③ EN50530 动态MPPT")
    _title(data, "step4_off", "④ 关机设置")
    data["title"] = "动态MPPT"
    data["testType"] = "dynamicmppt"
    return _finish(data, by)


def patch_power_family(
    data: dict,
    *,
    test_type: str,
    title: str,
    step3_title: str,
    ladder_name: Optional[str],
    ladder_label: str,
    ladder_default: Optional[str],
    hold_default: str,
    hold_unit: str = "秒",
    off_gid: str = "step4_off",
    step3_gid: str = "step3_test",
    enable_s3: bool = True,
    use_voltage_ladder_hold: bool = False,
) -> dict:
    by = _by(data)
    group_ids = {g.get("id") for g in data.get("groups") or []}
    if "step1_time" not in group_ids:
        # 插到 step1_dc 后
        groups = list(data.get("groups") or [])
        insert_at = next((i + 1 for i, g in enumerate(groups) if g.get("id") == "step1_dc"), len(groups))
        groups.insert(insert_at, {"id": "step1_time", "title": "① 时序"})
        data["groups"] = groups
    _common_ac_dc(by, time_group="step1_time")
    _put(by, "checkBox_S2", label="启用功率分析仪", default=True, type="checkbox", group="step2_wt")
    if enable_s3:
        _put(by, "checkBox_S3", label="启用实验步骤", default=True, type="checkbox", group=step3_gid)
    if ladder_name:
        _put(
            by,
            ladder_name,
            label=ladder_label,
            default=ladder_default,
            type="text",
            group=step3_gid,
        )
    if use_voltage_ladder_hold:
        _put(by, "textEdit_VoltageLadder_Un", label="Un基准(V)", default="230", type="text", group=step3_gid)
        _put(by, "textEdit_VoltageLadder_FR", label="频率(Hz)", default="50", type="text", group=step3_gid)
        _put(
            by,
            "textEdit_VoltageLadder_TIME",
            label="每点驻留",
            default=hold_default,
            type="text",
            group=step3_gid,
        )
        _put(
            by,
            "comboBox_VoltageLadder_TIME",
            label="驻留单位",
            default=hold_unit,
            type="select",
            group=step3_gid,
            options=["分钟", "秒", "毫秒"],
        )
        if test_type == "testpu":
            _put(by, "checkBox_S_PU", label="PU 测试", default=True, type="checkbox", group=step3_gid)
    else:
        _put(
            by,
            "textEdit_S3_TIME_2",
            label="保持时间",
            default=hold_default,
            type="text",
            group=step3_gid,
        )
        _put(
            by,
            "comboBox_S3_TIME_2",
            label="保持时间单位",
            default=hold_unit,
            type="select",
            group=step3_gid,
            options=["秒", "分钟", "毫秒", "小时"],
        )
    for i in range(1, 5):
        if f"checkBox_S3_DC{i}" in by or enable_s3:
            _put(
                by,
                f"checkBox_S3_DC{i}",
                label=f"工况 DC{i}",
                default=(i == 1),
                type="checkbox",
                group=step3_gid,
            )
    _common_shutdown(by, off_gid)
    _title(data, step3_gid, step3_title)
    _title(data, off_gid, "④ 关机设置")
    data["title"] = title
    data["testType"] = test_type
    return _finish(data, by)


_U_LADDER = (
    "100,103,105,106,107,108,110,112,115,"
    "112,110,108,107,106,105,103,100,"
    "97,94,93,90,87,85"
)

POWER_SPECS: List[Tuple[str, str, dict]] = [
    (
        "cosphibrazil",
        "iot_cosphibrazil_schema_data.json",
        dict(
            test_type="cosphibrazil",
            title="Cos(φ)_Brazil",
            step3_title="③ cosPhi 设置",
            ladder_name=None,
            ladder_label="",
            ladder_default=None,
            hold_default="2",
            hold_unit="分钟",
        ),
    ),
    (
        "staticcosphi",
        "iot_staticcosphi_schema_data.json",
        dict(
            test_type="staticcosphi",
            title="静态Cos(φ)",
            step3_title="③ cosPhi 设置",
            ladder_name="textEdit_PowerLadder",
            ladder_label="稳态功率档(%)",
            ladder_default="100,90,80,70",
            hold_default="30",
            hold_unit="秒",
        ),
    ),
    (
        "staticqu",
        "iot_staticqu_schema_data.json",
        dict(
            test_type="staticqu",
            title="静态QU",
            step3_title="③ 电压阶梯",
            ladder_name="textEdit_VoltageLadder",
            ladder_label="电压阶梯 Un%",
            ladder_default=_U_LADDER,
            hold_default="1",
            hold_unit="分钟",
            use_voltage_ladder_hold=True,
        ),
    ),
    (
        "testpu",
        "iot_testpu_schema_data.json",
        dict(
            test_type="testpu",
            title="Test_PU",
            step3_title="③ PU 测试",
            ladder_name="textEdit_VoltageLadder",
            ladder_label="电压Un%",
            ladder_default=_U_LADDER,
            hold_default="1",
            hold_unit="分钟",
            use_voltage_ladder_hold=True,
        ),
    ),
    (
        "dynamiccosphi",
        "iot_dynamiccosphi_schema_data.json",
        dict(
            test_type="dynamiccosphi",
            title="动态Cos(φ)",
            step3_title="③ 功率阶梯",
            ladder_name="textEdit_PowerLadder",
            ladder_label="功率阶梯(%)",
            ladder_default="20,40,60,80,100,80,60,40,20",
            hold_default="5",
            hold_unit="秒",
        ),
    ),
    (
        "dynamicqu",
        "iot_dynamicqu_schema_data.json",
        dict(
            test_type="dynamicqu",
            title="动态QU",
            step3_title="③ 电压阶梯",
            ladder_name="textEdit_VoltageLadder",
            ladder_label="电压Un%",
            ladder_default=_U_LADDER,
            hold_default="1",
            hold_unit="分钟",
            use_voltage_ladder_hold=True,
        ),
    ),
    (
        "reactiveqcap",
        "iot_reactiveqcap_schema_data.json",
        dict(
            test_type="reactiveqcap",
            title="无功能力范围",
            step3_title="③ 能力工况",
            ladder_name="textEdit_PowerLadder",
            ladder_label="功率阶梯(%)",
            ladder_default="10,20,30,40,50,60,70,80,90,100",
            hold_default="1",
            hold_unit="分钟",
        ),
    ),
    (
        "fixedq",
        "iot_fixedq_schema_data.json",
        dict(
            test_type="fixedq",
            title="定无功",
            step3_title="③ Q 设定",
            ladder_name="textEdit_PowerLadder",
            ladder_label="功率阶梯(%)",
            ladder_default="50,100",
            hold_default="1",
            hold_unit="分钟",
        ),
    ),
    (
        "reactiveqin",
        "iot_reactiveqin_schema_data.json",
        dict(
            test_type="reactiveqin",
            title="无功注入",
            step3_title="③ Q 设定",
            ladder_name="textEdit_PowerLadder",
            ladder_label="功率阶梯(%)",
            ladder_default="20,50,100",
            hold_default="1",
            hold_unit="分钟",
        ),
    ),
    (
        "reactiveqacc",
        "iot_reactiveqacc_schema_data.json",
        dict(
            test_type="reactiveqacc",
            title="无功精度",
            step3_title="③ Q 设定",
            ladder_name="textEdit_PowerLadder",
            ladder_label="功率阶梯(%)",
            ladder_default="100",
            hold_default="1",
            hold_unit="分钟",
        ),
    ),
    (
        "activep",
        "iot_activep_schema_data.json",
        dict(
            test_type="activep",
            title="有功调度",
            step3_title="③ P 调度",
            ladder_name="textEdit_PowerLadder",
            ladder_label="功率阶梯(%)",
            ladder_default="100,80,60,40,20,0",
            hold_default="1",
            hold_unit="分钟",
        ),
    ),
]


SPECS: List[Tuple[str, str, Callable[[dict], dict]]] = [
    ("rapidvolt", "iot_rapidvolt_schema_data.json", patch_rapidvolt),
    (
        "lvrt",
        "iot_lvrt_schema_data.json",
        lambda d: patch_timing_profile(
            d, test_type="lvrt", title="低电压穿越", profile_title="③ LVRT 电压阶跃时序"
        ),
    ),
    (
        "phasejump",
        "iot_phasejump_schema_data.json",
        lambda d: patch_timing_profile(
            d, test_type="phasejump", title="相角突变", profile_title="③ 相角突变时序"
        ),
    ),
    ("dynamicmppt", "iot_dynamicmppt_schema_data.json", patch_dynamicmppt),
]


def _apply(tt: str, sw_name: str, fn: Callable[[dict], dict]) -> int:
    iot = IOT / f"{tt}_fields.json"
    data = fn(_load(iot))
    _save(iot, data)
    sw = SW / sw_name
    if sw.is_file():
        _save(sw, fn(_load(sw)))
    return len(data["fields"])


def main() -> None:
    for tt, sw_name, fn in SPECS:
        n = _apply(tt, sw_name, fn)
        print(f"ok {tt} fields={n}")
    for tt, sw_name, kw in POWER_SPECS:
        n = _apply(tt, sw_name, lambda d, k=kw: patch_power_family(d, **k))
        print(f"ok {tt} fields={n}")


if __name__ == "__main__":
    main()
