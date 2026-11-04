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
    "Bluesight": ["SYST:MODE SAS"],  # 先切 SAS 再写 STC 曲线块
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
    """同压三相启机（EDIT ALL）；保留旧名供矩阵测试导入。"""
    return ac_startup_three_phase(volt, freq) + ac_output_on_sequence() + ac_output_off_sequence()


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


def bluesight_stc_from_iv(vmp, imp, voc=None, isc=None, pf="100", ff=None):
    """由试验对话框 Vmp/Imp（及可选 Voc/Isc、功率百分比、填充因子）得到蓝点 STC 三元组。

    ff 显式传入时优先使用（IOT Sandia 的填充因子），不再用四点反算顶替。

    Returns:
        (pmpp_kw, umpp_v, ff) 或 None（参数非法）。
    """
    try:
        f_vmp = float(str(vmp).strip())
        f_imp = float(str(imp).strip())
    except (TypeError, ValueError, AttributeError):
        return None
    if f_vmp <= 0 or f_imp <= 0:
        return None
    pf_pct = 100.0
    if pf is not None and str(pf).strip() != "":
        vs = str(pf).strip()
        if vs.endswith("%"):
            vs = vs[:-1].strip()
        try:
            pf_pct = float(vs)
        except ValueError:
            pf_pct = 100.0
        if 0 < pf_pct <= 1.0:
            pf_pct *= 100.0
    scale = pf_pct / 100.0
    f_imp_s = f_imp * scale
    pmpp_kw = f_vmp * f_imp_s / 1000.0
    ff_out = None
    if ff is not None and str(ff).strip() != "":
        try:
            ff_out = float(str(ff).strip())
            if ff_out > 1.0 and ff_out <= 100.0:
                ff_out = ff_out / 100.0
            if not (0.0 < ff_out <= 1.0):
                ff_out = None
        except (TypeError, ValueError):
            ff_out = None
    if ff_out is None:
        ff_out = 0.8
        try:
            voc_s = "" if voc is None else str(voc).strip()
            isc_s = "" if isc is None else str(isc).strip()
            if voc_s and isc_s:
                f_voc = float(voc_s)
                f_isc_s = float(isc_s) * scale
                if f_voc > 0 and f_isc_s > 0:
                    ff_out = (f_vmp * f_imp_s) / (f_voc * f_isc_s)
                    ff_out = max(0.50, min(0.95, ff_out))
        except (TypeError, ValueError):
            pass
    if pmpp_kw <= 0:
        return None
    return (pmpp_kw, f_vmp, float(ff_out))


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
