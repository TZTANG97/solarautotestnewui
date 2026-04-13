from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, \
    QFileDialog, QMessageBox
import csv

#泰国过欠压保存设定
def Save_File_ThaiGuoQianYa(dialog_windowguoqianya, uithaiguoqianya):
    directory1 = QFileDialog.getSaveFileName(dialog_windowguoqianya, "单个文件保存", "./", "Text Files(*.csv)")
    if directory1[0] == '':
        print('请选择一个文件')
    else:
        arrayRow1 = ['Style', 'checkBox_S1',"checkBox_S2","checkBox_S3",
                     'comboBox_S1_AC','comboBox_S1_AC_2',"comboBox_S1_ACWaitTIME",
                     "comboBox_S1_DC1","comboBox_S1_DC2","comboBox_S1_DL850","comboBox_S1_TIME",
                     "comboBox_S2_WT3000_Setting","comboBox_S2_WT3000_S1","comboBox_S2_WT3000_S1_FR_TIME",
                     "comboBox_S2_WT300_STAYTIME","comboBox_S2_DL850","comboBox_S2_AC_FR_RAMP1_SPACETIME",
                     "comboBox_S2_AC_FR_RAMP2_SPACETIME","comboBox_S2_AC_FR_RAMP2_STAYTIME","comboBox_S2_WT3000_S2",
                     "comboBox_S2_TIME","comboBox_S3_DL850_S1","comboBox_S3_SPACETIME1","comboBox_S3_SPACETIME2",
                     "comboBox_S3_SPACETIME3","comboBox_S3_SPACETIME4","comboBox_S3_DL850_S2",
                     "textEdit_S1_AC_VOLT","textEdit_S1_AC_VOLT_2","textEdit_S1_AC_VOLT_3",
                     "textEdit_S1_AC_FR","textEdit_S1_ACWaitTIME","textEdit_S1_DC1_VOLT","textEdit_S1_DC1_CURR",
                     "textEdit_S1_DC2_VOLT","textEdit_S1_DC2_CURR","textEdit_S1_TIME","textEdit_S2_CYCLE_TIME",
                     "textEdit_S2_WT3000_S1_FR_TIME","textEdit_S2_WT300_STAYTIME","textEdit_S2_AC_VOLT_RAMP1_1_1",
                     "textEdit_S2_AC_VOLT_RAMP1_1_2","textEdit_S2_AC_VOLT_RAMP1_2_1","textEdit_S2_AC_VOLT_RAMP1_2_2",
                     "textEdit_S2_AC_VOLT_RAMP1_3_1","textEdit_S2_AC_VOLT_RAMP1_3_2","textEdit_S2_AC_VOLT_RAMP1_TIMES",
                     "textEdit_S2_AC_FR_RAMP1_SPACETIME","textEdit_S2_AC_FR_RAMP2_1_1","textEdit_S2_AC_FR_RAMP2_1_2",
                     "textEdit_S2_AC_FR_RAMP2_2_1","textEdit_S2_AC_FR_RAMP2_2_2","textEdit_S2_AC_FR_RAMP2_3_1",
                     "textEdit_S2_AC_FR_RAMP2_3_2","textEdit_S2_AC_FR_RAMP2_TIMES","textEdit_S2_AC_FR_RAMP2_SPACETIME",
                     "textEdit_S2_AC_FR_RAMP2_STAYTIME","textEdit_S2_AC_VOLT","textEdit_S2_AC_VOLT_2","textEdit_S2_AC_VOLT_3",
                     "textEdit_S2_AC_FR","textEdit_S2_TIME","textEdit_S3_CYCLE_TIME","textEdit_S3_AC_VOLT","textEdit_S3_AC_VOLT_2",
                     "textEdit_S3_AC_VOLT_3","textEdit_S3_AC_FR","textEdit_S3_SPACETIME1","textEdit_S3_AC_VOLT2",
                     "textEdit_S3_AC_VOLT2_2","textEdit_S3_AC_VOLT2_3","textEdit_S3_AC_FR_2","textEdit_S3_SPACETIME2",
                     "textEdit_S3_AC_VOLT3","textEdit_S3_AC_VOLT3_2","textEdit_S3_AC_VOLT3_3","textEdit_S3_AC_FR_3","textEdit_S3_SPACETIME3",
                     "textEdit_S3_AC_VOLT4", "textEdit_S3_AC_VOLT4_2", "textEdit_S3_AC_VOLT4_3", "textEdit_S3_AC_FR_4",
                     "textEdit_S3_SPACETIME4",
                     "checkBox_S1_AC1","checkBox_S1_DC1","checkBox_S1_DC2","checkBox_S1_DC3","checkBox_S1_DL850",
                     "checkBox_S2_WT3000","checkBox_S2_DL850","checkBox_S2_AC1_1","checkBox_S2_AC1_2","checkBox_S2_WT3000_2",
                     "checkBox_S2_AC1_3","checkBox_S3_DL850_1","checkBox_S3_AC1_1","checkBox_S3_AC1_2","checkBox_S3_AC1_3",
                     "checkBox_S3_AC1_4","checkBox_S3_DL850_2","checkBox_S4","checkBox_S4_AC1_1","checkBox_S4_DC1_1",
                     "checkBox_S4_DC2_1","checkBox_S4_DC3_1",
                     "comboBox_S1_DC3","comboBox_S4_AC1_1","comboBox_S4_DC1_1","comboBox_S4_DC2_1","comboBox_S4_DC3_1",
                     "textEdit_S1_DC1_Voc","textEdit_S1_DC1_Isc","textEdit_S1_DC1_PF",
                     "textEdit_S1_DC2_Voc","textEdit_S1_DC2_Isc","textEdit_S1_DC2_PF",
                     "textEdit_S1_DC3_VOLT","textEdit_S1_DC3_CURR",
                     "textEdit_S1_DC3_Voc","textEdit_S1_DC3_Isc","textEdit_S1_DC3_PF"]

        arrayRow2 = ['ThaiGuoQianYa']

        if uithaiguoqianya.checkBox_S1.isChecked():
            checkBox_S1 = '1'
        else:
            checkBox_S1 = '0'
        arrayRow2.append(checkBox_S1)

        if uithaiguoqianya.checkBox_S2.isChecked():
            checkBox_S2 = '1'
        else:
            checkBox_S2 = '0'
        arrayRow2.append(checkBox_S2)

        if uithaiguoqianya.checkBox_S3.isChecked():
            checkBox_S3 = '1'
        else:
            checkBox_S3 = '0'
        arrayRow2.append(checkBox_S3)

        comboBox_S1_AC = uithaiguoqianya.comboBox_S1_AC.currentIndex()
        arrayRow2.append(comboBox_S1_AC)

        comboBox_S1_AC_2 = uithaiguoqianya.comboBox_S1_AC_2.currentIndex()
        arrayRow2.append(comboBox_S1_AC_2)

        comboBox_S1_ACWaitTIME = uithaiguoqianya.comboBox_S1_ACWaitTIME.currentIndex()
        arrayRow2.append(comboBox_S1_ACWaitTIME)

        comboBox_S1_DC1 = uithaiguoqianya.comboBox_S1_DC1.currentIndex()
        arrayRow2.append(comboBox_S1_DC1)

        comboBox_S1_DC2 = uithaiguoqianya.comboBox_S1_DC2.currentIndex()
        arrayRow2.append(comboBox_S1_DC2)

        comboBox_S1_DL850 = uithaiguoqianya.comboBox_S1_DL850.currentIndex()
        arrayRow2.append(comboBox_S1_DL850)

        comboBox_S1_TIME = uithaiguoqianya.comboBox_S1_TIME.currentIndex()
        arrayRow2.append(comboBox_S1_TIME)

        comboBox_S2_WT3000_Setting = uithaiguoqianya.comboBox_S2_WT3000_Setting.currentIndex()
        arrayRow2.append(comboBox_S2_WT3000_Setting)

        comboBox_S2_WT3000_S1 = uithaiguoqianya.comboBox_S2_WT3000_S1.currentIndex()
        arrayRow2.append(comboBox_S2_WT3000_S1)

        comboBox_S2_WT3000_S1_FR_TIME = uithaiguoqianya.comboBox_S2_WT3000_S1_FR_TIME.currentIndex()
        arrayRow2.append(comboBox_S2_WT3000_S1_FR_TIME)

        comboBox_S2_WT300_STAYTIME = uithaiguoqianya.comboBox_S2_WT300_STAYTIME.currentIndex()
        arrayRow2.append(comboBox_S2_WT300_STAYTIME)

        comboBox_S2_DL850 = uithaiguoqianya.comboBox_S2_DL850.currentIndex()
        arrayRow2.append(comboBox_S2_DL850)

        comboBox_S2_AC_FR_RAMP1_SPACETIME = uithaiguoqianya.comboBox_S2_AC_FR_RAMP1_SPACETIME.currentIndex()
        arrayRow2.append(comboBox_S2_AC_FR_RAMP1_SPACETIME)

        comboBox_S2_AC_FR_RAMP2_SPACETIME = uithaiguoqianya.comboBox_S2_AC_FR_RAMP2_SPACETIME.currentIndex()
        arrayRow2.append(comboBox_S2_AC_FR_RAMP2_SPACETIME)

        comboBox_S2_AC_FR_RAMP2_STAYTIME = uithaiguoqianya.comboBox_S2_AC_FR_RAMP2_STAYTIME.currentIndex()
        arrayRow2.append(comboBox_S2_AC_FR_RAMP2_STAYTIME)

        comboBox_S2_WT3000_S2 = uithaiguoqianya.comboBox_S2_WT3000_S2.currentIndex()
        arrayRow2.append(comboBox_S2_WT3000_S2)

        comboBox_S2_TIME = uithaiguoqianya.comboBox_S2_TIME.currentIndex()
        arrayRow2.append(comboBox_S2_TIME)

        comboBox_S3_DL850_S1 = uithaiguoqianya.comboBox_S3_DL850_S1.currentIndex()
        arrayRow2.append(comboBox_S3_DL850_S1)

        comboBox_S3_SPACETIME1 = uithaiguoqianya.comboBox_S3_SPACETIME1.currentIndex()
        arrayRow2.append(comboBox_S3_SPACETIME1)

        comboBox_S3_SPACETIME2 = uithaiguoqianya.comboBox_S3_SPACETIME2.currentIndex()
        arrayRow2.append(comboBox_S3_SPACETIME2)

        comboBox_S3_SPACETIME3 = uithaiguoqianya.comboBox_S3_SPACETIME3.currentIndex()
        arrayRow2.append(comboBox_S3_SPACETIME3)

        comboBox_S3_SPACETIME4 = uithaiguoqianya.comboBox_S3_SPACETIME4.currentIndex()
        arrayRow2.append(comboBox_S3_SPACETIME4)

        comboBox_S3_DL850_S2 = uithaiguoqianya.comboBox_S3_DL850_S2.currentIndex()
        arrayRow2.append(comboBox_S3_DL850_S2)

        textEdit_S1_AC_VOLT = uithaiguoqianya.textEdit_S1_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT)

        textEdit_S1_AC_VOLT_2 = uithaiguoqianya.textEdit_S1_AC_VOLT_2.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_2)

        textEdit_S1_AC_VOLT_3 = uithaiguoqianya.textEdit_S1_AC_VOLT_3.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_3)

        textEdit_S1_AC_FR = uithaiguoqianya.textEdit_S1_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S1_AC_FR)

        textEdit_S1_ACWaitTIME = uithaiguoqianya.textEdit_S1_ACWaitTIME.toPlainText()
        arrayRow2.append(textEdit_S1_ACWaitTIME)

        textEdit_S1_DC1_VOLT = uithaiguoqianya.textEdit_S1_DC1_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_VOLT)

        textEdit_S1_DC1_CURR = uithaiguoqianya.textEdit_S1_DC1_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_CURR)

        textEdit_S1_DC2_VOLT = uithaiguoqianya.textEdit_S1_DC2_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_VOLT)

        textEdit_S1_DC2_CURR = uithaiguoqianya.textEdit_S1_DC2_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_CURR)

        textEdit_S1_TIME = uithaiguoqianya.textEdit_S1_TIME.toPlainText()
        arrayRow2.append(textEdit_S1_TIME)

        textEdit_S2_CYCLE_TIME = uithaiguoqianya.textEdit_S2_CYCLE_TIME.toPlainText()
        arrayRow2.append(textEdit_S2_CYCLE_TIME)

        textEdit_S2_WT3000_S1_FR_TIME = uithaiguoqianya.textEdit_S2_WT3000_S1_FR_TIME.toPlainText()
        arrayRow2.append(textEdit_S2_WT3000_S1_FR_TIME)

        textEdit_S2_WT300_STAYTIME = uithaiguoqianya.textEdit_S2_WT300_STAYTIME.toPlainText()
        arrayRow2.append(textEdit_S2_WT300_STAYTIME)

        textEdit_S2_AC_VOLT_RAMP1_1_1 = uithaiguoqianya.textEdit_S2_AC_VOLT_RAMP1_1_1.toPlainText()
        arrayRow2.append(textEdit_S2_AC_VOLT_RAMP1_1_1)

        textEdit_S2_AC_VOLT_RAMP1_1_2 = uithaiguoqianya.textEdit_S2_AC_VOLT_RAMP1_1_2.toPlainText()
        arrayRow2.append(textEdit_S2_AC_VOLT_RAMP1_1_2)

        textEdit_S2_AC_VOLT_RAMP1_2_1 = uithaiguoqianya.textEdit_S2_AC_VOLT_RAMP1_2_1.toPlainText()
        arrayRow2.append(textEdit_S2_AC_VOLT_RAMP1_2_1)

        textEdit_S2_AC_VOLT_RAMP1_2_2 = uithaiguoqianya.textEdit_S2_AC_VOLT_RAMP1_2_2.toPlainText()
        arrayRow2.append(textEdit_S2_AC_VOLT_RAMP1_2_2)

        textEdit_S2_AC_VOLT_RAMP1_3_1 = uithaiguoqianya.textEdit_S2_AC_VOLT_RAMP1_3_1.toPlainText()
        arrayRow2.append(textEdit_S2_AC_VOLT_RAMP1_3_1)

        textEdit_S2_AC_VOLT_RAMP1_3_2 = uithaiguoqianya.textEdit_S2_AC_VOLT_RAMP1_3_2.toPlainText()
        arrayRow2.append(textEdit_S2_AC_VOLT_RAMP1_3_2)

        textEdit_S2_AC_VOLT_RAMP1_TIMES = uithaiguoqianya.textEdit_S2_AC_VOLT_RAMP1_TIMES.toPlainText()
        arrayRow2.append(textEdit_S2_AC_VOLT_RAMP1_TIMES)

        textEdit_S2_AC_FR_RAMP1_SPACETIME = uithaiguoqianya.textEdit_S2_AC_FR_RAMP1_SPACETIME.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP1_SPACETIME)

        textEdit_S2_AC_FR_RAMP2_1_1 = uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_1_1.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP2_1_1)

        textEdit_S2_AC_FR_RAMP2_1_2 = uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_1_2.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP2_1_2)

        textEdit_S2_AC_FR_RAMP2_2_1 = uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_2_1.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP2_2_1)

        textEdit_S2_AC_FR_RAMP2_2_2 = uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_2_2.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP2_2_2)

        textEdit_S2_AC_FR_RAMP2_3_1 = uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_3_1.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP2_3_1)

        textEdit_S2_AC_FR_RAMP2_3_2 = uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_3_2.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP2_3_2)

        textEdit_S2_AC_FR_RAMP2_TIMES = uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_TIMES.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP2_TIMES)

        textEdit_S2_AC_FR_RAMP2_SPACETIME = uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_SPACETIME.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP2_SPACETIME)

        textEdit_S2_AC_FR_RAMP2_STAYTIME = uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_STAYTIME.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP2_STAYTIME)

        textEdit_S2_AC_VOLT = uithaiguoqianya.textEdit_S2_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S2_AC_VOLT)

        textEdit_S2_AC_VOLT_2 = uithaiguoqianya.textEdit_S2_AC_VOLT_2.toPlainText()
        arrayRow2.append(textEdit_S2_AC_VOLT_2)

        textEdit_S2_AC_VOLT_3 = uithaiguoqianya.textEdit_S2_AC_VOLT_3.toPlainText()
        arrayRow2.append(textEdit_S2_AC_VOLT_3)

        textEdit_S2_AC_FR = uithaiguoqianya.textEdit_S2_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR)

        textEdit_S2_TIME = uithaiguoqianya.textEdit_S2_TIME.toPlainText()
        arrayRow2.append(textEdit_S2_TIME)

        textEdit_S3_CYCLE_TIME = uithaiguoqianya.textEdit_S3_CYCLE_TIME.toPlainText()
        arrayRow2.append(textEdit_S3_CYCLE_TIME)

        textEdit_S3_AC_VOLT = uithaiguoqianya.textEdit_S3_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT)

        textEdit_S3_AC_VOLT_2 = uithaiguoqianya.textEdit_S3_AC_VOLT_2.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT_2)

        textEdit_S3_AC_VOLT_3 = uithaiguoqianya.textEdit_S3_AC_VOLT_3.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT_3)

        textEdit_S3_AC_FR = uithaiguoqianya.textEdit_S3_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S3_AC_FR)

        textEdit_S3_SPACETIME1 = uithaiguoqianya.textEdit_S3_SPACETIME1.toPlainText()
        arrayRow2.append(textEdit_S3_SPACETIME1)

        textEdit_S3_AC_VOLT2 = uithaiguoqianya.textEdit_S3_AC_VOLT2.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT2)

        textEdit_S3_AC_VOLT2_2 = uithaiguoqianya.textEdit_S3_AC_VOLT2_2.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT2_2)

        textEdit_S3_AC_VOLT2_3 = uithaiguoqianya.textEdit_S3_AC_VOLT2_3.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT2_3)

        textEdit_S3_AC_FR_2 = uithaiguoqianya.textEdit_S3_AC_FR_2.toPlainText()
        arrayRow2.append(textEdit_S3_AC_FR_2)

        textEdit_S3_SPACETIME2 = uithaiguoqianya.textEdit_S3_SPACETIME2.toPlainText()
        arrayRow2.append(textEdit_S3_SPACETIME2)

        textEdit_S3_AC_VOLT3 = uithaiguoqianya.textEdit_S3_AC_VOLT3.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT3)

        textEdit_S3_AC_VOLT3_2 = uithaiguoqianya.textEdit_S3_AC_VOLT3_2.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT3_2)

        textEdit_S3_AC_VOLT3_3 = uithaiguoqianya.textEdit_S3_AC_VOLT3_3.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT3_3)

        textEdit_S3_AC_FR_3 = uithaiguoqianya.textEdit_S3_AC_FR_3.toPlainText()
        arrayRow2.append(textEdit_S3_AC_FR_3)

        textEdit_S3_SPACETIME3 = uithaiguoqianya.textEdit_S3_SPACETIME3.toPlainText()
        arrayRow2.append(textEdit_S3_SPACETIME3)

        textEdit_S3_AC_VOLT4 = uithaiguoqianya.textEdit_S3_AC_VOLT4.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT4)

        textEdit_S3_AC_VOLT4_2 = uithaiguoqianya.textEdit_S3_AC_VOLT4_2.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT4_2)

        textEdit_S3_AC_VOLT4_3 = uithaiguoqianya.textEdit_S3_AC_VOLT4_3.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT4_3)

        textEdit_S3_AC_FR_4 = uithaiguoqianya.textEdit_S3_AC_FR_4.toPlainText()
        arrayRow2.append(textEdit_S3_AC_FR_4)

        textEdit_S3_SPACETIME4 = uithaiguoqianya.textEdit_S3_SPACETIME4.toPlainText()
        arrayRow2.append(textEdit_S3_SPACETIME4)


        if uithaiguoqianya.checkBox_S1_AC1.isChecked():
            checkBox_S1_AC1 = '1'
        else:
            checkBox_S1_AC1 = '0'
        arrayRow2.append(checkBox_S1_AC1)

        if uithaiguoqianya.checkBox_S1_DC1.isChecked():
            checkBox_S1_DC1 = '1'
        else:
            checkBox_S1_DC1 = '0'
        arrayRow2.append(checkBox_S1_DC1)

        if uithaiguoqianya.checkBox_S1_DC2.isChecked():
            checkBox_S1_DC2 = '1'
        else:
            checkBox_S1_DC2 = '0'
        arrayRow2.append(checkBox_S1_DC2)

        if uithaiguoqianya.checkBox_S1_DC3.isChecked():
            checkBox_S1_DC3 = '1'
        else:
            checkBox_S1_DC3 = '0'
        arrayRow2.append(checkBox_S1_DC3)

        if uithaiguoqianya.checkBox_S1_DL850.isChecked():
            checkBox_S1_DL850 = '1'
        else:
            checkBox_S1_DL850 = '0'
        arrayRow2.append(checkBox_S1_DL850)

        if uithaiguoqianya.checkBox_S2_WT3000.isChecked():
            checkBox_S2_WT3000 = '1'
        else:
            checkBox_S2_WT3000 = '0'
        arrayRow2.append(checkBox_S2_WT3000)

        if uithaiguoqianya.checkBox_S2_DL850.isChecked():
            checkBox_S2_DL850 = '1'
        else:
            checkBox_S2_DL850 = '0'
        arrayRow2.append(checkBox_S2_DL850)

        if uithaiguoqianya.checkBox_S2_AC1_1.isChecked():
            checkBox_S2_AC1_1 = '1'
        else:
            checkBox_S2_AC1_1 = '0'
        arrayRow2.append(checkBox_S2_AC1_1)

        if uithaiguoqianya.checkBox_S2_AC1_2.isChecked():
            checkBox_S2_AC1_2 = '1'
        else:
            checkBox_S2_AC1_2 = '0'
        arrayRow2.append(checkBox_S2_AC1_2)

        if uithaiguoqianya.checkBox_S2_WT3000_2.isChecked():
            checkBox_S2_WT3000_2 = '1'
        else:
            checkBox_S2_WT3000_2 = '0'
        arrayRow2.append(checkBox_S2_WT3000_2)

        if uithaiguoqianya.checkBox_S2_AC1_3.isChecked():
            checkBox_S2_AC1_3 = '1'
        else:
            checkBox_S2_AC1_3 = '0'
        arrayRow2.append(checkBox_S2_AC1_3)

        if uithaiguoqianya.checkBox_S3_DL850_1.isChecked():
            checkBox_S3_DL850_1 = '1'
        else:
            checkBox_S3_DL850_1 = '0'
        arrayRow2.append(checkBox_S3_DL850_1)

        if uithaiguoqianya.checkBox_S3_AC1_1.isChecked():
            checkBox_S3_AC1_1 = '1'
        else:
            checkBox_S3_AC1_1 = '0'
        arrayRow2.append(checkBox_S3_AC1_1)

        if uithaiguoqianya.checkBox_S3_AC1_2.isChecked():
            checkBox_S3_AC1_2 = '1'
        else:
            checkBox_S3_AC1_2 = '0'
        arrayRow2.append(checkBox_S3_AC1_2)

        if uithaiguoqianya.checkBox_S3_AC1_3.isChecked():
            checkBox_S3_AC1_3 = '1'
        else:
            checkBox_S3_AC1_3 = '0'
        arrayRow2.append(checkBox_S3_AC1_3)

        if uithaiguoqianya.checkBox_S3_AC1_4.isChecked():
            checkBox_S3_AC1_4 = '1'
        else:
            checkBox_S3_AC1_4 = '0'
        arrayRow2.append(checkBox_S3_AC1_4)

        if uithaiguoqianya.checkBox_S3_DL850_2.isChecked():
            checkBox_S3_DL850_2 = '1'
        else:
            checkBox_S3_DL850_2 = '0'
        arrayRow2.append(checkBox_S3_DL850_2)

        if uithaiguoqianya.checkBox_S4.isChecked():
            checkBox_S4 = '1'
        else:
            checkBox_S4 = '0'
        arrayRow2.append(checkBox_S4)

        if uithaiguoqianya.checkBox_S4_AC1_1.isChecked():
            checkBox_S4_AC1_1 = '1'
        else:
            checkBox_S4_AC1_1 = '0'
        arrayRow2.append(checkBox_S4_AC1_1)

        if uithaiguoqianya.checkBox_S4_DC1_1.isChecked():
            checkBox_S4_DC1_1 = '1'
        else:
            checkBox_S4_DC1_1 = '0'
        arrayRow2.append(checkBox_S4_DC1_1)

        if uithaiguoqianya.checkBox_S4_DC2_1.isChecked():
            checkBox_S4_DC2_1 = '1'
        else:
            checkBox_S4_DC2_1 = '0'
        arrayRow2.append(checkBox_S4_DC2_1)

        if uithaiguoqianya.checkBox_S4_DC3_1.isChecked():
            checkBox_S4_DC3_1 = '1'
        else:
            checkBox_S4_DC3_1 = '0'
        arrayRow2.append(checkBox_S4_DC3_1)


        comboBox_S1_DC3 = uithaiguoqianya.comboBox_S1_DC3.currentIndex()
        arrayRow2.append(comboBox_S1_DC3)

        comboBox_S4_AC1_1 = uithaiguoqianya.comboBox_S4_AC1_1.currentIndex()
        arrayRow2.append(comboBox_S4_AC1_1)

        comboBox_S4_DC1_1 = uithaiguoqianya.comboBox_S4_DC1_1.currentIndex()
        arrayRow2.append(comboBox_S4_DC1_1)

        comboBox_S4_DC2_1 = uithaiguoqianya.comboBox_S4_DC2_1.currentIndex()
        arrayRow2.append(comboBox_S4_DC2_1)

        comboBox_S4_DC3_1 = uithaiguoqianya.comboBox_S4_DC3_1.currentIndex()
        arrayRow2.append(comboBox_S4_DC3_1)


        textEdit_S1_DC1_Voc = uithaiguoqianya.textEdit_S1_DC1_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Voc)

        textEdit_S1_DC1_Isc = uithaiguoqianya.textEdit_S1_DC1_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Isc)

        textEdit_S1_DC1_PF = uithaiguoqianya.textEdit_S1_DC1_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF)

        textEdit_S1_DC2_Voc = uithaiguoqianya.textEdit_S1_DC2_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Voc)

        textEdit_S1_DC2_Isc = uithaiguoqianya.textEdit_S1_DC2_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Isc)

        textEdit_S1_DC2_PF = uithaiguoqianya.textEdit_S1_DC2_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_PF)

        textEdit_S1_DC3_VOLT = uithaiguoqianya.textEdit_S1_DC3_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_VOLT)

        textEdit_S1_DC3_CURR = uithaiguoqianya.textEdit_S1_DC3_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_CURR)

        textEdit_S1_DC3_Voc = uithaiguoqianya.textEdit_S1_DC3_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Voc)

        textEdit_S1_DC3_Isc = uithaiguoqianya.textEdit_S1_DC3_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Isc)

        textEdit_S1_DC3_PF = uithaiguoqianya.textEdit_S1_DC3_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_PF)

        out = open(directory1[0], 'w+', newline='')
        csv_write = csv.writer(out, dialect="excel")
        csv_write.writerow(arrayRow1)
        csv_write.writerow(arrayRow2)
        out.close()
        QMessageBox.information(dialog_windowguoqianya, "实验设定提示信息", "过欠压文件保存完成", QMessageBox.Ok, QMessageBox.Ok)

#泰国过欠压读取设定
def Open_File_ThaiGuoQianYa(dialog_windowguoqianya, uithaiguoqianya):
    strFlag = "0"
    directory1 = QFileDialog.getOpenFileName(dialog_windowguoqianya, "单个文件选择", "./", "Text Files(*.csv)")
    if directory1[0] == '':
        print("请选择一个文件")
    else:
        arrayRow1 = ['Style', 'checkBox_S1', "checkBox_S2", "checkBox_S3", 'comboBox_S1_AC', 'comboBox_S1_AC_2',
                     "comboBox_S1_ACWaitTIME", "comboBox_S1_DC1", "comboBox_S1_DC2", "comboBox_S1_DL850",
                     "comboBox_S1_TIME", "comboBox_S2_WT3000_Setting", "comboBox_S2_WT3000_S1",
                     "comboBox_S2_WT3000_S1_FR_TIME", "comboBox_S2_WT300_STAYTIME", "comboBox_S2_DL850",
                     "comboBox_S2_AC_FR_RAMP1_SPACETIME", "comboBox_S2_AC_FR_RAMP2_SPACETIME",
                     "comboBox_S2_AC_FR_RAMP2_STAYTIME", "comboBox_S2_WT3000_S2", "comboBox_S2_TIME",
                     "comboBox_S3_DL850_S1", "comboBox_S3_SPACETIME1", "comboBox_S3_SPACETIME2",
                     "comboBox_S3_SPACETIME3", "comboBox_S3_SPACETIME4", "comboBox_S3_DL850_S2", "textEdit_S1_AC_VOLT",
                     "textEdit_S1_AC_VOLT_2", "textEdit_S1_AC_VOLT_3", "textEdit_S1_AC_FR", "textEdit_S1_ACWaitTIME",
                     "textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR",
                     "textEdit_S1_TIME", "textEdit_S2_CYCLE_TIME", "textEdit_S2_WT3000_S1_FR_TIME",
                     "textEdit_S2_WT300_STAYTIME", "textEdit_S2_AC_VOLT_RAMP1_1_1", "textEdit_S2_AC_VOLT_RAMP1_1_2",
                     "textEdit_S2_AC_VOLT_RAMP1_2_1", "textEdit_S2_AC_VOLT_RAMP1_2_2", "textEdit_S2_AC_VOLT_RAMP1_3_1",
                     "textEdit_S2_AC_VOLT_RAMP1_3_2", "textEdit_S2_AC_VOLT_RAMP1_TIMES",
                     "textEdit_S2_AC_FR_RAMP1_SPACETIME", "textEdit_S2_AC_FR_RAMP2_1_1", "textEdit_S2_AC_FR_RAMP2_1_2",
                     "textEdit_S2_AC_FR_RAMP2_2_1", "textEdit_S2_AC_FR_RAMP2_2_2", "textEdit_S2_AC_FR_RAMP2_3_1",
                     "textEdit_S2_AC_FR_RAMP2_3_2", "textEdit_S2_AC_FR_RAMP2_TIMES",
                     "textEdit_S2_AC_FR_RAMP2_SPACETIME", "textEdit_S2_AC_FR_RAMP2_STAYTIME", "textEdit_S2_AC_VOLT",
                     "textEdit_S2_AC_VOLT_2", "textEdit_S2_AC_VOLT_3", "textEdit_S2_AC_FR", "textEdit_S2_TIME",
                     "textEdit_S3_CYCLE_TIME", "textEdit_S3_AC_VOLT", "textEdit_S3_AC_VOLT_2", "textEdit_S3_AC_VOLT_3",
                     "textEdit_S3_AC_FR", "textEdit_S3_SPACETIME1", "textEdit_S3_AC_VOLT2", "textEdit_S3_AC_VOLT2_2",
                     "textEdit_S3_AC_VOLT2_3", "textEdit_S3_AC_FR_2", "textEdit_S3_SPACETIME2", "textEdit_S3_AC_VOLT3",
                     "textEdit_S3_AC_VOLT3_2", "textEdit_S3_AC_VOLT3_3", "textEdit_S3_AC_FR_3",
                     "textEdit_S3_SPACETIME3", "textEdit_S3_AC_VOLT4", "textEdit_S3_AC_VOLT4_2",
                     "textEdit_S3_AC_VOLT4_3", "textEdit_S3_AC_FR_4", "textEdit_S3_SPACETIME4", "checkBox_S1_AC1",
                     "checkBox_S1_DC1", "checkBox_S1_DC2", "checkBox_S1_DC3", "checkBox_S1_DL850", "checkBox_S2_WT3000",
                     "checkBox_S2_DL850", "checkBox_S2_AC1_1", "checkBox_S2_AC1_2", "checkBox_S2_WT3000_2",
                     "checkBox_S2_AC1_3", "checkBox_S3_DL850_1", "checkBox_S3_AC1_1", "checkBox_S3_AC1_2",
                     "checkBox_S3_AC1_3", "checkBox_S3_AC1_4", "checkBox_S3_DL850_2", "checkBox_S4",
                     "checkBox_S4_AC1_1", "checkBox_S4_DC1_1", "checkBox_S4_DC2_1", "checkBox_S4_DC3_1",
                     "comboBox_S1_DC3", "comboBox_S4_AC1_1", "comboBox_S4_DC1_1", "comboBox_S4_DC2_1",
                     "comboBox_S4_DC3_1", "textEdit_S1_DC1_Voc", "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF",
                     "textEdit_S1_DC2_Voc", "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF", "textEdit_S1_DC3_VOLT",
                     "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Voc", "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF"]

        f1 = open(directory1[0], 'r')
        reader = csv.DictReader(f1)
        # print(reader)
        for i in reader:
            print(i)

        if arrayRow1[0] in i:
            if i[arrayRow1[0]] == "ThaiGuoQianYa":
                # checkBox
                if strFlag == "0":
                    if arrayRow1[1] in i:
                        checkBox_S1 = i[arrayRow1[1]]
                        if checkBox_S1 == '1':
                            uithaiguoqianya.checkBox_S1.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[2] in i:
                        checkBox_S2 = i[arrayRow1[2]]
                        if checkBox_S2 == '1':
                            uithaiguoqianya.checkBox_S2.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[3] in i:
                        checkBox_S3 = i[arrayRow1[3]]
                        if checkBox_S3 == '1':
                            uithaiguoqianya.checkBox_S3.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S3.setChecked(False)
                    else:
                        strFlag = 1

                # comBox
                if strFlag == "0":
                    if arrayRow1[4] in i:
                        comboBox_S1_AC = i[arrayRow1[4]]
                        uithaiguoqianya.comboBox_S1_AC.setCurrentIndex(int(comboBox_S1_AC))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[5] in i:
                        comboBox_S1_AC_2 = i[arrayRow1[5]]
                        uithaiguoqianya.comboBox_S1_AC_2.setCurrentIndex(int(comboBox_S1_AC_2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[6] in i:
                        comboBox_S1_ACWaitTIME = i[arrayRow1[6]]
                        uithaiguoqianya.comboBox_S1_ACWaitTIME.setCurrentIndex(int(comboBox_S1_ACWaitTIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[7] in i:
                        comboBox_S1_DC1 = i[arrayRow1[7]]
                        uithaiguoqianya.comboBox_S1_DC1.setCurrentIndex(int(comboBox_S1_DC1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[8] in i:
                        comboBox_S1_DC2 = i[arrayRow1[8]]
                        uithaiguoqianya.comboBox_S1_DC2.setCurrentIndex(int(comboBox_S1_DC2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[9] in i:
                        comboBox_S1_DL850 = i[arrayRow1[9]]
                        uithaiguoqianya.comboBox_S1_DL850.setCurrentIndex(int(comboBox_S1_DL850))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[10] in i:
                        comboBox_S1_TIME = i[arrayRow1[10]]
                        uithaiguoqianya.comboBox_S1_TIME.setCurrentIndex(int(comboBox_S1_TIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[11] in i:
                        comboBox_S2_WT3000_Setting = i[arrayRow1[11]]
                        uithaiguoqianya.comboBox_S2_WT3000_Setting.setCurrentIndex(int(comboBox_S2_WT3000_Setting))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[12] in i:
                        comboBox_S2_WT3000_S1 = i[arrayRow1[12]]
                        uithaiguoqianya.comboBox_S2_WT3000_S1.setCurrentIndex(int(comboBox_S2_WT3000_S1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[13] in i:
                        comboBox_S2_WT3000_S1_FR_TIME = i[arrayRow1[13]]
                        uithaiguoqianya.comboBox_S2_WT3000_S1_FR_TIME.setCurrentIndex(
                            int(comboBox_S2_WT3000_S1_FR_TIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[14] in i:
                        comboBox_S2_WT300_STAYTIME = i[arrayRow1[14]]
                        uithaiguoqianya.comboBox_S2_WT300_STAYTIME.setCurrentIndex(int(comboBox_S2_WT300_STAYTIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[15] in i:
                        comboBox_S2_DL850 = i[arrayRow1[15]]
                        uithaiguoqianya.comboBox_S2_DL850.setCurrentIndex(int(comboBox_S2_DL850))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[16] in i:
                        comboBox_S2_AC_FR_RAMP1_SPACETIME = i[arrayRow1[16]]
                        uithaiguoqianya.comboBox_S2_AC_FR_RAMP1_SPACETIME.setCurrentIndex(
                            int(comboBox_S2_AC_FR_RAMP1_SPACETIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[17] in i:
                        comboBox_S2_AC_FR_RAMP2_SPACETIME = i[arrayRow1[17]]
                        uithaiguoqianya.comboBox_S2_AC_FR_RAMP2_SPACETIME.setCurrentIndex(
                            int(comboBox_S2_AC_FR_RAMP2_SPACETIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[18] in i:
                        comboBox_S2_AC_FR_RAMP2_STAYTIME = i[arrayRow1[18]]
                        uithaiguoqianya.comboBox_S2_AC_FR_RAMP2_STAYTIME.setCurrentIndex(
                            int(comboBox_S2_AC_FR_RAMP2_STAYTIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[19] in i:
                        comboBox_S2_WT3000_S2 = i[arrayRow1[19]]
                        uithaiguoqianya.comboBox_S2_WT3000_S2.setCurrentIndex(int(comboBox_S2_WT3000_S2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[20] in i:
                        comboBox_S2_TIME = i[arrayRow1[20]]
                        uithaiguoqianya.comboBox_S2_TIME.setCurrentIndex(int(comboBox_S2_TIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[21] in i:
                        comboBox_S3_DL850_S1 = i[arrayRow1[21]]
                        uithaiguoqianya.comboBox_S3_DL850_S1.setCurrentIndex(int(comboBox_S3_DL850_S1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[22] in i:
                        comboBox_S3_SPACETIME1 = i[arrayRow1[22]]
                        uithaiguoqianya.comboBox_S3_SPACETIME1.setCurrentIndex(int(comboBox_S3_SPACETIME1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[23] in i:
                        comboBox_S3_SPACETIME2 = i[arrayRow1[23]]
                        uithaiguoqianya.comboBox_S3_SPACETIME2.setCurrentIndex(int(comboBox_S3_SPACETIME2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[24] in i:
                        comboBox_S3_SPACETIME3 = i[arrayRow1[24]]
                        uithaiguoqianya.comboBox_S3_SPACETIME3.setCurrentIndex(int(comboBox_S3_SPACETIME3))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[25] in i:
                        comboBox_S3_SPACETIME4 = i[arrayRow1[25]]
                        uithaiguoqianya.comboBox_S3_SPACETIME4.setCurrentIndex(int(comboBox_S3_SPACETIME4))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[26] in i:
                        comboBox_S3_DL850_S2 = i[arrayRow1[26]]
                        uithaiguoqianya.comboBox_S3_DL850_S2.setCurrentIndex(int(comboBox_S3_DL850_S2))
                    else:
                        strFlag = 1

                # EditText
                if strFlag == "0":
                    if arrayRow1[27] in i:
                        textEdit_S1_AC_VOLT = i[arrayRow1[27]]
                        uithaiguoqianya.textEdit_S1_AC_VOLT.setText(textEdit_S1_AC_VOLT)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[28] in i:
                        textEdit_S1_AC_VOLT_2 = i[arrayRow1[28]]
                        uithaiguoqianya.textEdit_S1_AC_VOLT_2.setText(textEdit_S1_AC_VOLT_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[29] in i:
                        textEdit_S1_AC_VOLT_3 = i[arrayRow1[29]]
                        uithaiguoqianya.textEdit_S1_AC_VOLT_3.setText(textEdit_S1_AC_VOLT_3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[30] in i:
                        textEdit_S1_AC_VOLT_3 = i[arrayRow1[30]]
                        uithaiguoqianya.textEdit_S1_AC_VOLT_3.setText(textEdit_S1_AC_VOLT_3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[31] in i:
                        textEdit_S1_AC_FR = i[arrayRow1[31]]
                        uithaiguoqianya.textEdit_S1_AC_FR.setText(textEdit_S1_AC_FR)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[32] in i:
                        textEdit_S1_ACWaitTIME = i[arrayRow1[32]]
                        uithaiguoqianya.textEdit_S1_ACWaitTIME.setText(textEdit_S1_ACWaitTIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[33] in i:
                        textEdit_S1_DC1_VOLT = i[arrayRow1[33]]
                        uithaiguoqianya.textEdit_S1_DC1_VOLT.setText(textEdit_S1_DC1_VOLT)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[34] in i:
                        textEdit_S1_DC1_CURR = i[arrayRow1[34]]
                        uithaiguoqianya.textEdit_S1_DC1_CURR.setText(textEdit_S1_DC1_CURR)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[35] in i:
                        textEdit_S1_DC2_VOLT = i[arrayRow1[35]]
                        uithaiguoqianya.textEdit_S1_DC2_VOLT.setText(textEdit_S1_DC2_VOLT)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[36] in i:
                        textEdit_S1_DC2_CURR = i[arrayRow1[36]]
                        uithaiguoqianya.textEdit_S1_DC2_CURR.setText(textEdit_S1_DC2_CURR)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[37] in i:
                        textEdit_S1_TIME = i[arrayRow1[37]]
                        uithaiguoqianya.textEdit_S1_TIME.setText(textEdit_S1_TIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[38] in i:
                        textEdit_S2_CYCLE_TIME = i[arrayRow1[38]]
                        uithaiguoqianya.textEdit_S2_CYCLE_TIME.setText(textEdit_S2_CYCLE_TIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[39] in i:
                        textEdit_S2_WT3000_S1_FR_TIME = i[arrayRow1[39]]
                        uithaiguoqianya.textEdit_S2_WT3000_S1_FR_TIME.setText(textEdit_S2_WT3000_S1_FR_TIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[40] in i:
                        textEdit_S2_WT300_STAYTIME = i[arrayRow1[40]]
                        uithaiguoqianya.textEdit_S2_WT300_STAYTIME.setText(textEdit_S2_WT300_STAYTIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[41] in i:
                        textEdit_S2_AC_VOLT_RAMP1_1_1 = i[arrayRow1[41]]
                        uithaiguoqianya.textEdit_S2_AC_VOLT_RAMP1_1_1.setText(textEdit_S2_AC_VOLT_RAMP1_1_1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[42] in i:
                        textEdit_S2_AC_VOLT_RAMP1_1_2 = i[arrayRow1[42]]
                        uithaiguoqianya.textEdit_S2_AC_VOLT_RAMP1_1_2.setText(textEdit_S2_AC_VOLT_RAMP1_1_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[43] in i:
                        textEdit_S2_AC_VOLT_RAMP1_2_1 = i[arrayRow1[43]]
                        uithaiguoqianya.textEdit_S2_AC_VOLT_RAMP1_2_1.setText(textEdit_S2_AC_VOLT_RAMP1_2_1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[44] in i:
                        textEdit_S2_AC_VOLT_RAMP1_2_2 = i[arrayRow1[44]]
                        uithaiguoqianya.textEdit_S2_AC_VOLT_RAMP1_2_2.setText(textEdit_S2_AC_VOLT_RAMP1_2_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[45] in i:
                        textEdit_S2_AC_VOLT_RAMP1_3_1 = i[arrayRow1[45]]
                        uithaiguoqianya.textEdit_S2_AC_VOLT_RAMP1_3_1.setText(textEdit_S2_AC_VOLT_RAMP1_3_1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[46] in i:
                        textEdit_S2_AC_VOLT_RAMP1_3_2 = i[arrayRow1[46]]
                        uithaiguoqianya.textEdit_S2_AC_VOLT_RAMP1_3_2.setText(textEdit_S2_AC_VOLT_RAMP1_3_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[47] in i:
                        textEdit_S2_AC_VOLT_RAMP1_TIMES = i[arrayRow1[47]]
                        uithaiguoqianya.textEdit_S2_AC_VOLT_RAMP1_TIMES.setText(textEdit_S2_AC_VOLT_RAMP1_TIMES)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[48] in i:
                        textEdit_S2_AC_FR_RAMP1_SPACETIME = i[arrayRow1[48]]
                        uithaiguoqianya.textEdit_S2_AC_FR_RAMP1_SPACETIME.setText(textEdit_S2_AC_FR_RAMP1_SPACETIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[49] in i:
                        textEdit_S2_AC_FR_RAMP2_1_1 = i[arrayRow1[49]]
                        uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_1_1.setText(textEdit_S2_AC_FR_RAMP2_1_1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[50] in i:
                        textEdit_S2_AC_FR_RAMP2_1_2 = i[arrayRow1[50]]
                        uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_1_2.setText(textEdit_S2_AC_FR_RAMP2_1_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[51] in i:
                        textEdit_S2_AC_FR_RAMP2_2_1 = i[arrayRow1[51]]
                        uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_2_1.setText(textEdit_S2_AC_FR_RAMP2_2_1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[52] in i:
                        textEdit_S2_AC_FR_RAMP2_2_2 = i[arrayRow1[52]]
                        uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_2_2.setText(textEdit_S2_AC_FR_RAMP2_2_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[53] in i:
                        textEdit_S2_AC_FR_RAMP2_3_1 = i[arrayRow1[53]]
                        uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_3_1.setText(textEdit_S2_AC_FR_RAMP2_3_1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[54] in i:
                        textEdit_S2_AC_FR_RAMP2_3_2 = i[arrayRow1[54]]
                        uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_3_2.setText(textEdit_S2_AC_FR_RAMP2_3_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[55] in i:
                        textEdit_S2_AC_FR_RAMP2_TIMES = i[arrayRow1[55]]
                        uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_TIMES.setText(textEdit_S2_AC_FR_RAMP2_TIMES)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[56] in i:
                        textEdit_S2_AC_FR_RAMP2_SPACETIME = i[arrayRow1[56]]
                        uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_SPACETIME.setText(textEdit_S2_AC_FR_RAMP2_SPACETIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[57] in i:
                        textEdit_S2_AC_FR_RAMP2_STAYTIME = i[arrayRow1[57]]
                        uithaiguoqianya.textEdit_S2_AC_FR_RAMP2_STAYTIME.setText(textEdit_S2_AC_FR_RAMP2_STAYTIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[58] in i:
                        textEdit_S2_AC_VOLT = i[arrayRow1[58]]
                        uithaiguoqianya.textEdit_S2_AC_VOLT.setText(textEdit_S2_AC_VOLT)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[59] in i:
                        textEdit_S2_AC_VOLT_2 = i[arrayRow1[59]]
                        uithaiguoqianya.textEdit_S2_AC_VOLT_2.setText(textEdit_S2_AC_VOLT_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[60] in i:
                        textEdit_S2_AC_VOLT_3 = i[arrayRow1[60]]
                        uithaiguoqianya.textEdit_S2_AC_VOLT_3.setText(textEdit_S2_AC_VOLT_3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[61] in i:
                        textEdit_S2_AC_FR = i[arrayRow1[61]]
                        uithaiguoqianya.textEdit_S2_AC_FR.setText(textEdit_S2_AC_FR)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[62] in i:
                        textEdit_S2_TIME = i[arrayRow1[62]]
                        uithaiguoqianya.textEdit_S2_TIME.setText(textEdit_S2_TIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[63] in i:
                        textEdit_S3_CYCLE_TIME = i[arrayRow1[63]]
                        uithaiguoqianya.textEdit_S3_CYCLE_TIME.setText(textEdit_S3_CYCLE_TIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[64] in i:
                        textEdit_S3_AC_VOLT = i[arrayRow1[64]]
                        uithaiguoqianya.textEdit_S3_AC_VOLT.setText(textEdit_S3_AC_VOLT)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[65] in i:
                        textEdit_S3_AC_VOLT_2 = i[arrayRow1[65]]
                        uithaiguoqianya.textEdit_S3_AC_VOLT_2.setText(textEdit_S3_AC_VOLT_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[66] in i:
                        textEdit_S3_AC_VOLT_3 = i[arrayRow1[66]]
                        uithaiguoqianya.textEdit_S3_AC_VOLT_3.setText(textEdit_S3_AC_VOLT_3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[67] in i:
                        textEdit_S3_AC_FR = i[arrayRow1[67]]
                        uithaiguoqianya.textEdit_S3_AC_FR.setText(textEdit_S3_AC_FR)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[68] in i:
                        textEdit_S3_SPACETIME1 = i[arrayRow1[68]]
                        uithaiguoqianya.textEdit_S3_SPACETIME1.setText(textEdit_S3_SPACETIME1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[69] in i:
                        textEdit_S3_AC_VOLT2 = i[arrayRow1[69]]
                        uithaiguoqianya.textEdit_S3_AC_VOLT2.setText(textEdit_S3_AC_VOLT2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[70] in i:
                        textEdit_S3_AC_VOLT2_2 = i[arrayRow1[70]]
                        uithaiguoqianya.textEdit_S3_AC_VOLT2_2.setText(textEdit_S3_AC_VOLT2_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[71] in i:
                        textEdit_S3_AC_VOLT2_3 = i[arrayRow1[71]]
                        uithaiguoqianya.textEdit_S3_AC_VOLT2_3.setText(textEdit_S3_AC_VOLT2_3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[72] in i:
                        textEdit_S3_AC_FR_2 = i[arrayRow1[72]]
                        uithaiguoqianya.textEdit_S3_AC_FR_2.setText(textEdit_S3_AC_FR_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[73] in i:
                        textEdit_S3_SPACETIME2 = i[arrayRow1[73]]
                        uithaiguoqianya.textEdit_S3_SPACETIME2.setText(textEdit_S3_SPACETIME2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[74] in i:
                        textEdit_S3_AC_VOLT3 = i[arrayRow1[74]]
                        uithaiguoqianya.textEdit_S3_AC_VOLT3.setText(textEdit_S3_AC_VOLT3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[75] in i:
                        textEdit_S3_AC_VOLT3_2 = i[arrayRow1[75]]
                        uithaiguoqianya.textEdit_S3_AC_VOLT3_2.setText(textEdit_S3_AC_VOLT3_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[76] in i:
                        textEdit_S3_AC_VOLT3_3 = i[arrayRow1[76]]
                        uithaiguoqianya.textEdit_S3_AC_VOLT3_3.setText(textEdit_S3_AC_VOLT3_3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[77] in i:
                        textEdit_S3_AC_FR_3 = i[arrayRow1[77]]
                        uithaiguoqianya.textEdit_S3_AC_FR_3.setText(textEdit_S3_AC_FR_3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[78] in i:
                        textEdit_S3_SPACETIME3 = i[arrayRow1[78]]
                        uithaiguoqianya.textEdit_S3_SPACETIME3.setText(textEdit_S3_SPACETIME3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[79] in i:
                        textEdit_S3_AC_VOLT4 = i[arrayRow1[79]]
                        uithaiguoqianya.textEdit_S3_AC_VOLT4.setText(textEdit_S3_AC_VOLT4)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[80] in i:
                        textEdit_S3_AC_VOLT4_2 = i[arrayRow1[80]]
                        uithaiguoqianya.textEdit_S3_AC_VOLT4_2.setText(textEdit_S3_AC_VOLT4_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[81] in i:
                        textEdit_S3_AC_VOLT4_3 = i[arrayRow1[81]]
                        uithaiguoqianya.textEdit_S3_AC_VOLT4_3.setText(textEdit_S3_AC_VOLT4_3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[82] in i:
                        textEdit_S3_AC_FR_4 = i[arrayRow1[82]]
                        uithaiguoqianya.textEdit_S3_AC_FR_4.setText(textEdit_S3_AC_FR_4)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[83] in i:
                        textEdit_S3_SPACETIME4 = i[arrayRow1[83]]
                        uithaiguoqianya.textEdit_S3_SPACETIME4.setText(textEdit_S3_SPACETIME4)
                    else:
                        strFlag = 1
                #New
                if strFlag == "0":
                    if arrayRow1[84] in i:
                        checkBox_S1_AC1 = i[arrayRow1[84]]
                        if checkBox_S1_AC1 == '1':
                            uithaiguoqianya.checkBox_S1_AC1.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S1_AC1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[85] in i:
                        checkBox_S1_DC1 = i[arrayRow1[85]]
                        if checkBox_S1_DC1 == '1':
                            uithaiguoqianya.checkBox_S1_DC1.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S1_DC1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[86] in i:
                        checkBox_S1_DC2 = i[arrayRow1[86]]
                        if checkBox_S1_DC2 == '1':
                            uithaiguoqianya.checkBox_S1_DC2.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S1_DC2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[87] in i:
                        checkBox_S1_DC3 = i[arrayRow1[87]]
                        if checkBox_S1_DC3 == '1':
                            uithaiguoqianya.checkBox_S1_DC3.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S1_DC3.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[88] in i:
                        checkBox_S1_DL850 = i[arrayRow1[88]]
                        if checkBox_S1_DL850 == '1':
                            uithaiguoqianya.checkBox_S1_DL850.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S1_DL850.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[89] in i:
                        checkBox_S2_WT3000 = i[arrayRow1[89]]
                        if checkBox_S2_WT3000 == '1':
                            uithaiguoqianya.checkBox_S2_WT3000.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S2_WT3000.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[90] in i:
                        checkBox_S2_DL850 = i[arrayRow1[90]]
                        if checkBox_S2_DL850 == '1':
                            uithaiguoqianya.checkBox_S2_DL850.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S2_DL850.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[91] in i:
                        checkBox_S2_AC1_1 = i[arrayRow1[91]]
                        if checkBox_S2_AC1_1 == '1':
                            uithaiguoqianya.checkBox_S2_AC1_1.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S2_AC1_1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[92] in i:
                        checkBox_S2_AC1_2 = i[arrayRow1[92]]
                        if checkBox_S2_AC1_2 == '1':
                            uithaiguoqianya.checkBox_S2_AC1_2.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S2_AC1_2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[93] in i:
                        checkBox_S2_WT3000_2 = i[arrayRow1[93]]
                        if checkBox_S2_WT3000_2 == '1':
                            uithaiguoqianya.checkBox_S2_WT3000_2.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S2_WT3000_2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[94] in i:
                        checkBox_S2_AC1_3 = i[arrayRow1[94]]
                        if checkBox_S2_AC1_3 == '1':
                            uithaiguoqianya.checkBox_S2_AC1_3.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S2_AC1_3.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[95] in i:
                        checkBox_S3_DL850_1 = i[arrayRow1[95]]
                        if checkBox_S3_DL850_1 == '1':
                            uithaiguoqianya.checkBox_S3_DL850_1.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S3_DL850_1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[96] in i:
                        checkBox_S3_AC1_1 = i[arrayRow1[96]]
                        if checkBox_S3_AC1_1 == '1':
                            uithaiguoqianya.checkBox_S3_AC1_1.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S3_AC1_1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[97] in i:
                        checkBox_S3_AC1_2 = i[arrayRow1[97]]
                        if checkBox_S3_AC1_2 == '1':
                            uithaiguoqianya.checkBox_S3_AC1_2.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S3_AC1_2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[98] in i:
                        checkBox_S3_AC1_3 = i[arrayRow1[98]]
                        if checkBox_S3_AC1_3 == '1':
                            uithaiguoqianya.checkBox_S3_AC1_3.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S3_AC1_3.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[99] in i:
                        checkBox_S3_AC1_4 = i[arrayRow1[99]]
                        if checkBox_S3_AC1_4 == '1':
                            uithaiguoqianya.checkBox_S3_AC1_4.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S3_AC1_4.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[100] in i:
                        checkBox_S3_DL850_2 = i[arrayRow1[100]]
                        if checkBox_S3_DL850_2 == '1':
                            uithaiguoqianya.checkBox_S3_DL850_2.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S3_DL850_2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[101] in i:
                        checkBox_S4 = i[arrayRow1[101]]
                        if checkBox_S4 == '1':
                            uithaiguoqianya.checkBox_S4.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S4.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[102] in i:
                        checkBox_S4_AC1_1 = i[arrayRow1[102]]
                        if checkBox_S4_AC1_1 == '1':
                            uithaiguoqianya.checkBox_S4_AC1_1.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S4_AC1_1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[102] in i:
                        checkBox_S4_DC1_1 = i[arrayRow1[102]]
                        if checkBox_S4_DC1_1 == '1':
                            uithaiguoqianya.checkBox_S4_DC1_1.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S4_DC1_1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[103] in i:
                        checkBox_S4_DC2_1 = i[arrayRow1[103]]
                        if checkBox_S4_DC2_1 == '1':
                            uithaiguoqianya.checkBox_S4_DC2_1.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S4_DC2_1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[104] in i:
                        checkBox_S4_DC3_1 = i[arrayRow1[104]]
                        if checkBox_S4_DC3_1 == '1':
                            uithaiguoqianya.checkBox_S4_DC3_1.setChecked(True)
                        else:
                            uithaiguoqianya.checkBox_S4_DC3_1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[105] in i:
                        comboBox_S1_DC3 = i[arrayRow1[105]]
                        uithaiguoqianya.comboBox_S1_DC3.setCurrentIndex(int(comboBox_S1_DC3))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[106] in i:
                        comboBox_S4_AC1_1 = i[arrayRow1[106]]
                        uithaiguoqianya.comboBox_S4_AC1_1.setCurrentIndex(int(comboBox_S4_AC1_1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[107] in i:
                        comboBox_S4_DC1_1 = i[arrayRow1[107]]
                        uithaiguoqianya.comboBox_S4_DC1_1.setCurrentIndex(int(comboBox_S4_DC1_1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[108] in i:
                        comboBox_S4_DC2_1 = i[arrayRow1[108]]
                        uithaiguoqianya.comboBox_S4_DC2_1.setCurrentIndex(int(comboBox_S4_DC2_1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[109] in i:
                        comboBox_S4_DC3_1 = i[arrayRow1[109]]
                        uithaiguoqianya.comboBox_S4_DC3_1.setCurrentIndex(int(comboBox_S4_DC3_1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[110] in i:
                        textEdit_S1_DC1_Voc = i[arrayRow1[110]]
                        uithaiguoqianya.textEdit_S1_DC1_Voc.setText(textEdit_S1_DC1_Voc)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[111] in i:
                        textEdit_S1_DC1_Isc = i[arrayRow1[111]]
                        uithaiguoqianya.textEdit_S1_DC1_Isc.setText(textEdit_S1_DC1_Isc)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[112] in i:
                        textEdit_S1_DC1_PF = i[arrayRow1[112]]
                        uithaiguoqianya.textEdit_S1_DC1_PF.setText(textEdit_S1_DC1_PF)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[113] in i:
                        textEdit_S1_DC2_Voc = i[arrayRow1[113]]
                        uithaiguoqianya.textEdit_S1_DC2_Voc.setText(textEdit_S1_DC2_Voc)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[114] in i:
                        textEdit_S1_DC2_Isc = i[arrayRow1[114]]
                        uithaiguoqianya.textEdit_S1_DC2_Isc.setText(textEdit_S1_DC2_Isc)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[115] in i:
                        textEdit_S1_DC2_PF = i[arrayRow1[115]]
                        uithaiguoqianya.textEdit_S1_DC2_PF.setText(textEdit_S1_DC2_PF)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[116] in i:
                        textEdit_S1_DC3_VOLT = i[arrayRow1[116]]
                        uithaiguoqianya.textEdit_S1_DC3_VOLT.setText(textEdit_S1_DC3_VOLT)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[117] in i:
                        textEdit_S1_DC3_CURR = i[arrayRow1[117]]
                        uithaiguoqianya.textEdit_S1_DC3_CURR.setText(textEdit_S1_DC3_CURR)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[118] in i:
                        textEdit_S1_DC3_Voc = i[arrayRow1[118]]
                        uithaiguoqianya.textEdit_S1_DC3_Voc.setText(textEdit_S1_DC3_Voc)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[119] in i:
                        textEdit_S1_DC3_Isc = i[arrayRow1[119]]
                        uithaiguoqianya.textEdit_S1_DC3_Isc.setText(textEdit_S1_DC3_Isc)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[120] in i:
                        textEdit_S1_DC3_PF = i[arrayRow1[120]]
                        uithaiguoqianya.textEdit_S1_DC3_PF.setText(textEdit_S1_DC3_PF)
                    else:
                        strFlag = 1

        QMessageBox.information(dialog_windowguoqianya, "实验设定提示信息", "过欠压文件读取完成", QMessageBox.Ok, QMessageBox.Ok)
