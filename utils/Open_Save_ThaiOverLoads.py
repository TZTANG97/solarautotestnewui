from PyQt5.QtWidgets import QMainWindow,QApplication,QDialog,QFileDialog, QMessageBox
import csv
from utils.Open_Save_ThaiXieBoDianLiu import _PageWidgetFinder
from utils.Open_Save_ThaiWT3000_Config import Save_File_ThaiWT3000_Config, Open_File_ThaiWT3000_Config
from utils.Open_Save_ThaiWT1800_Config import Save_File_ThaiWT1800_Config, Open_File_ThaiWT1800_Config
from utils.Open_Save_ThaiWT1806E_Config import Save_File_ThaiWT1806E_Config, Open_File_ThaiWT1806E_Config
from utils.Open_Save_ThaiWT5000_Config import Save_File_ThaiWT5000_Config, Open_File_ThaiWT5000_Config
from dewetron_autotest import (
    PROJECT_SPECS,
    append_dewetron_tail_columns,
    extract_ui_config,
    extract_ui_mode,
    read_dewetron_tail_columns,
)

_DEWETRON_SPEC = PROJECT_SPECS["过载能力测试"]


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


arrayRow1 = ['Style', 'checkBox_S1', 'comboBox_S1_AC',"textEdit_S1_AC_VOLT", "textEdit_S1_AC_VOLT_2",
                     "textEdit_S1_AC_VOLT_3","textEdit_S1_AC_FR","comboBox_S1_AC_2",
                "checkBox_S1_DC1", "comboBox_S1_DC1", "textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR",
                    "textEdit_S1_DC1_Voc","textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF",
                "checkBox_S1_DC2", "comboBox_S1_DC2", "textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR",
                    "textEdit_S1_DC2_Voc", "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF",
                "checkBox_S1_DC3", "comboBox_S1_DC3", "textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR",
                     "textEdit_S1_DC3_Voc", "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF", 
                "checkBox_S1_DC4", "comboBox_S1_DC4", "textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR",
                     "textEdit_S1_DC4_Voc", "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF",
                "textEdit_S1_ACWaitTIME", "comboBox_S1_ACWaitTIME", "textEdit_S1_TIME", "comboBox_S1_TIME",
                "checkBox_S2", "checkBox_S2_WT3000", "checkBox_S2_WT1800",
                "checkBox_S3", "textEdit_S3_TIME_2", "comboBox_S3_TIME_2",
                "checkBox_S5", "comboBox_S5_AC", "checkBox_S5_DC1", "comboBox_S5_DC1", "checkBox_S5_DC2",
                "comboBox_S5_DC2", "checkBox_S5_DC3", "comboBox_S5_DC3", "checkBox_S5_DC4", "comboBox_S5_DC4",
            "checkBox_S2_WT1806E", "checkBox_S2_WT5000"]

#德国overloads保存设定
def Save_File_ThaiOverLoads(kwargs):
    dialog_windowoverloads = kwargs['dialog_windowoverloads']
    uiThaiOverLoads = kwargs['uiThaiOverLoads']
    uiThiaWT3000E = kwargs['uiThiaWT3000E']
    uiThiaWT1800 = kwargs['uiThiaWT1800']
    uiThiaWT1806E = kwargs['uiThiaWT1806E']
    uiThiaWT5000 = kwargs['uiThiaWT5000']
    result = []
    directory1 = QFileDialog.getSaveFileName(None, "单个文件保存", "./", "Text Files(*.csv)")
    if directory1[0] == '':
        print('请选择一个文件')
    else:
        arrayRow2 = ['ThaiOverLoads']

        # step1
        if uiThaiOverLoads.checkBox_S1.isChecked():
            checkBox_S1 = '1'
        else:
            checkBox_S1 = '0'
        arrayRow2.append(checkBox_S1)

        comboBox_S1_AC = uiThaiOverLoads.comboBox_S1_AC.currentIndex()
        arrayRow2.append(comboBox_S1_AC)

        textEdit_S1_AC_VOLT = uiThaiOverLoads.textEdit_S1_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT)

        textEdit_S1_AC_VOLT_2 = uiThaiOverLoads.textEdit_S1_AC_VOLT_2.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_2)

        textEdit_S1_AC_VOLT_3 = uiThaiOverLoads.textEdit_S1_AC_VOLT_3.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_3)

        textEdit_S1_AC_FR = uiThaiOverLoads.textEdit_S1_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S1_AC_FR)

        comboBox_S1_AC_2 = uiThaiOverLoads.comboBox_S1_AC_2.currentIndex()
        arrayRow2.append(comboBox_S1_AC_2)

        if uiThaiOverLoads.checkBox_S1_DC1.isChecked():
            checkBox_S1_DC1 = '1'
        else:
            checkBox_S1_DC1 = '0'
        arrayRow2.append(checkBox_S1_DC1)

        comboBox_S1_DC1 = uiThaiOverLoads.comboBox_S1_DC1.currentIndex()
        arrayRow2.append(comboBox_S1_DC1)

        textEdit_S1_DC1_VOLT = uiThaiOverLoads.textEdit_S1_DC1_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_VOLT)

        textEdit_S1_DC1_CURR = uiThaiOverLoads.textEdit_S1_DC1_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_CURR)

        textEdit_S1_DC1_Voc = uiThaiOverLoads.textEdit_S1_DC1_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Voc)

        textEdit_S1_DC1_Isc = uiThaiOverLoads.textEdit_S1_DC1_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Isc)
        
        textEdit_S1_DC1_PF = uiThaiOverLoads.textEdit_S1_DC1_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF)

        if uiThaiOverLoads.checkBox_S1_DC2.isChecked():
            checkBox_S1_DC2 = '1'
        else:
            checkBox_S1_DC2 = '0'
        arrayRow2.append(checkBox_S1_DC2)

        comboBox_S1_DC2 = uiThaiOverLoads.comboBox_S1_DC2.currentIndex()
        arrayRow2.append(comboBox_S1_DC2)

        textEdit_S1_DC2_VOLT = uiThaiOverLoads.textEdit_S1_DC2_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_VOLT)

        textEdit_S1_DC2_CURR = uiThaiOverLoads.textEdit_S1_DC2_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_CURR)

        textEdit_S1_DC2_Voc = uiThaiOverLoads.textEdit_S1_DC2_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Voc)

        textEdit_S1_DC2_Isc = uiThaiOverLoads.textEdit_S1_DC2_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Isc)
        
        textEdit_S1_DC2_PF = uiThaiOverLoads.textEdit_S1_DC2_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_PF)
        
        if uiThaiOverLoads.checkBox_S1_DC3.isChecked():
            checkBox_S1_DC3 = '1'
        else:
            checkBox_S1_DC3 = '0'
        arrayRow2.append(checkBox_S1_DC3)

        comboBox_S1_DC3 = uiThaiOverLoads.comboBox_S1_DC3.currentIndex()
        arrayRow2.append(comboBox_S1_DC3)

        textEdit_S1_DC3_VOLT = uiThaiOverLoads.textEdit_S1_DC3_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_VOLT)

        textEdit_S1_DC3_CURR = uiThaiOverLoads.textEdit_S1_DC3_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_CURR)

        textEdit_S1_DC3_Voc = uiThaiOverLoads.textEdit_S1_DC3_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Voc)

        textEdit_S1_DC3_Isc = uiThaiOverLoads.textEdit_S1_DC3_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Isc)
        
        textEdit_S1_DC3_PF = uiThaiOverLoads.textEdit_S1_DC3_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_PF)

        if uiThaiOverLoads.checkBox_S1_DC4.isChecked():
            checkBox_S1_DC4 = '1'
        else:
            checkBox_S1_DC4 = '0'
        arrayRow2.append(checkBox_S1_DC4)

        comboBox_S1_DC4 = uiThaiOverLoads.comboBox_S1_DC4.currentIndex()
        arrayRow2.append(comboBox_S1_DC4)

        textEdit_S1_DC4_VOLT = uiThaiOverLoads.textEdit_S1_DC4_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_VOLT)

        textEdit_S1_DC4_CURR = uiThaiOverLoads.textEdit_S1_DC4_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_CURR)

        textEdit_S1_DC4_Voc = uiThaiOverLoads.textEdit_S1_DC4_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Voc)

        textEdit_S1_DC4_Isc = uiThaiOverLoads.textEdit_S1_DC4_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Isc)
        
        textEdit_S1_DC4_PF = uiThaiOverLoads.textEdit_S1_DC4_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_PF)

        textEdit_S1_ACWaitTIME = uiThaiOverLoads.textEdit_S1_ACWaitTIME.toPlainText()
        arrayRow2.append(textEdit_S1_ACWaitTIME)

        comboBox_S1_ACWaitTIME = uiThaiOverLoads.comboBox_S1_ACWaitTIME.currentIndex()
        arrayRow2.append(comboBox_S1_ACWaitTIME)
        
        textEdit_S1_TIME = uiThaiOverLoads.textEdit_S1_TIME.toPlainText()
        arrayRow2.append(textEdit_S1_TIME)

        comboBox_S1_TIME = uiThaiOverLoads.comboBox_S1_TIME.currentIndex()
        arrayRow2.append(comboBox_S1_TIME)

        # step2
        if uiThaiOverLoads.checkBox_S2.isChecked():
            checkBox_S2 = '1'
        else:
            checkBox_S2 = '0'
        arrayRow2.append(checkBox_S2)

        if uiThaiOverLoads.radioButton_S2_WT3000.isChecked():
            checkBox_S2_WT3000 = '1'
        else:
            checkBox_S2_WT3000 = '0'
        arrayRow2.append(checkBox_S2_WT3000)

        if uiThaiOverLoads.radioButton_S2_WT1800.isChecked():
            checkBox_S2_WT1800 = '1'
        else:
            checkBox_S2_WT1800 = '0'
        arrayRow2.append(checkBox_S2_WT1800)

        # step3
        if uiThaiOverLoads.checkBox_S3.isChecked():
            checkBox_S3 = '1'
        else:
            checkBox_S3 = '0'
        arrayRow2.append(checkBox_S3)
        
        textEdit_S3_TIME_2 = uiThaiOverLoads.textEdit_S3_TIME_2.toPlainText()
        arrayRow2.append(textEdit_S3_TIME_2)

        comboBox_S3_TIME_2 = uiThaiOverLoads.comboBox_S3_TIME_2.currentIndex()
        arrayRow2.append(comboBox_S3_TIME_2)

        # step14
        if uiThaiOverLoads.checkBox_S5.isChecked():
            checkBox_S5 = '1'
        else:
            checkBox_S5 = '0'
        arrayRow2.append(checkBox_S5)

        comboBox_S5_AC = uiThaiOverLoads.comboBox_S5_AC.currentIndex()
        arrayRow2.append(comboBox_S5_AC)
        
        if uiThaiOverLoads.checkBox_S5_DC1.isChecked():
            checkBox_S5_DC1 = '1'
        else:
            checkBox_S5_DC1 = '0'
        arrayRow2.append(checkBox_S5_DC1)

        comboBox_S5_DC1 = uiThaiOverLoads.comboBox_S5_DC1.currentIndex()
        arrayRow2.append(comboBox_S5_DC1)
        
        if uiThaiOverLoads.checkBox_S5_DC2.isChecked():
            checkBox_S5_DC2 = '1'
        else:
            checkBox_S5_DC2 = '0'
        arrayRow2.append(checkBox_S5_DC2)

        comboBox_S5_DC2 = uiThaiOverLoads.comboBox_S5_DC2.currentIndex()
        arrayRow2.append(comboBox_S5_DC2)
        
        if uiThaiOverLoads.checkBox_S5_DC3.isChecked():
            checkBox_S5_DC3 = '1'
        else:
            checkBox_S5_DC3 = '0'
        arrayRow2.append(checkBox_S5_DC3)

        comboBox_S5_DC3 = uiThaiOverLoads.comboBox_S5_DC3.currentIndex()
        arrayRow2.append(comboBox_S5_DC3)

        if uiThaiOverLoads.checkBox_S5_DC4.isChecked():
            checkBox_S5_DC4 = '1'
        else:
            checkBox_S5_DC4 = '0'
        arrayRow2.append(checkBox_S5_DC4)

        comboBox_S5_DC4 = uiThaiOverLoads.comboBox_S5_DC4.currentIndex()
        arrayRow2.append(comboBox_S5_DC4)

        if uiThaiOverLoads.radioButton_S2_WT1806E.isChecked():
            checkBox_S2_WT1806E = '1'
        else:
            checkBox_S2_WT1806E = '0'
        arrayRow2.append(checkBox_S2_WT1806E)

        if uiThaiOverLoads.radioButton_S2_WT5000.isChecked():
            checkBox_S2_WT5000 = '1'
        else:
            checkBox_S2_WT5000 = '0'
        arrayRow2.append(checkBox_S2_WT5000)

        _append_dewetron_tail(arrayRow2, uiThaiOverLoads)

        result = []
        if uiThaiOverLoads.radioButton_S2_WT3000.isChecked():
            result = Save_File_ThaiWT3000_Config(_PageWidgetFinder(uiThaiOverLoads._wtStacked.widget(0)))
        elif uiThaiOverLoads.radioButton_S2_WT1800.isChecked():
            result = Save_File_ThaiWT1800_Config(_PageWidgetFinder(uiThaiOverLoads._wtStacked.widget(1)))
        elif uiThaiOverLoads.radioButton_S2_WT1806E.isChecked():
            result = Save_File_ThaiWT1806E_Config(_PageWidgetFinder(uiThaiOverLoads._wtStacked.widget(2)))
        elif uiThaiOverLoads.radioButton_S2_WT5000.isChecked():
            result = Save_File_ThaiWT5000_Config(_PageWidgetFinder(uiThaiOverLoads._wtStacked.widget(3)))

        out = open(directory1[0], 'w+', newline='', encoding='utf-8-sig')
        csv_write = csv.writer(out, dialect="excel")
        csv_write.writerow(arrayRow1)
        csv_write.writerow(arrayRow2)
        if len(result) > 0:
            csv_write.writerow(result[0])
            csv_write.writerow(result[1])
        out.close()
        QMessageBox.information(None, "实验设定提示信息", "overloads文件保存完成", QMessageBox.Ok, QMessageBox.Ok)

#德国overloads读取设定
def Open_File_ThaiOverLoads(kwargs):
    dialog_windowoverloads = kwargs['dialog_windowoverloads']
    uiThaiOverLoads = kwargs['uiThaiOverLoads']
    uiThiaWT3000E = kwargs['uiThiaWT3000E']
    uiThiaWT1800 = kwargs['uiThiaWT1800']
    uiThiaWT1806E = kwargs['uiThiaWT1806E']
    uiThiaWT5000 = kwargs['uiThiaWT5000']
    strFlag  = "0"
    result_list = []
    config_dict = {}
    wt_config_dict = {}
    directory1 = QFileDialog.getOpenFileName(None, "单个文件选择", "./", "Text Files(*.csv)")
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
                if config_dict[arrayRow1[0]] == "ThaiOverLoads":
                    # step1
                    if strFlag == "0":
                        if arrayRow1[1] in config_dict:
                            checkBox_S1 = config_dict[arrayRow1[1]]
                            if checkBox_S1 == '1':
                                uiThaiOverLoads.checkBox_S1.setChecked(True)
                            else:
                                uiThaiOverLoads.checkBox_S1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[2] in config_dict:
                            comboBox_S1_AC = config_dict[arrayRow1[2]]
                            uiThaiOverLoads.comboBox_S1_AC.setCurrentIndex(int(comboBox_S1_AC))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[3] in config_dict:
                            textEdit_S1_AC_VOLT = config_dict[arrayRow1[3]]
                            uiThaiOverLoads.textEdit_S1_AC_VOLT.setText(textEdit_S1_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[4] in config_dict:
                            textEdit_S1_AC_VOLT_2 = config_dict[arrayRow1[4]]
                            uiThaiOverLoads.textEdit_S1_AC_VOLT_2.setText(textEdit_S1_AC_VOLT_2)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[5] in config_dict:
                            textEdit_S1_AC_VOLT_3 = config_dict[arrayRow1[5]]
                            uiThaiOverLoads.textEdit_S1_AC_VOLT_3.setText(textEdit_S1_AC_VOLT_3)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[6] in config_dict:
                            textEdit_S1_AC_FR = config_dict[arrayRow1[6]]
                            uiThaiOverLoads.textEdit_S1_AC_FR.setText(textEdit_S1_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[7] in config_dict:
                            comboBox_S1_AC_2 = config_dict[arrayRow1[7]]
                            uiThaiOverLoads.comboBox_S1_AC_2.setCurrentIndex(int(comboBox_S1_AC_2))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[8] in config_dict:
                            checkBox_S1_DC1 = config_dict[arrayRow1[8]]
                            if checkBox_S1_DC1 == '1':
                                uiThaiOverLoads.checkBox_S1_DC1.setChecked(True)
                            else:
                                uiThaiOverLoads.checkBox_S1_DC1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[9] in config_dict:
                            comboBox_S1_DC1 = config_dict[arrayRow1[9]]
                            uiThaiOverLoads.comboBox_S1_DC1.setCurrentIndex(int(comboBox_S1_DC1))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[10] in config_dict:
                            textEdit_S1_DC1_VOLT = config_dict[arrayRow1[10]]
                            uiThaiOverLoads.textEdit_S1_DC1_VOLT.setText(textEdit_S1_DC1_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[11] in config_dict:
                            textEdit_S1_DC1_CURR = config_dict[arrayRow1[11]]
                            uiThaiOverLoads.textEdit_S1_DC1_CURR.setText(textEdit_S1_DC1_CURR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[12] in config_dict:
                            textEdit_S1_DC1_Voc = config_dict[arrayRow1[12]]
                            uiThaiOverLoads.textEdit_S1_DC1_Voc.setText(textEdit_S1_DC1_Voc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[13] in config_dict:
                            textEdit_S1_DC1_Isc = config_dict[arrayRow1[13]]
                            uiThaiOverLoads.textEdit_S1_DC1_Isc.setText(textEdit_S1_DC1_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[14] in config_dict:
                            textEdit_S1_DC1_PF = config_dict[arrayRow1[14]]
                            uiThaiOverLoads.textEdit_S1_DC1_PF.setText(textEdit_S1_DC1_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[15] in config_dict:
                            checkBox_S1_DC2 = config_dict[arrayRow1[15]]
                            if checkBox_S1_DC2 == '1':
                                uiThaiOverLoads.checkBox_S1_DC2.setChecked(True)
                            else:
                                uiThaiOverLoads.checkBox_S1_DC2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[16] in config_dict:
                            comboBox_S1_DC2 = config_dict[arrayRow1[16]]
                            uiThaiOverLoads.comboBox_S1_DC2.setCurrentIndex(int(comboBox_S1_DC2))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[17] in config_dict:
                            textEdit_S1_DC2_VOLT = config_dict[arrayRow1[17]]
                            uiThaiOverLoads.textEdit_S1_DC2_VOLT.setText(textEdit_S1_DC2_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[18] in config_dict:
                            textEdit_S1_DC2_CURR = config_dict[arrayRow1[18]]
                            uiThaiOverLoads.textEdit_S1_DC2_CURR.setText(textEdit_S1_DC2_CURR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[19] in config_dict:
                            textEdit_S1_DC2_Voc = config_dict[arrayRow1[19]]
                            uiThaiOverLoads.textEdit_S1_DC2_Voc.setText(textEdit_S1_DC2_Voc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[20] in config_dict:
                            textEdit_S1_DC2_Isc = config_dict[arrayRow1[20]]
                            uiThaiOverLoads.textEdit_S1_DC2_Isc.setText(textEdit_S1_DC2_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[21] in config_dict:
                            textEdit_S1_DC2_PF = config_dict[arrayRow1[21]]
                            uiThaiOverLoads.textEdit_S1_DC2_PF.setText(textEdit_S1_DC2_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[22] in config_dict:
                            checkBox_S1_DC3 = config_dict[arrayRow1[22]]
                            if checkBox_S1_DC3 == '1':
                                uiThaiOverLoads.checkBox_S1_DC3.setChecked(True)
                            else:
                                uiThaiOverLoads.checkBox_S1_DC3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[23] in config_dict:
                            comboBox_S1_DC3 = config_dict[arrayRow1[23]]
                            uiThaiOverLoads.comboBox_S1_DC3.setCurrentIndex(int(comboBox_S1_DC3))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[24] in config_dict:
                            textEdit_S1_DC3_VOLT = config_dict[arrayRow1[24]]
                            uiThaiOverLoads.textEdit_S1_DC3_VOLT.setText(textEdit_S1_DC3_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[25] in config_dict:
                            textEdit_S1_DC3_CURR = config_dict[arrayRow1[25]]
                            uiThaiOverLoads.textEdit_S1_DC3_CURR.setText(textEdit_S1_DC3_CURR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[26] in config_dict:
                            textEdit_S1_DC3_Voc = config_dict[arrayRow1[26]]
                            uiThaiOverLoads.textEdit_S1_DC3_Voc.setText(textEdit_S1_DC3_Voc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[27] in config_dict:
                            textEdit_S1_DC3_Isc = config_dict[arrayRow1[27]]
                            uiThaiOverLoads.textEdit_S1_DC3_Isc.setText(textEdit_S1_DC3_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[28] in config_dict:
                            textEdit_S1_DC3_PF = config_dict[arrayRow1[28]]
                            uiThaiOverLoads.textEdit_S1_DC3_PF.setText(textEdit_S1_DC3_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[29] in config_dict:
                            checkBox_S1_DC4 = config_dict[arrayRow1[29]]
                            if checkBox_S1_DC4 == '1':
                                uiThaiOverLoads.checkBox_S1_DC4.setChecked(True)
                            else:
                                uiThaiOverLoads.checkBox_S1_DC4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[30] in config_dict:
                            comboBox_S1_DC4 = config_dict[arrayRow1[30]]
                            uiThaiOverLoads.comboBox_S1_DC4.setCurrentIndex(int(comboBox_S1_DC4))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[31] in config_dict:
                            textEdit_S1_DC4_VOLT = config_dict[arrayRow1[31]]
                            uiThaiOverLoads.textEdit_S1_DC4_VOLT.setText(textEdit_S1_DC4_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[32] in config_dict:
                            textEdit_S1_DC4_CURR = config_dict[arrayRow1[32]]
                            uiThaiOverLoads.textEdit_S1_DC4_CURR.setText(textEdit_S1_DC4_CURR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[33] in config_dict:
                            textEdit_S1_DC4_Voc = config_dict[arrayRow1[33]]
                            uiThaiOverLoads.textEdit_S1_DC4_Voc.setText(textEdit_S1_DC4_Voc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[34] in config_dict:
                            textEdit_S1_DC4_Isc = config_dict[arrayRow1[34]]
                            uiThaiOverLoads.textEdit_S1_DC4_Isc.setText(textEdit_S1_DC4_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[35] in config_dict:
                            textEdit_S1_DC4_PF = config_dict[arrayRow1[35]]
                            uiThaiOverLoads.textEdit_S1_DC4_PF.setText(textEdit_S1_DC4_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[36] in config_dict:
                            textEdit_S1_ACWaitTIME = config_dict[arrayRow1[36]]
                            uiThaiOverLoads.textEdit_S1_ACWaitTIME.setText(textEdit_S1_ACWaitTIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[37] in config_dict:
                            comboBox_S1_ACWaitTIME = config_dict[arrayRow1[37]]
                            uiThaiOverLoads.comboBox_S1_ACWaitTIME.setCurrentIndex(int(comboBox_S1_ACWaitTIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[38] in config_dict:
                            textEdit_S1_TIME = config_dict[arrayRow1[38]]
                            uiThaiOverLoads.textEdit_S1_TIME.setText(textEdit_S1_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[39] in config_dict:
                            comboBox_S1_TIME = config_dict[arrayRow1[39]]
                            uiThaiOverLoads.comboBox_S1_TIME.setCurrentIndex(int(comboBox_S1_TIME))
                        else:
                            strFlag = 1
                    
                    # step2
                    if strFlag == "0":
                        if arrayRow1[40] in config_dict:
                            checkBox_S2 = config_dict[arrayRow1[40]]
                            if checkBox_S2 == '1':
                                uiThaiOverLoads.checkBox_S2.setChecked(True)
                            else:
                                uiThaiOverLoads.checkBox_S2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[41] in config_dict:
                            checkBox_S2_WT3000 = config_dict[arrayRow1[41]]
                            if checkBox_S2_WT3000 == '1':
                                uiThaiOverLoads.radioButton_S2_WT3000.setChecked(True)
                            else:
                                uiThaiOverLoads.radioButton_S2_WT3000.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[42] in config_dict:
                            checkBox_S2_WT1800 = config_dict[arrayRow1[42]]
                            if checkBox_S2_WT1800 == '1':
                                uiThaiOverLoads.radioButton_S2_WT1800.setChecked(True)
                            else:
                                uiThaiOverLoads.radioButton_S2_WT1800.setChecked(False)
                        else:
                            strFlag = 1

                    # step3
                    if strFlag == "0":
                        if arrayRow1[43] in config_dict:
                            checkBox_S3 = config_dict[arrayRow1[43]]
                            if checkBox_S3 == '1':
                                uiThaiOverLoads.checkBox_S3.setChecked(True)
                            else:
                                uiThaiOverLoads.checkBox_S3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[44] in config_dict:
                            textEdit_S3_TIME_2 = config_dict[arrayRow1[44]]
                            uiThaiOverLoads.textEdit_S3_TIME_2.setText(textEdit_S3_TIME_2)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[45] in config_dict:
                            comboBox_S3_TIME_2 = config_dict[arrayRow1[45]]
                            uiThaiOverLoads.comboBox_S3_TIME_2.setCurrentIndex(int(comboBox_S3_TIME_2))
                        else:
                            strFlag = 1
                    
                    # step14
                    if strFlag == "0":
                        if arrayRow1[46] in config_dict:
                            checkBox_S5 = config_dict[arrayRow1[46]]
                            if checkBox_S5 == '1':
                                uiThaiOverLoads.checkBox_S5.setChecked(True)
                            else:
                                uiThaiOverLoads.checkBox_S5.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[47] in config_dict:
                            comboBox_S5_AC = config_dict[arrayRow1[47]]
                            uiThaiOverLoads.comboBox_S5_AC.setCurrentIndex(int(comboBox_S5_AC))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[48] in config_dict:
                            checkBox_S5_DC1 = config_dict[arrayRow1[48]]
                            if checkBox_S5_DC1 == '1':
                                uiThaiOverLoads.checkBox_S5_DC1.setChecked(True)
                            else:
                                uiThaiOverLoads.checkBox_S5_DC1.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[49] in config_dict:
                            comboBox_S5_DC1 = config_dict[arrayRow1[49]]
                            uiThaiOverLoads.comboBox_S5_DC1.setCurrentIndex(int(comboBox_S5_DC1))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[50] in config_dict:
                            checkBox_S5_DC2 = config_dict[arrayRow1[50]]
                            if checkBox_S5_DC2 == '1':
                                uiThaiOverLoads.checkBox_S5_DC2.setChecked(True)
                            else:
                                uiThaiOverLoads.checkBox_S5_DC2.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[51] in config_dict:
                            comboBox_S5_DC2 = config_dict[arrayRow1[51]]
                            uiThaiOverLoads.comboBox_S5_DC2.setCurrentIndex(int(comboBox_S5_DC2))
                        else:
                            strFlag = 1
                    if strFlag == "0":
                        if arrayRow1[52] in config_dict:
                            checkBox_S5_DC3 = config_dict[arrayRow1[52]]
                            if checkBox_S5_DC3 == '1':
                                uiThaiOverLoads.checkBox_S5_DC3.setChecked(True)
                            else:
                                uiThaiOverLoads.checkBox_S5_DC3.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[53] in config_dict:
                            comboBox_S5_DC3 = config_dict[arrayRow1[53]]
                            uiThaiOverLoads.comboBox_S5_DC3.setCurrentIndex(int(comboBox_S5_DC3))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[54] in config_dict:
                            checkBox_S5_DC4 = config_dict[arrayRow1[54]]
                            if checkBox_S5_DC4 == '1':
                                uiThaiOverLoads.checkBox_S5_DC4.setChecked(True)
                            else:
                                uiThaiOverLoads.checkBox_S5_DC4.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[55] in config_dict:
                            comboBox_S5_DC4 = config_dict[arrayRow1[55]]
                            uiThaiOverLoads.comboBox_S5_DC4.setCurrentIndex(int(comboBox_S5_DC4))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[56] in config_dict:
                            checkBox_S2_WT1806E = config_dict[arrayRow1[56]]
                            if checkBox_S2_WT1806E == '1':
                                uiThaiOverLoads.radioButton_S2_WT1806E.setChecked(True)
                            else:
                                uiThaiOverLoads.radioButton_S2_WT1806E.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[57] in config_dict:
                            checkBox_S2_WT5000 = config_dict[arrayRow1[57]]
                            if checkBox_S2_WT5000 == '1':
                                uiThaiOverLoads.radioButton_S2_WT5000.setChecked(True)
                            else:
                                uiThaiOverLoads.radioButton_S2_WT5000.setChecked(False)
                        else:
                            strFlag = 1

                    if arrayRow1[41] in config_dict:
                        checkBox_S2_WT3000 = config_dict[arrayRow1[41]]
                        if checkBox_S2_WT3000 == '1':
                            page0 = uiThaiOverLoads._wtStacked.widget(0)
                            Open_File_ThaiWT3000_Config(_PageWidgetFinder(page0), wt_config_dict)
                    else:
                        strFlag = 1

                    if arrayRow1[42] in config_dict:
                        checkBox_S2_WT1800 = config_dict[arrayRow1[42]]
                        if checkBox_S2_WT1800 == '1':
                            page1 = uiThaiOverLoads._wtStacked.widget(1)
                            Open_File_ThaiWT1800_Config(_PageWidgetFinder(page1), wt_config_dict)
                    else:
                        strFlag = 1

                    if arrayRow1[56] in config_dict:
                        checkBox_S2_WT1806E = config_dict[arrayRow1[56]]
                        if checkBox_S2_WT1806E == '1':
                            page2 = uiThaiOverLoads._wtStacked.widget(2)
                            Open_File_ThaiWT1806E_Config(_PageWidgetFinder(page2), wt_config_dict)
                    else:
                        strFlag = 1

                    if arrayRow1[57] in config_dict:
                        checkBox_S2_WT5000 = config_dict[arrayRow1[57]]
                        if checkBox_S2_WT5000 == '1':
                            page3 = uiThaiOverLoads._wtStacked.widget(3)
                            Open_File_ThaiWT5000_Config(_PageWidgetFinder(page3), wt_config_dict)
                    else:
                        strFlag = 1

                    _restore_dewetron_tail(result_list[0], result_list[1], uiThaiOverLoads)

        QMessageBox.information(None, "实验设定提示信息", "overloads文件读取完成", QMessageBox.Ok, QMessageBox.Ok)

# def save_file_header():
#     directory1 = [r"D:\\project\\photovoltaic_automation_t\\config_files\\project_step_configs\\overloads.csv"]
#     if directory1[0] == '':
#         print('请选择一个文件')
#     else:
#         out = open(directory1[0], 'w+', newline='')
#         csv_write = csv.writer(out, dialect="excel")
#         csv_write.writerow(arrayRow1)
#         out.close()

# if __name__ == "__main__":
#     save_file_header()