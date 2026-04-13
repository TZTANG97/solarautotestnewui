from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, \
    QFileDialog, QMessageBox
import csv
from utils.Open_Save_ThaiWT3000_Config import Save_File_ThaiWT3000_Config, Open_File_ThaiWT3000_Config
from utils.Open_Save_ThaiWT1800_Config import Save_File_ThaiWT1800_Config, Open_File_ThaiWT1800_Config
from utils.Open_Save_ThaiWT1806E_Config import Save_File_ThaiWT1806E_Config, Open_File_ThaiWT1806E_Config
from utils.Open_Save_ThaiWT5000_Config import Save_File_ThaiWT5000_Config, Open_File_ThaiWT5000_Config

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
    'checkBox_S2', "checkBox_S2_WT3000", "checkBox_S2_WT1800",
    'checkBox_S3', 'textEdit_S3_AC_VOLT', 'comboBox_S3_AC_Trend', 'textEdit_S3_AC_Range_S', 'textEdit_S3_AC_Range_E', 'textEdit_S3_AC_Range_Point',
        'textEdit_S3_AC_Step', 'textEdit_S3_AC_FR', 'textEdit_S3_TIME', 'comboBox_S3_TIME',
    'checkBox_S4', 'textEdit_S4_AC_VOLT', 'comboBox_S4_AC_Trend', 'textEdit_S4_AC_Range_S', 'textEdit_S4_AC_Range_E', 'textEdit_S4_AC_Range_Point',
        'textEdit_S4_AC_Step', 'textEdit_S4_AC_FR', 'textEdit_S4_TIME', 'comboBox_S4_TIME',
    'checkBox_S5', 'textEdit_S5_AC_VOLT', 'comboBox_S5_AC_Trend', 'textEdit_S5_AC_Range_S', 'textEdit_S5_AC_Range_E', 'textEdit_S5_AC_Range_Point',
        'textEdit_S5_AC_Step', 'textEdit_S5_AC_FR', 'textEdit_S5_TIME', 'comboBox_S5_TIME',
    'checkBox_S6', 'textEdit_S6_AC_VOLT', 'comboBox_S6_AC_Trend', 'textEdit_S6_AC_Range_S', 'textEdit_S6_AC_Range_E', 'textEdit_S6_AC_Range_Point',
        'textEdit_S6_AC_Step', 'textEdit_S6_AC_FR', 'textEdit_S6_TIME', 'comboBox_S6_TIME',
    'checkBox_S_End', "comboBox_S_End_AC", "checkBox_S_End_DC1", "comboBox_S_End_DC1","checkBox_S_End_DC2",
        "comboBox_S_End_DC2","checkBox_S_End_DC3", "comboBox_S_End_DC3","checkBox_S_End_DC4","comboBox_S_End_DC4",
    "checkBox_S2_WT1806E", "checkBox_S2_WT5000"]

# 静态QU保存设定
def Save_File_ThaiStaticQU(kwargs):
    dialog_window = kwargs['dialog_windowstaticQU']
    uithaistaticQU = kwargs['uiThaiStaticQU']
    uiThiaWT3000E = kwargs['uiThiaWT3000E']
    uiThiaWT1800 = kwargs['uiThiaWT1800']
    uiThiaWT1806E = kwargs['uiThiaWT1806E']
    uiThiaWT5000 = kwargs['uiThiaWT5000']
    result = []
    directory1 = QFileDialog.getSaveFileName(dialog_window,"单个文件保存","./","Text Files(*.csv)")
    if directory1[0] == '':
        print('请选择一个文件')
    else:
        arrayRow2 = ['ThaiStaticQU']

        if uithaistaticQU.checkBox_S1.isChecked():
            checkBox_S1 = '1'
        else:
            checkBox_S1 = '0'
        arrayRow2.append(checkBox_S1)

        comboBox_S1_AC = uithaistaticQU.comboBox_S1_AC.currentIndex()
        arrayRow2.append(comboBox_S1_AC)

        textEdit_S1_AC_VOLT = uithaistaticQU.textEdit_S1_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT)

        textEdit_S1_AC_VOLT_2 = uithaistaticQU.textEdit_S1_AC_VOLT_2.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_2)

        textEdit_S1_AC_VOLT_3 = uithaistaticQU.textEdit_S1_AC_VOLT_3.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_3)

        textEdit_S1_AC_FR = uithaistaticQU.textEdit_S1_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S1_AC_FR)

        comboBox_S1_AC_2 = uithaistaticQU.comboBox_S1_AC_2.currentIndex()
        arrayRow2.append(comboBox_S1_AC_2)

        if uithaistaticQU.checkBox_S1_DC1.isChecked():
            checkBox_S1_DC1 = '1'
        else:
            checkBox_S1_DC1 = '0'
        arrayRow2.append(checkBox_S1_DC1)

        comboBox_S1_DC1 = uithaistaticQU.comboBox_S1_DC1.currentIndex()
        arrayRow2.append(comboBox_S1_DC1)

        textEdit_S1_DC1_VOLT = uithaistaticQU.textEdit_S1_DC1_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_VOLT)

        textEdit_S1_DC1_CURR = uithaistaticQU.textEdit_S1_DC1_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_CURR)

        textEdit_S1_DC1_Voc = uithaistaticQU.textEdit_S1_DC1_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Voc)
        
        textEdit_S1_DC1_Isc = uithaistaticQU.textEdit_S1_DC1_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Isc)
        
        textEdit_S1_DC1_PF = uithaistaticQU.textEdit_S1_DC1_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF)

        if uithaistaticQU.checkBox_S1_DC2.isChecked():
            checkBox_S1_DC2 = '1'
        else:
            checkBox_S1_DC2 = '0'
        arrayRow2.append(checkBox_S1_DC2)

        comboBox_S1_DC2 = uithaistaticQU.comboBox_S1_DC2.currentIndex()
        arrayRow2.append(comboBox_S1_DC2)

        textEdit_S1_DC2_VOLT = uithaistaticQU.textEdit_S1_DC2_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_VOLT)

        textEdit_S1_DC2_CURR = uithaistaticQU.textEdit_S1_DC2_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_CURR)

        textEdit_S1_DC2_Voc = uithaistaticQU.textEdit_S1_DC2_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Voc)
        
        textEdit_S1_DC2_Isc = uithaistaticQU.textEdit_S1_DC2_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Isc)
        
        textEdit_S1_DC2_PF = uithaistaticQU.textEdit_S1_DC2_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_PF)

        if uithaistaticQU.checkBox_S1_DC3.isChecked():
            checkBox_S1_DC3 = '1'
        else:
            checkBox_S1_DC3 = '0'
        arrayRow2.append(checkBox_S1_DC3)

        comboBox_S1_DC3 = uithaistaticQU.comboBox_S1_DC3.currentIndex()
        arrayRow2.append(comboBox_S1_DC3)

        textEdit_S1_DC3_VOLT = uithaistaticQU.textEdit_S1_DC3_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_VOLT)

        textEdit_S1_DC3_CURR = uithaistaticQU.textEdit_S1_DC3_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_CURR)

        textEdit_S1_DC3_Voc = uithaistaticQU.textEdit_S1_DC3_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Voc)
        
        textEdit_S1_DC3_Isc = uithaistaticQU.textEdit_S1_DC3_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Isc)
        
        textEdit_S1_DC3_PF = uithaistaticQU.textEdit_S1_DC3_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_PF)

        if uithaistaticQU.checkBox_S1_DC4.isChecked():
            checkBox_S1_DC4 = '1'
        else:
            checkBox_S1_DC4 = '0'
        arrayRow2.append(checkBox_S1_DC4)

        comboBox_S1_DC4 = uithaistaticQU.comboBox_S1_DC4.currentIndex()
        arrayRow2.append(comboBox_S1_DC4)

        textEdit_S1_DC4_VOLT = uithaistaticQU.textEdit_S1_DC4_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_VOLT)

        textEdit_S1_DC4_CURR = uithaistaticQU.textEdit_S1_DC4_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_CURR)

        textEdit_S1_DC4_Voc = uithaistaticQU.textEdit_S1_DC4_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Voc)
        
        textEdit_S1_DC4_Isc = uithaistaticQU.textEdit_S1_DC4_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Isc)
        
        textEdit_S1_DC4_PF = uithaistaticQU.textEdit_S1_DC4_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_PF)

        textEdit_S1_ACWaitTIME = uithaistaticQU.textEdit_S1_ACWaitTIME.toPlainText()
        arrayRow2.append(textEdit_S1_ACWaitTIME)

        comboBox_S1_ACWaitTIME = uithaistaticQU.comboBox_S1_ACWaitTIME.currentIndex()
        arrayRow2.append(comboBox_S1_ACWaitTIME)

        textEdit_S1_TIME = uithaistaticQU.textEdit_S1_TIME.toPlainText()
        arrayRow2.append(textEdit_S1_TIME)

        comboBox_S1_TIME = uithaistaticQU.comboBox_S1_TIME.currentIndex()
        arrayRow2.append(comboBox_S1_TIME)
        
        # step2
        if uithaistaticQU.checkBox_S2.isChecked():
            checkBox_S2 = '1'
        else:
            checkBox_S2 = '0'
        arrayRow2.append(checkBox_S2)

        if uithaistaticQU.checkBox_S2_WT3000.isChecked():
            checkBox_S2_WT3000 = '1'
        else:
            checkBox_S2_WT3000 = '0'
        arrayRow2.append(checkBox_S2_WT3000)

        if uithaistaticQU.checkBox_S2_WT1800.isChecked():
            checkBox_S2_WT1800 = '1'
        else:
            checkBox_S2_WT1800 = '0'
        arrayRow2.append(checkBox_S2_WT1800)

        # step3
        if uithaistaticQU.checkBox_S3.isChecked():
            checkBox_S3 = '1'
        else:
            checkBox_S3 = '0'
        arrayRow2.append(checkBox_S3)

        textEdit_S3_AC_VOLT = uithaistaticQU.textEdit_S3_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT)

        comboBox_S3_AC_Trend = uithaistaticQU.comboBox_S3_AC_Trend.currentIndex()
        arrayRow2.append(comboBox_S3_AC_Trend)

        textEdit_S3_AC_Range_S = uithaistaticQU.textEdit_S3_AC_Range_S.toPlainText()
        arrayRow2.append(textEdit_S3_AC_Range_S)

        textEdit_S3_AC_Range_E = uithaistaticQU.textEdit_S3_AC_Range_E.toPlainText()
        arrayRow2.append(textEdit_S3_AC_Range_E)

        textEdit_S3_AC_Range_Point = uithaistaticQU.textEdit_S3_AC_Range_Point.toPlainText()
        arrayRow2.append(textEdit_S3_AC_Range_Point)

        textEdit_S3_AC_Step = uithaistaticQU.textEdit_S3_AC_Step.toPlainText()
        arrayRow2.append(textEdit_S3_AC_Step)

        textEdit_S3_AC_FR = uithaistaticQU.textEdit_S3_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S3_AC_FR)

        textEdit_S3_TIME = uithaistaticQU.textEdit_S3_TIME.toPlainText()
        arrayRow2.append(textEdit_S3_TIME)

        comboBox_S3_TIME = uithaistaticQU.comboBox_S3_TIME.currentIndex()
        arrayRow2.append(comboBox_S3_TIME)

        # step4
        if uithaistaticQU.checkBox_S4.isChecked():
            checkBox_S4 = '1'
        else:
            checkBox_S4 = '0'
        arrayRow2.append(checkBox_S4)

        textEdit_S4_AC_VOLT = uithaistaticQU.textEdit_S4_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S4_AC_VOLT)

        comboBox_S4_AC_Trend = uithaistaticQU.comboBox_S4_AC_Trend.currentIndex()
        arrayRow2.append(comboBox_S4_AC_Trend)

        textEdit_S4_AC_Range_S = uithaistaticQU.textEdit_S4_AC_Range_S.toPlainText()
        arrayRow2.append(textEdit_S4_AC_Range_S)

        textEdit_S4_AC_Range_E = uithaistaticQU.textEdit_S4_AC_Range_E.toPlainText()
        arrayRow2.append(textEdit_S4_AC_Range_E)

        textEdit_S4_AC_Range_Point = uithaistaticQU.textEdit_S4_AC_Range_Point.toPlainText()
        arrayRow2.append(textEdit_S4_AC_Range_Point)

        textEdit_S3_AC_Step = uithaistaticQU.textEdit_S3_AC_Step.toPlainText()
        arrayRow2.append(textEdit_S3_AC_Step)
        
        textEdit_S4_AC_FR = uithaistaticQU.textEdit_S4_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S4_AC_FR)

        textEdit_S4_TIME = uithaistaticQU.textEdit_S4_TIME.toPlainText()
        arrayRow2.append(textEdit_S4_TIME)

        comboBox_S4_TIME = uithaistaticQU.comboBox_S4_TIME.currentIndex()
        arrayRow2.append(comboBox_S4_TIME)

        # step5
        if uithaistaticQU.checkBox_S5.isChecked():
            checkBox_S5 = '1'
        else:
            checkBox_S5 = '0'
        arrayRow2.append(checkBox_S5)

        textEdit_S5_AC_VOLT = uithaistaticQU.textEdit_S5_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S5_AC_VOLT)

        comboBox_S5_AC_Trend = uithaistaticQU.comboBox_S5_AC_Trend.currentIndex()
        arrayRow2.append(comboBox_S5_AC_Trend)

        textEdit_S5_AC_Range_S = uithaistaticQU.textEdit_S5_AC_Range_S.toPlainText()
        arrayRow2.append(textEdit_S5_AC_Range_S)

        textEdit_S5_AC_Range_E = uithaistaticQU.textEdit_S5_AC_Range_E.toPlainText()
        arrayRow2.append(textEdit_S5_AC_Range_E)

        textEdit_S5_AC_Range_Point = uithaistaticQU.textEdit_S5_AC_Range_Point.toPlainText()
        arrayRow2.append(textEdit_S5_AC_Range_Point)

        textEdit_S5_AC_Step = uithaistaticQU.textEdit_S5_AC_Step.toPlainText()
        arrayRow2.append(textEdit_S5_AC_Step)

        textEdit_S5_AC_FR = uithaistaticQU.textEdit_S5_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S5_AC_FR)

        textEdit_S5_TIME = uithaistaticQU.textEdit_S5_TIME.toPlainText()
        arrayRow2.append(textEdit_S5_TIME)

        comboBox_S5_TIME = uithaistaticQU.comboBox_S5_TIME.currentIndex()
        arrayRow2.append(comboBox_S5_TIME)

        # step6
        if uithaistaticQU.checkBox_S6.isChecked():
            checkBox_S6 = '1'
        else:
            checkBox_S6 = '0'
        arrayRow2.append(checkBox_S6)

        textEdit_S6_AC_VOLT = uithaistaticQU.textEdit_S6_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S6_AC_VOLT)

        comboBox_S6_AC_Trend = uithaistaticQU.comboBox_S6_AC_Trend.currentIndex()
        arrayRow2.append(comboBox_S6_AC_Trend)

        textEdit_S6_AC_Range_S = uithaistaticQU.textEdit_S6_AC_Range_S.toPlainText()
        arrayRow2.append(textEdit_S6_AC_Range_S)

        textEdit_S6_AC_Range_E = uithaistaticQU.textEdit_S6_AC_Range_E.toPlainText()
        arrayRow2.append(textEdit_S6_AC_Range_E)

        textEdit_S6_AC_Range_Point = uithaistaticQU.textEdit_S6_AC_Range_Point.toPlainText()
        arrayRow2.append(textEdit_S6_AC_Range_Point)

        textEdit_S6_AC_Step = uithaistaticQU.textEdit_S6_AC_Step.toPlainText()
        arrayRow2.append(textEdit_S6_AC_Step)

        textEdit_S6_AC_FR = uithaistaticQU.textEdit_S6_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S6_AC_FR)

        textEdit_S6_TIME = uithaistaticQU.textEdit_S6_TIME.toPlainText()
        arrayRow2.append(textEdit_S6_TIME)

        comboBox_S6_TIME = uithaistaticQU.comboBox_S6_TIME.currentIndex()
        arrayRow2.append(comboBox_S6_TIME)

        # step7
        if uithaistaticQU.checkBox_S_End.isChecked():
            checkBox_S_End = '1'
        else:
            checkBox_S_End = '0'
        arrayRow2.append(checkBox_S_End)

        comboBox_S_End_AC = uithaistaticQU.comboBox_S_End_AC.currentIndex()
        arrayRow2.append(comboBox_S_End_AC)

        if uithaistaticQU.checkBox_S_End_DC1.isChecked():
            checkBox_S_End_DC1 = '1'
        else:
            checkBox_S_End_DC1 = '0'
        arrayRow2.append(checkBox_S_End_DC1)

        comboBox_S_End_DC1 = uithaistaticQU.comboBox_S_End_DC1.currentIndex()
        arrayRow2.append(comboBox_S_End_DC1)

        if uithaistaticQU.checkBox_S_End_DC2.isChecked():
            checkBox_S_End_DC2 = '1'
        else:
            checkBox_S_End_DC2 = '0'
        arrayRow2.append(checkBox_S_End_DC2)

        comboBox_S_End_DC2 = uithaistaticQU.comboBox_S_End_DC2.currentIndex()
        arrayRow2.append(comboBox_S_End_DC2)

        if uithaistaticQU.checkBox_S_End_DC3.isChecked():
            checkBox_S_End_DC3 = '1'
        else:
            checkBox_S_End_DC3 = '0'
        arrayRow2.append(checkBox_S_End_DC3)

        comboBox_S_End_DC3 = uithaistaticQU.comboBox_S_End_DC3.currentIndex()
        arrayRow2.append(comboBox_S_End_DC3)

        if uithaistaticQU.checkBox_S_End_DC4.isChecked():
            checkBox_S_End_DC4 = '1'
        else:
            checkBox_S_End_DC4 = '0'
        arrayRow2.append(checkBox_S_End_DC4)

        comboBox_S_End_DC4 = uithaistaticQU.comboBox_S_End_DC4.currentIndex()
        arrayRow2.append(comboBox_S_End_DC4)

        if uithaistaticQU.checkBox_S2_WT1806E.isChecked():
            checkBox_S2_WT1806E = '1'
        else:
            checkBox_S2_WT1806E = '0'
        arrayRow2.append(checkBox_S2_WT1806E)

        if uithaistaticQU.checkBox_S2_WT5000.isChecked():
            checkBox_S2_WT5000 = '1'
        else:
            checkBox_S2_WT5000 = '0'
        arrayRow2.append(checkBox_S2_WT5000)

        if uithaistaticQU.checkBox_S2_WT3000.isChecked():
            result = Save_File_ThaiWT3000_Config(uiThiaWT3000E)

        if uithaistaticQU.checkBox_S2_WT1800.isChecked():
            result = Save_File_ThaiWT1800_Config(uiThiaWT1800)

        if uithaistaticQU.checkBox_S2_WT1806E.isChecked():
            result = Save_File_ThaiWT1806E_Config(uiThiaWT1806E)

        if uithaistaticQU.checkBox_S2_WT5000.isChecked():
            result = Save_File_ThaiWT5000_Config(uiThiaWT5000)

        out = open(directory1[0], 'w+', newline='')
        csv_write = csv.writer(out, dialect="excel")
        csv_write.writerow(arrayRow1)
        csv_write.writerow(arrayRow2)
        if len(result) > 0:
            csv_write.writerow(result[0])
            csv_write.writerow(result[1])
        out.close()
        QMessageBox.information(dialog_window, "实验设定提示信息", "静态Q(U)文件保存完成", QMessageBox.Ok, QMessageBox.Ok)

# 静态QU读取设定
def Open_File_ThaiStaticQU(kwargs):
    dialog_window = kwargs['dialog_windowstaticQU']
    uithaistaticQU = kwargs['uiThaiStaticQU']
    uiThiaWT3000E = kwargs['uiThiaWT3000E']
    uiThiaWT1800 = kwargs['uiThiaWT1800']
    uiThiaWT1806E = kwargs['uiThiaWT1806E']
    uiThiaWT5000 = kwargs['uiThiaWT5000']
    strFlag  = "0"
    result_list = []
    config_dict = {}
    wt_config_dict = {}
    directory1 = QFileDialog.getOpenFileName(dialog_window,"单个文件选择","./","Text Files(*.csv)")
    if directory1[0] == '':
        print("请选择一个文件")
    else:
        with open(directory1[0], 'r') as f:
            data = csv.reader(f)
            for line in data:
                result_list.append(list(line))
        
        if len(result_list) == 2:
            delta_len = int(len(result_list[0]) - len(result_list[1]))
            if delta_len > 0:
                extend_list = ['' for k in range(delta_len)]
                result_list[1].extend(extend_list)
            config_dict = zip(result_list[0],result_list[1])
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
                if config_dict[arrayRow1[0]] == "ThaiStaticQU":
                    #checkBox
                    if strFlag == "0":
                        if arrayRow1[1] in config_dict:
                            checkBox_S1 = config_dict[arrayRow1[1]]
                            if checkBox_S1 == '1':
                                uithaistaticQU.checkBox_S1.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S1.setChecked(False)
                        else:
                            strFlag = 1

                    #comBox
                    if strFlag == "0":
                        if arrayRow1[2] in config_dict:
                            comboBox_S1_AC = config_dict[arrayRow1[2]]
                            uithaistaticQU.comboBox_S1_AC.setCurrentIndex(int(comboBox_S1_AC))
                        else:
                            strFlag = 1

                    #textEdit
                    if strFlag == "0":
                        if arrayRow1[3] in config_dict:
                            textEdit_S1_AC_VOLT = config_dict[arrayRow1[3]]
                            uithaistaticQU.textEdit_S1_AC_VOLT.setText(textEdit_S1_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[4] in config_dict:
                            textEdit_S1_AC_VOLT_2 = config_dict[arrayRow1[4]]
                            uithaistaticQU.textEdit_S1_AC_VOLT_2.setText(textEdit_S1_AC_VOLT_2)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[5] in config_dict:
                            textEdit_S1_AC_VOLT_3 = config_dict[arrayRow1[5]]
                            uithaistaticQU.textEdit_S1_AC_VOLT_3.setText(textEdit_S1_AC_VOLT_3)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[6] in config_dict:
                            textEdit_S1_AC_FR = config_dict[arrayRow1[6]]
                            uithaistaticQU.textEdit_S1_AC_FR.setText(textEdit_S1_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[7] in config_dict:
                            comboBox_S1_AC_2 = config_dict[arrayRow1[7]]
                            uithaistaticQU.comboBox_S1_AC_2.setCurrentIndex(int(comboBox_S1_AC_2))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[8] in config_dict:
                            checkBox_S1_DC1 = config_dict[arrayRow1[8]]
                            if checkBox_S1_DC1 == '1':
                                uithaistaticQU.checkBox_S1_DC1.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S1_DC1.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[9] in config_dict:
                            comboBox_S1_DC1 = config_dict[arrayRow1[9]]
                            uithaistaticQU.comboBox_S1_DC1.setCurrentIndex(int(comboBox_S1_DC1))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[10] in config_dict:
                            textEdit_S1_DC1_VOLT = config_dict[arrayRow1[10]]
                            uithaistaticQU.textEdit_S1_DC1_VOLT.setText(textEdit_S1_DC1_VOLT)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[11] in config_dict:
                            textEdit_S1_DC1_CURR = config_dict[arrayRow1[11]]
                            uithaistaticQU.textEdit_S1_DC1_CURR.setText(textEdit_S1_DC1_CURR)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[12] in config_dict:
                            textEdit_S1_DC1_Voc = config_dict[arrayRow1[12]]
                            uithaistaticQU.textEdit_S1_DC1_Voc.setText(textEdit_S1_DC1_Voc)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[13] in config_dict:
                            textEdit_S1_DC1_Isc = config_dict[arrayRow1[13]]
                            uithaistaticQU.textEdit_S1_DC1_Isc.setText(textEdit_S1_DC1_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[14] in config_dict:
                            textEdit_S1_DC1_PF = config_dict[arrayRow1[14]]
                            uithaistaticQU.textEdit_S1_DC1_PF.setText(textEdit_S1_DC1_PF)
                        else:
                            strFlag = 1
                            
                    if strFlag == "0":
                        if arrayRow1[15] in config_dict:
                            checkBox_S1_DC2 = config_dict[arrayRow1[15]]
                            if checkBox_S1_DC2 == '1':
                                uithaistaticQU.checkBox_S1_DC2.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S1_DC2.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[16] in config_dict:
                            comboBox_S1_DC2 = config_dict[arrayRow1[16]]
                            uithaistaticQU.comboBox_S1_DC2.setCurrentIndex(int(comboBox_S1_DC2))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[17] in config_dict:
                            textEdit_S1_DC2_VOLT = config_dict[arrayRow1[17]]
                            uithaistaticQU.textEdit_S1_DC2_VOLT.setText(textEdit_S1_DC2_VOLT)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[18] in config_dict:
                            textEdit_S1_DC2_CURR = config_dict[arrayRow1[18]]
                            uithaistaticQU.textEdit_S1_DC2_CURR.setText(textEdit_S1_DC2_CURR)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[19] in config_dict:
                            textEdit_S1_DC2_Voc = config_dict[arrayRow1[19]]
                            uithaistaticQU.textEdit_S1_DC2_Voc.setText(textEdit_S1_DC2_Voc)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[20] in config_dict:
                            textEdit_S1_DC2_Isc = config_dict[arrayRow1[20]]
                            uithaistaticQU.textEdit_S1_DC2_Isc.setText(textEdit_S1_DC2_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[21] in config_dict:
                            textEdit_S1_DC2_PF = config_dict[arrayRow1[21]]
                            uithaistaticQU.textEdit_S1_DC2_PF.setText(textEdit_S1_DC2_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[22] in config_dict:
                            checkBox_S1_DC3 = config_dict[arrayRow1[22]]
                            if checkBox_S1_DC3 == '1':
                                uithaistaticQU.checkBox_S1_DC3.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S1_DC3.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[23] in config_dict:
                            comboBox_S1_DC3 = config_dict[arrayRow1[23]]
                            uithaistaticQU.comboBox_S1_DC3.setCurrentIndex(int(comboBox_S1_DC3))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[24] in config_dict:
                            textEdit_S1_DC3_VOLT = config_dict[arrayRow1[24]]
                            uithaistaticQU.textEdit_S1_DC3_VOLT.setText(textEdit_S1_DC3_VOLT)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[25] in config_dict:
                            textEdit_S1_DC3_CURR = config_dict[arrayRow1[25]]
                            uithaistaticQU.textEdit_S1_DC3_CURR.setText(textEdit_S1_DC3_CURR)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[26] in config_dict:
                            textEdit_S1_DC3_Voc = config_dict[arrayRow1[26]]
                            uithaistaticQU.textEdit_S1_DC3_Voc.setText(textEdit_S1_DC3_Voc)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[27] in config_dict:
                            textEdit_S1_DC3_Isc = config_dict[arrayRow1[27]]
                            uithaistaticQU.textEdit_S1_DC3_Isc.setText(textEdit_S1_DC3_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[28] in config_dict:
                            textEdit_S1_DC3_PF = config_dict[arrayRow1[28]]
                            uithaistaticQU.textEdit_S1_DC3_PF.setText(textEdit_S1_DC3_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[29] in config_dict:
                            checkBox_S1_DC4 = config_dict[arrayRow1[29]]
                            if checkBox_S1_DC4 == '1':
                                uithaistaticQU.checkBox_S1_DC4.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S1_DC4.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[30] in config_dict:
                            comboBox_S1_DC4 = config_dict[arrayRow1[30]]
                            uithaistaticQU.comboBox_S1_DC4.setCurrentIndex(int(comboBox_S1_DC4))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[31] in config_dict:
                            textEdit_S1_DC4_VOLT = config_dict[arrayRow1[31]]
                            uithaistaticQU.textEdit_S1_DC4_VOLT.setText(textEdit_S1_DC4_VOLT)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[32] in config_dict:
                            textEdit_S1_DC4_CURR = config_dict[arrayRow1[32]]
                            uithaistaticQU.textEdit_S1_DC4_CURR.setText(textEdit_S1_DC4_CURR)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[33] in config_dict:
                            textEdit_S1_DC4_Voc = config_dict[arrayRow1[33]]
                            uithaistaticQU.textEdit_S1_DC4_Voc.setText(textEdit_S1_DC4_Voc)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[34] in config_dict:
                            textEdit_S1_DC4_Isc = config_dict[arrayRow1[34]]
                            uithaistaticQU.textEdit_S1_DC4_Isc.setText(textEdit_S1_DC4_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[35] in config_dict:
                            textEdit_S1_DC4_PF = config_dict[arrayRow1[35]]
                            uithaistaticQU.textEdit_S1_DC4_PF.setText(textEdit_S1_DC4_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[36] in config_dict:
                            textEdit_S1_ACWaitTIME = config_dict[arrayRow1[36]]
                            uithaistaticQU.textEdit_S1_ACWaitTIME.setText(textEdit_S1_ACWaitTIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[37] in config_dict:
                            comboBox_S1_ACWaitTIME = config_dict[arrayRow1[37]]
                            uithaistaticQU.comboBox_S1_ACWaitTIME.setCurrentIndex(int(comboBox_S1_ACWaitTIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[38] in config_dict:
                            textEdit_S1_TIME = config_dict[arrayRow1[38]]
                            uithaistaticQU.textEdit_S1_TIME.setText(textEdit_S1_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[39] in config_dict:
                            comboBox_S1_TIME = config_dict[arrayRow1[39]]
                            uithaistaticQU.comboBox_S1_TIME.setCurrentIndex(int(comboBox_S1_TIME))
                        else:
                            strFlag = 1
                    # step2
                    if strFlag == "0":
                        if arrayRow1[40] in config_dict:
                            checkBox_S2 = config_dict[arrayRow1[40]]
                            if checkBox_S2 == '1':
                                uithaistaticQU.checkBox_S2.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[41] in config_dict:
                            checkBox_S2_WT3000 = config_dict[arrayRow1[41]]
                            if checkBox_S2_WT3000 == '1':
                                uithaistaticQU.checkBox_S2_WT3000.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S2_WT3000.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[42] in config_dict:
                            checkBox_S2_WT1800 = config_dict[arrayRow1[42]]
                            if checkBox_S2_WT1800 == '1':
                                uithaistaticQU.checkBox_S2_WT1800.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S2_WT1800.setChecked(False)
                        else:
                            strFlag = 1
                    # step3
                    if strFlag == "0":
                        if arrayRow1[43] in config_dict:
                            checkBox_S3 = config_dict[arrayRow1[43]]
                            if checkBox_S3 == '1':
                                uithaistaticQU.checkBox_S3.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[44] in config_dict:
                            textEdit_S3_AC_VOLT = config_dict[arrayRow1[44]]
                            uithaistaticQU.textEdit_S3_AC_VOLT.setText(textEdit_S3_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[45] in config_dict:
                            comboBox_S3_AC_Trend = config_dict[arrayRow1[45]]
                            uithaistaticQU.comboBox_S3_AC_Trend.setCurrentIndex(int(comboBox_S3_AC_Trend))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[46] in config_dict:
                            textEdit_S3_AC_Range_S = config_dict[arrayRow1[46]]
                            uithaistaticQU.textEdit_S3_AC_Range_S.setText(textEdit_S3_AC_Range_S)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[47] in config_dict:
                            textEdit_S3_AC_Range_E = config_dict[arrayRow1[47]]
                            uithaistaticQU.textEdit_S3_AC_Range_E.setText(textEdit_S3_AC_Range_E)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[48] in config_dict:
                            textEdit_S3_AC_Range_Point = config_dict[arrayRow1[48]]
                            uithaistaticQU.textEdit_S3_AC_Range_Point.setText(textEdit_S3_AC_Range_Point)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[49] in config_dict:
                            textEdit_S3_AC_Step = config_dict[arrayRow1[49]]
                            uithaistaticQU.textEdit_S3_AC_Step.setText(textEdit_S3_AC_Step)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[50] in config_dict:
                            textEdit_S3_AC_FR = config_dict[arrayRow1[50]]
                            uithaistaticQU.textEdit_S3_AC_FR.setText(textEdit_S3_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[51] in config_dict:
                            textEdit_S3_TIME = config_dict[arrayRow1[51]]
                            uithaistaticQU.textEdit_S3_TIME.setText(textEdit_S3_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[52] in config_dict:
                            comboBox_S3_TIME = config_dict[arrayRow1[52]]
                            uithaistaticQU.comboBox_S3_TIME.setCurrentIndex(int(comboBox_S3_TIME))
                        else:
                            strFlag = 1
                    # step4   
                    if strFlag == "0":
                        if arrayRow1[53] in config_dict:
                            checkBox_S4 = config_dict[arrayRow1[53]]
                            if checkBox_S4 == '1':
                                uithaistaticQU.checkBox_S4.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[54] in config_dict:
                            textEdit_S4_AC_VOLT = config_dict[arrayRow1[54]]
                            uithaistaticQU.textEdit_S4_AC_VOLT.setText(textEdit_S4_AC_VOLT)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[55] in config_dict:
                            comboBox_S4_AC_Trend = config_dict[arrayRow1[55]]
                            uithaistaticQU.comboBox_S4_AC_Trend.setCurrentIndex(int(comboBox_S4_AC_Trend))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[56] in config_dict:
                            textEdit_S4_AC_Range_S = config_dict[arrayRow1[56]]
                            uithaistaticQU.textEdit_S4_AC_Range_S.setText(textEdit_S4_AC_Range_S)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[57] in config_dict:
                            textEdit_S4_AC_Range_E = config_dict[arrayRow1[57]]
                            uithaistaticQU.textEdit_S4_AC_Range_E.setText(textEdit_S4_AC_Range_E)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[58] in config_dict:
                            textEdit_S4_AC_Range_Point = config_dict[arrayRow1[58]]
                            uithaistaticQU.textEdit_S4_AC_Range_Point.setText(textEdit_S4_AC_Range_Point)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[59] in config_dict:
                            textEdit_S4_AC_Step = config_dict[arrayRow1[59]]
                            uithaistaticQU.textEdit_S4_AC_Step.setText(textEdit_S4_AC_Step)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[60] in config_dict:
                            textEdit_S4_AC_FR = config_dict[arrayRow1[60]]
                            uithaistaticQU.textEdit_S4_AC_FR.setText(textEdit_S4_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[61] in config_dict:
                            textEdit_S4_TIME = config_dict[arrayRow1[61]]
                            uithaistaticQU.textEdit_S4_TIME.setText(textEdit_S4_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[62] in config_dict:
                            comboBox_S4_TIME = config_dict[arrayRow1[62]]
                            uithaistaticQU.comboBox_S4_TIME.setCurrentIndex(int(comboBox_S4_TIME))
                        else:
                            strFlag = 1
                    # step5
                    if strFlag == "0":
                        if arrayRow1[63] in config_dict:
                            checkBox_S5 = config_dict[arrayRow1[63]]
                            if checkBox_S5 == '1':
                                uithaistaticQU.checkBox_S5.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S5.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[64] in config_dict:
                            textEdit_S5_AC_VOLT = config_dict[arrayRow1[64]]
                            uithaistaticQU.textEdit_S5_AC_VOLT.setText(textEdit_S5_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[65] in config_dict:
                            comboBox_S5_AC_Trend = config_dict[arrayRow1[65]]
                            uithaistaticQU.comboBox_S5_AC_Trend.setCurrentIndex(int(comboBox_S5_AC_Trend))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[66] in config_dict:
                            textEdit_S5_AC_Range_S = config_dict[arrayRow1[66]]
                            uithaistaticQU.textEdit_S5_AC_Range_S.setText(textEdit_S5_AC_Range_S)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[67] in config_dict:
                            textEdit_S5_AC_Range_E = config_dict[arrayRow1[67]]
                            uithaistaticQU.textEdit_S5_AC_Range_E.setText(textEdit_S5_AC_Range_E)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[68] in config_dict:
                            textEdit_S5_AC_Range_Point = config_dict[arrayRow1[68]]
                            uithaistaticQU.textEdit_S5_AC_Range_Point.setText(textEdit_S5_AC_Range_Point)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[69] in config_dict:
                            textEdit_S5_AC_Step = config_dict[arrayRow1[69]]
                            uithaistaticQU.textEdit_S5_AC_Step.setText(textEdit_S5_AC_Step)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[70] in config_dict:
                            textEdit_S5_AC_FR = config_dict[arrayRow1[70]]
                            uithaistaticQU.textEdit_S5_AC_FR.setText(textEdit_S5_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[71] in config_dict:
                            textEdit_S5_TIME = config_dict[arrayRow1[71]]
                            uithaistaticQU.textEdit_S5_TIME.setText(textEdit_S5_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[72] in config_dict:
                            comboBox_S5_TIME = config_dict[arrayRow1[72]]
                            uithaistaticQU.comboBox_S5_TIME.setCurrentIndex(int(comboBox_S5_TIME))
                        else:
                            strFlag = 1
                    # step6
                    if strFlag == "0":
                        if arrayRow1[73] in config_dict:
                            checkBox_S6 = config_dict[arrayRow1[73]]
                            if checkBox_S6 == '1':
                                uithaistaticQU.checkBox_S6.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S6.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[74] in config_dict:
                            textEdit_S6_AC_VOLT = config_dict[arrayRow1[74]]
                            uithaistaticQU.textEdit_S6_AC_VOLT.setText(textEdit_S6_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[75] in config_dict:
                            comboBox_S6_AC_Trend = config_dict[arrayRow1[75]]
                            uithaistaticQU.comboBox_S6_AC_Trend.setCurrentIndex(int(comboBox_S6_AC_Trend))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[76] in config_dict:
                            textEdit_S6_AC_Range_S = config_dict[arrayRow1[76]]
                            uithaistaticQU.textEdit_S6_AC_Range_S.setText(textEdit_S6_AC_Range_S)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[77] in config_dict:
                            textEdit_S6_AC_Range_E = config_dict[arrayRow1[77]]
                            uithaistaticQU.textEdit_S6_AC_Range_E.setText(textEdit_S6_AC_Range_E)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[78] in config_dict:
                            textEdit_S6_AC_Range_Point = config_dict[arrayRow1[78]]
                            uithaistaticQU.textEdit_S6_AC_Range_Point.setText(textEdit_S6_AC_Range_Point)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[79] in config_dict:
                            textEdit_S6_AC_Step = config_dict[arrayRow1[79]]
                            uithaistaticQU.textEdit_S6_AC_Step.setText(textEdit_S6_AC_Step)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[80] in config_dict:
                            textEdit_S6_AC_FR = config_dict[arrayRow1[80]]
                            uithaistaticQU.textEdit_S6_AC_FR.setText(textEdit_S6_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[81] in config_dict:
                            textEdit_S6_TIME = config_dict[arrayRow1[81]]
                            uithaistaticQU.textEdit_S6_TIME.setText(textEdit_S6_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[82] in config_dict:
                            comboBox_S6_TIME = config_dict[arrayRow1[82]]
                            uithaistaticQU.comboBox_S6_TIME.setCurrentIndex(int(comboBox_S6_TIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[83] in config_dict:
                            checkBox_S_End = config_dict[arrayRow1[83]]
                            if checkBox_S_End == '1':
                                uithaistaticQU.checkBox_S_End.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S_End.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[84] in config_dict:
                            comboBox_S_End_AC = config_dict[arrayRow1[84]]
                            uithaistaticQU.comboBox_S_End_AC.setCurrentIndex(int(comboBox_S_End_AC))

                    if strFlag == "0":
                        if arrayRow1[85] in config_dict:
                            checkBox_S_End_DC1 = config_dict[arrayRow1[85]]
                            if checkBox_S_End_DC1 == '1':
                                uithaistaticQU.checkBox_S_End_DC1.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S_End_DC1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[86] in config_dict:
                            comboBox_S_End_DC1 = config_dict[arrayRow1[86]]
                            uithaistaticQU.comboBox_S_End_DC1.setCurrentIndex(int(comboBox_S_End_DC1))

                    if strFlag == "0":
                        if arrayRow1[87] in config_dict:
                            checkBox_S_End_DC2 = config_dict[arrayRow1[87]]
                            if checkBox_S_End_DC2 == '1':
                                uithaistaticQU.checkBox_S_End_DC2.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S_End_DC2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[88] in config_dict:
                            comboBox_S_End_DC2 = config_dict[arrayRow1[88]]
                            uithaistaticQU.comboBox_S_End_DC2.setCurrentIndex(int(comboBox_S_End_DC2))

                    if strFlag == "0":
                        if arrayRow1[89] in config_dict:
                            checkBox_S_End_DC3 = config_dict[arrayRow1[89]]
                            if checkBox_S_End_DC3 == '1':
                                uithaistaticQU.checkBox_S_End_DC3.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S_End_DC3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[90] in config_dict:
                            comboBox_S_End_DC3 = config_dict[arrayRow1[90]]
                            uithaistaticQU.comboBox_S_End_DC3.setCurrentIndex(int(comboBox_S_End_DC3))

                    if strFlag == "0":
                        if arrayRow1[91] in config_dict:
                            checkBox_S_End_DC4 = config_dict[arrayRow1[91]]
                            if checkBox_S_End_DC4 == '1':
                                uithaistaticQU.checkBox_S_End_DC4.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S_End_DC4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[92] in config_dict:
                            comboBox_S_End_DC4 = config_dict[arrayRow1[92]]
                            uithaistaticQU.comboBox_S_End_DC4.setCurrentIndex(int(comboBox_S_End_DC4))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[93] in config_dict:
                            checkBox_S2_WT1806E = config_dict[arrayRow1[93]]
                            if checkBox_S2_WT1806E == '1':
                                uithaistaticQU.checkBox_S2_WT1806E.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S2_WT1806E.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[94] in config_dict:
                            checkBox_S2_WT5000 = config_dict[arrayRow1[94]]
                            if checkBox_S2_WT5000 == '1':
                                uithaistaticQU.checkBox_S2_WT5000.setChecked(True)
                            else:
                                uithaistaticQU.checkBox_S2_WT5000.setChecked(False)
                        else:
                            strFlag = 1

                    if arrayRow1[41] in config_dict:
                        checkBox_S2_WT3000 = config_dict[arrayRow1[41]]
                        if checkBox_S2_WT3000 == '1':
                            Open_File_ThaiWT3000_Config(uiThiaWT3000E, wt_config_dict)
                        
                    else:
                        strFlag = 1

                    if arrayRow1[42] in config_dict:
                        checkBox_S2_WT1800 = config_dict[arrayRow1[42]]
                        if checkBox_S2_WT1800 == '1':
                            Open_File_ThaiWT1800_Config(uiThiaWT1800, wt_config_dict)
                    else:
                        strFlag = 1

                    if arrayRow1[93] in config_dict:
                        checkBox_S2_WT1806E = config_dict[arrayRow1[93]]
                        if checkBox_S2_WT1806E == '1':
                            Open_File_ThaiWT1806E_Config(uiThiaWT1806E, wt_config_dict)
                    else:
                        strFlag = 1

                    if arrayRow1[94] in config_dict:
                        checkBox_S2_WT5000 = config_dict[arrayRow1[94]]
                        if checkBox_S2_WT5000 == '1':
                            Open_File_ThaiWT5000_Config(uiThiaWT5000, wt_config_dict)
                    else:
                        strFlag = 1

                else:
                    print("no")
                    strFlag = "1"

        QMessageBox.information(dialog_window, "实验设定提示信息", "静态Q(U)文件读取完成", QMessageBox.Ok, QMessageBox.Ok)

# def save_file_header():
#     directory1 = [r"D:\\project\\photovoltaic_automation_t\\config_files\\project_step_configs\\staticQU.csv"]
#     if directory1[0] == '':
#         print('请选择一个文件')
#     else:
#         out = open(directory1[0], 'w+', newline='')
#         csv_write = csv.writer(out, dialect="excel")
#         csv_write.writerow(arrayRow1)
#         out.close()

# if __name__ == "__main__":
#     save_file_header()