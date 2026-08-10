# -*- coding: utf-8 -*-
"""国产 AC/DC 软件映射模拟：P0 菜单 × 品牌 的典型 SCPI 序列。

不连真机。供 pytest 矩阵与后续抽验扩展复用。
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

AC_BRANDS = ("Chroma", "Itech")
DC_BRANDS = ("Chroma", "Bluesight", "Itech")


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


def p0_matrix_cases() -> list[dict]:
    """返回可参数化用例：每个 P0 菜单 × AC 品牌 × DC 品牌。"""
    cases: list[dict] = []
    for menu in P0_MENUS:
        for ac in AC_BRANDS:
            for dc in DC_BRANDS:
                cases.append(
                    {
                        "menu": menu,
                        "ac_brand": ac,
                        "dc_brand": dc,
                        "ac_cmds": ac_smoke_sequence(single_phase=True),
                        "dc_preamble": list(DC_MODE_PREAMBLE[dc]),
                        "dc_bluesight_cmds": (
                            dc_bluesight_smoke_sequence() if dc == "Bluesight" else []
                        ),
                    }
                )
    return cases


def p2_matrix_cases() -> list[dict]:
    """P2 菜单矩阵（快速电压变化用阶跃序列）。"""
    cases: list[dict] = []
    for menu in P2_MENUS:
        for ac in AC_BRANDS:
            for dc in DC_BRANDS:
                cases.append(
                    {
                        "menu": menu,
                        "ac_brand": ac,
                        "dc_brand": dc,
                        "ac_cmds": ac_rapid_volt_step_sequence(),
                        "dc_preamble": list(DC_MODE_PREAMBLE[dc]),
                        "dc_bluesight_cmds": (
                            dc_bluesight_smoke_sequence() if dc == "Bluesight" else []
                        ),
                    }
                )
    return cases
