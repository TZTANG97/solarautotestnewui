# -*- coding: utf-8 -*-
"""批量细核对齐：重连 / 静态MPPT / 过欠压_过欠频 / 巴西过欠频稳定性。"""
from __future__ import annotations

import json
from pathlib import Path

IOT = Path(r"E:/IOT/iot/app/services/solar_test_schemas")
SW = Path(r"E:/solarautotestnewui/utils")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def _title(data: dict, gid: str, title: str):
    for g in data.get("groups") or []:
        if g.get("id") == gid:
            g["title"] = title


def patch_reconnect(data: dict) -> dict:
    by = _by(data)
    # 桌面步骤条用「重联」，对话框标题用「重连」——Web 标签与步骤条一致
    gid_map = {3: "step3_r1", 4: "step4_r2", 5: "step5_r3", 6: "step6_r4", 7: "step7_r5"}
    for n in (3, 4, 5, 6, 7):
        idx = n - 2
        gid = gid_map[n]
        _put(by, f"checkBox_S{n}", group=gid, label=f"启用重联测试{idx}", default=True, type="checkbox")
        _put(
            by,
            f"textEdit_S{n}_AC_VOLT",
            label=f"重联{idx} 电压(V)",
            default="230",
            type="text",
            group=gid,
        )
        _put(
            by,
            f"textEdit_S{n}_AC_FR",
            label=f"重联{idx} 频率(Hz)",
            default="50",
            type="text",
            group=gid,
        )
        _put(
            by,
            f"textEdit_S{n}_TIME",
            label=f"重联{idx} 采集时长",
            default="2.5",
            type="text",
            group=gid,
        )
        _put(
            by,
            f"comboBox_S{n}_TIME",
            label=f"重联{idx} 时长单位",
            default="秒",
            type="select",
            group=gid,
            options=["秒", "毫秒", "分钟"],
        )
    _put(by, "checkBox_S_End", label="启用关机", default=True, type="checkbox", group="step8_off")
    _put(
        by,
        "comboBox_S_End_AC",
        label="交流电源",
        default="关闭",
        type="select",
        group="step8_off",
        options=["关闭", "开启"],
    )
    for i in range(1, 5):
        _put(
            by,
            f"checkBox_S_End_DC{i}",
            label=f"直流电源{i}",
            default=True,
            type="checkbox",
            group="step8_off",
        )
        _put(
            by,
            f"comboBox_S_End_DC{i}",
            label=f"直流电源{i}关机",
            default="关闭",
            type="select",
            group="step8_off",
            options=["关闭", "开启"],
        )
    for gid, title in (
        ("step3_r1", "③ 重联测试1"),
        ("step4_r2", "④ 重联测试2"),
        ("step5_r3", "⑤ 重联测试3"),
        ("step6_r4", "⑥ 重联测试4"),
        ("step7_r5", "⑦ 重联测试5"),
        ("step8_off", "⑧ 关机设置"),
    ):
        _title(data, gid, title)
    return _finish(data, by)


def patch_staticmppt(data: dict) -> dict:
    by = _by(data)
    # 去掉代码模板字面量垃圾字段
    for name in list(by):
        if "{dcPrefix}" in name or "{dc" in name:
            by[name]["hidden"] = True
            by[name]["uiHint"] = "legacy_hidden"
            by[name]["group"] = "other"

    _put(by, "checkBox_S1", label="启用步骤1 AC/DC", default=True, type="checkbox", group="step1_ac")
    _put(by, "radio_Mode_Bluesight", label="蓝电 IP（国产）", default=True, type="radio", group="step1_ac")
    _put(by, "radio_Mode_SoftPanel", label="Soft Panel 曲线", default=False, type="radio", group="step1_ac")
    _put(by, "comboBox_S1_AC", label="交流电源", default="开启", type="select", group="step1_ac", options=["开启", "关闭"])
    _put(by, "comboBox_S1_AC_2", label="相数", default="单相", type="select", group="step1_ac", options=["单相", "三相"])
    _put(by, "textEdit_S1_AC_VOLT", label="电压 L1(V)", default="230", type="text", group="step1_ac")
    _put(by, "textEdit_S1_AC_VOLT_2", label="电压 L2(V)", default="230", type="text", group="step1_ac")
    _put(by, "textEdit_S1_AC_VOLT_3", label="电压 L3(V)", default="230", type="text", group="step1_ac")
    _put(by, "textEdit_S1_AC_FR", label="频率(Hz)", default="50", type="text", group="step1_ac")
    _put(by, "textEdit_S1_ACWaitTIME", label="AC 等待时长", default="3", type="text", group="step1_ac")
    _put(
        by,
        "comboBox_S1_ACWaitTIME",
        label="AC 等待单位",
        default="秒",
        type="select",
        group="step1_ac",
        options=["秒", "毫秒", "分钟"],
    )
    _put(by, "textEdit_S1_TIME", label="启机等待", default="5", type="text", group="step1_ac")
    _put(
        by,
        "comboBox_S1_TIME",
        label="启机等待单位",
        default="分钟",
        type="select",
        group="step1_ac",
        options=["分钟", "秒", "毫秒"],
    )
    _put(
        by,
        "comboBox_S1_Vdc_Count",
        label="Vdc 点数",
        default="3",
        type="select",
        group="step1_dc",
        options=["1", "2", "3"],
    )
    _put(
        by,
        "comboBox_S1_DC_START",
        label="直流启机",
        default="开启",
        type="select",
        group="step1_dc",
        options=["开启", "关闭"],
    )

    # 真实 DC 通道（桌面动态生成 DC1~4）
    for i, dc in enumerate(("DC1", "DC2", "DC3", "DC4"), start=1):
        _put(
            by,
            f"checkBox_S1_{dc}",
            label=f"直流电源{i}",
            default=(dc == "DC1"),
            type="checkbox",
            group="step1_dc",
        )
        _put(
            by,
            f"comboBox_S1_{dc}_PORT",
            label=f"{dc} 接口",
            type="select",
            group="step1_dc",
            options=[],
        )
        for band in ("Vmin", "Vnom", "Vmax", "Vdc1", "Vdc2", "Vdc3"):
            # 冒烟默认只勾各通道 Vnom
            _put(
                by,
                f"checkBox_S1_{dc}_{band}",
                label=f"{dc}·{band}",
                default=(band == "Vnom"),
                type="checkbox",
                group="step1_dc",
            )
            _put(
                by,
                f"textEdit_S1_{dc}_{band}",
                label=f"{dc}·{band}文件/值",
                type="text",
                group="step1_dc",
            )

    # 蓝电 IV 默认值与 Dialog 一致
    bs_defaults = {
        ("Vnom", "Vmp"): "650",
        ("Vnom", "Imp"): "12.3",
        ("Vnom", "Voc"): "800",
        ("Vnom", "Isc"): "13.5",
        ("Vmin", "Vmp"): "500",
        ("Vmin", "Imp"): "12.3",
        ("Vmin", "Voc"): "650",
        ("Vmin", "Isc"): "13.5",
        ("Vmax", "Vmp"): "750",
        ("Vmax", "Imp"): "12.3",
        ("Vmax", "Voc"): "900",
        ("Vmax", "Isc"): "13.5",
    }
    for band in ("Vnom", "Vmin", "Vmax"):
        for suffix in ("Vmp", "Imp", "Voc", "Isc"):
            _put(
                by,
                f"textEdit_BS_{band}_{suffix}",
                label=f"蓝电 {band}·{suffix}",
                default=bs_defaults[(band, suffix)],
                type="text",
                group="step1_dc",
            )

    _put(by, "checkBox_S2", label="启用测试功率段", default=True, type="checkbox", group="step3_power")
    for pct, default in (
        ("100", True),
        ("75", False),
        ("50", False),
        ("30", False),
        ("25", False),
        ("20", False),
        ("10", False),
        ("5", False),
    ):
        _put(
            by,
            f"checkBox_S2_Pn_{pct}",
            label=f"{pct}%",
            default=default,
            type="checkbox",
            group="step3_power",
        )
    for key, label in (
        ("Vmin", "Vmin 路径"),
        ("Vnom", "Vnom 路径"),
        ("Vmax", "Vmax 路径"),
        ("Vdc1", "Vdc1 路径"),
        ("Vdc2", "Vdc2 路径"),
        ("Vdc3", "Vdc3 路径"),
    ):
        _put(by, f"textEdit_S2_{key}_PATH", label=label, type="text", group="step3_power")

    _put(by, "checkBox_S3", label="启用MPPT时长", default=True, type="checkbox", group="step4_mppt")
    _put(by, "textEdit_S3_TOTAL_H", label="MPPT总时长(时)", default="0", type="text", group="step4_mppt")
    _put(by, "textEdit_S3_TOTAL_M", label="MPPT总时长(分)", default="30", type="text", group="step4_mppt")
    _put(by, "textEdit_S3_PER_H", label="单次时长(时)", default="0", type="text", group="step4_mppt")
    _put(by, "textEdit_S3_PER_M", label="单次时长(分)", default="5", type="text", group="step4_mppt")

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
    _put(by, "checkBox_S_End_DC", label="直流电源", default=True, type="checkbox", group="step5_off")
    _put(
        by,
        "comboBox_S_End_DC",
        label="直流关机",
        default="关闭",
        type="select",
        group="step5_off",
        options=["关闭", "开启"],
    )
    for gid, title in (
        ("step1_ac", "① AC 电源"),
        ("step1_dc", "① DC 电源"),
        ("step3_power", "③ 测试功率段"),
        ("step4_mppt", "④ MPPT时长"),
        ("step5_off", "⑤ 关机设置"),
    ):
        _title(data, gid, title)
    return _finish(data, by)


def patch_ovuf(data: dict) -> dict:
    by = _by(data)
    scans = [
        ("S3", "step3_ov", "过压"),
        ("S4", "step4_uv", "欠压"),
        ("S5", "step5_of", "过频"),
        ("S6", "step6_uf", "欠频"),
    ]
    for suffix, gid, zh in scans:
        _put(by, f"checkBox_{suffix}", label=f"启用{zh}扫描", default=True, type="checkbox", group=gid)
        _put(
            by,
            f"textEdit_{suffix}_AC_VOLT_Start",
            label=f"{zh} 电压起点(V)",
            default="230",
            type="text",
            group=gid,
        )
        _put(
            by,
            f"textEdit_{suffix}_AC_VOLT_End",
            label=f"{zh} 电压终点(V)",
            default="230",
            type="text",
            group=gid,
        )
        _put(
            by,
            f"textEdit_{suffix}_AC_FR_Start",
            label=f"{zh} 频率起点(Hz)",
            default="50",
            type="text",
            group=gid,
        )
        _put(
            by,
            f"textEdit_{suffix}_AC_FR_End",
            label=f"{zh} 频率终点(Hz)",
            default="50",
            type="text",
            group=gid,
        )
        _put(by, f"textEdit_{suffix}_Step_Size", label=f"{zh} 步长", default="5", type="text", group=gid)
        _put(by, f"textEdit_{suffix}_TIME", label=f"{zh} 采集时长", default="3", type="text", group=gid)
        _put(
            by,
            f"comboBox_{suffix}_TIME",
            label=f"{zh} 时长单位",
            default="秒",
            type="select",
            group=gid,
            options=["秒", "毫秒", "分钟"],
        )

    _put(by, "comboBox_Test_Project", label="测试项目", default="过欠压", type="select", group="step7_phase", options=["过欠压", "过欠频"])
    for ph in ("L1", "L2", "L3"):
        _put(by, f"checkBox_AC_Test_{ph}", label=f"测试相 {ph}", default=True, type="checkbox", group="step7_phase")
    _put(by, "checkBox_S7", label="启用过频扫描(相位页)", default=True, type="checkbox", group="step7_phase")
    _put(by, "checkBox_S8", label="启用欠频扫描(相位页)", default=True, type="checkbox", group="step7_phase")
    for suffix, zh in (("S7", "过频相位"), ("S8", "欠频相位")):
        for name, label, default in (
            (f"textEdit_{suffix}_AC_VOLT_Start", f"{zh} 电压起点(V)", "230"),
            (f"textEdit_{suffix}_AC_VOLT_End", f"{zh} 电压终点(V)", "230"),
            (f"textEdit_{suffix}_AC_FR_Start", f"{zh} 频率起点(Hz)", "50"),
            (f"textEdit_{suffix}_AC_FR_End", f"{zh} 频率终点(Hz)", "50"),
            (f"textEdit_{suffix}_Step_Size", f"{zh} 步长", "5"),
            (f"textEdit_{suffix}_TIME", f"{zh} 采集时长", "3"),
        ):
            _put(by, name, label=label, default=default, type="text", group="step7_phase")
        _put(
            by,
            f"comboBox_{suffix}_TIME",
            label=f"{zh} 时长单位",
            default="秒",
            type="select",
            group="step7_phase",
            options=["秒", "毫秒", "分钟"],
        )

    _put(by, "checkBox_S_End", label="启用关机", default=True, type="checkbox", group="step8_off")
    _put(
        by,
        "comboBox_S_End_AC",
        label="交流电源",
        default="关闭",
        type="select",
        group="step8_off",
        options=["关闭", "开启"],
    )
    for i in range(1, 5):
        _put(by, f"checkBox_S_End_DC{i}", label=f"直流电源{i}", default=True, type="checkbox", group="step8_off")
        _put(
            by,
            f"comboBox_S_End_DC{i}",
            label=f"直流{i}关机",
            default="关闭",
            type="select",
            group="step8_off",
            options=["关闭", "开启"],
        )
    for gid, title in (
        ("step3_ov", "③ 过压扫描"),
        ("step4_uv", "④ 欠压扫描"),
        ("step5_of", "⑤ 过频扫描"),
        ("step6_uf", "⑥ 欠频扫描"),
        ("step7_phase", "⑦ 测试相位"),
        ("step8_off", "⑧ 关机设置"),
    ):
        _title(data, gid, title)
    return _finish(data, by)


def patch_immun(data: dict) -> dict:
    by = _by(data)
    _put(by, "checkBox_S3", label="启用频率扫描", default=True, type="checkbox", group="step3_sweep")
    _put(by, "checkBox_RATE", label="更新率(分析仪)", default=True, type="checkbox", group="step2_wt")
    for i, suffix in enumerate(["S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11"], start=1):
        _put(
            by,
            f"checkBox_{suffix}",
            label=f"启用频率扫描{i}",
            default=True,
            type="checkbox",
            group="step3_sweep",
        )
        _put(
            by,
            f"checkBox_{suffix}_RATE",
            label=f"扫描{i} 更新率",
            default=True,
            type="checkbox",
            group="step3_sweep",
        )
        _put(
            by,
            f"textEdit_{suffix}_AC_FR_Start",
            label=f"扫描{i} 频率起点(Hz)",
            type="text",
            group="step3_sweep",
        )
        _put(
            by,
            f"textEdit_{suffix}_AC_FR_End",
            label=f"扫描{i} 频率终点(Hz)",
            type="text",
            group="step3_sweep",
        )
        _put(by, f"textEdit_{suffix}_TIME", label=f"扫描{i} 采集时长", type="text", group="step3_sweep")
        _put(
            by,
            f"comboBox_{suffix}_TIME",
            label=f"扫描{i} 时长单位",
            default="秒",
            type="select",
            group="step3_sweep",
            options=["秒", "毫秒", "分钟"],
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
        _put(by, f"checkBox_S_End_DC{i}", label=f"直流电源{i}", default=True, type="checkbox", group="step4_off")
        _put(
            by,
            f"comboBox_S_End_DC{i}",
            label=f"直流{i}关机",
            default="关闭",
            type="select",
            group="step4_off",
            options=["关闭", "开启"],
        )
    _title(data, "step3_sweep", "③ 频率扫描")
    _title(data, "step4_off", "④ 关机设置")
    return _finish(data, by)


SPECS = [
    ("reconnect", "iot_reconnect_schema_data.json", patch_reconnect),
    ("staticmppt", "iot_staticmppt_schema_data.json", patch_staticmppt),
    ("ovuf", "iot_ovuf_schema_data.json", patch_ovuf),
    ("guoqianpin_immun", "iot_guoqianpin_immun_schema_data.json", patch_immun),
]


def main() -> None:
    for tt, sw_name, fn in SPECS:
        iot = IOT / f"{tt}_fields.json"
        data = fn(_load(iot))
        _save(iot, data)
        sw = SW / sw_name
        if sw.is_file():
            _save(sw, fn(_load(sw)))
        print(f"ok {tt} fields={len(data['fields'])}")


if __name__ == "__main__":
    main()
