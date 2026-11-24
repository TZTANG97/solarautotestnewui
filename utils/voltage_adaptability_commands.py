from utils.dc_channels import s1_dc_slots
# -*- coding: utf-8 -*-
"""电压适应性：巴西 Ordinance 5.4.21 流程（对齐频率适应性更新率扫压，改扫电压）。"""

import re

from utils.safe_shutdown import (
    build_forced_shutdown_rows,
    enabled_shutdown_dc_channels,
)
from utils.time_helpers import SetTimeFunction
from utils.ac_scpi_commands import (
    append_ac_startup_from_ui,
    append_chroma_three_phase_setpoints,
    append_legacy_three_phase_setpoints,
    append_volt_set,
    fmt_ac_volt,
    resolve_chroma_61800,
)

_fmt_volt = fmt_ac_volt

# WT 通用模板 / 其它试验残留的文件名，电压适应性 Send 时勿保留
_STALE_WT_NAME_RE = re.compile(
    r"(ambient|freq[_-]?br|guopin|qianpin|overfreq|underfreq|rocof|"
    r"pu_curve|qu_curve|cosphi|fixed.?pf|reactive)",
    re.I,
)
_VOLT_LADDER_BAND_RE = re.compile(
    r"^\s*([0-9]+(?:\.[0-9]+)?)\s*[-~～]\s*([0-9]+(?:\.[0-9]+)?)"
    r"(?:\s*[@,，]\s*([0-9]+(?:\.[0-9]+)?)\s*(?:秒|s|S)?)?\s*$"
)


def _empty_row():
    return ["" for _ in range(10)]


def _row_ac_write(cmd):
    row = _empty_row()
    row[0] = "AC"
    row[1] = "write"
    row[2] = cmd
    return row


def _row_ac_wait_idn(wait_01s, slot=9):
    row = _empty_row()
    row[0] = "AC"
    row[1] = "query"
    row[2] = "*IDN?"
    row[slot] = wait_01s
    return row


def _row_wt_async_marker(marker):
    """连续录：col6=ASYNC_START 只启动不阻塞；WAIT_END 等停表。禁止用数字 col6（会卡死扫压）。"""
    row = _empty_row()
    row[0] = "AC"
    row[1] = "query"
    row[2] = "*IDN?"
    row[6] = marker
    return row


def _sum_wait_01s(rows):
    """统计命令行 col8/col9 驻留（0.1s 单位）。"""
    total = 0
    for r in rows or []:
        for slot in (8, 9):
            if len(r) <= slot:
                continue
            raw = r[slot]
            if raw in ("", None):
                continue
            try:
                total += int(float(raw))
            except (TypeError, ValueError):
                continue
    return total


def _count_sweep_dwell_steps(rows):
    """
    扫压循环次数：每条带 col8/col9 驻留的命令算一步。
    0.1V 量化会跳过重复 VOLT，但驻留行仍保留 → 开销须按步数而非仅 VOLT 条数计。
    """
    n = 0
    for r in rows or []:
        for slot in (8, 9):
            if len(r) <= slot:
                continue
            raw = r[slot]
            if raw in ("", None):
                continue
            try:
                if int(float(raw)) > 0:
                    n += 1
                    break
            except (TypeError, ValueError):
                continue
    return n


def estimate_continuous_record_01s(band_rows, *, scpi_overhead_01s_per_step=3):
    """
    连续录 StopTime 用墙钟：Σ驻留(col8/col9) + 每扫压步 SCPI 开销。

    真机爱科 Modbus 下单步常见约 0.25~0.35s（VOLT 写 + *IDN? + 驻留），
    默认开销按 0.3s/步（3 个 0.1s tick），避免 StopTime 早于扫压结束导致录波截断。
    """
    wait_01s = _sum_wait_01s(band_rows)
    n_dwell = _count_sweep_dwell_steps(band_rows)
    n_volt = sum(
        1
        for r in (band_rows or [])
        if len(r) > 2 and str(r[2]).strip().upper().startswith("VOLT")
    )
    n_steps = max(n_dwell, n_volt)
    overhead = max(0, int(scpi_overhead_01s_per_step)) * n_steps
    return wait_01s + overhead, wait_01s, n_volt, n_dwell


def suggested_stoptime_margin_sec(wall_01s, *, n_volt=0):
    """按扫段长度选 StopTime 余量：短扫频小余量，长扫压大余量。

    ROCOF 等短扫若固定 +60s，AC 早已扫完仍会空等录波；
    电压适应性细步进则需要较大余量，避免回额定前停录。
    """
    wall_sec = max(0.0, float(wall_01s or 0) / 10.0)
    if int(n_volt or 0) > 50 or wall_sec >= 180.0:
        return 60
    if wall_sec >= 90.0:
        return 30
    return 15


def stoptime_str_from_wall_01s(wall_01s, *, margin_sec=None, min_sec=20, n_volt=0):
    """墙钟(0.1s) + 余量 → hh:mm:ss（WT textEdit_StopTime）。"""
    if margin_sec is None:
        margin_sec = suggested_stoptime_margin_sec(wall_01s, n_volt=n_volt)
    stop_sec = int(round(int(wall_01s or 0) / 10.0 + int(margin_sec)))
    stop_sec = max(int(min_sec), stop_sec)
    hh, rem = divmod(stop_sec, 3600)
    mm, ss = divmod(rem, 60)
    return f"{hh:02d}:{mm:02d}:{ss:02d}", stop_sec


def extract_continuous_band_rows(commands, start_index=None):
    """从 ASYNC_START 到 WAIT_END（含）截取连续录扫压段。"""
    rows = list(commands or [])
    async_i = None
    if start_index is not None and 0 <= int(start_index) < len(rows):
        if any(
            len(r) > 6 and str(r[6]).strip().upper() == "ASYNC_START"
            for r in rows[int(start_index) : int(start_index) + 1]
        ):
            async_i = int(start_index)
    if async_i is None:
        for i, r in enumerate(rows):
            if len(r) > 6 and str(r[6]).strip().upper() == "ASYNC_START":
                async_i = i
                break
    if async_i is None:
        return []
    wait_i = None
    for j in range(async_i, len(rows)):
        if len(rows[j]) > 6 and str(rows[j][6]).strip().upper() == "WAIT_END":
            wait_i = j
            break
    if wait_i is None:
        return rows[async_i:]
    return rows[async_i : wait_i + 1]


def recalculate_stoptime_from_band_rows(band_rows, *, margin_sec=None):
    """按命令表扫压段重算 StopTime（ASYNC_START 前刷新 config_dict 用）。"""
    wall_01s, wait_01s, n_volt, n_dwell = estimate_continuous_record_01s(band_rows)
    stop_str, stop_sec = stoptime_str_from_wall_01s(
        wall_01s, margin_sec=margin_sec, n_volt=n_volt
    )
    return stop_str, stop_sec, wall_01s, wait_01s, n_volt, n_dwell


def is_stale_wt_filename(name):
    """其它试验 / WT 模板残留名（如 100%_ambient、freq_br_*）。"""
    raw = str(name or "").strip()
    if not raw:
        return True
    if "," in raw or "，" in raw:
        return True
    if _STALE_WT_NAME_RE.search(raw):
        return True
    return False


def parse_voltage_ladder_text(text, default_duration_s=30.0):
    """
    解析电压 list：`230-253@30` / `230~195@30s`，多段逗号或换行。
    返回 [(start, end, duration_s), ...]
    """
    raw = str(text or "").strip()
    if not raw:
        return []
    parts = []
    for chunk in re.split(r"[\n,，;；]+", raw):
        chunk = chunk.strip()
        if not chunk or chunk.startswith("#"):
            continue
        m = _VOLT_LADDER_BAND_RE.match(chunk)
        if not m:
            continue
        start, end, dur = m.group(1), m.group(2), m.group(3)
        try:
            dur_s = float(dur) if dur not in (None, "") else float(default_duration_s)
        except (TypeError, ValueError):
            dur_s = float(default_duration_s)
        if dur_s <= 0:
            continue
        parts.append((start, end, dur_s))
    return parts


def collect_voltage_ladder_bands(ui, side_tag, default_duration_s=30.0):
    te = getattr(ui, "textEdit_VoltageLadder_%s" % side_tag, None)
    if te is None:
        return []
    try:
        text = te.toPlainText()
    except Exception:
        text = ""
    return parse_voltage_ladder_text(text, default_duration_s=default_duration_s)


def _row_device_write(device, cmd):
    row = _empty_row()
    row[0] = device
    row[1] = "write"
    row[2] = cmd
    return row


def build_volt_step_list(
    volt_start,
    volt_end,
    real_test_time_s,
    per_second_range,
    use_rate,
    *,
    chroma_61800=False,
):
    """
    巴西过欠压适应性同款：勾更新率时，在数据采集时间内均分扫压；
    不勾则只取起点。
    real_test_time_s / per_second_range 均为「秒」单位。
    chroma_61800=True 时输出电压量化到 0.1 V；相邻重复点保留，以维持驻留时长。
    """
    start = str(volt_start).strip()
    end = str(volt_end).strip()
    if not start and not end:
        return []
    if not start:
        start = end
    if not end:
        end = start
    if not use_rate or start == end:
        return [_fmt_volt(start, chroma_61800=chroma_61800)]

    f0 = float(start)
    f1 = float(end)
    delta = abs(f1 - f0)
    total_count = max(1, int(float(real_test_time_s) * float(per_second_range)))
    step = delta / total_count
    out = []
    cur = f0
    ascending = f1 > f0
    while True:
        if ascending:
            if cur < f1:
                out.append(_fmt_volt(cur, chroma_61800=chroma_61800))
                cur = cur + step
            else:
                out.append(_fmt_volt(f1, chroma_61800=chroma_61800))
                break
        else:
            if f1 < cur:
                out.append(_fmt_volt(cur, chroma_61800=chroma_61800))
                cur = cur - step
            else:
                out.append(_fmt_volt(f1, chroma_61800=chroma_61800))
                break
    return out


def _interval_seconds(value, unit):
    """时间 → 秒（保留亚 0.1s，避免 SetTimeFunction 对 50ms 截成 0）。"""
    v = float(value)
    if unit == "小时":
        return v * 3600.0
    if unit == "分钟":
        return v * 60.0
    if unit == "秒":
        return v
    if unit == "毫秒":
        return v / 1000.0
    return v


def read_update_rate(ui):
    """
    读取全局更新率。返回 (ok, err, rate_interval_s, per_second)。
    rate_interval_s：每步间隔（秒）；per_second：每秒步数。
    """
    rate_on = getattr(ui, "checkBox_S2_update_rate", None)
    if rate_on is None or not rate_on.isChecked():
        return True, "", None, None
    te = getattr(ui, "textEdit_S2_update_rate", None)
    cmb = getattr(ui, "comboBox_S2_update_rate", None)
    if te is None or cmb is None:
        return False, "电压适应性 更新率控件缺失", None, None
    raw = te.toPlainText().strip()
    if not raw:
        return False, "电压适应性 更新率未填写", None, None
    try:
        interval_s = _interval_seconds(raw, cmb.currentText())
    except (TypeError, ValueError):
        return False, "电压适应性 更新率格式错误", None, None
    if interval_s <= 0:
        return False, "电压适应性 更新率必须大于 0", None, None
    return True, "", interval_s, 1.0 / interval_s


def append_volt_band_brazil(
    out_rows,
    phase_mode,
    volt_start,
    volt_end,
    duration_01s,
    *,
    use_rate,
    rate_interval_s,
    per_second_range,
    wt_first_trigger,
    chroma_61800=False,
):
    """
    巴西 5.4.21 / 过欠压适应性：扫压步进 + 每步等待。
    wt_first_trigger=True：首步前插入 ASYNC_START（不阻塞），所有 dwell 一律 col[9]。
    禁止把等待秒数写进 col[6]：数字 col6 会启动 WT 并阻塞到录完，扫压被卡在起点。
    返回 (ok, err, end_volt, used_wt_trigger)。
    """
    real_s = float(duration_01s) / 10.0
    steps = build_volt_step_list(
        volt_start,
        volt_end,
        real_s,
        per_second_range or 1.0,
        use_rate=bool(use_rate and rate_interval_s and per_second_range),
        chroma_61800=chroma_61800,
    )
    if not steps:
        return False, "电压区间未填写", None, False

    wait_01s = max(1, int(round(float(rate_interval_s) * 10))) if use_rate and rate_interval_s else int(duration_01s)

    triggered = False
    multi_step = use_rate and rate_interval_s and len(steps) > 1
    prev_step = None
    for i, step in enumerate(steps):
        if wt_first_trigger and not triggered:
            out_rows.append(_row_wt_async_marker("ASYNC_START"))
            triggered = True
        # 0.1 V 量化后相邻步可能相同：跳过重复 VOLT，仍保留等待以维持总驻留
        if step != prev_step:
            append_volt_set(
                out_rows,
                phase_mode,
                step,
                edit_all=(i == 0 or prev_step is None),
                chroma_61800=chroma_61800,
            )
            prev_step = step
        if multi_step:
            out_rows.append(_row_ac_wait_idn(wait_01s, slot=9))
        else:
            # 单点 / 不扫压：保持整段数据采集时间（仍用 col9，勿用数字 col6）
            out_rows.append(_row_ac_wait_idn(int(duration_01s), slot=9))
            break
    return True, "", steps[-1], triggered


def append_enabled_bands(
    ui,
    out_rows,
    phase_mode,
    step_nums,
    side_tag,
    page_attr,
    *,
    rate_interval_s=None,
    per_second_range=None,
    global_rate_on=False,
    wt_armed=False,
    chroma_61800=False,
):
    """
    遍历启用电压带。返回 (ok, error, band_metas, wt_armed)。
    优先 textEdit_VoltageLadder_<side> list；空则回退勾选卡片。
    wt_armed：若仍为 True，表示尚未插入 ASYNC_START。
    """
    page_cb = getattr(ui, page_attr, None)
    if page_cb is not None and not page_cb.isChecked():
        return True, "", [], wt_armed

    metas = []
    ladder = collect_voltage_ladder_bands(ui, side_tag)
    if ladder:
        for bi, (volt_start, volt_end, dur_s) in enumerate(ladder):
            try:
                duration_01s = SetTimeFunction(float(dur_s), "秒")
            except (TypeError, ValueError):
                return False, "电压适应性 list 时长格式错误", [], wt_armed
            use_rate = bool(global_rate_on)
            ok, err, _end_v, triggered = append_volt_band_brazil(
                out_rows,
                phase_mode,
                volt_start,
                volt_end,
                duration_01s,
                use_rate=use_rate,
                rate_interval_s=rate_interval_s,
                per_second_range=per_second_range,
                wt_first_trigger=wt_armed,
                chroma_61800=chroma_61800,
            )
            if not ok:
                return False, err or "电压适应性 list 无效", [], wt_armed
            if triggered:
                wt_armed = False
            prefix = "OV" if side_tag == "guoya" else "UV"
            safe_start = str(volt_start).replace(".", "p")
            safe_end = str(volt_end).replace(".", "p")
            metas.append({
                "name": "%s_L%d_%s-%s" % (prefix, bi + 1, safe_start, safe_end),
                "duration_01s": duration_01s,
                "step": bi + 1,
                "side": side_tag,
                "source": "ladder",
            })
        return True, "", metas, wt_armed

    for sn in step_nums:
        cb = getattr(ui, "checkBox_S%d" % sn, None)
        if cb is None or not cb.isChecked():
            continue
        te_start = getattr(ui, "textEdit_S%d_volt_start_%s" % (sn, side_tag), None)
        te_end = getattr(ui, "textEdit_S%d_volt_end_%s" % (sn, side_tag), None)
        te_dur = getattr(ui, "textEdit_S%d_test_duration_%s" % (sn, side_tag), None)
        cmb_unit = getattr(ui, "comboBox_S%d_test_time_unit_%s" % (sn, side_tag), None)
        if te_start is None or te_end is None or te_dur is None or cmb_unit is None:
            return False, "电压适应性 step%d 控件缺失" % sn, [], wt_armed

        volt_start = te_start.toPlainText().strip()
        volt_end = te_end.toPlainText().strip()
        dur_text = te_dur.toPlainText().strip()
        if not volt_start and not volt_end:
            return False, "电压适应性 step%d 电压区间未填写" % sn, [], wt_armed
        if not dur_text:
            return False, "电压适应性 step%d 测试时间未填写" % sn, [], wt_armed
        try:
            duration_01s = SetTimeFunction(float(dur_text), cmb_unit.currentText())
        except (TypeError, ValueError):
            return False, "电压适应性 step%d 测试时间格式错误" % sn, [], wt_armed

        rate_cb = getattr(ui, "checkBox_S%d_RATE" % sn, None)
        card_rate = True if rate_cb is None else rate_cb.isChecked()
        use_rate = bool(global_rate_on and card_rate)

        ok, err, _end_v, triggered = append_volt_band_brazil(
            out_rows,
            phase_mode,
            volt_start,
            volt_end,
            duration_01s,
            use_rate=use_rate,
            rate_interval_s=rate_interval_s,
            per_second_range=per_second_range,
            wt_first_trigger=wt_armed,
            chroma_61800=chroma_61800,
        )
        if not ok:
            return False, err, [], wt_armed
        if triggered:
            wt_armed = False

        start = volt_start or volt_end
        end = volt_end or volt_start
        prefix = "OV" if side_tag == "guoya" else "UV"
        safe_start = str(start).replace(".", "p")
        safe_end = str(end).replace(".", "p")
        metas.append({
            "name": "%s_S%d_%s-%s" % (prefix, sn, safe_start, safe_end),
            "duration_01s": duration_01s,
            "step": sn,
            "side": side_tag,
            "source": "card",
        })
    return True, "", metas, wt_armed


def volt_side_has_bands(ui, side_tag, page_attr, step_nums):
    """过压/欠压页启用且存在 list 或勾选卡片。"""
    page_cb = getattr(ui, page_attr, None)
    if page_cb is None or not page_cb.isChecked():
        return False
    if collect_voltage_ladder_bands(ui, side_tag):
        return True
    for sn in step_nums:
        cb = getattr(ui, "checkBox_S%d" % sn, None)
        if cb is not None and cb.isChecked():
            return True
    return False


def want_split_ov_uv_recording(ui):
    """过压+欠压均启用且 UI 勾选分文件录制。"""
    split_cb = getattr(ui, "checkBox_S2_split_ov_uv_files", None)
    if split_cb is None or not split_cb.isChecked():
        return False
    return (
        volt_side_has_bands(ui, "guoya", "checkBox_guoya_page", list(range(3, 12)))
        and volt_side_has_bands(ui, "qianya", "checkBox_qianya_page", list(range(12, 21)))
    )


def resolve_volt_file_name_list(band_metas, existing_names=None, split_two_files=False):
    """
    巴西流程默认整次连续录 1 条，推荐 VoltAdapt_BR_5421。
    split_two_files=True 时返回两条名（过压/欠压各一），对齐 5.4.21 分文件分析。
    不保留 WT 模板 / 其它试验残留名（100%_ambient、freq_br_* 等）。
    """
    defaults = (
        ["VoltAdapt_OV_5421", "VoltAdapt_UV_5421"]
        if split_two_files
        else ["VoltAdapt_BR_5421"]
    )
    raw_existing = [str(p).strip() for p in (existing_names or []) if str(p).strip()]
    if split_two_files:
        existing = [p for p in raw_existing if p and not is_stale_wt_filename(p)]
        if len(existing) >= 2:
            return existing[:2]
        if len(existing) == 1:
            return [existing[0], defaults[1]]
        return list(defaults)
    auto_names = [str(m.get("name") or "").strip() for m in (band_metas or []) if m]
    auto_names = [n for n in auto_names if n]
    existing = [p for p in raw_existing if p and not is_stale_wt_filename(p)]
    if len(existing) == 1:
        return existing
    if auto_names and len(existing) == len(auto_names):
        return existing
    return list(defaults)


def default_dc_iv_resolver(vmp, imp, voc, isc, pf, dc_num):
    """轻量 DC IV 解析（模拟/无厂家配置时用）。

    默认按 Chroma 包一层 MODE TABLE + SELect，避免只下 IVC 点表却无输出功率。
    """
    try:
        f_vmp = float(str(vmp).strip())
        f_imp = float(str(imp).strip())
        f_voc = float(str(voc).strip())
        f_isc = float(str(isc).strip())
        _ = float(str(pf).strip().rstrip("%"))
    except (TypeError, ValueError):
        return "err1", None
    if min(f_vmp, f_imp, f_voc, f_isc) <= 0:
        return "err1", None
    if f_imp >= f_isc or f_vmp >= f_voc:
        return "err1", None
    if f_isc > 1000:
        return "err2", None
    _ = dc_num
    return "ok", [
        "OUTP:MODE TABLE",
        "IVC:IT %.3f,%.3f" % (f_imp, f_isc),
        "IVC:VT %.3f,%.3f" % (f_vmp, f_voc),
        "IVCurve:SELect 1",
    ]


def build_voltage_adaptability_plan(
    ui,
    *,
    wt_config_dict=None,
    str_add_flag="0",
    project_change="0",
    existing_commands=None,
    dc_iv_resolver=None,
    per_dc_factor=None,
    chroma_61800=None,
):
    """根据 Dialog UI 生成巴西 5.4.21 命令计划。

    chroma_61800：None 时按当前已连接 AC 的 *IDN? 自动识别（Chroma 61800 / 通用）。
    """
    if wt_config_dict is None:
        wt_config_dict = {}
    if dc_iv_resolver is None:
        dc_iv_resolver = default_dc_iv_resolver
    if chroma_61800 is None:
        chroma_61800 = resolve_chroma_61800()

    commands = list(existing_commands or [])
    if str_add_flag == "0":
        commands = []

    steps = []
    dc_errors = []
    test_program = []
    wt_type = None
    wt_is_checked = "0"

    need_wt = True  # 同项目追加也刷新 WT 文件名，避免多轮覆盖
    if need_wt:
        row = _empty_row()
        row[0] = "Upper_WT_Config"
        row[3] = "config_dict"
        row[4] = wt_config_dict
        commands.append(row)

    if str_add_flag == "1" and project_change == "1":
        row = _empty_row()
        row[0] = "AC"
        row[1] = "wait"
        row[2] = ""
        row[9] = 3000
        commands.append(row)

    phase_mode = ui.comboBox_S1_AC_2.currentText()

    # step1
    if ui.checkBox_S1.isChecked():
        step_rows = []
        f_s1 = SetTimeFunction(float(ui.textEdit_S1_TIME.toPlainText()), ui.comboBox_S1_TIME.currentText())
        f_ac_wait = SetTimeFunction(
            float(ui.textEdit_S1_ACWaitTIME.toPlainText()),
            ui.comboBox_S1_ACWaitTIME.currentText(),
        )
        ac_status = ui.comboBox_S1_AC.currentText()

        append_ac_startup_from_ui(ui, commands, step_rows, chroma_61800=chroma_61800)

        row = _row_ac_write("OUTP ON" if ac_status == "开启" else "OUTP OFF")
        row[9] = f_ac_wait
        commands.append(row)
        step_rows.append(row)

        for ch, device, dc_num, label in s1_dc_slots(ui):
            if not getattr(ui, "checkBox_S1_DC%d" % ch).isChecked():
                continue
            vmp = getattr(ui, "textEdit_S1_DC%d_VOLT" % ch).toPlainText()
            imp = getattr(ui, "textEdit_S1_DC%d_CURR" % ch).toPlainText()
            voc = getattr(ui, "textEdit_S1_DC%d_Voc" % ch).toPlainText()
            isc = getattr(ui, "textEdit_S1_DC%d_Isc" % ch).toPlainText()
            pf = getattr(ui, "textEdit_S1_DC%d_PF" % ch).toPlainText()
            code, iv_cmds = dc_iv_resolver(vmp, imp, voc, isc, pf, dc_num)
            if code == "err1":
                dc_errors.append("%s赋值错误" % label)
            elif code == "err2":
                dc_errors.append("%sIsc,Imp赋值超范围" % label)
            elif code == "err_brand":
                dc_errors.append("%sDC命令与厂家不匹配（已拦截致茂IVC混用）" % label)
            elif code == "ok" and iv_cmds:
                wait = _row_ac_wait_idn(2, slot=8)
                commands.append(wait)
                step_rows.append(wait)
                for cmd in iv_cmds:
                    row = _row_device_write(device, cmd)
                    commands.append(row)
                    step_rows.append(row)

            status = getattr(ui, "comboBox_S1_DC%d" % ch).currentText()
            row = _row_device_write(device, "OUTP ON" if status == "开启" else "OUTP OFF")
            commands.append(row)
            step_rows.append(row)
            wait = _row_ac_wait_idn(2, slot=8)
            commands.append(wait)
            step_rows.append(wait)

        wait = _row_ac_wait_idn(f_s1)
        commands.append(wait)
        step_rows.append(wait)
        steps.append(step_rows)

    # step2 WT meta
    if ui.checkBox_S2.isChecked():
        wt_is_checked = "1"
        if need_wt:
            if ui.radioButton_S2_WT3000.isChecked():
                wt_type = "WT3000"
            elif ui.radioButton_S2_WT1800.isChecked():
                wt_type = "WT1800"
            elif ui.radioButton_S2_WT1806E.isChecked():
                wt_type = "WT1806E"
            elif ui.radioButton_S2_WT5000.isChecked():
                wt_type = "WT5000"
            if wt_type:
                test_program.append(["12", wt_type])

    ok_rate, rate_err, rate_interval_s, per_second = read_update_rate(ui)
    if not ok_rate:
        return {
            "ok": False,
            "error": rate_err,
            "dc_errors": dc_errors,
            "commands": commands,
            "steps": steps,
            "wt_type": wt_type,
            "test_program": test_program,
            "wt_is_checked": wt_is_checked,
            "band_metas": [],
            "file_names": [],
            "wt_rounds": 0,
            "wt_continuous": False,
            "band_duration_01s": 0,
        }

    global_rate_on = rate_interval_s is not None
    band_rows = []
    band_metas = []
    wt_armed = wt_is_checked == "1"
    split_two_files = want_split_ov_uv_recording(ui)
    band_kw = {
        "rate_interval_s": rate_interval_s,
        "per_second_range": per_second,
        "global_rate_on": global_rate_on,
        "chroma_61800": chroma_61800,
    }
    if split_two_files:
        ok_bands, band_err, metas_of, wt_armed = append_enabled_bands(
            ui,
            band_rows,
            phase_mode,
            list(range(3, 12)),
            "guoya",
            "checkBox_guoya_page",
            wt_armed=wt_armed,
            **band_kw,
        )
        if ok_bands and metas_of:
            band_metas.extend(metas_of)
            if wt_is_checked == "1":
                band_rows.append(_row_wt_async_marker("WAIT_END"))
                wt_armed = True
        if ok_bands:
            ok_bands, band_err, metas_uf, wt_armed = append_enabled_bands(
                ui,
                band_rows,
                phase_mode,
                list(range(12, 21)),
                "qianya",
                "checkBox_qianya_page",
                wt_armed=wt_armed,
                **band_kw,
            )
            if ok_bands and metas_uf:
                band_metas.extend(metas_uf)
                if wt_is_checked == "1":
                    band_rows.append(_row_wt_async_marker("WAIT_END"))
    else:
        ok_bands, band_err, metas_of, wt_armed = append_enabled_bands(
            ui,
            band_rows,
            phase_mode,
            list(range(3, 12)),
            "guoya",
            "checkBox_guoya_page",
            wt_armed=wt_armed,
            **band_kw,
        )
        if ok_bands:
            band_metas.extend(metas_of)
            ok_bands, band_err, metas_uf, wt_armed = append_enabled_bands(
                ui,
                band_rows,
                phase_mode,
                list(range(12, 21)),
                "qianya",
                "checkBox_qianya_page",
                wt_armed=wt_armed,
                **band_kw,
            )
            if ok_bands:
                band_metas.extend(metas_uf)
        if wt_is_checked == "1" and band_rows and any(
            len(r) > 6 and str(r[6]).strip().upper() == "ASYNC_START" for r in band_rows
        ):
            band_rows.append(_row_wt_async_marker("WAIT_END"))
    if not ok_bands:
        return {
            "ok": False,
            "error": band_err,
            "dc_errors": dc_errors,
            "commands": commands,
            "steps": steps,
            "wt_type": wt_type,
            "test_program": test_program,
            "wt_is_checked": wt_is_checked,
            "band_metas": [],
            "file_names": [],
            "wt_rounds": 0,
            "wt_continuous": False,
            "band_duration_01s": 0,
        }

    commands.extend(band_rows)
    if band_rows:
        steps.append(list(band_rows))

    file_names = resolve_volt_file_name_list(band_metas, split_two_files=split_two_files)
    if wt_is_checked == "1" and band_metas:
        wt_rounds = 2 if split_two_files else 1
    else:
        wt_rounds = 0
    # StopTime 必须覆盖实际扫压墙钟，禁止只用 UI 数据采集合计（会早停表、命令还在跑）
    ui_duration_01s = sum(int(m.get("duration_01s") or 0) for m in band_metas)
    wall_01s, wait_01s, n_volt, n_dwell = estimate_continuous_record_01s(band_rows)
    band_duration_01s = max(ui_duration_01s, wall_01s)
    max_band_duration_01s = band_duration_01s

    # shutdown
    if ui.checkBox_S_End.isChecked():
        dc_channels = enabled_shutdown_dc_channels(
            ui, end_fmt="checkBox_S_End_DC%d"
        )
        step_rows = build_forced_shutdown_rows(
            dc_channels=dc_channels,
            per_dc_factor=per_dc_factor,
        )
        commands.extend(step_rows)
        steps.append(step_rows)

    return {
        "ok": True,
        "error": None,
        "dc_errors": dc_errors,
        "commands": commands,
        "steps": steps,
        "wt_type": wt_type,
        "test_program": test_program,
        "wt_is_checked": wt_is_checked,
        "band_metas": band_metas,
        "file_names": file_names,
        "wt_rounds": wt_rounds,
        "wt_continuous": wt_rounds == 1,
        "split_two_files": split_two_files,
        "band_duration_01s": band_duration_01s,
        "max_band_duration_01s": max_band_duration_01s,
        "ui_duration_01s": ui_duration_01s,
        "sweep_wait_01s": wait_01s,
        "sweep_volt_steps": n_volt,
        "sweep_dwell_steps": n_dwell,
    }
