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
                "checkBox_S2", "checkBox_S2_WT3000", "checkBox_S2_WT1800", "checkBox_S2_WT1806E",
                "checkBox_S3", "checkBox_S3_DC1", "checkBox_S3_DC2", "checkBox_S3_DC3",
                    "checkBox_S3_DC4", "textEdit_S3_DC_PF",
                "checkBox_S4", "checkBox_S4_DC1", "checkBox_S4_DC2", "checkBox_S4_DC3",
                    "checkBox_S4_DC4", "textEdit_S4_DC_PF",
                "checkBox_S5", "checkBox_S5_DC1", "checkBox_S5_DC2", "checkBox_S5_DC3",
                    "checkBox_S5_DC3", "textEdit_S5_DC_PF",
                "checkBox_S6", "checkBox_S6_DC1", "checkBox_S6_DC2", "checkBox_S6_DC3",
                    "checkBox_S6_DC4", "textEdit_S6_DC_PF", 
                "checkBox_S7", "checkBox_S7_DC1", "checkBox_S7_DC2", "checkBox_S7_DC3",
                    "checkBox_S7_DC4", "textEdit_S7_DC_PF",
                "checkBox_S8", "checkBox_S8_DC1", "checkBox_S8_DC2", "checkBox_S8_DC3",
                    "checkBox_S8_DC4", "textEdit_S8_DC_PF",
                "checkBox_S9", "checkBox_S9_AC_Check", "textEdit_S9_AC_Volt", "checkBox_S9_DC1", "checkBox_S9_DC2", "checkBox_S9_DC3",
                    "checkBox_S9_DC4", "textEdit_S9_DC_PF",
                "textEdit_S3_TIME_2", "comboBox_S3_TIME_2",
                "checkBox_S_END", "comboBox_S_END_AC", "checkBox_S_END_DC1", "comboBox_S_END_DC1", "checkBox_S_END_DC2",
                "comboBox_S_END_DC2", "checkBox_S_END_DC3", "comboBox_S_END_DC3", "checkBox_S_END_DC4", "comboBox_S_END_DC4"
                , "checkBox_S2_WT5000"
            ]

# 巴西CosPhi保存设定
def Save_File_ThaiCosPhiBrazil(kwargs):
    dialog_windowcosPhiBrazil = kwargs['dialog_windowcosPhiBrazil']
    uiThaiCosPhiBrazil = kwargs['uiThaiCosPhiBrazil']
    uiThiaWT3000E = kwargs['uiThiaWT3000E']
    uiThiaWT1800 = kwargs['uiThiaWT1800']
    uiThiaWT1806E = kwargs['uiThiaWT1806E']
    uiThiaWT5000 = kwargs['uiThiaWT5000']
    result = []
    directory1 = QFileDialog.getSaveFileName(NonecosPhiBrazil, "单个文件保存", "./", "Text Files(*.csv)")
    if directory1[0] == '':
        print('请选择一个文件')
    else:
        arrayRow2 = ['ThaiCosPhiBrazil']

        # step1
        if uiThaiCosPhiBrazil.checkBox_S1.isChecked():
            checkBox_S1 = '1'
        else:
            checkBox_S1 = '0'
        arrayRow2.append(checkBox_S1)

        comboBox_S1_AC = uiThaiCosPhiBrazil.comboBox_S1_AC.currentIndex()
        arrayRow2.append(comboBox_S1_AC)

        textEdit_S1_AC_VOLT = uiThaiCosPhiBrazil.textEdit_S1_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT)

        textEdit_S1_AC_VOLT_2 = uiThaiCosPhiBrazil.textEdit_S1_AC_VOLT_2.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_2)

        textEdit_S1_AC_VOLT_3 = uiThaiCosPhiBrazil.textEdit_S1_AC_VOLT_3.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_3)

        textEdit_S1_AC_FR = uiThaiCosPhiBrazil.textEdit_S1_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S1_AC_FR)

        comboBox_S1_AC_2 = uiThaiCosPhiBrazil.comboBox_S1_AC_2.currentIndex()
        arrayRow2.append(comboBox_S1_AC_2)

        if uiThaiCosPhiBrazil.checkBox_S1_DC1.isChecked():
            checkBox_S1_DC1 = '1'
        else:
            checkBox_S1_DC1 = '0'
        arrayRow2.append(checkBox_S1_DC1)

        comboBox_S1_DC1 = uiThaiCosPhiBrazil.comboBox_S1_DC1.currentIndex()
        arrayRow2.append(comboBox_S1_DC1)

        textEdit_S1_DC1_VOLT = uiThaiCosPhiBrazil.textEdit_S1_DC1_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_VOLT)

        textEdit_S1_DC1_CURR = uiThaiCosPhiBrazil.textEdit_S1_DC1_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_CURR)

        textEdit_S1_DC1_Voc = uiThaiCosPhiBrazil.textEdit_S1_DC1_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Voc)

        textEdit_S1_DC1_Isc = uiThaiCosPhiBrazil.textEdit_S1_DC1_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Isc)
        
        textEdit_S1_DC1_PF = uiThaiCosPhiBrazil.textEdit_S1_DC1_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF)

        if uiThaiCosPhiBrazil.checkBox_S1_DC2.isChecked():
            checkBox_S1_DC2 = '1'
        else:
            checkBox_S1_DC2 = '0'
        arrayRow2.append(checkBox_S1_DC2)

        comboBox_S1_DC2 = uiThaiCosPhiBrazil.comboBox_S1_DC2.currentIndex()
        arrayRow2.append(comboBox_S1_DC2)

        textEdit_S1_DC2_VOLT = uiThaiCosPhiBrazil.textEdit_S1_DC2_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_VOLT)

        textEdit_S1_DC2_CURR = uiThaiCosPhiBrazil.textEdit_S1_DC2_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_CURR)

        textEdit_S1_DC2_Voc = uiThaiCosPhiBrazil.textEdit_S1_DC2_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Voc)

        textEdit_S1_DC2_Isc = uiThaiCosPhiBrazil.textEdit_S1_DC2_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Isc)
        
        textEdit_S1_DC2_PF = uiThaiCosPhiBrazil.textEdit_S1_DC2_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_PF)
        
        if uiThaiCosPhiBrazil.checkBox_S1_DC3.isChecked():
            checkBox_S1_DC3 = '1'
        else:
            checkBox_S1_DC3 = '0'
        arrayRow2.append(checkBox_S1_DC3)

        comboBox_S1_DC3 = uiThaiCosPhiBrazil.comboBox_S1_DC3.currentIndex()
        arrayRow2.append(comboBox_S1_DC3)

        textEdit_S1_DC3_VOLT = uiThaiCosPhiBrazil.textEdit_S1_DC3_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_VOLT)

        textEdit_S1_DC3_CURR = uiThaiCosPhiBrazil.textEdit_S1_DC3_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_CURR)

        textEdit_S1_DC3_Voc = uiThaiCosPhiBrazil.textEdit_S1_DC3_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Voc)

        textEdit_S1_DC3_Isc = uiThaiCosPhiBrazil.textEdit_S1_DC3_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Isc)
        
        textEdit_S1_DC3_PF = uiThaiCosPhiBrazil.textEdit_S1_DC3_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_PF)

        if uiThaiCosPhiBrazil.checkBox_S1_DC4.isChecked():
            checkBox_S1_DC4 = '1'
        else:
            checkBox_S1_DC4 = '0'
        arrayRow2.append(checkBox_S1_DC4)

        comboBox_S1_DC4 = uiThaiCosPhiBrazil.comboBox_S1_DC4.currentIndex()
        arrayRow2.append(comboBox_S1_DC4)

        textEdit_S1_DC4_VOLT = uiThaiCosPhiBrazil.textEdit_S1_DC4_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_VOLT)

        textEdit_S1_DC4_CURR = uiThaiCosPhiBrazil.textEdit_S1_DC4_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_CURR)

        textEdit_S1_DC4_Voc = uiThaiCosPhiBrazil.textEdit_S1_DC4_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Voc)

        textEdit_S1_DC4_Isc = uiThaiCosPhiBrazil.textEdit_S1_DC4_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Isc)
        
        textEdit_S1_DC4_PF = uiThaiCosPhiBrazil.textEdit_S1_DC4_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_PF)

        textEdit_S1_ACWaitTIME = uiThaiCosPhiBrazil.textEdit_S1_ACWaitTIME.toPlainText()
        arrayRow2.append(textEdit_S1_ACWaitTIME)

        comboBox_S1_ACWaitTIME = uiThaiCosPhiBrazil.comboBox_S1_ACWaitTIME.currentIndex()
        arrayRow2.append(comboBox_S1_ACWaitTIME)
        
        textEdit_S1_TIME = uiThaiCosPhiBrazil.textEdit_S1_TIME.toPlainText()
        arrayRow2.append(textEdit_S1_TIME)

        comboBox_S1_TIME = uiThaiCosPhiBrazil.comboBox_S1_TIME.currentIndex()
        arrayRow2.append(comboBox_S1_TIME)

        # step2
        if uiThaiCosPhiBrazil.checkBox_S2.isChecked():
            checkBox_S2 = '1'
        else:
            checkBox_S2 = '0'
        arrayRow2.append(checkBox_S2)

        if uiThaiCosPhiBrazil.checkBox_S2_WT3000.isChecked():
            checkBox_S2_WT3000 = '1'
        else:
            checkBox_S2_WT3000 = '0'
        arrayRow2.append(checkBox_S2_WT3000)

        if uiThaiCosPhiBrazil.checkBox_S2_WT1800.isChecked():
            checkBox_S2_WT1800 = '1'
        else:
            checkBox_S2_WT1800 = '0'
        arrayRow2.append(checkBox_S2_WT1800)

        if uiThaiCosPhiBrazil.checkBox_S2_WT1806E.isChecked():
            checkBox_S2_WT1806E = '1'
        else:
            checkBox_S2_WT1806E = '0'
        arrayRow2.append(checkBox_S2_WT1806E)

        # step3
        if uiThaiCosPhiBrazil.checkBox_S3.isChecked():
            checkBox_S3 = '1'
        else:
            checkBox_S3 = '0'
        arrayRow2.append(checkBox_S3)

        if uiThaiCosPhiBrazil.checkBox_S3_DC1.isChecked():
            checkBox_S3_DC1 = '1'
        else:
            checkBox_S3_DC1 = '0'
        arrayRow2.append(checkBox_S3_DC1)

        if uiThaiCosPhiBrazil.checkBox_S3_DC2.isChecked():
            checkBox_S3_DC2 = '1'
        else:
            checkBox_S3_DC2 = '0'
        arrayRow2.append(checkBox_S3_DC2)

        if uiThaiCosPhiBrazil.checkBox_S3_DC3.isChecked():
            checkBox_S3_DC3 = '1'
        else:
            checkBox_S3_DC3 = '0'
        arrayRow2.append(checkBox_S3_DC3)

        if uiThaiCosPhiBrazil.checkBox_S3_DC4.isChecked():
            checkBox_S3_DC4 = '1'
        else:
            checkBox_S3_DC4 = '0'
        arrayRow2.append(checkBox_S3_DC4)

        textEdit_S3_DC_PF = uiThaiCosPhiBrazil.textEdit_S3_DC_PF.toPlainText()
        arrayRow2.append(textEdit_S3_DC_PF)

        # step4
        if uiThaiCosPhiBrazil.checkBox_S4.isChecked():
            checkBox_S4 = '1'
        else:
            checkBox_S4 = '0'
        arrayRow2.append(checkBox_S4)

        if uiThaiCosPhiBrazil.checkBox_S4_DC1.isChecked():
            checkBox_S4_DC1 = '1'
        else:
            checkBox_S4_DC1 = '0'
        arrayRow2.append(checkBox_S4_DC1)

        if uiThaiCosPhiBrazil.checkBox_S4_DC2.isChecked():
            checkBox_S4_DC2 = '1'
        else:
            checkBox_S4_DC2 = '0'
        arrayRow2.append(checkBox_S4_DC2)

        if uiThaiCosPhiBrazil.checkBox_S4_DC3.isChecked():
            checkBox_S4_DC3 = '1'
        else:
            checkBox_S4_DC3 = '0'
        arrayRow2.append(checkBox_S4_DC3)

        if uiThaiCosPhiBrazil.checkBox_S4_DC4.isChecked():
            checkBox_S4_DC4 = '1'
        else:
            checkBox_S4_DC4 = '0'
        arrayRow2.append(checkBox_S4_DC4)

        textEdit_S4_DC_PF = uiThaiCosPhiBrazil.textEdit_S4_DC_PF.toPlainText()
        arrayRow2.append(textEdit_S4_DC_PF)

        # step5
        if uiThaiCosPhiBrazil.checkBox_S5.isChecked():
            checkBox_S5 = '1'
        else:
            checkBox_S5 = '0'
        arrayRow2.append(checkBox_S5)

        if uiThaiCosPhiBrazil.checkBox_S5_DC1.isChecked():
            checkBox_S5_DC1 = '1'
        else:
            checkBox_S5_DC1 = '0'
        arrayRow2.append(checkBox_S5_DC1)

        if uiThaiCosPhiBrazil.checkBox_S5_DC2.isChecked():
            checkBox_S5_DC2 = '1'
        else:
            checkBox_S5_DC2 = '0'
        arrayRow2.append(checkBox_S5_DC2)
        
        if uiThaiCosPhiBrazil.checkBox_S5_DC3.isChecked():
            checkBox_S5_DC3 = '1'
        else:
            checkBox_S5_DC3 = '0'
        arrayRow2.append(checkBox_S5_DC3)

        if uiThaiCosPhiBrazil.checkBox_S5_DC4.isChecked():
            checkBox_S5_DC4 = '1'
        else:
            checkBox_S5_DC4 = '0'
        arrayRow2.append(checkBox_S5_DC4)

        textEdit_S5_DC_PF = uiThaiCosPhiBrazil.textEdit_S5_DC_PF.toPlainText()
        arrayRow2.append(textEdit_S5_DC_PF)

        # step6
        if uiThaiCosPhiBrazil.checkBox_S6.isChecked():
            checkBox_S6 = '1'
        else:
            checkBox_S6 = '0'
        arrayRow2.append(checkBox_S6)

        if uiThaiCosPhiBrazil.checkBox_S6_DC1.isChecked():
            checkBox_S6_DC1 = '1'
        else:
            checkBox_S6_DC1 = '0'
        arrayRow2.append(checkBox_S6_DC1)

        if uiThaiCosPhiBrazil.checkBox_S6_DC2.isChecked():
            checkBox_S6_DC2 = '1'
        else:
            checkBox_S6_DC2 = '0'
        arrayRow2.append(checkBox_S6_DC2)
        
        if uiThaiCosPhiBrazil.checkBox_S6_DC3.isChecked():
            checkBox_S6_DC3 = '1'
        else:
            checkBox_S6_DC3 = '0'
        arrayRow2.append(checkBox_S6_DC3)

        if uiThaiCosPhiBrazil.checkBox_S6_DC4.isChecked():
            checkBox_S6_DC4 = '1'
        else:
            checkBox_S6_DC4 = '0'
        arrayRow2.append(checkBox_S6_DC4)

        textEdit_S6_DC_PF = uiThaiCosPhiBrazil.textEdit_S6_DC_PF.toPlainText()
        arrayRow2.append(textEdit_S6_DC_PF)
        
        # step7
        if uiThaiCosPhiBrazil.checkBox_S7.isChecked():
            checkBox_S7 = '1'
        else:
            checkBox_S7 = '0'
        arrayRow2.append(checkBox_S7)

        if uiThaiCosPhiBrazil.checkBox_S7_DC1.isChecked():
            checkBox_S7_DC1 = '1'
        else:
            checkBox_S7_DC1 = '0'
        arrayRow2.append(checkBox_S7_DC1)

        if uiThaiCosPhiBrazil.checkBox_S7_DC2.isChecked():
            checkBox_S7_DC2 = '1'
        else:
            checkBox_S7_DC2 = '0'
        arrayRow2.append(checkBox_S7_DC2)
        
        if uiThaiCosPhiBrazil.checkBox_S7_DC3.isChecked():
            checkBox_S7_DC3 = '1'
        else:
            checkBox_S7_DC3 = '0'
        arrayRow2.append(checkBox_S7_DC3)

        if uiThaiCosPhiBrazil.checkBox_S7_DC4.isChecked():
            checkBox_S7_DC4 = '1'
        else:
            checkBox_S7_DC4 = '0'
        arrayRow2.append(checkBox_S7_DC4)

        textEdit_S7_DC_PF = uiThaiCosPhiBrazil.textEdit_S7_DC_PF.toPlainText()
        arrayRow2.append(textEdit_S7_DC_PF)
        
        # step8
        if uiThaiCosPhiBrazil.checkBox_S8.isChecked():
            checkBox_S8 = '1'
        else:
            checkBox_S8 = '0'
        arrayRow2.append(checkBox_S8)

        if uiThaiCosPhiBrazil.checkBox_S8_DC1.isChecked():
            checkBox_S8_DC1 = '1'
        else:
            checkBox_S8_DC1 = '0'
        arrayRow2.append(checkBox_S8_DC1)

        if uiThaiCosPhiBrazil.checkBox_S8_DC2.isChecked():
            checkBox_S8_DC2 = '1'
        else:
            checkBox_S8_DC2 = '0'
        arrayRow2.append(checkBox_S8_DC2)
        
        if uiThaiCosPhiBrazil.checkBox_S8_DC3.isChecked():
            checkBox_S8_DC3 = '1'
        else:
            checkBox_S8_DC3 = '0'
        arrayRow2.append(checkBox_S8_DC3)

        if uiThaiCosPhiBrazil.checkBox_S8_DC4.isChecked():
            checkBox_S8_DC4 = '1'
        else:
            checkBox_S8_DC4 = '0'
        arrayRow2.append(checkBox_S8_DC4)

        textEdit_S8_DC_PF = uiThaiCosPhiBrazil.textEdit_S8_DC_PF.toPlainText()
        arrayRow2.append(textEdit_S8_DC_PF)
        
        # step9
        if uiThaiCosPhiBrazil.checkBox_S9.isChecked():
            checkBox_S9 = '1'
        else:
            checkBox_S9 = '0'
        arrayRow2.append(checkBox_S9)

        if uiThaiCosPhiBrazil.checkBox_S9_AC_Check.isChecked():
            checkBox_S9_AC_Check = '1'
        else:
            checkBox_S9_AC_Check = '0'
        arrayRow2.append(checkBox_S9_AC_Check)

        textEdit_S9_AC_Volt = uiThaiCosPhiBrazil.textEdit_S9_AC_Volt.toPlainText()
        arrayRow2.append(textEdit_S9_AC_Volt)

        if uiThaiCosPhiBrazil.checkBox_S9_DC1.isChecked():
            checkBox_S9_DC1 = '1'
        else:
            checkBox_S9_DC1 = '0'
        arrayRow2.append(checkBox_S9_DC1)

        if uiThaiCosPhiBrazil.checkBox_S9_DC2.isChecked():
            checkBox_S9_DC2 = '1'
        else:
            checkBox_S9_DC2 = '0'
        arrayRow2.append(checkBox_S9_DC2)
        
        if uiThaiCosPhiBrazil.checkBox_S9_DC3.isChecked():
            checkBox_S9_DC3 = '1'
        else:
            checkBox_S9_DC3 = '0'
        arrayRow2.append(checkBox_S9_DC3)

        if uiThaiCosPhiBrazil.checkBox_S9_DC4.isChecked():
            checkBox_S9_DC4 = '1'
        else:
            checkBox_S9_DC4 = '0'
        arrayRow2.append(checkBox_S9_DC4)

        textEdit_S9_DC_PF = uiThaiCosPhiBrazil.textEdit_S9_DC_PF.toPlainText()
        arrayRow2.append(textEdit_S9_DC_PF)
        
        textEdit_S3_TIME_2 = uiThaiCosPhiBrazil.textEdit_S3_TIME_2.toPlainText()
        arrayRow2.append(textEdit_S3_TIME_2)

        comboBox_S3_TIME_2 = uiThaiCosPhiBrazil.comboBox_S3_TIME_2.currentIndex()
        arrayRow2.append(comboBox_S3_TIME_2)

        # step_end
        if uiThaiCosPhiBrazil.checkBox_S_END.isChecked():
            checkBox_S_END = '1'
        else:
            checkBox_S_END = '0'
        arrayRow2.append(checkBox_S_END)

        comboBox_S_END_AC = uiThaiCosPhiBrazil.comboBox_S_END_AC.currentIndex()
        arrayRow2.append(comboBox_S_END_AC)
        
        if uiThaiCosPhiBrazil.checkBox_S_END_DC1.isChecked():
            checkBox_S_END_DC1 = '1'
        else:
            checkBox_S_END_DC1 = '0'
        arrayRow2.append(checkBox_S_END_DC1)

        comboBox_S_END_DC1 = uiThaiCosPhiBrazil.comboBox_S_END_DC1.currentIndex()
        arrayRow2.append(comboBox_S_END_DC1)
        
        if uiThaiCosPhiBrazil.checkBox_S_END_DC2.isChecked():
            checkBox_S_END_DC2 = '1'
        else:
            checkBox_S_END_DC2 = '0'
        arrayRow2.append(checkBox_S_END_DC2)

        comboBox_S_END_DC2 = uiThaiCosPhiBrazil.comboBox_S_END_DC2.currentIndex()
        arrayRow2.append(comboBox_S_END_DC2)
        
        if uiThaiCosPhiBrazil.checkBox_S_END_DC3.isChecked():
            checkBox_S_END_DC3 = '1'
        else:
            checkBox_S_END_DC3 = '0'
        arrayRow2.append(checkBox_S_END_DC3)

        comboBox_S_END_DC3 = uiThaiCosPhiBrazil.comboBox_S_END_DC3.currentIndex()
        arrayRow2.append(comboBox_S_END_DC3)

        if uiThaiCosPhiBrazil.checkBox_S_END_DC4.isChecked():
            checkBox_S_END_DC4 = '1'
        else:
            checkBox_S_END_DC4 = '0'
        arrayRow2.append(checkBox_S_END_DC4)

        comboBox_S_END_DC4 = uiThaiCosPhiBrazil.comboBox_S_END_DC4.currentIndex()
        arrayRow2.append(comboBox_S_END_DC4)

        if uiThaiCosPhiBrazil.checkBox_S2_WT5000.isChecked():
            checkBox_S2_WT5000 = '1'
        else:
            checkBox_S2_WT5000 = '0'
        arrayRow2.append(checkBox_S2_WT5000)

        if uiThaiCosPhiBrazil.checkBox_S2_WT3000.isChecked():
            result = Save_File_ThaiWT3000_Config(uiThiaWT3000E)

        if uiThaiCosPhiBrazil.checkBox_S2_WT1800.isChecked():
            result = Save_File_ThaiWT1800_Config(uiThiaWT1800)

        if uiThaiCosPhiBrazil.checkBox_S2_WT1806E.isChecked():
            result = Save_File_ThaiWT1806E_Config(uiThiaWT1806E)

        if uiThaiCosPhiBrazil.checkBox_S2_WT5000.isChecked():
            result = Save_File_ThaiWT5000_Config(uiThiaWT5000)

        out = open(directory1[0], 'w+', newline='')
        csv_write = csv.writer(out, dialect="excel")
        csv_write.writerow(arrayRow1)
        csv_write.writerow(arrayRow2)
        if len(result) > 0:
            csv_write.writerow(result[0])
            csv_write.writerow(result[1])
        out.close()
        QMessageBox.information(NonecosPhiBrazil, "实验设定提示信息", "巴西Cos(φ)文件保存完成", QMessageBox.Ok, QMessageBox.Ok)

# 巴西CosPhi读取设定
def Open_File_ThaiCosPhiBrazil(kwargs):
    dialog_windowcosPhiBrazil = kwargs['dialog_windowcosPhiBrazil']
    uiThaiCosPhiBrazil = kwargs['uiThaiCosPhiBrazil']
    uiThiaWT3000E = kwargs['uiThiaWT3000E']
    uiThiaWT1800 = kwargs['uiThiaWT1800']
    uiThiaWT1806E = kwargs['uiThiaWT1806E']
    uiThiaWT5000 = kwargs['uiThiaWT5000']
    strFlag  = "0"
    result_list = []
    config_dict = {}
    wt_config_dict = {}
    directory1 = QFileDialog.getOpenFileName(NonecosPhiBrazil, "单个文件选择", "./", "Text Files(*.csv)")
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
                if config_dict[arrayRow1[0]] == "ThaiCosPhiBrazil":
                    # step1
                    if strFlag == "0":
                        if arrayRow1[1] in config_dict:
                            checkBox_S1 = config_dict[arrayRow1[1]]
                            if checkBox_S1 == '1':
                                uiThaiCosPhiBrazil.checkBox_S1.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[2] in config_dict:
                            comboBox_S1_AC = config_dict[arrayRow1[2]]
                            uiThaiCosPhiBrazil.comboBox_S1_AC.setCurrentIndex(int(comboBox_S1_AC))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[3] in config_dict:
                            textEdit_S1_AC_VOLT = config_dict[arrayRow1[3]]
                            uiThaiCosPhiBrazil.textEdit_S1_AC_VOLT.setText(textEdit_S1_AC_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[4] in config_dict:
                            textEdit_S1_AC_VOLT_2 = config_dict[arrayRow1[4]]
                            uiThaiCosPhiBrazil.textEdit_S1_AC_VOLT_2.setText(textEdit_S1_AC_VOLT_2)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[5] in config_dict:
                            textEdit_S1_AC_VOLT_3 = config_dict[arrayRow1[5]]
                            uiThaiCosPhiBrazil.textEdit_S1_AC_VOLT_3.setText(textEdit_S1_AC_VOLT_3)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[6] in config_dict:
                            textEdit_S1_AC_FR = config_dict[arrayRow1[6]]
                            uiThaiCosPhiBrazil.textEdit_S1_AC_FR.setText(textEdit_S1_AC_FR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[7] in config_dict:
                            comboBox_S1_AC_2 = config_dict[arrayRow1[7]]
                            uiThaiCosPhiBrazil.comboBox_S1_AC_2.setCurrentIndex(int(comboBox_S1_AC_2))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[8] in config_dict:
                            checkBox_S1_DC1 = config_dict[arrayRow1[8]]
                            if checkBox_S1_DC1 == '1':
                                uiThaiCosPhiBrazil.checkBox_S1_DC1.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S1_DC1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[9] in config_dict:
                            comboBox_S1_DC1 = config_dict[arrayRow1[9]]
                            uiThaiCosPhiBrazil.comboBox_S1_DC1.setCurrentIndex(int(comboBox_S1_DC1))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[10] in config_dict:
                            textEdit_S1_DC1_VOLT = config_dict[arrayRow1[10]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC1_VOLT.setText(textEdit_S1_DC1_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[11] in config_dict:
                            textEdit_S1_DC1_CURR = config_dict[arrayRow1[11]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC1_CURR.setText(textEdit_S1_DC1_CURR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[12] in config_dict:
                            textEdit_S1_DC1_Voc = config_dict[arrayRow1[12]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC1_Voc.setText(textEdit_S1_DC1_Voc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[13] in config_dict:
                            textEdit_S1_DC1_Isc = config_dict[arrayRow1[13]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC1_Isc.setText(textEdit_S1_DC1_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[14] in config_dict:
                            textEdit_S1_DC1_PF = config_dict[arrayRow1[14]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC1_PF.setText(textEdit_S1_DC1_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[15] in config_dict:
                            checkBox_S1_DC2 = config_dict[arrayRow1[15]]
                            if checkBox_S1_DC2 == '1':
                                uiThaiCosPhiBrazil.checkBox_S1_DC2.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S1_DC2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[16] in config_dict:
                            comboBox_S1_DC2 = config_dict[arrayRow1[16]]
                            uiThaiCosPhiBrazil.comboBox_S1_DC2.setCurrentIndex(int(comboBox_S1_DC2))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[17] in config_dict:
                            textEdit_S1_DC2_VOLT = config_dict[arrayRow1[17]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC2_VOLT.setText(textEdit_S1_DC2_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[18] in config_dict:
                            textEdit_S1_DC2_CURR = config_dict[arrayRow1[18]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC2_CURR.setText(textEdit_S1_DC2_CURR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[19] in config_dict:
                            textEdit_S1_DC2_Voc = config_dict[arrayRow1[19]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC2_Voc.setText(textEdit_S1_DC2_Voc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[20] in config_dict:
                            textEdit_S1_DC2_Isc = config_dict[arrayRow1[20]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC2_Isc.setText(textEdit_S1_DC2_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[21] in config_dict:
                            textEdit_S1_DC2_PF = config_dict[arrayRow1[21]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC2_PF.setText(textEdit_S1_DC2_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[22] in config_dict:
                            checkBox_S1_DC3 = config_dict[arrayRow1[22]]
                            if checkBox_S1_DC3 == '1':
                                uiThaiCosPhiBrazil.checkBox_S1_DC3.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S1_DC3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[23] in config_dict:
                            comboBox_S1_DC3 = config_dict[arrayRow1[23]]
                            uiThaiCosPhiBrazil.comboBox_S1_DC3.setCurrentIndex(int(comboBox_S1_DC3))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[24] in config_dict:
                            textEdit_S1_DC3_VOLT = config_dict[arrayRow1[24]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC3_VOLT.setText(textEdit_S1_DC3_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[25] in config_dict:
                            textEdit_S1_DC3_CURR = config_dict[arrayRow1[25]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC3_CURR.setText(textEdit_S1_DC3_CURR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[26] in config_dict:
                            textEdit_S1_DC3_Voc = config_dict[arrayRow1[26]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC3_Voc.setText(textEdit_S1_DC3_Voc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[27] in config_dict:
                            textEdit_S1_DC3_Isc = config_dict[arrayRow1[27]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC3_Isc.setText(textEdit_S1_DC3_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[28] in config_dict:
                            textEdit_S1_DC3_PF = config_dict[arrayRow1[28]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC3_PF.setText(textEdit_S1_DC3_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[29] in config_dict:
                            checkBox_S1_DC4 = config_dict[arrayRow1[29]]
                            if checkBox_S1_DC4 == '1':
                                uiThaiCosPhiBrazil.checkBox_S1_DC4.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S1_DC4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[30] in config_dict:
                            comboBox_S1_DC4 = config_dict[arrayRow1[30]]
                            uiThaiCosPhiBrazil.comboBox_S1_DC4.setCurrentIndex(int(comboBox_S1_DC4))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[31] in config_dict:
                            textEdit_S1_DC4_VOLT = config_dict[arrayRow1[31]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC4_VOLT.setText(textEdit_S1_DC4_VOLT)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[32] in config_dict:
                            textEdit_S1_DC4_CURR = config_dict[arrayRow1[32]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC4_CURR.setText(textEdit_S1_DC4_CURR)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[33] in config_dict:
                            textEdit_S1_DC4_Voc = config_dict[arrayRow1[33]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC4_Voc.setText(textEdit_S1_DC4_Voc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[34] in config_dict:
                            textEdit_S1_DC4_Isc = config_dict[arrayRow1[34]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC4_Isc.setText(textEdit_S1_DC4_Isc)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[35] in config_dict:
                            textEdit_S1_DC4_PF = config_dict[arrayRow1[35]]
                            uiThaiCosPhiBrazil.textEdit_S1_DC4_PF.setText(textEdit_S1_DC4_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[36] in config_dict:
                            textEdit_S1_ACWaitTIME = config_dict[arrayRow1[36]]
                            uiThaiCosPhiBrazil.textEdit_S1_ACWaitTIME.setText(textEdit_S1_ACWaitTIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[37] in config_dict:
                            comboBox_S1_ACWaitTIME = config_dict[arrayRow1[37]]
                            uiThaiCosPhiBrazil.comboBox_S1_ACWaitTIME.setCurrentIndex(int(comboBox_S1_ACWaitTIME))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[38] in config_dict:
                            textEdit_S1_TIME = config_dict[arrayRow1[38]]
                            uiThaiCosPhiBrazil.textEdit_S1_TIME.setText(textEdit_S1_TIME)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[39] in config_dict:
                            comboBox_S1_TIME = config_dict[arrayRow1[39]]
                            uiThaiCosPhiBrazil.comboBox_S1_TIME.setCurrentIndex(int(comboBox_S1_TIME))
                        else:
                            strFlag = 1
                    
                    # step2
                    if strFlag == "0":
                        if arrayRow1[40] in config_dict:
                            checkBox_S2 = config_dict[arrayRow1[40]]
                            if checkBox_S2 == '1':
                                uiThaiCosPhiBrazil.checkBox_S2.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[41] in config_dict:
                            checkBox_S2_WT3000 = config_dict[arrayRow1[41]]
                            if checkBox_S2_WT3000 == '1':
                                uiThaiCosPhiBrazil.checkBox_S2_WT3000.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S2_WT3000.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[42] in config_dict:
                            checkBox_S2_WT1800 = config_dict[arrayRow1[42]]
                            if checkBox_S2_WT1800 == '1':
                                uiThaiCosPhiBrazil.checkBox_S2_WT1800.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S2_WT1800.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[43] in config_dict:
                            checkBox_S2_WT1806E = config_dict[arrayRow1[43]]
                            if checkBox_S2_WT1806E == '1':
                                uiThaiCosPhiBrazil.checkBox_S2_WT1806E.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S2_WT1806E.setChecked(False)
                        else:
                            strFlag = 1

                    # step3
                    if strFlag == "0":
                        if arrayRow1[44] in config_dict:
                            checkBox_S3 = config_dict[arrayRow1[44]]
                            if checkBox_S3 == '1':
                                uiThaiCosPhiBrazil.checkBox_S3.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[45] in config_dict:
                            checkBox_S3_DC1 = config_dict[arrayRow1[45]]
                            if checkBox_S3_DC1 == '1':
                                uiThaiCosPhiBrazil.checkBox_S3_DC1.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S3_DC1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[46] in config_dict:
                            checkBox_S3_DC2 = config_dict[arrayRow1[46]]
                            if checkBox_S3_DC2 == '1':
                                uiThaiCosPhiBrazil.checkBox_S3_DC2.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S3_DC2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[47] in config_dict:
                            checkBox_S3_DC3 = config_dict[arrayRow1[47]]
                            if checkBox_S3_DC3 == '1':
                                uiThaiCosPhiBrazil.checkBox_S3_DC3.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S3_DC3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[48] in config_dict:
                            checkBox_S3_DC4 = config_dict[arrayRow1[48]]
                            if checkBox_S3_DC4 == '1':
                                uiThaiCosPhiBrazil.checkBox_S3_DC4.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S3_DC4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[49] in config_dict:
                            textEdit_S3_DC_PF = config_dict[arrayRow1[49]]
                            uiThaiCosPhiBrazil.textEdit_S3_DC_PF.setText(textEdit_S3_DC_PF)
                        else:
                            strFlag = 1

                    # step4
                    if strFlag == "0":
                        if arrayRow1[50] in config_dict:
                            checkBox_S4 = config_dict[arrayRow1[50]]
                            if checkBox_S4 == '1':
                                uiThaiCosPhiBrazil.checkBox_S4.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[51] in config_dict:
                            checkBox_S4_DC1 = config_dict[arrayRow1[51]]
                            if checkBox_S4_DC1 == '1':
                                uiThaiCosPhiBrazil.checkBox_S4_DC1.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S4_DC1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[52] in config_dict:
                            checkBox_S4_DC2 = config_dict[arrayRow1[52]]
                            if checkBox_S4_DC2 == '1':
                                uiThaiCosPhiBrazil.checkBox_S4_DC2.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S4_DC2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[53] in config_dict:
                            checkBox_S4_DC3 = config_dict[arrayRow1[53]]
                            if checkBox_S4_DC3 == '1':
                                uiThaiCosPhiBrazil.checkBox_S4_DC3.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S4_DC3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[54] in config_dict:
                            checkBox_S4_DC4 = config_dict[arrayRow1[54]]
                            if checkBox_S4_DC4 == '1':
                                uiThaiCosPhiBrazil.checkBox_S4_DC4.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S4_DC4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[55] in config_dict:
                            textEdit_S4_DC_PF = config_dict[arrayRow1[55]]
                            uiThaiCosPhiBrazil.textEdit_S4_DC_PF.setText(textEdit_S4_DC_PF)
                        else:
                            strFlag = 1
                    
                    # step5
                    if strFlag == "0":
                        if arrayRow1[56] in config_dict:
                            checkBox_S5 = config_dict[arrayRow1[56]]
                            if checkBox_S5 == '1':
                                uiThaiCosPhiBrazil.checkBox_S5.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S5.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[57] in config_dict:
                            checkBox_S5_DC1 = config_dict[arrayRow1[57]]
                            if checkBox_S5_DC1 == '1':
                                uiThaiCosPhiBrazil.checkBox_S5_DC1.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S5_DC1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[58] in config_dict:
                            checkBox_S5_DC2 = config_dict[arrayRow1[58]]
                            if checkBox_S5_DC2 == '1':
                                uiThaiCosPhiBrazil.checkBox_S5_DC2.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S5_DC2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[59] in config_dict:
                            checkBox_S5_DC3 = config_dict[arrayRow1[59]]
                            if checkBox_S5_DC3 == '1':
                                uiThaiCosPhiBrazil.checkBox_S5_DC3.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S5_DC3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[60] in config_dict:
                            checkBox_S5_DC4 = config_dict[arrayRow1[60]]
                            if checkBox_S5_DC4 == '1':
                                uiThaiCosPhiBrazil.checkBox_S5_DC4.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S5_DC4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[61] in config_dict:
                            textEdit_S5_DC_PF = config_dict[arrayRow1[61]]
                            uiThaiCosPhiBrazil.textEdit_S5_DC_PF.setText(textEdit_S5_DC_PF)
                        else:
                            strFlag = 1

                    # step6
                    if strFlag == "0":
                        if arrayRow1[62] in config_dict:
                            checkBox_S6 = config_dict[arrayRow1[62]]
                            if checkBox_S6 == '1':
                                uiThaiCosPhiBrazil.checkBox_S6.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S6.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[63] in config_dict:
                            checkBox_S6_DC1 = config_dict[arrayRow1[63]]
                            if checkBox_S6_DC1 == '1':
                                uiThaiCosPhiBrazil.checkBox_S6_DC1.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S6_DC1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[64] in config_dict:
                            checkBox_S6_DC2 = config_dict[arrayRow1[64]]
                            if checkBox_S6_DC2 == '1':
                                uiThaiCosPhiBrazil.checkBox_S6_DC2.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S6_DC2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[65] in config_dict:
                            checkBox_S6_DC3 = config_dict[arrayRow1[65]]
                            if checkBox_S6_DC3 == '1':
                                uiThaiCosPhiBrazil.checkBox_S6_DC3.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S6_DC3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[66] in config_dict:
                            checkBox_S6_DC4 = config_dict[arrayRow1[66]]
                            if checkBox_S6_DC4 == '1':
                                uiThaiCosPhiBrazil.checkBox_S6_DC4.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S6_DC4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[67] in config_dict:
                            textEdit_S6_DC_PF = config_dict[arrayRow1[67]]
                            uiThaiCosPhiBrazil.textEdit_S6_DC_PF.setText(textEdit_S6_DC_PF)
                        else:
                            strFlag = 1

                    # step7
                    if strFlag == "0":
                        if arrayRow1[68] in config_dict:
                            checkBox_S7 = config_dict[arrayRow1[68]]
                            if checkBox_S7 == '1':
                                uiThaiCosPhiBrazil.checkBox_S7.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S7.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[69] in config_dict:
                            checkBox_S7_DC1 = config_dict[arrayRow1[69]]
                            if checkBox_S7_DC1 == '1':
                                uiThaiCosPhiBrazil.checkBox_S7_DC1.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S7_DC1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[70] in config_dict:
                            checkBox_S7_DC2 = config_dict[arrayRow1[70]]
                            if checkBox_S7_DC2 == '1':
                                uiThaiCosPhiBrazil.checkBox_S7_DC2.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S7_DC2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[71] in config_dict:
                            checkBox_S7_DC3 = config_dict[arrayRow1[71]]
                            if checkBox_S7_DC3 == '1':
                                uiThaiCosPhiBrazil.checkBox_S7_DC3.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S7_DC3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[72] in config_dict:
                            checkBox_S7_DC4 = config_dict[arrayRow1[72]]
                            if checkBox_S7_DC4 == '1':
                                uiThaiCosPhiBrazil.checkBox_S7_DC4.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S7_DC4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[73] in config_dict:
                            textEdit_S7_DC_PF = config_dict[arrayRow1[73]]
                            uiThaiCosPhiBrazil.textEdit_S7_DC_PF.setText(textEdit_S7_DC_PF)
                        else:
                            strFlag = 1

                    # step8
                    if strFlag == "0":
                        if arrayRow1[74] in config_dict:
                            checkBox_S8 = config_dict[arrayRow1[74]]
                            if checkBox_S8 == '1':
                                uiThaiCosPhiBrazil.checkBox_S8.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S8.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[75] in config_dict:
                            checkBox_S8_DC1 = config_dict[arrayRow1[75]]
                            if checkBox_S8_DC1 == '1':
                                uiThaiCosPhiBrazil.checkBox_S8_DC1.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S8_DC1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[76] in config_dict:
                            checkBox_S8_DC2 = config_dict[arrayRow1[76]]
                            if checkBox_S8_DC2 == '1':
                                uiThaiCosPhiBrazil.checkBox_S8_DC2.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S8_DC2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[77] in config_dict:
                            checkBox_S8_DC3 = config_dict[arrayRow1[77]]
                            if checkBox_S8_DC3 == '1':
                                uiThaiCosPhiBrazil.checkBox_S8_DC3.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S8_DC3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[78] in config_dict:
                            checkBox_S8_DC4 = config_dict[arrayRow1[78]]
                            if checkBox_S8_DC4 == '1':
                                uiThaiCosPhiBrazil.checkBox_S8_DC4.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S8_DC4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[79] in config_dict:
                            textEdit_S8_DC_PF = config_dict[arrayRow1[79]]
                            uiThaiCosPhiBrazil.textEdit_S8_DC_PF.setText(textEdit_S8_DC_PF)
                        else:
                            strFlag = 1

                    # step9
                    if strFlag == "0":
                        if arrayRow1[80] in config_dict:
                            checkBox_S9 = config_dict[arrayRow1[80]]
                            if checkBox_S9 == '1':
                                uiThaiCosPhiBrazil.checkBox_S9.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S9.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[81] in config_dict:
                            checkBox_S9_AC_Check = config_dict[arrayRow1[81]]
                            if checkBox_S9_AC_Check == '1':
                                uiThaiCosPhiBrazil.checkBox_S9_AC_Check.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S9_AC_Check.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[82] in config_dict:
                            textEdit_S9_AC_Volt = config_dict[arrayRow1[82]]
                            uiThaiCosPhiBrazil.textEdit_S9_AC_Volt.setText(textEdit_S9_AC_Volt)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[83] in config_dict:
                            checkBox_S9_DC1 = config_dict[arrayRow1[83]]
                            if checkBox_S9_DC1 == '1':
                                uiThaiCosPhiBrazil.checkBox_S9_DC1.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S9_DC1.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[84] in config_dict:
                            checkBox_S9_DC2 = config_dict[arrayRow1[84]]
                            if checkBox_S9_DC2 == '1':
                                uiThaiCosPhiBrazil.checkBox_S9_DC2.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S9_DC2.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[85] in config_dict:
                            checkBox_S9_DC3 = config_dict[arrayRow1[85]]
                            if checkBox_S9_DC3 == '1':
                                uiThaiCosPhiBrazil.checkBox_S9_DC3.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S9_DC3.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[86] in config_dict:
                            checkBox_S9_DC4 = config_dict[arrayRow1[86]]
                            if checkBox_S9_DC4 == '1':
                                uiThaiCosPhiBrazil.checkBox_S9_DC4.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S9_DC4.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[87] in config_dict:
                            textEdit_S9_DC_PF = config_dict[arrayRow1[87]]
                            uiThaiCosPhiBrazil.textEdit_S9_DC_PF.setText(textEdit_S9_DC_PF)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[88] in config_dict:
                            textEdit_S3_TIME_2 = config_dict[arrayRow1[88]]
                            uiThaiCosPhiBrazil.textEdit_S3_TIME_2.setText(textEdit_S3_TIME_2)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[89] in config_dict:
                            comboBox_S3_TIME_2 = config_dict[arrayRow1[89]]
                            uiThaiCosPhiBrazil.comboBox_S3_TIME_2.setCurrentIndex(int(comboBox_S3_TIME_2))
                        else:
                            strFlag = 1
                    
                    # step_end
                    if strFlag == "0":
                        if arrayRow1[90] in config_dict:
                            checkBox_S_END = config_dict[arrayRow1[90]]
                            if checkBox_S_END == '1':
                                uiThaiCosPhiBrazil.checkBox_S_END.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S_END.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[91] in config_dict:
                            comboBox_S_END_AC = config_dict[arrayRow1[91]]
                            uiThaiCosPhiBrazil.comboBox_S_END_AC.setCurrentIndex(int(comboBox_S_END_AC))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[92] in config_dict:
                            checkBox_S_END_DC1 = config_dict[arrayRow1[92]]
                            if checkBox_S_END_DC1 == '1':
                                uiThaiCosPhiBrazil.checkBox_S_END_DC1.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S_END_DC1.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[93] in config_dict:
                            comboBox_S_END_DC1 = config_dict[arrayRow1[93]]
                            uiThaiCosPhiBrazil.comboBox_S_END_DC1.setCurrentIndex(int(comboBox_S_END_DC1))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[94] in config_dict:
                            checkBox_S_END_DC2 = config_dict[arrayRow1[94]]
                            if checkBox_S_END_DC2 == '1':
                                uiThaiCosPhiBrazil.checkBox_S_END_DC2.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S5_DC2.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[95] in config_dict:
                            comboBox_S_END_DC2 = config_dict[arrayRow1[95]]
                            uiThaiCosPhiBrazil.comboBox_S_END_DC2.setCurrentIndex(int(comboBox_S_END_DC2))
                        else:
                            strFlag = 1
                    if strFlag == "0":
                        if arrayRow1[96] in config_dict:
                            checkBox_S_END_DC3 = config_dict[arrayRow1[96]]
                            if checkBox_S_END_DC3 == '1':
                                uiThaiCosPhiBrazil.checkBox_S_END_DC3.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S_END_DC3.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[97] in config_dict:
                            comboBox_S_END_DC3 = config_dict[arrayRow1[97]]
                            uiThaiCosPhiBrazil.comboBox_S_END_DC3.setCurrentIndex(int(comboBox_S_END_DC3))
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[98] in config_dict:
                            checkBox_S_END_DC4 = config_dict[arrayRow1[98]]
                            if checkBox_S_END_DC4 == '1':
                                uiThaiCosPhiBrazil.checkBox_S_END_DC4.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S_END_DC4.setChecked(False)
                        else:
                            strFlag = 1
                    
                    if strFlag == "0":
                        if arrayRow1[99] in config_dict:
                            comboBox_S_END_DC4 = config_dict[arrayRow1[99]]
                            uiThaiCosPhiBrazil.comboBox_S_END_DC4.setCurrentIndex(int(comboBox_S_END_DC4))
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

                    if arrayRow1[43] in config_dict:
                        checkBox_S2_WT1806E = config_dict[arrayRow1[43]]
                        if checkBox_S2_WT1806E == '1':
                            Open_File_ThaiWT1806E_Config(uiThiaWT1806E, wt_config_dict)
                    else:
                        strFlag = 1

                    # wt5000
                    if strFlag == "0":
                        if arrayRow1[100] in config_dict:
                            checkBox_S2_WT5000 = config_dict[arrayRow1[100]]
                            if checkBox_S2_WT5000 == '1':
                                uiThaiCosPhiBrazil.checkBox_S2_WT5000.setChecked(True)
                            else:
                                uiThaiCosPhiBrazil.checkBox_S2_WT5000.setChecked(False)
                        else:
                            strFlag = 1

                    if arrayRow1[100] in config_dict:
                        checkBox_S2_WT5000 = config_dict[arrayRow1[100]]
                        if checkBox_S2_WT5000 == '1':
                            Open_File_ThaiWT5000_Config(uiThiaWT5000, wt_config_dict)
                    else:
                        strFlag = 1

        QMessageBox.information(NonecosPhiBrazil, "实验设定提示信息", "巴西Cos(φ)文件读取完成", QMessageBox.Ok, QMessageBox.Ok)

# def save_file_header():
#     directory1 = [r"D:\\project\\photovoltaic_automation_t\\config_files\\project_step_configs\\cosPhiBrazil.csv"]
#     if directory1[0] == '':
#         print('请选择一个文件')
#     else:
#         out = open(directory1[0], 'w+', newline='')
#         csv_write = csv.writer(out, dialect="excel")
#         csv_write.writerow(arrayRow1)
#         out.close()

# if __name__ == "__main__":
#     save_file_header()