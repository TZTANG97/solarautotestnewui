# -*- coding: utf-8 -*-
"""Replace hardcoded S3~S17 blocks with frequency-list generation."""
from __future__ import annotations

import re
from pathlib import Path

PATH = Path(r"E:\solarautotestnewui\SCPITestWave.py")

NEW_GUOPIN = r'''
    # 频率台阶：优先 FrequencyLadder list（点数不限）；否则回退 S3~S17 卡片
    if uiThaiGuoPinJiangZai.checkBox_S3.isChecked() or (
        getattr(uiThaiGuoPinJiangZai, "textEdit_FrequencyLadder", None) is not None
        and (uiThaiGuoPinJiangZai.textEdit_FrequencyLadder.toPlainText() or "").strip()
    ):
        from utils.overfreq_ladder_commands import (
            append_freq_ladder_commands,
            collect_freq_points_with_per_step_dwell,
            sync_freq_list_to_legacy_cards,
        )
        try:
            sync_freq_list_to_legacy_cards(uiThaiGuoPinJiangZai)
        except Exception as _e:
            _append_debug_log(f"[过频降载] sync list->cards failed: {_e}")
        _pts, _src = collect_freq_points_with_per_step_dwell(uiThaiGuoPinJiangZai)
        if not _pts:
            QMessageBox.information(
                None,
                "错误提示信息",
                "过频频率 list 为空或无效，请填写如 50,50.25,50.7,...",
                QMessageBox.Ok,
                QMessageBox.Ok,
            )
            return
        n_pts = append_freq_ladder_commands(
            strArrayTest, strArrayTestStep, S1ACEACHStatus, _pts
        )
        _src_label = "list" if _src == "list" else "旧卡片"
        ui.textEdit_ReturnMessage.append(
            f"[过频降载] 频率台阶 {n_pts} 点（来源={_src_label}）"
        )

    # 频率台阶连续录 1 条（ASYNC_START / WAIT_END）
    _enable_freq_step_continuous_record(
        strArrayTest,
        uiThaiGuoPinJiangZai,
        file_default="OF_curve",
        log_label="过频降载",
    )

'''

NEW_QIANPIN = r'''
    # 频率台阶：优先 FrequencyLadder list（点数不限）；否则回退 S3~S17 卡片
    if uiThaiQianPinShengZai.checkBox_S3.isChecked() or (
        getattr(uiThaiQianPinShengZai, "textEdit_FrequencyLadder", None) is not None
        and (uiThaiQianPinShengZai.textEdit_FrequencyLadder.toPlainText() or "").strip()
    ):
        from utils.overfreq_ladder_commands import (
            append_freq_ladder_commands,
            collect_freq_points_with_per_step_dwell,
            sync_freq_list_to_legacy_cards,
        )
        try:
            sync_freq_list_to_legacy_cards(uiThaiQianPinShengZai)
        except Exception as _e:
            _append_debug_log(f"[欠频升载] sync list->cards failed: {_e}")
        _pts, _src = collect_freq_points_with_per_step_dwell(uiThaiQianPinShengZai)
        if not _pts:
            QMessageBox.information(
                None,
                "错误提示信息",
                "欠频频率 list 为空或无效，请填写如 50,49.5,49.0,...",
                QMessageBox.Ok,
                QMessageBox.Ok,
            )
            return
        n_pts = append_freq_ladder_commands(
            strArrayTest, strArrayTestStep, S1ACEACHStatus, _pts
        )
        _src_label = "list" if _src == "list" else "旧卡片"
        ui.textEdit_ReturnMessage.append(
            f"[欠频升载] 频率台阶 {n_pts} 点（来源={_src_label}）"
        )

    # 频率台阶连续录 1 条（ASYNC_START / WAIT_END）
    _enable_freq_step_continuous_record(
        strArrayTest,
        uiThaiQianPinShengZai,
        file_default="UF_curve",
        log_label="欠频升载",
    )

'''


def replace_between(text: str, fn_name: str, new_block: str) -> str:
    m = re.search(rf"def {fn_name}\(\):", text)
    if not m:
        raise SystemExit(f"missing {fn_name}")
    m2 = re.search(r"\ndef [a-zA-Z_].*\(\):", text[m.end() :])
    if not m2:
        raise SystemExit(f"missing next def after {fn_name}")
    start, end = m.start(), m.end() + m2.start()
    body = text[start:end]
    i = body.find("\n    # step3\n")
    j = body.find("\n    # step_end\n")
    if i < 0 or j < 0:
        raise SystemExit(f"markers not found in {fn_name}: step3={i}, step_end={j}")
    new_body = body[:i] + "\n" + new_block + body[j:]
    print(fn_name, "removed", j - i, "chars, inserted", len(new_block))
    return text[:start] + new_body + text[end:]


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    text = replace_between(text, "thaiguopinjiangzaiSend", NEW_GUOPIN)
    text = replace_between(text, "thaiqianpinshengzaiSend", NEW_QIANPIN)
    PATH.write_text(text, encoding="utf-8")
    print("saved", PATH)


if __name__ == "__main__":
    main()
