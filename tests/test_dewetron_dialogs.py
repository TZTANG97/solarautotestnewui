# -*- coding: utf-8 -*-
"""Headless integration tests for shared analyzer mode project dialogs."""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtWidgets

from Dialog_thaichonglian import Ui_Dialog_thaichonglian
from Dialog_thaioverloads import Ui_Dialog_thaioverloads
from Dialog_thaizhiliufenliang import Ui_Dialog_thaizhiliufenliang
from Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU
from Dialog_thaitestPU import Ui_Dialog_thaitestPU
from Dialog_thaistaticcosPhi import Ui_Dialog_thaistaticcosPhi
from Dialog_thaicosPhi_Brazil import Ui_Dialog_thaicosPhi_Brazil
from Dialog_thaivoltprotect10min import Ui_Dialog_thaivoltprotect10min
from Dialog_thaiguopinjiangzai import Ui_Dialog_thaiguopinjiangzai
from Dialog_thaiqianpinshengzai import Ui_Dialog_thaiqianpinshengzai
from Dialog_thaiguoqianya_pin import Ui_Dialog_thaiguoqianya_pin
from Dialog_thaiguoqianpin_immun import Ui_Dialog_thaiguoqianpin_immun
from Dialog_thaifrequencyadaptability import Ui_Dialog_thaifrequencyadaptability
from Dialog_thaivoltageadaptability import Ui_Dialog_thaivoltageadaptability
from Dialog_thairocof import Ui_Dialog_thairocof
from Dialog_thairapidvolt import Ui_Dialog_thairapidvolt


DIALOG_CLASSES = (
    Ui_Dialog_thaichonglian,
    Ui_Dialog_thaioverloads,
    Ui_Dialog_thaizhiliufenliang,
    Ui_Dialog_thaiStaticQU,
    Ui_Dialog_thaitestPU,
    Ui_Dialog_thaistaticcosPhi,
    Ui_Dialog_thaicosPhi_Brazil,
    Ui_Dialog_thaivoltprotect10min,
    Ui_Dialog_thaiguopinjiangzai,
    Ui_Dialog_thaiqianpinshengzai,
    Ui_Dialog_thaiguoqianya_pin,
    Ui_Dialog_thaiguoqianpin_immun,
    Ui_Dialog_thaifrequencyadaptability,
    Ui_Dialog_thaivoltageadaptability,
    Ui_Dialog_thairocof,
    Ui_Dialog_thairapidvolt,
)

PANEL_WIDGET_ALIASES = (
    "pushButton_DEW_TestApply",
    "pushButton_DEW_RefreshFields",
    "pushButton_DEW_DataViewer",
    "comboBox_DEW_MaxRefreshRate",
    "spinBox_DEW_DecimalPlaces",
    "checkBox_DEW_RealtimeWaveform",
    "treeWidget_DEW_ExportFields",
)

PANEL_METHOD_ALIASES = (
    "get_checked_export_fields",
    "refresh_export_field_tree",
    "set_checked_export_fields",
    "get_checked_fields",
    "refresh_checked_fields",
    "set_checked_fields",
)


class AnalyzerModeDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def _build_ui(self, ui_class):
        dialog = QtWidgets.QDialog()
        ui = ui_class()
        ui.setupUi(dialog)
        self.addCleanup(dialog.deleteLater)
        return dialog, ui

    def test_all_approved_dialogs_share_analyzer_modes_and_preserve_wt_pages(self):
        for ui_class in DIALOG_CLASSES:
            with self.subTest(dialog=ui_class.__name__):
                _dialog, ui = self._build_ui(ui_class)

                self.assertEqual(ui._wtStacked.count(), 4)
                self.assertIsNot(ui._wtStacked,
                                 ui.analyzerModeSection.analyzer_stack)
                wt_pages = tuple(ui._wtStacked.widget(index) for index in range(4))
                self.assertEqual(len({id(page) for page in wt_pages}), 4)
                wt_group = ui.analyzerModeSection.primary_wt_widget
                self.assertIs(wt_group.parentWidget(),
                              ui.analyzerModeSection.analyzer_stack)
                self.assertIs(ui.analyzerModeSection.analyzer_stack.widget(0), wt_group)
                self.assertIs(ui.analyzerModeSection.analyzer_stack.widget(1),
                              ui.dewetronPanel)
                self.assertTrue(wt_group.isAncestorOf(ui._wtStacked))
                self.assertEqual(
                    tuple(ui._wtStacked.widget(index) for index in range(4)), wt_pages
                )

                wt_radios = (
                    ui.radioButton_S2_WT3000,
                    ui.radioButton_S2_WT1800,
                    ui.radioButton_S2_WT1806E,
                    ui.radioButton_S2_WT5000,
                )
                self.assertEqual(
                    tuple(radio.objectName() for radio in wt_radios),
                    ("radio_S2_WT3000", "radio_S2_WT1800",
                     "radio_S2_WT1806E", "radio_S2_WT5000"),
                )
                for radio in wt_radios:
                    self.assertTrue(wt_group.isAncestorOf(radio))

                self.assertIs(ui.radio_wt3000, ui.analyzerModeSection.radio_wt)
                self.assertIs(ui.radio_dewetron,
                              ui.analyzerModeSection.radio_dewetron)
                self.assertTrue(ui.radio_wt3000.isChecked())
                self.assertFalse(ui.radio_dewetron.isChecked())
                self.assertEqual(ui._mode, "wt3000")
                self.assertEqual(ui.analyzerModeSection.currentIndex()
                                 if hasattr(ui.analyzerModeSection, "currentIndex")
                                 else ui.analyzerModeSection.analyzer_stack.currentIndex(), 0)

                for name in PANEL_WIDGET_ALIASES:
                    self.assertIs(getattr(ui, name), getattr(ui.dewetronPanel, name))
                for name in PANEL_METHOD_ALIASES:
                    self.assertTrue(callable(getattr(ui, name)))

                ui.radio_dewetron.setChecked(True)
                self.app.processEvents()
                self.assertEqual(ui._mode, "dewetron")
                self.assertEqual(ui.analyzerModeSection.current_mode(), "dewetron")
                self.assertEqual(ui.analyzerModeSection.analyzer_stack.currentIndex(), 1)

                ui.checkBox_S2.setChecked(False)
                self.app.processEvents()
                self.assertFalse(ui.radio_wt3000.isEnabled())
                self.assertFalse(ui.radio_dewetron.isEnabled())
                self.assertFalse(ui.analyzerModeSection.analyzer_stack.isEnabled())
                self.assertFalse(ui._wtStacked.isEnabled())
                self.assertFalse(ui.dewetronPanel.isEnabled())
                for radio in wt_radios:
                    self.assertFalse(radio.isEnabled())
                self.assertTrue(ui.checkBox_S2.isEnabled())

                ui.checkBox_S2.setChecked(True)
                self.app.processEvents()
                self.assertTrue(ui.radio_wt3000.isEnabled())
                self.assertTrue(ui.radio_dewetron.isEnabled())
                self.assertTrue(ui.analyzerModeSection.analyzer_stack.isEnabled())
                self.assertTrue(ui._wtStacked.isEnabled())
                self.assertTrue(ui.dewetronPanel.isEnabled())
                for radio in wt_radios:
                    self.assertTrue(radio.isEnabled())

                ui.radio_wt3000.setChecked(True)
                self.app.processEvents()
                self.assertEqual(ui._mode, "wt3000")
                self.assertEqual(ui.analyzerModeSection.analyzer_stack.currentIndex(), 0)

    def test_wt_device_radios_still_drive_original_wt_stack(self):
        for ui_class in DIALOG_CLASSES:
            with self.subTest(dialog=ui_class.__name__):
                _dialog, ui = self._build_ui(ui_class)
                radios = (
                    ui.radioButton_S2_WT3000,
                    ui.radioButton_S2_WT1800,
                    ui.radioButton_S2_WT1806E,
                    ui.radioButton_S2_WT5000,
                )
                for index, radio in enumerate(radios):
                    radio.setChecked(True)
                    self.app.processEvents()
                    self.assertEqual(ui._wtStacked.currentIndex(), index)

    def test_special_step_two_siblings_remain_outside_mode_stack(self):
        _dialog, brazil = self._build_ui(Ui_Dialog_thaicosPhi_Brazil)
        self.assertEqual(brazil.checkBox_S2.objectName(), "checkBox_S2")
        self.assertIsNotNone(brazil.textEdit_S3_TIME_2.parentWidget())
        self.assertFalse(
            brazil.analyzerModeSection.isAncestorOf(brazil.textEdit_S3_TIME_2)
        )
        brazil.radio_dewetron.setChecked(True)
        self.app.processEvents()
        self.assertTrue(brazil.textEdit_S3_TIME_2.isEnabled())
        self.assertTrue(brazil.comboBox_S3_TIME_2.isEnabled())

        _dialog, immun = self._build_ui(Ui_Dialog_thaiguoqianpin_immun)
        rate_controls = (
            immun.checkBox_RATE,
            immun.textEdit_S2_RATE_TIME,
            immun.comboBox_S2_RATE_TIME,
        )
        for control in rate_controls:
            self.assertTrue(immun.analyzerModeSection.primary_wt_widget.isAncestorOf(control))
        immun.radio_dewetron.setChecked(True)
        self.app.processEvents()
        self.assertEqual(immun.analyzerModeSection.analyzer_stack.currentIndex(), 1)
        immun.radio_wt3000.setChecked(True)
        self.app.processEvents()
        for control in rate_controls:
            self.assertTrue(control.isEnabled())


if __name__ == "__main__":
    unittest.main()
