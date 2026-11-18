# -*- coding: utf-8 -*-
"""Shared modern timing dialog and the LVRT specialization."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from PyQt5 import QtCore, QtGui, QtWidgets

from components.dewetron_autotest_panel import AnalyzerModeSection
from components.timing_profile_table import TimingProfileTable
from components.wt_config_content import (
    build_wt1800_content,
    build_wt1806e_content,
    build_wt3000_content,
    build_wt5000_content,
)
from utils.timing_profile import LVRT_SCHEMA


_GROUP_STYLE = (
    "QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px;"
    " margin-top: 8px; padding-top: 10px; font-weight: bold; }"
    "QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 5px; }"
)


class _BaseTimingProfileDialogUi(object):
    """Complete AC/DC + analyzer + profile + shutdown dialog skeleton."""

    OBJECT_NAME = "Dialog_thaitiming"
    WINDOW_TITLE = "时序工况项目配置"
    PROFILE_TITLE = "时序工况"
    SCHEMA = LVRT_SCHEMA
    DEFAULT_PROFILE: Sequence[Dict[str, Any]] = ()
    # 子类填写后启用顶部「国家标准」下拉（与 IOT solar_standard_profiles 对齐）
    SOLAR_STANDARD_TT = ""

    def setupUi(self, dialog: QtWidgets.QDialog) -> None:
        dialog.setObjectName(self.OBJECT_NAME)
        dialog.resize(1400, 900)
        dialog.setMinimumSize(QtCore.QSize(1180, 720))
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(".\\ui_files\\logo.jpg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On,
        )
        dialog.setWindowIcon(icon)

        root = QtWidgets.QVBoxLayout(dialog)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_toolbar())

        self.stackedWidget = QtWidgets.QStackedWidget()
        self.stackedWidget.setObjectName("stackedWidget")
        self.stackedWidget.setStyleSheet("background: white;")
        root.addWidget(self.stackedWidget, 1)

        self._build_ac_dc_page()
        self._build_analyzer_page()
        self._build_profile_page()
        self._build_shutdown_page()
        self._connect_dc_linkage()
        self._switch_step(0)

        # Compatibility target: command generation is triggered by TestAppend.
        self.pushButton_Send = QtWidgets.QPushButton("提交")
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        dialog.setWindowTitle(self.WINDOW_TITLE)
        QtCore.QMetaObject.connectSlotsByName(dialog)

    def _build_toolbar(self) -> QtWidgets.QWidget:
        bar = QtWidgets.QWidget()
        bar.setObjectName("timingDialogToolbar")
        bar.setFixedHeight(58)
        bar.setStyleSheet(
            "QWidget#timingDialogToolbar { background: #f8fafc;"
            " border-bottom: 1px solid #e2e8f0; }"
        )
        layout = QtWidgets.QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        self.pushButton_TestAppend = self._toolbar_button(
            "pushButton_TestAppend", "测试追加", "#8b5cf6"
        )
        self.pushButton_ReadSettingFile = self._toolbar_button(
            "pushButton_ReadSettingFile", "读取设定", "#3b82f6"
        )
        self.pushButton_SaveSettingFile = self._toolbar_button(
            "pushButton_SaveSettingFile", "保存设定", "#10b981"
        )
        self.pushButton_ResetCount = self._toolbar_button(
            "pushButton_ResetCount", "重置", "#ef4444"
        )
        # Short aliases ease central wiring without replacing established names.
        self.pushButton_Append = self.pushButton_TestAppend
        self.pushButton_Read = self.pushButton_ReadSettingFile
        self.pushButton_Save = self.pushButton_SaveSettingFile
        self.pushButton_Reset = self.pushButton_ResetCount
        layout.addWidget(self.pushButton_TestAppend)
        layout.addWidget(self.pushButton_ReadSettingFile)
        layout.addWidget(self.pushButton_SaveSettingFile)

        layout.addWidget(QtWidgets.QLabel("追加次数"))
        self.label_append_count = QtWidgets.QLabel("0")
        self.label_append_count.setObjectName("label_append_count")
        self.label_append_count.setAlignment(QtCore.Qt.AlignCenter)
        self.label_append_count.setMinimumWidth(30)
        self.label_append_count.setStyleSheet(
            "color:#7c3aed;background:#ede9fe;border-radius:10px;padding:2px 8px;"
        )
        layout.addWidget(self.label_append_count)
        layout.addWidget(self.pushButton_ResetCount)
        self._install_solar_standard_combo(layout)
        layout.addStretch()

        self._step_labels: List[QtWidgets.QLabel] = []
        for index, title in enumerate(
            (
                "① AC/DC 电源",
                "② 功率分析仪",
                "③ %s" % self.PROFILE_TITLE,
                "④ 关机设置",
            )
        ):
            label = QtWidgets.QLabel(title)
            label.setObjectName("step_indicator_%d" % index)
            label.setCursor(QtCore.Qt.PointingHandCursor)
            label.mousePressEvent = (
                lambda _event, step=index: self._switch_step(step)
            )
            layout.addWidget(label)
            self._step_labels.append(label)
        return bar

    @staticmethod
    def _toolbar_button(name: str, text: str, color: str) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton(text)
        button.setObjectName(name)
        button.setStyleSheet(
            "QPushButton { background:%s;color:white;border:0;border-radius:4px;"
            " padding:6px 13px;font-size:12px;}" % color
        )
        return button

    def _install_solar_standard_combo(self, layout: QtWidgets.QHBoxLayout) -> None:
        tt = str(getattr(self, "SOLAR_STANDARD_TT", "") or "").strip()
        if not tt:
            return
        std_label = QtWidgets.QLabel("国家标准")
        std_label.setStyleSheet(
            "font-size: 12px; color: #475569; background: transparent; border: none;"
        )
        layout.addWidget(std_label)
        self.comboBox_SolarStandard = QtWidgets.QComboBox()
        self.comboBox_SolarStandard.setObjectName("comboBox_SolarStandard")
        self.comboBox_SolarStandard.setFixedWidth(168)
        self.comboBox_SolarStandard.setStyleSheet(
            "QComboBox { font-size: 12px; padding: 2px 6px; background: white; }"
        )
        try:
            mod = __import__(f"utils.iot_{tt}_standard", fromlist=["*"])
            list_fn = getattr(mod, f"list_{tt}_standard_options")
            for opt in list_fn():
                self.comboBox_SolarStandard.addItem(str(opt["label"]), str(opt["id"]))
        except Exception:
            self.comboBox_SolarStandard.addItem("泰国 PEA/MEA（现行）", "thai")
        self.comboBox_SolarStandard.setCurrentIndex(0)
        self._solar_standard = "thai"
        self.comboBox_SolarStandard.currentIndexChanged.connect(
            self._on_solar_standard_changed
        )
        layout.addWidget(self.comboBox_SolarStandard)

    def set_solar_standard(self, standard_id, *, apply_defaults=False):
        tt = str(getattr(self, "SOLAR_STANDARD_TT", "") or "").strip()
        if not tt:
            self._solar_standard = str(standard_id or "thai").strip() or "thai"
            return
        try:
            mod = __import__(f"utils.iot_{tt}_standard", fromlist=["*"])
            apply_fn = getattr(mod, f"apply_{tt}_standard_to_ui")
            apply_fn(
                self,
                standard_id,
                force=True,
                apply_defaults=bool(apply_defaults),
            )
        except Exception:
            self._solar_standard = str(standard_id or "thai").strip() or "thai"

    def _on_solar_standard_changed(self, index):
        sid = self.comboBox_SolarStandard.itemData(index)
        if sid is None:
            sid = "thai"
        self.set_solar_standard(str(sid), apply_defaults=True)

    def _switch_step(self, index: int) -> None:
        self.stackedWidget.setCurrentIndex(index)
        for current, label in enumerate(self._step_labels):
            if current == index:
                label.setStyleSheet(
                    "padding:6px 8px;color:#7c3aed;font-weight:bold;"
                    "border-bottom:2px solid #8b5cf6;background:#f3e8ff;"
                )
            else:
                label.setStyleSheet(
                    "padding:6px 8px;color:#64748b;"
                    "border-bottom:2px solid transparent;background:transparent;"
                )

    @staticmethod
    def _text_edit(name: str, default: str = "", width: int = 78) -> QtWidgets.QTextEdit:
        edit = QtWidgets.QTextEdit()
        edit.setObjectName(name)
        edit.setFixedSize(width, 28)
        edit.setPlainText(default)
        return edit

    @staticmethod
    def _combo(
        name: str, values: Sequence[str], current: int = 0, width: int = 95
    ) -> QtWidgets.QComboBox:
        combo = QtWidgets.QComboBox()
        combo.setObjectName(name)
        combo.addItems(list(values))
        combo.setCurrentIndex(current)
        combo.setFixedWidth(width)
        return combo

    def _build_ac_dc_page(self) -> None:
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.groupBox = QtWidgets.QGroupBox("交流电源设置")
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setStyleSheet(_GROUP_STYLE)
        ac = QtWidgets.QGridLayout(self.groupBox)
        self.checkBox_S1 = QtWidgets.QCheckBox("step1")
        self.checkBox_S1.setObjectName("checkBox_S1")
        self.checkBox_S1.setChecked(True)
        ac.addWidget(self.checkBox_S1, 0, 0)
        ac.addWidget(QtWidgets.QLabel("交流输出"), 0, 1)
        self.comboBox_S1_AC = self._combo(
            "comboBox_S1_AC", ("开启", "关闭")
        )
        ac.addWidget(self.comboBox_S1_AC, 0, 2)
        for index, default in enumerate(("230", "230", "230"), 1):
            attr = (
                "textEdit_S1_AC_VOLT"
                if index == 1
                else "textEdit_S1_AC_VOLT_%d" % index
            )
            edit = self._text_edit(attr, default)
            setattr(self, attr, edit)
            ac.addWidget(QtWidgets.QLabel("交流电压%d" % index), 1, (index - 1) * 2)
            ac.addWidget(edit, 1, (index - 1) * 2 + 1)
        self.textEdit_S1_AC_FR = self._text_edit("textEdit_S1_AC_FR", "50")
        ac.addWidget(QtWidgets.QLabel("频率(Hz)"), 2, 0)
        ac.addWidget(self.textEdit_S1_AC_FR, 2, 1)
        self.comboBox_S1_AC_2 = self._combo(
            "comboBox_S1_AC_2", ("单相", "三相"), current=1
        )
        ac.addWidget(QtWidgets.QLabel("相制"), 2, 2)
        ac.addWidget(self.comboBox_S1_AC_2, 2, 3)
        layout.addWidget(self.groupBox)

        self.groupBox_2 = QtWidgets.QGroupBox("直流电源设置")
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setStyleSheet(_GROUP_STYLE)
        dc = QtWidgets.QGridLayout(self.groupBox_2)
        for column, title in enumerate(
            ("通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率(%)")
        ):
            heading = QtWidgets.QLabel(title)
            heading.setAlignment(QtCore.Qt.AlignCenter)
            dc.addWidget(heading, 0, column)
        defaults = ("650", "12", "720", "13", "100")
        suffixes = ("VOLT", "CURR", "Voc", "Isc", "PF")
        for channel in range(1, 5):
            checkbox = QtWidgets.QCheckBox("直流电源%d" % channel)
            checkbox.setObjectName("checkBox_S1_DC%d" % channel)
            checkbox.setChecked(True)
            setattr(self, checkbox.objectName(), checkbox)
            dc.addWidget(checkbox, channel, 0)
            combo = self._combo(
                "comboBox_S1_DC%d" % channel, ("开启", "关闭"), width=78
            )
            setattr(self, combo.objectName(), combo)
            dc.addWidget(combo, channel, 1)
            for column, (suffix, default) in enumerate(
                zip(suffixes, defaults), 2
            ):
                name = "textEdit_S1_DC%d_%s" % (channel, suffix)
                edit = self._text_edit(name, default, 70)
                setattr(self, name, edit)
                dc.addWidget(edit, channel, column)
        layout.addWidget(self.groupBox_2)

        timing = QtWidgets.QGroupBox("启机时序")
        timing.setObjectName("groupBox_4")
        timing.setStyleSheet(_GROUP_STYLE)
        grid = QtWidgets.QGridLayout(timing)
        self.textEdit_S1_ACWaitTIME = self._text_edit(
            "textEdit_S1_ACWaitTIME", "3"
        )
        self.comboBox_S1_ACWaitTIME = self._combo(
            "comboBox_S1_ACWaitTIME", ("秒", "分钟", "毫秒")
        )
        self.textEdit_S1_TIME = self._text_edit("textEdit_S1_TIME", "5")
        self.comboBox_S1_TIME = self._combo(
            "comboBox_S1_TIME", ("分钟", "秒", "毫秒"), current=0
        )
        grid.addWidget(QtWidgets.QLabel("交流输出等待"), 0, 0)
        grid.addWidget(self.textEdit_S1_ACWaitTIME, 0, 1)
        grid.addWidget(self.comboBox_S1_ACWaitTIME, 0, 2)
        grid.addWidget(QtWidgets.QLabel("启机等待"), 0, 3)
        grid.addWidget(self.textEdit_S1_TIME, 0, 4)
        grid.addWidget(self.comboBox_S1_TIME, 0, 5)
        layout.addWidget(timing)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    def _make_radio(
        self, name: str, text: str, *, checked: bool = False
    ) -> QtWidgets.QRadioButton:
        radio = QtWidgets.QRadioButton(text)
        radio.setObjectName(name)
        radio.setChecked(checked)
        setattr(self, name, radio)
        return radio

    def _build_analyzer_page(self) -> None:
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)

        wt_group = QtWidgets.QGroupBox("功率分析仪设置")
        wt_group.setObjectName("groupBox_wt")
        wt_group.setStyleSheet(_GROUP_STYLE)
        wt_layout = QtWidgets.QVBoxLayout(wt_group)
        top = QtWidgets.QHBoxLayout()
        self.checkBox_S2 = QtWidgets.QCheckBox("step2")
        self.checkBox_S2.setObjectName("checkBox_S2")
        self.checkBox_S2.setChecked(True)
        top.addWidget(self.checkBox_S2)
        radios = (
            self._make_radio("radioButton_S2_WT3000", "WT3000", checked=True),
            self._make_radio("radioButton_S2_WT1800", "WT1800"),
            self._make_radio("radioButton_S2_WT1806E", "WT1806E"),
            self._make_radio("radioButton_S2_WT5000", "WT5000"),
        )
        self._radio_group = QtWidgets.QButtonGroup(None)
        for index, radio in enumerate(radios):
            self._radio_group.addButton(radio, index)
            top.addWidget(radio)
        top.addStretch()
        wt_layout.addLayout(top)

        self._wtStacked = QtWidgets.QStackedWidget()
        self._wtStacked.setObjectName("wtConfigStack")
        self._wtStacked.addWidget(build_wt3000_content(self))
        self._wtStacked.addWidget(build_wt1800_content(self))
        self._wtStacked.addWidget(build_wt1806e_content(self))
        self._wtStacked.addWidget(build_wt5000_content(self))
        wt_layout.addWidget(self._wtStacked, 1)
        self._radio_group.buttonToggled.connect(
            lambda button, checked: self._wtStacked.setCurrentIndex(
                self._radio_group.id(button)
            )
            if checked
            else None
        )

        self.analyzerModeSection = AnalyzerModeSection(
            wt_group, self.checkBox_S2
        )
        self.analyzerModeSection.setObjectName("analyzerModeSection")
        self.dewetronPanel = self.analyzerModeSection.dewetron_panel
        self.radio_wt3000 = self.analyzerModeSection.radio_wt
        self.radio_dewetron = self.analyzerModeSection.radio_dewetron
        self._mode = self.analyzerModeSection.current_mode()
        self.analyzerModeSection.mode_changed.connect(
            lambda mode: setattr(self, "_mode", mode)
        )
        for name in (
            "pushButton_DEW_TestApply",
            "pushButton_DEW_RefreshFields",
            "pushButton_DEW_DataViewer",
            "comboBox_DEW_MaxRefreshRate",
            "spinBox_DEW_DecimalPlaces",
            "checkBox_DEW_RealtimeWaveform",
            "treeWidget_DEW_ExportFields",
        ):
            setattr(self, name, getattr(self.dewetronPanel, name))
        self.get_checked_export_fields = (
            self.dewetronPanel.get_checked_export_fields
        )
        self.refresh_export_field_tree = (
            self.dewetronPanel.refresh_export_field_tree
        )
        self.set_checked_export_fields = (
            self.dewetronPanel.set_checked_export_fields
        )
        layout.addWidget(self.analyzerModeSection, 1)
        self.stackedWidget.addWidget(page)

    def _build_profile_page(self) -> None:
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        group = QtWidgets.QGroupBox(self.PROFILE_TITLE)
        group.setObjectName("groupBox_timing_profile")
        group.setStyleSheet(_GROUP_STYLE)
        group_layout = QtWidgets.QVBoxLayout(group)
        selector = QtWidgets.QHBoxLayout()
        self.checkBox_S3 = QtWidgets.QCheckBox("step3")
        self.checkBox_S3.setObjectName("checkBox_S3")
        self.checkBox_S3.setChecked(True)
        selector.addWidget(self.checkBox_S3)
        selector.addWidget(QtWidgets.QLabel("参与工况的直流通道："))
        for channel in range(1, 5):
            checkbox = QtWidgets.QCheckBox("DC%d" % channel)
            checkbox.setObjectName("checkBox_S3_DC%d" % channel)
            checkbox.setChecked(True)
            setattr(self, checkbox.objectName(), checkbox)
            selector.addWidget(checkbox)
        selector.addStretch()
        group_layout.addLayout(selector)

        rows = list(self.DEFAULT_PROFILE) or None
        self.timingProfileTable = TimingProfileTable(
            self.SCHEMA, rows=rows
        )
        self.timingProfileTable.setObjectName("timingProfileTable")
        self.timing_profile_table = self.timingProfileTable
        self.tableWidget_TimingProfile = (
            self.timingProfileTable.tableWidget_TimingProfile
        )
        group_layout.addWidget(self.timingProfileTable, 1)
        self._mount_extra_profile_widgets(group_layout)
        layout.addWidget(group, 1)
        self.stackedWidget.addWidget(page)

    def _mount_extra_profile_widgets(
        self, group_layout: QtWidgets.QVBoxLayout
    ) -> None:
        """Hook for LVRT PEA phase-condition list; other timing dialogs no-op."""
        return

    def _build_shutdown_page(self) -> None:
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        self.groupBox_End = QtWidgets.QGroupBox("安全关机设置")
        self.groupBox_End.setObjectName("groupBox_End")
        self.groupBox_End.setStyleSheet(_GROUP_STYLE)
        grid = QtWidgets.QGridLayout(self.groupBox_End)
        self.checkBox_S_End = QtWidgets.QCheckBox("step_last")
        self.checkBox_S_End.setObjectName("checkBox_S_End")
        self.checkBox_S_End.setChecked(True)
        grid.addWidget(self.checkBox_S_End, 0, 0)
        grid.addWidget(QtWidgets.QLabel("交流电源"), 0, 1)
        self.comboBox_S_End_AC = self._combo(
            "comboBox_S_End_AC", ("关闭", "开启")
        )
        grid.addWidget(self.comboBox_S_End_AC, 0, 2)
        for channel in range(1, 5):
            checkbox = QtWidgets.QCheckBox("直流电源%d" % channel)
            checkbox.setObjectName("checkBox_S_End_DC%d" % channel)
            checkbox.setChecked(True)
            setattr(self, checkbox.objectName(), checkbox)
            combo = self._combo(
                "comboBox_S_End_DC%d" % channel,
                ("关闭", "开启"),
                width=80,
            )
            setattr(self, combo.objectName(), combo)
            grid.addWidget(checkbox, 1, (channel - 1) * 2)
            grid.addWidget(combo, 1, (channel - 1) * 2 + 1)
        note = QtWidgets.QLabel(
            "默认顺序为 DC 通道依次关闭并等待，再关闭 AC；中央安全关机 helper 接入后自动优先使用。"
        )
        note.setWordWrap(True)
        note.setStyleSheet("color:#64748b;")
        grid.addWidget(note, 2, 0, 1, 8)
        layout.addWidget(self.groupBox_End)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    def _connect_dc_linkage(self) -> None:
        s1 = [getattr(self, "checkBox_S1_DC%d" % i) for i in range(1, 5)]
        groups = (
            (
                self.checkBox_S3,
                [getattr(self, "checkBox_S3_DC%d" % i) for i in range(1, 5)],
            ),
            (
                self.checkBox_S_End,
                [
                    getattr(self, "checkBox_S_End_DC%d" % i)
                    for i in range(1, 5)
                ],
            ),
        )
        self._dc_link_callbacks = []
        for step_checkbox, children in groups:
            def update(
                _checked: Any = None,
                step: QtWidgets.QCheckBox = step_checkbox,
                targets: Sequence[QtWidgets.QCheckBox] = children,
            ) -> None:
                step_on = step.isChecked()
                for source, target in zip(s1, targets):
                    enabled = step_on and source.isChecked()
                    target.setEnabled(enabled)
                    target.setChecked(enabled)

            step_checkbox.toggled.connect(update)
            for source in s1:
                source.toggled.connect(update)
            self._dc_link_callbacks.append(update)
            update()


class Ui_Dialog_thailvrt(_BaseTimingProfileDialogUi):
    OBJECT_NAME = "Dialog_thailvrt"
    WINDOW_TITLE = "低电压穿越（LVRT）项目配置"
    PROFILE_TITLE = "LVRT 电压阶跃时序"
    SOLAR_STANDARD_TT = "lvrt"
    SCHEMA = LVRT_SCHEMA
    DEFAULT_PROFILE = (
        {
            "enabled": True,
            "label": "LVRT 0.20 p.u.",
            "t_pre": 1,
            "t_pre_unit": "秒",
            "t_dwell": 0.15,
            "t_dwell_unit": "秒",
            "t_post": 3,
            "t_post_unit": "秒",
            "u_pu": 0.2,
            "repeats": 1,
        },
    )

    def _lvrt_rated_un(self) -> float:
        try:
            raw = self.textEdit_S1_AC_VOLT.toPlainText().strip() or "230"
            value = float(raw)
            return value if value > 0 else 230.0
        except (TypeError, ValueError, AttributeError):
            return 230.0

    def _mount_extra_profile_widgets(
        self, group_layout: QtWidgets.QVBoxLayout
    ) -> None:
        from components.ovuf_condition_list import OvufConditionList

        note = QtWidgets.QLabel(
            "PEA 分相电压穿越（可选）：有启用行时优先于上方对称时序表。"
        )
        note.setWordWrap(True)
        note.setStyleSheet("color:#64748b; font-size: 13px;")
        group_layout.addWidget(note)

        self.lvrtConditionList = OvufConditionList(
            voltage_only=True,
            object_name="lvrtConditionList",
        )
        self.lvrtConditionList.set_un_provider(self._lvrt_rated_un)
        group_layout.addWidget(self.lvrtConditionList)


# Common capitalization aliases used by older integration branches.
Ui_Dialog_ThaiLVRT = Ui_Dialog_thailvrt


__all__ = [
    "Ui_Dialog_ThaiLVRT",
    "Ui_Dialog_thailvrt",
    "_BaseTimingProfileDialogUi",
]
