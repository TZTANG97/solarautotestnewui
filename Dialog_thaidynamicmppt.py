# -*- coding: utf-8 -*-
"""Dynamic-MPPT timing dialog."""

from Dialog_thailvrt import _BaseTimingProfileDialogUi
from utils.timing_profile import DYNAMIC_MPPT_SCHEMA


class Ui_Dialog_thaidynamicmppt(_BaseTimingProfileDialogUi):
    OBJECT_NAME = "Dialog_thaidynamicmppt"
    WINDOW_TITLE = "动态 MPPT 项目配置"
    PROFILE_TITLE = "动态 MPPT 曲线时序"
    SCHEMA = DYNAMIC_MPPT_SCHEMA
    DEFAULT_PROFILE = (
        {
            "enabled": True,
            "label": "STC 100%",
            "t_pre": 1,
            "t_pre_unit": "秒",
            "t_dwell": 10,
            "t_dwell_unit": "秒",
            "t_post": 1,
            "t_post_unit": "秒",
            "p_pct": 100,
            "irr_wm2": 1000,
            "temp_c": 25,
            "pmpp": 8000,
            "umpp": 650,
            "ff": 0.8,
            "repeats": 1,
        },
        {
            "enabled": True,
            "label": "辐照度 50%",
            "t_pre": 1,
            "t_pre_unit": "秒",
            "t_dwell": 10,
            "t_dwell_unit": "秒",
            "t_post": 1,
            "t_post_unit": "秒",
            "p_pct": 50,
            "irr_wm2": 500,
            "temp_c": 25,
            "pmpp": 4000,
            "umpp": 640,
            "ff": 0.78,
            "repeats": 1,
        },
    )


Ui_Dialog_ThaiDynamicMPPT = Ui_Dialog_thaidynamicmppt


__all__ = ["Ui_Dialog_ThaiDynamicMPPT", "Ui_Dialog_thaidynamicmppt"]
