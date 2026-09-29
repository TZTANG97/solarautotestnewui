# -*- coding: utf-8 -*-
"""Three-phase Chroma phase-jump timing dialog."""

from Dialog_thailvrt import _BaseTimingProfileDialogUi
from utils.timing_profile import PHASE_JUMP_SCHEMA


class Ui_Dialog_thaiphasejump(_BaseTimingProfileDialogUi):
    OBJECT_NAME = "Dialog_thaiphasejump"
    WINDOW_TITLE = "相角突变项目配置"
    PROFILE_TITLE = "Chroma 三相相位差突变时序"
    SCHEMA = PHASE_JUMP_SCHEMA
    DEFAULT_PROFILE = (
        {
            "enabled": True,
            "label": "相角 +10°",
            "t_pre": 1,
            "t_pre_unit": "秒",
            "t_dwell": 0.5,
            "t_dwell_unit": "秒",
            "t_post": 2,
            "t_post_unit": "秒",
            "phase_deg": 10,
            "repeats": 1,
        },
        {
            "enabled": False,
            "label": "相角 -10°",
            "t_pre": 1,
            "t_pre_unit": "秒",
            "t_dwell": 0.5,
            "t_dwell_unit": "秒",
            "t_post": 2,
            "t_post_unit": "秒",
            "phase_deg": -10,
            "repeats": 1,
        },
    )


Ui_Dialog_ThaiPhaseJump = Ui_Dialog_thaiphasejump


__all__ = ["Ui_Dialog_ThaiPhaseJump", "Ui_Dialog_thaiphasejump"]
