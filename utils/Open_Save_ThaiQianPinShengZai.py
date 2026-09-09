import re
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, \
    QFileDialog, QMessageBox
import csv
from utils.Open_Save_ThaiWT3000_Config import Save_File_ThaiWT3000_Config, Open_File_ThaiWT3000_Config
from utils.Open_Save_ThaiWT1800_Config import Save_File_ThaiWT1800_Config, Open_File_ThaiWT1800_Config
from utils.Open_Save_ThaiWT1806E_Config import Save_File_ThaiWT1806E_Config, Open_File_ThaiWT1806E_Config
from utils.Open_Save_ThaiWT5000_Config import Save_File_ThaiWT5000_Config, Open_File_ThaiWT5000_Config
from utils.Open_Save_ThaiXieBoDianLiu import _PageWidgetFinder
from dewetron_autotest import (
    PROJECT_SPECS,
    append_dewetron_tail_columns,
    extract_ui_config,
    extract_ui_mode,
    read_dewetron_tail_columns,
)

_DEWETRON_SPEC = PROJECT_SPECS["欠频升载"]


def _append_dewetron_tail(values, ui):
    """Append or update this project's named DEWETRON persistence tail."""
    section = getattr(ui, "analyzerModeSection", None)
    source = section if section is not None else ui
    return append_dewetron_tail_columns(
        arrayRow1,
        values,
        extract_ui_config(source),
        mode=extract_ui_mode(source),
        test_type=_DEWETRON_SPEC.test_type,
        profile=_DEWETRON_SPEC.profile,
    )


def _restore_dewetron_tail(headers, values, ui):
    """Restore named DEWETRON data without requiring a newer dialog build."""
    try:
        mode, config = read_dewetron_tail_columns(headers, values)
    except (IndexError, TypeError, ValueError):
        mode, config = read_dewetron_tail_columns([], [])
    section = getattr(ui, "analyzerModeSection", None)
    if section is not None:
        set_config = getattr(section, "set_dewetron_config", None)
        if not callable(set_config):
            set_config = getattr(section, "set_config", None)
        if callable(set_config):
            set_config(config)
        set_mode = getattr(section, "set_mode", None)
        if callable(set_mode):
            set_mode(mode)
    return mode, config


arrayRow1 = ['Style',
    'checkBox_S1',
        'comboBox_S1_AC',"textEdit_S1_AC_VOLT", "textEdit_S1_AC_VOLT_2", "textEdit_S1_AC_VOLT_3",
            "textEdit_S1_AC_FR","comboBox_S1_AC_2",
        "checkBox_S1_DC1", "comboBox_S1_DC1", "textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR",
            "textEdit_S1_DC1_Voc", "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF",
        "checkBox_S1_DC2", "comboBox_S1_DC2", "textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR",
            "textEdit_S1_DC2_Voc", "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF",
        "checkBox_S1_DC3", "comboBox_S1_DC3", "textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR",
            "textEdit_S1_DC3_Voc", "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF",
        "checkBox_S1_DC4", "comboBox_S1_DC4", "textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR",
            "textEdit_S1_DC4_Voc", "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF",
        "textEdit_S1_ACWaitTIME", "comboBox_S1_ACWaitTIME", "textEdit_S1_TIME", "comboBox_S1_TIME",
    'checkBox_S2', "checkBox_S2_WT3000", "checkBox_S2_WT1800", "checkBox_S2_WT1806E",
    'checkBox_S3', 'textEdit_S3_AC_VOLT', 'textEdit_S3_AC_FR', 'textEdit_S3_TIME', 'comboBox_S3_TIME',
    'checkBox_S4', 'textEdit_S4_AC_VOLT', 'textEdit_S4_AC_FR', 'textEdit_S4_TIME', 'comboBox_S4_TIME',
    'checkBox_S5', 'textEdit_S5_AC_VOLT', 'textEdit_S5_AC_FR', 'textEdit_S5_TIME', 'comboBox_S5_TIME',
    'checkBox_S6', 'textEdit_S6_AC_VOLT', 'textEdit_S6_AC_FR', 'textEdit_S6_TIME', 'comboBox_S6_TIME',
    'checkBox_S7', 'textEdit_S7_AC_VOLT', 'textEdit_S7_AC_FR', 'textEdit_S7_TIME', 'comboBox_S7_TIME',
    'checkBox_S8', 'textEdit_S8_AC_VOLT', 'textEdit_S8_AC_FR', 'textEdit_S8_TIME', 'comboBox_S8_TIME',
    'checkBox_S9', 'textEdit_S9_AC_VOLT', 'textEdit_S9_AC_FR', 'textEdit_S9_TIME', 'comboBox_S9_TIME',
    'checkBox_S10', 'textEdit_S10_AC_VOLT', 'textEdit_S10_AC_FR', 'textEdit_S10_TIME', 'comboBox_S10_TIME',
    'checkBox_S11', 'textEdit_S11_AC_VOLT', 'textEdit_S11_AC_FR', 'textEdit_S11_TIME', 'comboBox_S11_TIME',
    'checkBox_S12', 'textEdit_S12_AC_VOLT', 'textEdit_S12_AC_FR', 'textEdit_S12_TIME', 'comboBox_S12_TIME',
    'checkBox_S13', 'textEdit_S13_AC_VOLT', 'textEdit_S13_AC_FR', 'textEdit_S13_TIME', 'comboBox_S13_TIME',
    'checkBox_S14', 'textEdit_S14_AC_VOLT', 'textEdit_S14_AC_FR', 'textEdit_S14_TIME', 'comboBox_S14_TIME',
    'checkBox_S15', 'textEdit_S15_AC_VOLT', 'textEdit_S15_AC_FR', 'textEdit_S15_TIME', 'comboBox_S15_TIME',
    'checkBox_S16', 'textEdit_S16_AC_VOLT', 'textEdit_S16_AC_FR', 'textEdit_S16_TIME', 'comboBox_S16_TIME',
    'checkBox_S17', 'textEdit_S17_AC_VOLT', 'textEdit_S17_AC_FR', 'textEdit_S17_TIME', 'comboBox_S17_TIME',
    'checkBox_S_End', "comboBox_S_End_AC", "checkBox_S_End_DC1", "comboBox_S_End_DC1","checkBox_S_End_DC2",
        "comboBox_S_End_DC2","checkBox_S_End_DC3", "comboBox_S_End_DC3","checkBox_S_End_DC4","comboBox_S_End_DC4",
        "checkBox_S2_WT5000",
        "textEdit_FrequencyLadder", "textEdit_FrequencyLadder_VOLT",
        "textEdit_FrequencyLadder_TIME", "comboBox_FrequencyLadder_TIME"]

# 泰国欠频升载保存设定
def Save_File_ThaiQianPinShengZai(kwargs):
    dialog_windowqianpinshengzai = kwargs['dialog_windowqianpinshengzai']
    uithaiQianPinShengZai = kwargs['uiThaiQianPinShengZai']
    uiThiaWT3000E = kwargs['uiThiaWT3000E']
    uiThiaWT1800 = kwargs['uiThiaWT1800']
    uiThiaWT1806E = kwargs['uiThiaWT1806E']
    uiThiaWT5000 = kwargs['uiThiaWT5000']
    result = []
    directory1 = QFileDialog.getSaveFileName(None,"单个文件保存","./","Text Files(*.csv)")
    if directory1[0] == '':
        print('请选择一个文件')
    else:
        arrayRow2 = ['ThaiQianPinShengZai']

        if uithaiQianPinShengZai.checkBox_S1.isChecked():
            checkBox_S1 = '1'
        else:
            checkBox_S1 = '0'
        arrayRow2.append(checkBox_S1)

        comboBox_S1_AC = uithaiQianPinShengZai.comboBox_S1_AC.currentIndex()
        arrayRow2.append(comboBox_S1_AC)

        textEdit_S1_AC_VOLT = uithaiQianPinShengZai.textEdit_S1_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT)

        textEdit_S1_AC_VOLT_2 = uithaiQianPinShengZai.textEdit_S1_AC_VOLT_2.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_2)

        textEdit_S1_AC_VOLT_3 = uithaiQianPinShengZai.textEdit_S1_AC_VOLT_3.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_3)

        textEdit_S1_AC_FR = uithaiQianPinShengZai.textEdit_S1_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S1_AC_FR)

        comboBox_S1_AC_2 = uithaiQianPinShengZai.comboBox_S1_AC_2.currentIndex()
        arrayRow2.append(comboBox_S1_AC_2)

        if uithaiQianPinShengZai.checkBox_S1_DC1.isChecked():
            checkBox_S1_DC1 = '1'
        else:
            checkBox_S1_DC1 = '0'
        arrayRow2.append(checkBox_S1_DC1)

        comboBox_S1_DC1 = uithaiQianPinShengZai.comboBox_S1_DC1.currentIndex()
        arrayRow2.append(comboBox_S1_DC1)

        textEdit_S1_DC1_VOLT = uithaiQianPinShengZai.textEdit_S1_DC1_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_VOLT)

        textEdit_S1_DC1_CURR = uithaiQianPinShengZai.textEdit_S1_DC1_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_CURR)

        textEdit_S1_DC1_Voc = uithaiQianPinShengZai.textEdit_S1_DC1_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Voc)
        
        textEdit_S1_DC1_Isc = uithaiQianPinShengZai.textEdit_S1_DC1_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Isc)
        
        textEdit_S1_DC1_PF = uithaiQianPinShengZai.textEdit_S1_DC1_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF)

        if uithaiQianPinShengZai.checkBox_S1_DC2.isChecked():
            checkBox_S1_DC2 = '1'
        else:
            checkBox_S1_DC2 = '0'
        arrayRow2.append(checkBox_S1_DC2)

        comboBox_S1_DC2 = uithaiQianPinShengZai.comboBox_S1_DC2.currentIndex()
        arrayRow2.append(comboBox_S1_DC2)

        textEdit_S1_DC2_VOLT = uithaiQianPinShengZai.textEdit_S1_DC2_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_VOLT)

        textEdit_S1_DC2_CURR = uithaiQianPinShengZai.textEdit_S1_DC2_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_CURR)

        textEdit_S1_DC2_Voc = uithaiQianPinShengZai.textEdit_S1_DC2_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Voc)
        
        textEdit_S1_DC2_Isc = uithaiQianPinShengZai.textEdit_S1_DC2_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Isc)
        
        textEdit_S1_DC2_PF = uithaiQianPinShengZai.textEdit_S1_DC2_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_PF)

        if uithaiQianPinShengZai.checkBox_S1_DC3.isChecked():
            checkBox_S1_DC3 = '1'
        else:
            checkBox_S1_DC3 = '0'
        arrayRow2.append(checkBox_S1_DC3)

        comboBox_S1_DC3 = uithaiQianPinShengZai.comboBox_S1_DC3.currentIndex()
        arrayRow2.append(comboBox_S1_DC3)

        textEdit_S1_DC3_VOLT = uithaiQianPinShengZai.textEdit_S1_DC3_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_VOLT)

        textEdit_S1_DC3_CURR = uithaiQianPinShengZai.textEdit_S1_DC3_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_CURR)

        textEdit_S1_DC3_Voc = uithaiQianPinShengZai.textEdit_S1_DC3_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Voc)
        
        textEdit_S1_DC3_Isc = uithaiQianPinShengZai.textEdit_S1_DC3_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Isc)
        
        textEdit_S1_DC3_PF = uithaiQianPinShengZai.textEdit_S1_DC3_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_PF)

        if uithaiQianPinShengZai.checkBox_S1_DC4.isChecked():
            checkBox_S1_DC4 = '1'
        else:
            checkBox_S1_DC4 = '0'
        arrayRow2.append(checkBox_S1_DC4)

        comboBox_S1_DC4 = uithaiQianPinShengZai.comboBox_S1_DC4.currentIndex()
        arrayRow2.append(comboBox_S1_DC4)

        textEdit_S1_DC4_VOLT = uithaiQianPinShengZai.textEdit_S1_DC4_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_VOLT)

        textEdit_S1_DC4_CURR = uithaiQianPinShengZai.textEdit_S1_DC4_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_CURR)

        textEdit_S1_DC4_Voc = uithaiQianPinShengZai.textEdit_S1_DC4_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Voc)
        
        textEdit_S1_DC4_Isc = uithaiQianPinShengZai.textEdit_S1_DC4_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Isc)
        
        textEdit_S1_DC4_PF = uithaiQianPinShengZai.textEdit_S1_DC4_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_PF)

        textEdit_S1_ACWaitTIME = uithaiQianPinShengZai.textEdit_S1_ACWaitTIME.toPlainText()
        arrayRow2.append(textEdit_S1_ACWaitTIME)

        comboBox_S1_ACWaitTIME = uithaiQianPinShengZai.comboBox_S1_ACWaitTIME.currentIndex()
        arrayRow2.append(comboBox_S1_ACWaitTIME)

        textEdit_S1_TIME = uithaiQianPinShengZai.textEdit_S1_TIME.toPlainText()
        arrayRow2.append(textEdit_S1_TIME)

        comboBox_S1_TIME = uithaiQianPinShengZai.comboBox_S1_TIME.currentIndex()
        arrayRow2.append(comboBox_S1_TIME)
        
        # step2
        if uithaiQianPinShengZai.checkBox_S2.isChecked():
            checkBox_S2 = '1'
        else:
            checkBox_S2 = '0'
        arrayRow2.append(checkBox_S2)

        if uithaiQianPinShengZai.radioButton_S2_WT3000.isChecked():
            checkBox_S2_WT3000 = '1'
        else:
            checkBox_S2_WT3000 = '0'
        arrayRow2.append(checkBox_S2_WT3000)

        if uithaiQianPinShengZai.radioButton_S2_WT1800.isChecked():
            checkBox_S2_WT1800 = '1'
        else:
            checkBox_S2_WT1800 = '0'
        arrayRow2.append(checkBox_S2_WT1800)

        if uithaiQianPinShengZai.radioButton_S2_WT1806E.isChecked():
            checkBox_S2_WT1806E = '1'
        else:
            checkBox_S2_WT1806E = '0'
        arrayRow2.append(checkBox_S2_WT1806E)

        # step3
        if uithaiQianPinShengZai.checkBox_S3.isChecked():
            checkBox_S3 = '1'
        else:
            checkBox_S3 = '0'
        arrayRow2.append(checkBox_S3)

        textEdit_S3_AC_VOLT = uithaiQianPinShengZai.textEdit_S3_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT)

        textEdit_S3_AC_FR = uithaiQianPinShengZai.textEdit_S3_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S3_AC_FR)

        textEdit_S3_TIME = uithaiQianPinShengZai.textEdit_S3_TIME.toPlainText()
        arrayRow2.append(textEdit_S3_TIME)

        comboBox_S3_TIME = uithaiQianPinShengZai.comboBox_S3_TIME.currentIndex()
        arrayRow2.append(comboBox_S3_TIME)

        # step4
        if uithaiQianPinShengZai.checkBox_S4.isChecked():
            checkBox_S4 = '1'
        else:
            checkBox_S4 = '0'
        arrayRow2.append(checkBox_S4)

        textEdit_S4_AC_VOLT = uithaiQianPinShengZai.textEdit_S4_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S4_AC_VOLT)

        textEdit_S4_AC_FR = uithaiQianPinShengZai.textEdit_S4_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S4_AC_FR)

        textEdit_S4_TIME = uithaiQianPinShengZai.textEdit_S4_TIME.toPlainText()
        arrayRow2.append(textEdit_S4_TIME)

        comboBox_S4_TIME = uithaiQianPinShengZai.comboBox_S4_TIME.currentIndex()
        arrayRow2.append(comboBox_S4_TIME)

        # step5
        if uithaiQianPinShengZai.checkBox_S5.isChecked():
            checkBox_S5 = '1'
        else:
            checkBox_S5 = '0'
        arrayRow2.append(checkBox_S5)

        textEdit_S5_AC_VOLT = uithaiQianPinShengZai.textEdit_S5_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S5_AC_VOLT)

        textEdit_S5_AC_FR = uithaiQianPinShengZai.textEdit_S5_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S5_AC_FR)

        textEdit_S5_TIME = uithaiQianPinShengZai.textEdit_S5_TIME.toPlainText()
        arrayRow2.append(textEdit_S5_TIME)

        comboBox_S5_TIME = uithaiQianPinShengZai.comboBox_S5_TIME.currentIndex()
        arrayRow2.append(comboBox_S5_TIME)

        # step6
        if uithaiQianPinShengZai.checkBox_S6.isChecked():
            checkBox_S6 = '1'
        else:
            checkBox_S6 = '0'
        arrayRow2.append(checkBox_S6)

        textEdit_S6_AC_VOLT = uithaiQianPinShengZai.textEdit_S6_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S6_AC_VOLT)

        textEdit_S6_AC_FR = uithaiQianPinShengZai.textEdit_S6_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S6_AC_FR)

        textEdit_S6_TIME = uithaiQianPinShengZai.textEdit_S6_TIME.toPlainText()
        arrayRow2.append(textEdit_S6_TIME)

        comboBox_S6_TIME = uithaiQianPinShengZai.comboBox_S6_TIME.currentIndex()
        arrayRow2.append(comboBox_S6_TIME)

        # step7
        if uithaiQianPinShengZai.checkBox_S7.isChecked():
            checkBox_S7 = '1'
        else:
            checkBox_S7 = '0'
        arrayRow2.append(checkBox_S7)

        textEdit_S7_AC_VOLT = uithaiQianPinShengZai.textEdit_S7_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S7_AC_VOLT)

        textEdit_S7_AC_FR = uithaiQianPinShengZai.textEdit_S7_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S7_AC_FR)

        textEdit_S7_TIME = uithaiQianPinShengZai.textEdit_S7_TIME.toPlainText()
        arrayRow2.append(textEdit_S7_TIME)

        comboBox_S7_TIME = uithaiQianPinShengZai.comboBox_S7_TIME.currentIndex()
        arrayRow2.append(comboBox_S7_TIME)

        # step8
        if uithaiQianPinShengZai.checkBox_S8.isChecked():
            checkBox_S8 = '1'
        else:
            checkBox_S8 = '0'
        arrayRow2.append(checkBox_S8)

        textEdit_S8_AC_VOLT = uithaiQianPinShengZai.textEdit_S8_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S8_AC_VOLT)

        textEdit_S8_AC_FR = uithaiQianPinShengZai.textEdit_S8_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S8_AC_FR)

        textEdit_S8_TIME = uithaiQianPinShengZai.textEdit_S8_TIME.toPlainText()
        arrayRow2.append(textEdit_S8_TIME)

        comboBox_S8_TIME = uithaiQianPinShengZai.comboBox_S8_TIME.currentIndex()
        arrayRow2.append(comboBox_S8_TIME)

        # step9
        if uithaiQianPinShengZai.checkBox_S9.isChecked():
            checkBox_S9 = '1'
        else:
            checkBox_S9 = '0'
        arrayRow2.append(checkBox_S9)

        textEdit_S9_AC_VOLT = uithaiQianPinShengZai.textEdit_S9_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S9_AC_VOLT)

        textEdit_S9_AC_FR = uithaiQianPinShengZai.textEdit_S9_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S9_AC_FR)

        textEdit_S9_TIME = uithaiQianPinShengZai.textEdit_S9_TIME.toPlainText()
        arrayRow2.append(textEdit_S9_TIME)

        comboBox_S9_TIME = uithaiQianPinShengZai.comboBox_S9_TIME.currentIndex()
        arrayRow2.append(comboBox_S9_TIME)

        # step10
        if uithaiQianPinShengZai.checkBox_S10.isChecked():
            checkBox_S10 = '1'
        else:
            checkBox_S10 = '0'
        arrayRow2.append(checkBox_S10)

        textEdit_S10_AC_VOLT = uithaiQianPinShengZai.textEdit_S10_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S10_AC_VOLT)

        textEdit_S10_AC_FR = uithaiQianPinShengZai.textEdit_S10_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S10_AC_FR)

        textEdit_S10_TIME = uithaiQianPinShengZai.textEdit_S10_TIME.toPlainText()
        arrayRow2.append(textEdit_S10_TIME)

        comboBox_S10_TIME = uithaiQianPinShengZai.comboBox_S10_TIME.currentIndex()
        arrayRow2.append(comboBox_S10_TIME)

        # step11
        if uithaiQianPinShengZai.checkBox_S11.isChecked():
            checkBox_S11 = '1'
        else:
            checkBox_S11 = '0'
        arrayRow2.append(checkBox_S11)

        textEdit_S11_AC_VOLT = uithaiQianPinShengZai.textEdit_S11_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S11_AC_VOLT)

        textEdit_S11_AC_FR = uithaiQianPinShengZai.textEdit_S11_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S11_AC_FR)

        textEdit_S11_TIME = uithaiQianPinShengZai.textEdit_S11_TIME.toPlainText()
        arrayRow2.append(textEdit_S11_TIME)

        comboBox_S11_TIME = uithaiQianPinShengZai.comboBox_S11_TIME.currentIndex()
        arrayRow2.append(comboBox_S11_TIME)

        # step12
        if uithaiQianPinShengZai.checkBox_S12.isChecked():
            checkBox_S12 = '1'
        else:
            checkBox_S12 = '0'
        arrayRow2.append(checkBox_S12)

        textEdit_S12_AC_VOLT = uithaiQianPinShengZai.textEdit_S12_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S12_AC_VOLT)

        textEdit_S12_AC_FR = uithaiQianPinShengZai.textEdit_S12_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S12_AC_FR)

        textEdit_S12_TIME = uithaiQianPinShengZai.textEdit_S12_TIME.toPlainText()
        arrayRow2.append(textEdit_S12_TIME)

        comboBox_S12_TIME = uithaiQianPinShengZai.comboBox_S12_TIME.currentIndex()
        arrayRow2.append(comboBox_S12_TIME)

        # step13
        if uithaiQianPinShengZai.checkBox_S13.isChecked():
            checkBox_S13 = '1'
        else:
            checkBox_S13 = '0'
        arrayRow2.append(checkBox_S13)

        textEdit_S13_AC_VOLT = uithaiQianPinShengZai.textEdit_S13_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S13_AC_VOLT)

        textEdit_S13_AC_FR = uithaiQianPinShengZai.textEdit_S13_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S13_AC_FR)

        textEdit_S13_TIME = uithaiQianPinShengZai.textEdit_S13_TIME.toPlainText()
        arrayRow2.append(textEdit_S13_TIME)

        comboBox_S13_TIME = uithaiQianPinShengZai.comboBox_S13_TIME.currentIndex()
        arrayRow2.append(comboBox_S13_TIME)

        # step14
        if uithaiQianPinShengZai.checkBox_S14.isChecked():
            checkBox_S14 = '1'
        else:
            checkBox_S14 = '0'
        arrayRow2.append(checkBox_S14)

        textEdit_S14_AC_VOLT = uithaiQianPinShengZai.textEdit_S14_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S14_AC_VOLT)

        textEdit_S14_AC_FR = uithaiQianPinShengZai.textEdit_S14_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S14_AC_FR)

        textEdit_S14_TIME = uithaiQianPinShengZai.textEdit_S14_TIME.toPlainText()
        arrayRow2.append(textEdit_S14_TIME)

        comboBox_S14_TIME = uithaiQianPinShengZai.comboBox_S14_TIME.currentIndex()
        arrayRow2.append(comboBox_S14_TIME)

        # step15
        if uithaiQianPinShengZai.checkBox_S15.isChecked():
            checkBox_S15 = '1'
        else:
            checkBox_S15 = '0'
        arrayRow2.append(checkBox_S15)

        textEdit_S15_AC_VOLT = uithaiQianPinShengZai.textEdit_S15_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S15_AC_VOLT)

        textEdit_S15_AC_FR = uithaiQianPinShengZai.textEdit_S15_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S15_AC_FR)

        textEdit_S15_TIME = uithaiQianPinShengZai.textEdit_S15_TIME.toPlainText()
        arrayRow2.append(textEdit_S15_TIME)

        comboBox_S15_TIME = uithaiQianPinShengZai.comboBox_S15_TIME.currentIndex()
        arrayRow2.append(comboBox_S15_TIME)

        # step16
        if uithaiQianPinShengZai.checkBox_S16.isChecked():
            checkBox_S16 = '1'
        else:
            checkBox_S16 = '0'
        arrayRow2.append(checkBox_S16)

        textEdit_S16_AC_VOLT = uithaiQianPinShengZai.textEdit_S16_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S16_AC_VOLT)

        textEdit_S16_AC_FR = uithaiQianPinShengZai.textEdit_S16_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S16_AC_FR)

        textEdit_S16_TIME = uithaiQianPinShengZai.textEdit_S16_TIME.toPlainText()
        arrayRow2.append(textEdit_S16_TIME)

        comboBox_S16_TIME = uithaiQianPinShengZai.comboBox_S16_TIME.currentIndex()
        arrayRow2.append(comboBox_S16_TIME)
        
        # step17
        if uithaiQianPinShengZai.checkBox_S17.isChecked():
            checkBox_S17 = '1'
        else:
            checkBox_S17 = '0'
        arrayRow2.append(checkBox_S17)

        textEdit_S17_AC_VOLT = uithaiQianPinShengZai.textEdit_S17_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S17_AC_VOLT)

        textEdit_S17_AC_FR = uithaiQianPinShengZai.textEdit_S17_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S17_AC_FR)

        textEdit_S17_TIME = uithaiQianPinShengZai.textEdit_S17_TIME.toPlainText()
        arrayRow2.append(textEdit_S17_TIME)

        comboBox_S17_TIME = uithaiQianPinShengZai.comboBox_S17_TIME.currentIndex()
        arrayRow2.append(comboBox_S17_TIME)

        # step_end
        if uithaiQianPinShengZai.checkBox_S_End.isChecked():
            checkBox_S_End = '1'
        else:
            checkBox_S_End = '0'
        arrayRow2.append(checkBox_S_End)

        comboBox_S_End_AC = uithaiQianPinShengZai.comboBox_S_End_AC.currentIndex()
        arrayRow2.append(comboBox_S_End_AC)

        if uithaiQianPinShengZai.checkBox_S_End_DC1.isChecked():
            checkBox_S_End_DC1 = '1'
        else:
            checkBox_S_End_DC1 = '0'
        arrayRow2.append(checkBox_S_End_DC1)

        comboBox_S_End_DC1 = uithaiQianPinShengZai.comboBox_S_End_DC1.currentIndex()
        arrayRow2.append(comboBox_S_End_DC1)

        if uithaiQianPinShengZai.checkBox_S_End_DC2.isChecked():
            checkBox_S_End_DC2 = '1'
        else:
            checkBox_S_End_DC2 = '0'
        arrayRow2.append(checkBox_S_End_DC2)

        comboBox_S_End_DC2 = uithaiQianPinShengZai.comboBox_S_End_DC2.currentIndex()
        arrayRow2.append(comboBox_S_End_DC2)

        if uithaiQianPinShengZai.checkBox_S_End_DC3.isChecked():
            checkBox_S_End_DC3 = '1'
        else:
            checkBox_S_End_DC3 = '0'
        arrayRow2.append(checkBox_S_End_DC3)

        comboBox_S_End_DC3 = uithaiQianPinShengZai.comboBox_S_End_DC3.currentIndex()
        arrayRow2.append(comboBox_S_End_DC3)

        if uithaiQianPinShengZai.checkBox_S_End_DC4.isChecked():
            checkBox_S_End_DC4 = '1'
        else:
            checkBox_S_End_DC4 = '0'
        arrayRow2.append(checkBox_S_End_DC4)

        comboBox_S_End_DC4 = uithaiQianPinShengZai.comboBox_S_End_DC4.currentIndex()
        arrayRow2.append(comboBox_S_End_DC4)

        if uithaiQianPinShengZai.radioButton_S2_WT5000.isChecked():
            checkBox_S2_WT5000 = '1'
        else:
            checkBox_S2_WT5000 = '0'
        arrayRow2.append(checkBox_S2_WT5000)

        try:
            from utils.overfreq_ladder_commands import sync_freq_list_to_legacy_cards
            sync_freq_list_to_legacy_cards(uithaiQianPinShengZai)
        except Exception:
            pass
        _fl = getattr(uithaiQianPinShengZai, "textEdit_FrequencyLadder", None)
        _flv = getattr(uithaiQianPinShengZai, "textEdit_FrequencyLadder_VOLT", None)
        _flt = getattr(uithaiQianPinShengZai, "textEdit_FrequencyLadder_TIME", None)
        _flu = getattr(uithaiQianPinShengZai, "comboBox_FrequencyLadder_TIME", None)
        arrayRow2.append(_fl.toPlainText() if _fl is not None else "")
        arrayRow2.append(_flv.toPlainText() if _flv is not None else "230")
        arrayRow2.append(_flt.toPlainText() if _flt is not None else "60")
        arrayRow2.append(_flu.currentIndex() if _flu is not None else 0)

        _append_dewetron_tail(arrayRow2, uithaiQianPinShengZai)

        if uithaiQianPinShengZai.radioButton_S2_WT3000.isChecked():
            result = Save_File_ThaiWT3000_Config(_PageWidgetFinder(uithaiQianPinShengZai._wtStacked.widget(0)))

        if uithaiQianPinShengZai.radioButton_S2_WT1800.isChecked():
            result = Save_File_ThaiWT1800_Config(_PageWidgetFinder(uithaiQianPinShengZai._wtStacked.widget(1)))

        if uithaiQianPinShengZai.radioButton_S2_WT1806E.isChecked():
            result = Save_File_ThaiWT1806E_Config(_PageWidgetFinder(uithaiQianPinShengZai._wtStacked.widget(2)))

        if uithaiQianPinShengZai.radioButton_S2_WT5000.isChecked():
            result = Save_File_ThaiWT5000_Config(_PageWidgetFinder(uithaiQianPinShengZai._wtStacked.widget(3)))

        out = open(directory1[0], 'w+', newline='', encoding='utf-8-sig')
        csv_write = csv.writer(out, dialect="excel")
        csv_write.writerow(arrayRow1)
        csv_write.writerow(arrayRow2)
        if len(result) > 0:
            csv_write.writerow(result[0])
            csv_write.writerow(result[1])
        out.close()
        QMessageBox.information(None, "实验设定提示信息", "欠频升载文件保存完成", QMessageBox.Ok, QMessageBox.Ok)

# 欠频升载取设定
def Open_File_ThaiQianPinShengZai(kwargs):
    dialog_windowqianpinshengzai = kwargs['dialog_windowqianpinshengzai']
    uithaiQianPinShengZai = kwargs['uiThaiQianPinShengZai']
    uiThiaWT3000E = kwargs['uiThiaWT3000E']
    uiThiaWT1800 = kwargs['uiThiaWT1800']
    uiThiaWT1806E = kwargs['uiThiaWT1806E']
    uiThiaWT5000 = kwargs['uiThiaWT5000']
    strFlag  = "0"
    result_list = []
    config_dict = {}
    wt_config_dict = {}
    directory1 = QFileDialog.getOpenFileName(None,"单个文件选择","./","Text Files(*.csv)")
    if directory1[0] == '':
        print("请选择一个文件")
    else:
        try:
            f = open(directory1[0], 'r', encoding='utf-8-sig')
            f.read(1)
            f.seek(0)
        except UnicodeDecodeError:
            f = open(directory1[0], 'r', encoding='gbk')
        with f:
            data = csv.reader(f)
            for line in data:
                result_list.append(list(line))
        
        if len(result_list) == 2:
            delta_len = int(len(result_list[0]) - len(result_list[1]))
            if delta_len > 0:
                extend_list = ['' for k in range(delta_len)]
                result_list[1].extend(extend_list)
            config_dict = dict(zip(result_list[0], result_list[1]))
        if len(result_list) == 4:
            delta_len1 = int(len(result_list[0]) - len(result_list[1]))
            if delta_len1 > 0:
                extend_list1 = ['' for k in range(delta_len1)]
                result_list[1].extend(extend_list1)
            delta_len2 = int(len(result_list[2]) - len(result_list[3]))
            if delta_len2 > 0:
                extend_list2 = ['' for k in range(delta_len2)]
                result_list[3].extend(extend_list2)
            config_dict = dict(zip(result_list[0],result_list[1]))
            wt_config_dict = dict(zip(result_list[2],result_list[3]))

        if config_dict != {}:
            if arrayRow1[0] in config_dict:
                if config_dict[arrayRow1[0]] == "ThaiQianPinShengZai":
                    #checkBox
                    if strFlag == "0":
                        if arrayRow1[1] in config_dict:
                            checkBox_S1 = config_dict[arrayRow1[1]]
                            if checkBox_S1 == '1':
                                uithaiQianPinShengZai.checkBox_S1.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S1.setChecked(False)
                        else:
                            strFlag = 1

                    #comBox
                    if strFlag == "0":
                        if arrayRow1[2] in config_dict:
                            comboBox_S1_AC = config_dict[arrayRow1[2]]
                            uithaiQianPinShengZai.comboBox_S1_AC.setCurrentIndex(int(comboBox_S1_AC))
                        else:
                            strFlag = 1

                    #textEdit
                    if strFlag == "0":
                        if arrayRow1[3] in config_dict:
                            textEdit_S1_AC_VOLT = config_dict[arrayRow1[3]]
                            uithaiQianPinShengZai.textEdit_S1_AC_VOLT.setText(textEdit_S1_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[4] in config_dict:
                            textEdit_S1_AC_VOLT_2 = config_dict[arrayRow1[4]]
                            uithaiQianPinShengZai.textEdit_S1_AC_VOLT_2.setText(textEdit_S1_AC_VOLT_2)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[5] in config_dict:
                            textEdit_S1_AC_VOLT_3 = config_dict[arrayRow1[5]]
                            uithaiQianPinShengZai.textEdit_S1_AC_VOLT_3.setText(textEdit_S1_AC_VOLT_3)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[6] in config_dict:
                            textEdit_S1_AC_FR = config_dict[arrayRow1[6]]
                            uithaiQianPinShengZai.textEdit_S1_AC_FR.setText(textEdit_S1_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[7] in config_dict:
                            comboBox_S1_AC_2 = config_dict[arrayRow1[7]]
                            uithaiQianPinShengZai.comboBox_S1_AC_2.setCurrentIndex(int(comboBox_S1_AC_2))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[8] in config_dict:
                            checkBox_S1_DC1 = config_dict[arrayRow1[8]]
                            if checkBox_S1_DC1 == '1':
                                uithaiQianPinShengZai.checkBox_S1_DC1.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S1_DC1.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[9] in config_dict:
                            comboBox_S1_DC1 = config_dict[arrayRow1[9]]
                            uithaiQianPinShengZai.comboBox_S1_DC1.setCurrentIndex(int(comboBox_S1_DC1))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[10] in config_dict:
                            textEdit_S1_DC1_VOLT = config_dict[arrayRow1[10]]
                            uithaiQianPinShengZai.textEdit_S1_DC1_VOLT.setText(textEdit_S1_DC1_VOLT)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[11] in config_dict:
                            textEdit_S1_DC1_CURR = config_dict[arrayRow1[11]]
                            uithaiQianPinShengZai.textEdit_S1_DC1_CURR.setText(textEdit_S1_DC1_CURR)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[12] in config_dict:
                            textEdit_S1_DC1_Voc = config_dict[arrayRow1[12]]
                            uithaiQianPinShengZai.textEdit_S1_DC1_Voc.setText(textEdit_S1_DC1_Voc)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[13] in config_dict:
                            textEdit_S1_DC1_Isc = config_dict[arrayRow1[13]]
                            uithaiQianPinShengZai.textEdit_S1_DC1_Isc.setText(textEdit_S1_DC1_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[14] in config_dict:
                            textEdit_S1_DC1_PF = config_dict[arrayRow1[14]]
                            uithaiQianPinShengZai.textEdit_S1_DC1_PF.setText(textEdit_S1_DC1_PF)
                        else:
                            strFlag = 1
                            
                    if strFlag == "0":
                        if arrayRow1[15] in config_dict:
                            checkBox_S1_DC2 = config_dict[arrayRow1[15]]
                            if checkBox_S1_DC2 == '1':
                                uithaiQianPinShengZai.checkBox_S1_DC2.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S1_DC2.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[16] in config_dict:
                            comboBox_S1_DC2 = config_dict[arrayRow1[16]]
                            uithaiQianPinShengZai.comboBox_S1_DC2.setCurrentIndex(int(comboBox_S1_DC2))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[17] in config_dict:
                            textEdit_S1_DC2_VOLT = config_dict[arrayRow1[17]]
                            uithaiQianPinShengZai.textEdit_S1_DC2_VOLT.setText(textEdit_S1_DC2_VOLT)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[18] in config_dict:
                            textEdit_S1_DC2_CURR = config_dict[arrayRow1[18]]
                            uithaiQianPinShengZai.textEdit_S1_DC2_CURR.setText(textEdit_S1_DC2_CURR)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[19] in config_dict:
                            textEdit_S1_DC2_Voc = config_dict[arrayRow1[19]]
                            uithaiQianPinShengZai.textEdit_S1_DC2_Voc.setText(textEdit_S1_DC2_Voc)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[20] in config_dict:
                            textEdit_S1_DC2_Isc = config_dict[arrayRow1[20]]
                            uithaiQianPinShengZai.textEdit_S1_DC2_Isc.setText(textEdit_S1_DC2_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[21] in config_dict:
                            textEdit_S1_DC2_PF = config_dict[arrayRow1[21]]
                            uithaiQianPinShengZai.textEdit_S1_DC2_PF.setText(textEdit_S1_DC2_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[22] in config_dict:
                            checkBox_S1_DC3 = config_dict[arrayRow1[22]]
                            if checkBox_S1_DC3 == '1':
                                uithaiQianPinShengZai.checkBox_S1_DC3.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S1_DC3.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[23] in config_dict:
                            comboBox_S1_DC3 = config_dict[arrayRow1[23]]
                            uithaiQianPinShengZai.comboBox_S1_DC3.setCurrentIndex(int(comboBox_S1_DC3))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[24] in config_dict:
                            textEdit_S1_DC3_VOLT = config_dict[arrayRow1[24]]
                            uithaiQianPinShengZai.textEdit_S1_DC3_VOLT.setText(textEdit_S1_DC3_VOLT)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[25] in config_dict:
                            textEdit_S1_DC3_CURR = config_dict[arrayRow1[25]]
                            uithaiQianPinShengZai.textEdit_S1_DC3_CURR.setText(textEdit_S1_DC3_CURR)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[26] in config_dict:
                            textEdit_S1_DC3_Voc = config_dict[arrayRow1[26]]
                            uithaiQianPinShengZai.textEdit_S1_DC3_Voc.setText(textEdit_S1_DC3_Voc)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[27] in config_dict:
                            textEdit_S1_DC3_Isc = config_dict[arrayRow1[27]]
                            uithaiQianPinShengZai.textEdit_S1_DC3_Isc.setText(textEdit_S1_DC3_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[28] in config_dict:
                            textEdit_S1_DC3_PF = config_dict[arrayRow1[28]]
                            uithaiQianPinShengZai.textEdit_S1_DC3_PF.setText(textEdit_S1_DC3_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[29] in config_dict:
                            checkBox_S1_DC4 = config_dict[arrayRow1[29]]
                            if checkBox_S1_DC4 == '1':
                                uithaiQianPinShengZai.checkBox_S1_DC4.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S1_DC4.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[30] in config_dict:
                            comboBox_S1_DC4 = config_dict[arrayRow1[30]]
                            uithaiQianPinShengZai.comboBox_S1_DC4.setCurrentIndex(int(comboBox_S1_DC4))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[31] in config_dict:
                            textEdit_S1_DC4_VOLT = config_dict[arrayRow1[31]]
                            uithaiQianPinShengZai.textEdit_S1_DC4_VOLT.setText(textEdit_S1_DC4_VOLT)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[32] in config_dict:
                            textEdit_S1_DC4_CURR = config_dict[arrayRow1[32]]
                            uithaiQianPinShengZai.textEdit_S1_DC4_CURR.setText(textEdit_S1_DC4_CURR)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[33] in config_dict:
                            textEdit_S1_DC4_Voc = config_dict[arrayRow1[33]]
                            uithaiQianPinShengZai.textEdit_S1_DC4_Voc.setText(textEdit_S1_DC4_Voc)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[34] in config_dict:
                            textEdit_S1_DC4_Isc = config_dict[arrayRow1[34]]
                            uithaiQianPinShengZai.textEdit_S1_DC4_Isc.setText(textEdit_S1_DC4_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[35] in config_dict:
                            textEdit_S1_DC4_PF = config_dict[arrayRow1[35]]
                            uithaiQianPinShengZai.textEdit_S1_DC4_PF.setText(textEdit_S1_DC4_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[36] in config_dict:
                            textEdit_S1_ACWaitTIME = config_dict[arrayRow1[36]]
                            uithaiQianPinShengZai.textEdit_S1_ACWaitTIME.setText(textEdit_S1_ACWaitTIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[37] in config_dict:
                            comboBox_S1_ACWaitTIME = config_dict[arrayRow1[37]]
                            uithaiQianPinShengZai.comboBox_S1_ACWaitTIME.setCurrentIndex(int(comboBox_S1_ACWaitTIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[38] in config_dict:
                            textEdit_S1_TIME = config_dict[arrayRow1[38]]
                            uithaiQianPinShengZai.textEdit_S1_TIME.setText(textEdit_S1_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[39] in config_dict:
                            comboBox_S1_TIME = config_dict[arrayRow1[39]]
                            uithaiQianPinShengZai.comboBox_S1_TIME.setCurrentIndex(int(comboBox_S1_TIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[40] in config_dict:
                            checkBox_S2 = config_dict[arrayRow1[40]]
                            if checkBox_S2 == '1':
                                uithaiQianPinShengZai.checkBox_S2.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[41] in config_dict:
                            checkBox_S2_WT3000 = config_dict[arrayRow1[41]]
                            if checkBox_S2_WT3000 == '1':
                                uithaiQianPinShengZai.radioButton_S2_WT3000.setChecked(True)
                            else:
                                uithaiQianPinShengZai.radioButton_S2_WT3000.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[42] in config_dict:
                            checkBox_S2_WT1800 = config_dict[arrayRow1[42]]
                            if checkBox_S2_WT1800 == '1':
                                uithaiQianPinShengZai.radioButton_S2_WT1800.setChecked(True)
                            else:
                                uithaiQianPinShengZai.radioButton_S2_WT1800.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[43] in config_dict:
                            checkBox_S2_WT1806E = config_dict[arrayRow1[43]]
                            if checkBox_S2_WT1806E == '1':
                                uithaiQianPinShengZai.radioButton_S2_WT1806E.setChecked(True)
                            else:
                                uithaiQianPinShengZai.radioButton_S2_WT1806E.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[44] in config_dict:
                            checkBox_S3 = config_dict[arrayRow1[44]]
                            if checkBox_S3 == '1':
                                uithaiQianPinShengZai.checkBox_S3.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[45] in config_dict:
                            textEdit_S3_AC_VOLT = config_dict[arrayRow1[45]]
                            uithaiQianPinShengZai.textEdit_S3_AC_VOLT.setText(textEdit_S3_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[46] in config_dict:
                            textEdit_S3_AC_FR = config_dict[arrayRow1[46]]
                            uithaiQianPinShengZai.textEdit_S3_AC_FR.setText(textEdit_S3_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[47] in config_dict:
                            textEdit_S3_TIME = config_dict[arrayRow1[47]]
                            uithaiQianPinShengZai.textEdit_S3_TIME.setText(textEdit_S3_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[48] in config_dict:
                            comboBox_S3_TIME = config_dict[arrayRow1[48]]
                            uithaiQianPinShengZai.comboBox_S3_TIME.setCurrentIndex(int(comboBox_S3_TIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[49] in config_dict:
                            checkBox_S4 = config_dict[arrayRow1[49]]
                            if checkBox_S4 == '1':
                                uithaiQianPinShengZai.checkBox_S4.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[50] in config_dict:
                            textEdit_S4_AC_VOLT = config_dict[arrayRow1[50]]
                            uithaiQianPinShengZai.textEdit_S4_AC_VOLT.setText(textEdit_S4_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[51] in config_dict:
                            textEdit_S4_AC_FR = config_dict[arrayRow1[51]]
                            uithaiQianPinShengZai.textEdit_S4_AC_FR.setText(textEdit_S4_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[52] in config_dict:
                            textEdit_S4_TIME = config_dict[arrayRow1[52]]
                            uithaiQianPinShengZai.textEdit_S4_TIME.setText(textEdit_S4_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[53] in config_dict:
                            comboBox_S4_TIME = config_dict[arrayRow1[53]]
                            uithaiQianPinShengZai.comboBox_S4_TIME.setCurrentIndex(int(comboBox_S4_TIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[54] in config_dict:
                            checkBox_S5 = config_dict[arrayRow1[54]]
                            if checkBox_S5 == '1':
                                uithaiQianPinShengZai.checkBox_S5.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S5.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[55] in config_dict:
                            textEdit_S5_AC_VOLT = config_dict[arrayRow1[55]]
                            uithaiQianPinShengZai.textEdit_S5_AC_VOLT.setText(textEdit_S5_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[56] in config_dict:
                            textEdit_S5_AC_FR = config_dict[arrayRow1[56]]
                            uithaiQianPinShengZai.textEdit_S5_AC_FR.setText(textEdit_S5_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[57] in config_dict:
                            textEdit_S5_TIME = config_dict[arrayRow1[57]]
                            uithaiQianPinShengZai.textEdit_S5_TIME.setText(textEdit_S5_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[58] in config_dict:
                            comboBox_S5_TIME = config_dict[arrayRow1[58]]
                            uithaiQianPinShengZai.comboBox_S5_TIME.setCurrentIndex(int(comboBox_S5_TIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[59] in config_dict:
                            checkBox_S6 = config_dict[arrayRow1[59]]
                            if checkBox_S6 == '1':
                                uithaiQianPinShengZai.checkBox_S6.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S6.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[60] in config_dict:
                            textEdit_S6_AC_VOLT = config_dict[arrayRow1[60]]
                            uithaiQianPinShengZai.textEdit_S6_AC_VOLT.setText(textEdit_S6_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[61] in config_dict:
                            textEdit_S6_AC_FR = config_dict[arrayRow1[61]]
                            uithaiQianPinShengZai.textEdit_S6_AC_FR.setText(textEdit_S6_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[62] in config_dict:
                            textEdit_S6_TIME = config_dict[arrayRow1[62]]
                            uithaiQianPinShengZai.textEdit_S6_TIME.setText(textEdit_S6_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[63] in config_dict:
                            comboBox_S6_TIME = config_dict[arrayRow1[63]]
                            uithaiQianPinShengZai.comboBox_S6_TIME.setCurrentIndex(int(comboBox_S6_TIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[64] in config_dict:
                            checkBox_S7 = config_dict[arrayRow1[64]]
                            if checkBox_S7 == '1':
                                uithaiQianPinShengZai.checkBox_S7.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S7.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[65] in config_dict:
                            textEdit_S7_AC_VOLT = config_dict[arrayRow1[65]]
                            uithaiQianPinShengZai.textEdit_S7_AC_VOLT.setText(textEdit_S7_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[66] in config_dict:
                            textEdit_S7_AC_FR = config_dict[arrayRow1[66]]
                            uithaiQianPinShengZai.textEdit_S7_AC_FR.setText(textEdit_S7_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[67] in config_dict:
                            textEdit_S7_TIME = config_dict[arrayRow1[67]]
                            uithaiQianPinShengZai.textEdit_S7_TIME.setText(textEdit_S7_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[68] in config_dict:
                            comboBox_S7_TIME = config_dict[arrayRow1[68]]
                            uithaiQianPinShengZai.comboBox_S7_TIME.setCurrentIndex(int(comboBox_S7_TIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[69] in config_dict:
                            checkBox_S8 = config_dict[arrayRow1[69]]
                            if checkBox_S8 == '1':
                                uithaiQianPinShengZai.checkBox_S8.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S8.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[70] in config_dict:
                            textEdit_S8_AC_VOLT = config_dict[arrayRow1[70]]
                            uithaiQianPinShengZai.textEdit_S8_AC_VOLT.setText(textEdit_S8_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[71] in config_dict:
                            textEdit_S8_AC_FR = config_dict[arrayRow1[71]]
                            uithaiQianPinShengZai.textEdit_S8_AC_FR.setText(textEdit_S8_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[72] in config_dict:
                            textEdit_S8_TIME = config_dict[arrayRow1[72]]
                            uithaiQianPinShengZai.textEdit_S8_TIME.setText(textEdit_S8_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[73] in config_dict:
                            comboBox_S8_TIME = config_dict[arrayRow1[73]]
                            uithaiQianPinShengZai.comboBox_S8_TIME.setCurrentIndex(int(comboBox_S8_TIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[74] in config_dict:
                            checkBox_S9 = config_dict[arrayRow1[74]]
                            if checkBox_S9 == '1':
                                uithaiQianPinShengZai.checkBox_S9.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S9.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[75] in config_dict:
                            textEdit_S9_AC_VOLT = config_dict[arrayRow1[75]]
                            uithaiQianPinShengZai.textEdit_S9_AC_VOLT.setText(textEdit_S9_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[76] in config_dict:
                            textEdit_S9_AC_FR = config_dict[arrayRow1[76]]
                            uithaiQianPinShengZai.textEdit_S9_AC_FR.setText(textEdit_S9_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[77] in config_dict:
                            textEdit_S9_TIME = config_dict[arrayRow1[77]]
                            uithaiQianPinShengZai.textEdit_S9_TIME.setText(textEdit_S9_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[78] in config_dict:
                            comboBox_S9_TIME = config_dict[arrayRow1[78]]
                            uithaiQianPinShengZai.comboBox_S9_TIME.setCurrentIndex(int(comboBox_S9_TIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[79] in config_dict:
                            checkBox_S10 = config_dict[arrayRow1[79]]
                            if checkBox_S10 == '1':
                                uithaiQianPinShengZai.checkBox_S10.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S10.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[80] in config_dict:
                            textEdit_S10_AC_VOLT = config_dict[arrayRow1[80]]
                            uithaiQianPinShengZai.textEdit_S10_AC_VOLT.setText(textEdit_S10_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[81] in config_dict:
                            textEdit_S10_AC_FR = config_dict[arrayRow1[81]]
                            uithaiQianPinShengZai.textEdit_S10_AC_FR.setText(textEdit_S10_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[82] in config_dict:
                            textEdit_S10_TIME = config_dict[arrayRow1[82]]
                            uithaiQianPinShengZai.textEdit_S10_TIME.setText(textEdit_S10_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[83] in config_dict:
                            comboBox_S10_TIME = config_dict[arrayRow1[83]]
                            uithaiQianPinShengZai.comboBox_S10_TIME.setCurrentIndex(int(comboBox_S10_TIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[84] in config_dict:
                            checkBox_S11 = config_dict[arrayRow1[84]]
                            if checkBox_S11 == '1':
                                uithaiQianPinShengZai.checkBox_S11.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S11.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[85] in config_dict:
                            textEdit_S11_AC_VOLT = config_dict[arrayRow1[85]]
                            uithaiQianPinShengZai.textEdit_S11_AC_VOLT.setText(textEdit_S11_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[86] in config_dict:
                            textEdit_S11_AC_FR = config_dict[arrayRow1[86]]
                            uithaiQianPinShengZai.textEdit_S11_AC_FR.setText(textEdit_S11_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[87] in config_dict:
                            textEdit_S11_TIME = config_dict[arrayRow1[87]]
                            uithaiQianPinShengZai.textEdit_S11_TIME.setText(textEdit_S11_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[88] in config_dict:
                            comboBox_S11_TIME = config_dict[arrayRow1[88]]
                            uithaiQianPinShengZai.comboBox_S11_TIME.setCurrentIndex(int(comboBox_S11_TIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[89] in config_dict:
                            checkBox_S12 = config_dict[arrayRow1[89]]
                            if checkBox_S12 == '1':
                                uithaiQianPinShengZai.checkBox_S12.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S12.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[90] in config_dict:
                            textEdit_S12_AC_VOLT = config_dict[arrayRow1[90]]
                            uithaiQianPinShengZai.textEdit_S12_AC_VOLT.setText(textEdit_S12_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[91] in config_dict:
                            textEdit_S12_AC_FR = config_dict[arrayRow1[91]]
                            uithaiQianPinShengZai.textEdit_S12_AC_FR.setText(textEdit_S12_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[92] in config_dict:
                            textEdit_S12_TIME = config_dict[arrayRow1[92]]
                            uithaiQianPinShengZai.textEdit_S12_TIME.setText(textEdit_S12_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[93] in config_dict:
                            comboBox_S12_TIME = config_dict[arrayRow1[93]]
                            uithaiQianPinShengZai.comboBox_S12_TIME.setCurrentIndex(int(comboBox_S12_TIME))
                        else:
                            strFlag = 1

                    # step13
                    if strFlag == "0":
                        if arrayRow1[94] in config_dict:
                            checkBox_S13 = config_dict[arrayRow1[94]]
                            if checkBox_S13 == '1':
                                uithaiQianPinShengZai.checkBox_S13.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S13.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[95] in config_dict:
                            textEdit_S13_AC_VOLT = config_dict[arrayRow1[95]]
                            uithaiQianPinShengZai.textEdit_S13_AC_VOLT.setText(textEdit_S13_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[96] in config_dict:
                            textEdit_S13_AC_FR = config_dict[arrayRow1[96]]
                            uithaiQianPinShengZai.textEdit_S13_AC_FR.setText(textEdit_S13_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[97] in config_dict:
                            textEdit_S13_TIME = config_dict[arrayRow1[97]]
                            uithaiQianPinShengZai.textEdit_S13_TIME.setText(textEdit_S13_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[98] in config_dict:
                            comboBox_S13_TIME = config_dict[arrayRow1[98]]
                            uithaiQianPinShengZai.comboBox_S13_TIME.setCurrentIndex(int(comboBox_S13_TIME))
                        else:
                            strFlag = 1

                    # step14
                    if strFlag == "0":
                        if arrayRow1[99] in config_dict:
                            checkBox_S14 = config_dict[arrayRow1[99]]
                            if checkBox_S14 == '1':
                                uithaiQianPinShengZai.checkBox_S14.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S14.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[100] in config_dict:
                            textEdit_S14_AC_VOLT = config_dict[arrayRow1[100]]
                            uithaiQianPinShengZai.textEdit_S14_AC_VOLT.setText(textEdit_S14_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[101] in config_dict:
                            textEdit_S14_AC_FR = config_dict[arrayRow1[101]]
                            uithaiQianPinShengZai.textEdit_S14_AC_FR.setText(textEdit_S14_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[102] in config_dict:
                            textEdit_S14_TIME = config_dict[arrayRow1[102]]
                            uithaiQianPinShengZai.textEdit_S14_TIME.setText(textEdit_S14_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[103] in config_dict:
                            comboBox_S14_TIME = config_dict[arrayRow1[103]]
                            uithaiQianPinShengZai.comboBox_S14_TIME.setCurrentIndex(int(comboBox_S14_TIME))
                        else:
                            strFlag = 1

                    # step15
                    if strFlag == "0":
                        if arrayRow1[104] in config_dict:
                            checkBox_S15 = config_dict[arrayRow1[104]]
                            if checkBox_S15 == '1':
                                uithaiQianPinShengZai.checkBox_S15.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S15.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[105] in config_dict:
                            textEdit_S15_AC_VOLT = config_dict[arrayRow1[105]]
                            uithaiQianPinShengZai.textEdit_S15_AC_VOLT.setText(textEdit_S15_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[106] in config_dict:
                            textEdit_S15_AC_FR = config_dict[arrayRow1[106]]
                            uithaiQianPinShengZai.textEdit_S15_AC_FR.setText(textEdit_S15_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[107] in config_dict:
                            textEdit_S15_TIME = config_dict[arrayRow1[107]]
                            uithaiQianPinShengZai.textEdit_S15_TIME.setText(textEdit_S15_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[108] in config_dict:
                            comboBox_S15_TIME = config_dict[arrayRow1[108]]
                            uithaiQianPinShengZai.comboBox_S15_TIME.setCurrentIndex(int(comboBox_S15_TIME))
                        else:
                            strFlag = 1

                    # step16
                    if strFlag == "0":
                        if arrayRow1[109] in config_dict:
                            checkBox_S16 = config_dict[arrayRow1[109]]
                            if checkBox_S16 == '1':
                                uithaiQianPinShengZai.checkBox_S16.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S16.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[110] in config_dict:
                            textEdit_S16_AC_VOLT = config_dict[arrayRow1[110]]
                            uithaiQianPinShengZai.textEdit_S16_AC_VOLT.setText(textEdit_S16_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[111] in config_dict:
                            textEdit_S16_AC_FR = config_dict[arrayRow1[111]]
                            uithaiQianPinShengZai.textEdit_S16_AC_FR.setText(textEdit_S16_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[112] in config_dict:
                            textEdit_S16_TIME = config_dict[arrayRow1[112]]
                            uithaiQianPinShengZai.textEdit_S16_TIME.setText(textEdit_S16_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[113] in config_dict:
                            comboBox_S16_TIME = config_dict[arrayRow1[113]]
                            uithaiQianPinShengZai.comboBox_S16_TIME.setCurrentIndex(int(comboBox_S16_TIME))
                        else:
                            strFlag = 1

                    # step17
                    if strFlag == "0":
                        if arrayRow1[114] in config_dict:
                            checkBox_S17 = config_dict[arrayRow1[114]]
                            if checkBox_S17 == '1':
                                uithaiQianPinShengZai.checkBox_S17.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S17.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[115] in config_dict:
                            textEdit_S17_AC_VOLT = config_dict[arrayRow1[115]]
                            uithaiQianPinShengZai.textEdit_S17_AC_VOLT.setText(textEdit_S17_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[116] in config_dict:
                            textEdit_S17_AC_FR = config_dict[arrayRow1[116]]
                            uithaiQianPinShengZai.textEdit_S17_AC_FR.setText(textEdit_S17_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[117] in config_dict:
                            textEdit_S17_TIME = config_dict[arrayRow1[117]]
                            uithaiQianPinShengZai.textEdit_S17_TIME.setText(textEdit_S17_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[118] in config_dict:
                            comboBox_S17_TIME = config_dict[arrayRow1[118]]
                            uithaiQianPinShengZai.comboBox_S17_TIME.setCurrentIndex(int(comboBox_S17_TIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[119] in config_dict:
                            checkBox_S_End = config_dict[arrayRow1[119]]
                            if checkBox_S_End == '1':
                                uithaiQianPinShengZai.checkBox_S_End.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S_End.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[120] in config_dict:
                            comboBox_S_End_AC = config_dict[arrayRow1[120]]
                            uithaiQianPinShengZai.comboBox_S_End_AC.setCurrentIndex(int(comboBox_S_End_AC))

                    if strFlag == "0":
                        if arrayRow1[121] in config_dict:
                            checkBox_S_End_DC1 = config_dict[arrayRow1[121]]
                            if checkBox_S_End_DC1 == '1':
                                uithaiQianPinShengZai.checkBox_S_End_DC1.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S_End_DC1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[122] in config_dict:
                            comboBox_S_End_DC1 = config_dict[arrayRow1[122]]
                            uithaiQianPinShengZai.comboBox_S_End_DC1.setCurrentIndex(int(comboBox_S_End_DC1))

                    if strFlag == "0":
                        if arrayRow1[123] in config_dict:
                            checkBox_S_End_DC2 = config_dict[arrayRow1[123]]
                            if checkBox_S_End_DC2 == '1':
                                uithaiQianPinShengZai.checkBox_S_End_DC2.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S_End_DC2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[124] in config_dict:
                            comboBox_S_End_DC2 = config_dict[arrayRow1[124]]
                            uithaiQianPinShengZai.comboBox_S_End_DC2.setCurrentIndex(int(comboBox_S_End_DC2))

                    if strFlag == "0":
                        if arrayRow1[125] in config_dict:
                            checkBox_S_End_DC3 = config_dict[arrayRow1[125]]
                            if checkBox_S_End_DC3 == '1':
                                uithaiQianPinShengZai.checkBox_S_End_DC3.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S_End_DC3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[126] in config_dict:
                            comboBox_S_End_DC3 = config_dict[arrayRow1[126]]
                            uithaiQianPinShengZai.comboBox_S_End_DC3.setCurrentIndex(int(comboBox_S_End_DC3))

                    if strFlag == "0":
                        if arrayRow1[127] in config_dict:
                            checkBox_S_End_DC4 = config_dict[arrayRow1[127]]
                            if checkBox_S_End_DC4 == '1':
                                uithaiQianPinShengZai.checkBox_S_End_DC4.setChecked(True)
                            else:
                                uithaiQianPinShengZai.checkBox_S_End_DC4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[128] in config_dict:
                            comboBox_S_End_DC4 = config_dict[arrayRow1[128]]
                            uithaiQianPinShengZai.comboBox_S_End_DC4.setCurrentIndex(int(comboBox_S_End_DC4))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[129] in config_dict:
                            checkBox_S2_WT5000 = config_dict[arrayRow1[129]]
                            if checkBox_S2_WT5000 == '1':
                                uithaiQianPinShengZai.radioButton_S2_WT5000.setChecked(True)
                            else:
                                uithaiQianPinShengZai.radioButton_S2_WT5000.setChecked(False)
                        else:
                            strFlag = 1

                    try:
                        from utils.overfreq_ladder_commands import sync_legacy_cards_to_freq_list
                        _has_ladder = False
                        if len(arrayRow1) > 130 and arrayRow1[130] in config_dict:
                            _has_ladder = True
                            _fl = getattr(uithaiQianPinShengZai, "textEdit_FrequencyLadder", None)
                            if _fl is not None:
                                _fl.setPlainText(str(config_dict[arrayRow1[130]] or ""))
                        if len(arrayRow1) > 131 and arrayRow1[131] in config_dict:
                            _flv = getattr(uithaiQianPinShengZai, "textEdit_FrequencyLadder_VOLT", None)
                            if _flv is not None:
                                _flv.setPlainText(str(config_dict[arrayRow1[131]] or "230"))
                        if len(arrayRow1) > 132 and arrayRow1[132] in config_dict:
                            _flt = getattr(uithaiQianPinShengZai, "textEdit_FrequencyLadder_TIME", None)
                            if _flt is not None:
                                _flt.setPlainText(str(config_dict[arrayRow1[132]] or "60"))
                        if len(arrayRow1) > 133 and arrayRow1[133] in config_dict:
                            _flu = getattr(uithaiQianPinShengZai, "comboBox_FrequencyLadder_TIME", None)
                            if _flu is not None:
                                try:
                                    _flu.setCurrentIndex(int(config_dict[arrayRow1[133]]))
                                except Exception:
                                    pass
                        if not _has_ladder:
                            sync_legacy_cards_to_freq_list(uithaiQianPinShengZai)
                    except Exception:
                        pass

                    if arrayRow1[41] in config_dict:
                        checkBox_S2_WT3000 = config_dict[arrayRow1[41]]
                        if checkBox_S2_WT3000 == '1':
                            Open_File_ThaiWT3000_Config(_PageWidgetFinder(uithaiQianPinShengZai._wtStacked.widget(0)), wt_config_dict)

                    else:
                        strFlag = 1

                    if arrayRow1[42] in config_dict:
                        checkBox_S2_WT1800 = config_dict[arrayRow1[42]]
                        if checkBox_S2_WT1800 == '1':
                            Open_File_ThaiWT1800_Config(_PageWidgetFinder(uithaiQianPinShengZai._wtStacked.widget(1)), wt_config_dict)
                    else:
                        strFlag = 1

                    if arrayRow1[43] in config_dict:
                        checkBox_S2_WT1806E = config_dict[arrayRow1[43]]
                        if checkBox_S2_WT1806E == '1':
                            Open_File_ThaiWT1806E_Config(_PageWidgetFinder(uithaiQianPinShengZai._wtStacked.widget(2)), wt_config_dict)
                    else:
                        strFlag = 1

                    if arrayRow1[129] in config_dict:
                        checkBox_S2_WT5000 = config_dict[arrayRow1[129]]
                        if checkBox_S2_WT5000 == '1':
                            Open_File_ThaiWT5000_Config(_PageWidgetFinder(uithaiQianPinShengZai._wtStacked.widget(3)), wt_config_dict)
                    else:
                        strFlag = 1

                    _restore_dewetron_tail(result_list[0], result_list[1], uithaiQianPinShengZai)
                else:
                    print("no")
                    strFlag = "1"

        QMessageBox.information(None, "实验设定提示信息", "欠频升载文件读取完成", QMessageBox.Ok, QMessageBox.Ok)

# def save_file_header():
#     directory1 = [r"D:\\project\\photovoltaic_automation_t\\config_files\\project_step_configs\\qianpinshengzai.csv"]
#     if directory1[0] == '':
#         print('请选择一个文件')
#     else:
#         out = open(directory1[0], 'w+', newline='')
#         csv_write = csv.writer(out, dialect="excel")
#         csv_write.writerow(arrayRow1)
#         out.close()

# if __name__ == "__main__":
#     save_file_header()
