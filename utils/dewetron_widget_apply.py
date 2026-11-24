# -*- coding: utf-8 -*-
"""把 IOT 仪器页德威创 widgets 写到桌面设置页 / 试验内嵌面板。"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional


def _as_bool(val: Any) -> Optional[bool]:
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    text = str(val).strip().lower()
    if text in ("1", "true", "yes", "on", "checked"):
        return True
    if text in ("0", "false", "no", "off", "unchecked", ""):
        return False
    return None


def apply_dewetron_panel_widgets(ui_obj: Any, widgets: Mapping[str, Any]) -> Dict[str, bool]:
    """把刷新率/小数位/波形/绝对时间/原始录波/保存路径写到带同名控件的 UI。

    返回各键是否写成功，便于单测与日志。
    """
    done = {
        "rate": False,
        "decimal": False,
        "realtime": False,
        "abs_time": False,
        "keep_dmd": False,
        "save_dir": False,
    }
    if ui_obj is None or not isinstance(widgets, Mapping):
        return done

    # 优先走面板 set_config，避免漏控件别名
    panel = getattr(ui_obj, "dewetron_panel", None) or getattr(ui_obj, "dewetronPanel", None)
    target = panel if panel is not None else ui_obj
    set_cfg = getattr(target, "set_config", None) or getattr(target, "set_dewetron_config", None)
    if callable(set_cfg):
        try:
            from components.dewetron_autotest_panel import DewetronUiConfig

            cur = None
            getter = getattr(target, "get_config", None) or getattr(
                target, "get_dewetron_config", None
            )
            if callable(getter):
                try:
                    cur = getter()
                except Exception:
                    cur = None
            base = DewetronUiConfig.coerce(cur) if cur is not None else DewetronUiConfig()
            rate = widgets.get("comboBox_DEW_MaxRefreshRate")
            if rate is None or str(rate).strip() == "":
                rate = widgets.get("comboBox_maxRefreshRate")
            if rate is not None and str(rate).strip() != "":
                base.rate_text = str(rate).strip()
                done["rate"] = True
            dec = widgets.get("spinBox_DEW_DecimalPlaces")
            if dec is None:
                dec = widgets.get("decimal_places")
            if dec is not None and str(dec).strip() != "":
                try:
                    base.decimal_places = int(float(dec))
                    done["decimal"] = True
                except (TypeError, ValueError):
                    pass
            rt = _as_bool(widgets.get("checkBox_DEW_RealtimeWaveform"))
            if rt is not None:
                base.realtime_waveform = rt
                done["realtime"] = True
            abs_t = _as_bool(widgets.get("checkBox_DEW_ExportAbsTime"))
            if abs_t is not None:
                base.export_abs_time = abs_t
                done["abs_time"] = True
            keep = _as_bool(widgets.get("checkBox_DEW_KeepOxygenDmd"))
            if keep is not None:
                base.keep_oxygen_dmd = keep
                done["keep_dmd"] = True
            save = widgets.get("lineEdit_DEW_SaveDir")
            if save is not None:
                base.save_dir = str(save).strip()
                done["save_dir"] = True
            set_cfg(base)
            return done
        except Exception:
            pass

    def _set_check(name: str, key: str) -> None:
        box = getattr(target, name, None) or getattr(ui_obj, name, None)
        flag = _as_bool(widgets.get(name))
        if box is None or flag is None or not hasattr(box, "setChecked"):
            return
        try:
            box.setChecked(flag)
            done[key] = True
        except Exception:
            pass

    rate = widgets.get("comboBox_DEW_MaxRefreshRate") or widgets.get("comboBox_maxRefreshRate")
    combo = getattr(target, "comboBox_DEW_MaxRefreshRate", None) or getattr(
        ui_obj, "comboBox_DEW_MaxRefreshRate", None
    )
    if combo is not None and rate is not None and str(rate).strip() != "":
        try:
            text = str(rate).strip()
            idx = combo.findText(text) if hasattr(combo, "findText") else -1
            if idx >= 0:
                combo.setCurrentIndex(idx)
            elif hasattr(combo, "setCurrentText"):
                combo.setCurrentText(text)
            done["rate"] = True
        except Exception:
            pass

    dec = widgets.get("spinBox_DEW_DecimalPlaces")
    if dec is None:
        dec = widgets.get("decimal_places")
    spin = getattr(target, "spinBox_DEW_DecimalPlaces", None) or getattr(
        ui_obj, "spinBox_DEW_DecimalPlaces", None
    )
    if spin is not None and dec is not None and str(dec).strip() != "" and hasattr(spin, "setValue"):
        try:
            spin.setValue(int(float(dec)))
            done["decimal"] = True
        except (TypeError, ValueError, Exception):
            pass

    _set_check("checkBox_DEW_RealtimeWaveform", "realtime")
    _set_check("checkBox_DEW_ExportAbsTime", "abs_time")
    _set_check("checkBox_DEW_KeepOxygenDmd", "keep_dmd")

    save = widgets.get("lineEdit_DEW_SaveDir")
    edit = getattr(target, "lineEdit_DEW_SaveDir", None) or getattr(
        ui_obj, "lineEdit_DEW_SaveDir", None
    )
    if edit is not None and save is not None and hasattr(edit, "setText"):
        try:
            edit.setText(str(save))
            done["save_dir"] = True
        except Exception:
            pass
    return done
