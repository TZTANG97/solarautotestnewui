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

_DEWETRON_SPEC = PROJECT_SPECS["过欠压_过欠频"]


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
    'comboBox_Test_Project', 'checkBox_AC_Test_L1',
        'checkBox_AC_Test_L2', 'checkBox_AC_Test_L3',
    'checkBox_S3', 'textEdit_S3_AC_VOLT_Start', 'textEdit_S3_AC_VOLT_End', 'textEdit_S3_AC_FR_Start',
        'textEdit_S3_AC_FR_End', 'textEdit_S3_Step_Size', 'textEdit_S3_TIME', 'comboBox_S3_TIME',
    'checkBox_S4', 'textEdit_S4_AC_VOLT_Start', 'textEdit_S4_AC_VOLT_End', 'textEdit_S4_AC_FR_Start',
        'textEdit_S4_AC_FR_End', 'textEdit_S4_Step_Size', 'textEdit_S4_TIME', 'comboBox_S4_TIME',
    'checkBox_S5', 'textEdit_S5_AC_VOLT_Start', 'textEdit_S5_AC_VOLT_End', 'textEdit_S5_AC_FR_Start',
        'textEdit_S5_AC_FR_End', 'textEdit_S5_Step_Size', 'textEdit_S5_TIME', 'comboBox_S5_TIME',
    'checkBox_S6', 'textEdit_S6_AC_VOLT_Start', 'textEdit_S6_AC_VOLT_End', 'textEdit_S6_AC_FR_Start',
        'textEdit_S6_AC_FR_End', 'textEdit_S6_Step_Size', 'textEdit_S6_TIME', 'comboBox_S6_TIME',
    'checkBox_S7', 'textEdit_S7_AC_VOLT_Start', 'textEdit_S7_AC_VOLT_End', 'textEdit_S7_AC_FR_Start',
        'textEdit_S7_AC_FR_End', 'textEdit_S7_Step_Size', 'textEdit_S7_TIME', 'comboBox_S7_TIME',
    'checkBox_S8', 'textEdit_S8_AC_VOLT_Start', 'textEdit_S8_AC_VOLT_End', 'textEdit_S8_AC_FR_Start',
        'textEdit_S8_AC_FR_End', 'textEdit_S8_Step_Size', 'textEdit_S8_TIME', 'comboBox_S8_TIME',
    'checkBox_S_End', "comboBox_S_End_AC", "checkBox_S_End_DC1", "comboBox_S_End_DC1","checkBox_S_End_DC2",
        "comboBox_S_End_DC2","checkBox_S_End_DC3", "comboBox_S_End_DC3","checkBox_S_End_DC4","comboBox_S_End_DC4",
        "checkBox_S2_WT5000"]

# 泰国过频降载保存设定
def Save_File_ThaiGuoQianYa_Pin(kwargs):
    dialog_windowguoqianya_pin = kwargs['dialog_windowguoqianya_pin']
    uithaiGuoQianYa_Pin = kwargs['uiThaiGuoQianYa_Pin']
    uiThiaWT3000E = kwargs['uiThiaWT3000E']
    uiThiaWT1800 = kwargs['uiThiaWT1800']
    uiThiaWT1806E = kwargs['uiThiaWT1806E']
    uiThiaWT5000 = kwargs['uiThiaWT5000']
    result = []
    directory1 = QFileDialog.getSaveFileName(None,"单个文件保存","./","Text Files(*.csv)")
    if directory1[0] == '':
        print('请选择一个文件')
    else:
        arrayRow2 = ['ThaiGuoQianYa_Pin']

        if uithaiGuoQianYa_Pin.checkBox_S1.isChecked():
            checkBox_S1 = '1'
        else:
            checkBox_S1 = '0'
        arrayRow2.append(checkBox_S1)

        comboBox_S1_AC = uithaiGuoQianYa_Pin.comboBox_S1_AC.currentIndex()
        arrayRow2.append(comboBox_S1_AC)

        textEdit_S1_AC_VOLT = uithaiGuoQianYa_Pin.textEdit_S1_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT)

        textEdit_S1_AC_VOLT_2 = uithaiGuoQianYa_Pin.textEdit_S1_AC_VOLT_2.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_2)

        textEdit_S1_AC_VOLT_3 = uithaiGuoQianYa_Pin.textEdit_S1_AC_VOLT_3.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_3)

        textEdit_S1_AC_FR = uithaiGuoQianYa_Pin.textEdit_S1_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S1_AC_FR)

        comboBox_S1_AC_2 = uithaiGuoQianYa_Pin.comboBox_S1_AC_2.currentIndex()
        arrayRow2.append(comboBox_S1_AC_2)

        if uithaiGuoQianYa_Pin.checkBox_S1_DC1.isChecked():
            checkBox_S1_DC1 = '1'
        else:
            checkBox_S1_DC1 = '0'
        arrayRow2.append(checkBox_S1_DC1)

        comboBox_S1_DC1 = uithaiGuoQianYa_Pin.comboBox_S1_DC1.currentIndex()
        arrayRow2.append(comboBox_S1_DC1)

        textEdit_S1_DC1_VOLT = uithaiGuoQianYa_Pin.textEdit_S1_DC1_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_VOLT)

        textEdit_S1_DC1_CURR = uithaiGuoQianYa_Pin.textEdit_S1_DC1_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_CURR)

        textEdit_S1_DC1_Voc = uithaiGuoQianYa_Pin.textEdit_S1_DC1_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Voc)
        
        textEdit_S1_DC1_Isc = uithaiGuoQianYa_Pin.textEdit_S1_DC1_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Isc)
        
        textEdit_S1_DC1_PF = uithaiGuoQianYa_Pin.textEdit_S1_DC1_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF)

        if uithaiGuoQianYa_Pin.checkBox_S1_DC2.isChecked():
            checkBox_S1_DC2 = '1'
        else:
            checkBox_S1_DC2 = '0'
        arrayRow2.append(checkBox_S1_DC2)

        comboBox_S1_DC2 = uithaiGuoQianYa_Pin.comboBox_S1_DC2.currentIndex()
        arrayRow2.append(comboBox_S1_DC2)

        textEdit_S1_DC2_VOLT = uithaiGuoQianYa_Pin.textEdit_S1_DC2_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_VOLT)

        textEdit_S1_DC2_CURR = uithaiGuoQianYa_Pin.textEdit_S1_DC2_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_CURR)

        textEdit_S1_DC2_Voc = uithaiGuoQianYa_Pin.textEdit_S1_DC2_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Voc)
        
        textEdit_S1_DC2_Isc = uithaiGuoQianYa_Pin.textEdit_S1_DC2_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Isc)
        
        textEdit_S1_DC2_PF = uithaiGuoQianYa_Pin.textEdit_S1_DC2_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_PF)

        if uithaiGuoQianYa_Pin.checkBox_S1_DC3.isChecked():
            checkBox_S1_DC3 = '1'
        else:
            checkBox_S1_DC3 = '0'
        arrayRow2.append(checkBox_S1_DC3)

        comboBox_S1_DC3 = uithaiGuoQianYa_Pin.comboBox_S1_DC3.currentIndex()
        arrayRow2.append(comboBox_S1_DC3)

        textEdit_S1_DC3_VOLT = uithaiGuoQianYa_Pin.textEdit_S1_DC3_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_VOLT)

        textEdit_S1_DC3_CURR = uithaiGuoQianYa_Pin.textEdit_S1_DC3_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_CURR)

        textEdit_S1_DC3_Voc = uithaiGuoQianYa_Pin.textEdit_S1_DC3_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Voc)
        
        textEdit_S1_DC3_Isc = uithaiGuoQianYa_Pin.textEdit_S1_DC3_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Isc)
        
        textEdit_S1_DC3_PF = uithaiGuoQianYa_Pin.textEdit_S1_DC3_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_PF)

        if uithaiGuoQianYa_Pin.checkBox_S1_DC4.isChecked():
            checkBox_S1_DC4 = '1'
        else:
            checkBox_S1_DC4 = '0'
        arrayRow2.append(checkBox_S1_DC4)

        comboBox_S1_DC4 = uithaiGuoQianYa_Pin.comboBox_S1_DC4.currentIndex()
        arrayRow2.append(comboBox_S1_DC4)

        textEdit_S1_DC4_VOLT = uithaiGuoQianYa_Pin.textEdit_S1_DC4_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_VOLT)

        textEdit_S1_DC4_CURR = uithaiGuoQianYa_Pin.textEdit_S1_DC4_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_CURR)

        textEdit_S1_DC4_Voc = uithaiGuoQianYa_Pin.textEdit_S1_DC4_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Voc)
        
        textEdit_S1_DC4_Isc = uithaiGuoQianYa_Pin.textEdit_S1_DC4_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Isc)
        
        textEdit_S1_DC4_PF = uithaiGuoQianYa_Pin.textEdit_S1_DC4_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_PF)

        textEdit_S1_ACWaitTIME = uithaiGuoQianYa_Pin.textEdit_S1_ACWaitTIME.toPlainText()
        arrayRow2.append(textEdit_S1_ACWaitTIME)

        comboBox_S1_ACWaitTIME = uithaiGuoQianYa_Pin.comboBox_S1_ACWaitTIME.currentIndex()
        arrayRow2.append(comboBox_S1_ACWaitTIME)

        textEdit_S1_TIME = uithaiGuoQianYa_Pin.textEdit_S1_TIME.toPlainText()
        arrayRow2.append(textEdit_S1_TIME)

        comboBox_S1_TIME = uithaiGuoQianYa_Pin.comboBox_S1_TIME.currentIndex()
        arrayRow2.append(comboBox_S1_TIME)
        
        # step2
        if uithaiGuoQianYa_Pin.checkBox_S2.isChecked():
            checkBox_S2 = '1'
        else:
            checkBox_S2 = '0'
        arrayRow2.append(checkBox_S2)

        if uithaiGuoQianYa_Pin.radioButton_S2_WT3000.isChecked():
            checkBox_S2_WT3000 = '1'
        else:
            checkBox_S2_WT3000 = '0'
        arrayRow2.append(checkBox_S2_WT3000)

        if uithaiGuoQianYa_Pin.radioButton_S2_WT1800.isChecked():
            checkBox_S2_WT1800 = '1'
        else:
            checkBox_S2_WT1800 = '0'
        arrayRow2.append(checkBox_S2_WT1800)

        if uithaiGuoQianYa_Pin.radioButton_S2_WT1806E.isChecked():
            checkBox_S2_WT1806E = '1'
        else:
            checkBox_S2_WT1806E = '0'
        arrayRow2.append(checkBox_S2_WT1806E)

        # extend_step
        comboBox_Test_Project = uithaiGuoQianYa_Pin.comboBox_Test_Project.currentIndex()
        arrayRow2.append(comboBox_Test_Project)

        if uithaiGuoQianYa_Pin.checkBox_AC_Test_L1.isChecked():
            checkBox_AC_Test_L1 = '1'
        else:
            checkBox_AC_Test_L1 = '0'
        arrayRow2.append(checkBox_AC_Test_L1)

        if uithaiGuoQianYa_Pin.checkBox_AC_Test_L2.isChecked():
            checkBox_AC_Test_L2 = '1'
        else:
            checkBox_AC_Test_L2 = '0'
        arrayRow2.append(checkBox_AC_Test_L2)

        if uithaiGuoQianYa_Pin.checkBox_AC_Test_L3.isChecked():
            checkBox_AC_Test_L3 = '1'
        else:
            checkBox_AC_Test_L3 = '0'
        arrayRow2.append(checkBox_AC_Test_L3)

        # step3
        if uithaiGuoQianYa_Pin.checkBox_S3.isChecked():
            checkBox_S3 = '1'
        else:
            checkBox_S3 = '0'
        arrayRow2.append(checkBox_S3)

        textEdit_S3_AC_VOLT_Start = uithaiGuoQianYa_Pin.textEdit_S3_AC_VOLT_Start.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT_Start)

        textEdit_S3_AC_VOLT_End = uithaiGuoQianYa_Pin.textEdit_S3_AC_VOLT_End.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT_End)

        textEdit_S3_AC_FR_Start = uithaiGuoQianYa_Pin.textEdit_S3_AC_FR_Start.toPlainText()
        arrayRow2.append(textEdit_S3_AC_FR_Start)

        textEdit_S3_AC_FR_End = uithaiGuoQianYa_Pin.textEdit_S3_AC_FR_End.toPlainText()
        arrayRow2.append(textEdit_S3_AC_FR_End)
        
        textEdit_S3_Step_Size = uithaiGuoQianYa_Pin.textEdit_S3_Step_Size.toPlainText()
        arrayRow2.append(textEdit_S3_Step_Size)

        textEdit_S3_TIME = uithaiGuoQianYa_Pin.textEdit_S3_TIME.toPlainText()
        arrayRow2.append(textEdit_S3_TIME)

        comboBox_S3_TIME = uithaiGuoQianYa_Pin.comboBox_S3_TIME.currentIndex()
        arrayRow2.append(comboBox_S3_TIME)

        # step4
        if uithaiGuoQianYa_Pin.checkBox_S4.isChecked():
            checkBox_S4 = '1'
        else:
            checkBox_S4 = '0'
        arrayRow2.append(checkBox_S4)

        textEdit_S4_AC_VOLT_Start = uithaiGuoQianYa_Pin.textEdit_S4_AC_VOLT_Start.toPlainText()
        arrayRow2.append(textEdit_S4_AC_VOLT_Start)

        textEdit_S4_AC_VOLT_End = uithaiGuoQianYa_Pin.textEdit_S4_AC_VOLT_End.toPlainText()
        arrayRow2.append(textEdit_S4_AC_VOLT_End)

        textEdit_S4_AC_FR_Start = uithaiGuoQianYa_Pin.textEdit_S4_AC_FR_Start.toPlainText()
        arrayRow2.append(textEdit_S4_AC_FR_Start)

        textEdit_S4_AC_FR_End = uithaiGuoQianYa_Pin.textEdit_S4_AC_FR_End.toPlainText()
        arrayRow2.append(textEdit_S4_AC_FR_End)

        textEdit_S4_Step_Size = uithaiGuoQianYa_Pin.textEdit_S4_Step_Size.toPlainText()
        arrayRow2.append(textEdit_S4_Step_Size)

        textEdit_S4_TIME = uithaiGuoQianYa_Pin.textEdit_S4_TIME.toPlainText()
        arrayRow2.append(textEdit_S4_TIME)

        comboBox_S4_TIME = uithaiGuoQianYa_Pin.comboBox_S4_TIME.currentIndex()
        arrayRow2.append(comboBox_S4_TIME)

        # step5
        if uithaiGuoQianYa_Pin.checkBox_S5.isChecked():
            checkBox_S5 = '1'
        else:
            checkBox_S5 = '0'
        arrayRow2.append(checkBox_S5)

        textEdit_S5_AC_VOLT_Start = uithaiGuoQianYa_Pin.textEdit_S5_AC_VOLT_Start.toPlainText()
        arrayRow2.append(textEdit_S5_AC_VOLT_Start)

        textEdit_S5_AC_VOLT_End = uithaiGuoQianYa_Pin.textEdit_S5_AC_VOLT_End.toPlainText()
        arrayRow2.append(textEdit_S5_AC_VOLT_End)

        textEdit_S5_AC_FR_Start = uithaiGuoQianYa_Pin.textEdit_S5_AC_FR_Start.toPlainText()
        arrayRow2.append(textEdit_S5_AC_FR_Start)

        textEdit_S5_AC_FR_End = uithaiGuoQianYa_Pin.textEdit_S5_AC_FR_End.toPlainText()
        arrayRow2.append(textEdit_S5_AC_FR_End)

        textEdit_S5_Step_Size = uithaiGuoQianYa_Pin.textEdit_S5_Step_Size.toPlainText()
        arrayRow2.append(textEdit_S5_Step_Size)

        textEdit_S5_TIME = uithaiGuoQianYa_Pin.textEdit_S5_TIME.toPlainText()
        arrayRow2.append(textEdit_S5_TIME)

        comboBox_S5_TIME = uithaiGuoQianYa_Pin.comboBox_S5_TIME.currentIndex()
        arrayRow2.append(comboBox_S5_TIME)

        # step6
        if uithaiGuoQianYa_Pin.checkBox_S6.isChecked():
            checkBox_S6 = '1'
        else:
            checkBox_S6 = '0'
        arrayRow2.append(checkBox_S6)

        textEdit_S6_AC_VOLT_Start = uithaiGuoQianYa_Pin.textEdit_S6_AC_VOLT_Start.toPlainText()
        arrayRow2.append(textEdit_S6_AC_VOLT_Start)

        textEdit_S6_AC_VOLT_End = uithaiGuoQianYa_Pin.textEdit_S6_AC_VOLT_End.toPlainText()
        arrayRow2.append(textEdit_S6_AC_VOLT_End)

        textEdit_S6_AC_FR_Start = uithaiGuoQianYa_Pin.textEdit_S6_AC_FR_Start.toPlainText()
        arrayRow2.append(textEdit_S6_AC_FR_Start)

        textEdit_S6_AC_FR_End = uithaiGuoQianYa_Pin.textEdit_S6_AC_FR_End.toPlainText()
        arrayRow2.append(textEdit_S6_AC_FR_End)

        textEdit_S6_Step_Size = uithaiGuoQianYa_Pin.textEdit_S6_Step_Size.toPlainText()
        arrayRow2.append(textEdit_S6_Step_Size)

        textEdit_S6_TIME = uithaiGuoQianYa_Pin.textEdit_S6_TIME.toPlainText()
        arrayRow2.append(textEdit_S6_TIME)

        comboBox_S6_TIME = uithaiGuoQianYa_Pin.comboBox_S6_TIME.currentIndex()
        arrayRow2.append(comboBox_S6_TIME)

        # step7
        if uithaiGuoQianYa_Pin.checkBox_S7.isChecked():
            checkBox_S7 = '1'
        else:
            checkBox_S7 = '0'
        arrayRow2.append(checkBox_S7)

        textEdit_S7_AC_VOLT_Start = uithaiGuoQianYa_Pin.textEdit_S7_AC_VOLT_Start.toPlainText()
        arrayRow2.append(textEdit_S7_AC_VOLT_Start)

        textEdit_S7_AC_VOLT_End = uithaiGuoQianYa_Pin.textEdit_S7_AC_VOLT_End.toPlainText()
        arrayRow2.append(textEdit_S7_AC_VOLT_End)

        textEdit_S7_AC_FR_Start = uithaiGuoQianYa_Pin.textEdit_S7_AC_FR_Start.toPlainText()
        arrayRow2.append(textEdit_S7_AC_FR_Start)

        textEdit_S7_AC_FR_End = uithaiGuoQianYa_Pin.textEdit_S7_AC_FR_End.toPlainText()
        arrayRow2.append(textEdit_S7_AC_FR_End)

        textEdit_S7_Step_Size = uithaiGuoQianYa_Pin.textEdit_S7_Step_Size.toPlainText()
        arrayRow2.append(textEdit_S7_Step_Size)

        textEdit_S7_TIME = uithaiGuoQianYa_Pin.textEdit_S7_TIME.toPlainText()
        arrayRow2.append(textEdit_S7_TIME)

        comboBox_S7_TIME = uithaiGuoQianYa_Pin.comboBox_S7_TIME.currentIndex()
        arrayRow2.append(comboBox_S7_TIME)

        # step8
        if uithaiGuoQianYa_Pin.checkBox_S8.isChecked():
            checkBox_S8 = '1'
        else:
            checkBox_S8 = '0'
        arrayRow2.append(checkBox_S8)

        textEdit_S8_AC_VOLT_Start = uithaiGuoQianYa_Pin.textEdit_S8_AC_VOLT_Start.toPlainText()
        arrayRow2.append(textEdit_S8_AC_VOLT_Start)

        textEdit_S8_AC_VOLT_End = uithaiGuoQianYa_Pin.textEdit_S8_AC_VOLT_End.toPlainText()
        arrayRow2.append(textEdit_S8_AC_VOLT_End)

        textEdit_S8_AC_FR_Start = uithaiGuoQianYa_Pin.textEdit_S8_AC_FR_Start.toPlainText()
        arrayRow2.append(textEdit_S8_AC_FR_Start)

        textEdit_S8_AC_FR_End = uithaiGuoQianYa_Pin.textEdit_S8_AC_FR_End.toPlainText()
        arrayRow2.append(textEdit_S8_AC_FR_End)

        textEdit_S8_Step_Size = uithaiGuoQianYa_Pin.textEdit_S8_Step_Size.toPlainText()
        arrayRow2.append(textEdit_S8_Step_Size)

        textEdit_S8_TIME = uithaiGuoQianYa_Pin.textEdit_S8_TIME.toPlainText()
        arrayRow2.append(textEdit_S8_TIME)

        comboBox_S8_TIME = uithaiGuoQianYa_Pin.comboBox_S8_TIME.currentIndex()
        arrayRow2.append(comboBox_S8_TIME)

        # step_end
        if uithaiGuoQianYa_Pin.checkBox_S_End.isChecked():
            checkBox_S_End = '1'
        else:
            checkBox_S_End = '0'
        arrayRow2.append(checkBox_S_End)

        comboBox_S_End_AC = uithaiGuoQianYa_Pin.comboBox_S_End_AC.currentIndex()
        arrayRow2.append(comboBox_S_End_AC)

        if uithaiGuoQianYa_Pin.checkBox_S_End_DC1.isChecked():
            checkBox_S_End_DC1 = '1'
        else:
            checkBox_S_End_DC1 = '0'
        arrayRow2.append(checkBox_S_End_DC1)

        comboBox_S_End_DC1 = uithaiGuoQianYa_Pin.comboBox_S_End_DC1.currentIndex()
        arrayRow2.append(comboBox_S_End_DC1)

        if uithaiGuoQianYa_Pin.checkBox_S_End_DC2.isChecked():
            checkBox_S_End_DC2 = '1'
        else:
            checkBox_S_End_DC2 = '0'
        arrayRow2.append(checkBox_S_End_DC2)

        comboBox_S_End_DC2 = uithaiGuoQianYa_Pin.comboBox_S_End_DC2.currentIndex()
        arrayRow2.append(comboBox_S_End_DC2)

        if uithaiGuoQianYa_Pin.checkBox_S_End_DC3.isChecked():
            checkBox_S_End_DC3 = '1'
        else:
            checkBox_S_End_DC3 = '0'
        arrayRow2.append(checkBox_S_End_DC3)

        comboBox_S_End_DC3 = uithaiGuoQianYa_Pin.comboBox_S_End_DC3.currentIndex()
        arrayRow2.append(comboBox_S_End_DC3)

        if uithaiGuoQianYa_Pin.checkBox_S_End_DC4.isChecked():
            checkBox_S_End_DC4 = '1'
        else:
            checkBox_S_End_DC4 = '0'
        arrayRow2.append(checkBox_S_End_DC4)

        comboBox_S_End_DC4 = uithaiGuoQianYa_Pin.comboBox_S_End_DC4.currentIndex()
        arrayRow2.append(comboBox_S_End_DC4)

        if uithaiGuoQianYa_Pin.radioButton_S2_WT5000.isChecked():
            checkBox_S2_WT5000 = '1'
        else:
            checkBox_S2_WT5000 = '0'
        arrayRow2.append(checkBox_S2_WT5000)

        _append_dewetron_tail(arrayRow2, uithaiGuoQianYa_Pin)

        if uithaiGuoQianYa_Pin.radioButton_S2_WT3000.isChecked():
            result = Save_File_ThaiWT3000_Config(_PageWidgetFinder(uithaiGuoQianYa_Pin._wtStacked.widget(0)))

        if uithaiGuoQianYa_Pin.radioButton_S2_WT1800.isChecked():
            result = Save_File_ThaiWT1800_Config(_PageWidgetFinder(uithaiGuoQianYa_Pin._wtStacked.widget(1)))

        if uithaiGuoQianYa_Pin.radioButton_S2_WT1806E.isChecked():
            result = Save_File_ThaiWT1806E_Config(_PageWidgetFinder(uithaiGuoQianYa_Pin._wtStacked.widget(2)))

        if uithaiGuoQianYa_Pin.radioButton_S2_WT5000.isChecked():
            result = Save_File_ThaiWT5000_Config(_PageWidgetFinder(uithaiGuoQianYa_Pin._wtStacked.widget(3)))

        out = open(directory1[0], 'w+', newline='', encoding='utf-8-sig')
        csv_write = csv.writer(out, dialect="excel")
        csv_write.writerow(arrayRow1)
        csv_write.writerow(arrayRow2)
        if len(result) > 0:
            csv_write.writerow(result[0])
            csv_write.writerow(result[1])
        out.close()
        QMessageBox.information(None, "实验设定提示信息", "过欠压_过欠频文件保存完成", QMessageBox.Ok, QMessageBox.Ok)

# 泰国过频降载取设定
def Open_File_ThaiGuoQianYa_Pin(kwargs):
    dialog_windowguoqianya_pin = kwargs['dialog_windowguoqianya_pin']
    uithaiGuoQianYa_Pin = kwargs['uiThaiGuoQianYa_Pin']
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
                if config_dict[arrayRow1[0]] == "ThaiGuoQianYa_Pin":
                    #checkBox
                    if strFlag == "0":
                        if arrayRow1[1] in config_dict:
                            checkBox_S1 = config_dict[arrayRow1[1]]
                            if checkBox_S1 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S1.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S1.setChecked(False)
                        else:
                            strFlag = 1

                    #comBox
                    if strFlag == "0":
                        if arrayRow1[2] in config_dict:
                            comboBox_S1_AC = config_dict[arrayRow1[2]]
                            uithaiGuoQianYa_Pin.comboBox_S1_AC.setCurrentIndex(int(comboBox_S1_AC))
                        else:
                            strFlag = 1

                    #textEdit
                    if strFlag == "0":
                        if arrayRow1[3] in config_dict:
                            textEdit_S1_AC_VOLT = config_dict[arrayRow1[3]]
                            uithaiGuoQianYa_Pin.textEdit_S1_AC_VOLT.setText(textEdit_S1_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[4] in config_dict:
                            textEdit_S1_AC_VOLT_2 = config_dict[arrayRow1[4]]
                            uithaiGuoQianYa_Pin.textEdit_S1_AC_VOLT_2.setText(textEdit_S1_AC_VOLT_2)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[5] in config_dict:
                            textEdit_S1_AC_VOLT_3 = config_dict[arrayRow1[5]]
                            uithaiGuoQianYa_Pin.textEdit_S1_AC_VOLT_3.setText(textEdit_S1_AC_VOLT_3)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[6] in config_dict:
                            textEdit_S1_AC_FR = config_dict[arrayRow1[6]]
                            uithaiGuoQianYa_Pin.textEdit_S1_AC_FR.setText(textEdit_S1_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[7] in config_dict:
                            comboBox_S1_AC_2 = config_dict[arrayRow1[7]]
                            uithaiGuoQianYa_Pin.comboBox_S1_AC_2.setCurrentIndex(int(comboBox_S1_AC_2))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[8] in config_dict:
                            checkBox_S1_DC1 = config_dict[arrayRow1[8]]
                            if checkBox_S1_DC1 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S1_DC1.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S1_DC1.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[9] in config_dict:
                            comboBox_S1_DC1 = config_dict[arrayRow1[9]]
                            uithaiGuoQianYa_Pin.comboBox_S1_DC1.setCurrentIndex(int(comboBox_S1_DC1))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[10] in config_dict:
                            textEdit_S1_DC1_VOLT = config_dict[arrayRow1[10]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC1_VOLT.setText(textEdit_S1_DC1_VOLT)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[11] in config_dict:
                            textEdit_S1_DC1_CURR = config_dict[arrayRow1[11]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC1_CURR.setText(textEdit_S1_DC1_CURR)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[12] in config_dict:
                            textEdit_S1_DC1_Voc = config_dict[arrayRow1[12]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC1_Voc.setText(textEdit_S1_DC1_Voc)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[13] in config_dict:
                            textEdit_S1_DC1_Isc = config_dict[arrayRow1[13]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC1_Isc.setText(textEdit_S1_DC1_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[14] in config_dict:
                            textEdit_S1_DC1_PF = config_dict[arrayRow1[14]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC1_PF.setText(textEdit_S1_DC1_PF)
                        else:
                            strFlag = 1
                            
                    if strFlag == "0":
                        if arrayRow1[15] in config_dict:
                            checkBox_S1_DC2 = config_dict[arrayRow1[15]]
                            if checkBox_S1_DC2 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S1_DC2.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S1_DC2.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[16] in config_dict:
                            comboBox_S1_DC2 = config_dict[arrayRow1[16]]
                            uithaiGuoQianYa_Pin.comboBox_S1_DC2.setCurrentIndex(int(comboBox_S1_DC2))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[17] in config_dict:
                            textEdit_S1_DC2_VOLT = config_dict[arrayRow1[17]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC2_VOLT.setText(textEdit_S1_DC2_VOLT)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[18] in config_dict:
                            textEdit_S1_DC2_CURR = config_dict[arrayRow1[18]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC2_CURR.setText(textEdit_S1_DC2_CURR)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[19] in config_dict:
                            textEdit_S1_DC2_Voc = config_dict[arrayRow1[19]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC2_Voc.setText(textEdit_S1_DC2_Voc)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[20] in config_dict:
                            textEdit_S1_DC2_Isc = config_dict[arrayRow1[20]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC2_Isc.setText(textEdit_S1_DC2_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[21] in config_dict:
                            textEdit_S1_DC2_PF = config_dict[arrayRow1[21]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC2_PF.setText(textEdit_S1_DC2_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[22] in config_dict:
                            checkBox_S1_DC3 = config_dict[arrayRow1[22]]
                            if checkBox_S1_DC3 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S1_DC3.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S1_DC3.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[23] in config_dict:
                            comboBox_S1_DC3 = config_dict[arrayRow1[23]]
                            uithaiGuoQianYa_Pin.comboBox_S1_DC3.setCurrentIndex(int(comboBox_S1_DC3))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[24] in config_dict:
                            textEdit_S1_DC3_VOLT = config_dict[arrayRow1[24]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC3_VOLT.setText(textEdit_S1_DC3_VOLT)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[25] in config_dict:
                            textEdit_S1_DC3_CURR = config_dict[arrayRow1[25]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC3_CURR.setText(textEdit_S1_DC3_CURR)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[26] in config_dict:
                            textEdit_S1_DC3_Voc = config_dict[arrayRow1[26]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC3_Voc.setText(textEdit_S1_DC3_Voc)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[27] in config_dict:
                            textEdit_S1_DC3_Isc = config_dict[arrayRow1[27]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC3_Isc.setText(textEdit_S1_DC3_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[28] in config_dict:
                            textEdit_S1_DC3_PF = config_dict[arrayRow1[28]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC3_PF.setText(textEdit_S1_DC3_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[29] in config_dict:
                            checkBox_S1_DC4 = config_dict[arrayRow1[29]]
                            if checkBox_S1_DC4 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S1_DC4.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S1_DC4.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[30] in config_dict:
                            comboBox_S1_DC4 = config_dict[arrayRow1[30]]
                            uithaiGuoQianYa_Pin.comboBox_S1_DC4.setCurrentIndex(int(comboBox_S1_DC4))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[31] in config_dict:
                            textEdit_S1_DC4_VOLT = config_dict[arrayRow1[31]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC4_VOLT.setText(textEdit_S1_DC4_VOLT)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[32] in config_dict:
                            textEdit_S1_DC4_CURR = config_dict[arrayRow1[32]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC4_CURR.setText(textEdit_S1_DC4_CURR)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[33] in config_dict:
                            textEdit_S1_DC4_Voc = config_dict[arrayRow1[33]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC4_Voc.setText(textEdit_S1_DC4_Voc)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[34] in config_dict:
                            textEdit_S1_DC4_Isc = config_dict[arrayRow1[34]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC4_Isc.setText(textEdit_S1_DC4_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[35] in config_dict:
                            textEdit_S1_DC4_PF = config_dict[arrayRow1[35]]
                            uithaiGuoQianYa_Pin.textEdit_S1_DC4_PF.setText(textEdit_S1_DC4_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[36] in config_dict:
                            textEdit_S1_ACWaitTIME = config_dict[arrayRow1[36]]
                            uithaiGuoQianYa_Pin.textEdit_S1_ACWaitTIME.setText(textEdit_S1_ACWaitTIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[37] in config_dict:
                            comboBox_S1_ACWaitTIME = config_dict[arrayRow1[37]]
                            uithaiGuoQianYa_Pin.comboBox_S1_ACWaitTIME.setCurrentIndex(int(comboBox_S1_ACWaitTIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[38] in config_dict:
                            textEdit_S1_TIME = config_dict[arrayRow1[38]]
                            uithaiGuoQianYa_Pin.textEdit_S1_TIME.setText(textEdit_S1_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[39] in config_dict:
                            comboBox_S1_TIME = config_dict[arrayRow1[39]]
                            uithaiGuoQianYa_Pin.comboBox_S1_TIME.setCurrentIndex(int(comboBox_S1_TIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[40] in config_dict:
                            checkBox_S2 = config_dict[arrayRow1[40]]
                            if checkBox_S2 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S2.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[41] in config_dict:
                            checkBox_S2_WT3000 = config_dict[arrayRow1[41]]
                            if checkBox_S2_WT3000 == '1':
                                uithaiGuoQianYa_Pin.radioButton_S2_WT3000.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.radioButton_S2_WT3000.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[42] in config_dict:
                            checkBox_S2_WT1800 = config_dict[arrayRow1[42]]
                            if checkBox_S2_WT1800 == '1':
                                uithaiGuoQianYa_Pin.radioButton_S2_WT1800.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.radioButton_S2_WT1800.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[43] in config_dict:
                            checkBox_S2_WT1806E = config_dict[arrayRow1[43]]
                            if checkBox_S2_WT1806E == '1':
                                uithaiGuoQianYa_Pin.radioButton_S2_WT1806E.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.radioButton_S2_WT1806E.setChecked(False)
                        else:
                            strFlag = 1

                    #comBox
                    if strFlag == "0":
                        if arrayRow1[44] in config_dict:
                            comboBox_Test_Project = config_dict[arrayRow1[44]]
                            uithaiGuoQianYa_Pin.comboBox_Test_Project.setCurrentIndex(int(comboBox_Test_Project))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[45] in config_dict:
                            checkBox_AC_Test_L1 = config_dict[arrayRow1[45]]
                            if checkBox_AC_Test_L1 == '1':
                                uithaiGuoQianYa_Pin.checkBox_AC_Test_L1.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_AC_Test_L1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[46] in config_dict:
                            checkBox_AC_Test_L2 = config_dict[arrayRow1[46]]
                            if checkBox_AC_Test_L2 == '1':
                                uithaiGuoQianYa_Pin.checkBox_AC_Test_L2.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_AC_Test_L2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[47] in config_dict:
                            checkBox_AC_Test_L3 = config_dict[arrayRow1[47]]
                            if checkBox_AC_Test_L3 == '1':
                                uithaiGuoQianYa_Pin.checkBox_AC_Test_L3.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_AC_Test_L3.setChecked(False)
                        else:
                            strFlag = 1

                    # step3
                    if strFlag == "0":
                        if arrayRow1[48] in config_dict:
                            checkBox_S3 = config_dict[arrayRow1[48]]
                            if checkBox_S3 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S3.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[49] in config_dict:
                            textEdit_S3_AC_VOLT_Start = config_dict[arrayRow1[49]]
                            uithaiGuoQianYa_Pin.textEdit_S3_AC_VOLT_Start.setText(textEdit_S3_AC_VOLT_Start)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[50] in config_dict:
                            textEdit_S3_AC_VOLT_End = config_dict[arrayRow1[50]]
                            uithaiGuoQianYa_Pin.textEdit_S3_AC_VOLT_End.setText(textEdit_S3_AC_VOLT_End)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[51] in config_dict:
                            textEdit_S3_AC_FR_Start = config_dict[arrayRow1[51]]
                            uithaiGuoQianYa_Pin.textEdit_S3_AC_FR_Start.setText(textEdit_S3_AC_FR_Start)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[52] in config_dict:
                            textEdit_S3_AC_FR_End = config_dict[arrayRow1[52]]
                            uithaiGuoQianYa_Pin.textEdit_S3_AC_FR_End.setText(textEdit_S3_AC_FR_End)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[53] in config_dict:
                            textEdit_S3_Step_Size = config_dict[arrayRow1[53]]
                            uithaiGuoQianYa_Pin.textEdit_S3_Step_Size.setText(textEdit_S3_Step_Size)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[54] in config_dict:
                            textEdit_S3_TIME = config_dict[arrayRow1[54]]
                            uithaiGuoQianYa_Pin.textEdit_S3_TIME.setText(textEdit_S3_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[55] in config_dict:
                            comboBox_S3_TIME = config_dict[arrayRow1[55]]
                            uithaiGuoQianYa_Pin.comboBox_S3_TIME.setCurrentIndex(int(comboBox_S3_TIME))
                        else:
                            strFlag = 1

                    # step4
                    if strFlag == "0":
                        if arrayRow1[56] in config_dict:
                            checkBox_S4 = config_dict[arrayRow1[56]]
                            if checkBox_S4 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S4.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[57] in config_dict:
                            textEdit_S4_AC_VOLT_Start = config_dict[arrayRow1[57]]
                            uithaiGuoQianYa_Pin.textEdit_S4_AC_VOLT_Start.setText(textEdit_S4_AC_VOLT_Start)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[58] in config_dict:
                            textEdit_S4_AC_VOLT_End = config_dict[arrayRow1[58]]
                            uithaiGuoQianYa_Pin.textEdit_S4_AC_VOLT_End.setText(textEdit_S4_AC_VOLT_End)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[59] in config_dict:
                            textEdit_S4_AC_FR_Start = config_dict[arrayRow1[59]]
                            uithaiGuoQianYa_Pin.textEdit_S4_AC_FR_Start.setText(textEdit_S4_AC_FR_Start)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[60] in config_dict:
                            textEdit_S4_AC_FR_End = config_dict[arrayRow1[60]]
                            uithaiGuoQianYa_Pin.textEdit_S4_AC_FR_End.setText(textEdit_S4_AC_FR_End)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[61] in config_dict:
                            textEdit_S4_Step_Size = config_dict[arrayRow1[61]]
                            uithaiGuoQianYa_Pin.textEdit_S4_Step_Size.setText(textEdit_S4_Step_Size)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[62] in config_dict:
                            textEdit_S4_TIME = config_dict[arrayRow1[62]]
                            uithaiGuoQianYa_Pin.textEdit_S4_TIME.setText(textEdit_S4_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[63] in config_dict:
                            comboBox_S4_TIME = config_dict[arrayRow1[63]]
                            uithaiGuoQianYa_Pin.comboBox_S4_TIME.setCurrentIndex(int(comboBox_S4_TIME))
                        else:
                            strFlag = 1

                    # step5
                    if strFlag == "0":
                        if arrayRow1[64] in config_dict:
                            checkBox_S5 = config_dict[arrayRow1[64]]
                            if checkBox_S5 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S5.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S5.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[65] in config_dict:
                            textEdit_S5_AC_VOLT_Start = config_dict[arrayRow1[65]]
                            uithaiGuoQianYa_Pin.textEdit_S5_AC_VOLT_Start.setText(textEdit_S5_AC_VOLT_Start)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[66] in config_dict:
                            textEdit_S5_AC_VOLT_End = config_dict[arrayRow1[66]]
                            uithaiGuoQianYa_Pin.textEdit_S5_AC_VOLT_End.setText(textEdit_S5_AC_VOLT_End)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[67] in config_dict:
                            textEdit_S5_AC_FR_Start = config_dict[arrayRow1[67]]
                            uithaiGuoQianYa_Pin.textEdit_S5_AC_FR_Start.setText(textEdit_S5_AC_FR_Start)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[68] in config_dict:
                            textEdit_S5_AC_FR_End = config_dict[arrayRow1[68]]
                            uithaiGuoQianYa_Pin.textEdit_S5_AC_FR_End.setText(textEdit_S5_AC_FR_End)
                        else:
                            strFlag = 1
                    if strFlag == "0":
                        if arrayRow1[69] in config_dict:
                            textEdit_S5_Step_Size = config_dict[arrayRow1[69]]
                            uithaiGuoQianYa_Pin.textEdit_S5_Step_Size.setText(textEdit_S5_Step_Size)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[70] in config_dict:
                            textEdit_S5_TIME = config_dict[arrayRow1[70]]
                            uithaiGuoQianYa_Pin.textEdit_S5_TIME.setText(textEdit_S5_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[71] in config_dict:
                            comboBox_S5_TIME = config_dict[arrayRow1[71]]
                            uithaiGuoQianYa_Pin.comboBox_S5_TIME.setCurrentIndex(int(comboBox_S5_TIME))
                        else:
                            strFlag = 1

                    # step6
                    if strFlag == "0":
                        if arrayRow1[72] in config_dict:
                            checkBox_S6 = config_dict[arrayRow1[72]]
                            if checkBox_S6 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S6.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S6.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[73] in config_dict:
                            textEdit_S6_AC_VOLT_Start = config_dict[arrayRow1[73]]
                            uithaiGuoQianYa_Pin.textEdit_S6_AC_VOLT_Start.setText(textEdit_S6_AC_VOLT_Start)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[74] in config_dict:
                            textEdit_S6_AC_VOLT_End = config_dict[arrayRow1[74]]
                            uithaiGuoQianYa_Pin.textEdit_S6_AC_VOLT_End.setText(textEdit_S6_AC_VOLT_End)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[75] in config_dict:
                            textEdit_S6_AC_FR_Start = config_dict[arrayRow1[75]]
                            uithaiGuoQianYa_Pin.textEdit_S6_AC_FR_Start.setText(textEdit_S6_AC_FR_Start)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[76] in config_dict:
                            textEdit_S6_AC_FR_End = config_dict[arrayRow1[76]]
                            uithaiGuoQianYa_Pin.textEdit_S6_AC_FR_End.setText(textEdit_S6_AC_FR_End)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[77] in config_dict:
                            textEdit_S6_Step_Size = config_dict[arrayRow1[77]]
                            uithaiGuoQianYa_Pin.textEdit_S6_Step_Size.setText(textEdit_S6_Step_Size)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[78] in config_dict:
                            textEdit_S6_TIME = config_dict[arrayRow1[78]]
                            uithaiGuoQianYa_Pin.textEdit_S6_TIME.setText(textEdit_S6_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[79] in config_dict:
                            comboBox_S6_TIME = config_dict[arrayRow1[79]]
                            uithaiGuoQianYa_Pin.comboBox_S6_TIME.setCurrentIndex(int(comboBox_S6_TIME))
                        else:
                            strFlag = 1

                    # step7
                    if strFlag == "0":
                        if arrayRow1[80] in config_dict:
                            checkBox_S7 = config_dict[arrayRow1[80]]
                            if checkBox_S7 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S7.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S7.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[81] in config_dict:
                            textEdit_S7_AC_VOLT_Start = config_dict[arrayRow1[81]]
                            uithaiGuoQianYa_Pin.textEdit_S7_AC_VOLT_Start.setText(textEdit_S7_AC_VOLT_Start)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[82] in config_dict:
                            textEdit_S7_AC_VOLT_End = config_dict[arrayRow1[82]]
                            uithaiGuoQianYa_Pin.textEdit_S7_AC_VOLT_End.setText(textEdit_S7_AC_VOLT_End)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[83] in config_dict:
                            textEdit_S7_AC_FR_Start = config_dict[arrayRow1[83]]
                            uithaiGuoQianYa_Pin.textEdit_S7_AC_FR_Start.setText(textEdit_S7_AC_FR_Start)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[84] in config_dict:
                            textEdit_S7_AC_FR_End = config_dict[arrayRow1[84]]
                            uithaiGuoQianYa_Pin.textEdit_S7_AC_FR_End.setText(textEdit_S7_AC_FR_End)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[85] in config_dict:
                            textEdit_S7_Step_Size = config_dict[arrayRow1[85]]
                            uithaiGuoQianYa_Pin.textEdit_S7_Step_Size.setText(textEdit_S7_Step_Size)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[86] in config_dict:
                            textEdit_S7_TIME = config_dict[arrayRow1[86]]
                            uithaiGuoQianYa_Pin.textEdit_S7_TIME.setText(textEdit_S7_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[87] in config_dict:
                            comboBox_S7_TIME = config_dict[arrayRow1[87]]
                            uithaiGuoQianYa_Pin.comboBox_S7_TIME.setCurrentIndex(int(comboBox_S7_TIME))
                        else:
                            strFlag = 1

                    # step8
                    if strFlag == "0":
                        if arrayRow1[88] in config_dict:
                            checkBox_S8 = config_dict[arrayRow1[88]]
                            if checkBox_S8 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S8.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S8.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[89] in config_dict:
                            textEdit_S8_AC_VOLT_Start = config_dict[arrayRow1[89]]
                            uithaiGuoQianYa_Pin.textEdit_S8_AC_VOLT_Start.setText(textEdit_S8_AC_VOLT_Start)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[90] in config_dict:
                            textEdit_S8_AC_VOLT_End = config_dict[arrayRow1[90]]
                            uithaiGuoQianYa_Pin.textEdit_S8_AC_VOLT_End.setText(textEdit_S8_AC_VOLT_End)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[91] in config_dict:
                            textEdit_S8_AC_FR_Start = config_dict[arrayRow1[91]]
                            uithaiGuoQianYa_Pin.textEdit_S8_AC_FR_Start.setText(textEdit_S8_AC_FR_Start)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[92] in config_dict:
                            textEdit_S8_AC_FR_End = config_dict[arrayRow1[92]]
                            uithaiGuoQianYa_Pin.textEdit_S8_AC_FR_End.setText(textEdit_S8_AC_FR_End)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[93] in config_dict:
                            textEdit_S8_Step_Size = config_dict[arrayRow1[93]]
                            uithaiGuoQianYa_Pin.textEdit_S8_Step_Size.setText(textEdit_S8_Step_Size)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[94] in config_dict:
                            textEdit_S8_TIME = config_dict[arrayRow1[94]]
                            uithaiGuoQianYa_Pin.textEdit_S8_TIME.setText(textEdit_S8_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[95] in config_dict:
                            comboBox_S8_TIME = config_dict[arrayRow1[95]]
                            uithaiGuoQianYa_Pin.comboBox_S8_TIME.setCurrentIndex(int(comboBox_S8_TIME))
                        else:
                            strFlag = 1

                    # step_end
                    if strFlag == "0":
                        if arrayRow1[96] in config_dict:
                            checkBox_S_End = config_dict[arrayRow1[96]]
                            if checkBox_S_End == '1':
                                uithaiGuoQianYa_Pin.checkBox_S_End.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S_End.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[97] in config_dict:
                            comboBox_S_End_AC = config_dict[arrayRow1[97]]
                            uithaiGuoQianYa_Pin.comboBox_S_End_AC.setCurrentIndex(int(comboBox_S_End_AC))

                    if strFlag == "0":
                        if arrayRow1[98] in config_dict:
                            checkBox_S_End_DC1 = config_dict[arrayRow1[98]]
                            if checkBox_S_End_DC1 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S_End_DC1.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S_End_DC1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[99] in config_dict:
                            comboBox_S_End_DC1 = config_dict[arrayRow1[99]]
                            uithaiGuoQianYa_Pin.comboBox_S_End_DC1.setCurrentIndex(int(comboBox_S_End_DC1))

                    if strFlag == "0":
                        if arrayRow1[100] in config_dict:
                            checkBox_S_End_DC2 = config_dict[arrayRow1[100]]
                            if checkBox_S_End_DC2 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S_End_DC2.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S_End_DC2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[101] in config_dict:
                            comboBox_S_End_DC2 = config_dict[arrayRow1[101]]
                            uithaiGuoQianYa_Pin.comboBox_S_End_DC2.setCurrentIndex(int(comboBox_S_End_DC2))

                    if strFlag == "0":
                        if arrayRow1[102] in config_dict:
                            checkBox_S_End_DC3 = config_dict[arrayRow1[102]]
                            if checkBox_S_End_DC3 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S_End_DC3.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S_End_DC3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[103] in config_dict:
                            comboBox_S_End_DC3 = config_dict[arrayRow1[103]]
                            uithaiGuoQianYa_Pin.comboBox_S_End_DC3.setCurrentIndex(int(comboBox_S_End_DC3))

                    if strFlag == "0":
                        if arrayRow1[104] in config_dict:
                            checkBox_S_End_DC4 = config_dict[arrayRow1[104]]
                            if checkBox_S_End_DC4 == '1':
                                uithaiGuoQianYa_Pin.checkBox_S_End_DC4.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.checkBox_S_End_DC4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[105] in config_dict:
                            comboBox_S_End_DC4 = config_dict[arrayRow1[105]]
                            uithaiGuoQianYa_Pin.comboBox_S_End_DC4.setCurrentIndex(int(comboBox_S_End_DC4))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[106] in config_dict:
                            checkBox_S2_WT5000 = config_dict[arrayRow1[106]]
                            if checkBox_S2_WT5000 == '1':
                                uithaiGuoQianYa_Pin.radioButton_S2_WT5000.setChecked(True)
                            else:
                                uithaiGuoQianYa_Pin.radioButton_S2_WT5000.setChecked(False)
                        else:
                            strFlag = 1

                    if arrayRow1[41] in config_dict:
                        checkBox_S2_WT3000 = config_dict[arrayRow1[41]]
                        if checkBox_S2_WT3000 == '1':
                            Open_File_ThaiWT3000_Config(_PageWidgetFinder(uithaiGuoQianYa_Pin._wtStacked.widget(0)), wt_config_dict)

                    else:
                        strFlag = 1

                    if arrayRow1[42] in config_dict:
                        checkBox_S2_WT1800 = config_dict[arrayRow1[42]]
                        if checkBox_S2_WT1800 == '1':
                            Open_File_ThaiWT1800_Config(_PageWidgetFinder(uithaiGuoQianYa_Pin._wtStacked.widget(1)), wt_config_dict)
                    else:
                        strFlag = 1

                    if arrayRow1[43] in config_dict:
                        checkBox_S2_WT1806E = config_dict[arrayRow1[43]]
                        if checkBox_S2_WT1806E == '1':
                            Open_File_ThaiWT1806E_Config(_PageWidgetFinder(uithaiGuoQianYa_Pin._wtStacked.widget(2)), wt_config_dict)
                    else:
                        strFlag = 1

                    if arrayRow1[106] in config_dict:
                        checkBox_S2_WT5000 = config_dict[arrayRow1[106]]
                        if checkBox_S2_WT5000 == '1':
                            Open_File_ThaiWT5000_Config(_PageWidgetFinder(uithaiGuoQianYa_Pin._wtStacked.widget(3)), wt_config_dict)
                    else:
                        strFlag = 1

                    _restore_dewetron_tail(result_list[0], result_list[1], uithaiGuoQianYa_Pin)
                else:
                    print("no")
                    strFlag = "1"

        QMessageBox.information(None, "实验设定提示信息", "过欠压_过欠频文件读取完成", QMessageBox.Ok, QMessageBox.Ok)

# def save_file_header():
#     directory1 = [r"D:\\project\\photovoltaic_automation_t\\config_files\\project_step_configs\\guoqianya_pin.csv"]
#     if directory1[0] == '':
#         print('请选择一个文件')
#     else:
#         out = open(directory1[0], 'w+', newline='')
#         csv_write = csv.writer(out, dialect="excel")
#         csv_write.writerow(arrayRow1)
#         out.close()

# if __name__ == "__main__":
#     save_file_header()
