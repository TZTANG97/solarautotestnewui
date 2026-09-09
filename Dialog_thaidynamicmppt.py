# -*- coding: utf-8 -*-
"""Dynamic MPPT dialog — EN50530 table aligned with Chroma, SCPI execution."""

from __future__ import annotations

from PyQt5 import QtWidgets

from Dialog_thailvrt import _BaseTimingProfileDialogUi
from utils.timing_profile import DYNAMIC_MPPT_SCHEMA


class Ui_Dialog_thaidynamicmppt(_BaseTimingProfileDialogUi):
    OBJECT_NAME = "Dialog_thaidynamicmppt"
    WINDOW_TITLE = "动态 MPPT 项目配置"
    PROFILE_TITLE = "EN50530 & CGC/GF004"
    SCHEMA = DYNAMIC_MPPT_SCHEMA
    DEFAULT_PROFILE = ()

    def _build_profile_page(self) -> None:
        from components.en50530_dynamic_mppt_panel import En50530DynamicMpptPanel

        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)

        head = QtWidgets.QHBoxLayout()
        self.checkBox_S3 = QtWidgets.QCheckBox("step3")
        self.checkBox_S3.setObjectName("checkBox_S3")
        self.checkBox_S3.setChecked(True)
        head.addWidget(self.checkBox_S3)
        head.addWidget(
            QtWidgets.QLabel("参数页与 Chroma Dynamic MPPT Panel 对齐；执行方式为 SCPI 写 IV 曲线。")
        )
        head.addStretch()
        layout.addLayout(head)

        self.en50530Panel = En50530DynamicMpptPanel()
        self.en50530Panel.setObjectName("en50530Panel")
        layout.addWidget(self.en50530Panel, 1)

        selector = QtWidgets.QHBoxLayout()
        selector.addWidget(QtWidgets.QLabel("参与工况的直流通道："))
        for channel in range(1, 5):
            checkbox = QtWidgets.QCheckBox("DC%d" % channel)
            checkbox.setObjectName("checkBox_S3_DC%d" % channel)
            checkbox.setChecked(channel == 1)
            setattr(self, checkbox.objectName(), checkbox)
            selector.addWidget(checkbox)
        selector.addStretch()
        layout.addLayout(selector)

        self.timingProfileTable = self.en50530Panel
        self.timing_profile_table = self.en50530Panel
        self.tableWidget_TimingProfile = self.en50530Panel.tabWidget_EN50530

        self.stackedWidget.addWidget(page)


Ui_Dialog_ThaiDynamicMPPT = Ui_Dialog_thaidynamicmppt

__all__ = ["Ui_Dialog_ThaiDynamicMPPT", "Ui_Dialog_thaidynamicmppt"]
