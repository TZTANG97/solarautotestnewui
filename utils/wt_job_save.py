# -*- coding: utf-8 -*-
"""云任务交接：WT 保存目录、停机时间、录波方式、自动命名。

与 IOT app/services/solar_test_schemas/wt_layout.py 的连续录文件名表保持一致。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

RECORD_MODE_CONTINUOUS = "一条线连续录（单文件）"
RECORD_MODE_SPLIT = "分开录（多文件/逐点存盘）"
DEFAULT_STOP_TIME = "00:05:00"

CONTINUOUS_FILENAME_BY_TEST = {
    "reconnect": "Reconn_BR",
    "chonglian": "Reconn_BR",
    "dccomponent": "DCInj_BR",
    "zhiliufenliang": "DCInj_BR",
    "overload": "Overload_BR",
    "fixedpf": "FixedPF_BR",
    "reactiveqcap": "QCap_BR",
    "fixedq": "Qset_BR",
    "reactiveqin": "Qin_BR",
    "reactiveqacc": "Qacc_BR",
    "activep": "Pdisp_BR",
    "antibackflow": "AntiBackflow_BR",
    "ovuf": "OVUF_BR",
    "guoqianpin_immun": "Immun_BR",
    "staticqu": "QU_curve",
    "dynamicqu": "QU_dyn_curve",
    "testpu": "PU_curve",
    "staticcosphi": "CosPhi_BR",
    "dynamiccosphi": "CosPhiP_curve",
    "cosphibrazil": "CosPhiBR_BR",
    "voltprotect10min": "OV_10min_curve",
    "guopinjiangzai": "OF_curve",
    "qianpinshengzai": "UF_curve",
    "frequencyadaptability": "FreqAdapt_BR_5420",
    "voltageadaptability": "VoltAdapt_BR_5421",
    "rocof": "ROCOF_BR",
    "rapidvolt": "RVC_BR",
    "harmonic": "Harmonic_BR",
    "lvrt": "LVRT_BR",
    "staticmppt": "StaticMPPT_BR",
    "dynamicmppt": "DynamicMPPT_BR",
    "phasejump": "PhaseJump_BR",
}
_ALIASES = {
    "过频降载": "guopinjiangzai",
    "guopin": "guopinjiangzai",
    "of_reduce": "guopinjiangzai",
    "欠频升载": "qianpinshengzai",
    "qianpin": "qianpinshengzai",
    "谐波": "harmonic",
    "谐波电流": "harmonic",
    "谐波电流测试": "harmonic",
    "xiebodianliu": "harmonic",
    "重连": "reconnect",
    "直流分量": "dccomponent",
    "过载": "overload",
    "固定pf": "fixedpf",
    "过欠压": "ovuf",
    "过欠频": "ovuf",
}


def continuous_filename_for_test(test_key: str) -> str:
    key = str(test_key or "").strip()
    low = key.lower()
    canon = _ALIASES.get(key) or _ALIASES.get(low) or low
    return CONTINUOUS_FILENAME_BY_TEST.get(canon) or CONTINUOUS_FILENAME_BY_TEST.get(low) or "Record_BR"


def validate_stop_time(raw: str) -> tuple:
    """返回 (是否合法, 错误文案)。空串不合法。接受 时:分:秒、分:秒、秒数。"""
    text = str(raw or "").strip().replace("：", ":")
    if not text:
        return False, "请填写停机时间，格式 00:05:00、05:00 或秒数"
    parts = text.split(":")
    if len(parts) > 3:
        return False, "停机时间无效，请用 时:分:秒、分:秒 或秒数"
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        return False, "停机时间无效，请用 时:分:秒、分:秒 或秒数"
    if any(n < 0 for n in nums):
        return False, "停机时间不能为负"
    if len(nums) == 3:
        _h, m, s = nums
        if m >= 60 or s >= 60:
            return False, "停机时间的分、秒须小于 60"
        return True, ""
    if len(nums) == 2:
        _m, s = nums
        if s >= 60:
            return False, "停机时间的秒须小于 60"
        return True, ""
    if len(nums) == 1:
        return True, ""
    return False, "停机时间无效，请用 时:分:秒、分:秒 或秒数"


def dialog_recording_is_continuous(ui) -> bool:
    """读云任务钉住的录波方式，否则读 S3 下拉或当前 WT 页。缺控件时保持连续录。"""
    if ui is None:
        return True
    pinned = getattr(ui, "_wt_record_mode_from_job", None)
    if pinned in ("continuous", "split"):
        return pinned == "continuous"
    s3 = getattr(ui, "comboBox_S3_record_mode", None)
    if s3 is not None and hasattr(s3, "currentIndex"):
        try:
            return int(s3.currentIndex()) == 0
        except (TypeError, ValueError):
            return True
    stacked = getattr(ui, "_wtStacked", None)
    page = None
    try:
        if stacked is not None and hasattr(stacked, "currentWidget"):
            page = stacked.currentWidget()
    except Exception:
        page = None
    if page is None or not hasattr(page, "findChild"):
        return True
    try:
        from PyQt5 import QtWidgets

        combo = page.findChild(QtWidgets.QComboBox, "comboBox_recording_mode")
    except Exception:
        return True
    if combo is None:
        return True
    try:
        return int(combo.currentIndex()) == 0
    except (TypeError, ValueError):
        return True


def split_freq_filenames(points, file_default: str, existing: str = "") -> str:
    """分开录：已有不少于点数的名单则保留，否则按频率点展开，避免逐点覆盖同一个文件。"""
    import re

    existing_names = [p.strip() for p in re.split(r"[,，]", str(existing or "")) if p.strip()]
    clean_points = [str(p).strip() for p in (points or []) if str(p).strip()]
    if clean_points and len(existing_names) >= len(clean_points):
        return ",".join(existing_names)
    if not clean_points:
        return existing_names[0] if existing_names else str(file_default or "Record_BR")
    base = existing_names[0] if existing_names else str(file_default or "Record_BR")
    out = []
    for raw in clean_points:
        try:
            tag = ("%g" % float(raw)).replace(".", "p").replace("-", "m")
        except ValueError:
            tag = raw.replace(".", "p").replace("-", "m")
        out.append(f"{base}_{tag}")
    return ",".join(out)


def apply_split_freq_filenames(str_array_test, ui_dialog, *, file_default: str, log_label: str = "") -> str:
    """分开录不改成一条线；把文件名列表写成逐点名称。停机时间保留用户填写值。"""
    points = []
    ladder = getattr(ui_dialog, "textEdit_FrequencyLadder", None)
    raw = ""
    if ladder is not None and hasattr(ladder, "toPlainText"):
        raw = ladder.toPlainText() or ""
    elif ladder is not None and hasattr(ladder, "text"):
        raw = ladder.text() or ""
    points = [p.strip() for p in str(raw).replace("，", ",").split(",") if p.strip()]
    existing = ""
    rows = str_array_test or []
    for cfg_row in rows:
        if cfg_row and cfg_row[0] == "Upper_WT_Config" and isinstance(cfg_row[4], dict):
            existing = str(cfg_row[4].get("textEdit_FileNameList") or "")
            break
    if not existing and ui_dialog is not None:
        stacked = getattr(ui_dialog, "_wtStacked", None)
        try:
            from PyQt5 import QtWidgets

            if stacked is not None:
                page = stacked.currentWidget()
                if page is not None:
                    te = page.findChild(QtWidgets.QTextEdit, "textEdit_FileNameList")
                    if te is not None:
                        existing = te.toPlainText() or ""
        except Exception:
            existing = existing or ""
    text = split_freq_filenames(points, file_default, existing)
    for cfg_row in rows:
        if cfg_row and cfg_row[0] == "Upper_WT_Config" and isinstance(cfg_row[4], dict):
            cfg_row[4]["textEdit_FileNameList"] = text
            if str(cfg_row[4].get("comboBox_AutoSave") or "") in ("", "0", "OFF"):
                cfg_row[4]["comboBox_AutoSave"] = 1
            break
    try:
        from PyQt5 import QtWidgets

        stacked = getattr(ui_dialog, "_wtStacked", None)
        if stacked is not None:
            for page_idx in range(stacked.count()):
                page = stacked.widget(page_idx)
                if page is None:
                    continue
                te = page.findChild(QtWidgets.QTextEdit, "textEdit_FileNameList")
                if te is not None:
                    te.setPlainText(text)
    except Exception:
        pass
    if log_label:
        print(f"[{log_label}] 分开录 {len(points) or 1} 个文件: {text}", flush=True)
    return text


def record_mode_index(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return 0 if int(value) == 0 else 1
    text = str(value or "").strip()
    low = text.lower()
    if low in ("", "0", "continuous", "async") or "连续" in text:
        return 0
    if low in ("1", "split") or "分开" in text:
        return 1
    try:
        return 0 if int(float(text)) == 0 else 1
    except ValueError:
        return 0


def _is_checked(val: Any) -> bool:
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "on")
    return bool(val)


def prepare_wt_save_widgets(
    widgets: Optional[Dict[str, Any]],
    test_key: str = "",
    *,
    ensure_dir: bool = True,
) -> Dict[str, Any]:
    """补齐停机时间、自动命名文件名，并在工控机上创建保存目录。"""
    if not isinstance(widgets, dict):
        return {}
    out = dict(widgets)
    if "textEdit_SavePath" in out and ensure_dir:
        from utils.wt_save_path import ensure_wt_save_dir

        out["textEdit_SavePath"] = ensure_wt_save_dir(str(out.get("textEdit_SavePath") or "").strip())
    if "textEdit_StopTime" in out:
        raw = str(out.get("textEdit_StopTime") or "").strip().replace("：", ":")
        ok, _msg = validate_stop_time(raw)
        out["textEdit_StopTime"] = raw if ok else DEFAULT_STOP_TIME
    if _is_checked(out.get("checkBox_AutoName")) and not str(out.get("textEdit_FileNameList") or "").strip():
        out["textEdit_FileNameList"] = continuous_filename_for_test(test_key)
        if str(out.get("comboBox_AutoSave") or "") in ("", "OFF", "0"):
            out["comboBox_AutoSave"] = "自动保存"
    return out


def widgets_for_standard_apply(root, widgets: Dict[str, Any]) -> Dict[str, Any]:
    """没有 S3 录波下拉的试验（如过频降载）不把该键交给通用写入，避免记成缺失控件。"""
    if not isinstance(widgets, dict) or "comboBox_S3_record_mode" not in widgets:
        return widgets
    if _has_named_widget(root, "comboBox_S3_record_mode"):
        return widgets
    return {k: v for k, v in widgets.items() if k != "comboBox_S3_record_mode"}


def _has_named_widget(root, name: str) -> bool:
    if root is None:
        return False
    if getattr(root, name, None) is not None:
        return True
    try:
        from PyQt5.QtWidgets import QWidget

        if hasattr(root, "findChild") and root.findChild(QWidget, name) is not None:
            return True
    except Exception:
        return False
    return False


def apply_wt_save_to_dialog(root, widgets: Dict[str, Any]) -> None:
    """把保存路径、停机时间、文件名、录波方式写到 WT 各机型页。"""
    if root is None or not isinstance(widgets, dict):
        return
    from PyQt5 import QtWidgets

    pages = []
    stacked = getattr(root, "_wtStacked", None)
    try:
        if stacked is not None and hasattr(stacked, "count"):
            for i in range(int(stacked.count())):
                page = stacked.widget(i)
                if page is not None:
                    pages.append(page)
    except Exception:
        pages = []
    if not pages:
        pages = [root]

    if "comboBox_S3_record_mode" in widgets:
        try:
            setattr(
                root,
                "_wt_record_mode_from_job",
                "split" if record_mode_index(widgets.get("comboBox_S3_record_mode")) else "continuous",
            )
        except Exception:
            pass
    path = str(widgets.get("textEdit_SavePath") or "")
    stop = str(widgets.get("textEdit_StopTime") or "")
    names = str(widgets.get("textEdit_FileNameList") or "")
    mode_idx = record_mode_index(widgets.get("comboBox_S3_record_mode")) if "comboBox_S3_record_mode" in widgets else None

    for page in pages:
        _set_plain(page, "textEdit_SavePath", path)
        _set_plain(page, "textEdit_StopTime", stop)
        _set_plain(page, "textEdit_FileNameList", names)
        if "comboBox_AutoSave" in widgets:
            _set_combo(page.findChild(QtWidgets.QComboBox, "comboBox_AutoSave"), widgets.get("comboBox_AutoSave"))
        if mode_idx is not None:
            combo = page.findChild(QtWidgets.QComboBox, "comboBox_recording_mode")
            if combo is not None:
                combo.blockSignals(True)
                try:
                    combo.setCurrentIndex(mode_idx)
                finally:
                    combo.blockSignals(False)
        if "checkBox_AutoName" in widgets:
            try:
                cb = page.findChild(QtWidgets.QCheckBox, "checkBox_AutoName")
                if cb is not None:
                    cb.blockSignals(True)
                    try:
                        cb.setChecked(_is_checked(widgets.get("checkBox_AutoName")))
                    finally:
                        cb.blockSignals(False)
            except Exception:
                pass

    if mode_idx is None:
        return
    s3 = getattr(root, "comboBox_S3_record_mode", None)
    if s3 is None and hasattr(root, "findChild"):
        s3 = root.findChild(QtWidgets.QComboBox, "comboBox_S3_record_mode")
    if s3 is None:
        return
    s3.blockSignals(True)
    try:
        text = str(widgets.get("comboBox_S3_record_mode") or "")
        idx = s3.findText(text) if text else -1
        s3.setCurrentIndex(idx if idx >= 0 else mode_idx)
    finally:
        s3.blockSignals(False)


def _set_plain(page, name: str, text: str) -> None:
    if not text or page is None or not hasattr(page, "findChild"):
        return
    from PyQt5 import QtWidgets

    edit = page.findChild(QtWidgets.QTextEdit, name)
    if edit is None:
        edit = page.findChild(QtWidgets.QLineEdit, name)
    if edit is None:
        return
    if hasattr(edit, "setPlainText"):
        edit.setPlainText(text)
    elif hasattr(edit, "setText"):
        edit.setText(text)


def _set_combo(combo, value: Any) -> None:
    if combo is None or value is None:
        return
    combo.blockSignals(True)
    try:
        if isinstance(value, int) and not isinstance(value, bool):
            combo.setCurrentIndex(int(value))
            return
        text = str(value)
        idx = combo.findText(text)
        if idx < 0:
            try:
                idx = int(text)
            except ValueError:
                idx = -1
        if idx >= 0:
            combo.setCurrentIndex(idx)
    finally:
        combo.blockSignals(False)
