# -*- coding: utf-8 -*-
"""
IOT 云任务 → 桌面界面交接。

Agent（execution_mode=handoff）把任务写入 iot_job_inbox/pending/，
本模块在主界面定时扫描：应用参数 → 调用过载追加 →（可选）开始试验 →
等试验结束再写回 results/。
"""
from __future__ import annotations

import json
import time
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QRadioButton,
    QSpinBox,
    QTextEdit,
    QWidget,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def stop_request_should_execute(
    *,
    current_job: int,
    stop_job: int,
    running_job: int = 0,
    running: bool = False,
) -> bool:
    """停机单必须就是当前交接任务，或本机确实在跑的那一单。

    云端收口的上一单（例如 58）在下一单还没写入 _awaiting 时 current_job 仍是 0，
    不能因此去点结束试验。
    """
    try:
        stop_job = int(stop_job or 0)
        current_job = int(current_job or 0)
        running_job = int(running_job or 0)
    except (TypeError, ValueError):
        return False
    if stop_job <= 0:
        return False
    if current_job > 0:
        return stop_job == current_job
    if running and running_job > 0:
        return stop_job == running_job
    return False


_SLOT_LABEL_ZH = {
    "ac": "交流电源",
    "dc1": "直流电源1",
    "dc2": "直流电源2",
    "dc3": "直流电源3",
    "dc4": "直流电源4",
    "wt": "功率分析仪",
    "scope": "示波器",
    "dew": "德威创",
}


def _format_auto_connect_summary(summary: Any) -> str:
    if not isinstance(summary, dict):
        return str(summary)
    found = summary.get("found", 0)
    attempted = summary.get("attempted", 0)
    connected = summary.get("connected") or []
    errors = summary.get("errors") or []
    skipped = summary.get("skipped_ambiguous", 0)
    conn_txt = "、".join(str(x) for x in connected) if connected else "无"
    err_txt = "、".join(str(x) for x in errors) if errors else "无"
    return (
        f"发现{found}台，尝试连接{attempted}台，已连接={conn_txt}，"
        f"失败={err_txt}，因歧义跳过{skipped}台"
    )


def collect_widget_values(root_widget) -> Dict[str, Any]:
    """从 Dialog 根控件按 objectName 读出可序列化参数（供 IOT / prefs）。"""
    out: Dict[str, Any] = {}
    if root_widget is None:
        return out
    # 与 apply_widget_values 对称：WT 叠页同名控件只采当前型号页。
    # Dialog 未显示时全部 isVisible()==False，单靠可见性会退化为「遍历顺序第一页」。
    skip_wt_ids: set = set()
    try:
        stacked = getattr(root_widget, "_wtStacked", None)
        if stacked is not None and hasattr(stacked, "currentWidget") and hasattr(stacked, "count"):
            active = stacked.currentWidget()
            for i in range(int(stacked.count())):
                page = stacked.widget(i)
                if page is None or page is active:
                    continue
                skip_wt_ids.add(id(page))
                try:
                    for child in page.findChildren(QWidget):
                        skip_wt_ids.add(id(child))
                except Exception:
                    pass
    except Exception:
        skip_wt_ids = set()
    try:
        widgets = root_widget.findChildren(QWidget) if hasattr(root_widget, "findChildren") else []
    except Exception:
        widgets = []
    # 根自身
    try:
        widgets = [root_widget] + list(widgets or [])
    except Exception:
        pass
    for w in widgets:
        try:
            if id(w) in skip_wt_ids:
                continue
            name = str(w.objectName() or "").strip()
        except Exception:
            continue
        if not name or name.startswith("qt_"):
            continue
        if not name.startswith(
            ("textEdit_", "comboBox_", "checkBox_", "radio_", "radioButton_", "spinBox_", "doubleSpinBox_")
        ):
            continue
        try:
            # 无 _wtStacked 时仍用可见性：后扫到的隐藏同名控件不覆盖已有值
            try:
                visible = bool(w.isVisible())
            except Exception:
                visible = True
            if name in out and not visible:
                continue
            if isinstance(w, (QTextEdit, QPlainTextEdit)):
                out[name] = w.toPlainText()
            elif isinstance(w, QLineEdit):
                out[name] = w.text()
            elif isinstance(w, QCheckBox):
                out[name] = bool(w.isChecked())
            elif isinstance(w, QRadioButton):
                out[name] = bool(w.isChecked())
            elif isinstance(w, QComboBox):
                out[name] = w.currentText()
            elif hasattr(w, "value") and callable(getattr(w, "value")):
                out[name] = w.value()
        except Exception:
            continue
    # 时序 / EN50530 整包
    try:
        table = getattr(root_widget, "timingProfileTable", None) or getattr(
            root_widget, "timing_profile_table", None
        )
        if table is not None and hasattr(table, "to_json"):
            raw = table.to_json()
            if raw:
                out["TIMING_PROFILE_JSON"] = raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False)
        panel = getattr(root_widget, "en50530Panel", None)
        if panel is not None and hasattr(panel, "get_bundle_json"):
            raw = panel.get_bundle_json()
            if raw:
                out["EN50530_BUNDLE_JSON"] = raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False)
    except Exception:
        pass
    return out


def collect_widgets_for_project(project_name: str, handoff_svc=None) -> Dict[str, Any]:
    """按项目名解析 Dialog，采集全部实验类型的实际参数（闪变/谐波/过载/…）。"""
    name = (project_name or "").strip()
    if not name:
        return {}
    try:
        svc = handoff_svc
        if svc is None:
            import SCPITestWave as sw

            svc = getattr(sw, "_iot_ui_handoff_svc", None)
        if svc is None:
            return {}
        handler = svc._resolve_handler(name)
        if not handler:
            return {}
        resolve_ui = handler.get("resolve_ui")
        ui = resolve_ui() if callable(resolve_ui) else None
        if ui is None:
            return {}
        widgets = collect_widget_values(ui)
        return _overlay_live_bluesight_dc(widgets)
    except Exception:
        return {}


def _overlay_live_bluesight_dc(widgets: Dict[str, Any]) -> Dict[str, Any]:
    """当前直流是蓝点 SAS 时，实验直流四点跟曲线走，不用对话框里的旧默认。"""
    try:
        import SCPITestWave as sw
        from utils.bluesight_experiment_iv import overlay_experiment_dc1
        from utils.status_json_devices import bluesight_iv_fields, canonical_reported_brand

        brand = canonical_reported_brand(sw._dc_brand_raw(0))
        if brand != "bluesight":
            return widgets
        page = sw._read_dc1_bluesight_page()
        if not isinstance(page, dict) or str(page.get("mode") or "") != "sas":
            return widgets
        iv = bluesight_iv_fields(page)
        if not str(iv.get("vmp") or "").strip():
            return widgets
        return overlay_experiment_dc1(widgets, iv)
    except Exception:
        return widgets


def persist_current_project_prefs(project_name: str, handoff_svc=None) -> int:
    """追加/开测：把当前 Dialog 参数写入本地并推云端（全实验类型通用）。返回采集字段数。"""
    name = (project_name or "").strip()
    if not name:
        return 0
    try:
        svc = handoff_svc
        if svc is None:
            import SCPITestWave as sw

            svc = getattr(sw, "_iot_ui_handoff_svc", None)
        widgets = collect_widgets_for_project(name, handoff_svc=svc)
        if not widgets:
            return 0
        from utils.iot_bench_prefs import save_test_params

        handler = svc._resolve_handler(name) if svc is not None else None
        tt = str((handler or {}).get("key") or name).strip().lower()
        save_test_params(tt, widgets=widgets)
        return len(widgets)
    except Exception:
        return 0


def apply_widget_values(root_widget, values: Dict[str, Any]) -> list:
    """按 objectName 写控件。返回未找到的键列表。

    功率分析仪为 QStackedWidget 多页同名控件时，优先写当前可见页，
    避免 findChild 总命中第一页（WT3000）导致其它型号配置无效。
    """
    missing = []
    if not values:
        return missing
    try:
        from utils.wt_measure_aliases import expand_wt_measure_checks

        values = expand_wt_measure_checks(values)
    except Exception:
        pass

    active_page = None
    try:
        stacked = getattr(root_widget, "_wtStacked", None)
        if stacked is not None and hasattr(stacked, "currentWidget"):
            active_page = stacked.currentWidget()
    except Exception:
        active_page = None

    def _find(name: str):
        w = None
        if active_page is not None and hasattr(active_page, "findChild"):
            try:
                w = active_page.findChild(QWidget, str(name))
            except Exception:
                w = None
        if w is None and hasattr(root_widget, "findChild"):
            try:
                w = root_widget.findChild(QWidget, str(name))
            except Exception:
                w = None
        if w is None and hasattr(root_widget, str(name)):
            w = getattr(root_widget, str(name), None)
        return w

    # 先切型号 / 分析仪模式，再写其它控件
    priority = (
        "radio_wt",
        "radio_dewetron",
        "radio_S2_WT3000",
        "radio_S2_WT1800",
        "radio_S2_WT1806E",
        "radio_S2_WT5000",
        "radioButton_S2_WT3000",
        "radioButton_S2_WT1800",
        "radioButton_S2_WT1806E",
        "radioButton_S2_WT5000",
    )
    ordered = []
    seen = set()
    for k in priority:
        if k in values:
            ordered.append(k)
            seen.add(k)
    for k in values:
        if k not in seen:
            ordered.append(k)

    for name in ordered:
        val = values.get(name)
        key = str(name)
        if key in ("wt_acquire_mode", "comboBox_wt_acquire_mode"):
            try:
                from utils.wt_acquire_mode import apply_mode_across

                apply_mode_across(root_widget, val)
            except Exception:
                missing.append(key)
            continue
        # 时序表 / EN50530 面板：JSON 整包写入（非普通 QWidget 文本）
        if key in (
            "TIMING_PROFILE_JSON",
            "timing_profile_json",
            "timingProfileTable",
            "EN50530_BUNDLE_JSON",
            "en50530_bundle_json",
        ):
            table = getattr(root_widget, "timingProfileTable", None) or getattr(
                root_widget, "timing_profile_table", None
            )
            panel = getattr(root_widget, "en50530Panel", None) or table
            try:
                if key.startswith("EN50530") or key.startswith("en50530"):
                    target = panel
                    if target is not None and hasattr(target, "set_bundle_json"):
                        if val is not None and str(val).strip():
                            target.set_bundle_json(
                                val if isinstance(val, str) else json.dumps(val, ensure_ascii=False)
                            )
                        continue
                if table is not None and hasattr(table, "from_json"):
                    if val is not None and str(val).strip():
                        table.from_json(val)
                    continue
                if table is not None and hasattr(table, "set_bundle_json"):
                    if val is not None and str(val).strip():
                        table.set_bundle_json(
                            val if isinstance(val, str) else json.dumps(val, ensure_ascii=False)
                        )
                    continue
            except Exception:
                missing.append(key)
                continue
            missing.append(key)
            continue
        if key in ("OVUF_SCAN_LIST_JSON", "ovuf_scan_list_json"):
            try:
                from utils.ovuf_recording import load_ovuf_scan_lists

                if val is not None and str(val).strip() not in ("", "{}"):
                    load_ovuf_scan_lists(root_widget, val)
            except Exception:
                missing.append(key)
            continue
        w = _find(name)
        if w is None:
            missing.append(str(name))
            continue
        try:
            if isinstance(w, (QTextEdit, QPlainTextEdit)):
                w.setPlainText("" if val is None else str(val))
            elif isinstance(w, QLineEdit):
                w.setText("" if val is None else str(val))
            elif isinstance(w, QCheckBox):
                w.setChecked(bool(val) if not isinstance(val, str) else val.strip() in ("1", "true", "True", "yes"))
            elif isinstance(w, QRadioButton):
                checked = bool(val) if not isinstance(val, str) else val.strip() in ("1", "true", "True", "yes")
                w.setChecked(checked)
                if checked:
                    try:
                        # 触发 stacked 切页
                        w.click()
                    except Exception:
                        pass
                    try:
                        stacked = getattr(root_widget, "_wtStacked", None)
                        if stacked is not None and hasattr(stacked, "currentWidget"):
                            active_page = stacked.currentWidget()
                    except Exception:
                        pass
            elif isinstance(w, (QSpinBox, QDoubleSpinBox)):
                try:
                    if val is None or val == "":
                        continue
                    w.setValue(int(float(val)))
                except (TypeError, ValueError):
                    missing.append(str(name))
            elif isinstance(w, QComboBox):
                if isinstance(val, int):
                    w.setCurrentIndex(val)
                else:
                    text = str(val)
                    idx = w.findText(text)
                    # Blockly / 协议常用 Three|Single；桌面 Dialog 选项是 三相|单相
                    if idx < 0 and key in ("comboBox_S1_AC_2", "comboBox_Phase"):
                        try:
                            from utils.iot_boot_params_sync import phase_combo_aliases

                            for cand in phase_combo_aliases(text):
                                idx = w.findText(str(cand))
                                if idx >= 0:
                                    break
                        except Exception:
                            pass
                    # IOT 常下发 min|sec|ms；Dialog 选项是 分钟|秒|毫秒（job110 因此回读失败）
                    if idx < 0 and (
                        key.endswith("_TIME")
                        or key
                        in (
                            "comboBox_ovuf_grid_wait",
                            "comboBox_lvrt_grid_wait",
                        )
                        or "TIME" in key
                    ):
                        try:
                            from utils.iot_ovuf_apply import time_unit_aliases

                            for cand in time_unit_aliases(text):
                                idx = w.findText(str(cand))
                                if idx >= 0:
                                    break
                        except Exception:
                            pass
                    # Web/Blockly 写 ON|OFF|true；Dialog 选项是 开启|关闭
                    if idx < 0 and (
                        key.startswith("comboBox_S1_AC")
                        and not key.endswith("_2")
                        or key.startswith("comboBox_S1_DC")
                        or key.startswith("comboBox_S_End")
                    ):
                        try:
                            from utils.iot_boot_params_sync import output_combo_aliases

                            for cand in output_combo_aliases(text):
                                idx = w.findText(str(cand))
                                if idx >= 0:
                                    break
                        except Exception:
                            pass
                    if idx >= 0:
                        w.setCurrentIndex(idx)
                    else:
                        try:
                            w.setCurrentIndex(int(val))
                        except (TypeError, ValueError):
                            missing.append(str(name))
            else:
                if hasattr(w, "setPlainText"):
                    w.setPlainText(str(val))
                elif hasattr(w, "setText"):
                    w.setText(str(val))
                elif hasattr(w, "setChecked"):
                    w.setChecked(bool(val))
                elif hasattr(w, "setCurrentIndex"):
                    w.setCurrentIndex(int(val))
                else:
                    missing.append(str(name))
        except Exception:
            missing.append(str(name))
    return missing


def _append_with_message_capture(project_append: Callable[[], None]) -> Tuple[Optional[str], Optional[BaseException]]:
    """Call append; capture QMessageBox.information as append failure.

    试验 Send 失败一律 ``information(..., \"错误提示信息\", ...)``。
    旧逻辑只认「厂家/赋值/IVC」等关键词，漏掉「请至少勾选一个极限 cosφ」等文案，
    会把失败追加当成成功再点开始，桌面就弹出「还没有可执行的试验命令」。
    """
    captured: List[str] = []
    orig = QMessageBox.information

    def _info(parent, title, text, *args, **kwargs):
        try:
            title_s = str(title or "").strip()
            text_s = str(text or "").strip()
            if title_s and text_s:
                captured.append(f"{title_s}: {text_s}")
            else:
                captured.append(text_s or title_s)
        except Exception:
            pass
        try:
            # 云任务交接时不弹窗，避免挡住自动流程；文案已捕获写入失败原因
            return QMessageBox.Ok
        except Exception:
            return QMessageBox.Ok

    QMessageBox.information = staticmethod(_info)  # type: ignore[method-assign]
    err: Optional[BaseException] = None
    try:
        project_append()
    except BaseException as exc:  # noqa: BLE001 — surface to caller as fail_reason
        err = exc
    finally:
        QMessageBox.information = orig  # type: ignore[method-assign]
    fail_reason = None
    for msg in captured:
        text = (msg or "").strip()
        if not text:
            continue
        # 追加成功路径只写操作日志，不走 information；凡弹 information 即失败
        fail_reason = text
        break
    return fail_reason, err


class IotUiHandoffService(QObject):
    """挂在主窗口上的定时扫描服务。"""

    # testType 别名 → (项目中文名, handler_key)
    _TYPE_MAP = {
        "overload": ("过载能力测试", "overload"),
        "overloads": ("过载能力测试", "overload"),
        "过载能力测试": ("过载能力测试", "overload"),
        "antibackflow": ("防逆流测试", "antibackflow"),
        "anti_backflow": ("防逆流测试", "antibackflow"),
        "防逆流测试": ("防逆流测试", "antibackflow"),
        "防逆流": ("防逆流测试", "antibackflow"),
        "flicker": ("电压闪变", "flicker"),
        "voltage_flicker": ("电压闪变", "flicker"),
        "电压闪变": ("电压闪变", "flicker"),
        "闪变": ("电压闪变", "flicker"),
        "harmonic": ("谐波电流", "harmonic"),
        "harmonics": ("谐波电流", "harmonic"),
        "harmonic_current": ("谐波电流", "harmonic"),
        "谐波电流": ("谐波电流", "harmonic"),
        "谐波": ("谐波电流", "harmonic"),
        "谐波电流测试": ("谐波电流", "harmonic"),
        "fixedpf": ("固定PF=1", "fixedpf"),
        "fixed_pf": ("固定PF=1", "fixedpf"),
        "fixedpf1": ("固定PF=1", "fixedpf"),
        "固定PF=1": ("固定PF=1", "fixedpf"),
        "固定PF": ("固定PF=1", "fixedpf"),
        "固定pf=1": ("固定PF=1", "fixedpf"),
        "固定pf": ("固定PF=1", "fixedpf"),
        "dccomponent": ("直流分量", "dccomponent"),
        "dc_component": ("直流分量", "dccomponent"),
        "zhiliufenliang": ("直流分量", "dccomponent"),
        "直流分量": ("直流分量", "dccomponent"),
        "直流分量测试": ("直流分量", "dccomponent"),
        "reconnect": ("重连", "reconnect"),
        "chonglian": ("重连", "reconnect"),
        "reconn": ("重连", "reconnect"),
        "重连": ("重连", "reconnect"),
        "重联": ("重连", "reconnect"),
        "重连测试": ("重连", "reconnect"),
        "ovuf": ("过欠压_过欠频", "ovuf"),
        "guoqianya_pin": ("过欠压_过欠频", "ovuf"),
        "volt_freq": ("过欠压_过欠频", "ovuf"),
        "过欠压_过欠频": ("过欠压_过欠频", "ovuf"),
        "过欠压过欠频": ("过欠压_过欠频", "ovuf"),
        "guopinjiangzai": ("过频降载", "guopinjiangzai"),
        "guopin": ("过频降载", "guopinjiangzai"),
        "of_reduce": ("过频降载", "guopinjiangzai"),
        "过频降载": ("过频降载", "guopinjiangzai"),
        "qianpinshengzai": ("欠频升载", "qianpinshengzai"),
        "qianpin": ("欠频升载", "qianpinshengzai"),
        "uf_raise": ("欠频升载", "qianpinshengzai"),
        "欠频升载": ("欠频升载", "qianpinshengzai"),
        "voltprotect10min": ("10min过压保护", "voltprotect10min"),
        "voltprotect": ("10min过压保护", "voltprotect10min"),
        "10min过压保护": ("10min过压保护", "voltprotect10min"),
        "过压保护10min": ("10min过压保护", "voltprotect10min"),
        "guoqianpin_immun": ("巴西过欠频稳定性", "guoqianpin_immun"),
        "guoqianpinimmun": ("巴西过欠频稳定性", "guoqianpin_immun"),
        "brazil_ovuf": ("巴西过欠频稳定性", "guoqianpin_immun"),
        "巴西过欠频稳定性": ("巴西过欠频稳定性", "guoqianpin_immun"),
        "过欠频稳定性": ("巴西过欠频稳定性", "guoqianpin_immun"),
        "staticmppt": ("静态MPPT测试", "staticmppt"),
        "staticmppttest": ("静态MPPT测试", "staticmppt"),
        "static_mppt": ("静态MPPT测试", "staticmppt"),
        "静态MPPT测试": ("静态MPPT测试", "staticmppt"),
        "静态MPPT": ("静态MPPT测试", "staticmppt"),
        "静态mppt测试": ("静态MPPT测试", "staticmppt"),
        "静态mppt": ("静态MPPT测试", "staticmppt"),
        "frequencyadaptability": ("频率适应性", "frequencyadaptability"),
        "freqadapt": ("频率适应性", "frequencyadaptability"),
        "频率适应性": ("频率适应性", "frequencyadaptability"),
        "voltageadaptability": ("电压适应性", "voltageadaptability"),
        "voltadapt": ("电压适应性", "voltageadaptability"),
        "voltage_adaptability": ("电压适应性", "voltageadaptability"),
        "电压适应性": ("电压适应性", "voltageadaptability"),
        "rocof": ("ROCOF保护", "rocof"),
        "rocofprotect": ("ROCOF保护", "rocof"),
        "rocof_protect": ("ROCOF保护", "rocof"),
        "ROCOF保护": ("ROCOF保护", "rocof"),
        "rocof保护": ("ROCOF保护", "rocof"),
        "rapidvolt": ("快速电压变化", "rapidvolt"),
        "rapid_volt": ("快速电压变化", "rapidvolt"),
        "rvc": ("快速电压变化", "rapidvolt"),
        "快速电压变化": ("快速电压变化", "rapidvolt"),
        "lvrt": ("低电压穿越", "lvrt"),
        "lowvoltage_ride_through": ("低电压穿越", "lvrt"),
        "低电压穿越": ("低电压穿越", "lvrt"),
        "phasejump": ("相角突变", "phasejump"),
        "phase_jump": ("相角突变", "phasejump"),
        "相角突变": ("相角突变", "phasejump"),
        "dynamicmppt": ("动态MPPT", "dynamicmppt"),
        "dynamic_mppt": ("动态MPPT", "dynamicmppt"),
        "动态MPPT": ("动态MPPT", "dynamicmppt"),
        "动态mppt": ("动态MPPT", "dynamicmppt"),
        "reactiveqcap": ("无功能力范围", "reactiveqcap"),
        "reactiveQcap": ("无功能力范围", "reactiveqcap"),
        "reactiveqcap": ("无功能力范围", "reactiveqcap"),
        "reactive_qcap": ("无功能力范围", "reactiveqcap"),
        "无功能力范围": ("无功能力范围", "reactiveqcap"),
        "无功控制范围": ("无功能力范围", "reactiveqcap"),
        "fixedq": ("定无功", "fixedq"),
        "fixedQ": ("定无功", "fixedq"),
        "fixedq": ("定无功", "fixedq"),
        "fixed_q": ("定无功", "fixedq"),
        "定无功": ("定无功", "fixedq"),
        "固无功": ("定无功", "fixedq"),
        "reactiveqin": ("无功注入", "reactiveqin"),
        "reactiveQin": ("无功注入", "reactiveqin"),
        "reactiveqin": ("无功注入", "reactiveqin"),
        "reactive_qin": ("无功注入", "reactiveqin"),
        "无功注入": ("无功注入", "reactiveqin"),
        "reactiveqacc": ("无功精度", "reactiveqacc"),
        "reactiveQacc": ("无功精度", "reactiveqacc"),
        "reactiveqacc": ("无功精度", "reactiveqacc"),
        "reactive_qacc": ("无功精度", "reactiveqacc"),
        "无功精度": ("无功精度", "reactiveqacc"),
        "activep": ("有功调度", "activep"),
        "activeP": ("有功调度", "activep"),
        "activep": ("有功调度", "activep"),
        "active_p": ("有功调度", "activep"),
        "有功调度": ("有功调度", "activep"),
        "有功控制": ("有功调度", "activep"),
        "staticqu": ("静态QU", "staticqu"),
        "staticQU": ("静态QU", "staticqu"),
        "staticqu": ("静态QU", "staticqu"),
        "static_qu": ("静态QU", "staticqu"),
        "静态QU": ("静态QU", "staticqu"),
        "静态qu": ("静态QU", "staticqu"),
        "静态qu": ("静态QU", "staticqu"),
        "dynamicqu": ("动态QU", "dynamicqu"),
        "dynamicQU": ("动态QU", "dynamicqu"),
        "dynamicqu": ("动态QU", "dynamicqu"),
        "dynamic_qu": ("动态QU", "dynamicqu"),
        "动态QU": ("动态QU", "dynamicqu"),
        "动态qu": ("动态QU", "dynamicqu"),
        "动态qu": ("动态QU", "dynamicqu"),
        "testpu": ("Test_PU", "testpu"),
        "testPU": ("Test_PU", "testpu"),
        "testpu": ("Test_PU", "testpu"),
        "test_pu": ("Test_PU", "testpu"),
        "Test_PU": ("Test_PU", "testpu"),
        "test_pu": ("Test_PU", "testpu"),
        "test_PU": ("Test_PU", "testpu"),
        "test_pu": ("Test_PU", "testpu"),
        "staticcosphi": ("静态Cos(φ)", "staticcosphi"),
        "staticcosPhi": ("静态Cos(φ)", "staticcosphi"),
        "staticcosphi": ("静态Cos(φ)", "staticcosphi"),
        "static_cosphi": ("静态Cos(φ)", "staticcosphi"),
        "静态Cos(φ)": ("静态Cos(φ)", "staticcosphi"),
        "静态cos(φ)": ("静态Cos(φ)", "staticcosphi"),
        "静态cos(φ)": ("静态Cos(φ)", "staticcosphi"),
        "静态CosPhi": ("静态Cos(φ)", "staticcosphi"),
        "静态cosphi": ("静态Cos(φ)", "staticcosphi"),
        "dynamiccosphi": ("动态Cos(φ)", "dynamiccosphi"),
        "dynamiccosPhi": ("动态Cos(φ)", "dynamiccosphi"),
        "dynamiccosphi": ("动态Cos(φ)", "dynamiccosphi"),
        "dynamic_cosphi": ("动态Cos(φ)", "dynamiccosphi"),
        "动态Cos(φ)": ("动态Cos(φ)", "dynamiccosphi"),
        "动态cos(φ)": ("动态Cos(φ)", "dynamiccosphi"),
        "动态cos(φ)": ("动态Cos(φ)", "dynamiccosphi"),
        "动态CosPhi": ("动态Cos(φ)", "dynamiccosphi"),
        "动态cosphi": ("动态Cos(φ)", "dynamiccosphi"),
        "cosphibrazil": ("Cos(φ)_Brazil", "cosphibrazil"),
        "cosPhiBrazil": ("Cos(φ)_Brazil", "cosphibrazil"),
        "cosphibrazil": ("Cos(φ)_Brazil", "cosphibrazil"),
        "cos_phi_brazil": ("Cos(φ)_Brazil", "cosphibrazil"),
        "Cos(φ)_Brazil": ("Cos(φ)_Brazil", "cosphibrazil"),
        "cos(φ)_brazil": ("Cos(φ)_Brazil", "cosphibrazil"),
        "cos(φ)_brazil": ("Cos(φ)_Brazil", "cosphibrazil"),
        "巴西CosPhi": ("Cos(φ)_Brazil", "cosphibrazil"),
        "巴西cosphi": ("Cos(φ)_Brazil", "cosphibrazil"),
    }

    # (summary_or_none, error_or_none) — 探测在后台线程，回主线程继续交接
    _auto_connect_finished = pyqtSignal(object, object)
    _desktop_run_finished = pyqtSignal()

    def __init__(
        self,
        *,
        repo_root: Optional[Path] = None,
        resolve_overload_ui: Optional[Callable[[], Any]] = None,
        overload_append: Optional[Callable[[], None]] = None,
        resolve_antibackflow_ui: Optional[Callable[[], Any]] = None,
        antibackflow_append: Optional[Callable[[], None]] = None,
        resolve_flicker_ui: Optional[Callable[[], Any]] = None,
        flicker_append: Optional[Callable[[], None]] = None,
        resolve_harmonic_ui: Optional[Callable[[], Any]] = None,
        harmonic_append: Optional[Callable[[], None]] = None,
        resolve_fixedpf_ui: Optional[Callable[[], Any]] = None,
        fixedpf_append: Optional[Callable[[], None]] = None,
        resolve_dccomponent_ui: Optional[Callable[[], Any]] = None,
        dccomponent_append: Optional[Callable[[], None]] = None,
        resolve_reconnect_ui: Optional[Callable[[], Any]] = None,
        reconnect_append: Optional[Callable[[], None]] = None,
        resolve_ovuf_ui: Optional[Callable[[], Any]] = None,
        ovuf_append: Optional[Callable[[], None]] = None,
        resolve_guopinjiangzai_ui: Optional[Callable[[], Any]] = None,
        guopinjiangzai_append: Optional[Callable[[], None]] = None,
        resolve_qianpinshengzai_ui: Optional[Callable[[], Any]] = None,
        qianpinshengzai_append: Optional[Callable[[], None]] = None,
        resolve_voltprotect10min_ui: Optional[Callable[[], Any]] = None,
        voltprotect10min_append: Optional[Callable[[], None]] = None,
        resolve_guoqianpin_immun_ui: Optional[Callable[[], Any]] = None,
        guoqianpin_immun_append: Optional[Callable[[], None]] = None,
        resolve_staticmppt_ui: Optional[Callable[[], Any]] = None,
        staticmppt_append: Optional[Callable[[], None]] = None,
        resolve_frequencyadaptability_ui: Optional[Callable[[], Any]] = None,
        frequencyadaptability_append: Optional[Callable[[], None]] = None,
        resolve_voltageadaptability_ui: Optional[Callable[[], Any]] = None,
        voltageadaptability_append: Optional[Callable[[], None]] = None,
        resolve_rocof_ui: Optional[Callable[[], Any]] = None,
        rocof_append: Optional[Callable[[], None]] = None,
        resolve_rapidvolt_ui: Optional[Callable[[], Any]] = None,
        rapidvolt_append: Optional[Callable[[], None]] = None,
        resolve_lvrt_ui: Optional[Callable[[], Any]] = None,
        lvrt_append: Optional[Callable[[], None]] = None,
        resolve_phasejump_ui: Optional[Callable[[], Any]] = None,
        phasejump_append: Optional[Callable[[], None]] = None,
        resolve_dynamicmppt_ui: Optional[Callable[[], Any]] = None,
        dynamicmppt_append: Optional[Callable[[], None]] = None,
        resolve_reactiveqcap_ui: Optional[Callable[[], Any]] = None,
        reactiveqcap_append: Optional[Callable[[], None]] = None,
        resolve_fixedq_ui: Optional[Callable[[], Any]] = None,
        fixedq_append: Optional[Callable[[], None]] = None,
        resolve_reactiveqin_ui: Optional[Callable[[], Any]] = None,
        reactiveqin_append: Optional[Callable[[], None]] = None,
        resolve_reactiveqacc_ui: Optional[Callable[[], Any]] = None,
        reactiveqacc_append: Optional[Callable[[], None]] = None,
        resolve_activep_ui: Optional[Callable[[], Any]] = None,
        activep_append: Optional[Callable[[], None]] = None,
        resolve_staticqu_ui: Optional[Callable[[], Any]] = None,
        staticqu_append: Optional[Callable[[], None]] = None,
        resolve_dynamicqu_ui: Optional[Callable[[], Any]] = None,
        dynamicqu_append: Optional[Callable[[], None]] = None,
        resolve_testpu_ui: Optional[Callable[[], Any]] = None,
        testpu_append: Optional[Callable[[], None]] = None,
        resolve_staticcosphi_ui: Optional[Callable[[], Any]] = None,
        staticcosphi_append: Optional[Callable[[], None]] = None,
        resolve_dynamiccosphi_ui: Optional[Callable[[], Any]] = None,
        dynamiccosphi_append: Optional[Callable[[], None]] = None,
        resolve_cosphibrazil_ui: Optional[Callable[[], Any]] = None,
        cosphibrazil_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
        get_run_status: Optional[Callable[[], str]] = None,
        get_run_progress: Optional[Callable[[], Dict[str, Any]]] = None,
        ensure_project: Optional[Callable[[str], None]] = None,
        auto_connect: Optional[Callable[[], Any]] = None,
        prepare_auto_connect: Optional[Callable[[], Any]] = None,
        apply_auto_connect: Optional[Callable[[Any], Any]] = None,
        ensure_ready: Optional[Callable[[Any, str], tuple]] = None,
        session_ok: Optional[Callable[[str], bool]] = None,
        stop_test: Optional[Callable[[], None]] = None,
        reset_append_count: Optional[Callable[[], None]] = None,
        wrap_append_errors: bool = True,
        log: Optional[Callable[[str], None]] = None,
        interval_ms: int = 3000,
        parent=None,
    ):
        super().__init__(parent)
        self.repo_root = Path(repo_root) if repo_root else _repo_root()
        self.resolve_overload_ui = resolve_overload_ui
        self.overload_append = overload_append
        self.resolve_antibackflow_ui = resolve_antibackflow_ui
        self.antibackflow_append = antibackflow_append
        self.resolve_flicker_ui = resolve_flicker_ui
        self.flicker_append = flicker_append
        self.resolve_harmonic_ui = resolve_harmonic_ui
        self.harmonic_append = harmonic_append
        self.resolve_fixedpf_ui = resolve_fixedpf_ui
        self.fixedpf_append = fixedpf_append
        self.resolve_dccomponent_ui = resolve_dccomponent_ui
        self.dccomponent_append = dccomponent_append
        self.resolve_reconnect_ui = resolve_reconnect_ui
        self.reconnect_append = reconnect_append
        self.resolve_ovuf_ui = resolve_ovuf_ui
        self.ovuf_append = ovuf_append
        self.resolve_guopinjiangzai_ui = resolve_guopinjiangzai_ui
        self.guopinjiangzai_append = guopinjiangzai_append
        self.resolve_qianpinshengzai_ui = resolve_qianpinshengzai_ui
        self.qianpinshengzai_append = qianpinshengzai_append
        self.resolve_voltprotect10min_ui = resolve_voltprotect10min_ui
        self.voltprotect10min_append = voltprotect10min_append
        self.resolve_guoqianpin_immun_ui = resolve_guoqianpin_immun_ui
        self.guoqianpin_immun_append = guoqianpin_immun_append
        self.resolve_staticmppt_ui = resolve_staticmppt_ui
        self.staticmppt_append = staticmppt_append
        self.resolve_frequencyadaptability_ui = resolve_frequencyadaptability_ui
        self.frequencyadaptability_append = frequencyadaptability_append
        self.resolve_voltageadaptability_ui = resolve_voltageadaptability_ui
        self.voltageadaptability_append = voltageadaptability_append
        self.resolve_rocof_ui = resolve_rocof_ui
        self.rocof_append = rocof_append
        self.resolve_rapidvolt_ui = resolve_rapidvolt_ui
        self.rapidvolt_append = rapidvolt_append
        self.resolve_lvrt_ui = resolve_lvrt_ui
        self.lvrt_append = lvrt_append
        self.resolve_phasejump_ui = resolve_phasejump_ui
        self.phasejump_append = phasejump_append
        self.resolve_dynamicmppt_ui = resolve_dynamicmppt_ui
        self.dynamicmppt_append = dynamicmppt_append
        self.resolve_reactiveqcap_ui = resolve_reactiveqcap_ui
        self.reactiveqcap_append = reactiveqcap_append
        self.resolve_fixedq_ui = resolve_fixedq_ui
        self.fixedq_append = fixedq_append
        self.resolve_reactiveqin_ui = resolve_reactiveqin_ui
        self.reactiveqin_append = reactiveqin_append
        self.resolve_reactiveqacc_ui = resolve_reactiveqacc_ui
        self.reactiveqacc_append = reactiveqacc_append
        self.resolve_activep_ui = resolve_activep_ui
        self.activep_append = activep_append
        self.resolve_staticqu_ui = resolve_staticqu_ui
        self.staticqu_append = staticqu_append
        self.resolve_dynamicqu_ui = resolve_dynamicqu_ui
        self.dynamicqu_append = dynamicqu_append
        self.resolve_testpu_ui = resolve_testpu_ui
        self.testpu_append = testpu_append
        self.resolve_staticcosphi_ui = resolve_staticcosphi_ui
        self.staticcosphi_append = staticcosphi_append
        self.resolve_dynamiccosphi_ui = resolve_dynamiccosphi_ui
        self.dynamiccosphi_append = dynamiccosphi_append
        self.resolve_cosphibrazil_ui = resolve_cosphibrazil_ui
        self.cosphibrazil_append = cosphibrazil_append
        self.start_test = start_test
        self.get_run_status = get_run_status
        self.get_run_progress = get_run_progress
        self.ensure_project = ensure_project
        self.auto_connect = auto_connect
        self.prepare_auto_connect = prepare_auto_connect
        self.apply_auto_connect = apply_auto_connect
        self.ensure_ready = ensure_ready
        self.session_ok = session_ok
        self.stop_test = stop_test
        self.reset_append_count = reset_append_count
        self.wrap_append_errors = bool(wrap_append_errors)
        self._log = log or (lambda m: print(f"[IOT交接] {m}", flush=True))
        self._busy = False
        self._awaiting: Optional[Dict[str, Any]] = None
        self._timer = QTimer(self)
        self._timer.setInterval(max(1000, int(interval_ms)))
        self._timer.timeout.connect(self.poll_once)
        self._device_cmd_busy = False
        self._last_progress_key = None
        self._stop_inflight = False
        self._job_ctx: Optional[Dict[str, Any]] = None
        self._auto_connect_finished.connect(self._on_auto_connect_finished)
        self._desktop_run_finished.connect(self._check_awaiting_finish)
        # 云端仪器控制（连接/输出/德威创构造）回调，由 SCPITestWave 启动后挂载
        self.device_apply_connect = None
        self.device_apply_disconnect = None
        self.device_output_on = None
        self.device_output_off = None
        self.device_dew_build = None
        self.device_switch_flicker = None
        # 已连接时在线下发 AC/DC 参数（不必断开重连）
        self.device_apply_setpoints = None
        # IOT「扫描网口上报」：局域网探测后写入 scanned_resources，供心跳上报
        self.device_discover_lan = None
        # 交接写完 Dialog 后：把 S1 AC/DC 同步到 Soft Panel 并尽量下发真机
        self.device_sync_boot_params = None
        # 德威创开测：把开测页比例系数/刷新率等写到桌面设置页
        self.device_apply_dew_widgets = None

    def start(self) -> None:
        watched = " ; ".join(str(d / "pending") for d in self._inbox_dirs())
        self._log(f"已启动，监视 {watched}")
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def _inbox_dirs(self) -> list:
        """安装根 iot_job_inbox 优先；兼容旧 Agent 误写到 agent/iot_job_inbox。"""
        primary = self.repo_root / "iot_job_inbox"
        legacy = self.repo_root / "agent" / "iot_job_inbox"
        out = [primary]
        if legacy.resolve() != primary.resolve():
            out.append(legacy)
        return out

    def _write_roots_for(self, pending_path: Optional[Path]) -> list:
        """结案/进度写入安装根；若 pending 来自旧 agent/ 目录则双写，让旧 Agent wait_result 能收到。"""
        roots = [self.repo_root]
        if pending_path is not None:
            try:
                parts = set(Path(pending_path).resolve().parts)
            except OSError:
                parts = set(Path(pending_path).parts)
            if "agent" in parts and "iot_job_inbox" in parts:
                legacy_root = self.repo_root / "agent"
                if legacy_root.resolve() != self.repo_root.resolve():
                    roots.append(legacy_root)
        return roots

    def _write_result_all(self, pending_path: Optional[Path], job_id: int, result: Dict[str, Any]) -> None:
        from agent.job_inbox import write_result

        for root in self._write_roots_for(pending_path):
            write_result(root, job_id, result)

    def notify_desktop_run_finished(self) -> None:
        """桌面试验线程已写终态。立刻查一次，不必等下一拍定时器。"""
        aw = self._awaiting
        if isinstance(aw, dict):
            aw["desktop_finished"] = True
        try:
            self._desktop_run_finished.emit()
        except Exception as exc:
            self._log(f"终态通知失败: {exc}")

    def poll_once(self) -> None:
        # 仪器控制（连接/输出/德威创构造）优先于试验任务，与自动化同路径
        try:
            self._drain_device_cmds()
        except Exception as exc:
            self._log(f"仪器控制轮询异常: {exc}")
        if self._awaiting:
            self._check_awaiting_finish()
            self._drain_stop_requests()
            return
        if self._busy:
            return
        self._drain_stop_requests()
        for inbox in self._inbox_dirs():
            pending_dir = inbox / "pending"
            if not pending_dir.is_dir():
                continue
            files = sorted(pending_dir.glob("job_*.json"))
            if not files:
                continue
            for path in files:
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except Exception as exc:
                    self._log(f"读取失败 {path.name}: {exc}")
                    continue
                job = payload.get("job") or payload
                job_id = int(job.get("id") or 0)
                if job_id <= 0:
                    continue
                already = False
                for root in self._write_roots_for(path):
                    if (root / "iot_job_inbox" / "results" / f"job_{job_id}.json").is_file():
                        already = True
                        break
                if already:
                    continue
                self._busy = True
                try:
                    self._handle_job(job, path)
                finally:
                    # 后台探测中 (_job_ctx) 或等待试验结束 (_awaiting) 时保持 busy
                    if not self._awaiting and self._job_ctx is None:
                        self._busy = False
                return

    def _drain_device_cmds(self) -> None:
        """执行 Agent 下发的逐台连接 / 开关输出 / 德威创构造。

        必须停掉本定时器再连设备：连接内部会 processEvents / 嵌套事件循环，
        否则定时器重入会再连一次，并弹出模态框把主界面卡住。
        """
        if self._device_cmd_busy:
            return
        from utils.iot_device_cmd_inbox import (
            execute_device_cmd,
            list_pending,
            write_result,
        )
        from utils.iot_remote_ui import silent_remote_connect

        paths = list_pending(self.repo_root)
        if not paths:
            return
        path = paths[0]
        self._device_cmd_busy = True
        was_active = self._timer.isActive()
        self._timer.stop()
        request_id = ""
        try:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                self._log(f"仪器控制读取失败 {path.name}: {exc}")
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    pass
                return
            if not isinstance(payload, dict):
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    pass
                return
            request_id = str(payload.get("requestId") or "").strip() or path.stem.replace("cmd_", "", 1)
            done = self.repo_root / "iot_job_inbox" / "device_cmds" / "results" / f"cmd_{request_id}.json"
            if done.is_file():
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    pass
                return
            # 先挪走 pending，避免连接过程中重入又执行同一条
            running = path.parent.parent / "running"
            running.mkdir(parents=True, exist_ok=True)
            claimed = running / path.name
            try:
                path.replace(claimed)
            except Exception:
                claimed = path
            with silent_remote_connect():
                result = execute_device_cmd(
                    payload,
                    apply_connect=self.device_apply_connect,
                    apply_disconnect=self.device_apply_disconnect,
                    output_on=self.device_output_on,
                    output_off=self.device_output_off,
                    dew_build=self.device_dew_build,
                    switch_flicker=self.device_switch_flicker,
                    apply_setpoints=self.device_apply_setpoints,
                    discover_lan=self.device_discover_lan,
                    log=self._log,
                )
            try:
                write_result(self.repo_root, request_id, result)
            except Exception as exc:
                self._log(f"仪器控制写结果失败: {exc}")
            try:
                claimed.unlink(missing_ok=True)
            except Exception:
                pass
        finally:
            self._device_cmd_busy = False
            if was_active:
                self._timer.start()

    def _current_handoff_job_id(self) -> int:
        """正在交接或等待结束的云端任务。过期 stop_request 不能拿来停这一单。"""
        for src in (self._awaiting, getattr(self, "_job_ctx", None)):
            if not isinstance(src, dict):
                continue
            try:
                job_id = int(src.get("job_id") or 0)
            except (TypeError, ValueError):
                job_id = 0
            if job_id > 0:
                return job_id
        return 0

    def _drain_stop_requests(self) -> None:
        """扫描 stop_requests：调用结束试验/关电源后 ack。"""
        if self._stop_inflight:
            return
        from agent.job_inbox import ack_stop_request, list_stop_requests

        reqs = list_stop_requests(self.repo_root)
        # 兼容旧 Agent 误写到 agent/iot_job_inbox
        legacy = self.repo_root / "agent"
        if legacy.resolve() != self.repo_root.resolve():
            for extra in list_stop_requests(legacy):
                reqs.append(extra)
        if not reqs:
            return
        current_job = self._current_handoff_job_id()
        running = False
        running_job = 0
        try:
            from utils.iot_local_run import bench_is_running

            running = bench_is_running(self._read_run_status())
            running_job = self._status_file_job_id()
        except Exception:
            running = False
            running_job = 0
        self._stop_inflight = True
        try:
            for req in reqs:
                job_id = int(req.get("job_id") or 0)
                if job_id <= 0:
                    continue
                # 云端收口的是上一单（例如 58 已被心跳标已中止）。
                # 下一单尚未写入 _awaiting 时 current_job 为 0，也不能拿来停 59/60。
                # 但若停机单就是本机正在交接/正在跑的任务，绝不能当「上一单」忽略
                # （开跑时误把本单写入 superseded 会导致 IOT 中止 106 无效）。
                is_current = stop_request_should_execute(
                    current_job=current_job,
                    stop_job=job_id,
                    running_job=running_job,
                    running=running,
                )
                try:
                    from agent.job_inbox import forget_superseded_job, is_superseded_job

                    if is_superseded_job(self.repo_root, job_id):
                        if is_current:
                            forget_superseded_job(self.repo_root, job_id)
                            self._log(
                                f"停机 job={job_id} 曾误标为上一单，仍是当前任务，继续停机"
                            )
                        else:
                            self._log(f"忽略上一单停机 job={job_id}（本机已新开试验）")
                            ack_stop_request(self.repo_root, job_id)
                            if legacy.resolve() != self.repo_root.resolve():
                                ack_stop_request(legacy, job_id)
                            continue
                except Exception:
                    pass
                if not is_current:
                    self._log(
                        f"忽略过期停机 job={job_id}（当前任务 {current_job or running_job or 0}）"
                    )
                    ack_stop_request(self.repo_root, job_id)
                    if legacy.resolve() != self.repo_root.resolve():
                        ack_stop_request(legacy, job_id)
                    continue
                if callable(self.stop_test):
                    try:
                        self.stop_test()
                        self._log("收到远程停机，已执行结束试验/关电源")
                    except Exception as exc:
                        self._log(f"远程停机执行失败: {exc}")
                else:
                    self._log("收到远程停机，但未绑定 stop_test 回调")
                ack_stop_request(self.repo_root, job_id)
                if legacy.resolve() != self.repo_root.resolve():
                    ack_stop_request(legacy, job_id)
        finally:
            self._stop_inflight = False

    def _status_file_job_id(self) -> int:
        path = self.repo_root / "status.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return 0
        proj = data.get("project") if isinstance(data, dict) else None
        if not isinstance(proj, dict):
            return 0
        try:
            return int(proj.get("jobId") or proj.get("job_id") or 0)
        except (TypeError, ValueError):
            return 0

    def _discard_unrelated_stops(self, keep_job_id: int) -> None:
        """开跑新任务前清掉上一单的 stop_request，避免嵌套事件里误点结束试验。"""
        from agent.job_inbox import ack_stop_request, list_stop_requests

        keep = int(keep_job_id or 0)
        for req in list_stop_requests(self.repo_root):
            try:
                jid = int(req.get("job_id") or 0)
            except (TypeError, ValueError):
                jid = 0
            if jid <= 0 or jid == keep:
                continue
            ack_stop_request(self.repo_root, jid)
            self._log(f"忽略过期停机 job={jid}（开始任务 {keep}）")

    def _read_run_status(self) -> str:
        if not self.get_run_status:
            return ""
        try:
            return str(self.get_run_status() or "").strip()
        except Exception as exc:
            self._log(f"读取试验状态失败: {exc}")
            return ""

    def _emit_progress(self, job_id: int, *, force: bool = False) -> None:
        from agent.job_inbox import write_progress

        percent = 15
        text = "试验进行中"
        step = "running"
        if self.get_run_progress:
            try:
                snap = self.get_run_progress() or {}
                if isinstance(snap, dict):
                    if snap.get("percent") is not None:
                        percent = int(snap.get("percent") or 0)
                    if snap.get("text"):
                        text = str(snap.get("text"))
                    if snap.get("step"):
                        step = str(snap.get("step"))
            except Exception as exc:
                self._log(f"读取进度失败: {exc}")
        key = (percent, text, step)
        if not force and key == self._last_progress_key:
            return
        self._last_progress_key = key
        pending = None
        if self._awaiting:
            pending = self._awaiting.get("pending_path")
        try:
            for root in self._write_roots_for(pending):
                write_progress(root, job_id, percent=percent, text=text, step=step)
        except Exception as exc:
            self._log(f"写进度失败: {exc}")

    def _resolve_handler(self, test_type: str):
        raw = str(test_type or "").strip()
        key = raw.lower() if raw.isascii() else raw
        mapped = self._TYPE_MAP.get(key) or self._TYPE_MAP.get(raw)
        if not mapped:
            return None
        project_name, handler_key = mapped
        if handler_key == "overload":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_overload_ui,
                "append": self.overload_append,
                "label": "过载",
            }
        if handler_key == "antibackflow":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_antibackflow_ui,
                "append": self.antibackflow_append,
                "label": "防逆流",
            }
        if handler_key == "flicker":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_flicker_ui,
                "append": self.flicker_append,
                "label": "电压闪变",
            }
        if handler_key == "harmonic":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_harmonic_ui,
                "append": self.harmonic_append,
                "label": "谐波电流",
            }
        if handler_key == "fixedpf":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_fixedpf_ui,
                "append": self.fixedpf_append,
                "label": "固定PF=1",
            }
        if handler_key == "dccomponent":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_dccomponent_ui,
                "append": self.dccomponent_append,
                "label": "直流分量",
            }
        if handler_key == "reconnect":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_reconnect_ui,
                "append": self.reconnect_append,
                "label": "重连",
            }
        if handler_key == "ovuf":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_ovuf_ui,
                "append": self.ovuf_append,
                "label": "过欠压_过欠频",
            }
        if handler_key == "guopinjiangzai":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_guopinjiangzai_ui,
                "append": self.guopinjiangzai_append,
                "label": "过频降载",
            }
        if handler_key == "qianpinshengzai":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_qianpinshengzai_ui,
                "append": self.qianpinshengzai_append,
                "label": "欠频升载",
            }
        if handler_key == "voltprotect10min":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_voltprotect10min_ui,
                "append": self.voltprotect10min_append,
                "label": "10min过压保护",
            }
        if handler_key == "guoqianpin_immun":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_guoqianpin_immun_ui,
                "append": self.guoqianpin_immun_append,
                "label": "巴西过欠频稳定性",
            }
        if handler_key == "staticmppt":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_staticmppt_ui,
                "append": self.staticmppt_append,
                "label": "静态MPPT测试",
            }
        if handler_key == "frequencyadaptability":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_frequencyadaptability_ui,
                "append": self.frequencyadaptability_append,
                "label": "频率适应性",
            }
        if handler_key == "voltageadaptability":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_voltageadaptability_ui,
                "append": self.voltageadaptability_append,
                "label": "电压适应性",
            }
        if handler_key == "rocof":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_rocof_ui,
                "append": self.rocof_append,
                "label": "ROCOF保护",
            }
        if handler_key == "rapidvolt":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_rapidvolt_ui,
                "append": self.rapidvolt_append,
                "label": "快速电压变化",
            }
        if handler_key == "lvrt":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_lvrt_ui,
                "append": self.lvrt_append,
                "label": "低电压穿越",
            }
        if handler_key == "phasejump":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_phasejump_ui,
                "append": self.phasejump_append,
                "label": "相角突变",
            }
        if handler_key == "dynamicmppt":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_dynamicmppt_ui,
                "append": self.dynamicmppt_append,
                "label": "动态MPPT",
            }
        if handler_key == "reactiveqcap":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_reactiveqcap_ui,
                "append": self.reactiveqcap_append,
                "label": "无功能力范围",
            }
        if handler_key == "fixedq":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_fixedq_ui,
                "append": self.fixedq_append,
                "label": "定无功",
            }
        if handler_key == "reactiveqin":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_reactiveqin_ui,
                "append": self.reactiveqin_append,
                "label": "无功注入",
            }
        if handler_key == "reactiveqacc":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_reactiveqacc_ui,
                "append": self.reactiveqacc_append,
                "label": "无功精度",
            }
        if handler_key == "activep":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_activep_ui,
                "append": self.activep_append,
                "label": "有功调度",
            }
        if handler_key == "staticqu":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_staticqu_ui,
                "append": self.staticqu_append,
                "label": "静态QU",
            }
        if handler_key == "dynamicqu":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_dynamicqu_ui,
                "append": self.dynamicqu_append,
                "label": "动态QU",
            }
        if handler_key == "testpu":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_testpu_ui,
                "append": self.testpu_append,
                "label": "Test_PU",
            }
        if handler_key == "staticcosphi":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_staticcosphi_ui,
                "append": self.staticcosphi_append,
                "label": "静态Cos(φ)",
            }
        if handler_key == "dynamiccosphi":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_dynamiccosphi_ui,
                "append": self.dynamiccosphi_append,
                "label": "动态Cos(φ)",
            }
        if handler_key == "cosphibrazil":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_cosphibrazil_ui,
                "append": self.cosphibrazil_append,
                "label": "Cos(φ)_Brazil",
            }
        return None

    def _move_pending_done(self, pending_path: Path) -> None:
        try:
            done_dir = self.repo_root / "iot_job_inbox" / "done"
            done_dir.mkdir(parents=True, exist_ok=True)
            pending_path.replace(done_dir / pending_path.name)
        except OSError:
            pass

    def _attach_report_files(self, result: Dict[str, Any], job_id: int) -> None:
        """结案时把本机近期试验产出路径写入 result_summary.report_files，供 Agent 上传。"""
        try:
            from agent.reports import collect_report_files
        except Exception:
            return
        summary = result.get("result_summary")
        if not isinstance(summary, dict):
            summary = {}
            result["result_summary"] = summary
        from agent.job_inbox import write_result

        pending = None
        if self._awaiting:
            pending = self._awaiting.get("pending_path")
        for root in self._write_roots_for(pending):
            write_result(root, job_id, result)
        paths = collect_report_files(self.repo_root, job_id, result)
        # 合并而非覆盖：保留 last_dew / 先前注入的 dewetron_csv
        existing = list(summary.get("report_files") or [])
        seen = set()
        listed = []

        def _push(item) -> None:
            if isinstance(item, dict):
                raw = str(item.get("path") or item.get("file") or "")
            else:
                raw = str(item or "")
            key = raw.replace("\\", "/").lower()
            if not raw or key in seen:
                return
            seen.add(key)
            listed.append(item if isinstance(item, dict) else raw)

        for item in existing:
            _push(item)
        for p in paths:
            try:
                _push(str(p.resolve()))
            except OSError:
                _push(str(p))
        if listed:
            summary["report_files"] = listed
            result["result_summary"] = summary
            for root in self._write_roots_for(pending):
                write_result(root, job_id, result)

    def abort_awaiting_job(self, fail_reason: str = "软件急停") -> Optional[int]:
        """若有等待结案的云任务，立即以 aborted 写回并释放 UI。返回 job_id 或 None。"""
        aw = self._awaiting
        if not aw:
            return None
        job_id = int(aw["job_id"])
        pending_path = aw.get("pending_path")
        started_at = float(aw.get("started_at") or time.time())
        elapsed = max(0.0, time.time() - started_at)
        reason = str(fail_reason or "软件急停").strip() or "软件急停"
        try:
            from agent.job_inbox import ack_stop_request, write_stop_request

            write_stop_request(self.repo_root, job_id, reason=reason)
            ack_stop_request(self.repo_root, job_id)
        except Exception as exc:
            self._log(f"软件急停写 stop_request 失败: {exc}")
        self._finish_job(
            job_id=job_id,
            pending_path=pending_path,
            result={
                "status": "aborted",
                "fail_reason": reason,
                "result_summary": {
                    "handoff": True,
                    "software_estop": True,
                    "appended": aw.get("appended"),
                    "started": bool(aw.get("seen_running")),
                    "waited_finish": False,
                    "elapsed_sec": round(elapsed, 1),
                    "missingWidgets": aw.get("missing") or [],
                    "note": reason,
                },
                "report_meta": [],
            },
        )
        self._log(f"任务 {job_id} 因软件急停已中止")
        return job_id

    def finish_awaiting_as_new_round(self) -> Optional[int]:
        """本机已另行追加/开测：把还挂着的上一云任务按完成结案，避免进度写回旧单。"""
        aw = self._awaiting
        if not isinstance(aw, dict):
            return None
        try:
            job_id = int(aw.get("job_id") or 0)
        except (TypeError, ValueError):
            return None
        if job_id <= 0:
            return None
        pending_path = aw.get("pending_path")
        self._finish_job(
            job_id=job_id,
            pending_path=pending_path,
            result={
                "status": "success",
                "fail_reason": "",
                "result_summary": {
                    "handoff": True,
                    "appended": aw.get("appended"),
                    "note": "本机已另行追加，上一云任务按完成结案",
                },
                "report_meta": [],
            },
        )
        self._log(f"任务 {job_id} 已结案（本机另行追加）")
        return job_id

    def _finish_job(
        self,
        *,
        job_id: int,
        pending_path: Optional[Path],
        result: Dict[str, Any],
        release_ui: bool = True,
    ) -> None:
        jid = int(job_id)
        finishing = getattr(self, "_finishing_job_ids", None)
        if finishing is None:
            finishing = set()
            self._finishing_job_ids = finishing
        if jid in finishing:
            self._log(f"任务 {jid} 结案重入已忽略")
            return
        finishing.add(jid)

        # 结案含同步跑数据处理，耗时长。必须立刻摘掉 _awaiting，
        # 否则定时器 / desktop_finished / 「本机另行追加」会再进一次，
        # 两个 headless 同秒写同一 headless_result.json → Extra data。
        aw = self._awaiting if isinstance(self._awaiting, dict) else {}
        try:
            aw_job = int(aw.get("job_id") or 0)
        except (TypeError, ValueError):
            aw_job = 0
        if isinstance(aw, dict):
            aw["_finishing"] = True
        if aw_job and aw_job == jid:
            self._awaiting = None
        elif self._awaiting is not None and aw_job == 0:
            self._awaiting = None

        try:
            self._finish_job_body(
                job_id=jid,
                pending_path=pending_path,
                result=result,
                release_ui=release_ui,
                aw=aw,
            )
        finally:
            finishing.discard(jid)

    def _finish_job_body(
        self,
        *,
        job_id: int,
        pending_path: Optional[Path],
        result: Dict[str, Any],
        release_ui: bool,
        aw: Dict[str, Any],
    ) -> None:
        from agent.job_inbox import write_result
        from agent.ui_mutex import ui_release

        # 先写入 testType，再收集报告：aborted 也要按 OVUF 等 token 扫 wt_save
        summary = result.get("result_summary") if isinstance(result.get("result_summary"), dict) else {}
        if aw.get("test_type") and not summary.get("testType"):
            summary["testType"] = aw.get("test_type")
        if aw.get("handler_key") and not summary.get("handler_key"):
            summary["handler_key"] = aw.get("handler_key")
        if aw.get("widgets") and not summary.get("widgets"):
            summary["widgets"] = aw.get("widgets")
        try:
            started = float(aw.get("started_at") or 0)
        except (TypeError, ValueError):
            started = 0.0
        if started > 1_000_000_000 and not summary.get("started_at"):
            summary["started_at"] = started
        result["result_summary"] = summary

        # 德威创刚写出的 CSV：进度状态 / 内存 / sidecar 三路交叉验证
        try:
            from pathlib import Path as _P

            from utils.last_dew_export import (
                last_dew_csv,
                last_dew_dir,
                last_dew_dmd,
                read_sidecar_full,
            )

            candidates = []
            if self.get_run_progress:
                try:
                    snap = self.get_run_progress() or {}
                    if isinstance(snap, dict):
                        candidates.append(snap.get("last_dew_csv"))
                        if snap.get("analysis_input_dir") and not summary.get(
                            "analysis_input_dir"
                        ):
                            summary["analysis_input_dir"] = str(
                                snap.get("analysis_input_dir")
                            )
                except Exception:
                    pass
            candidates.append(last_dew_csv())
            side_csv, side_dir, side_dmd = read_sidecar_full()
            candidates.append(side_csv)
            if side_dir and not summary.get("analysis_input_dir"):
                summary["analysis_input_dir"] = side_dir
            mem_dir = last_dew_dir()
            if mem_dir and not summary.get("analysis_input_dir"):
                summary["analysis_input_dir"] = mem_dir

            last_dew = ""
            for raw in candidates:
                text = str(raw or "").strip()
                if not text:
                    continue
                p = _P(text)
                if p.is_file() or p.is_dir():
                    last_dew = text
                    break
                # 文件刚写出偶发 is_file 失败时仍记下路径
                if text.lower().endswith(".csv"):
                    last_dew = text
                    break
            listed = list(summary.get("report_files") or [])
            if last_dew:
                p = _P(str(last_dew))
                d = p if p.is_dir() else p.parent
                if str(d):
                    summary["analysis_input_dir"] = str(d)
                    summary["last_dew_csv"] = str(last_dew)
                if p.suffix.lower() == ".csv":
                    listed.append(
                        {"path": str(p), "name": p.name, "kind": "dewetron_csv"}
                    )
            dmd = last_dew_dmd() or side_dmd

            def _dmd_belongs_to_csv(dmd_path: _P, csv_path: _P) -> bool:
                """禁止把目录里几天前的旧 .dmd（如 dewetron_20261109_*.dmd）当成本轮报告。"""
                try:
                    if not dmd_path.is_file() or dmd_path.suffix.lower() != ".dmd":
                        return False
                    name = dmd_path.name.lower()
                    stem = csv_path.stem.lower() if csv_path.suffix.lower() == ".csv" else ""
                    if stem and (stem in name or stem.replace("-", "_") in name):
                        return True
                    if csv_path.is_file():
                        dt = abs(dmd_path.stat().st_mtime - csv_path.stat().st_mtime)
                        # 同一次试验落盘通常紧挨着；放宽到 2 小时防时钟偏差
                        if dt <= 2 * 3600:
                            return True
                except OSError:
                    return False
                return False

            csv_for_dmd = _P(str(last_dew)) if last_dew else None
            if dmd and csv_for_dmd is not None and csv_for_dmd.suffix.lower() == ".csv":
                if not _dmd_belongs_to_csv(_P(str(dmd)), csv_for_dmd):
                    self._log(
                        f"忽略与本轮 CSV 无关的旧 .dmd: {dmd}（csv={csv_for_dmd.name}）"
                    )
                    dmd = ""
            if not dmd and csv_for_dmd is not None and csv_for_dmd.suffix.lower() == ".csv":
                # STORE 偶发未 remember：仅收与本轮 CSV 同名/同时段的 .dmd
                try:
                    folder = csv_for_dmd.parent
                    if folder.is_dir():
                        siblings = sorted(
                            folder.glob("*.dmd"),
                            key=lambda p: p.stat().st_mtime,
                            reverse=True,
                        )
                        for sib in siblings:
                            if _dmd_belongs_to_csv(sib, csv_for_dmd):
                                dmd = str(sib)
                                break
                except Exception:
                    pass
            if dmd:
                dp = _P(str(dmd))
                if dp.suffix.lower() == ".dmd" and dp.is_file():
                    summary["last_dew_dmd"] = str(dp)
                    listed.append(
                        {"path": str(dp), "name": dp.name, "kind": "dewetron_dmd"}
                    )
            if listed:
                summary["report_files"] = listed
            result["result_summary"] = summary
        except Exception:
            pass
        try:
            self._attach_report_files(result, job_id)
        except Exception:
            pass
        try:
            from utils.iot_data_analysis_bridge import remember_analysis_input_dir

            remembered = remember_analysis_input_dir(result, self.repo_root)
            if remembered is None:
                self._log(
                    "结案未定位到 CSV 目录（已扫 last_dew/sidecar/LOCALAPPDATA/dewetron_save）"
                )
        except Exception:
            pass
        # 结案自动数据处理（台架本机）；失败不阻断写回
        try:
            from utils.iot_data_analysis_bridge import run_analysis_after_job

            job_snap = {
                "id": job_id,
                "testType": aw.get("test_type")
                or summary.get("testType")
                or summary.get("handler_key")
                or "",
                "widgets": aw.get("widgets") or summary.get("widgets") or {},
                "params": aw.get("params") or {},
            }
            ana = run_analysis_after_job(
                repo_root=self.repo_root, job=job_snap, result=result
            )
            csv_hint = (
                ana.get("input_dir")
                or (ana.get("csv_files") or [None])[0]
                or ""
            )
            if ana.get("ran") or ana.get("reason"):
                self._log(
                    f"数据处理 {'OK' if ana.get('success') else 'skip'}: "
                    f"{ana.get('reason') or ana.get('target')}"
                    + (f" csv={csv_hint}" if csv_hint else "")
                )
            # 试验队列跑完曾一律 success；单帧/分析失败时要降级，避免云端误判合格
            if str(result.get("status") or "").lower() in ("success", "ok"):
                if ana.get("ran") and not ana.get("success"):
                    result["status"] = "failed"
                    result["fail_reason"] = (
                        f"数据处理失败: {ana.get('reason') or 'exit!=0'}"
                    )[:512]
                elif (not ana.get("ran")) and ana.get("quality") in (
                    "too_few_rows",
                    "wrong_csv",
                ):
                    result["status"] = "failed"
                    result["fail_reason"] = (
                        f"录波无效: {ana.get('reason') or 'CSV 不适用'}"
                    )[:512]
        except Exception as exc:
            self._log(f"数据处理跳过: {exc}")
        try:
            summary = result.get("result_summary")
            if isinstance(summary, dict):
                rf = summary.get("report_files") or summary.get("reportFiles") or []
                paths = []
                for item in rf:
                    if isinstance(item, dict):
                        raw = str(item.get("path") or item.get("file") or "")
                    else:
                        raw = str(item or "")
                    if not raw:
                        continue
                    name = raw.replace("\\", "/").rsplit("/", 1)[-1].lower()
                    # 日志不要刷 status.json / job_*.json 等交接元数据
                    if name == "status.json" or (
                        name.startswith("job_") and name.endswith(".json")
                    ):
                        continue
                    if not name.endswith(
                        (
                            ".csv",
                            ".xlsx",
                            ".xls",
                            ".docx",
                            ".pdf",
                            ".png",
                            ".jpg",
                            ".dmd",
                        )
                    ):
                        continue
                    paths.append(raw)
                    if len(paths) >= 8:
                        break
                if paths:
                    self._log("导出文件: " + " | ".join(paths))
                elif summary.get("analysis_input_dir") or summary.get("analysisInputDir"):
                    self._log(
                        "导出目录: "
                        + str(
                            summary.get("analysis_input_dir")
                            or summary.get("analysisInputDir")
                        )
                    )
        except Exception:
            pass
        for root in self._write_roots_for(pending_path):
            try:
                write_result(root, job_id, result)
            except Exception:
                pass
        self._log(f"任务 {job_id} 已写回 results status={result.get('status')}")
        if pending_path is not None:
            self._move_pending_done(pending_path)
        self._awaiting = None
        self._busy = False
        if release_ui:
            ui_release(repo_root=self.repo_root)

    def _check_awaiting_finish(self) -> None:
        aw = self._awaiting
        if not aw:
            return
        # 结案中（含数据处理）禁止重入，避免双开 headless 写坏 result-json
        if aw.get("_finishing"):
            return
        job_id = int(aw["job_id"])
        pending_path = aw.get("pending_path")
        now = time.time()
        elapsed = now - float(aw.get("started_at") or now)
        status = self._read_run_status()
        # 上一单已被心跳写成已中止时，不要把它当成这一单的结果。
        if (
            status in ("已结束", "已中止", "失败")
            and not aw.get("seen_running")
        ):
            file_job = self._status_file_job_id()
            if file_job and file_job != job_id:
                status = ""
        start_grace = float(aw.get("start_grace_sec") or 20)
        timeout = float(aw.get("timeout_sec") or 7200)

        # 真正执行过至少 1 条命令才算开跑。RunProjectPush 会先把状态写成「进行中」
        # 且 cmd_index=0，空队列/瞬间收尾若只认状态会秒成功。
        cmd_index, cmd_total = 0, 0
        if self.get_run_progress:
            try:
                snap = self.get_run_progress() or {}
                if isinstance(snap, dict):
                    cmd_index = int(snap.get("cmd_index") or 0)
                    cmd_total = int(snap.get("cmd_total") or 0)
            except Exception:
                cmd_index, cmd_total = 0, 0
        if cmd_index > int(aw.get("max_cmd_index") or 0):
            aw["max_cmd_index"] = cmd_index
        if cmd_total > int(aw.get("max_cmd_total") or 0):
            aw["max_cmd_total"] = cmd_total

        if status == "进行中":
            if (
                not aw.get("seen_running")
                and cmd_index >= 1
                and (cmd_total > 0 or int(aw.get("max_cmd_total") or 0) > 0)
            ):
                aw["seen_running"] = True
                self._log(
                    f"任务 {job_id} 已真正开跑（命令 {cmd_index}/{cmd_total or aw.get('max_cmd_total')}）"
                )
            self._emit_progress(job_id)
            return

        if status == "已结束":
            # 没见过这一单真正执行命令时，宽限内继续等；超时后必须失败。
            # 否则「乐观进行中 + 空跑已结束」会在数秒内收成 success。
            if not aw.get("seen_running"):
                if elapsed < start_grace:
                    return
                self._finish_job(
                    job_id=job_id,
                    pending_path=pending_path,
                    result={
                        "status": "failed",
                        "fail_reason": (
                            f"开始试验后 {int(start_grace)}s 内未见命令真正执行"
                            f"（当前状态=已结束，cmd={aw.get('max_cmd_index') or 0}/"
                            f"{aw.get('max_cmd_total') or 0}），可能队列为空或启动被拦截"
                        ),
                        "result_summary": {
                            "handoff": True,
                            "appended": aw.get("appended"),
                            "started": False,
                            "waited_finish": True,
                            "run_status": status,
                            "elapsed_sec": round(elapsed, 1),
                            "cmd_index": int(aw.get("max_cmd_index") or 0),
                            "cmd_total": int(aw.get("max_cmd_total") or 0),
                            "missingWidgets": aw.get("missing") or [],
                        },
                        "report_meta": [],
                    },
                )
                return
            self._finish_job(
                job_id=job_id,
                pending_path=pending_path,
                result={
                    "status": "success",
                    "fail_reason": "",
                    "result_summary": {
                        "handoff": True,
                        "appended": aw.get("appended"),
                        "started": True,
                        "waited_finish": True,
                        "run_status": status,
                        "elapsed_sec": round(elapsed, 1),
                        "cmd_index": int(aw.get("max_cmd_index") or 0),
                        "cmd_total": int(aw.get("max_cmd_total") or 0),
                        "missingWidgets": aw.get("missing") or [],
                        "note": "试验已正常结束并回传",
                    },
                    "report_meta": [],
                },
            )
            return

        if status in ("已中止", "失败"):
            if (
                not aw.get("seen_running")
                and not aw.get("desktop_finished")
                and elapsed < start_grace
            ):
                return
            max_i = int(aw.get("max_cmd_index") or cmd_index or 0)
            max_t = int(aw.get("max_cmd_total") or cmd_total or 0)
            # 末段 OUTP OFF 等收口偶发写成「已中止」（如 job99 496/500）：按完成结案以便上传 CSV
            near_done = (
                status == "已中止"
                and bool(aw.get("seen_running"))
                and max_t > 0
                and max_i >= max(1, int(max_t * 0.95))
            )
            if near_done:
                self._finish_job(
                    job_id=job_id,
                    pending_path=pending_path,
                    result={
                        "status": "success",
                        "fail_reason": "",
                        "result_summary": {
                            "handoff": True,
                            "appended": aw.get("appended"),
                            "started": True,
                            "waited_finish": True,
                            "run_status": status,
                            "elapsed_sec": round(elapsed, 1),
                            "cmd_index": max_i,
                            "cmd_total": max_t,
                            "missingWidgets": aw.get("missing") or [],
                            "note": (
                                f"末段收口本地状态为已中止（命令 {max_i}/{max_t}），按完成结案"
                            ),
                        },
                        "report_meta": [],
                    },
                )
                return
            self._finish_job(
                job_id=job_id,
                pending_path=pending_path,
                result={
                    "status": "aborted" if status == "已中止" else "failed",
                    "fail_reason": (
                        f"开始试验后 {int(start_grace)}s 内未进入「进行中」"
                        if not aw.get("seen_running") and not aw.get("desktop_finished")
                        else f"试验状态={status}"
                    ),
                    "result_summary": {
                        "handoff": True,
                        "appended": aw.get("appended"),
                        "started": bool(aw.get("seen_running")),
                        "waited_finish": True,
                        "run_status": status,
                        "elapsed_sec": round(elapsed, 1),
                        "cmd_index": max_i,
                        "cmd_total": max_t,
                        "missingWidgets": aw.get("missing") or [],
                    },
                    "report_meta": [],
                },
            )
            return

        if not aw.get("seen_running") and elapsed >= start_grace:
            self._finish_job(
                job_id=job_id,
                pending_path=pending_path,
                result={
                    "status": "failed",
                    "fail_reason": (
                        f"开始试验后 {int(start_grace)}s 内未进入「进行中」"
                        f"（当前状态={status or '空'}），可能启动被拦截"
                    ),
                    "result_summary": {
                        "handoff": True,
                        "appended": aw.get("appended"),
                        "started": False,
                        "waited_finish": True,
                        "run_status": status,
                        "missingWidgets": aw.get("missing") or [],
                    },
                    "report_meta": [],
                },
            )
            return

        if elapsed >= timeout:
            self._finish_job(
                job_id=job_id,
                pending_path=pending_path,
                result={
                    "status": "failed",
                    "fail_reason": f"等待试验结束超时（{int(timeout)}s），当前状态={status or '空'}",
                    "result_summary": {
                        "handoff": True,
                        "appended": aw.get("appended"),
                        "started": bool(aw.get("seen_running")),
                        "waited_finish": True,
                        "run_status": status,
                        "missingWidgets": aw.get("missing") or [],
                    },
                    "report_meta": [],
                },
            )

    def _handle_job(self, job: dict, pending_path: Path) -> None:
        from agent.job_inbox import write_result
        from agent.ui_mutex import ui_release, ui_try_acquire

        job_id = int(job.get("id") or 0)
        test_type = str(job.get("testType") or "").strip().lower()
        self._log(f"处理任务 id={job_id} type={test_type}")
        try:
            self._discard_unrelated_stops(job_id)
        except Exception as exc:
            self._log(f"清理过期停机失败: {exc}")

        # 本机已在跑、且这条云任务不追加：拒收，避免再开一局。
        # 带自动追加时放行，后面只把命令接到当前队列，不清空、不二次开始。
        # 进度条和 strTestStatusFlag 任一在跑都算占用，避免刚启动的窗口误改绑。
        from utils.iot_local_run import bench_is_running

        local_status = self._read_run_status()
        bench_running = bench_is_running(local_status)
        params_early = job.get("params") if isinstance(job.get("params"), dict) else {}
        auto_append_early = True
        if isinstance(params_early, dict) and "auto_append" in params_early:
            auto_append_early = bool(params_early.get("auto_append"))
        if bench_running and not auto_append_early:
            reason = "本机试验进行中，已拒收云端任务"
            self._log(reason + f"（status={local_status}）")
            self._write_result_all(
                pending_path,
                job_id,
                {
                    "status": "failed",
                    "fail_reason": reason,
                    "result_summary": {
                        "handoff": True,
                        "rejected": True,
                        "local_status": local_status,
                    },
                },
            )
            self._move_pending_done(pending_path)
            return

        if not ui_try_acquire(meta=f"handoff:{job_id}", repo_root=self.repo_root):
            self._log("无法占本机 UI 锁（可能 Agent 仍占用），本轮跳过")
            return

        try:
            handler = self._resolve_handler(test_type)
            if not handler:
                self._write_result_all(
                    pending_path,
                    job_id,
                    {
                        "status": "failed",
                        "fail_reason": f"界面交接暂不支持试验类型={test_type}",
                    },
                )
                self._move_pending_done(pending_path)
                return

            if self.ensure_project:
                try:
                    self.ensure_project(handler["project_name"])
                except Exception as exc:
                    self._log(f"切换项目失败: {exc}")

            try:
                from utils.iot_local_run import adopt_cloud_job

                if bench_running:
                    self._log("本机正在执行，保留当前任务号，只把 IOT 命令追加进队列")
                else:
                    raw_eid = job.get("experId") or job.get("experid")
                    try:
                        eid = int(raw_eid) if raw_eid else None
                    except (TypeError, ValueError):
                        eid = None
                    adopt_cloud_job(job_id, eid)
            except Exception as exc:
                self._log(f"写入当前任务号失败: {exc}")

            resolve_ui = handler.get("resolve_ui")
            ui_obj = resolve_ui() if resolve_ui else None
            if ui_obj is None:
                self._write_result_all(
                    pending_path,
                    job_id,
                    {"status": "failed", "fail_reason": f"{handler['label']}界面未就绪"},
                )
                self._move_pending_done(pending_path)
                return

            # 强制 LazyDialog 创建
            real_ui = ui_obj
            if hasattr(ui_obj, "ui"):
                try:
                    real_ui = ui_obj.ui
                except Exception:
                    real_ui = ui_obj
            if hasattr(ui_obj, "ensure"):
                try:
                    ui_obj.ensure()
                    real_ui = getattr(ui_obj, "_real_ui", None) or real_ui
                except Exception:
                    pass

            params = job.get("params") or {}
            widgets = params.get("widgets") if isinstance(params, dict) else None
            if not isinstance(widgets, dict):
                widgets = params if isinstance(params, dict) else {}
            # 去掉非控件元数据（含 Blockly 快照字段，避免误写入 Dialog）
            _meta_keys = (
                "e2e",
                "auto_append",
                "auto_start",
                "wait_finish",
                "wait_finish_timeout_sec",
                "start_grace_sec",
                "settings_csv",
                "widgets",
                "instruments",
                "auto_connect_from",
                "experId",
                "experid",
                "source",
                "useSavedTestParams",
                "useSavedInstruments",
                "blocklyCode",
                "blockly_code",
                "blocklyXml",
                "blockly_xml",
                "blocklyPreserved",
                "blocklySource",
                "procedureSteps",
                "procedureSource",
                "solarStandard",
                # 执行模式元数据：勿写入 Dialog 控件
                "executionMode",
                "execution_mode",
                "blocklyShadowCompare",
                "blockly_shadow_compare",
                "fallbackDialogAppend",
            )
            if isinstance(widgets, dict):
                widgets = {
                    k: v
                    for k, v in widgets.items()
                    if k not in _meta_keys and not str(k).startswith("_")
                }
            try:
                steps = params.get("procedureSteps") if isinstance(params, dict) else None
                n_steps = len(steps) if isinstance(steps, list) else 0
                src = str((params or {}).get("procedureSource") or "")
                bsrc = str((params or {}).get("blocklySource") or "")
                from utils.iot_blockly_interpreter import (
                    format_plan_log_lines,
                    normalize_execution_mode,
                    plan_from_blockly,
                    shadow_compare_plan,
                )

                exec_mode = normalize_execution_mode(
                    (params or {}).get("executionMode")
                    or (params or {}).get("execution_mode")
                )
                _shadow_raw = (params or {}).get("blocklyShadowCompare")
                if _shadow_raw is None:
                    _shadow_raw = (params or {}).get("blockly_shadow_compare")
                if isinstance(_shadow_raw, bool):
                    shadow_on = _shadow_raw
                else:
                    shadow_on = str(_shadow_raw or "").strip().lower() in (
                        "1",
                        "true",
                        "yes",
                        "on",
                    )
                if n_steps or bsrc or exec_mode != "dialog_append":
                    self._log(
                        f"Blockly 步骤包 steps={n_steps} source={src or '-'} "
                        f"blockly={bsrc or '-'} "
                        f"preserved={bool((params or {}).get('blocklyPreserved'))} "
                        f"executionMode={exec_mode} shadow={shadow_on}"
                    )
                # 影子对照只打日志，不改变执行路径
                if shadow_on:
                    code = str(
                        (params or {}).get("blocklyCode")
                        or (params or {}).get("blockly_code")
                        or ""
                    )
                    plan = plan_from_blockly(
                        code,
                        procedure_steps=steps if isinstance(steps, list) else None,
                    )
                    cmp_ = shadow_compare_plan(
                        plan,
                        procedure_steps=steps if isinstance(steps, list) else None,
                        widgets=widgets if isinstance(widgets, dict) else None,
                    )
                    for line in format_plan_log_lines(plan, limit=24):
                        self._log(f"[shadow] {line}")
                    self._log(
                        f"[shadow] compare missingInProc={len(cmp_.get('missingInProcedure') or [])} "
                        f"extraInProc={len(cmp_.get('extraInProcedure') or [])} "
                        f"widgetMismatch={len(cmp_.get('widgetMismatches') or [])} "
                        f"ovufSeg={cmp_.get('ovufSegmentOrder')}"
                    )
            except Exception as _blk_exc:
                self._log(f"Blockly 执行模式/影子对照日志跳过: {_blk_exc}")

            if (handler.get("key") or "") == "overload":
                try:
                    from utils.iot_overload_schema import merge_widgets

                    widgets = merge_widgets(None, widgets if isinstance(widgets, dict) else {})
                except Exception as exc:
                    self._log(f"过载 schema 默认值合并跳过: {exc}")

            # 工控机上次试验参数：勾选开启时补全云端未填字段
            try:
                from utils.iot_bench_prefs import merge_widgets_with_memory, update_and_push

                tt_key = str(handler.get("key") or job.get("testType") or "").strip().lower()
                widgets = merge_widgets_with_memory(
                    tt_key,
                    widgets if isinstance(widgets, dict) else {},
                    params if isinstance(params, dict) else {},
                )
                if isinstance(widgets, dict) and widgets:
                    update_and_push(
                        {
                            "testParamsByType": {
                                tt_key: {
                                    "widgets": dict(widgets),
                                    "auto_append": bool((params or {}).get("auto_append", True))
                                    if isinstance(params, dict)
                                    else True,
                                    "auto_start": bool((params or {}).get("auto_start", True))
                                    if isinstance(params, dict)
                                    else True,
                                    "wait_finish": bool((params or {}).get("wait_finish", True))
                                    if isinstance(params, dict)
                                    else True,
                                }
                            },
                            "source": "desktop",
                        }
                    )
            except Exception as exc:
                self._log(f"工控机参数记忆合并跳过: {exc}")

            # 闪变/谐波/直流分量/固定PF/过载/重连/过欠压_过欠频：认 job/widgets.solarStandard，按标准补全空字段默认工况
            flicker_sid = ""
            harmonic_sid = ""
            dccomponent_sid = ""
            fixedpf_sid = ""
            overload_sid = ""
            reconnect_sid = ""
            ovuf_sid = ""
            guopinjiangzai_sid = ""
            cosphibrazil_sid = ""
            dynamiccosphi_sid = ""
            staticcosphi_sid = ""
            testpu_sid = ""
            dynamicqu_sid = ""
            staticqu_sid = ""
            activep_sid = ""
            reactiveqacc_sid = ""
            reactiveqin_sid = ""
            fixedq_sid = ""
            reactiveqcap_sid = ""
            dynamicmppt_sid = ""
            staticmppt_sid = ""
            phasejump_sid = ""
            lvrt_sid = ""
            rapidvolt_sid = ""
            guoqianpin_immun_sid = ""
            rocof_sid = ""
            frequencyadaptability_sid = ""
            qianpinshengzai_sid = ""
            voltageadaptability_sid = ""
            voltprotect10min_sid = ""
            antibackflow_sid = ""
            if (handler.get("key") or "") == "flicker":
                try:
                    from utils.iot_flicker_standard import (
                        apply_flicker_standard_to_widgets,
                        resolve_flicker_standard_id,
                    )

                    flicker_sid = resolve_flicker_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_flicker_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        flicker_sid,
                        force=False,
                    )
                    self._log(f"闪变标准 solarStandard={flicker_sid}")
                except Exception as exc:
                    self._log(f"闪变标准默认合并跳过: {exc}")
            elif (handler.get("key") or "") == "harmonic":
                try:
                    from utils.iot_harmonic_standard import (
                        apply_harmonic_standard_to_widgets,
                        resolve_harmonic_standard_id,
                    )

                    harmonic_sid = resolve_harmonic_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_harmonic_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        harmonic_sid,
                        force=False,
                    )
                    self._log(f"谐波标准 solarStandard={harmonic_sid}")
                except Exception as exc:
                    self._log(f"谐波标准默认合并跳过: {exc}")
            elif (handler.get("key") or "") == "dccomponent":
                try:
                    from utils.iot_dccomponent_standard import (
                        apply_dccomponent_standard_to_widgets,
                        resolve_dccomponent_standard_id,
                    )

                    dccomponent_sid = resolve_dccomponent_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_dccomponent_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        dccomponent_sid,
                        force=False,
                    )
                    self._log(f"直流分量标准 solarStandard={dccomponent_sid}")
                except Exception as exc:
                    self._log(f"直流分量标准默认合并跳过: {exc}")
            elif (handler.get("key") or "") == "fixedpf":
                try:
                    from utils.iot_fixedpf_standard import (
                        apply_fixedpf_standard_to_widgets,
                        resolve_fixedpf_standard_id,
                    )

                    fixedpf_sid = resolve_fixedpf_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_fixedpf_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        fixedpf_sid,
                        force=False,
                    )
                    self._log(f"固定PF标准 solarStandard={fixedpf_sid}")
                except Exception as exc:
                    self._log(f"固定PF标准默认合并跳过: {exc}")
            elif (handler.get("key") or "") == "overload":
                try:
                    from utils.iot_overload_standard import (
                        apply_overload_standard_to_widgets,
                        resolve_overload_standard_id,
                    )

                    overload_sid = resolve_overload_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_overload_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        overload_sid,
                        force=False,
                    )
                    self._log(f"过载标准 solarStandard={overload_sid}")
                except Exception as exc:
                    self._log(f"过载标准默认合并跳过: {exc}")
            elif (handler.get("key") or "") == "reconnect":
                try:
                    from utils.iot_reconnect_standard import (
                        apply_reconnect_standard_to_widgets,
                        resolve_reconnect_standard_id,
                    )

                    reconnect_sid = resolve_reconnect_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_reconnect_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        reconnect_sid,
                        force=False,
                    )
                    self._log(f"重连标准 solarStandard={reconnect_sid}")
                except Exception as exc:
                    self._log(f"重连标准默认合并跳过: {exc}")
            elif (handler.get("key") or "") == "ovuf":
                try:
                    from utils.iot_ovuf_standard import (
                        apply_ovuf_standard_to_widgets,
                        resolve_ovuf_standard_id,
                    )

                    ovuf_sid = resolve_ovuf_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_ovuf_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        ovuf_sid,
                        force=False,
                    )
                    self._log(f"过欠压_过欠频标准 solarStandard={ovuf_sid}")
                except Exception as exc:
                    self._log(f"过欠压_过欠频标准默认合并跳过: {exc}")
            elif (handler.get("key") or "") == "guopinjiangzai":
                try:
                    from utils.iot_guopinjiangzai_standard import (
                        apply_guopinjiangzai_standard_to_widgets,
                        resolve_guopinjiangzai_standard_id,
                    )

                    guopinjiangzai_sid = resolve_guopinjiangzai_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_guopinjiangzai_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        guopinjiangzai_sid,
                        force=False,
                    )
                    self._log(f"过频降载标准 solarStandard={guopinjiangzai_sid}")
                except Exception as exc:
                    self._log(f"过频降载标准默认合并跳过: {exc}")
            elif (handler.get("key") or "") == "qianpinshengzai":
                try:
                    from utils.iot_qianpinshengzai_standard import (
                        apply_qianpinshengzai_standard_to_widgets,
                        resolve_qianpinshengzai_standard_id,
                    )

                    qianpinshengzai_sid = resolve_qianpinshengzai_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_qianpinshengzai_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        qianpinshengzai_sid,
                        force=False,
                    )
                    self._log(f"欠频升载标准 solarStandard={qianpinshengzai_sid}")
                except Exception as exc:
                    self._log(f"欠频升载标准默认合并跳过: {exc}")
            elif (handler.get("key") or "") == "voltageadaptability":
                try:
                    from utils.iot_voltageadaptability_standard import (
                        apply_voltageadaptability_standard_to_widgets,
                        resolve_voltageadaptability_standard_id,
                    )

                    voltageadaptability_sid = resolve_voltageadaptability_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_voltageadaptability_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        voltageadaptability_sid,
                        force=False,
                    )
                    self._log(f"电压适应性标准 solarStandard={voltageadaptability_sid}")
                except Exception as exc:
                    self._log(f"电压适应性标准默认合并跳过: {exc}")
            elif (handler.get("key") or "") == "voltprotect10min":
                try:
                    from utils.iot_voltprotect10min_standard import (
                        apply_voltprotect10min_standard_to_widgets,
                        resolve_voltprotect10min_standard_id,
                    )

                    voltprotect10min_sid = resolve_voltprotect10min_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_voltprotect10min_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        voltprotect10min_sid,
                        force=False,
                    )
                    self._log(f"10min过压保护标准 solarStandard={voltprotect10min_sid}")
                except Exception as exc:
                    self._log(f"10min过压保护标准默认合并跳过: {exc}")
            elif (handler.get("key") or "") == "antibackflow":
                try:
                    from utils.iot_antibackflow_standard import (
                        apply_antibackflow_standard_to_widgets,
                        resolve_antibackflow_standard_id,
                    )

                    antibackflow_sid = resolve_antibackflow_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_antibackflow_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        antibackflow_sid,
                        force=False,
                    )
                    self._log(f"防逆流标准 solarStandard={antibackflow_sid}")
                except Exception as exc:
                    self._log(f"防逆流标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "flicker":
                try:
                    from utils.iot_flicker_standard import (
                        apply_flicker_standard_to_widgets,
                        resolve_flicker_standard_id,
                    )

                    flicker_sid = resolve_flicker_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_flicker_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        flicker_sid,
                        force=False,
                    )
                    self._log(f"flicker标准 solarStandard={flicker_sid}")
                except Exception as exc:
                    self._log(f"flicker标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "frequencyadaptability":
                try:
                    from utils.iot_frequencyadaptability_standard import (
                        apply_frequencyadaptability_standard_to_widgets,
                        resolve_frequencyadaptability_standard_id,
                    )

                    frequencyadaptability_sid = resolve_frequencyadaptability_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_frequencyadaptability_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        frequencyadaptability_sid,
                        force=False,
                    )
                    self._log(f"frequencyadaptability标准 solarStandard={frequencyadaptability_sid}")
                except Exception as exc:
                    self._log(f"frequencyadaptability标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "rocof":
                try:
                    from utils.iot_rocof_standard import (
                        apply_rocof_standard_to_widgets,
                        resolve_rocof_standard_id,
                    )

                    rocof_sid = resolve_rocof_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_rocof_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        rocof_sid,
                        force=False,
                    )
                    self._log(f"rocof标准 solarStandard={rocof_sid}")
                except Exception as exc:
                    self._log(f"rocof标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "guoqianpin_immun":
                try:
                    from utils.iot_guoqianpin_immun_standard import (
                        apply_guoqianpin_immun_standard_to_widgets,
                        resolve_guoqianpin_immun_standard_id,
                    )

                    guoqianpin_immun_sid = resolve_guoqianpin_immun_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_guoqianpin_immun_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        guoqianpin_immun_sid,
                        force=False,
                    )
                    self._log(f"guoqianpin_immun标准 solarStandard={guoqianpin_immun_sid}")
                except Exception as exc:
                    self._log(f"guoqianpin_immun标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "rapidvolt":
                try:
                    from utils.iot_rapidvolt_standard import (
                        apply_rapidvolt_standard_to_widgets,
                        resolve_rapidvolt_standard_id,
                    )

                    rapidvolt_sid = resolve_rapidvolt_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_rapidvolt_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        rapidvolt_sid,
                        force=False,
                    )
                    self._log(f"rapidvolt标准 solarStandard={rapidvolt_sid}")
                except Exception as exc:
                    self._log(f"rapidvolt标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "lvrt":
                try:
                    from utils.iot_lvrt_standard import (
                        apply_lvrt_standard_to_widgets,
                        resolve_lvrt_standard_id,
                    )

                    lvrt_sid = resolve_lvrt_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_lvrt_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        lvrt_sid,
                        force=False,
                    )
                    self._log(f"lvrt标准 solarStandard={lvrt_sid}")
                except Exception as exc:
                    self._log(f"lvrt标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "phasejump":
                try:
                    from utils.iot_phasejump_standard import (
                        apply_phasejump_standard_to_widgets,
                        resolve_phasejump_standard_id,
                    )

                    phasejump_sid = resolve_phasejump_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_phasejump_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        phasejump_sid,
                        force=False,
                    )
                    self._log(f"phasejump标准 solarStandard={phasejump_sid}")
                except Exception as exc:
                    self._log(f"phasejump标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "staticmppt":
                try:
                    from utils.iot_staticmppt_standard import (
                        apply_staticmppt_standard_to_widgets,
                        resolve_staticmppt_standard_id,
                    )

                    staticmppt_sid = resolve_staticmppt_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_staticmppt_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        staticmppt_sid,
                        force=False,
                    )
                    self._log(f"staticmppt标准 solarStandard={staticmppt_sid}")
                except Exception as exc:
                    self._log(f"staticmppt标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "dynamicmppt":
                try:
                    from utils.iot_dynamicmppt_standard import (
                        apply_dynamicmppt_standard_to_widgets,
                        resolve_dynamicmppt_standard_id,
                    )

                    dynamicmppt_sid = resolve_dynamicmppt_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_dynamicmppt_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        dynamicmppt_sid,
                        force=False,
                    )
                    self._log(f"dynamicmppt标准 solarStandard={dynamicmppt_sid}")
                except Exception as exc:
                    self._log(f"dynamicmppt标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "reactiveqcap":
                try:
                    from utils.iot_reactiveqcap_standard import (
                        apply_reactiveqcap_standard_to_widgets,
                        resolve_reactiveqcap_standard_id,
                    )

                    reactiveqcap_sid = resolve_reactiveqcap_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_reactiveqcap_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        reactiveqcap_sid,
                        force=False,
                    )
                    self._log(f"reactiveqcap标准 solarStandard={reactiveqcap_sid}")
                except Exception as exc:
                    self._log(f"reactiveqcap标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "fixedq":
                try:
                    from utils.iot_fixedq_standard import (
                        apply_fixedq_standard_to_widgets,
                        resolve_fixedq_standard_id,
                    )

                    fixedq_sid = resolve_fixedq_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_fixedq_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        fixedq_sid,
                        force=False,
                    )
                    self._log(f"fixedq标准 solarStandard={fixedq_sid}")
                except Exception as exc:
                    self._log(f"fixedq标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "reactiveqin":
                try:
                    from utils.iot_reactiveqin_standard import (
                        apply_reactiveqin_standard_to_widgets,
                        resolve_reactiveqin_standard_id,
                    )

                    reactiveqin_sid = resolve_reactiveqin_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_reactiveqin_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        reactiveqin_sid,
                        force=False,
                    )
                    self._log(f"reactiveqin标准 solarStandard={reactiveqin_sid}")
                except Exception as exc:
                    self._log(f"reactiveqin标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "reactiveqacc":
                try:
                    from utils.iot_reactiveqacc_standard import (
                        apply_reactiveqacc_standard_to_widgets,
                        resolve_reactiveqacc_standard_id,
                    )

                    reactiveqacc_sid = resolve_reactiveqacc_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_reactiveqacc_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        reactiveqacc_sid,
                        force=False,
                    )
                    self._log(f"reactiveqacc标准 solarStandard={reactiveqacc_sid}")
                except Exception as exc:
                    self._log(f"reactiveqacc标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "activep":
                try:
                    from utils.iot_activep_standard import (
                        apply_activep_standard_to_widgets,
                        resolve_activep_standard_id,
                    )

                    activep_sid = resolve_activep_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_activep_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        activep_sid,
                        force=False,
                    )
                    self._log(f"activep标准 solarStandard={activep_sid}")
                except Exception as exc:
                    self._log(f"activep标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "staticqu":
                try:
                    from utils.iot_staticqu_standard import (
                        apply_staticqu_standard_to_widgets,
                        resolve_staticqu_standard_id,
                    )

                    staticqu_sid = resolve_staticqu_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_staticqu_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        staticqu_sid,
                        force=False,
                    )
                    self._log(f"staticqu标准 solarStandard={staticqu_sid}")
                except Exception as exc:
                    self._log(f"staticqu标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "dynamicqu":
                try:
                    from utils.iot_dynamicqu_standard import (
                        apply_dynamicqu_standard_to_widgets,
                        resolve_dynamicqu_standard_id,
                    )

                    dynamicqu_sid = resolve_dynamicqu_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_dynamicqu_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        dynamicqu_sid,
                        force=False,
                    )
                    self._log(f"dynamicqu标准 solarStandard={dynamicqu_sid}")
                except Exception as exc:
                    self._log(f"dynamicqu标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "testpu":
                try:
                    from utils.iot_testpu_standard import (
                        apply_testpu_standard_to_widgets,
                        resolve_testpu_standard_id,
                    )

                    testpu_sid = resolve_testpu_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_testpu_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        testpu_sid,
                        force=False,
                    )
                    self._log(f"testpu标准 solarStandard={testpu_sid}")
                except Exception as exc:
                    self._log(f"testpu标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "staticcosphi":
                try:
                    from utils.iot_staticcosphi_standard import (
                        apply_staticcosphi_standard_to_widgets,
                        resolve_staticcosphi_standard_id,
                    )

                    staticcosphi_sid = resolve_staticcosphi_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_staticcosphi_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        staticcosphi_sid,
                        force=False,
                    )
                    self._log(f"staticcosphi标准 solarStandard={staticcosphi_sid}")
                except Exception as exc:
                    self._log(f"staticcosphi标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "dynamiccosphi":
                try:
                    from utils.iot_dynamiccosphi_standard import (
                        apply_dynamiccosphi_standard_to_widgets,
                        resolve_dynamiccosphi_standard_id,
                    )

                    dynamiccosphi_sid = resolve_dynamiccosphi_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_dynamiccosphi_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        dynamiccosphi_sid,
                        force=False,
                    )
                    self._log(f"dynamiccosphi标准 solarStandard={dynamiccosphi_sid}")
                except Exception as exc:
                    self._log(f"dynamiccosphi标准默认合并跳过: {exc}")


            elif (handler.get("key") or "") == "cosphibrazil":
                try:
                    from utils.iot_cosphibrazil_standard import (
                        apply_cosphibrazil_standard_to_widgets,
                        resolve_cosphibrazil_standard_id,
                    )

                    cosphibrazil_sid = resolve_cosphibrazil_standard_id(
                        params=params if isinstance(params, dict) else {},
                        widgets=widgets if isinstance(widgets, dict) else {},
                    )
                    widgets = apply_cosphibrazil_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {},
                        cosphibrazil_sid,
                        force=False,
                    )
                    self._log(f"cosphibrazil标准 solarStandard={cosphibrazil_sid}")
                except Exception as exc:
                    self._log(f"cosphibrazil标准默认合并跳过: {exc}")

            widgets_for_ui = {
                k: v
                for k, v in (widgets or {}).items()
                if k not in ("dew_export_fields", "solarStandard", "solar_standard", "standard")
                and not str(k).startswith("_")
            }
            # 闪变/谐波/固定PF/直流分量/过载/重连/过欠压_过欠频/过频降载 Dialog 用 radio_wt3000；线上表单写 radio_wt
            if (handler.get("key") or "") in (
                "flicker",
                "harmonic",
                "fixedpf",
                "dccomponent",
                "overload",
                "reconnect",
                "ovuf",
                "guopinjiangzai",
                "qianpinshengzai",
                "voltprotect10min",
                "antibackflow",
                "guoqianpin_immun",
                "staticmppt",
                "frequencyadaptability",
                "voltageadaptability",
                "rocof",
                "rapidvolt",
                "lvrt",
                "phasejump",
                "dynamicmppt",
                "reactiveqcap",
                "fixedq",
                "reactiveqin",
                "reactiveqacc",
                "activep",
                "staticqu",
                "dynamicqu",
                "testpu",
                "staticcosphi",
                "dynamiccosphi",
                "cosphibrazil",
            ) and isinstance(widgets_for_ui, dict):
                if "radio_wt3000" not in widgets_for_ui and "radio_wt" in widgets_for_ui:
                    widgets_for_ui = {**widgets_for_ui, "radio_wt3000": widgets_for_ui.get("radio_wt")}
                try:
                    from utils.iot_boot_params_sync import fill_missing_phase_volts

                    widgets_for_ui = fill_missing_phase_volts(widgets_for_ui)
                except Exception:
                    pass
            _wt_apply_payload = widgets_for_ui
            # 过欠压连续录：IOT 常残留 textEdit_StopTime=00:05:00；若写进 Soft Panel，
            # ASYNC 重算失败时 Soft Panel 停表会显示「约步数×0.3s≈21s」或空等 5 分钟，
            # 试验员易把停表当成「数据采集」。StopTime 改由 Append/ASYNC 按扫段重算。
            if (handler.get("key") or "") == "ovuf" and isinstance(widgets_for_ui, dict):
                _stale_stop = str(widgets_for_ui.get("textEdit_StopTime") or "").strip()
                if _stale_stop:
                    widgets_for_ui = {**widgets_for_ui, "textEdit_StopTime": ""}
                    self._log(
                        f"过欠压: 忽略 IOT StopTime={_stale_stop!r}，"
                        "由 Append/ASYNC 按扫段驻留重算"
                    )
            try:
                from utils.wt_job_save import prepare_wt_save_widgets, widgets_for_standard_apply

                if isinstance(widgets_for_ui, dict):
                    _before_path = str(widgets_for_ui.get("textEdit_SavePath") or "").strip()
                    widgets_for_ui = prepare_wt_save_widgets(
                        widgets_for_ui,
                        str(handler.get("key") or ""),
                    )
                    _after_path = str(widgets_for_ui.get("textEdit_SavePath") or "").strip()
                    if _before_path and _after_path and _before_path != _after_path:
                        self._log(f"WT 保存目录已就绪: {_before_path} -> {_after_path}")
                    _wt_apply_payload = widgets_for_standard_apply(real_ui, widgets_for_ui)
                else:
                    _wt_apply_payload = widgets_for_ui
            except Exception as _wt_save_exc:
                self._log(f"WT 保存设置预处理跳过: {_wt_save_exc}")
                _wt_apply_payload = widgets_for_ui
            missing = apply_widget_values(real_ui, _wt_apply_payload)
            if missing:
                self._log(f"部分控件未写入: {missing[:12]}")
            # 过欠压：关键字段强制对齐 + 钉死字段记忆，避免 Dialog 仍显示 181.7 / 11 秒
            # 以 IOT job.widgets 为准（勿用可能被 WT 预处理裁掉的 payload）
            if (handler.get("key") or "") == "ovuf" and isinstance(widgets, dict) and widgets:
                try:
                    from utils.iot_ovuf_apply import apply_ovuf_critical_widgets

                    still_bad = apply_ovuf_critical_widgets(
                        real_ui, widgets, log=self._log, rounds=2
                    )
                except Exception as _rb_exc:
                    self._log(f"过欠压强制写入跳过: {_rb_exc}")
                    still_bad = ["__apply_exc__"]
                if still_bad:
                    self._write_result_all(
                        pending_path,
                        job_id,
                        {
                            "status": "failed",
                            "fail_reason": (
                                "过欠压关键字段写入后回读不一致，已中止以免本机旧值进扫段: "
                                + ",".join(str(x) for x in still_bad[:12])
                            )[:500],
                            "result_summary": {
                                "handoff": True,
                                "appended": False,
                                "started": False,
                                "missingWidgets": missing,
                                "ovuf_mismatch": list(still_bad)[:20],
                            },
                        },
                    )
                    self._move_pending_done(pending_path)
                    return
            try:
                from utils.wt_job_save import apply_wt_save_to_dialog

                if isinstance(widgets_for_ui, dict):
                    apply_wt_save_to_dialog(real_ui, widgets_for_ui)
            except Exception as _wt_apply_exc:
                self._log(f"WT 保存设置写入跳过: {_wt_apply_exc}")

            # 重连等试验：Dialog 写完后同步 Soft Panel 交流相数/直流 IV（仅界面）。
            # 开测交接禁止在此下真机：后面 Append 的 S1 会发同一套 VOLT/FREQ/IV，
            # 否则日志里会出现开头 AC/DC 命令打两遍。
            try:
                sync_fn = getattr(self, "device_sync_boot_params", None)
                if callable(sync_fn) and isinstance(widgets_for_ui, dict) and widgets_for_ui:
                    try:
                        sync_fn(widgets_for_ui, apply_to_device=False)
                    except TypeError:
                        sync_fn(widgets_for_ui)
            except Exception as sync_exc:
                self._log(f"Soft Panel 启机参数同步跳过: {sync_exc}")

            # 闪变/谐波/直流分量/固定PF/过载/重连/过欠压_过欠频/过频降载/欠频升载：挂标准到 Dialog 并同步下拉（不重写已填 widgets）
            if (handler.get("key") or "") == "flicker" and real_ui is not None:
                try:
                    from utils.iot_flicker_standard import flicker_cycle_seconds

                    sid = flicker_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                        setattr(
                            real_ui,
                            "_flicker_cycle_sec",
                            flicker_cycle_seconds(
                                sid, widgets if isinstance(widgets, dict) else {}
                            ),
                        )
                except Exception as exc:
                    self._log(f"闪变标准挂载 Dialog 跳过: {exc}")
            elif (handler.get("key") or "") == "harmonic" and real_ui is not None:
                try:
                    sid = harmonic_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"谐波标准挂载 Dialog 跳过: {exc}")
            elif (handler.get("key") or "") == "dccomponent" and real_ui is not None:
                try:
                    sid = dccomponent_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"直流分量标准挂载 Dialog 跳过: {exc}")
            elif (handler.get("key") or "") == "fixedpf" and real_ui is not None:
                try:
                    sid = fixedpf_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"固定PF标准挂载 Dialog 跳过: {exc}")
            elif (handler.get("key") or "") == "overload" and real_ui is not None:
                try:
                    sid = overload_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"过载标准挂载 Dialog 跳过: {exc}")
            elif (handler.get("key") or "") == "reconnect" and real_ui is not None:
                try:
                    sid = reconnect_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"重连标准挂载 Dialog 跳过: {exc}")
            elif (handler.get("key") or "") == "ovuf" and real_ui is not None:
                try:
                    sid = ovuf_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"过欠压_过欠频标准挂载 Dialog 跳过: {exc}")
            elif (handler.get("key") or "") == "guopinjiangzai" and real_ui is not None:
                try:
                    sid = guopinjiangzai_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"过频降载标准挂载 Dialog 跳过: {exc}")
            elif (handler.get("key") or "") == "qianpinshengzai" and real_ui is not None:
                try:
                    sid = qianpinshengzai_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"欠频升载标准挂载 Dialog 跳过: {exc}")
            elif (handler.get("key") or "") == "voltageadaptability" and real_ui is not None:
                try:
                    sid = voltageadaptability_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"电压适应性标准挂载 Dialog 跳过: {exc}")
            elif (handler.get("key") or "") == "voltprotect10min" and real_ui is not None:
                try:
                    sid = voltprotect10min_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"10min过压保护标准挂载 Dialog 跳过: {exc}")
            elif (handler.get("key") or "") == "antibackflow" and real_ui is not None:
                try:
                    sid = antibackflow_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"防逆流标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "flicker" and real_ui is not None:
                try:
                    sid = flicker_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"flicker标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "frequencyadaptability" and real_ui is not None:
                try:
                    sid = frequencyadaptability_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"frequencyadaptability标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "rocof" and real_ui is not None:
                try:
                    sid = rocof_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"rocof标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "guoqianpin_immun" and real_ui is not None:
                try:
                    sid = guoqianpin_immun_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"guoqianpin_immun标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "rapidvolt" and real_ui is not None:
                try:
                    sid = rapidvolt_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"rapidvolt标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "lvrt" and real_ui is not None:
                try:
                    sid = lvrt_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"lvrt标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "phasejump" and real_ui is not None:
                try:
                    sid = phasejump_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"phasejump标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "staticmppt" and real_ui is not None:
                try:
                    sid = staticmppt_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"staticmppt标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "dynamicmppt" and real_ui is not None:
                try:
                    sid = dynamicmppt_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"dynamicmppt标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "reactiveqcap" and real_ui is not None:
                try:
                    sid = reactiveqcap_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"reactiveqcap标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "fixedq" and real_ui is not None:
                try:
                    sid = fixedq_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"fixedq标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "reactiveqin" and real_ui is not None:
                try:
                    sid = reactiveqin_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"reactiveqin标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "reactiveqacc" and real_ui is not None:
                try:
                    sid = reactiveqacc_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"reactiveqacc标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "activep" and real_ui is not None:
                try:
                    sid = activep_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"activep标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "staticqu" and real_ui is not None:
                try:
                    sid = staticqu_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"staticqu标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "dynamicqu" and real_ui is not None:
                try:
                    sid = dynamicqu_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"dynamicqu标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "testpu" and real_ui is not None:
                try:
                    sid = testpu_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"testpu标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "staticcosphi" and real_ui is not None:
                try:
                    sid = staticcosphi_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"staticcosphi标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "dynamiccosphi" and real_ui is not None:
                try:
                    sid = dynamiccosphi_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"dynamiccosphi标准挂载 Dialog 跳过: {exc}")


            elif (handler.get("key") or "") == "cosphibrazil" and real_ui is not None:
                try:
                    sid = cosphibrazil_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"cosphibrazil标准挂载 Dialog 跳过: {exc}")

            # 德威创导出字段：不在标准控件树里，单独写入面板
            try:
                raw_fields = None
                if isinstance(widgets, dict):
                    raw_fields = widgets.get("dew_export_fields")
                if raw_fields is not None and hasattr(real_ui, "set_checked_export_fields"):
                    if isinstance(raw_fields, str):
                        field_list = [x.strip() for x in raw_fields.replace("，", ",").split(",") if x.strip()]
                    elif isinstance(raw_fields, (list, tuple)):
                        field_list = [str(x).strip() for x in raw_fields if str(x).strip()]
                    else:
                        field_list = []
                    if field_list:
                        real_ui.set_checked_export_fields(field_list)
                        self._log(f"德威创导出字段已写入 {len(field_list)} 项")
                # 切到德威创模式
                if isinstance(widgets, dict) and (
                    widgets.get("radio_dewetron") in (True, "1", 1, "true", "True")
                ):
                    radio = getattr(real_ui, "radio_dewetron", None)
                    if radio is not None and hasattr(radio, "setChecked"):
                        radio.setChecked(True)
                        try:
                            radio.click()
                        except Exception:
                            pass
                    # IOT 开测勾选 ↔ 桌面试验页同名控件：刷新率/小数位/波形/绝对时间/原始录波/路径
                    try:
                        from utils.dewetron_widget_apply import apply_dewetron_panel_widgets

                        applied = apply_dewetron_panel_widgets(real_ui, widgets)
                        ok = [k for k, v in (applied or {}).items() if v]
                        if ok:
                            self._log("德威创试验面板已同步: " + ",".join(ok))
                    except Exception as exc:
                        self._log(f"德威创试验面板同步跳过: {exc}")
                    # 比例系数等到设置页（试验页无比例输入框）
                    apply_dew = getattr(self, "device_apply_dew_widgets", None)
                    if callable(apply_dew) and (
                        isinstance(widgets.get("dew_channel_scales"), dict)
                        or widgets.get("comboBox_DEW_MaxRefreshRate")
                        or widgets.get("comboBox_maxRefreshRate")
                        or widgets.get("lineEdit_DEW_SaveDir") is not None
                        or widgets.get("checkBox_DEW_ExportAbsTime") is not None
                        or widgets.get("checkBox_DEW_KeepOxygenDmd") is not None
                    ):
                        try:
                            apply_dew(widgets)
                            self._log("德威创设置页/比例已按开测勾选同步")
                        except Exception as exc:
                            self._log(f"德威创设置页同步跳过: {exc}")

                elif (handler.get("key") or "") in (
                    "flicker",
                    "harmonic",
                    "fixedpf",
                    "dccomponent",
                    "reconnect",
                    "ovuf",
                    "guopinjiangzai",
                    "qianpinshengzai",
                    "voltprotect10min",
                    "guoqianpin_immun",
                    "staticmppt",
                    "frequencyadaptability",
                    "voltageadaptability",
                    "rocof",
                    "rapidvolt",
                    "lvrt",
                    "phasejump",
                    "dynamicmppt",
                    "reactiveqcap",
                    "fixedq",
                    "reactiveqin",
                    "reactiveqacc",
                    "activep",
                    "staticqu",
                    "dynamicqu",
                    "testpu",
                    "staticcosphi",
                    "dynamiccosphi",
                    "cosphibrazil",
                ) and isinstance(widgets, dict):
                    # WT 模式：点选 radio_wt3000
                    use_wt = widgets.get("radio_wt") in (True, "1", 1, "true", "True") or widgets.get(
                        "radio_wt3000"
                    ) in (True, "1", 1, "true", "True")
                    if use_wt:
                        radio = getattr(real_ui, "radio_wt3000", None)
                        if radio is not None and hasattr(radio, "setChecked"):
                            radio.setChecked(True)
                            try:
                                radio.click()
                            except Exception:
                                pass
            except Exception as exc:
                self._log(f"德威创面板写入跳过: {exc}")

            from utils.iot_force_overwrite_append import coerce_auto_append, coerce_auto_start

            auto_append = coerce_auto_append(params if isinstance(params, dict) else None)
            auto_start = coerce_auto_start(params if isinstance(params, dict) else None)
            wait_finish = True
            if isinstance(params, dict) and "wait_finish" in params:
                src = str(params.get("source") or "").strip().lower()
                # 实验管理开测必须等结束，禁止被本地记忆改成 false
                if src not in ("experiment_start", "exper_start", "blockly_start"):
                    wait_finish = bool(params.get("wait_finish"))

            self._job_ctx = {
                "job": job,
                "pending_path": pending_path,
                "job_id": job_id,
                "test_type": test_type,
                "handler": handler,
                "real_ui": real_ui,
                "missing": missing,
                "auto_append": auto_append,
                "auto_start": auto_start,
                "wait_finish": wait_finish,
                "params": params,
                # 供 _continue_job_after_connect 写入 _awaiting（该方法不在本作用域）
                "widgets": dict(widgets) if isinstance(widgets, dict) else {},
            }

            cloud_inst = None
            if isinstance(params, dict):
                raw_inst = params.get("instruments")
                if isinstance(raw_inst, list) and raw_inst:
                    cloud_inst = raw_inst

            def _cloud_slots_missing() -> list:
                """云端配了但本机会话未建的槽位（常见：AC/DC 已连、WT 未连被误跳过）。"""
                missing_slots = []
                if not cloud_inst or not self.session_ok:
                    return missing_slots
                for item in cloud_inst:
                    if not isinstance(item, dict):
                        continue
                    slot = str(item.get("slot") or "").strip().lower()
                    if not slot:
                        continue
                    try:
                        ok = bool(self.session_ok(slot))
                    except Exception:
                        ok = False
                    if not ok:
                        missing_slots.append(slot)
                return missing_slots

            # 已连好则跳过扫连，避免主线程卡在 TCP/SCPI 探测
            if self.ensure_ready:
                try:
                    ready_ok, _ready_reason = self.ensure_ready(real_ui, test_type)
                except Exception:
                    ready_ok = False
                missing_cloud = _cloud_slots_missing()
                if ready_ok and missing_cloud:
                    ready_ok = False
                    self._log(
                        "AC/DC 看似就绪，但云端仪器仍有未连接槽位: "
                        + ",".join(missing_cloud)
                        + "，继续自动连"
                    )
                if ready_ok:
                    self._log("设备已就绪，跳过自动扫连")
                    self._continue_job_after_connect(None)
                    return

            if cloud_inst and self.apply_auto_connect:
                self._log("按 IOT 下发的仪器配置连接（后台探测计划）…")
                import threading

                def _worker_cloud():
                    prepared = None
                    err = None
                    try:
                        from utils.iot_auto_connect import prepare_jobs_from_cloud_instruments

                        from utils.iot_auto_connect import job_wants_dewetron

                        jobs = prepare_jobs_from_cloud_instruments(cloud_inst)
                        had_cloud_jobs = bool(jobs)
                        want_dew = job_wants_dewetron(
                            widgets=widgets, params=params, instruments=cloud_inst
                        )
                        # 已连槽位不再点 Connect（按钮文案是「取消连接」会误断开）
                        if self.session_ok and jobs:
                            filtered = []
                            for slot, plan, dev in jobs:
                                try:
                                    already = bool(self.session_ok(str(slot or "")))
                                except Exception:
                                    already = False
                                if already:
                                    continue
                                filtered.append((slot, plan, dev))
                            jobs = filtered
                        # WT 试验勿强连德威创（台架仪器表常残留 dew，失败弹窗会卡死开测）
                        if not want_dew and jobs:
                            before = len(jobs)
                            jobs = [
                                (s, p, d)
                                for s, p, d in jobs
                                if str(s or "").strip().lower() != "dew"
                            ]
                            if len(jobs) < before:
                                self._log("本试验为 WT 模式，已跳过德威创自动连接")

                        # 云端常把 WT 写成 pending:wt（会被丢掉），AC/DC 有地址时不会整单回退；
                        # 功率分析仪模式且本机未连 WT 时，只补扫本机 wt 槽位。
                        want_wt = False
                        for item in cloud_inst or []:
                            if not isinstance(item, dict):
                                continue
                            if str(item.get("slot") or "").strip().lower() == "wt":
                                want_wt = True
                                break
                        # 德威创试验的 checkBox_S2 只是步骤开关，不能据此去补扫 WT
                        if want_dew:
                            want_wt = False
                        elif isinstance(widgets, dict):
                            if widgets.get("checkBox_S2") in (True, "1", 1, "true", "True"):
                                want_wt = True
                            if widgets.get("radio_wt") in (True, "1", 1, "true", "True") or widgets.get(
                                "radio_wt3000"
                            ) in (True, "1", 1, "true", "True"):
                                want_wt = True
                        if not want_dew:
                            want_wt = True
                        wt_ok = False
                        try:
                            wt_ok = bool(self.session_ok("wt")) if self.session_ok else False
                        except Exception:
                            wt_ok = False
                        has_wt_job = any(
                            str(slot or "").strip().lower() == "wt" for slot, _p, _d in (jobs or [])
                        )
                        if (
                            want_wt
                            and not wt_ok
                            and not has_wt_job
                            and self.prepare_auto_connect
                        ):
                            try:
                                local_jobs, local_devs = self.prepare_auto_connect()
                                local_jobs = local_jobs or []
                                wt_only = [
                                    (s, p, d)
                                    for s, p, d in local_jobs
                                    if str(s or "").strip().lower() == "wt"
                                ]
                                if wt_only:
                                    jobs = list(jobs or []) + wt_only
                                    self._log("云端无有效 WT 地址，已本机补扫功率分析仪")
                                    prepared = (jobs, local_devs or [])
                                else:
                                    prepared = (jobs, [])
                            except Exception as wt_exc:
                                self._log(f"本机补扫 WT 失败: {wt_exc}")
                                prepared = (jobs, [])
                        else:
                            prepared = (jobs, [])

                        if not had_cloud_jobs and not (prepared and prepared[0]):
                            err = ValueError("云端仪器配置无有效槽位/地址，将尝试本机扫连")
                        # had_cloud_jobs 但过滤后为空：全部已连，正常跳过连接
                    except Exception as exc:
                        err = exc
                    if err is not None and prepared and prepared[0]:
                        err = None
                    try:
                        if err is not None and not (prepared and prepared[0]):
                            # 回退本机扫连（仍跳过德威创，除非试验明确要）
                            if self.prepare_auto_connect:
                                try:
                                    prepared = self.prepare_auto_connect()
                                    err = None
                                    self._log("云端配置无效，已回退本机扫连计划")
                                except Exception as exc2:
                                    err = exc2
                        # 回退计划里再滤一次 dew
                        try:
                            from utils.iot_auto_connect import job_wants_dewetron as _want_dew

                            if (
                                prepared
                                and isinstance(prepared, tuple)
                                and prepared[0]
                                and not _want_dew(
                                    widgets=widgets, params=params, instruments=cloud_inst
                                )
                            ):
                                jobs2 = [
                                    (s, p, d)
                                    for s, p, d in (prepared[0] or [])
                                    if str(s or "").strip().lower() != "dew"
                                ]
                                prepared = (jobs2, prepared[1] if len(prepared) > 1 else [])
                        except Exception:
                            pass
                        self._auto_connect_finished.emit(prepared, err)
                    except Exception:
                        QTimer.singleShot(
                            0, lambda: self._on_auto_connect_finished(prepared, err)
                        )

                threading.Thread(
                    target=_worker_cloud, name="iot-handoff-cloud-connect", daemon=True
                ).start()
                return

            if self.prepare_auto_connect and self.apply_auto_connect:
                self._log("后台探测设备（不阻塞界面）…")
                import threading

                def _worker():
                    prepared = None
                    err = None
                    try:
                        prepared = self.prepare_auto_connect()
                    except Exception as exc:
                        err = exc
                    try:
                        self._auto_connect_finished.emit(prepared, err)
                    except Exception:
                        QTimer.singleShot(
                            0, lambda: self._on_auto_connect_finished(prepared, err)
                        )

                threading.Thread(target=_worker, name="iot-handoff-autoconnect", daemon=True).start()
                return

            if self.auto_connect:
                self._log("后台自动连接设备（不阻塞界面）…")
                import threading

                def _worker2():
                    summary = None
                    err = None
                    try:
                        summary = self.auto_connect()
                    except Exception as exc:
                        err = exc
                    try:
                        self._auto_connect_finished.emit(summary, err)
                    except Exception:
                        QTimer.singleShot(
                            0, lambda: self._on_auto_connect_finished(summary, err)
                        )

                threading.Thread(target=_worker2, name="iot-handoff-autoconnect", daemon=True).start()
                return

            self._continue_job_after_connect(None)
            return
        except Exception as exc:
            self._log(f"处理失败: {exc}\n{traceback.format_exc()}")
            self._awaiting = None
            self._job_ctx = None
            try:
                self._write_result_all(
                    pending_path,
                    job_id,
                    {"status": "failed", "fail_reason": str(exc)[:500]},
                )
            except Exception:
                pass
        finally:
            # 等后台探测 / 等试验结束时不释放
            if not self._awaiting and self._job_ctx is None:
                self._busy = False
                try:
                    from agent.ui_mutex import ui_release

                    ui_release(repo_root=self.repo_root)
                except Exception:
                    pass

    def _on_auto_connect_finished(self, prepared: Any, err: Any) -> None:
        if err is not None:
            self._log(f"自动连接探测异常（尽力继续）: {err}")
            self._continue_job_after_connect(None)
            return
        from utils.iot_remote_ui import silent_remote_connect

        # prepare 返回 (jobs, devices) 时在主线程 apply；静默连接，禁止德威创失败模态框挡试验
        if self.apply_auto_connect and prepared is not None and not isinstance(prepared, dict):
            try:
                with silent_remote_connect():
                    summary = self.apply_auto_connect(prepared)
                self._log(f"自动连接结果: {_format_auto_connect_summary(summary)}")
            except Exception as exc:
                self._log(f"自动连接执行异常（尽力继续）: {exc}")
                summary = None
        elif isinstance(prepared, dict):
            self._log(f"自动连接结果: {_format_auto_connect_summary(prepared)}")
            summary = prepared
        else:
            summary = prepared
        self._continue_job_after_connect(summary)

    def _continue_job_after_connect(self, _summary: Any) -> None:
        from agent.ui_mutex import ui_release

        ctx = self._job_ctx
        if not ctx:
            self._busy = False
            return
        job = ctx["job"]
        pending_path = ctx["pending_path"]
        job_id = int(ctx["job_id"])
        test_type = ctx["test_type"]
        handler = ctx["handler"]
        real_ui = ctx["real_ui"]
        missing = ctx.get("missing") or []
        auto_append = bool(ctx.get("auto_append", True))
        auto_start = bool(ctx.get("auto_start", False))
        wait_finish = bool(ctx.get("wait_finish", True))
        params = ctx.get("params") or {}
        widgets = ctx.get("widgets") if isinstance(ctx.get("widgets"), dict) else {}
        if not widgets and isinstance(params, dict):
            raw_w = params.get("widgets")
            widgets = dict(raw_w) if isinstance(raw_w, dict) else {}

        try:
            # 自动连接后再同步 Soft Panel AC/DC 界面；真机由试验队列 S1 下发，
            # 避免「交接 live 下发 + RunProject」把 VOLT/FREQ/SAS 打两遍。
            try:
                sync_fn = getattr(self, "device_sync_boot_params", None)
                if callable(sync_fn) and isinstance(widgets, dict) and widgets:
                    try:
                        sync_fn(widgets, apply_to_device=False)
                    except TypeError:
                        sync_fn(widgets)
                    self._log("连接后已同步 Soft Panel 交流相数/直流 IV（仅界面）")
            except Exception as sync_exc:
                self._log(f"连接后 Soft Panel 同步跳过: {sync_exc}")

            if self.ensure_ready:
                try:
                    ready_ok, ready_reason = self.ensure_ready(real_ui, test_type)
                except Exception as exc:
                    ready_ok, ready_reason = False, f"设备就绪检查异常: {exc}"
                if not ready_ok:
                    self._write_result_all(
                        pending_path,
                        job_id,
                        {
                            "status": "failed",
                            "fail_reason": str(ready_reason or "设备未就绪"),
                            "result_summary": {
                                "handoff": True,
                                "appended": False,
                                "started": False,
                                "missingWidgets": missing,
                                "ready_check": False,
                            },
                        },
                    )
                    self._move_pending_done(pending_path)
                    return

            try:
                from utils.instrument_catalog_bootstrap import bootstrap_instrument_catalogs

                bootstrap_instrument_catalogs()
            except Exception:
                self._log("设备命令库 bootstrap（追加前）跳过")

            appended = False
            desktop_running = False
            project_append = handler.get("append")
            if auto_append and project_append:
                # Append 前再钉一次过欠压关键字段（连接/就绪检查期间 Dialog 可能被 polish 盖回旧值）
                if (handler.get("key") or "") == "ovuf" and isinstance(widgets, dict) and widgets:
                    try:
                        from utils.iot_ovuf_apply import apply_ovuf_critical_widgets

                        still_bad = apply_ovuf_critical_widgets(
                            real_ui, widgets, log=self._log, rounds=2
                        )
                    except Exception as _pre_exc:
                        self._log(f"追加前过欠压强制写入跳过: {_pre_exc}")
                        still_bad = ["__apply_exc__"]
                    if still_bad:
                        # 禁止带着 181.7/11 等脏 Dialog 生成命令
                        self._write_result_all(
                            pending_path,
                            job_id,
                            {
                                "status": "failed",
                                "fail_reason": (
                                    "过欠压关键字段写入后回读不一致，已中止追加以免用本机旧值跑扫段: "
                                    + ",".join(str(x) for x in still_bad[:12])
                                )[:500],
                                "result_summary": {
                                    "handoff": True,
                                    "appended": False,
                                    "started": False,
                                    "missingWidgets": missing,
                                    "ovuf_mismatch": list(still_bad)[:20],
                                },
                            },
                        )
                        self._move_pending_done(pending_path)
                        return
                # 队列已空且自动开跑：覆盖，防残留计数叠第二套。
                # 桌面已追加（队列非空）或本机已在跑：保留队列，交给 apply_append_mode。
                from utils.iot_force_overwrite_append import (
                    force_overwrite_before_iot_append,
                    should_force_overwrite_for_iot_job,
                )
                from utils.iot_local_run import bench_is_running, desktop_queue_nonempty

                desktop_running = bench_is_running(self._read_run_status())
                queue_nonempty = desktop_queue_nonempty()
                do_overwrite = should_force_overwrite_for_iot_job(
                    auto_start=auto_start,
                    desktop_running=desktop_running,
                    queue_nonempty=queue_nonempty,
                )
                if do_overwrite:
                    try:
                        ow_ok = force_overwrite_before_iot_append(
                            reset_count=self.reset_append_count,
                            log=self._log,
                        )
                    except Exception as _ow_exc:
                        self._log(f"IOT 追加前强制覆盖异常: {_ow_exc}")
                        ow_ok = False
                    if not ow_ok:
                        self._write_result_all(
                            pending_path,
                            job_id,
                            {
                                "status": "failed",
                                "fail_reason": "云开测追加前强制覆盖失败，已中止以免叠第二套命令",
                                "result_summary": {
                                    "handoff": True,
                                    "appended": False,
                                    "started": False,
                                    "missingWidgets": missing,
                                    "force_overwrite_failed": True,
                                },
                            },
                        )
                        self._move_pending_done(pending_path)
                        return
                else:
                    self._log(
                        "保留现有命令队列（桌面已追加或只追加；跨项/同项由 apply_append_mode 判定）"
                    )
                append_mode_label = "覆盖模式" if do_overwrite else "保留队列追加"

                def _invoke_project_append() -> None:
                    if self.wrap_append_errors:
                        fail_msg, append_err = _append_with_message_capture(project_append)
                        if fail_msg or append_err:
                            raise RuntimeError(fail_msg or str(append_err))
                    else:
                        project_append()

                # 双路径：默认 dialog_append；仅显式 blockly_interpret 才进解释器。
                # 未勾选 / 非 OVUF / 解释失败 → 原样 Append，不破坏现网。
                used_blockly = False
                try:
                    from utils.iot_blockly_interpreter import try_run_blockly_interpret

                    handled, _msg, _detail = try_run_blockly_interpret(
                        ui=real_ui,
                        test_type=str(handler.get("key") or test_type or ""),
                        params=params if isinstance(params, dict) else {},
                        append_fn=_invoke_project_append,
                        log=self._log,
                        apply_widget_values=apply_widget_values,
                    )
                    used_blockly = bool(handled)
                    if handled:
                        appended = bool((_detail or {}).get("appended"))
                        self._log(
                            f"blockly_interpret handled msg={_msg} "
                            f"appended={appended} detail_keys={list((_detail or {}).keys())}"
                        )
                        # fallbackDialogAppend=False 且未追加：勿当成成功继续开测
                        if not appended and (params or {}).get("fallbackDialogAppend") is False:
                            self._write_result_all(
                                pending_path,
                                job_id,
                                {
                                    "status": "failed",
                                    "fail_reason": (
                                        f"blockly_interpret 未追加且禁止回退 Append: {_msg}"
                                    )[:500],
                                    "result_summary": {
                                        "handoff": True,
                                        "appended": False,
                                        "started": False,
                                        "blockly_interpret": True,
                                        "missingWidgets": missing,
                                    },
                                },
                            )
                            self._move_pending_done(pending_path)
                            return
                except Exception as _bi_exc:
                    self._log(f"blockly_interpret 分支异常，改走 Append: {_bi_exc}")
                    used_blockly = False

                if not used_blockly:
                    try:
                        _invoke_project_append()
                        appended = True
                        self._log(f"已调用{handler['label']}追加（{append_mode_label}）")
                    except Exception as append_exc:
                        reason = str(append_exc)
                        self._write_result_all(
                            pending_path,
                            job_id,
                            {
                                "status": "failed",
                                "fail_reason": reason[:500],
                                "result_summary": {
                                    "handoff": True,
                                    "appended": False,
                                    "started": False,
                                    "missingWidgets": missing,
                                    "append_error": True,
                                },
                            },
                        )
                        self._move_pending_done(pending_path)
                        return
                elif appended:
                    self._log(
                        f"已按积木解释追加{handler['label']}（{append_mode_label}）"
                    )

            if desktop_running:
                if not appended:
                    self._write_result_all(
                        pending_path,
                        job_id,
                        {
                            "status": "failed",
                            "fail_reason": "本机正在执行，且本次没有追加进队列",
                            "result_summary": {
                                "handoff": True,
                                "appended": False,
                                "started": False,
                                "desktop_running": True,
                                "missingWidgets": missing,
                            },
                        },
                    )
                    self._move_pending_done(pending_path)
                    return
                # 追加进正在跑的队列后必须等本机真正跑完，不能立刻 success（否则秒结束）
                if wait_finish and self.get_run_status:
                    self._awaiting = {
                        "job_id": job_id,
                        "pending_path": pending_path,
                        "appended": True,
                        "missing": missing,
                        "started_at": time.time(),
                        "start_grace_sec": 20,
                        "timeout_sec": 7200,
                        "seen_running": False,
                        "desktop_finished": False,
                        "joined_running_queue": True,
                        "max_cmd_index": 0,
                        "max_cmd_total": 0,
                        "test_type": test_type,
                        "handler": {
                            "project_name": str((handler or {}).get("project_name") or ""),
                            "key": str((handler or {}).get("key") or test_type),
                            "label": str((handler or {}).get("label") or ""),
                        },
                    }
                    self._log("本机正在执行，IOT 追加已并入当前队列，等待本机跑完再结案")
                    self._emit_progress(job_id, force=True)
                    self._check_awaiting_finish()
                    return
                self._write_result_all(
                    pending_path,
                    job_id,
                    {
                        "status": "success",
                        "fail_reason": "",
                        "result_summary": {
                            "handoff": True,
                            "appended": True,
                            "started": False,
                            "desktop_running": True,
                            "joined_running_queue": True,
                            "missingWidgets": missing,
                            "note": "命令已接在正在执行的队列后，未等待结束",
                        },
                    },
                )
                self._move_pending_done(pending_path)
                self._log("本机正在执行，IOT 追加已并入当前队列（未等待结束）")
                return

            if auto_start:
                if not self.start_test:
                    self._write_result_all(
                        pending_path,
                        job_id,
                        {
                            "status": "failed",
                            "fail_reason": "已勾选自动开跑，但本机未绑定开始试验回调",
                            "result_summary": {"appended": appended},
                        },
                    )
                    self._move_pending_done(pending_path)
                    return
                # 追加弹窗未捕获时仍可能空队列；开跑前再确认，避免「无可执行命令」
                try:
                    from utils.iot_local_run import desktop_queue_nonempty

                    if appended and not desktop_queue_nonempty():
                        self._write_result_all(
                            pending_path,
                            job_id,
                            {
                                "status": "failed",
                                "fail_reason": (
                                    "追加后本机仍无试验命令（常见：未勾极限 cosφ / 工况未启用）。"
                                    "请在能力工况勾选 cosφ 后重开测。"
                                ),
                                "result_summary": {
                                    "handoff": True,
                                    "appended": False,
                                    "started": False,
                                    "empty_queue_after_append": True,
                                    "missingWidgets": missing,
                                },
                            },
                        )
                        self._move_pending_done(pending_path)
                        return
                except Exception as _q_exc:
                    self._log(f"开跑前队列检查跳过: {_q_exc}")
                # 开跑前再钉一次分项名，避免 comboBox_PS 被清空后 prepare project=
                try:
                    pname = str((handler or {}).get("project_name") or "").strip()
                    if pname and self.ensure_project:
                        self.ensure_project(pname)
                except Exception as _ens_exc:
                    self._log(f"开跑前切换项目跳过: {_ens_exc}")
                self.start_test()
                self._log("已调用开始试验")

            # 以下保持与原 _handle_job 后半一致：等结束或立即结案
            wait_finish_timeout = 7200
            # OVUF 等试验打开 Dialog/追加命令可能超过 8s；过短会把慢启动误判成未进入进行中
            start_grace = 20
            if isinstance(params, dict):
                try:
                    if params.get("wait_finish_timeout_sec") is not None:
                        wait_finish_timeout = int(params.get("wait_finish_timeout_sec"))
                except (TypeError, ValueError):
                    pass
                try:
                    if params.get("start_grace_sec") is not None:
                        start_grace = int(params.get("start_grace_sec"))
                except (TypeError, ValueError):
                    pass

            if auto_start and wait_finish and self.get_run_status:
                self._awaiting = {
                    "job_id": job_id,
                    "pending_path": pending_path,
                    "appended": appended,
                    "missing": missing,
                    "started_at": time.time(),
                    "timeout_sec": float(max(30, wait_finish_timeout)),
                    "start_grace_sec": float(max(0, start_grace)),
                    "seen_running": False,
                    "max_cmd_index": 0,
                    "max_cmd_total": 0,
                    "test_type": test_type,
                    "handler_key": str((handler or {}).get("key") or test_type),
                    # START 补 prepare / 空 comboBox_PS 时解析试验名用
                    "handler": {
                        "project_name": str((handler or {}).get("project_name") or ""),
                        "key": str((handler or {}).get("key") or test_type),
                        "label": str((handler or {}).get("label") or ""),
                    },
                    "widgets": dict(widgets) if isinstance(widgets, dict) else {},
                    "params": dict(params) if isinstance(params, dict) else {},
                }
                self._emit_progress(job_id, force=True)
                self._log(
                    f"任务 {job_id} 等待试验结束（超时{int(wait_finish_timeout)}秒，"
                    f"启动宽限{int(start_grace)}秒）"
                )
                self._check_awaiting_finish()
                return

            # 实验管理 / 要求等结束但未开跑：禁止「未执行就 success」（秒结束假成功）
            src = ""
            if isinstance(params, dict):
                src = str(params.get("source") or "").strip().lower()
            if (not auto_start) and wait_finish:
                self._write_result_all(
                    pending_path,
                    job_id,
                    {
                        "status": "failed",
                        "fail_reason": (
                            "云任务要求等待结束但未自动开跑（auto_start=false）；"
                            "已中止以免沿用上一单残留状态秒成功"
                        ),
                        "result_summary": {
                            "handoff": True,
                            "appended": appended,
                            "started": False,
                            "waited_finish": False,
                            "missingWidgets": missing,
                            "source": src or None,
                        },
                        "report_meta": [],
                    },
                )
                self._move_pending_done(pending_path)
                self._log(f"任务 {job_id} 已失败（wait_finish 但未开跑，拒绝秒成功）")
                return

            self._write_result_all(
                pending_path,
                job_id,
                {
                    "status": "success",
                    "fail_reason": "",
                    "result_summary": {
                        "handoff": True,
                        "appended": appended,
                        "started": bool(auto_start),
                        "waited_finish": False,
                        "missingWidgets": missing,
                    },
                    "report_meta": [],
                },
            )
            self._move_pending_done(pending_path)
            self._log(f"任务 {job_id} 已结案（未等待试验结束）")
        finally:
            self._job_ctx = None
            if not self._awaiting:
                self._busy = False
                try:
                    ui_release(repo_root=self.repo_root)
                except Exception:
                    pass


def start_iot_ui_handoff_from_main(
    *,
    resolve_overload_ui: Callable[[], Any],
    overload_append: Callable[[], None],
    resolve_antibackflow_ui: Optional[Callable[[], Any]] = None,
    antibackflow_append: Optional[Callable[[], None]] = None,
    resolve_flicker_ui: Optional[Callable[[], Any]] = None,
    flicker_append: Optional[Callable[[], None]] = None,
    resolve_harmonic_ui: Optional[Callable[[], Any]] = None,
    harmonic_append: Optional[Callable[[], None]] = None,
    resolve_fixedpf_ui: Optional[Callable[[], Any]] = None,
    fixedpf_append: Optional[Callable[[], None]] = None,
    resolve_dccomponent_ui: Optional[Callable[[], Any]] = None,
    dccomponent_append: Optional[Callable[[], None]] = None,
    resolve_reconnect_ui: Optional[Callable[[], Any]] = None,
    reconnect_append: Optional[Callable[[], None]] = None,
    resolve_ovuf_ui: Optional[Callable[[], Any]] = None,
    ovuf_append: Optional[Callable[[], None]] = None,
    resolve_guopinjiangzai_ui: Optional[Callable[[], Any]] = None,
    guopinjiangzai_append: Optional[Callable[[], None]] = None,
    resolve_qianpinshengzai_ui: Optional[Callable[[], Any]] = None,
    qianpinshengzai_append: Optional[Callable[[], None]] = None,
    resolve_voltprotect10min_ui: Optional[Callable[[], Any]] = None,
    voltprotect10min_append: Optional[Callable[[], None]] = None,
    resolve_guoqianpin_immun_ui: Optional[Callable[[], Any]] = None,
    guoqianpin_immun_append: Optional[Callable[[], None]] = None,
    resolve_staticmppt_ui: Optional[Callable[[], Any]] = None,
    staticmppt_append: Optional[Callable[[], None]] = None,
    resolve_frequencyadaptability_ui: Optional[Callable[[], Any]] = None,
    frequencyadaptability_append: Optional[Callable[[], None]] = None,
    resolve_voltageadaptability_ui: Optional[Callable[[], Any]] = None,
    voltageadaptability_append: Optional[Callable[[], None]] = None,
    resolve_rocof_ui: Optional[Callable[[], Any]] = None,
    rocof_append: Optional[Callable[[], None]] = None,
    resolve_rapidvolt_ui: Optional[Callable[[], Any]] = None,
    rapidvolt_append: Optional[Callable[[], None]] = None,
    resolve_lvrt_ui: Optional[Callable[[], Any]] = None,
    lvrt_append: Optional[Callable[[], None]] = None,
    resolve_phasejump_ui: Optional[Callable[[], Any]] = None,
    phasejump_append: Optional[Callable[[], None]] = None,
    resolve_dynamicmppt_ui: Optional[Callable[[], Any]] = None,
    dynamicmppt_append: Optional[Callable[[], None]] = None,
    resolve_reactiveqcap_ui: Optional[Callable[[], Any]] = None,
    reactiveqcap_append: Optional[Callable[[], None]] = None,
    resolve_fixedq_ui: Optional[Callable[[], Any]] = None,
    fixedq_append: Optional[Callable[[], None]] = None,
    resolve_reactiveqin_ui: Optional[Callable[[], Any]] = None,
    reactiveqin_append: Optional[Callable[[], None]] = None,
    resolve_reactiveqacc_ui: Optional[Callable[[], Any]] = None,
    reactiveqacc_append: Optional[Callable[[], None]] = None,
    resolve_activep_ui: Optional[Callable[[], Any]] = None,
    activep_append: Optional[Callable[[], None]] = None,
    resolve_staticqu_ui: Optional[Callable[[], Any]] = None,
    staticqu_append: Optional[Callable[[], None]] = None,
    resolve_dynamicqu_ui: Optional[Callable[[], Any]] = None,
    dynamicqu_append: Optional[Callable[[], None]] = None,
    resolve_testpu_ui: Optional[Callable[[], Any]] = None,
    testpu_append: Optional[Callable[[], None]] = None,
    resolve_staticcosphi_ui: Optional[Callable[[], Any]] = None,
    staticcosphi_append: Optional[Callable[[], None]] = None,
    resolve_dynamiccosphi_ui: Optional[Callable[[], Any]] = None,
    dynamiccosphi_append: Optional[Callable[[], None]] = None,
    resolve_cosphibrazil_ui: Optional[Callable[[], Any]] = None,
    cosphibrazil_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
    get_run_status: Optional[Callable[[], str]] = None,
    get_run_progress: Optional[Callable[[], Dict[str, Any]]] = None,
    ensure_project: Optional[Callable[[str], None]] = None,
    auto_connect: Optional[Callable[[], Any]] = None,
    prepare_auto_connect: Optional[Callable[[], Any]] = None,
    apply_auto_connect: Optional[Callable[[Any], Any]] = None,
    ensure_ready: Optional[Callable[[Any, str], tuple]] = None,
    session_ok: Optional[Callable[[str], bool]] = None,
    stop_test: Optional[Callable[[], None]] = None,
    reset_append_count: Optional[Callable[[], None]] = None,
    wrap_append_errors: bool = True,
    log: Optional[Callable[[str], None]] = None,
    parent=None,
) -> IotUiHandoffService:
    svc = IotUiHandoffService(
        resolve_overload_ui=resolve_overload_ui,
        overload_append=overload_append,
        resolve_antibackflow_ui=resolve_antibackflow_ui,
        antibackflow_append=antibackflow_append,
        resolve_flicker_ui=resolve_flicker_ui,
        flicker_append=flicker_append,
        resolve_harmonic_ui=resolve_harmonic_ui,
        harmonic_append=harmonic_append,
        resolve_fixedpf_ui=resolve_fixedpf_ui,
        fixedpf_append=fixedpf_append,
        resolve_dccomponent_ui=resolve_dccomponent_ui,
        dccomponent_append=dccomponent_append,
        resolve_reconnect_ui=resolve_reconnect_ui,
        reconnect_append=reconnect_append,
        resolve_ovuf_ui=resolve_ovuf_ui,
        ovuf_append=ovuf_append,
        resolve_guopinjiangzai_ui=resolve_guopinjiangzai_ui,
        guopinjiangzai_append=guopinjiangzai_append,
        resolve_qianpinshengzai_ui=resolve_qianpinshengzai_ui,
        qianpinshengzai_append=qianpinshengzai_append,
        resolve_voltprotect10min_ui=resolve_voltprotect10min_ui,
        voltprotect10min_append=voltprotect10min_append,
        resolve_guoqianpin_immun_ui=resolve_guoqianpin_immun_ui,
        guoqianpin_immun_append=guoqianpin_immun_append,
        resolve_staticmppt_ui=resolve_staticmppt_ui,
        staticmppt_append=staticmppt_append,
        resolve_frequencyadaptability_ui=resolve_frequencyadaptability_ui,
        frequencyadaptability_append=frequencyadaptability_append,
        resolve_voltageadaptability_ui=resolve_voltageadaptability_ui,
        voltageadaptability_append=voltageadaptability_append,
        resolve_rocof_ui=resolve_rocof_ui,
        rocof_append=rocof_append,
        resolve_rapidvolt_ui=resolve_rapidvolt_ui,
        rapidvolt_append=rapidvolt_append,
        resolve_lvrt_ui=resolve_lvrt_ui,
        lvrt_append=lvrt_append,
        resolve_phasejump_ui=resolve_phasejump_ui,
        phasejump_append=phasejump_append,
        resolve_dynamicmppt_ui=resolve_dynamicmppt_ui,
        dynamicmppt_append=dynamicmppt_append,
        resolve_reactiveqcap_ui=resolve_reactiveqcap_ui,
        reactiveqcap_append=reactiveqcap_append,
        resolve_fixedq_ui=resolve_fixedq_ui,
        fixedq_append=fixedq_append,
        resolve_reactiveqin_ui=resolve_reactiveqin_ui,
        reactiveqin_append=reactiveqin_append,
        resolve_reactiveqacc_ui=resolve_reactiveqacc_ui,
        reactiveqacc_append=reactiveqacc_append,
        resolve_activep_ui=resolve_activep_ui,
        activep_append=activep_append,
        resolve_staticqu_ui=resolve_staticqu_ui,
        staticqu_append=staticqu_append,
        resolve_dynamicqu_ui=resolve_dynamicqu_ui,
        dynamicqu_append=dynamicqu_append,
        resolve_testpu_ui=resolve_testpu_ui,
        testpu_append=testpu_append,
        resolve_staticcosphi_ui=resolve_staticcosphi_ui,
        staticcosphi_append=staticcosphi_append,
        resolve_dynamiccosphi_ui=resolve_dynamiccosphi_ui,
        dynamiccosphi_append=dynamiccosphi_append,
        resolve_cosphibrazil_ui=resolve_cosphibrazil_ui,
        cosphibrazil_append=cosphibrazil_append,
        start_test=start_test,
        get_run_status=get_run_status,
        get_run_progress=get_run_progress,
        ensure_project=ensure_project,
        auto_connect=auto_connect,
        prepare_auto_connect=prepare_auto_connect,
        apply_auto_connect=apply_auto_connect,
        ensure_ready=ensure_ready,
        session_ok=session_ok,
        stop_test=stop_test,
        reset_append_count=reset_append_count,
        wrap_append_errors=wrap_append_errors,
        log=log,
        parent=parent,
    )
    # 稍晚启动，等主界面事件循环稳定
    QTimer.singleShot(2500, svc.start)
    return svc
