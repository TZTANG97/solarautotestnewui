import re
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, \
    QFileDialog, QMessageBox
import csv

from dewetron_autotest import (
    PROJECT_SPECS,
    append_dewetron_tail_columns,
    extract_ui_config,
    extract_ui_mode,
    read_dewetron_tail_columns,
)


_DEWETRON_SPEC = PROJECT_SPECS["静态MPPT测试"]
ANALYZER_ENABLED_COLUMN = "checkBox_Analyzer"


arrayRow1 = ['Style',
    'checkBox_S1',
        'comboBox_S1_AC',"textEdit_S1_AC_VOLT", "textEdit_S1_AC_VOLT_2", "textEdit_S1_AC_VOLT_3",
            "textEdit_S1_AC_FR","comboBox_S1_AC_2",
        "comboBox_S1_Vdc_Count",
        "checkBox_S1_DC1", "comboBox_S1_DC1_PORT", 
            "checkBox_S1_DC1_Vmin", "textEdit_S1_DC1_Vmin", "checkBox_S1_DC1_Vnom", "textEdit_S1_DC1_Vnom",
            "checkBox_S1_DC1_Vmax", "textEdit_S1_DC1_Vmax", "checkBox_S1_DC1_Vdc1", "textEdit_S1_DC1_Vdc1",
             "checkBox_S1_DC1_Vdc2", "textEdit_S1_DC1_Vdc2", "checkBox_S1_DC1_Vdc3", "textEdit_S1_DC1_Vdc3",
        "checkBox_S1_DC2", "comboBox_S1_DC2_PORT", 
            "checkBox_S1_DC2_Vmin", "textEdit_S1_DC2_Vmin", "checkBox_S1_DC2_Vnom", "textEdit_S1_DC2_Vnom",
            "checkBox_S1_DC2_Vmax", "textEdit_S1_DC2_Vmax", "checkBox_S1_DC2_Vdc1", "textEdit_S1_DC2_Vdc1",
             "checkBox_S1_DC2_Vdc2", "textEdit_S1_DC2_Vdc2", "checkBox_S1_DC2_Vdc3", "textEdit_S1_DC2_Vdc3",
        "checkBox_S1_DC3", "comboBox_S1_DC3_PORT", 
            "checkBox_S1_DC3_Vmin", "textEdit_S1_DC3_Vmin", "checkBox_S1_DC3_Vnom", "textEdit_S1_DC3_Vnom",
            "checkBox_S1_DC3_Vmax", "textEdit_S1_DC3_Vmax", "checkBox_S1_DC3_Vdc1", "textEdit_S1_DC3_Vdc1",
             "checkBox_S1_DC3_Vdc2", "textEdit_S1_DC3_Vdc2", "checkBox_S1_DC3_Vdc3", "textEdit_S1_DC3_Vdc3",
        "checkBox_S1_DC4", "comboBox_S1_DC4_PORT", 
            "checkBox_S1_DC4_Vmin", "textEdit_S1_DC4_Vmin", "checkBox_S1_DC4_Vnom", "textEdit_S1_DC4_Vnom",
            "checkBox_S1_DC4_Vmax", "textEdit_S1_DC4_Vmax", "checkBox_S1_DC4_Vdc1", "textEdit_S1_DC4_Vdc1",
             "checkBox_S1_DC4_Vdc2", "textEdit_S1_DC4_Vdc2", "checkBox_S1_DC4_Vdc3", "textEdit_S1_DC4_Vdc3",
        "textEdit_S1_ACWaitTIME", "comboBox_S1_ACWaitTIME", "textEdit_S1_TIME", "comboBox_S1_TIME",
    'checkBox_S2',
        "textEdit_S2_Vmin_PATH", "textEdit_S2_Vnom_PATH", "textEdit_S2_Vmax_PATH",
        "textEdit_S2_Vdc1_PATH", "textEdit_S2_Vdc2_PATH", "textEdit_S2_Vdc3_PATH",
        "checkBox_S2_Pn_100", "checkBox_S2_Pn_75", "checkBox_S2_Pn_50", "checkBox_S2_Pn_30",
        "checkBox_S2_Pn_25", "checkBox_S2_Pn_20", "checkBox_S2_Pn_10", "checkBox_S2_Pn_5",
    'checkBox_S3', 
        'textEdit_S3_TOTAL_H', 'textEdit_S3_TOTAL_M',
        'textEdit_S3_PER_H', 'textEdit_S3_PER_M',
    
    'checkBox_S_End', "comboBox_S_End_AC", "checkBox_S_End_DC", "comboBox_S_End_DC",
    ANALYZER_ENABLED_COLUMN]


def _append_dewetron_tail(values, ui):
    """追加独立分析仪启用状态和共享 DEWETRON 命名配置列。"""
    analyzer_index = arrayRow1.index(ANALYZER_ENABLED_COLUMN)
    while len(values) <= analyzer_index:
        values.append("")
    analyzer_checkbox = getattr(ui, "checkBox_Analyzer", None)
    values[analyzer_index] = (
        "1"
        if analyzer_checkbox is None or analyzer_checkbox.isChecked()
        else "0"
    )

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
    """按列名恢复新字段；旧 CSV 缺少尾列时使用 WT 默认值。"""
    try:
        mode, config = read_dewetron_tail_columns(headers, values)
    except (IndexError, TypeError, ValueError):
        mode, config = read_dewetron_tail_columns([], [])

    row = {
        str(header): values[index] if index < len(values) else ""
        for index, header in enumerate(headers)
    }
    analyzer_checkbox = getattr(ui, "checkBox_Analyzer", None)
    if analyzer_checkbox is not None:
        enabled = row.get(ANALYZER_ENABLED_COLUMN)
        analyzer_checkbox.setChecked(
            True if enabled in (None, "") else str(enabled).strip().lower() in {
                "1", "true", "yes", "on"
            }
        )

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

# 静态MPPT测试存设定
def Save_File_ThaiStaticMPPTTest(dialog_windowstaticmppttest, uithaiStaticMPPTTest):
    directory1 = QFileDialog.getSaveFileName(None,"单个文件保存","./","Text Files(*.csv)")
    if directory1[0] == '':
        print('请选择一个文件')
    else:
        arrayRow2 = ['ThaiStaticMPPTTest']

        if uithaiStaticMPPTTest.checkBox_S1.isChecked():
            checkBox_S1 = '1'
        else:
            checkBox_S1 = '0'
        arrayRow2.append(checkBox_S1)

        comboBox_S1_AC = uithaiStaticMPPTTest.comboBox_S1_AC.currentIndex()
        arrayRow2.append(comboBox_S1_AC)

        textEdit_S1_AC_VOLT = uithaiStaticMPPTTest.textEdit_S1_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT)

        textEdit_S1_AC_VOLT_2 = uithaiStaticMPPTTest.textEdit_S1_AC_VOLT_2.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_2)

        textEdit_S1_AC_VOLT_3 = uithaiStaticMPPTTest.textEdit_S1_AC_VOLT_3.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_3)

        textEdit_S1_AC_FR = uithaiStaticMPPTTest.textEdit_S1_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S1_AC_FR)

        comboBox_S1_AC_2 = uithaiStaticMPPTTest.comboBox_S1_AC_2.currentIndex()
        arrayRow2.append(comboBox_S1_AC_2)

        comboBox_S1_Vdc_Count = uithaiStaticMPPTTest.comboBox_S1_Vdc_Count.currentIndex()
        arrayRow2.append(comboBox_S1_Vdc_Count)

        # DC1
        if uithaiStaticMPPTTest.checkBox_S1_DC1.isChecked():
            checkBox_S1_DC1 = '1'
        else:
            checkBox_S1_DC1 = '0'
        arrayRow2.append(checkBox_S1_DC1)

        comboBox_S1_DC1_PORT = uithaiStaticMPPTTest.comboBox_S1_DC1_PORT.currentIndex()
        arrayRow2.append(comboBox_S1_DC1_PORT)

        if uithaiStaticMPPTTest.checkBox_S1_DC1_Vmin.isChecked():
            checkBox_S1_DC1_Vmin = '1'
        else:
            checkBox_S1_DC1_Vmin = '0'
        arrayRow2.append(checkBox_S1_DC1_Vmin)

        textEdit_S1_DC1_Vmin = uithaiStaticMPPTTest.textEdit_S1_DC1_Vmin.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Vmin)

        if uithaiStaticMPPTTest.checkBox_S1_DC1_Vnom.isChecked():
            checkBox_S1_DC1_Vnom = '1'
        else:
            checkBox_S1_DC1_Vnom = '0'
        arrayRow2.append(checkBox_S1_DC1_Vnom)

        textEdit_S1_DC1_Vnom = uithaiStaticMPPTTest.textEdit_S1_DC1_Vnom.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Vnom)

        if uithaiStaticMPPTTest.checkBox_S1_DC1_Vmax.isChecked():
            checkBox_S1_DC1_Vmax = '1'
        else:
            checkBox_S1_DC1_Vmax = '0'
        arrayRow2.append(checkBox_S1_DC1_Vmax)

        textEdit_S1_DC1_Vmax = uithaiStaticMPPTTest.textEdit_S1_DC1_Vmax.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Vmax)

        if uithaiStaticMPPTTest.checkBox_S1_DC1_Vdc1.isChecked():
            checkBox_S1_DC1_Vdc1 = '1'
        else:
            checkBox_S1_DC1_Vdc1 = '0'
        arrayRow2.append(checkBox_S1_DC1_Vdc1)

        textEdit_S1_DC1_Vdc1 = uithaiStaticMPPTTest.textEdit_S1_DC1_Vdc1.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Vdc1)

        if uithaiStaticMPPTTest.checkBox_S1_DC1_Vdc2.isChecked():
            checkBox_S1_DC1_Vdc2 = '1'
        else:
            checkBox_S1_DC1_Vdc2 = '0'
        arrayRow2.append(checkBox_S1_DC1_Vdc2)

        textEdit_S1_DC1_Vdc2 = uithaiStaticMPPTTest.textEdit_S1_DC1_Vdc2.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Vdc2)

        if uithaiStaticMPPTTest.checkBox_S1_DC1_Vdc3.isChecked():
            checkBox_S1_DC1_Vdc3 = '1'
        else:
            checkBox_S1_DC1_Vdc3 = '0'
        arrayRow2.append(checkBox_S1_DC1_Vdc3)

        textEdit_S1_DC1_Vdc3 = uithaiStaticMPPTTest.textEdit_S1_DC1_Vdc3.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Vdc3)

        # DC2
        if uithaiStaticMPPTTest.checkBox_S1_DC2.isChecked():
            checkBox_S1_DC2 = '1'
        else:
            checkBox_S1_DC2 = '0'
        arrayRow2.append(checkBox_S1_DC2)

        comboBox_S1_DC2_PORT = uithaiStaticMPPTTest.comboBox_S1_DC2_PORT.currentIndex()
        arrayRow2.append(comboBox_S1_DC2_PORT)

        if uithaiStaticMPPTTest.checkBox_S1_DC2_Vmin.isChecked():
            checkBox_S1_DC2_Vmin = '1'
        else:
            checkBox_S1_DC2_Vmin = '0'
        arrayRow2.append(checkBox_S1_DC2_Vmin)

        textEdit_S1_DC2_Vmin = uithaiStaticMPPTTest.textEdit_S1_DC2_Vmin.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Vmin)

        if uithaiStaticMPPTTest.checkBox_S1_DC2_Vnom.isChecked():
            checkBox_S1_DC2_Vnom = '1'
        else:
            checkBox_S1_DC2_Vnom = '0'
        arrayRow2.append(checkBox_S1_DC2_Vnom)

        textEdit_S1_DC2_Vnom = uithaiStaticMPPTTest.textEdit_S1_DC2_Vnom.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Vnom)

        if uithaiStaticMPPTTest.checkBox_S1_DC2_Vmax.isChecked():
            checkBox_S1_DC2_Vmax = '1'
        else:
            checkBox_S1_DC2_Vmax = '0'
        arrayRow2.append(checkBox_S1_DC2_Vmax)

        textEdit_S1_DC2_Vmax = uithaiStaticMPPTTest.textEdit_S1_DC2_Vmax.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Vmax)

        if uithaiStaticMPPTTest.checkBox_S1_DC2_Vdc1.isChecked():
            checkBox_S1_DC2_Vdc1 = '1'
        else:
            checkBox_S1_DC2_Vdc1 = '0'
        arrayRow2.append(checkBox_S1_DC2_Vdc1)

        textEdit_S1_DC2_Vdc1 = uithaiStaticMPPTTest.textEdit_S1_DC2_Vdc1.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Vdc1)

        if uithaiStaticMPPTTest.checkBox_S1_DC2_Vdc2.isChecked():
            checkBox_S1_DC2_Vdc2 = '1'
        else:
            checkBox_S1_DC2_Vdc2 = '0'
        arrayRow2.append(checkBox_S1_DC2_Vdc2)

        textEdit_S1_DC2_Vdc2 = uithaiStaticMPPTTest.textEdit_S1_DC2_Vdc2.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Vdc2)

        if uithaiStaticMPPTTest.checkBox_S1_DC2_Vdc3.isChecked():
            checkBox_S1_DC2_Vdc3 = '1'
        else:
            checkBox_S1_DC2_Vdc3 = '0'
        arrayRow2.append(checkBox_S1_DC2_Vdc3)

        textEdit_S1_DC2_Vdc3 = uithaiStaticMPPTTest.textEdit_S1_DC2_Vdc3.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Vdc3)

        # DC3
        if uithaiStaticMPPTTest.checkBox_S1_DC3.isChecked():
            checkBox_S1_DC3 = '1'
        else:
            checkBox_S1_DC3 = '0'
        arrayRow2.append(checkBox_S1_DC3)

        comboBox_S1_DC3_PORT = uithaiStaticMPPTTest.comboBox_S1_DC3_PORT.currentIndex()
        arrayRow2.append(comboBox_S1_DC3_PORT)

        if uithaiStaticMPPTTest.checkBox_S1_DC3_Vmin.isChecked():
            checkBox_S1_DC3_Vmin = '1'
        else:
            checkBox_S1_DC3_Vmin = '0'
        arrayRow2.append(checkBox_S1_DC3_Vmin)

        textEdit_S1_DC3_Vmin = uithaiStaticMPPTTest.textEdit_S1_DC3_Vmin.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Vmin)

        if uithaiStaticMPPTTest.checkBox_S1_DC3_Vnom.isChecked():
            checkBox_S1_DC3_Vnom = '1'
        else:
            checkBox_S1_DC3_Vnom = '0'
        arrayRow2.append(checkBox_S1_DC3_Vnom)

        textEdit_S1_DC3_Vnom = uithaiStaticMPPTTest.textEdit_S1_DC3_Vnom.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Vnom)

        if uithaiStaticMPPTTest.checkBox_S1_DC3_Vmax.isChecked():
            checkBox_S1_DC3_Vmax = '1'
        else:
            checkBox_S1_DC3_Vmax = '0'
        arrayRow2.append(checkBox_S1_DC3_Vmax)

        textEdit_S1_DC3_Vmax = uithaiStaticMPPTTest.textEdit_S1_DC3_Vmax.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Vmax)

        if uithaiStaticMPPTTest.checkBox_S1_DC3_Vdc1.isChecked():
            checkBox_S1_DC3_Vdc1 = '1'
        else:
            checkBox_S1_DC3_Vdc1 = '0'
        arrayRow2.append(checkBox_S1_DC3_Vdc1)

        textEdit_S1_DC3_Vdc1 = uithaiStaticMPPTTest.textEdit_S1_DC3_Vdc1.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Vdc1)

        if uithaiStaticMPPTTest.checkBox_S1_DC3_Vdc2.isChecked():
            checkBox_S1_DC3_Vdc2 = '1'
        else:
            checkBox_S1_DC3_Vdc2 = '0'
        arrayRow2.append(checkBox_S1_DC3_Vdc2)

        textEdit_S1_DC3_Vdc2 = uithaiStaticMPPTTest.textEdit_S1_DC3_Vdc2.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Vdc2)

        if uithaiStaticMPPTTest.checkBox_S1_DC3_Vdc3.isChecked():
            checkBox_S1_DC3_Vdc3 = '1'
        else:
            checkBox_S1_DC3_Vdc3 = '0'
        arrayRow2.append(checkBox_S1_DC3_Vdc3)

        textEdit_S1_DC3_Vdc3 = uithaiStaticMPPTTest.textEdit_S1_DC3_Vdc3.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Vdc3)

        # DC4
        if uithaiStaticMPPTTest.checkBox_S1_DC4.isChecked():
            checkBox_S1_DC4 = '1'
        else:
            checkBox_S1_DC4 = '0'
        arrayRow2.append(checkBox_S1_DC4)

        comboBox_S1_DC4_PORT = uithaiStaticMPPTTest.comboBox_S1_DC4_PORT.currentIndex()
        arrayRow2.append(comboBox_S1_DC4_PORT)

        if uithaiStaticMPPTTest.checkBox_S1_DC4_Vmin.isChecked():
            checkBox_S1_DC4_Vmin = '1'
        else:
            checkBox_S1_DC4_Vmin = '0'
        arrayRow2.append(checkBox_S1_DC4_Vmin)

        textEdit_S1_DC4_Vmin = uithaiStaticMPPTTest.textEdit_S1_DC4_Vmin.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Vmin)

        if uithaiStaticMPPTTest.checkBox_S1_DC4_Vnom.isChecked():
            checkBox_S1_DC4_Vnom = '1'
        else:
            checkBox_S1_DC4_Vnom = '0'
        arrayRow2.append(checkBox_S1_DC4_Vnom)

        textEdit_S1_DC4_Vnom = uithaiStaticMPPTTest.textEdit_S1_DC4_Vnom.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Vnom)

        if uithaiStaticMPPTTest.checkBox_S1_DC4_Vmax.isChecked():
            checkBox_S1_DC4_Vmax = '1'
        else:
            checkBox_S1_DC4_Vmax = '0'
        arrayRow2.append(checkBox_S1_DC4_Vmax)

        textEdit_S1_DC4_Vmax = uithaiStaticMPPTTest.textEdit_S1_DC4_Vmax.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Vmax)

        if uithaiStaticMPPTTest.checkBox_S1_DC4_Vdc1.isChecked():
            checkBox_S1_DC4_Vdc1 = '1'
        else:
            checkBox_S1_DC4_Vdc1 = '0'
        arrayRow2.append(checkBox_S1_DC4_Vdc1)

        textEdit_S1_DC4_Vdc1 = uithaiStaticMPPTTest.textEdit_S1_DC4_Vdc1.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Vdc1)

        if uithaiStaticMPPTTest.checkBox_S1_DC4_Vdc2.isChecked():
            checkBox_S1_DC4_Vdc2 = '1'
        else:
            checkBox_S1_DC4_Vdc2 = '0'
        arrayRow2.append(checkBox_S1_DC4_Vdc2)

        textEdit_S1_DC4_Vdc2 = uithaiStaticMPPTTest.textEdit_S1_DC4_Vdc2.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Vdc2)

        if uithaiStaticMPPTTest.checkBox_S1_DC4_Vdc3.isChecked():
            checkBox_S1_DC4_Vdc3 = '1'
        else:
            checkBox_S1_DC4_Vdc3 = '0'
        arrayRow2.append(checkBox_S1_DC4_Vdc3)

        textEdit_S1_DC4_Vdc3 = uithaiStaticMPPTTest.textEdit_S1_DC4_Vdc3.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Vdc3)

        textEdit_S1_ACWaitTIME = uithaiStaticMPPTTest.textEdit_S1_ACWaitTIME.toPlainText()
        arrayRow2.append(textEdit_S1_ACWaitTIME)

        comboBox_S1_ACWaitTIME = uithaiStaticMPPTTest.comboBox_S1_ACWaitTIME.currentIndex()
        arrayRow2.append(comboBox_S1_ACWaitTIME)

        textEdit_S1_TIME = uithaiStaticMPPTTest.textEdit_S1_TIME.toPlainText()
        arrayRow2.append(textEdit_S1_TIME)

        comboBox_S1_TIME = uithaiStaticMPPTTest.comboBox_S1_TIME.currentIndex()
        arrayRow2.append(comboBox_S1_TIME)
        
        # step2
        if uithaiStaticMPPTTest.checkBox_S2.isChecked():
            checkBox_S2 = '1'
        else:
            checkBox_S2 = '0'
        arrayRow2.append(checkBox_S2)

        textEdit_S2_Vmin_PATH = uithaiStaticMPPTTest.textEdit_S2_Vmin_PATH.toPlainText()
        arrayRow2.append(textEdit_S2_Vmin_PATH)

        textEdit_S2_Vnom_PATH = uithaiStaticMPPTTest.textEdit_S2_Vnom_PATH.toPlainText()
        arrayRow2.append(textEdit_S2_Vnom_PATH)

        textEdit_S2_Vmax_PATH = uithaiStaticMPPTTest.textEdit_S2_Vmax_PATH.toPlainText()
        arrayRow2.append(textEdit_S2_Vmax_PATH)

        textEdit_S2_Vdc1_PATH = uithaiStaticMPPTTest.textEdit_S2_Vdc1_PATH.toPlainText()
        arrayRow2.append(textEdit_S2_Vdc1_PATH)

        textEdit_S2_Vdc2_PATH = uithaiStaticMPPTTest.textEdit_S2_Vdc2_PATH.toPlainText()
        arrayRow2.append(textEdit_S2_Vdc2_PATH)

        textEdit_S2_Vdc3_PATH = uithaiStaticMPPTTest.textEdit_S2_Vdc3_PATH.toPlainText()
        arrayRow2.append(textEdit_S2_Vdc3_PATH)

        if uithaiStaticMPPTTest.checkBox_S2_Pn_100.isChecked():
            checkBox_S2_Pn_100 = '1'
        else:
            checkBox_S2_Pn_100 = '0'
        arrayRow2.append(checkBox_S2_Pn_100)

        if uithaiStaticMPPTTest.checkBox_S2_Pn_75.isChecked():
            checkBox_S2_Pn_75 = '1'
        else:
            checkBox_S2_Pn_75 = '0'
        arrayRow2.append(checkBox_S2_Pn_75)

        if uithaiStaticMPPTTest.checkBox_S2_Pn_50.isChecked():
            checkBox_S2_Pn_50 = '1'
        else:
            checkBox_S2_Pn_50 = '0'
        arrayRow2.append(checkBox_S2_Pn_50)

        if uithaiStaticMPPTTest.checkBox_S2_Pn_30.isChecked():
            checkBox_S2_Pn_30 = '1'
        else:
            checkBox_S2_Pn_30 = '0'
        arrayRow2.append(checkBox_S2_Pn_30)

        if uithaiStaticMPPTTest.checkBox_S2_Pn_25.isChecked():
            checkBox_S2_Pn_25 = '1'
        else:
            checkBox_S2_Pn_25 = '0'
        arrayRow2.append(checkBox_S2_Pn_25)

        if uithaiStaticMPPTTest.checkBox_S2_Pn_20.isChecked():
            checkBox_S2_Pn_20 = '1'
        else:
            checkBox_S2_Pn_20 = '0'
        arrayRow2.append(checkBox_S2_Pn_20)

        if uithaiStaticMPPTTest.checkBox_S2_Pn_10.isChecked():
            checkBox_S2_Pn_10 = '1'
        else:
            checkBox_S2_Pn_10 = '0'
        arrayRow2.append(checkBox_S2_Pn_10)

        if uithaiStaticMPPTTest.checkBox_S2_Pn_5.isChecked():
            checkBox_S2_Pn_5 = '1'
        else:
            checkBox_S2_Pn_5 = '0'
        arrayRow2.append(checkBox_S2_Pn_5)

        # step3
        if uithaiStaticMPPTTest.checkBox_S3.isChecked():
            checkBox_S3 = '1'
        else:
            checkBox_S3 = '0'
        arrayRow2.append(checkBox_S3)

        textEdit_S3_TOTAL_H = uithaiStaticMPPTTest.textEdit_S3_TOTAL_H.toPlainText()
        arrayRow2.append(textEdit_S3_TOTAL_H)

        textEdit_S3_TOTAL_M = uithaiStaticMPPTTest.textEdit_S3_TOTAL_M.toPlainText()
        arrayRow2.append(textEdit_S3_TOTAL_M)

        textEdit_S3_PER_H = uithaiStaticMPPTTest.textEdit_S3_PER_H.toPlainText()
        arrayRow2.append(textEdit_S3_PER_H)

        textEdit_S3_PER_M = uithaiStaticMPPTTest.textEdit_S3_PER_M.toPlainText()
        arrayRow2.append(textEdit_S3_PER_M)

        # step_end
        if uithaiStaticMPPTTest.checkBox_S_End.isChecked():
            checkBox_S_End = '1'
        else:
            checkBox_S_End = '0'
        arrayRow2.append(checkBox_S_End)

        comboBox_S_End_AC = uithaiStaticMPPTTest.comboBox_S_End_AC.currentIndex()
        arrayRow2.append(comboBox_S_End_AC)

        if uithaiStaticMPPTTest.checkBox_S_End_DC.isChecked():
            checkBox_S_End_DC = '1'
        else:
            checkBox_S_End_DC = '0'
        arrayRow2.append(checkBox_S_End_DC)

        comboBox_S_End_DC = uithaiStaticMPPTTest.comboBox_S_End_DC.currentIndex()
        arrayRow2.append(comboBox_S_End_DC)

        _append_dewetron_tail(arrayRow2, uithaiStaticMPPTTest)

        out = open(directory1[0], 'w+', newline='', encoding='utf-8-sig')
        csv_write = csv.writer(out, dialect="excel")
        csv_write.writerow(arrayRow1)
        csv_write.writerow(arrayRow2)
        out.close()
        QMessageBox.information(None, "实验设定提示信息", "静态MPPT测试文件保存完成", QMessageBox.Ok, QMessageBox.Ok)

# 静态MPPT测试读取设定
def Open_File_ThaiStaticMPPTTest(dialog_windowstaticmppttest, uithaiStaticMPPTTest):
    strFlag  = "0"
    directory1 = QFileDialog.getOpenFileName(None,"单个文件选择","./","Text Files(*.csv)")
    if directory1[0] == '':
        print("请选择一个文件")
    else:
        try:
            f1 = open(directory1[0], 'r', encoding='utf-8-sig')
            f1.read(1)
            f1.seek(0)
        except UnicodeDecodeError:
            f1 = open(directory1[0], 'r', encoding='gbk')
        reader = csv.DictReader(f1)
        headers = list(reader.fieldnames or [])
        i = {}
        #print(reader)
        for i in reader:
            print(i)

        if arrayRow1[0] in i:
            if i[arrayRow1[0]] == "ThaiStaticMPPTTest":
                #checkBox
                if strFlag == "0":
                    if arrayRow1[1] in i:
                        checkBox_S1 = i[arrayRow1[1]]
                        if checkBox_S1 == '1':
                            uithaiStaticMPPTTest.checkBox_S1.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1.setChecked(False)
                    else:
                        strFlag = 1

                #comBox
                if strFlag == "0":
                    if arrayRow1[2] in i:
                        comboBox_S1_AC = i[arrayRow1[2]]
                        uithaiStaticMPPTTest.comboBox_S1_AC.setCurrentIndex(int(comboBox_S1_AC))
                    else:
                        strFlag = 1

                #textEdit
                if strFlag == "0":
                    if arrayRow1[3] in i:
                        textEdit_S1_AC_VOLT = i[arrayRow1[3]]
                        uithaiStaticMPPTTest.textEdit_S1_AC_VOLT.setText(textEdit_S1_AC_VOLT)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[4] in i:
                        textEdit_S1_AC_VOLT_2 = i[arrayRow1[4]]
                        uithaiStaticMPPTTest.textEdit_S1_AC_VOLT_2.setText(textEdit_S1_AC_VOLT_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[5] in i:
                        textEdit_S1_AC_VOLT_3 = i[arrayRow1[5]]
                        uithaiStaticMPPTTest.textEdit_S1_AC_VOLT_3.setText(textEdit_S1_AC_VOLT_3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[6] in i:
                        textEdit_S1_AC_FR = i[arrayRow1[6]]
                        uithaiStaticMPPTTest.textEdit_S1_AC_FR.setText(textEdit_S1_AC_FR)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[7] in i:
                        comboBox_S1_AC_2 = i[arrayRow1[7]]
                        uithaiStaticMPPTTest.comboBox_S1_AC_2.setCurrentIndex(int(comboBox_S1_AC_2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[8] in i:
                        comboBox_S1_Vdc_Count = i[arrayRow1[8]]
                        uithaiStaticMPPTTest.comboBox_S1_Vdc_Count.setCurrentIndex(int(comboBox_S1_Vdc_Count))
                    else:
                        strFlag = 1

                # DC1
                if strFlag == "0":
                    if arrayRow1[9] in i:
                        checkBox_S1_DC1 = i[arrayRow1[9]]
                        if checkBox_S1_DC1 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC1.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[10] in i:
                        comboBox_S1_DC1_PORT = i[arrayRow1[10]]
                        uithaiStaticMPPTTest.comboBox_S1_DC1_PORT.setCurrentIndex(int(comboBox_S1_DC1_PORT))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[11] in i:
                        checkBox_S1_DC1_Vmin = i[arrayRow1[11]]
                        if checkBox_S1_DC1_Vmin == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC1_Vmin.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC1_Vmin.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[12] in i:
                        textEdit_S1_DC1_Vmin = i[arrayRow1[12]]
                        uithaiStaticMPPTTest.textEdit_S1_DC1_Vmin.setText(textEdit_S1_DC1_Vmin)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[13] in i:
                        checkBox_S1_DC1_Vnom = i[arrayRow1[13]]
                        if checkBox_S1_DC1_Vnom == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC1_Vnom.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC1_Vnom.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[14] in i:
                        textEdit_S1_DC1_Vnom = i[arrayRow1[14]]
                        uithaiStaticMPPTTest.textEdit_S1_DC1_Vnom.setText(textEdit_S1_DC1_Vnom)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[15] in i:
                        checkBox_S1_DC1_Vmax = i[arrayRow1[15]]
                        if checkBox_S1_DC1_Vmax == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC1_Vmax.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC1_Vmax.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[16] in i:
                        textEdit_S1_DC1_Vmax = i[arrayRow1[16]]
                        uithaiStaticMPPTTest.textEdit_S1_DC1_Vmax.setText(textEdit_S1_DC1_Vmax)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[17] in i:
                        checkBox_S1_DC1_Vdc1 = i[arrayRow1[17]]
                        if checkBox_S1_DC1_Vdc1 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC1_Vdc1.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC1_Vdc1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[18] in i:
                        textEdit_S1_DC1_Vdc1 = i[arrayRow1[18]]
                        uithaiStaticMPPTTest.textEdit_S1_DC1_Vdc1.setText(textEdit_S1_DC1_Vdc1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[19] in i:
                        checkBox_S1_DC1_Vdc2 = i[arrayRow1[19]]
                        if checkBox_S1_DC1_Vdc2 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC1_Vdc2.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC1_Vdc2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[20] in i:
                        textEdit_S1_DC1_Vdc2 = i[arrayRow1[20]]
                        uithaiStaticMPPTTest.textEdit_S1_DC1_Vdc2.setText(textEdit_S1_DC1_Vdc2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[21] in i:
                        checkBox_S1_DC1_Vdc3 = i[arrayRow1[21]]
                        if checkBox_S1_DC1_Vdc3 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC1_Vdc3.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC1_Vdc3.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[22] in i:
                        textEdit_S1_DC1_Vdc3 = i[arrayRow1[22]]
                        uithaiStaticMPPTTest.textEdit_S1_DC1_Vdc3.setText(textEdit_S1_DC1_Vdc3)
                    else:
                        strFlag = 1

                # DC2
                if strFlag == "0":
                    if arrayRow1[23] in i:
                        checkBox_S1_DC2 = i[arrayRow1[23]]
                        if checkBox_S1_DC2 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC2.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[24] in i:
                        comboBox_S1_DC2_PORT = i[arrayRow1[24]]
                        uithaiStaticMPPTTest.comboBox_S1_DC2_PORT.setCurrentIndex(int(comboBox_S1_DC2_PORT))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[25] in i:
                        checkBox_S1_DC2_Vmin = i[arrayRow1[25]]
                        if checkBox_S1_DC2_Vmin == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC2_Vmin.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC2_Vmin.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[26] in i:
                        textEdit_S1_DC2_Vmin = i[arrayRow1[26]]
                        uithaiStaticMPPTTest.textEdit_S1_DC2_Vmin.setText(textEdit_S1_DC2_Vmin)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[27] in i:
                        checkBox_S1_DC2_Vnom = i[arrayRow1[27]]
                        if checkBox_S1_DC2_Vnom == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC2_Vnom.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC2_Vnom.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[28] in i:
                        textEdit_S1_DC2_Vnom = i[arrayRow1[28]]
                        uithaiStaticMPPTTest.textEdit_S1_DC2_Vnom.setText(textEdit_S1_DC2_Vnom)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[29] in i:
                        checkBox_S1_DC2_Vmax = i[arrayRow1[29]]
                        if checkBox_S1_DC2_Vmax == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC2_Vmax.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC2_Vmax.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[30] in i:
                        textEdit_S1_DC2_Vmax = i[arrayRow1[30]]
                        uithaiStaticMPPTTest.textEdit_S1_DC2_Vmax.setText(textEdit_S1_DC2_Vmax)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[31] in i:
                        checkBox_S1_DC2_Vdc1 = i[arrayRow1[31]]
                        if checkBox_S1_DC2_Vdc1 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC2_Vdc1.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC2_Vdc1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[32] in i:
                        textEdit_S1_DC2_Vdc1 = i[arrayRow1[32]]
                        uithaiStaticMPPTTest.textEdit_S1_DC2_Vdc1.setText(textEdit_S1_DC2_Vdc1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[33] in i:
                        checkBox_S1_DC2_Vdc2 = i[arrayRow1[33]]
                        if checkBox_S1_DC2_Vdc2 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC2_Vdc2.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC2_Vdc2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[34] in i:
                        textEdit_S1_DC2_Vdc2 = i[arrayRow1[34]]
                        uithaiStaticMPPTTest.textEdit_S1_DC2_Vdc2.setText(textEdit_S1_DC2_Vdc2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[35] in i:
                        checkBox_S1_DC2_Vdc3 = i[arrayRow1[35]]
                        if checkBox_S1_DC2_Vdc3 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC2_Vdc3.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC2_Vdc3.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[36] in i:
                        textEdit_S1_DC2_Vdc3 = i[arrayRow1[36]]
                        uithaiStaticMPPTTest.textEdit_S1_DC2_Vdc3.setText(textEdit_S1_DC2_Vdc3)
                    else:
                        strFlag = 1
                
                # DC3
                if strFlag == "0":
                    if arrayRow1[37] in i:
                        checkBox_S1_DC3 = i[arrayRow1[37]]
                        if checkBox_S1_DC3 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC3.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC3.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[38] in i:
                        comboBox_S1_DC3_PORT = i[arrayRow1[38]]
                        uithaiStaticMPPTTest.comboBox_S1_DC3_PORT.setCurrentIndex(int(comboBox_S1_DC3_PORT))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[39] in i:
                        checkBox_S1_DC3_Vmin = i[arrayRow1[39]]
                        if checkBox_S1_DC3_Vmin == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC3_Vmin.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC3_Vmin.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[40] in i:
                        textEdit_S1_DC3_Vmin = i[arrayRow1[40]]
                        uithaiStaticMPPTTest.textEdit_S1_DC3_Vmin.setText(textEdit_S1_DC3_Vmin)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[41] in i:
                        checkBox_S1_DC3_Vnom = i[arrayRow1[41]]
                        if checkBox_S1_DC3_Vnom == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC3_Vnom.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC3_Vnom.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[42] in i:
                        textEdit_S1_DC3_Vnom = i[arrayRow1[42]]
                        uithaiStaticMPPTTest.textEdit_S1_DC3_Vnom.setText(textEdit_S1_DC3_Vnom)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[43] in i:
                        checkBox_S1_DC3_Vmax = i[arrayRow1[43]]
                        if checkBox_S1_DC3_Vmax == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC3_Vmax.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC3_Vmax.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[44] in i:
                        textEdit_S1_DC3_Vmax = i[arrayRow1[44]]
                        uithaiStaticMPPTTest.textEdit_S1_DC3_Vmax.setText(textEdit_S1_DC3_Vmax)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[45] in i:
                        checkBox_S1_DC3_Vdc1 = i[arrayRow1[45]]
                        if checkBox_S1_DC3_Vdc1 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC3_Vdc1.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC3_Vdc1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[46] in i:
                        textEdit_S1_DC3_Vdc1 = i[arrayRow1[46]]
                        uithaiStaticMPPTTest.textEdit_S1_DC3_Vdc1.setText(textEdit_S1_DC3_Vdc1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[47] in i:
                        checkBox_S1_DC3_Vdc2 = i[arrayRow1[47]]
                        if checkBox_S1_DC3_Vdc2 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC3_Vdc2.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC3_Vdc2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[48] in i:
                        textEdit_S1_DC3_Vdc2 = i[arrayRow1[48]]
                        uithaiStaticMPPTTest.textEdit_S1_DC3_Vdc2.setText(textEdit_S1_DC3_Vdc2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[49] in i:
                        checkBox_S1_DC3_Vdc3 = i[arrayRow1[49]]
                        if checkBox_S1_DC3_Vdc3 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC3_Vdc3.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC3_Vdc3.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[50] in i:
                        textEdit_S1_DC3_Vdc3 = i[arrayRow1[50]]
                        uithaiStaticMPPTTest.textEdit_S1_DC3_Vdc3.setText(textEdit_S1_DC3_Vdc3)
                    else:
                        strFlag = 1

                # DC4
                if strFlag == "0":
                    if arrayRow1[51] in i:
                        checkBox_S1_DC4 = i[arrayRow1[51]]
                        if checkBox_S1_DC4 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC4.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC4.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[52] in i:
                        comboBox_S1_DC4_PORT = i[arrayRow1[52]]
                        uithaiStaticMPPTTest.comboBox_S1_DC4_PORT.setCurrentIndex(int(comboBox_S1_DC4_PORT))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[53] in i:
                        checkBox_S1_DC4_Vmin = i[arrayRow1[53]]
                        if checkBox_S1_DC4_Vmin == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC4_Vmin.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC4_Vmin.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[54] in i:
                        textEdit_S1_DC4_Vmin = i[arrayRow1[54]]
                        uithaiStaticMPPTTest.textEdit_S1_DC4_Vmin.setText(textEdit_S1_DC4_Vmin)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[55] in i:
                        checkBox_S1_DC4_Vnom = i[arrayRow1[55]]
                        if checkBox_S1_DC4_Vnom == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC4_Vnom.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC4_Vnom.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[56] in i:
                        textEdit_S1_DC4_Vnom = i[arrayRow1[56]]
                        uithaiStaticMPPTTest.textEdit_S1_DC4_Vnom.setText(textEdit_S1_DC4_Vnom)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[57] in i:
                        checkBox_S1_DC4_Vmax = i[arrayRow1[57]]
                        if checkBox_S1_DC4_Vmax == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC4_Vmax.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC4_Vmax.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[58] in i:
                        textEdit_S1_DC4_Vmax = i[arrayRow1[58]]
                        uithaiStaticMPPTTest.textEdit_S1_DC4_Vmax.setText(textEdit_S1_DC4_Vmax)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[59] in i:
                        checkBox_S1_DC4_Vdc1 = i[arrayRow1[59]]
                        if checkBox_S1_DC4_Vdc1 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC4_Vdc1.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC4_Vdc1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[60] in i:
                        textEdit_S1_DC4_Vdc1 = i[arrayRow1[60]]
                        uithaiStaticMPPTTest.textEdit_S1_DC4_Vdc1.setText(textEdit_S1_DC4_Vdc1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[61] in i:
                        checkBox_S1_DC4_Vdc2 = i[arrayRow1[61]]
                        if checkBox_S1_DC4_Vdc2 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC4_Vdc2.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC4_Vdc2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[62] in i:
                        textEdit_S1_DC4_Vdc2 = i[arrayRow1[62]]
                        uithaiStaticMPPTTest.textEdit_S1_DC4_Vdc2.setText(textEdit_S1_DC4_Vdc2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[63] in i:
                        checkBox_S1_DC4_Vdc3 = i[arrayRow1[63]]
                        if checkBox_S1_DC4_Vdc3 == '1':
                            uithaiStaticMPPTTest.checkBox_S1_DC4_Vdc3.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S1_DC4_Vdc3.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[64] in i:
                        textEdit_S1_DC4_Vdc3 = i[arrayRow1[64]]
                        uithaiStaticMPPTTest.textEdit_S1_DC4_Vdc3.setText(textEdit_S1_DC4_Vdc3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[65] in i:
                        textEdit_S1_ACWaitTIME = i[arrayRow1[65]]
                        uithaiStaticMPPTTest.textEdit_S1_ACWaitTIME.setText(textEdit_S1_ACWaitTIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[66] in i:
                        comboBox_S1_ACWaitTIME = i[arrayRow1[66]]
                        uithaiStaticMPPTTest.comboBox_S1_ACWaitTIME.setCurrentIndex(int(comboBox_S1_ACWaitTIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[67] in i:
                        textEdit_S1_TIME = i[arrayRow1[67]]
                        uithaiStaticMPPTTest.textEdit_S1_TIME.setText(textEdit_S1_TIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[68] in i:
                        comboBox_S1_TIME = i[arrayRow1[68]]
                        uithaiStaticMPPTTest.comboBox_S1_TIME.setCurrentIndex(int(comboBox_S1_TIME))
                    else:
                        strFlag = 1

                # step2
                if strFlag == "0":
                    if arrayRow1[69] in i:
                        checkBox_S2 = i[arrayRow1[69]]
                        if checkBox_S2 == '1':
                            uithaiStaticMPPTTest.checkBox_S2.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[70] in i:
                        textEdit_S2_Vmin_PATH = i[arrayRow1[70]]
                        uithaiStaticMPPTTest.textEdit_S2_Vmin_PATH.setText(textEdit_S2_Vmin_PATH)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[71] in i:
                        textEdit_S2_Vnom_PATH = i[arrayRow1[71]]
                        uithaiStaticMPPTTest.textEdit_S2_Vnom_PATH.setText(textEdit_S2_Vnom_PATH)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[72] in i:
                        textEdit_S2_Vmax_PATH = i[arrayRow1[72]]
                        uithaiStaticMPPTTest.textEdit_S2_Vmax_PATH.setText(textEdit_S2_Vmax_PATH)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[73] in i:
                        textEdit_S2_Vdc1_PATH = i[arrayRow1[73]]
                        uithaiStaticMPPTTest.textEdit_S2_Vdc1_PATH.setText(textEdit_S2_Vdc1_PATH)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[74] in i:
                        textEdit_S2_Vdc2_PATH = i[arrayRow1[74]]
                        uithaiStaticMPPTTest.textEdit_S2_Vdc2_PATH.setText(textEdit_S2_Vdc2_PATH)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[75] in i:
                        textEdit_S2_Vdc3_PATH = i[arrayRow1[75]]
                        uithaiStaticMPPTTest.textEdit_S2_Vdc3_PATH.setText(textEdit_S2_Vdc3_PATH)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[76] in i:
                        checkBox_S2_Pn_100 = i[arrayRow1[76]]
                        if checkBox_S2_Pn_100 == '1':
                            uithaiStaticMPPTTest.checkBox_S2_Pn_100.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S2_Pn_100.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[77] in i:
                        checkBox_S2_Pn_75 = i[arrayRow1[77]]
                        if checkBox_S2_Pn_75 == '1':
                            uithaiStaticMPPTTest.checkBox_S2_Pn_75.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S2_Pn_75.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[78] in i:
                        checkBox_S2_Pn_50 = i[arrayRow1[78]]
                        if checkBox_S2_Pn_50 == '1':
                            uithaiStaticMPPTTest.checkBox_S2_Pn_50.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S2_Pn_50.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[79] in i:
                        checkBox_S2_Pn_30 = i[arrayRow1[79]]
                        if checkBox_S2_Pn_30 == '1':
                            uithaiStaticMPPTTest.checkBox_S2_Pn_30.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S2_Pn_30.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[80] in i:
                        checkBox_S2_Pn_25 = i[arrayRow1[80]]
                        if checkBox_S2_Pn_25 == '1':
                            uithaiStaticMPPTTest.checkBox_S2_Pn_25.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S2_Pn_25.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[81] in i:
                        checkBox_S2_Pn_20 = i[arrayRow1[81]]
                        if checkBox_S2_Pn_20 == '1':
                            uithaiStaticMPPTTest.checkBox_S2_Pn_20.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S2_Pn_20.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[82] in i:
                        checkBox_S2_Pn_10 = i[arrayRow1[82]]
                        if checkBox_S2_Pn_10 == '1':
                            uithaiStaticMPPTTest.checkBox_S2_Pn_10.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S2_Pn_10.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[83] in i:
                        checkBox_S2_Pn_5 = i[arrayRow1[83]]
                        if checkBox_S2_Pn_5 == '1':
                            uithaiStaticMPPTTest.checkBox_S2_Pn_5.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S2_Pn_5.setChecked(False)
                    else:
                        strFlag = 1

                # step3
                if strFlag == "0":
                    if arrayRow1[84] in i:
                        checkBox_S3 = i[arrayRow1[84]]
                        if checkBox_S3 == '1':
                            uithaiStaticMPPTTest.checkBox_S3.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S3.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[85] in i:
                        textEdit_S3_TOTAL_H = i[arrayRow1[85]]
                        uithaiStaticMPPTTest.textEdit_S3_TOTAL_H.setText(textEdit_S3_TOTAL_H)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[86] in i:
                        textEdit_S3_TOTAL_M = i[arrayRow1[86]]
                        uithaiStaticMPPTTest.textEdit_S3_TOTAL_M.setText(textEdit_S3_TOTAL_M)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[87] in i:
                        textEdit_S3_PER_H = i[arrayRow1[87]]
                        uithaiStaticMPPTTest.textEdit_S3_PER_H.setText(textEdit_S3_PER_H)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[88] in i:
                        textEdit_S3_PER_M = i[arrayRow1[88]]
                        uithaiStaticMPPTTest.textEdit_S3_PER_M.setText(textEdit_S3_PER_M)
                    else:
                        strFlag = 1

                # step_end
                if strFlag == "0":
                    if arrayRow1[89] in i:
                        checkBox_S_End = i[arrayRow1[89]]
                        if checkBox_S_End == '1':
                            uithaiStaticMPPTTest.checkBox_S_End.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S_End.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[90] in i:
                        comboBox_S_End_AC = i[arrayRow1[90]]
                        uithaiStaticMPPTTest.comboBox_S_End_AC.setCurrentIndex(int(comboBox_S_End_AC))

                if strFlag == "0":
                    if arrayRow1[91] in i:
                        checkBox_S_End_DC = i[arrayRow1[91]]
                        if checkBox_S_End_DC == '1':
                            uithaiStaticMPPTTest.checkBox_S_End_DC.setChecked(True)
                        else:
                            uithaiStaticMPPTTest.checkBox_S_End_DC.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[92] in i:
                        comboBox_S_End_DC = i[arrayRow1[92]]
                        uithaiStaticMPPTTest.comboBox_S_End_DC.setCurrentIndex(int(comboBox_S_End_DC))

            else:
                print("no")
                strFlag = "1"

        values = [i.get(header, "") for header in headers]
        _restore_dewetron_tail(headers, values, uithaiStaticMPPTTest)
        QMessageBox.information(None, "实验设定提示信息", "静态MPPT测试文件读取完成", QMessageBox.Ok, QMessageBox.Ok)



def save_file_header():
    directory1 = [r"D:\\project\\photovoltaic_automation_t\\config_files\\project_step_configs\\staticmppttest.csv"]
    if directory1[0] == '':
        print('请选择一个文件')
    else:
        out = open(directory1[0], 'w+', newline='')
        csv_write = csv.writer(out, dialect="excel")
        csv_write.writerow(arrayRow1)
        out.close()

if __name__ == "__main__":
    save_file_header()
