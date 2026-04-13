from PyQt5.QtWidgets import QMainWindow,QApplication,QDialog,QFileDialog, QMessageBox
import csv
from utils.Open_Save_ThaiWT3000_Config import Save_File_ThaiWT3000_Config, Open_File_ThaiWT3000_Config
from utils.Open_Save_ThaiWT1800_Config import Save_File_ThaiWT1800_Config, Open_File_ThaiWT1800_Config
from utils.Open_Save_ThaiWT1806E_Config import Save_File_ThaiWT1806E_Config, Open_File_ThaiWT1806E_Config
from utils.Open_Save_ThaiWT5000_Config import Save_File_ThaiWT5000_Config, Open_File_ThaiWT5000_Config

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
                "checkBox_S3", "checkBox_S1_DC1_2", "checkBox_S1_DC2_2", "checkBox_S1_DC3_2",
                    "checkBox_S1_DC4_2", "textEdit_S1_DC1_PF_2",
                "checkBox_S3_2", "checkBox_S1_DC1_3", "checkBox_S1_DC2_3", "checkBox_S1_DC3_3",
                    "checkBox_S1_DC4_3", "textEdit_S1_DC1_PF_3",
                "checkBox_S3_3", "checkBox_S1_DC1_4", "checkBox_S1_DC2_4", "checkBox_S1_DC3_4",
                    "checkBox_S1_DC4_4", "textEdit_S1_DC1_PF_4",
                "checkBox_S3_4", "checkBox_S1_DC1_5", "checkBox_S1_DC2_5", "checkBox_S1_DC3_5",
                    "checkBox_S1_DC4_5", "textEdit_S1_DC1_PF_5", 
                "checkBox_S3_5", "checkBox_S1_DC1_6", "checkBox_S1_DC2_6", "checkBox_S1_DC3_6",
                    "checkBox_S1_DC4_6", "textEdit_S1_DC1_PF_6",
                "checkBox_S3_10", "checkBox_S1_DC1_10", "checkBox_S1_DC2_11", "checkBox_S1_DC3_10",
                    "checkBox_S1_DC4_7", "textEdit_S1_DC1_PF_10",
                "checkBox_S3_6", "checkBox_S1_DC1_11", "checkBox_S1_DC2_8", "checkBox_S1_DC3_11",
                    "checkBox_S1_DC3_15", "textEdit_S1_DC1_PF_9",
                "checkBox_S3_7", "checkBox_S1_DC1_7", "checkBox_S1_DC2_9", "checkBox_S1_DC3_8",
                    "checkBox_S1_DC3_14", "textEdit_S1_DC1_PF_7",
                "checkBox_S3_9", "checkBox_S1_DC1_9", "checkBox_S1_DC2_10", "checkBox_S1_DC3_9",
                    "checkBox_S1_DC3_16", "textEdit_S1_DC1_PF_11",
                "checkBox_S3_8", "checkBox_S1_DC1_8", "checkBox_S1_DC2_7", "checkBox_S1_DC3_7",
                    "checkBox_S1_DC3_17", "textEdit_S1_DC1_PF_8",
                "checkBox_S3_11", "checkBox_S1_DC1_12", "checkBox_S1_DC2_12", "checkBox_S1_DC3_12",
                    "checkBox_S1_DC3_13", "textEdit_S1_DC1_PF_12",
                "textEdit_S3_TIME_3", "comboBox_S3_TIME_3", "textEdit_S3_TIME_2", "comboBox_S3_TIME_2",
                "checkBox_S5", "comboBox_S5_AC", "checkBox_S5_DC1", "comboBox_S5_DC1", "checkBox_S5_DC2",
                "comboBox_S5_DC2", "checkBox_S5_DC3", "comboBox_S5_DC3", "checkBox_S5_DC4", "comboBox_S5_DC4",
            "checkBox_S2_WT1806E", "checkBox_S1_Integral", "comboBox_S1_Integral", "checkBox_S2_WT5000"]

#泰国电压闪变保存设定
def Save_File_ThaiXieBoDianLiu(kwargs):
    dialog_windowxiebodianliu = kwargs['dialog_windowxiebodianliu']
    uiThaiXieBoDianLiu = kwargs['uiThaiXieBoDianLiu']
    uiThiaWT3000E = kwargs['uiThiaWT3000E']
    uiThiaWT1800 = kwargs['uiThiaWT1800']
    uiThiaWT1806E = kwargs['uiThiaWT1806E']
    uiThiaWT5000 = kwargs['uiThiaWT5000']
    result = []
    directory1 = QFileDialog.getSaveFileName(dialog_windowxiebodianliu, "单个文件保存", "./", "Text Files(*.csv)")
    if directory1[0] == '':
        print('请选择一个文件')
    else:
        arrayRow2 = ['ThaiXieBoDianLiu']

        # step1
        if uiThaiXieBoDianLiu.checkBox_S1.isChecked():
            checkBox_S1 = '1'
        else:
            checkBox_S1 = '0'
        arrayRow2.append(checkBox_S1)

        comboBox_S1_AC = uiThaiXieBoDianLiu.comboBox_S1_AC.currentIndex()
        arrayRow2.append(comboBox_S1_AC)

        textEdit_S1_AC_VOLT = uiThaiXieBoDianLiu.textEdit_S1_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT)

        textEdit_S1_AC_VOLT_2 = uiThaiXieBoDianLiu.textEdit_S1_AC_VOLT_2.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_2)

        textEdit_S1_AC_VOLT_3 = uiThaiXieBoDianLiu.textEdit_S1_AC_VOLT_3.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_3)

        textEdit_S1_AC_FR = uiThaiXieBoDianLiu.textEdit_S1_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S1_AC_FR)

        comboBox_S1_AC_2 = uiThaiXieBoDianLiu.comboBox_S1_AC_2.currentIndex()
        arrayRow2.append(comboBox_S1_AC_2)

        if uiThaiXieBoDianLiu.checkBox_S1_DC1.isChecked():
            checkBox_S1_DC1 = '1'
        else:
            checkBox_S1_DC1 = '0'
        arrayRow2.append(checkBox_S1_DC1)

        comboBox_S1_DC1 = uiThaiXieBoDianLiu.comboBox_S1_DC1.currentIndex()
        arrayRow2.append(comboBox_S1_DC1)

        textEdit_S1_DC1_VOLT = uiThaiXieBoDianLiu.textEdit_S1_DC1_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_VOLT)

        textEdit_S1_DC1_CURR = uiThaiXieBoDianLiu.textEdit_S1_DC1_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_CURR)

        textEdit_S1_DC1_Voc = uiThaiXieBoDianLiu.textEdit_S1_DC1_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Voc)

        textEdit_S1_DC1_Isc = uiThaiXieBoDianLiu.textEdit_S1_DC1_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Isc)
        
        textEdit_S1_DC1_PF = uiThaiXieBoDianLiu.textEdit_S1_DC1_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF)

        if uiThaiXieBoDianLiu.checkBox_S1_DC2.isChecked():
            checkBox_S1_DC2 = '1'
        else:
            checkBox_S1_DC2 = '0'
        arrayRow2.append(checkBox_S1_DC2)

        comboBox_S1_DC2 = uiThaiXieBoDianLiu.comboBox_S1_DC2.currentIndex()
        arrayRow2.append(comboBox_S1_DC2)

        textEdit_S1_DC2_VOLT = uiThaiXieBoDianLiu.textEdit_S1_DC2_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_VOLT)

        textEdit_S1_DC2_CURR = uiThaiXieBoDianLiu.textEdit_S1_DC2_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_CURR)

        textEdit_S1_DC2_Voc = uiThaiXieBoDianLiu.textEdit_S1_DC2_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Voc)

        textEdit_S1_DC2_Isc = uiThaiXieBoDianLiu.textEdit_S1_DC2_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Isc)
        
        textEdit_S1_DC2_PF = uiThaiXieBoDianLiu.textEdit_S1_DC2_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_PF)
        
        if uiThaiXieBoDianLiu.checkBox_S1_DC3.isChecked():
            checkBox_S1_DC3 = '1'
        else:
            checkBox_S1_DC3 = '0'
        arrayRow2.append(checkBox_S1_DC3)

        comboBox_S1_DC3 = uiThaiXieBoDianLiu.comboBox_S1_DC3.currentIndex()
        arrayRow2.append(comboBox_S1_DC3)

        textEdit_S1_DC3_VOLT = uiThaiXieBoDianLiu.textEdit_S1_DC3_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_VOLT)

        textEdit_S1_DC3_CURR = uiThaiXieBoDianLiu.textEdit_S1_DC3_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_CURR)

        textEdit_S1_DC3_Voc = uiThaiXieBoDianLiu.textEdit_S1_DC3_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Voc)

        textEdit_S1_DC3_Isc = uiThaiXieBoDianLiu.textEdit_S1_DC3_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Isc)
        
        textEdit_S1_DC3_PF = uiThaiXieBoDianLiu.textEdit_S1_DC3_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_PF)

        if uiThaiXieBoDianLiu.checkBox_S1_DC4.isChecked():
            checkBox_S1_DC4 = '1'
        else:
            checkBox_S1_DC4 = '0'
        arrayRow2.append(checkBox_S1_DC4)

        comboBox_S1_DC4 = uiThaiXieBoDianLiu.comboBox_S1_DC4.currentIndex()
        arrayRow2.append(comboBox_S1_DC4)

        textEdit_S1_DC4_VOLT = uiThaiXieBoDianLiu.textEdit_S1_DC4_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_VOLT)

        textEdit_S1_DC4_CURR = uiThaiXieBoDianLiu.textEdit_S1_DC4_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_CURR)

        textEdit_S1_DC4_Voc = uiThaiXieBoDianLiu.textEdit_S1_DC4_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Voc)

        textEdit_S1_DC4_Isc = uiThaiXieBoDianLiu.textEdit_S1_DC4_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Isc)
        
        textEdit_S1_DC4_PF = uiThaiXieBoDianLiu.textEdit_S1_DC4_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_PF)

        textEdit_S1_ACWaitTIME = uiThaiXieBoDianLiu.textEdit_S1_ACWaitTIME.toPlainText()
        arrayRow2.append(textEdit_S1_ACWaitTIME)

        comboBox_S1_ACWaitTIME = uiThaiXieBoDianLiu.comboBox_S1_ACWaitTIME.currentIndex()
        arrayRow2.append(comboBox_S1_ACWaitTIME)
        
        textEdit_S1_TIME = uiThaiXieBoDianLiu.textEdit_S1_TIME.toPlainText()
        arrayRow2.append(textEdit_S1_TIME)

        comboBox_S1_TIME = uiThaiXieBoDianLiu.comboBox_S1_TIME.currentIndex()
        arrayRow2.append(comboBox_S1_TIME)

        # step2
        if uiThaiXieBoDianLiu.checkBox_S2.isChecked():
            checkBox_S2 = '1'
        else:
            checkBox_S2 = '0'
        arrayRow2.append(checkBox_S2)

        if uiThaiXieBoDianLiu.checkBox_S2_WT3000.isChecked():
            checkBox_S2_WT3000 = '1'
        else:
            checkBox_S2_WT3000 = '0'
        arrayRow2.append(checkBox_S2_WT3000)

        if uiThaiXieBoDianLiu.checkBox_S2_WT1800.isChecked():
            checkBox_S2_WT1800 = '1'
        else:
            checkBox_S2_WT1800 = '0'
        arrayRow2.append(checkBox_S2_WT1800)

        # step3
        if uiThaiXieBoDianLiu.checkBox_S3.isChecked():
            checkBox_S3 = '1'
        else:
            checkBox_S3 = '0'
        arrayRow2.append(checkBox_S3)

        if uiThaiXieBoDianLiu.checkBox_S1_DC1_2.isChecked():
            checkBox_S1_DC1_2 = '1'
        else:
            checkBox_S1_DC1_2 = '0'
        arrayRow2.append(checkBox_S1_DC1_2)

        if uiThaiXieBoDianLiu.checkBox_S1_DC2_2.isChecked():
            checkBox_S1_DC2_2 = '1'
        else:
            checkBox_S1_DC2_2 = '0'
        arrayRow2.append(checkBox_S1_DC2_2)

        if uiThaiXieBoDianLiu.checkBox_S1_DC3_2.isChecked():
            checkBox_S1_DC3_2 = '1'
        else:
            checkBox_S1_DC3_2 = '0'
        arrayRow2.append(checkBox_S1_DC3_2)

        if uiThaiXieBoDianLiu.checkBox_S1_DC4_2.isChecked():
            checkBox_S1_DC4_2 = '1'
        else:
            checkBox_S1_DC4_2 = '0'
        arrayRow2.append(checkBox_S1_DC4_2)

        textEdit_S1_DC1_PF_2 = uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_2.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF_2)

        # step4
        if uiThaiXieBoDianLiu.checkBox_S3_2.isChecked():
            checkBox_S3_2 = '1'
        else:
            checkBox_S3_2 = '0'
        arrayRow2.append(checkBox_S3_2)

        if uiThaiXieBoDianLiu.checkBox_S1_DC1_3.isChecked():
            checkBox_S1_DC1_3 = '1'
        else:
            checkBox_S1_DC1_3 = '0'
        arrayRow2.append(checkBox_S1_DC1_3)

        if uiThaiXieBoDianLiu.checkBox_S1_DC2_3.isChecked():
            checkBox_S1_DC2_3 = '1'
        else:
            checkBox_S1_DC2_3 = '0'
        arrayRow2.append(checkBox_S1_DC2_3)

        if uiThaiXieBoDianLiu.checkBox_S1_DC3_3.isChecked():
            checkBox_S1_DC3_3 = '1'
        else:
            checkBox_S1_DC3_3 = '0'
        arrayRow2.append(checkBox_S1_DC3_3)

        if uiThaiXieBoDianLiu.checkBox_S1_DC4_3.isChecked():
            checkBox_S1_DC4_3 = '1'
        else:
            checkBox_S1_DC4_3 = '0'
        arrayRow2.append(checkBox_S1_DC4_3)

        textEdit_S1_DC1_PF_3 = uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_3.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF_3)

        # step5
        if uiThaiXieBoDianLiu.checkBox_S3_3.isChecked():
            checkBox_S3_3 = '1'
        else:
            checkBox_S3_3 = '0'
        arrayRow2.append(checkBox_S3_3)

        if uiThaiXieBoDianLiu.checkBox_S1_DC1_4.isChecked():
            checkBox_S1_DC1_4 = '1'
        else:
            checkBox_S1_DC1_4 = '0'
        arrayRow2.append(checkBox_S1_DC1_4)

        if uiThaiXieBoDianLiu.checkBox_S1_DC2_4.isChecked():
            checkBox_S1_DC2_4 = '1'
        else:
            checkBox_S1_DC2_4 = '0'
        arrayRow2.append(checkBox_S1_DC2_4)
        
        if uiThaiXieBoDianLiu.checkBox_S1_DC3_4.isChecked():
            checkBox_S1_DC3_4 = '1'
        else:
            checkBox_S1_DC3_4 = '0'
        arrayRow2.append(checkBox_S1_DC3_4)

        if uiThaiXieBoDianLiu.checkBox_S1_DC4_4.isChecked():
            checkBox_S1_DC4_4 = '1'
        else:
            checkBox_S1_DC4_4 = '0'
        arrayRow2.append(checkBox_S1_DC4_4)

        textEdit_S1_DC1_PF_4 = uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_4.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF_4)

        # step6
        if uiThaiXieBoDianLiu.checkBox_S3_4.isChecked():
            checkBox_S3_4 = '1'
        else:
            checkBox_S3_4 = '0'
        arrayRow2.append(checkBox_S3_4)

        if uiThaiXieBoDianLiu.checkBox_S1_DC1_5.isChecked():
            checkBox_S1_DC1_5 = '1'
        else:
            checkBox_S1_DC1_5 = '0'
        arrayRow2.append(checkBox_S1_DC1_5)

        if uiThaiXieBoDianLiu.checkBox_S1_DC2_5.isChecked():
            checkBox_S1_DC2_5 = '1'
        else:
            checkBox_S1_DC2_5 = '0'
        arrayRow2.append(checkBox_S1_DC2_5)
        
        if uiThaiXieBoDianLiu.checkBox_S1_DC3_5.isChecked():
            checkBox_S1_DC3_5 = '1'
        else:
            checkBox_S1_DC3_5 = '0'
        arrayRow2.append(checkBox_S1_DC3_5)

        if uiThaiXieBoDianLiu.checkBox_S1_DC4_5.isChecked():
            checkBox_S1_DC4_5 = '1'
        else:
            checkBox_S1_DC4_5 = '0'
        arrayRow2.append(checkBox_S1_DC4_5)

        textEdit_S1_DC1_PF_5 = uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_5.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF_5)
        
        # step7
        if uiThaiXieBoDianLiu.checkBox_S3_5.isChecked():
            checkBox_S3_5 = '1'
        else:
            checkBox_S3_5 = '0'
        arrayRow2.append(checkBox_S3_5)

        if uiThaiXieBoDianLiu.checkBox_S1_DC1_6.isChecked():
            checkBox_S1_DC1_6 = '1'
        else:
            checkBox_S1_DC1_6 = '0'
        arrayRow2.append(checkBox_S1_DC1_6)

        if uiThaiXieBoDianLiu.checkBox_S1_DC2_6.isChecked():
            checkBox_S1_DC2_6 = '1'
        else:
            checkBox_S1_DC2_6 = '0'
        arrayRow2.append(checkBox_S1_DC2_6)
        
        if uiThaiXieBoDianLiu.checkBox_S1_DC3_6.isChecked():
            checkBox_S1_DC3_6 = '1'
        else:
            checkBox_S1_DC3_6 = '0'
        arrayRow2.append(checkBox_S1_DC3_6)

        if uiThaiXieBoDianLiu.checkBox_S1_DC4_6.isChecked():
            checkBox_S1_DC4_6 = '1'
        else:
            checkBox_S1_DC4_6 = '0'
        arrayRow2.append(checkBox_S1_DC4_6)

        textEdit_S1_DC1_PF_6 = uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_6.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF_6)
        
        # step8
        if uiThaiXieBoDianLiu.checkBox_S3_10.isChecked():
            checkBox_S3_10 = '1'
        else:
            checkBox_S3_10 = '0'
        arrayRow2.append(checkBox_S3_10)

        if uiThaiXieBoDianLiu.checkBox_S1_DC1_10.isChecked():
            checkBox_S1_DC1_10 = '1'
        else:
            checkBox_S1_DC1_10 = '0'
        arrayRow2.append(checkBox_S1_DC1_10)

        if uiThaiXieBoDianLiu.checkBox_S1_DC2_11.isChecked():
            checkBox_S1_DC2_11 = '1'
        else:
            checkBox_S1_DC2_11 = '0'
        arrayRow2.append(checkBox_S1_DC2_11)
        
        if uiThaiXieBoDianLiu.checkBox_S1_DC3_10.isChecked():
            checkBox_S1_DC3_10 = '1'
        else:
            checkBox_S1_DC3_10 = '0'
        arrayRow2.append(checkBox_S1_DC3_10)

        if uiThaiXieBoDianLiu.checkBox_S1_DC4_7.isChecked():
            checkBox_S1_DC4_7 = '1'
        else:
            checkBox_S1_DC4_7 = '0'
        arrayRow2.append(checkBox_S1_DC4_7)

        textEdit_S1_DC1_PF_10 = uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_10.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF_10)
        
        # step9
        if uiThaiXieBoDianLiu.checkBox_S3_6.isChecked():
            checkBox_S3_6 = '1'
        else:
            checkBox_S3_6 = '0'
        arrayRow2.append(checkBox_S3_6)

        if uiThaiXieBoDianLiu.checkBox_S1_DC1_11.isChecked():
            checkBox_S1_DC1_11 = '1'
        else:
            checkBox_S1_DC1_11 = '0'
        arrayRow2.append(checkBox_S1_DC1_11)

        if uiThaiXieBoDianLiu.checkBox_S1_DC2_8.isChecked():
            checkBox_S1_DC2_8 = '1'
        else:
            checkBox_S1_DC2_8 = '0'
        arrayRow2.append(checkBox_S1_DC2_8)
        
        if uiThaiXieBoDianLiu.checkBox_S1_DC3_11.isChecked():
            checkBox_S1_DC3_11 = '1'
        else:
            checkBox_S1_DC3_11 = '0'
        arrayRow2.append(checkBox_S1_DC3_11)

        if uiThaiXieBoDianLiu.checkBox_S1_DC3_15.isChecked():
            checkBox_S1_DC3_15 = '1'
        else:
            checkBox_S1_DC3_15 = '0'
        arrayRow2.append(checkBox_S1_DC3_15)

        textEdit_S1_DC1_PF_9 = uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_9.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF_9)
        
        # step10
        if uiThaiXieBoDianLiu.checkBox_S3_7.isChecked():
            checkBox_S3_7 = '1'
        else:
            checkBox_S3_7 = '0'
        arrayRow2.append(checkBox_S3_7)

        if uiThaiXieBoDianLiu.checkBox_S1_DC1_7.isChecked():
            checkBox_S1_DC1_7 = '1'
        else:
            checkBox_S1_DC1_7 = '0'
        arrayRow2.append(checkBox_S1_DC1_7)

        if uiThaiXieBoDianLiu.checkBox_S1_DC2_9.isChecked():
            checkBox_S1_DC2_9 = '1'
        else:
            checkBox_S1_DC2_9 = '0'
        arrayRow2.append(checkBox_S1_DC2_9)
        
        if uiThaiXieBoDianLiu.checkBox_S1_DC3_8.isChecked():
            checkBox_S1_DC3_8 = '1'
        else:
            checkBox_S1_DC3_8 = '0'
        arrayRow2.append(checkBox_S1_DC3_8)

        if uiThaiXieBoDianLiu.checkBox_S1_DC3_14.isChecked():
            checkBox_S1_DC3_14 = '1'
        else:
            checkBox_S1_DC3_14 = '0'
        arrayRow2.append(checkBox_S1_DC3_14)

        textEdit_S1_DC1_PF_7 = uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_7.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF_7)
        
        # step11
        if uiThaiXieBoDianLiu.checkBox_S3_9.isChecked():
            checkBox_S3_9 = '1'
        else:
            checkBox_S3_9 = '0'
        arrayRow2.append(checkBox_S3_9)

        if uiThaiXieBoDianLiu.checkBox_S1_DC1_9.isChecked():
            checkBox_S1_DC1_9 = '1'
        else:
            checkBox_S1_DC1_9 = '0'
        arrayRow2.append(checkBox_S1_DC1_9)

        if uiThaiXieBoDianLiu.checkBox_S1_DC2_10.isChecked():
            checkBox_S1_DC2_10 = '1'
        else:
            checkBox_S1_DC2_10 = '0'
        arrayRow2.append(checkBox_S1_DC2_10)
        
        if uiThaiXieBoDianLiu.checkBox_S1_DC3_9.isChecked():
            checkBox_S1_DC3_9 = '1'
        else:
            checkBox_S1_DC3_9 = '0'
        arrayRow2.append(checkBox_S1_DC3_9)

        if uiThaiXieBoDianLiu.checkBox_S1_DC3_16.isChecked():
            checkBox_S1_DC3_16 = '1'
        else:
            checkBox_S1_DC3_16 = '0'
        arrayRow2.append(checkBox_S1_DC3_16)

        textEdit_S1_DC1_PF_11 = uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_11.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF_11)

        # step12
        if uiThaiXieBoDianLiu.checkBox_S3_8.isChecked():
            checkBox_S3_8 = '1'
        else:
            checkBox_S3_8 = '0'
        arrayRow2.append(checkBox_S3_8)

        if uiThaiXieBoDianLiu.checkBox_S1_DC1_8.isChecked():
            checkBox_S1_DC1_8 = '1'
        else:
            checkBox_S1_DC1_8 = '0'
        arrayRow2.append(checkBox_S1_DC1_8)

        if uiThaiXieBoDianLiu.checkBox_S1_DC2_7.isChecked():
            checkBox_S1_DC2_7 = '1'
        else:
            checkBox_S1_DC2_7 = '0'
        arrayRow2.append(checkBox_S1_DC2_7)
        
        if uiThaiXieBoDianLiu.checkBox_S1_DC3_7.isChecked():
            checkBox_S1_DC3_7 = '1'
        else:
            checkBox_S1_DC3_7 = '0'
        arrayRow2.append(checkBox_S1_DC3_7)

        if uiThaiXieBoDianLiu.checkBox_S1_DC3_17.isChecked():
            checkBox_S1_DC3_17 = '1'
        else:
            checkBox_S1_DC3_17 = '0'
        arrayRow2.append(checkBox_S1_DC3_17)

        textEdit_S1_DC1_PF_8 = uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_8.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF_8)
        
        # step13
        if uiThaiXieBoDianLiu.checkBox_S3_11.isChecked():
            checkBox_S3_11 = '1'
        else:
            checkBox_S3_11 = '0'
        arrayRow2.append(checkBox_S3_11)

        if uiThaiXieBoDianLiu.checkBox_S1_DC1_12.isChecked():
            checkBox_S1_DC1_12 = '1'
        else:
            checkBox_S1_DC1_12 = '0'
        arrayRow2.append(checkBox_S1_DC1_12)

        if uiThaiXieBoDianLiu.checkBox_S1_DC2_12.isChecked():
            checkBox_S1_DC2_12 = '1'
        else:
            checkBox_S1_DC2_12 = '0'
        arrayRow2.append(checkBox_S1_DC2_12)
        
        if uiThaiXieBoDianLiu.checkBox_S1_DC3_12.isChecked():
            checkBox_S1_DC3_12 = '1'
        else:
            checkBox_S1_DC3_12 = '0'
        arrayRow2.append(checkBox_S1_DC3_12)

        if uiThaiXieBoDianLiu.checkBox_S1_DC3_13.isChecked():
            checkBox_S1_DC3_13 = '1'
        else:
            checkBox_S1_DC3_13 = '0'
        arrayRow2.append(checkBox_S1_DC3_13)

        textEdit_S1_DC1_PF_12 = uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_12.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF_12)

        textEdit_S3_TIME_3 = uiThaiXieBoDianLiu.textEdit_S3_TIME_3.toPlainText()
        arrayRow2.append(textEdit_S3_TIME_3)

        comboBox_S3_TIME_3 = uiThaiXieBoDianLiu.comboBox_S3_TIME_3.currentIndex()
        arrayRow2.append(comboBox_S3_TIME_3)
        
        textEdit_S3_TIME_2 = uiThaiXieBoDianLiu.textEdit_S3_TIME_2.toPlainText()
        arrayRow2.append(textEdit_S3_TIME_2)

        comboBox_S3_TIME_2 = uiThaiXieBoDianLiu.comboBox_S3_TIME_2.currentIndex()
        arrayRow2.append(comboBox_S3_TIME_2)

        # step14
        if uiThaiXieBoDianLiu.checkBox_S5.isChecked():
            checkBox_S5 = '1'
        else:
            checkBox_S5 = '0'
        arrayRow2.append(checkBox_S5)

        comboBox_S5_AC = uiThaiXieBoDianLiu.comboBox_S5_AC.currentIndex()
        arrayRow2.append(comboBox_S5_AC)
        
        if uiThaiXieBoDianLiu.checkBox_S5_DC1.isChecked():
            checkBox_S5_DC1 = '1'
        else:
            checkBox_S5_DC1 = '0'
        arrayRow2.append(checkBox_S5_DC1)

        comboBox_S5_DC1 = uiThaiXieBoDianLiu.comboBox_S5_DC1.currentIndex()
        arrayRow2.append(comboBox_S5_DC1)
        
        if uiThaiXieBoDianLiu.checkBox_S5_DC2.isChecked():
            checkBox_S5_DC2 = '1'
        else:
            checkBox_S5_DC2 = '0'
        arrayRow2.append(checkBox_S5_DC2)

        comboBox_S5_DC2 = uiThaiXieBoDianLiu.comboBox_S5_DC2.currentIndex()
        arrayRow2.append(comboBox_S5_DC2)
        
        if uiThaiXieBoDianLiu.checkBox_S5_DC3.isChecked():
            checkBox_S5_DC3 = '1'
        else:
            checkBox_S5_DC3 = '0'
        arrayRow2.append(checkBox_S5_DC3)

        comboBox_S5_DC3 = uiThaiXieBoDianLiu.comboBox_S5_DC3.currentIndex()
        arrayRow2.append(comboBox_S5_DC3)

        if uiThaiXieBoDianLiu.checkBox_S5_DC4.isChecked():
            checkBox_S5_DC4 = '1'
        else:
            checkBox_S5_DC4 = '0'
        arrayRow2.append(checkBox_S5_DC4)

        comboBox_S5_DC4 = uiThaiXieBoDianLiu.comboBox_S5_DC4.currentIndex()
        arrayRow2.append(comboBox_S5_DC4)

        if uiThaiXieBoDianLiu.checkBox_S2_WT1806E.isChecked():
            checkBox_S2_WT1806E = '1'
        else:
            checkBox_S2_WT1806E = '0'
        arrayRow2.append(checkBox_S2_WT1806E)

        if uiThaiXieBoDianLiu.checkBox_S1_Integral.isChecked():
            checkBox_S1_Integral = '1'
        else:
            checkBox_S1_Integral = '0'
        arrayRow2.append(checkBox_S1_Integral)

        comboBox_S1_Integral = uiThaiXieBoDianLiu.comboBox_S1_Integral.currentIndex()
        arrayRow2.append(comboBox_S1_Integral)

        if uiThaiXieBoDianLiu.checkBox_S2_WT5000.isChecked():
            checkBox_S2_WT5000 = '1'
        else:
            checkBox_S2_WT5000 = '0'
        arrayRow2.append(checkBox_S2_WT5000)

        if uiThaiXieBoDianLiu.checkBox_S2_WT3000.isChecked():
            result = Save_File_ThaiWT3000_Config(uiThiaWT3000E)

        if uiThaiXieBoDianLiu.checkBox_S2_WT1800.isChecked():
            result = Save_File_ThaiWT1800_Config(uiThiaWT1800)

        if uiThaiXieBoDianLiu.checkBox_S2_WT1806E.isChecked():
            result = Save_File_ThaiWT1806E_Config(uiThiaWT1806E)

        if uiThaiXieBoDianLiu.checkBox_S2_WT5000.isChecked():
            result = Save_File_ThaiWT5000_Config(uiThiaWT5000)

        out = open(directory1[0], 'w+', newline='')
        csv_write = csv.writer(out, dialect="excel")
        csv_write.writerow(arrayRow1)
        csv_write.writerow(arrayRow2)
        if len(result) > 0:
            csv_write.writerow(result[0])
            csv_write.writerow(result[1])
        out.close()
        QMessageBox.information(dialog_windowxiebodianliu, "实验设定提示信息", "谐波电流文件保存完成", QMessageBox.Ok, QMessageBox.Ok)

#谐波电流读取设定
def Open_File_ThaiXieBoDianLiu(kwargs):
    dialog_windowxiebodianliu = kwargs['dialog_windowxiebodianliu']
    uiThaiXieBoDianLiu = kwargs['uiThaiXieBoDianLiu']
    uiThiaWT3000E = kwargs['uiThiaWT3000E']
    uiThiaWT1800 = kwargs['uiThiaWT1800']
    uiThiaWT1806E = kwargs['uiThiaWT1806E']
    uiThiaWT5000 = kwargs['uiThiaWT5000']
    strFlag  = "0"
    result_list = []
    config_dict = {}
    wt_config_dict = {}
    directory1 = QFileDialog.getOpenFileName(dialog_windowxiebodianliu, "单个文件选择", "./", "Text Files(*.csv)")
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
                if config_dict[arrayRow1[0]] == "ThaiXieBoDianLiu":
                    # step1
                    if strFlag == "0":
                        if arrayRow1[1] in config_dict:
                            checkBox_S1 = config_dict[arrayRow1[1]]
                            if checkBox_S1 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[2] in config_dict:
                            comboBox_S1_AC = config_dict[arrayRow1[2]]
                            uiThaiXieBoDianLiu.comboBox_S1_AC.setCurrentIndex(int(comboBox_S1_AC))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[3] in config_dict:
                            textEdit_S1_AC_VOLT = config_dict[arrayRow1[3]]
                            uiThaiXieBoDianLiu.textEdit_S1_AC_VOLT.setText(textEdit_S1_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[4] in config_dict:
                            textEdit_S1_AC_VOLT_2 = config_dict[arrayRow1[4]]
                            uiThaiXieBoDianLiu.textEdit_S1_AC_VOLT_2.setText(textEdit_S1_AC_VOLT_2)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[5] in config_dict:
                            textEdit_S1_AC_VOLT_3 = config_dict[arrayRow1[5]]
                            uiThaiXieBoDianLiu.textEdit_S1_AC_VOLT_3.setText(textEdit_S1_AC_VOLT_3)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[6] in config_dict:
                            textEdit_S1_AC_FR = config_dict[arrayRow1[6]]
                            uiThaiXieBoDianLiu.textEdit_S1_AC_FR.setText(textEdit_S1_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[7] in config_dict:
                            comboBox_S1_AC_2 = config_dict[arrayRow1[7]]
                            uiThaiXieBoDianLiu.comboBox_S1_AC_2.setCurrentIndex(int(comboBox_S1_AC_2))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[8] in config_dict:
                            checkBox_S1_DC1 = config_dict[arrayRow1[8]]
                            if checkBox_S1_DC1 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC1.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[9] in config_dict:
                            comboBox_S1_DC1 = config_dict[arrayRow1[9]]
                            uiThaiXieBoDianLiu.comboBox_S1_DC1.setCurrentIndex(int(comboBox_S1_DC1))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[10] in config_dict:
                            textEdit_S1_DC1_VOLT = config_dict[arrayRow1[10]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_VOLT.setText(textEdit_S1_DC1_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[11] in config_dict:
                            textEdit_S1_DC1_CURR = config_dict[arrayRow1[11]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_CURR.setText(textEdit_S1_DC1_CURR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[12] in config_dict:
                            textEdit_S1_DC1_Voc = config_dict[arrayRow1[12]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_Voc.setText(textEdit_S1_DC1_Voc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[13] in config_dict:
                            textEdit_S1_DC1_Isc = config_dict[arrayRow1[13]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_Isc.setText(textEdit_S1_DC1_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[14] in config_dict:
                            textEdit_S1_DC1_PF = config_dict[arrayRow1[14]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_PF.setText(textEdit_S1_DC1_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[15] in config_dict:
                            checkBox_S1_DC2 = config_dict[arrayRow1[15]]
                            if checkBox_S1_DC2 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC2.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[16] in config_dict:
                            comboBox_S1_DC2 = config_dict[arrayRow1[16]]
                            uiThaiXieBoDianLiu.comboBox_S1_DC2.setCurrentIndex(int(comboBox_S1_DC2))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[17] in config_dict:
                            textEdit_S1_DC2_VOLT = config_dict[arrayRow1[17]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC2_VOLT.setText(textEdit_S1_DC2_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[18] in config_dict:
                            textEdit_S1_DC2_CURR = config_dict[arrayRow1[18]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC2_CURR.setText(textEdit_S1_DC2_CURR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[19] in config_dict:
                            textEdit_S1_DC2_Voc = config_dict[arrayRow1[19]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC2_Voc.setText(textEdit_S1_DC2_Voc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[20] in config_dict:
                            textEdit_S1_DC2_Isc = config_dict[arrayRow1[20]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC2_Isc.setText(textEdit_S1_DC2_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[21] in config_dict:
                            textEdit_S1_DC2_PF = config_dict[arrayRow1[21]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC2_PF.setText(textEdit_S1_DC2_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[22] in config_dict:
                            checkBox_S1_DC3 = config_dict[arrayRow1[22]]
                            if checkBox_S1_DC3 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[23] in config_dict:
                            comboBox_S1_DC3 = config_dict[arrayRow1[23]]
                            uiThaiXieBoDianLiu.comboBox_S1_DC3.setCurrentIndex(int(comboBox_S1_DC3))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[24] in config_dict:
                            textEdit_S1_DC3_VOLT = config_dict[arrayRow1[24]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC3_VOLT.setText(textEdit_S1_DC3_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[25] in config_dict:
                            textEdit_S1_DC3_CURR = config_dict[arrayRow1[25]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC3_CURR.setText(textEdit_S1_DC3_CURR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[26] in config_dict:
                            textEdit_S1_DC3_Voc = config_dict[arrayRow1[26]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC3_Voc.setText(textEdit_S1_DC3_Voc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[27] in config_dict:
                            textEdit_S1_DC3_Isc = config_dict[arrayRow1[27]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC3_Isc.setText(textEdit_S1_DC3_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[28] in config_dict:
                            textEdit_S1_DC3_PF = config_dict[arrayRow1[28]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC3_PF.setText(textEdit_S1_DC3_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[29] in config_dict:
                            checkBox_S1_DC4 = config_dict[arrayRow1[29]]
                            if checkBox_S1_DC4 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC4.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[30] in config_dict:
                            comboBox_S1_DC4 = config_dict[arrayRow1[30]]
                            uiThaiXieBoDianLiu.comboBox_S1_DC4.setCurrentIndex(int(comboBox_S1_DC4))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[31] in config_dict:
                            textEdit_S1_DC4_VOLT = config_dict[arrayRow1[31]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC4_VOLT.setText(textEdit_S1_DC4_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[32] in config_dict:
                            textEdit_S1_DC4_CURR = config_dict[arrayRow1[32]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC4_CURR.setText(textEdit_S1_DC4_CURR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[33] in config_dict:
                            textEdit_S1_DC4_Voc = config_dict[arrayRow1[33]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC4_Voc.setText(textEdit_S1_DC4_Voc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[34] in config_dict:
                            textEdit_S1_DC4_Isc = config_dict[arrayRow1[34]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC4_Isc.setText(textEdit_S1_DC4_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[35] in config_dict:
                            textEdit_S1_DC4_PF = config_dict[arrayRow1[35]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC4_PF.setText(textEdit_S1_DC4_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[36] in config_dict:
                            textEdit_S1_ACWaitTIME = config_dict[arrayRow1[36]]
                            uiThaiXieBoDianLiu.textEdit_S1_ACWaitTIME.setText(textEdit_S1_ACWaitTIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[37] in config_dict:
                            comboBox_S1_ACWaitTIME = config_dict[arrayRow1[37]]
                            uiThaiXieBoDianLiu.comboBox_S1_ACWaitTIME.setCurrentIndex(int(comboBox_S1_ACWaitTIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[38] in config_dict:
                            textEdit_S1_TIME = config_dict[arrayRow1[38]]
                            uiThaiXieBoDianLiu.textEdit_S1_TIME.setText(textEdit_S1_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[39] in config_dict:
                            comboBox_S1_TIME = config_dict[arrayRow1[39]]
                            uiThaiXieBoDianLiu.comboBox_S1_TIME.setCurrentIndex(int(comboBox_S1_TIME))
                        else:
                            strFlag = 1
                    
                    # step2
                    if strFlag == "0":
                        if arrayRow1[40] in config_dict:
                            checkBox_S2 = config_dict[arrayRow1[40]]
                            if checkBox_S2 == '1':
                                uiThaiXieBoDianLiu.checkBox_S2.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[41] in config_dict:
                            checkBox_S2_WT3000 = config_dict[arrayRow1[41]]
                            if checkBox_S2_WT3000 == '1':
                                uiThaiXieBoDianLiu.checkBox_S2_WT3000.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S2_WT3000.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[42] in config_dict:
                            checkBox_S2_WT1800 = config_dict[arrayRow1[42]]
                            if checkBox_S2_WT1800 == '1':
                                uiThaiXieBoDianLiu.checkBox_S2_WT1800.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S2_WT1800.setChecked(False)
                        else:
                            strFlag = 1

                    # step3
                    if strFlag == "0":
                        if arrayRow1[43] in config_dict:
                            checkBox_S3 = config_dict[arrayRow1[43]]
                            if checkBox_S3 == '1':
                                uiThaiXieBoDianLiu.checkBox_S3.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[44] in config_dict:
                            checkBox_S1_DC1_2 = config_dict[arrayRow1[44]]
                            if checkBox_S1_DC1_2 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_2.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[45] in config_dict:
                            checkBox_S1_DC2_2 = config_dict[arrayRow1[45]]
                            if checkBox_S1_DC2_2 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_2.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[46] in config_dict:
                            checkBox_S1_DC3_2 = config_dict[arrayRow1[46]]
                            if checkBox_S1_DC3_2 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_2.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[47] in config_dict:
                            checkBox_S1_DC4_2 = config_dict[arrayRow1[47]]
                            if checkBox_S1_DC4_2 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC4_2.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC4_2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[48] in config_dict:
                            textEdit_S1_DC1_PF_2 = config_dict[arrayRow1[48]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_2.setText(textEdit_S1_DC1_PF_2)
                        else:
                            strFlag = 1

                    # step4
                    if strFlag == "0":
                        if arrayRow1[49] in config_dict:
                            checkBox_S3_2 = config_dict[arrayRow1[49]]
                            if checkBox_S3_2 == '1':
                                uiThaiXieBoDianLiu.checkBox_S3_2.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S3_2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[50] in config_dict:
                            checkBox_S1_DC1_3 = config_dict[arrayRow1[50]]
                            if checkBox_S1_DC1_3 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_3.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[51] in config_dict:
                            checkBox_S1_DC2_3 = config_dict[arrayRow1[51]]
                            if checkBox_S1_DC2_3 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_3.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[52] in config_dict:
                            checkBox_S1_DC3_3 = config_dict[arrayRow1[52]]
                            if checkBox_S1_DC3_3 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_3.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[53] in config_dict:
                            checkBox_S1_DC4_3 = config_dict[arrayRow1[53]]
                            if checkBox_S1_DC4_3 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC4_3.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC4_3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[54] in config_dict:
                            textEdit_S1_DC1_PF_3 = config_dict[arrayRow1[54]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_3.setText(textEdit_S1_DC1_PF_3)
                        else:
                            strFlag = 1
                    
                    # step5
                    if strFlag == "0":
                        if arrayRow1[55] in config_dict:
                            checkBox_S3_3 = config_dict[arrayRow1[55]]
                            if checkBox_S3_3 == '1':
                                uiThaiXieBoDianLiu.checkBox_S3_3.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S3_3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[56] in config_dict:
                            checkBox_S1_DC1_4 = config_dict[arrayRow1[56]]
                            if checkBox_S1_DC1_4 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_4.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[57] in config_dict:
                            checkBox_S1_DC2_4 = config_dict[arrayRow1[57]]
                            if checkBox_S1_DC2_4 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_4.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[58] in config_dict:
                            checkBox_S1_DC3_4 = config_dict[arrayRow1[58]]
                            if checkBox_S1_DC3_4 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_4.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[59] in config_dict:
                            checkBox_S1_DC4_4 = config_dict[arrayRow1[59]]
                            if checkBox_S1_DC4_4 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC4_4.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC4_4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[60] in config_dict:
                            textEdit_S1_DC1_PF_4 = config_dict[arrayRow1[60]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_4.setText(textEdit_S1_DC1_PF_4)
                        else:
                            strFlag = 1

                    # step6
                    if strFlag == "0":
                        if arrayRow1[61] in config_dict:
                            checkBox_S3_4 = config_dict[arrayRow1[61]]
                            if checkBox_S3_4 == '1':
                                uiThaiXieBoDianLiu.checkBox_S3_4.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S3_4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[62] in config_dict:
                            checkBox_S1_DC1_5 = config_dict[arrayRow1[62]]
                            if checkBox_S1_DC1_5 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_5.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_5.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[63] in config_dict:
                            checkBox_S1_DC2_5 = config_dict[arrayRow1[63]]
                            if checkBox_S1_DC2_5 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_5.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_5.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[64] in config_dict:
                            checkBox_S1_DC3_5 = config_dict[arrayRow1[64]]
                            if checkBox_S1_DC3_5 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_5.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_5.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[65] in config_dict:
                            checkBox_S1_DC4_5 = config_dict[arrayRow1[65]]
                            if checkBox_S1_DC4_5 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC4_5.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC4_5.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[66] in config_dict:
                            textEdit_S1_DC1_PF_5 = config_dict[arrayRow1[66]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_5.setText(textEdit_S1_DC1_PF_5)
                        else:
                            strFlag = 1

                    # step7
                    if strFlag == "0":
                        if arrayRow1[67] in config_dict:
                            checkBox_S3_5 = config_dict[arrayRow1[67]]
                            if checkBox_S3_5 == '1':
                                uiThaiXieBoDianLiu.checkBox_S3_5.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S3_5.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[68] in config_dict:
                            checkBox_S1_DC1_6 = config_dict[arrayRow1[68]]
                            if checkBox_S1_DC1_6 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_6.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_6.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[69] in config_dict:
                            checkBox_S1_DC2_6 = config_dict[arrayRow1[69]]
                            if checkBox_S1_DC2_6 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_6.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_6.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[70] in config_dict:
                            checkBox_S1_DC3_6 = config_dict[arrayRow1[70]]
                            if checkBox_S1_DC3_6 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_6.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_6.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[71] in config_dict:
                            checkBox_S1_DC4_6 = config_dict[arrayRow1[71]]
                            if checkBox_S1_DC4_6 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC4_6.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC4_6.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[72] in config_dict:
                            textEdit_S1_DC1_PF_6 = config_dict[arrayRow1[72]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_6.setText(textEdit_S1_DC1_PF_6)
                        else:
                            strFlag = 1

                    # step8
                    if strFlag == "0":
                        if arrayRow1[73] in config_dict:
                            checkBox_S3_10 = config_dict[arrayRow1[73]]
                            if checkBox_S3_10 == '1':
                                uiThaiXieBoDianLiu.checkBox_S3_10.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S3_10.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[74] in config_dict:
                            checkBox_S1_DC1_10 = config_dict[arrayRow1[74]]
                            if checkBox_S1_DC1_10 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_10.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_10.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[75] in config_dict:
                            checkBox_S1_DC2_11 = config_dict[arrayRow1[75]]
                            if checkBox_S1_DC2_11 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_11.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_11.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[76] in config_dict:
                            checkBox_S1_DC3_10 = config_dict[arrayRow1[76]]
                            if checkBox_S1_DC3_10 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_10.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_10.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[77] in config_dict:
                            checkBox_S1_DC4_7 = config_dict[arrayRow1[77]]
                            if checkBox_S1_DC4_7 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC4_7.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC4_7.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[78] in config_dict:
                            textEdit_S1_DC1_PF_10 = config_dict[arrayRow1[78]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_10.setText(textEdit_S1_DC1_PF_10)
                        else:
                            strFlag = 1

                    # step9
                    if strFlag == "0":
                        if arrayRow1[79] in config_dict:
                            checkBox_S3_6 = config_dict[arrayRow1[79]]
                            if checkBox_S3_6 == '1':
                                uiThaiXieBoDianLiu.checkBox_S3_6.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S3_6.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[80] in config_dict:
                            checkBox_S1_DC1_11 = config_dict[arrayRow1[80]]
                            if checkBox_S1_DC1_11 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_11.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_11.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[81] in config_dict:
                            checkBox_S1_DC2_8 = config_dict[arrayRow1[81]]
                            if checkBox_S1_DC2_8 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_8.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_8.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[82] in config_dict:
                            checkBox_S1_DC3_11 = config_dict[arrayRow1[82]]
                            if checkBox_S1_DC3_11 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_11.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_11.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[83] in config_dict:
                            checkBox_S1_DC3_15 = config_dict[arrayRow1[83]]
                            if checkBox_S1_DC3_15 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_15.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_15.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[84] in config_dict:
                            textEdit_S1_DC1_PF_9 = config_dict[arrayRow1[84]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_9.setText(textEdit_S1_DC1_PF_9)
                        else:
                            strFlag = 1

                    # step10
                    if strFlag == "0":
                        if arrayRow1[85] in config_dict:
                            checkBox_S3_7 = config_dict[arrayRow1[85]]
                            if checkBox_S3_7 == '1':
                                uiThaiXieBoDianLiu.checkBox_S3_7.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S3_7.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[86] in config_dict:
                            checkBox_S1_DC1_7 = config_dict[arrayRow1[86]]
                            if checkBox_S1_DC1_7 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_7.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_7.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[87] in config_dict:
                            checkBox_S1_DC2_9 = config_dict[arrayRow1[87]]
                            if checkBox_S1_DC2_9 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_9.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_9.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[88] in config_dict:
                            checkBox_S1_DC3_8 = config_dict[arrayRow1[88]]
                            if checkBox_S1_DC3_8 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_8.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_8.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[89] in config_dict:
                            checkBox_S1_DC3_14 = config_dict[arrayRow1[89]]
                            if checkBox_S1_DC3_14 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_14.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_14.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[90] in config_dict:
                            textEdit_S1_DC1_PF_7 = config_dict[arrayRow1[90]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_7.setText(textEdit_S1_DC1_PF_7)
                        else:
                            strFlag = 1

                    # step11
                    if strFlag == "0":
                        if arrayRow1[91] in config_dict:
                            checkBox_S3_9 = config_dict[arrayRow1[91]]
                            if checkBox_S3_9 == '1':
                                uiThaiXieBoDianLiu.checkBox_S3_9.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S3_9.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[92] in config_dict:
                            checkBox_S1_DC1_9 = config_dict[arrayRow1[92]]
                            if checkBox_S1_DC1_9 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_9.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_9.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[93] in config_dict:
                            checkBox_S1_DC2_10 = config_dict[arrayRow1[93]]
                            if checkBox_S1_DC2_10 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_10.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_10.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[94] in config_dict:
                            checkBox_S1_DC3_9 = config_dict[arrayRow1[94]]
                            if checkBox_S1_DC3_9 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_9.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_9.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[95] in config_dict:
                            checkBox_S1_DC3_16 = config_dict[arrayRow1[95]]
                            if checkBox_S1_DC3_16 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_16.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_16.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[96] in config_dict:
                            textEdit_S1_DC1_PF_11 = config_dict[arrayRow1[96]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_11.setText(textEdit_S1_DC1_PF_11)
                        else:
                            strFlag = 1

                    # step12
                    if strFlag == "0":
                        if arrayRow1[97] in config_dict:
                            checkBox_S3_8 = config_dict[arrayRow1[97]]
                            if checkBox_S3_8 == '1':
                                uiThaiXieBoDianLiu.checkBox_S3_8.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S3_8.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[98] in config_dict:
                            checkBox_S1_DC1_8 = config_dict[arrayRow1[98]]
                            if checkBox_S1_DC1_8 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_8.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_8.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[99] in config_dict:
                            checkBox_S1_DC2_7 = config_dict[arrayRow1[99]]
                            if checkBox_S1_DC2_7 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_7.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_7.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[100] in config_dict:
                            checkBox_S1_DC3_7 = config_dict[arrayRow1[100]]
                            if checkBox_S1_DC3_7 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_7.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_7.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[101] in config_dict:
                            checkBox_S1_DC3_17 = config_dict[arrayRow1[101]]
                            if checkBox_S1_DC3_17 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_17.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_17.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[102] in config_dict:
                            textEdit_S1_DC1_PF_8 = config_dict[arrayRow1[102]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_8.setText(textEdit_S1_DC1_PF_8)
                        else:
                            strFlag = 1

                    # step13
                    if strFlag == "0":
                        if arrayRow1[103] in config_dict:
                            checkBox_S3_11 = config_dict[arrayRow1[103]]
                            if checkBox_S3_11 == '1':
                                uiThaiXieBoDianLiu.checkBox_S3_11.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S3_11.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[104] in config_dict:
                            checkBox_S1_DC1_12 = config_dict[arrayRow1[104]]
                            if checkBox_S1_DC1_12 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_12.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC1_12.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[105] in config_dict:
                            checkBox_S1_DC2_12 = config_dict[arrayRow1[105]]
                            if checkBox_S1_DC2_12 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_12.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC2_12.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[106] in config_dict:
                            checkBox_S1_DC3_12 = config_dict[arrayRow1[106]]
                            if checkBox_S1_DC3_12 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_12.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_12.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[107] in config_dict:
                            checkBox_S1_DC3_13 = config_dict[arrayRow1[107]]
                            if checkBox_S1_DC3_13 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_13.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_DC3_13.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[108] in config_dict:
                            textEdit_S1_DC1_PF_12 = config_dict[arrayRow1[108]]
                            uiThaiXieBoDianLiu.textEdit_S1_DC1_PF_12.setText(textEdit_S1_DC1_PF_12)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[109] in config_dict:
                            textEdit_S3_TIME_3 = config_dict[arrayRow1[109]]
                            uiThaiXieBoDianLiu.textEdit_S3_TIME_3.setText(textEdit_S3_TIME_3)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[110] in config_dict:
                            comboBox_S3_TIME_3 = config_dict[arrayRow1[110]]
                            uiThaiXieBoDianLiu.comboBox_S3_TIME_3.setCurrentIndex(int(comboBox_S3_TIME_3))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[111] in config_dict:
                            textEdit_S3_TIME_2 = config_dict[arrayRow1[111]]
                            uiThaiXieBoDianLiu.textEdit_S3_TIME_2.setText(textEdit_S3_TIME_2)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[112] in config_dict:
                            comboBox_S3_TIME_2 = config_dict[arrayRow1[112]]
                            uiThaiXieBoDianLiu.comboBox_S3_TIME_2.setCurrentIndex(int(comboBox_S3_TIME_2))
                        else:
                            strFlag = 1
                    
                    # step14
                    if strFlag == "0":
                        if arrayRow1[113] in config_dict:
                            checkBox_S5 = config_dict[arrayRow1[113]]
                            if checkBox_S5 == '1':
                                uiThaiXieBoDianLiu.checkBox_S5.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S5.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[114] in config_dict:
                            comboBox_S5_AC = config_dict[arrayRow1[114]]
                            uiThaiXieBoDianLiu.comboBox_S5_AC.setCurrentIndex(int(comboBox_S5_AC))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[115] in config_dict:
                            checkBox_S5_DC1 = config_dict[arrayRow1[115]]
                            if checkBox_S5_DC1 == '1':
                                uiThaiXieBoDianLiu.checkBox_S5_DC1.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S5_DC1.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[116] in config_dict:
                            comboBox_S5_DC1 = config_dict[arrayRow1[116]]
                            uiThaiXieBoDianLiu.comboBox_S5_DC1.setCurrentIndex(int(comboBox_S5_DC1))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[117] in config_dict:
                            checkBox_S5_DC2 = config_dict[arrayRow1[117]]
                            if checkBox_S5_DC2 == '1':
                                uiThaiXieBoDianLiu.checkBox_S5_DC2.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S5_DC2.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[118] in config_dict:
                            comboBox_S5_DC2 = config_dict[arrayRow1[118]]
                            uiThaiXieBoDianLiu.comboBox_S5_DC2.setCurrentIndex(int(comboBox_S5_DC2))
                        else:
                            strFlag = 1
                    if strFlag == "0":
                        if arrayRow1[119] in config_dict:
                            checkBox_S5_DC3 = config_dict[arrayRow1[119]]
                            if checkBox_S5_DC3 == '1':
                                uiThaiXieBoDianLiu.checkBox_S5_DC3.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S5_DC3.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[120] in config_dict:
                            comboBox_S5_DC3 = config_dict[arrayRow1[120]]
                            uiThaiXieBoDianLiu.comboBox_S5_DC3.setCurrentIndex(int(comboBox_S5_DC3))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[121] in config_dict:
                            checkBox_S5_DC4 = config_dict[arrayRow1[121]]
                            if checkBox_S5_DC4 == '1':
                                uiThaiXieBoDianLiu.checkBox_S5_DC4.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S5_DC4.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[122] in config_dict:
                            comboBox_S5_DC4 = config_dict[arrayRow1[122]]
                            uiThaiXieBoDianLiu.comboBox_S5_DC4.setCurrentIndex(int(comboBox_S5_DC4))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[123] in config_dict:
                            checkBox_S2_WT1806E = config_dict[arrayRow1[123]]
                            if checkBox_S2_WT1806E == '1':
                                uiThaiXieBoDianLiu.checkBox_S2_WT1806E.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S2_WT1806E.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[124] in config_dict:
                            checkBox_S1_Integral = config_dict[arrayRow1[124]]
                            if checkBox_S1_Integral == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_Integral.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_Integral.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[125] in config_dict:
                            comboBox_S1_Integral = config_dict[arrayRow1[125]]
                            uiThaiXieBoDianLiu.comboBox_S1_Integral.setCurrentIndex(int(comboBox_S1_Integral))
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[126] in config_dict:
                            checkBox_S2_WT5000 = config_dict[arrayRow1[126]]
                            if checkBox_S2_WT5000 == '1':
                                uiThaiXieBoDianLiu.checkBox_S2_WT5000.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S2_WT5000.setChecked(False)
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

                    if arrayRow1[123] in config_dict:
                        checkBox_S2_WT1806E = config_dict[arrayRow1[123]]
                        if checkBox_S2_WT1806E == '1':
                            Open_File_ThaiWT1806E_Config(uiThiaWT1806E, wt_config_dict)

                    if arrayRow1[126] in config_dict:
                        checkBox_S2_WT5000 = config_dict[arrayRow1[126]]
                        if checkBox_S2_WT5000 == '1':
                            Open_File_ThaiWT5000_Config(uiThiaWT5000, wt_config_dict)
                    else:
                        strFlag = 1
        QMessageBox.information(dialog_windowxiebodianliu, "实验设定提示信息", "谐波电流文件读取完成", QMessageBox.Ok, QMessageBox.Ok)

# def save_file_header():
#     directory1 = [r"D:\\project\\photovoltaic_automation_t\\config_files\\project_step_configs\\xiebodianliu.csv"]
#     if directory1[0] == '':
#         print('请选择一个文件')
#     else:
#         out = open(directory1[0], 'w+', newline='')
#         csv_write = csv.writer(out, dialect="excel")
#         csv_write.writerow(arrayRow1)
#         out.close()

# if __name__ == "__main__":
#     save_file_header()