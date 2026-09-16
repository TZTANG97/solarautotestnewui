# -*- coding: utf-8 -*-
"""WT 录波方式：一条线连续录 vs 分开录（逐点/分段存盘）。"""

from __future__ import annotations

MODE_CONTINUOUS = "continuous"
MODE_SPLIT = "split"

MODE_LABELS = {
    MODE_CONTINUOUS: "一条线连续录（单文件）",
    MODE_SPLIT: "分开录（多文件/逐点存盘）",
}

# Ui 类名 → 连续录（单文件）默认名。分开录由各试验 split 回调覆盖。
UI_CONTINUOUS_FILENAME = {
    "Ui_Dialog_thaichonglian": "Reconn_BR",
    "Ui_Dialog_thaizhiliufenliang": "DCInj_BR",
    "Ui_Dialog_thaioverloads": "Overload_BR",
    "Ui_Dialog_thaifixedPF": "FixedPF_BR",
    "Ui_Dialog_thaireactiveQcap": "QCap_BR",
    "Ui_Dialog_thaifixedQ": "Qset_BR",
    "Ui_Dialog_thaireactiveQin": "Qin_BR",
    "Ui_Dialog_thaireactiveQacc": "Qacc_BR",
    "Ui_Dialog_thaiactiveP": "Pdisp_BR",
    "Ui_Dialog_thaantibackflow": "AntiBackflow_BR",
    "Ui_Dialog_thaiguoqianya_pin": "OVUF_BR",
    "Ui_Dialog_thaiguoqianpin_immun": "Immun_BR",
    "Ui_Dialog_thaistaticQU": "QU_curve",
    "Ui_Dialog_thaiStaticQU": "QU_curve",
    "Ui_Dialog_thaidynamicQU": "QU_dyn_curve",
    "Ui_Dialog_thaitestPU": "PU_curve",
    "Ui_Dialog_thaistaticcosPhi": "CosPhi_BR",
    "Ui_Dialog_thaidynamiccosPhi": "CosPhiP_curve",
    "Ui_Dialog_thaicosPhi_Brazil": "CosPhiBR_BR",
    "Ui_Dialog_thaivoltprotect10min": "OV_10min_curve",
    "Ui_Dialog_thaiguopinjiangzai": "OF_curve",
    "Ui_Dialog_thaiqianpinshengzai": "UF_curve",
    "Ui_Dialog_thaifrequencyadaptability": "FreqAdapt_BR_5420",
    "Ui_Dialog_thaivoltageadaptability": "VoltAdapt_BR_5421",
    "Ui_Dialog_thairocof": "ROCOF_BR",
    "Ui_Dialog_thairapidvolt": "RVC_BR",
    "Ui_Dialog_thaixiebodianliu": "Harmonic_BR",
    "Ui_Dialog_thailvrt": "LVRT_BR",
    "Ui_Dialog_thaistaticmppttest": "StaticMPPT_BR",
    "Ui_Dialog_thaidynamicmppt": "DynamicMPPT_BR",
    "Ui_Dialog_thaiphasejump": "PhaseJump_BR",
}


def combo_index_to_mode(index: int) -> str:
    return MODE_CONTINUOUS if int(index) == 0 else MODE_SPLIT


def mode_to_combo_index(mode: str) -> int:
    return 0 if str(mode).strip().lower() in (MODE_CONTINUOUS, "0", "continuous", "async") else 1


def format_filename_list(names) -> str:
    return ",".join([str(n).strip() for n in names if str(n).strip()])


def apply_filename_list_to_wt_pages(stacked, names) -> None:
    """将逗号分隔文件名写入 WT 各机型页的 textEdit_FileNameList。"""
    if stacked is None:
        return
    text = format_filename_list(names)
    try:
        from PyQt5 import QtWidgets

        for page_idx in range(stacked.count()):
            page = stacked.widget(page_idx)
            if page is None:
                continue
            te = page.findChild(QtWidgets.QTextEdit, "textEdit_FileNameList")
            if te is not None:
                te.setPlainText(text)
            combo = page.findChild(QtWidgets.QComboBox, "comboBox_AutoSave")
            if combo is not None and combo.currentIndex() == 0:
                combo.setCurrentIndex(1)
    except Exception:
        pass


def resolve_continuous_filename(ui) -> str:
    """解析试验连续录单文件名：优先 ui.wt_continuous_filename，否则按 Ui 类名注册表。"""
    custom = getattr(ui, "wt_continuous_filename", None)
    if custom is not None and str(custom).strip():
        return str(custom).strip()
    return UI_CONTINUOUS_FILENAME.get(type(ui).__name__, "")


def default_names_for_mode(ui, mode: str):
    """无专用 split 回调时的默认文件名：连续录=单文件；分开录优先 split 回调。"""
    single = resolve_continuous_filename(ui) or "Record_BR"
    if mode == MODE_CONTINUOUS:
        return [single]
    split_fn = getattr(ui, "_recording_split_names_fn", None)
    if callable(split_fn):
        try:
            names = split_fn()
            if names:
                return list(names)
        except Exception:
            pass
    return [single]


def wire_recording_mode_autofill(ui, split_names_fn=None) -> None:
    """为 ui._wtStacked 各页录波方式行绑定：切换模式自动填充文件名列表。

    - 连续录：填 resolve_continuous_filename(ui)
    - 分开录：优先 split_names_fn / ui._recording_split_names_fn，否则仍填单文件名
    可重复调用；后注册的 split_names_fn 会覆盖。
    """
    stacked = getattr(ui, "_wtStacked", None)
    if stacked is None:
        return
    if split_names_fn is not None:
        ui._recording_split_names_fn = split_names_fn

    from components.wt_recording_mode_row import WtRecordingModeRow, install_on_wt_filename_group

    def _recommended():
        mode = MODE_CONTINUOUS
        try:
            from PyQt5 import QtWidgets

            s3 = getattr(ui, "comboBox_S3_record_mode", None)
            if s3 is not None:
                mode = combo_index_to_mode(s3.currentIndex())
            else:
                page = stacked.currentWidget()
                if page is not None:
                    combo = page.findChild(QtWidgets.QComboBox, "comboBox_recording_mode")
                    if combo is not None:
                        mode = combo_index_to_mode(combo.currentIndex())
        except Exception:
            pass
        return default_names_for_mode(ui, mode)

    def _fill(names=None):
        if names is None:
            names = _recommended()
        apply_filename_list_to_wt_pages(stacked, names)

    def _sync_rows(mode):
        for page_idx in range(stacked.count()):
            page = stacked.widget(page_idx)
            if page is None:
                continue
            row = page.findChild(WtRecordingModeRow)
            if row is None:
                continue
            row.blockSignals(True)
            row.set_mode(mode)
            row.blockSignals(False)

    def _on_mode(mode):
        _sync_rows(mode)
        s3 = getattr(ui, "comboBox_S3_record_mode", None)
        if s3 is not None:
            s3.blockSignals(True)
            s3.setCurrentIndex(mode_to_combo_index(mode))
            s3.blockSignals(False)
        _fill(default_names_for_mode(ui, mode))

    ui._recording_autofill_fill = _fill
    ui._recording_autofill_on_mode = _on_mode

    for page_idx in range(stacked.count()):
        page = stacked.widget(page_idx)
        row = install_on_wt_filename_group(page, _recommended)
        if row is None:
            continue
        if not getattr(row, "_autofill_mode_connected", False):
            row.mode_changed.connect(_on_mode)
            row.names_filled.connect(_fill)
            row._autofill_mode_connected = True

    _on_mode(MODE_CONTINUOUS)


def qcap_recommended_filenames(power_levels, cos_labels, mode: str = MODE_CONTINUOUS):
    """无功能力范围推荐文件名。"""
    if mode == MODE_CONTINUOUS:
        return ["QCap_BR"]
    names = []
    for pct in power_levels:
        pct_tag = ("%g" % pct).replace(".", "p")
        for cos_label in cos_labels:
            names.append("QCap_P%s_%s" % (pct_tag, cos_label))
    return names


def _format_setpoint_tag(value) -> str:
    s = ("%g" % float(value)).replace(".", "p")
    if s.startswith("-"):
        return "m" + s[1:]
    return s


def fixed_q_recommended_filenames(power_levels, q_setpoints, mode: str = MODE_CONTINUOUS):
    if mode == MODE_CONTINUOUS:
        return ["Qset_BR"]
    return [
        "Qset_P%s_Q%s" % (_format_setpoint_tag(p), _format_setpoint_tag(q))
        for p in power_levels
        for q in q_setpoints
    ]


def reactive_qin_recommended_filenames(power_levels, q_setpoints, mode: str = MODE_CONTINUOUS):
    if mode == MODE_CONTINUOUS:
        return ["Qin_BR"]
    return [
        "Qin_P%s_Q%s" % (_format_setpoint_tag(p), _format_setpoint_tag(q))
        for p in power_levels
        for q in q_setpoints
    ]


def reactive_qacc_recommended_filenames(power_levels, q_setpoints, mode: str = MODE_CONTINUOUS):
    if mode == MODE_CONTINUOUS:
        return ["Qacc_BR"]
    return [
        "Qacc_P%s_Q%s" % (_format_setpoint_tag(p), _format_setpoint_tag(q))
        for p in power_levels
        for q in q_setpoints
    ]


def active_p_recommended_filenames(power_levels, mode: str = MODE_CONTINUOUS):
    if mode == MODE_CONTINUOUS:
        return ["Pdisp_BR"]
    return ["Pdisp_P%s" % _format_setpoint_tag(p) for p in power_levels]


def fixed_pf_recommended_filenames(power_levels, mode: str = MODE_CONTINUOUS):
    if mode == MODE_CONTINUOUS:
        return ["FixedPF_BR"]
    return ["FixedPF_P%s" % _format_setpoint_tag(p) for p in power_levels]


def _apply_run_tag(names, run_tag: str = ""):
    """给文件名加轮次/时间后缀，避免再次追加或结束后重跑盖掉上一轮 CSV。"""
    tag = str(run_tag or "").strip()
    if not tag:
        return list(names)
    # 只保留文件名安全字符
    safe = "".join(ch for ch in tag if ch.isalnum() or ch in ("-", "_"))
    if not safe:
        return list(names)
    return ["%s_%s" % (n, safe) for n in names]


def harmonic_recommended_filenames(
    power_levels, mode: str = MODE_CONTINUOUS, run_tag: str = ""
):
    """谐波电流：连续录 Harmonic_BR；分开录 Harmonic_P100 等（按勾选功率点）。

    run_tag：追加/重跑时传入（如 085812），生成 Harmonic_P5_085812，避免覆盖上一轮。
    """
    if mode == MODE_CONTINUOUS:
        names = ["Harmonic_BR"]
    else:
        names = []
        seen = {}
        for p in power_levels:
            base = "Harmonic_P%s" % _format_setpoint_tag(p)
            n = seen.get(base, 0) + 1
            seen[base] = n
            names.append(base if n == 1 else "%s_%s" % (base, n))
        if not names:
            names = ["Harmonic_P100"]
    return _apply_run_tag(names, run_tag)


def previous_wt_filename_list(commands) -> list:
    """从已追加命令里取出最近一次 Upper_WT_Config 的文件名列表。"""
    import re

    last = []
    for row in commands or []:
        if not row or row[0] != "Upper_WT_Config":
            continue
        cfg = row[4] if len(row) > 4 else None
        if not isinstance(cfg, dict):
            continue
        raw = str(cfg.get("textEdit_FileNameList") or "").strip()
        if not raw:
            continue
        last = [p.strip() for p in re.split(r"[,，]", raw) if p.strip()]
    return last


def collect_harmonic_power_percents(ui):
    """③ 谐波设置里已勾选卡片的功率 %（与 Send 勾选顺序一致）。"""
    specs = (
        ("checkBox_S3", "textEdit_S1_DC1_PF_2"),
        ("checkBox_S3_2", "textEdit_S1_DC1_PF_3"),
        ("checkBox_S3_3", "textEdit_S1_DC1_PF_4"),
        ("checkBox_S3_4", "textEdit_S1_DC1_PF_5"),
        ("checkBox_S3_5", "textEdit_S1_DC1_PF_6"),
        ("checkBox_S3_10", "textEdit_S1_DC1_PF_10"),
        ("checkBox_S3_6", "textEdit_S1_DC1_PF_9"),
        ("checkBox_S3_7", "textEdit_S1_DC1_PF_7"),
        ("checkBox_S3_9", "textEdit_S1_DC1_PF_11"),
        ("checkBox_S3_8", "textEdit_S1_DC1_PF_8"),
        ("checkBox_S3_11", "textEdit_S1_DC1_PF_12"),
    )
    percents = []
    for cb_name, pf_name in specs:
        cb = getattr(ui, cb_name, None)
        if cb is None or not cb.isChecked():
            continue
        te = getattr(ui, pf_name, None)
        raw = te.toPlainText().strip() if te is not None else ""
        try:
            percents.append(float(raw))
        except (TypeError, ValueError):
            percents.append(float(len(percents) + 1))
    return percents


def overload_recommended_filenames(mode: str = MODE_CONTINUOUS):
    """过载能力：单段 90min，连续录/分开录都是 1 个文件，名字区分路径。"""
    if mode == MODE_CONTINUOUS:
        return ["Overload_BR"]
    return ["Overload_90min"]


def dc_injection_recommended_filenames(step_percents, mode: str = MODE_CONTINUOUS):
    """直流分量：连续录 DCInj_BR；分开录 DCInj_S3_P100 等。"""
    if mode == MODE_CONTINUOUS:
        return ["DCInj_BR"]
    names = []
    for step_no, pct in step_percents:
        names.append("DCInj_S%s_P%s" % (step_no, _format_setpoint_tag(pct)))
    return names or ["DCInj_S3_P100"]


def reconnect_recommended_filenames(step_nos, mode: str = MODE_CONTINUOUS):
    """重连：连续录 Reconn_BR；分开录 Reconn_S3 等。"""
    if mode == MODE_CONTINUOUS:
        return ["Reconn_BR"]
    names = ["Reconn_S%s" % step_no for step_no in step_nos]
    return names or ["Reconn_S3"]


def dedupe_errors(errors):
    seen = set()
    out = []
    for msg in errors or []:
        key = str(msg).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out
