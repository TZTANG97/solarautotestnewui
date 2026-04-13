from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, \
    QFileDialog, QMessageBox
import csv

# 泰国过欠频保存设定
def Save_File_ThaiGuoqianpin(dialog_windowguoqianpin, uithaiguoqianpin):
    directory1 = QFileDialog.getSaveFileName(dialog_windowguoqianpin,"单个文件保存","./","Text Files(*.csv)")
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
                     "comboBox_S3_DL850_S2","textEdit_S1_AC_VOLT","textEdit_S1_AC_VOLT_2","textEdit_S1_AC_VOLT_3",
                     "textEdit_S1_AC_FR","textEdit_S1_ACWaitTIME","textEdit_S1_DC1_VOLT","textEdit_S1_DC1_CURR",
                     "textEdit_S1_DC2_VOLT","textEdit_S1_DC2_CURR","textEdit_S1_TIME","textEdit_S2_CYCLE_TIME",
                     "textEdit_S2_AC_FR_RAMP1_1","textEdit_S2_AC_FR_RAMP1_2","textEdit_S2_AC_FR_RAMP1_TIMES",
                     "textEdit_S2_AC_FR_RAMP1_SPACETIME","textEdit_S2_AC_FR_RAMP2_1","textEdit_S2_AC_FR_RAMP2_2",
                     "textEdit_S2_AC_FR_RAMP2_TIMES","textEdit_S2_AC_FR_RAMP2_SPACETIME","textEdit_S2_AC_FR_RAMP2_STAYTIME",
                     "textEdit_S2_AC_VOLT","textEdit_S2_AC_VOLT_2","textEdit_S2_AC_VOLT_3","textEdit_S2_AC_FR",
                     "textEdit_S2_TIME","textEdit_S3_CYCLE_TIME","textEdit_S3_AC_VOLT","textEdit_S3_AC_VOLT_2",
                     "textEdit_S3_AC_VOLT_3","textEdit_S3_AC_FR","textEdit_S3_SPACETIME1","textEdit_S3_AC_FR_S1",
                     "textEdit_S3_SPACETIME2","textEdit_S3_AC_FR_S2"]

        arrayRow2 = ['ThaiGuoQianPin']

        if uithaiguoqianpin.checkBox_S1.isChecked():
            checkBox_S1 = '1'
        else:
            checkBox_S1 = '0'
        arrayRow2.append(checkBox_S1)

        if uithaiguoqianpin.checkBox_S2.isChecked():
            checkBox_S2 = '1'
        else:
            checkBox_S2 = '0'
        arrayRow2.append(checkBox_S2)

        if uithaiguoqianpin.checkBox_S3.isChecked():
            checkBox_S3 = '1'
        else:
            checkBox_S3 = '0'
        arrayRow2.append(checkBox_S3)

        comboBox_S1_AC = uithaiguoqianpin.comboBox_S1_AC.currentIndex()
        arrayRow2.append(comboBox_S1_AC)

        comboBox_S1_AC_2 = uithaiguoqianpin.comboBox_S1_AC_2.currentIndex()
        arrayRow2.append(comboBox_S1_AC_2)

        comboBox_S1_ACWaitTIME = uithaiguoqianpin.comboBox_S1_ACWaitTIME.currentIndex()
        arrayRow2.append(comboBox_S1_ACWaitTIME)

        comboBox_S1_DC1 = uithaiguoqianpin.comboBox_S1_DC1.currentIndex()
        arrayRow2.append(comboBox_S1_DC1)

        comboBox_S1_DC2 = uithaiguoqianpin.comboBox_S1_DC2.currentIndex()
        arrayRow2.append(comboBox_S1_DC2)

        comboBox_S1_DL850 = uithaiguoqianpin.comboBox_S1_DL850.currentIndex()
        arrayRow2.append(comboBox_S1_DL850)

        comboBox_S1_TIME = uithaiguoqianpin.comboBox_S1_TIME.currentIndex()
        arrayRow2.append(comboBox_S1_TIME)

        comboBox_S2_WT3000_Setting = uithaiguoqianpin.comboBox_S2_WT3000_Setting.currentIndex()
        arrayRow2.append(comboBox_S2_WT3000_Setting)

        comboBox_S2_WT3000_S1 = uithaiguoqianpin.comboBox_S2_WT3000_S1.currentIndex()
        arrayRow2.append(comboBox_S2_WT3000_S1)

        comboBox_S2_WT3000_S1_FR_TIME = uithaiguoqianpin.comboBox_S2_WT3000_S1_FR_TIME.currentIndex()
        arrayRow2.append(comboBox_S2_WT3000_S1_FR_TIME)

        comboBox_S2_WT300_STAYTIME = uithaiguoqianpin.comboBox_S2_WT300_STAYTIME.currentIndex()
        arrayRow2.append(comboBox_S2_WT300_STAYTIME)

        comboBox_S2_DL850 = uithaiguoqianpin.comboBox_S2_DL850.currentIndex()
        arrayRow2.append(comboBox_S2_DL850)

        comboBox_S2_AC_FR_RAMP1_SPACETIME = uithaiguoqianpin.comboBox_S2_AC_FR_RAMP1_SPACETIME.currentIndex()
        arrayRow2.append(comboBox_S2_AC_FR_RAMP1_SPACETIME)

        comboBox_S2_AC_FR_RAMP2_SPACETIME = uithaiguoqianpin.comboBox_S2_AC_FR_RAMP2_SPACETIME.currentIndex()
        arrayRow2.append(comboBox_S2_AC_FR_RAMP2_SPACETIME)

        comboBox_S2_AC_FR_RAMP2_STAYTIME = uithaiguoqianpin.comboBox_S2_AC_FR_RAMP2_STAYTIME.currentIndex()
        arrayRow2.append(comboBox_S2_AC_FR_RAMP2_STAYTIME)

        comboBox_S2_WT3000_S2 = uithaiguoqianpin.comboBox_S2_WT3000_S2.currentIndex()
        arrayRow2.append(comboBox_S2_WT3000_S2)

        comboBox_S2_TIME = uithaiguoqianpin.comboBox_S2_TIME.currentIndex()
        arrayRow2.append(comboBox_S2_TIME)

        comboBox_S3_DL850_S1 = uithaiguoqianpin.comboBox_S3_DL850_S1.currentIndex()
        arrayRow2.append(comboBox_S3_DL850_S1)

        comboBox_S3_SPACETIME1 = uithaiguoqianpin.comboBox_S3_SPACETIME1.currentIndex()
        arrayRow2.append(comboBox_S3_SPACETIME1)

        comboBox_S3_SPACETIME2 = uithaiguoqianpin.comboBox_S3_SPACETIME2.currentIndex()
        arrayRow2.append(comboBox_S3_SPACETIME2)

        comboBox_S3_DL850_S2 = uithaiguoqianpin.comboBox_S3_DL850_S2.currentIndex()
        arrayRow2.append(comboBox_S3_DL850_S2)

        textEdit_S1_AC_VOLT = uithaiguoqianpin.textEdit_S1_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT)

        textEdit_S1_AC_VOLT_2 = uithaiguoqianpin.textEdit_S1_AC_VOLT_2.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_2)

        textEdit_S1_AC_VOLT_3 = uithaiguoqianpin.textEdit_S1_AC_VOLT_3.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_3)

        textEdit_S1_AC_FR = uithaiguoqianpin.textEdit_S1_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S1_AC_FR)

        textEdit_S1_ACWaitTIME = uithaiguoqianpin.textEdit_S1_ACWaitTIME.toPlainText()
        arrayRow2.append(textEdit_S1_ACWaitTIME)

        textEdit_S1_DC1_VOLT = uithaiguoqianpin.textEdit_S1_DC1_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_VOLT)

        textEdit_S1_DC1_CURR = uithaiguoqianpin.textEdit_S1_DC1_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_CURR)

        textEdit_S1_DC2_VOLT = uithaiguoqianpin.textEdit_S1_DC2_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_VOLT)

        textEdit_S1_DC2_CURR = uithaiguoqianpin.textEdit_S1_DC2_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_CURR)

        textEdit_S1_TIME = uithaiguoqianpin.textEdit_S1_TIME.toPlainText()
        arrayRow2.append(textEdit_S1_TIME)

        textEdit_S2_CYCLE_TIME = uithaiguoqianpin.textEdit_S2_CYCLE_TIME.toPlainText()
        arrayRow2.append(textEdit_S2_CYCLE_TIME)

        textEdit_S2_AC_FR_RAMP1_1 = uithaiguoqianpin.textEdit_S2_AC_FR_RAMP1_1.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP1_1)

        textEdit_S2_AC_FR_RAMP1_2 = uithaiguoqianpin.textEdit_S2_AC_FR_RAMP1_2.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP1_2)

        textEdit_S2_AC_FR_RAMP1_TIMES = uithaiguoqianpin.textEdit_S2_AC_FR_RAMP1_TIMES.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP1_TIMES)

        textEdit_S2_AC_FR_RAMP1_SPACETIME = uithaiguoqianpin.textEdit_S2_AC_FR_RAMP1_SPACETIME.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP1_SPACETIME)

        textEdit_S2_AC_FR_RAMP2_1 = uithaiguoqianpin.textEdit_S2_AC_FR_RAMP2_1.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP2_1)

        textEdit_S2_AC_FR_RAMP2_2 = uithaiguoqianpin.textEdit_S2_AC_FR_RAMP2_2.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP2_2)

        textEdit_S2_AC_FR_RAMP2_TIMES = uithaiguoqianpin.textEdit_S2_AC_FR_RAMP2_TIMES.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP2_TIMES)

        textEdit_S2_AC_FR_RAMP2_SPACETIME = uithaiguoqianpin.textEdit_S2_AC_FR_RAMP2_SPACETIME.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP2_SPACETIME)

        textEdit_S2_AC_FR_RAMP2_STAYTIME = uithaiguoqianpin.textEdit_S2_AC_FR_RAMP2_STAYTIME.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR_RAMP2_STAYTIME)

        textEdit_S2_AC_VOLT = uithaiguoqianpin.textEdit_S2_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S2_AC_VOLT)

        textEdit_S2_AC_VOLT_2 = uithaiguoqianpin.textEdit_S2_AC_VOLT_2.toPlainText()
        arrayRow2.append(textEdit_S2_AC_VOLT_2)

        textEdit_S2_AC_VOLT_3 = uithaiguoqianpin.textEdit_S2_AC_VOLT_3.toPlainText()
        arrayRow2.append(textEdit_S2_AC_VOLT_3)

        textEdit_S2_AC_FR = uithaiguoqianpin.textEdit_S2_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S2_AC_FR)

        textEdit_S2_TIME = uithaiguoqianpin.textEdit_S2_TIME.toPlainText()
        arrayRow2.append(textEdit_S2_TIME)

        textEdit_S3_CYCLE_TIME = uithaiguoqianpin.textEdit_S3_CYCLE_TIME.toPlainText()
        arrayRow2.append(textEdit_S3_CYCLE_TIME)

        textEdit_S3_AC_VOLT = uithaiguoqianpin.textEdit_S3_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT)

        textEdit_S3_AC_VOLT_2 = uithaiguoqianpin.textEdit_S3_AC_VOLT_2.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT_2)

        textEdit_S3_AC_VOLT_3 = uithaiguoqianpin.textEdit_S3_AC_VOLT_3.toPlainText()
        arrayRow2.append(textEdit_S3_AC_VOLT_3)

        textEdit_S3_AC_FR = uithaiguoqianpin.textEdit_S3_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S3_AC_FR)

        textEdit_S3_SPACETIME1 = uithaiguoqianpin.textEdit_S3_SPACETIME1.toPlainText()
        arrayRow2.append(textEdit_S3_SPACETIME1)

        textEdit_S3_AC_FR_S1 = uithaiguoqianpin.textEdit_S3_AC_FR_S1.toPlainText()
        arrayRow2.append(textEdit_S3_AC_FR_S1)

        textEdit_S3_SPACETIME2 = uithaiguoqianpin.textEdit_S3_SPACETIME2.toPlainText()
        arrayRow2.append(textEdit_S3_SPACETIME2)

        textEdit_S3_AC_FR_S2 = uithaiguoqianpin.textEdit_S3_AC_FR_S2.toPlainText()
        arrayRow2.append(textEdit_S3_AC_FR_S2)

        out = open(directory1[0], 'w+', newline='')
        csv_write = csv.writer(out, dialect="excel")
        csv_write.writerow(arrayRow1)
        csv_write.writerow(arrayRow2)
        out.close()
        QMessageBox.information(dialog_windowguoqianpin, "实验设定提示信息", "过欠频文件保存完成", QMessageBox.Ok, QMessageBox.Ok)

# 泰国过欠频读取设定
def Open_File_ThaiGuoQianPin(dialog_windowguoqianpin, uithaiguoqianpin):
    strFlag  = "0"
    directory1 = QFileDialog.getOpenFileName(dialog_windowguoqianpin,"单个文件选择","./","Text Files(*.csv)")
    if directory1[0] == '':
        print("请选择一个文件")
    else:
        arrayRow1 = ['Style', 'checkBox_S1', "checkBox_S2", "checkBox_S3", 'comboBox_S1_AC', 'comboBox_S1_AC_2',
                     "comboBox_S1_ACWaitTIME", "comboBox_S1_DC1", "comboBox_S1_DC2", "comboBox_S1_DL850",
                     "comboBox_S1_TIME", "comboBox_S2_WT3000_Setting", "comboBox_S2_WT3000_S1",
                     "comboBox_S2_WT3000_S1_FR_TIME", "comboBox_S2_WT300_STAYTIME", "comboBox_S2_DL850",
                     "comboBox_S2_AC_FR_RAMP1_SPACETIME", "comboBox_S2_AC_FR_RAMP2_SPACETIME",
                     "comboBox_S2_AC_FR_RAMP2_STAYTIME", "comboBox_S2_WT3000_S2", "comboBox_S2_TIME",
                     "comboBox_S3_DL850_S1", "comboBox_S3_SPACETIME1", "comboBox_S3_SPACETIME2", "comboBox_S3_DL850_S2",
                     "textEdit_S1_AC_VOLT", "textEdit_S1_AC_VOLT_2", "textEdit_S1_AC_VOLT_3", "textEdit_S1_AC_FR",
                     "textEdit_S1_ACWaitTIME", "textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC2_VOLT",
                     "textEdit_S1_DC2_CURR", "textEdit_S1_TIME", "textEdit_S2_CYCLE_TIME", "textEdit_S2_AC_FR_RAMP1_1",
                     "textEdit_S2_AC_FR_RAMP1_2", "textEdit_S2_AC_FR_RAMP1_TIMES", "textEdit_S2_AC_FR_RAMP1_SPACETIME",
                     "textEdit_S2_AC_FR_RAMP2_1", "textEdit_S2_AC_FR_RAMP2_2", "textEdit_S2_AC_FR_RAMP2_TIMES",
                     "textEdit_S2_AC_FR_RAMP2_SPACETIME", "textEdit_S2_AC_FR_RAMP2_STAYTIME", "textEdit_S2_AC_VOLT",
                     "textEdit_S2_AC_VOLT_2", "textEdit_S2_AC_VOLT_3", "textEdit_S2_AC_FR", "textEdit_S2_TIME",
                     "textEdit_S3_CYCLE_TIME", "textEdit_S3_AC_VOLT", "textEdit_S3_AC_VOLT_2", "textEdit_S3_AC_VOLT_3",
                     "textEdit_S3_AC_FR", "textEdit_S3_SPACETIME1", "textEdit_S3_AC_FR_S1", "textEdit_S3_SPACETIME2",
                     "textEdit_S3_AC_FR_S2"]

        f1 = open(directory1[0], 'r')
        reader = csv.DictReader(f1)
        #print(reader)
        for i in reader:
            print(i)

        if arrayRow1[0] in i:
            if i[arrayRow1[0]] == "ThaiGuoQianPin":
                #checkBox
                if strFlag == "0":
                    if arrayRow1[1] in i:
                        checkBox_S1 = i[arrayRow1[1]]
                        if checkBox_S1 == '1':
                            uithaiguoqianpin.checkBox_S1.setChecked(True)
                        else:
                            uithaiguoqianpin.checkBox_S1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[2] in i:
                        checkBox_S2 = i[arrayRow1[2]]
                        if checkBox_S2 == '1':
                            uithaiguoqianpin.checkBox_S2.setChecked(True)
                        else:
                            uithaiguoqianpin.checkBox_S2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[3] in i:
                        checkBox_S3 = i[arrayRow1[3]]
                        if checkBox_S3 == '1':
                            uithaiguoqianpin.checkBox_S3.setChecked(True)
                        else:
                            uithaiguoqianpin.checkBox_S3.setChecked(False)
                    else:
                        strFlag = 1

                #comBox
                if strFlag == "0":
                    if arrayRow1[4] in i:
                        comboBox_S1_AC = i[arrayRow1[4]]
                        uithaiguoqianpin.comboBox_S1_AC.setCurrentIndex(int(comboBox_S1_AC))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[5] in i:
                        comboBox_S1_AC_2 = i[arrayRow1[5]]
                        uithaiguoqianpin.comboBox_S1_AC_2.setCurrentIndex(int(comboBox_S1_AC_2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[6] in i:
                        comboBox_S1_ACWaitTIME = i[arrayRow1[6]]
                        uithaiguoqianpin.comboBox_S1_ACWaitTIME.setCurrentIndex(int(comboBox_S1_ACWaitTIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[7] in i:
                        comboBox_S1_DC1 = i[arrayRow1[7]]
                        uithaiguoqianpin.comboBox_S1_DC1.setCurrentIndex(int(comboBox_S1_DC1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[8] in i:
                        comboBox_S1_DC2 = i[arrayRow1[8]]
                        uithaiguoqianpin.comboBox_S1_DC2.setCurrentIndex(int(comboBox_S1_DC2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[9] in i:
                        comboBox_S1_DL850 = i[arrayRow1[9]]
                        uithaiguoqianpin.comboBox_S1_DL850.setCurrentIndex(int(comboBox_S1_DL850))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[10] in i:
                        comboBox_S1_TIME = i[arrayRow1[10]]
                        uithaiguoqianpin.comboBox_S1_TIME.setCurrentIndex(int(comboBox_S1_TIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[11] in i:
                        comboBox_S2_WT3000_Setting = i[arrayRow1[11]]
                        uithaiguoqianpin.comboBox_S2_WT3000_Setting.setCurrentIndex(int(comboBox_S2_WT3000_Setting))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[12] in i:
                        comboBox_S2_WT3000_S1 = i[arrayRow1[12]]
                        uithaiguoqianpin.comboBox_S2_WT3000_S1.setCurrentIndex(int(comboBox_S2_WT3000_S1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[13] in i:
                        comboBox_S2_WT3000_S1_FR_TIME = i[arrayRow1[13]]
                        uithaiguoqianpin.comboBox_S2_WT3000_S1_FR_TIME.setCurrentIndex(int(comboBox_S2_WT3000_S1_FR_TIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[14] in i:
                        comboBox_S2_WT300_STAYTIME = i[arrayRow1[14]]
                        uithaiguoqianpin.comboBox_S2_WT300_STAYTIME.setCurrentIndex(int(comboBox_S2_WT300_STAYTIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[15] in i:
                        comboBox_S2_DL850 = i[arrayRow1[15]]
                        uithaiguoqianpin.comboBox_S2_DL850.setCurrentIndex(int(comboBox_S2_DL850))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[16] in i:
                        comboBox_S2_AC_FR_RAMP1_SPACETIME = i[arrayRow1[16]]
                        uithaiguoqianpin.comboBox_S2_AC_FR_RAMP1_SPACETIME.setCurrentIndex(int(comboBox_S2_AC_FR_RAMP1_SPACETIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[17] in i:
                        comboBox_S2_AC_FR_RAMP2_SPACETIME = i[arrayRow1[17]]
                        uithaiguoqianpin.comboBox_S2_AC_FR_RAMP2_SPACETIME.setCurrentIndex(int(comboBox_S2_AC_FR_RAMP2_SPACETIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[18] in i:
                        comboBox_S2_AC_FR_RAMP2_STAYTIME = i[arrayRow1[18]]
                        uithaiguoqianpin.comboBox_S2_AC_FR_RAMP2_STAYTIME.setCurrentIndex(int(comboBox_S2_AC_FR_RAMP2_STAYTIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[19] in i:
                        comboBox_S2_WT3000_S2 = i[arrayRow1[19]]
                        uithaiguoqianpin.comboBox_S2_WT3000_S2.setCurrentIndex(int(comboBox_S2_WT3000_S2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[20] in i:
                        comboBox_S2_TIME = i[arrayRow1[20]]
                        uithaiguoqianpin.comboBox_S2_TIME.setCurrentIndex(int(comboBox_S2_TIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[21] in i:
                        comboBox_S3_DL850_S1 = i[arrayRow1[21]]
                        uithaiguoqianpin.comboBox_S3_DL850_S1.setCurrentIndex(int(comboBox_S3_DL850_S1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[22] in i:
                        comboBox_S3_SPACETIME1 = i[arrayRow1[22]]
                        uithaiguoqianpin.comboBox_S3_SPACETIME1.setCurrentIndex(int(comboBox_S3_SPACETIME1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[23] in i:
                        comboBox_S3_SPACETIME2 = i[arrayRow1[23]]
                        uithaiguoqianpin.comboBox_S3_SPACETIME2.setCurrentIndex(int(comboBox_S3_SPACETIME2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[24] in i:
                        comboBox_S3_DL850_S2 = i[arrayRow1[24]]
                        uithaiguoqianpin.comboBox_S3_DL850_S2.setCurrentIndex(int(comboBox_S3_DL850_S2))
                    else:
                        strFlag = 1

                #textEdit
                if strFlag == "0":
                    if arrayRow1[25] in i:
                        textEdit_S1_AC_VOLT = i[arrayRow1[25]]
                        uithaiguoqianpin.textEdit_S1_AC_VOLT.setText(textEdit_S1_AC_VOLT)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[26] in i:
                        textEdit_S1_AC_VOLT = i[arrayRow1[26]]
                        uithaiguoqianpin.textEdit_S1_AC_VOLT.setText(textEdit_S1_AC_VOLT)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[27] in i:
                        textEdit_S1_AC_VOLT_2 = i[arrayRow1[27]]
                        uithaiguoqianpin.textEdit_S1_AC_VOLT_2.setText(textEdit_S1_AC_VOLT_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[28] in i:
                        textEdit_S1_AC_VOLT_3 = i[arrayRow1[28]]
                        uithaiguoqianpin.textEdit_S1_AC_VOLT_3.setText(textEdit_S1_AC_VOLT_3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[29] in i:
                        textEdit_S1_AC_FR = i[arrayRow1[29]]
                        uithaiguoqianpin.textEdit_S1_AC_FR.setText(textEdit_S1_AC_FR)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[30] in i:
                        textEdit_S1_ACWaitTIME = i[arrayRow1[30]]
                        uithaiguoqianpin.textEdit_S1_ACWaitTIME.setText(textEdit_S1_ACWaitTIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[31] in i:
                        textEdit_S1_DC1_VOLT = i[arrayRow1[31]]
                        uithaiguoqianpin.textEdit_S1_DC1_VOLT.setText(textEdit_S1_DC1_VOLT)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[32] in i:
                        textEdit_S1_DC1_CURR = i[arrayRow1[32]]
                        uithaiguoqianpin.textEdit_S1_DC1_CURR.setText(textEdit_S1_DC1_CURR)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[33] in i:
                        textEdit_S1_DC2_VOLT = i[arrayRow1[33]]
                        uithaiguoqianpin.textEdit_S1_DC2_VOLT.setText(textEdit_S1_DC2_VOLT)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[34] in i:
                        textEdit_S1_DC2_CURR = i[arrayRow1[34]]
                        uithaiguoqianpin.textEdit_S1_DC2_CURR.setText(textEdit_S1_DC2_CURR)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[35] in i:
                        textEdit_S1_TIME = i[arrayRow1[35]]
                        uithaiguoqianpin.textEdit_S1_TIME.setText(textEdit_S1_TIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[36] in i:
                        textEdit_S2_CYCLE_TIME = i[arrayRow1[36]]
                        uithaiguoqianpin.textEdit_S2_CYCLE_TIME.setText(textEdit_S2_CYCLE_TIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[37] in i:
                        textEdit_S2_AC_FR_RAMP1_1 = i[arrayRow1[37]]
                        uithaiguoqianpin.textEdit_S2_AC_FR_RAMP1_1.setText(textEdit_S2_AC_FR_RAMP1_1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[38] in i:
                        textEdit_S2_AC_FR_RAMP1_2 = i[arrayRow1[38]]
                        uithaiguoqianpin.textEdit_S2_AC_FR_RAMP1_2.setText(textEdit_S2_AC_FR_RAMP1_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[39] in i:
                        textEdit_S2_AC_FR_RAMP1_TIMES = i[arrayRow1[39]]
                        uithaiguoqianpin.textEdit_S2_AC_FR_RAMP1_TIMES.setText(textEdit_S2_AC_FR_RAMP1_TIMES)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[40] in i:
                        textEdit_S2_AC_FR_RAMP1_SPACETIME = i[arrayRow1[40]]
                        uithaiguoqianpin.textEdit_S2_AC_FR_RAMP1_SPACETIME.setText(textEdit_S2_AC_FR_RAMP1_SPACETIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[41] in i:
                        textEdit_S2_AC_FR_RAMP2_1 = i[arrayRow1[41]]
                        uithaiguoqianpin.textEdit_S2_AC_FR_RAMP2_1.setText(textEdit_S2_AC_FR_RAMP2_1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[42] in i:
                        textEdit_S2_AC_FR_RAMP2_2 = i[arrayRow1[42]]
                        uithaiguoqianpin.textEdit_S2_AC_FR_RAMP2_2.setText(textEdit_S2_AC_FR_RAMP2_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[43] in i:
                        textEdit_S2_AC_FR_RAMP2_TIMES = i[arrayRow1[43]]
                        uithaiguoqianpin.textEdit_S2_AC_FR_RAMP2_TIMES.setText(textEdit_S2_AC_FR_RAMP2_TIMES)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[44] in i:
                        textEdit_S2_AC_FR_RAMP2_SPACETIME = i[arrayRow1[44]]
                        uithaiguoqianpin.textEdit_S2_AC_FR_RAMP2_SPACETIME.setText(textEdit_S2_AC_FR_RAMP2_SPACETIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[45] in i:
                        textEdit_S2_AC_FR_RAMP2_STAYTIME = i[arrayRow1[45]]
                        uithaiguoqianpin.textEdit_S2_AC_FR_RAMP2_STAYTIME.setText(textEdit_S2_AC_FR_RAMP2_STAYTIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[46] in i:
                        textEdit_S2_AC_VOLT = i[arrayRow1[46]]
                        uithaiguoqianpin.textEdit_S2_AC_VOLT.setText(textEdit_S2_AC_VOLT)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[47] in i:
                        textEdit_S2_AC_VOLT_2 = i[arrayRow1[47]]
                        uithaiguoqianpin.textEdit_S2_AC_VOLT_2.setText(textEdit_S2_AC_VOLT_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[48] in i:
                        textEdit_S2_AC_VOLT_3 = i[arrayRow1[48]]
                        uithaiguoqianpin.textEdit_S2_AC_VOLT_3.setText(textEdit_S2_AC_VOLT_3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[49] in i:
                        textEdit_S2_AC_FR = i[arrayRow1[49]]
                        uithaiguoqianpin.textEdit_S2_AC_FR.setText(textEdit_S2_AC_FR)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[50] in i:
                        textEdit_S2_TIME = i[arrayRow1[50]]
                        uithaiguoqianpin.textEdit_S2_TIME.setText(textEdit_S2_TIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[51] in i:
                        textEdit_S3_CYCLE_TIME = i[arrayRow1[51]]
                        uithaiguoqianpin.textEdit_S3_CYCLE_TIME.setText(textEdit_S3_CYCLE_TIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[52] in i:
                        textEdit_S3_AC_VOLT = i[arrayRow1[52]]
                        uithaiguoqianpin.textEdit_S3_AC_VOLT.setText(textEdit_S3_AC_VOLT)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[53] in i:
                        textEdit_S3_AC_VOLT_2 = i[arrayRow1[53]]
                        uithaiguoqianpin.textEdit_S3_AC_VOLT_2.setText(textEdit_S3_AC_VOLT_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[54] in i:
                        textEdit_S3_AC_VOLT_3 = i[arrayRow1[54]]
                        uithaiguoqianpin.textEdit_S3_AC_VOLT_3.setText(textEdit_S3_AC_VOLT_3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[55] in i:
                        textEdit_S3_AC_FR = i[arrayRow1[55]]
                        uithaiguoqianpin.textEdit_S3_AC_FR.setText(textEdit_S3_AC_FR)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[56] in i:
                        textEdit_S3_SPACETIME1 = i[arrayRow1[56]]
                        uithaiguoqianpin.textEdit_S3_SPACETIME1.setText(textEdit_S3_SPACETIME1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[57] in i:
                        textEdit_S3_AC_FR_S1 = i[arrayRow1[57]]
                        uithaiguoqianpin.textEdit_S3_AC_FR_S1.setText(textEdit_S3_AC_FR_S1)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[58] in i:
                        textEdit_S3_SPACETIME2 = i[arrayRow1[58]]
                        uithaiguoqianpin.textEdit_S3_SPACETIME2.setText(textEdit_S3_SPACETIME2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[59] in i:
                        textEdit_S3_AC_FR_S2 = i[arrayRow1[59]]
                        uithaiguoqianpin.textEdit_S3_AC_FR_S2.setText(textEdit_S3_AC_FR_S2)
                    else:
                        strFlag = 1

            else:
                print("no")
                strFlag = "1"

        QMessageBox.information(dialog_windowguoqianpin, "实验设定提示信息", "过欠频文件读取完成", QMessageBox.Ok, QMessageBox.Ok)

