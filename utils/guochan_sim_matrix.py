# -*- coding: utf-8 -*-
"""国产 AC/DC 软件映射模拟：按品牌分场景的典型 SCPI 序列。

不连真机。供 pytest 矩阵与后续真机联调对照。
AC：Chroma=原生 SCPI；爱科=经 ItechTranslator 映射。
DC：Chroma/Itech=模式前缀命令；蓝点=BluesightTranslator。
"""

from __future__ import annotations

# 与 SCPITestWave 初始化 command_list_DC 保持一致
DC_MODE_PREAMBLE = {
    "Chroma": ["OUTP:MODE TABLE", "IVCurve:SELect 1"],
    "Itech": ["SOL 0", "SOL 1"],
    "Bluesight": [],  # 蓝点恒压/SAS 不走 IVCurve 前缀
    "Keysight": [],
}

# P0 冒烟菜单：典型 AC 启停序列（菜单生成命令的公共子集）
P0_MENUS = (
    "重连",
    "电压闪变",
    "固定PF=1",
    "直流分量",
    "过载能力测试",
    "静态MPPT测试",
)

# P2：新菜单（含快速电压变化阶跃）
P2_MENUS = (
    "快速电压变化",
)

# P3：扩展菜单（真机前软件映射必过）
P3_MENUS = (
    "频率适应性",
    "电压适应性",
    "Test_PU",
    "ROCOF保护",
    "静态QU",
    "10min过压保护",
)

AC_BRANDS = ("Chroma", "Itech")
DC_BRANDS = ("Chroma", "Bluesight", "Itech")

# 致茂 AC 扩展：爱科 Translator 必须拒绝（不可误写成设压/设频）
CHROMA_ONLY_AC_CMDS = (
    "VOLT:MODE LIST",
    "VOLT:OFFS 0",
    "LIST:VOLT 230,253",
    "TRIG:TRAN:SOUR BUS",
    "FUNC SIN",
    "FREQ:MODE LIST",
)

# 致茂 DC 曲线命令：蓝点 Translator 必须拒绝
CHROMA_ONLY_DC_CMDS = (
    "OUTP:MODE TABLE",
    "IVCurve:SELect 1",
    "IVC:IT 1,2,3",
    "IVC:VT 100,200,300",
)


def ac_startup_single_phase(volt: float = 230.0, freq: float = 50.0) -> list[str]:
    """爱科单相路径：勿含 INST:EDIT ALL（SINGLE 下由 Translator 忽略，但脚本侧宜省略）。"""
    return [
        "INST:PHASE SINGLE",
        f"VOLT {volt:g}",
        f"FREQ {freq:g}",
    ]


def ac_startup_three_phase(volt: float = 230.0, freq: float = 50.0) -> list[str]:
    return [
        "INST:PHASE THREE",
        "INST:EDIT ALL",
        f"VOLT {volt:g}",
        f"FREQ {freq:g}",
    ]


def ac_output_on_sequence() -> list[str]:
    """与 ac_controller.open_output 爱科路径一致：RUN → OUTP ON。"""
    return ["SYST:RUN", "OUTP ON"]


def ac_output_off_sequence() -> list[str]:
    return ["OUTP OFF", "SYST:STANDBY"]


def ac_smoke_sequence(*, single_phase: bool = True) -> list[str]:
    """单项目冒烟：启机参数 + 开输出 + 关输出。"""
    start = ac_startup_single_phase() if single_phase else ac_startup_three_phase()
    return start + ac_output_on_sequence() + ac_output_off_sequence()


def ac_rapid_volt_step_sequence(
    volt_start: float = 230.0,
    volt_end: float = 207.0,
    *,
    single_phase: bool = True,
) -> list[str]:
    """快速电压变化典型阶跃：启机 → 开出 → 起点 → 终点 → 回起点 → 关出。"""
    start = ac_startup_single_phase(volt_start) if single_phase else ac_startup_three_phase(volt_start)
    return (
        start
        + ac_output_on_sequence()
        + [
            f"VOLT {volt_start:g}",
            f"VOLT {volt_end:g}",
            f"VOLT {volt_start:g}",
        ]
        + ac_output_off_sequence()
    )


def ac_freq_ladder_sequence(
    freqs: tuple[float, ...] = (50.0, 50.2, 51.0, 49.0, 50.0),
    *,
    single_phase: bool = True,
) -> list[str]:
    """频率阶梯（频率适应性 / ROCOF 公共子集）。"""
    start = ac_startup_single_phase() if single_phase else ac_startup_three_phase()
    mid = [f"FREQ {f:g}" for f in freqs]
    return start + ac_output_on_sequence() + mid + ac_output_off_sequence()


def ac_volt_ladder_sequence(
    volts: tuple[float, ...] = (230.0, 253.0, 207.0, 230.0),
    *,
    single_phase: bool = True,
) -> list[str]:
    """电压阶梯（电压适应性 / 10min / 静态QU 公共子集）。"""
    start = (
        ac_startup_single_phase(volts[0]) if single_phase else ac_startup_three_phase(volts[0])
    )
    mid = [f"VOLT {v:g}" for v in volts]
    return start + ac_output_on_sequence() + mid + ac_output_off_sequence()


def ac_three_phase_nsel_sequence(
    volt: float = 230.0, freq: float = 50.0
) -> list[str]:
    """三相分相设压（与 ac_controller 爱科三相路径一致）。"""
    cmds = [
        "INST:PHASE THREE",
        "INST:EDIT EACH",
    ]
    for nsel in (1, 2, 3):
        cmds.extend([f"INST:NSEL {nsel}", f"VOLT {volt:g}", f"FREQ {freq:g}"])
    return cmds + ac_output_on_sequence() + ac_output_off_sequence()


def ac_sequence_for_menu(menu: str) -> list[str]:
    """按菜单取典型 AC 序列（软件映射用）。"""
    if menu == "快速电压变化":
        return ac_rapid_volt_step_sequence()
    if menu in ("频率适应性", "ROCOF保护"):
        return ac_freq_ladder_sequence()
    if menu == "Test_PU":
        return ac_volt_ladder_sequence(single_phase=False)
    if menu in ("电压适应性", "静态QU", "10min过压保护"):
        return ac_volt_ladder_sequence()
    return ac_smoke_sequence(single_phase=True)


def dc_bluesight_smoke_sequence() -> list[str]:
    """蓝点基础：原载/SAS 模式切换 + 输出开关（曲线块另测 write_curve_block）。"""
    return [
        "SYST:MODE 0",
        "OUTP ON",
        "OUTP OFF",
        "SYST:MODE SAS",
        "OUTP ON",
        "OUTP OFF",
    ]


def dc_iv_shape_for_brand(dc_brand: str) -> list[str]:
    """各品牌 IV/曲线下发的典型命令形态（对照 DCGetIVValueFunction）。"""
    if dc_brand == "Chroma":
        return ["OUTP:MODE TABLE", "IVC:IT 10,12", "IVC:VT 400,450", "IVCurve:SELect 1"]
    if dc_brand == "Itech":
        return [
            "SOL 0",
            "SOL:USER:VOC 450",
            "SOL:USER:IMP 10",
            "SOL:USER:VMP 400",
            "SOL:USER:ISC 12",
            "SOL 1",
        ]
    if dc_brand == "Bluesight":
        return ["SYST:MODE SAS", "BLUESIGHT:STC 8.0 650 0.8", "OUTP ON"]
    if dc_brand == "Keysight":
        return ["SAS:MODE TABL", "SAS:TABL1:VOLT 400", "SAS:TABL1:CURR 10", "SAS:TABL:ACT 1"]
    raise KeyError(dc_brand)


def is_chroma_only_ac(cmd: str) -> bool:
    u = cmd.strip().upper()
    if u.startswith("VOLT:") or u.startswith("FREQ:"):
        return True
    if u.startswith("LIST:") or u.startswith("TRIG:"):
        return True
    if u.startswith("FUNC "):
        return True
    return u in {c.upper() for c in CHROMA_ONLY_AC_CMDS}


def is_chroma_only_dc(cmd: str) -> bool:
    u = cmd.strip().upper()
    if u.startswith("IVC:") or u.startswith("IVCURVE:"):
        return True
    if u.startswith("OUTP:MODE"):
        return True
    if u.startswith("SAS:TABL") or u.startswith("SAS:MODE"):
        return True
    return False


def _matrix_case(menu: str, ac: str, dc: str, ac_cmds: list[str]) -> dict:
    return {
        "menu": menu,
        "ac_brand": ac,
        "dc_brand": dc,
        "ac_cmds": ac_cmds,
        "dc_preamble": list(DC_MODE_PREAMBLE[dc]),
        "dc_bluesight_cmds": (
            dc_bluesight_smoke_sequence() if dc == "Bluesight" else []
        ),
        "dc_iv_shape": dc_iv_shape_for_brand(dc),
    }


def p0_matrix_cases() -> list[dict]:
    """返回可参数化用例：每个 P0 菜单 × AC 品牌 × DC 品牌。"""
    cases: list[dict] = []
    for menu in P0_MENUS:
        for ac in AC_BRANDS:
            for dc in DC_BRANDS:
                cases.append(_matrix_case(menu, ac, dc, ac_smoke_sequence(single_phase=True)))
    return cases


def p2_matrix_cases() -> list[dict]:
    """P2 菜单矩阵（快速电压变化用阶跃序列）。"""
    cases: list[dict] = []
    for menu in P2_MENUS:
        for ac in AC_BRANDS:
            for dc in DC_BRANDS:
                cases.append(_matrix_case(menu, ac, dc, ac_rapid_volt_step_sequence()))
    return cases


def p3_matrix_cases() -> list[dict]:
    """P3 扩展菜单 × AC×DC。"""
    cases: list[dict] = []
    for menu in P3_MENUS:
        for ac in AC_BRANDS:
            for dc in DC_BRANDS:
                cases.append(_matrix_case(menu, ac, dc, ac_sequence_for_menu(menu)))
    return cases
