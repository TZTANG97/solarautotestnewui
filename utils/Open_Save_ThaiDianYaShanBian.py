from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, \
    QFileDialog, QMessageBox
import csv

# 上次打开的闪变配置文件路径，供 SCPITestWave.py 读取导出字段对比
last_opened_csv_path = None

arrayRow1 = ['Style',
    'checkBox_S1',
        'comboBox_S1_AC',"textEdit_S1_AC_VOLT", "textEdit_S1_AC_VOLT_2", "textEdit_S1_AC_VOLT_3",
            "textEdit_S1_AC_FR", "comboBox_S1_AC_2",
        "checkBox_S1_DC1", "comboBox_S1_DC1", "textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR",
            "textEdit_S1_DC1_Voc", "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF",
        "checkBox_S1_DC2", "comboBox_S1_DC2", "textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR",
            "textEdit_S1_DC2_Voc", "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF",
        "checkBox_S1_DC3", "comboBox_S1_DC3", "textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR",
            "textEdit_S1_DC3_Voc", "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF",
        "checkBox_S1_DC4", "comboBox_S1_DC4", "textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR",
            "textEdit_S1_DC4_Voc", "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF",
        "textEdit_S1_ACWaitTIME", "comboBox_S1_ACWaitTIME", "textEdit_S1_TIME", "comboBox_S1_TIME",
    "checkBox_S2",
        "comboBox_S2_WT","comboBox_S2_WT3000_Setting", "textEdit_S2_TIME", "comboBox_S2_TIME",
    "checkBox_S3",
        "checkBox_S3_DC1","comboBox_S3_DC1", "checkBox_S3_DC2", "comboBox_S3_DC2",
        "checkBox_S3_DC3", "comboBox_S3_DC3", "checkBox_S3_DC4", "comboBox_S3_DC4",
        "checkBox_S3_DC1_2", "comboBox_S3_DC1_2", "checkBox_S3_DC2_2", "comboBox_S3_DC2_2",
        "checkBox_S3_DC3_2", "comboBox_S3_DC3_2", "checkBox_S3_DC4_2", "comboBox_S3_DC4_2",
        "textEdit_S3_TIME", "comboBox_S3_TIME", "textEdit_S3_TIME_2", "comboBox_S3_TIME_2", "textEdit_S3_CYCLE_TIME",
    "checkBox_S4",
        "comboBox_S4_WT3000_1", "comboBox_S4_WT3000_2", "comboBox_S4_WT3000_3",
    "checkBox_S5",
        "comboBox_S5_AC",
        "checkBox_S5_DC1", "comboBox_S5_DC1","checkBox_S5_DC2", "comboBox_S5_DC2",
        "checkBox_S5_DC3", "comboBox_S5_DC3", "checkBox_S5_DC4", "comboBox_S5_DC4", "comboBox_S2_PER_FLICK_COUNT",
    # 德威创模式配置
    "DEW_mode", "checkBox_DEW_FlickerStandard", "comboBox_DEW_WeightingType",
    "comboBox_DEW_MaxRefreshRate", "textEdit_DEW_NominalVoltage",
    "textEdit_DEW_ShortFlickerTime", "textEdit_DEW_LongFlickerTime",
    "textEdit_DEW_ShortCircuitPower", "checkBox_DEW_RollingCalc",
    "spinBox_DEW_DecimalPlaces", "checkBox_DEW_RealtimeWaveform",
    "treeWidget_DEW_ExportFields", "lineEdit_DEW_StoreFileName",
    ]

#泰国电压闪变保存设定
def Save_File_Thaidianyashanbian(dialog_windowTdianyashanbian, uiThaiDianYaShanBian):
    directory1 = QFileDialog.getSaveFileName(None, "单个文件保存", "./", "Text Files(*.csv)")
    if directory1[0] == '':
        print('请选择一个文件')
    else:
        arrayRow2 = ['ThaiDianYaShanBian']

        # step1
        if uiThaiDianYaShanBian.checkBox_S1.isChecked():
            checkBox_S1 = '1'
        else:
            checkBox_S1 = '0'
        arrayRow2.append(checkBox_S1)

        comboBox_S1_AC = uiThaiDianYaShanBian.comboBox_S1_AC.currentIndex()
        arrayRow2.append(comboBox_S1_AC)

        textEdit_S1_AC_VOLT = uiThaiDianYaShanBian.textEdit_S1_AC_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT)

        textEdit_S1_AC_VOLT_2 = uiThaiDianYaShanBian.textEdit_S1_AC_VOLT_2.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_2)

        textEdit_S1_AC_VOLT_3 = uiThaiDianYaShanBian.textEdit_S1_AC_VOLT_3.toPlainText()
        arrayRow2.append(textEdit_S1_AC_VOLT_3)

        textEdit_S1_AC_FR = uiThaiDianYaShanBian.textEdit_S1_AC_FR.toPlainText()
        arrayRow2.append(textEdit_S1_AC_FR)

        comboBox_S1_AC_2 = uiThaiDianYaShanBian.comboBox_S1_AC_2.currentIndex()
        arrayRow2.append(comboBox_S1_AC_2)

        if uiThaiDianYaShanBian.checkBox_S1_DC1.isChecked():
            checkBox_S1_DC1 = '1'
        else:
            checkBox_S1_DC1 = '0'
        arrayRow2.append(checkBox_S1_DC1)

        comboBox_S1_DC1 = uiThaiDianYaShanBian.comboBox_S1_DC1.currentIndex()
        arrayRow2.append(comboBox_S1_DC1)

        textEdit_S1_DC1_VOLT = uiThaiDianYaShanBian.textEdit_S1_DC1_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_VOLT)

        textEdit_S1_DC1_CURR = uiThaiDianYaShanBian.textEdit_S1_DC1_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_CURR)

        textEdit_S1_DC1_Voc = uiThaiDianYaShanBian.textEdit_S1_DC1_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Voc)
        
        textEdit_S1_DC1_Isc = uiThaiDianYaShanBian.textEdit_S1_DC1_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_Isc)
        
        textEdit_S1_DC1_PF = uiThaiDianYaShanBian.textEdit_S1_DC1_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC1_PF)

        if uiThaiDianYaShanBian.checkBox_S1_DC2.isChecked():
            checkBox_S1_DC2 = '1'
        else:
            checkBox_S1_DC2 = '0'
        arrayRow2.append(checkBox_S1_DC2)

        comboBox_S1_DC2 = uiThaiDianYaShanBian.comboBox_S1_DC2.currentIndex()
        arrayRow2.append(comboBox_S1_DC2)

        textEdit_S1_DC2_VOLT = uiThaiDianYaShanBian.textEdit_S1_DC2_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_VOLT)

        textEdit_S1_DC2_CURR = uiThaiDianYaShanBian.textEdit_S1_DC2_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_CURR)

        textEdit_S1_DC2_Voc = uiThaiDianYaShanBian.textEdit_S1_DC2_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Voc)
        
        textEdit_S1_DC2_Isc = uiThaiDianYaShanBian.textEdit_S1_DC2_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_Isc)
        
        textEdit_S1_DC2_PF = uiThaiDianYaShanBian.textEdit_S1_DC2_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC2_PF)

        if uiThaiDianYaShanBian.checkBox_S1_DC3.isChecked():
            checkBox_S1_DC3 = '1'
        else:
            checkBox_S1_DC3 = '0'
        arrayRow2.append(checkBox_S1_DC3)

        comboBox_S1_DC3 = uiThaiDianYaShanBian.comboBox_S1_DC3.currentIndex()
        arrayRow2.append(comboBox_S1_DC3)

        textEdit_S1_DC3_VOLT = uiThaiDianYaShanBian.textEdit_S1_DC3_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_VOLT)

        textEdit_S1_DC3_CURR = uiThaiDianYaShanBian.textEdit_S1_DC3_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_CURR)

        textEdit_S1_DC3_Voc = uiThaiDianYaShanBian.textEdit_S1_DC3_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Voc)
        
        textEdit_S1_DC3_Isc = uiThaiDianYaShanBian.textEdit_S1_DC3_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_Isc)
        
        textEdit_S1_DC3_PF = uiThaiDianYaShanBian.textEdit_S1_DC3_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC3_PF)

        if uiThaiDianYaShanBian.checkBox_S1_DC4.isChecked():
            checkBox_S1_DC4 = '1'
        else:
            checkBox_S1_DC4 = '0'
        arrayRow2.append(checkBox_S1_DC4)

        comboBox_S1_DC4 = uiThaiDianYaShanBian.comboBox_S1_DC4.currentIndex()
        arrayRow2.append(comboBox_S1_DC4)

        textEdit_S1_DC4_VOLT = uiThaiDianYaShanBian.textEdit_S1_DC4_VOLT.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_VOLT)

        textEdit_S1_DC4_CURR = uiThaiDianYaShanBian.textEdit_S1_DC4_CURR.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_CURR)

        textEdit_S1_DC4_Voc = uiThaiDianYaShanBian.textEdit_S1_DC4_Voc.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Voc)
        
        textEdit_S1_DC4_Isc = uiThaiDianYaShanBian.textEdit_S1_DC4_Isc.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_Isc)
        
        textEdit_S1_DC4_PF = uiThaiDianYaShanBian.textEdit_S1_DC4_PF.toPlainText()
        arrayRow2.append(textEdit_S1_DC4_PF)

        textEdit_S1_ACWaitTIME = uiThaiDianYaShanBian.textEdit_S1_ACWaitTIME.toPlainText()
        arrayRow2.append(textEdit_S1_ACWaitTIME)

        comboBox_S1_ACWaitTIME = uiThaiDianYaShanBian.comboBox_S1_ACWaitTIME.currentIndex()
        arrayRow2.append(comboBox_S1_ACWaitTIME)

        textEdit_S1_TIME = uiThaiDianYaShanBian.textEdit_S1_TIME.toPlainText()
        arrayRow2.append(textEdit_S1_TIME)

        comboBox_S1_TIME = uiThaiDianYaShanBian.comboBox_S1_TIME.currentIndex()
        arrayRow2.append(comboBox_S1_TIME)

        if uiThaiDianYaShanBian.checkBox_S2.isChecked():
            checkBox_S2 = '1'
        else:
            checkBox_S2 = '0'
        arrayRow2.append(checkBox_S2)

        comboBox_S2_WT = uiThaiDianYaShanBian.comboBox_S2_WT.currentIndex()
        arrayRow2.append(comboBox_S2_WT)

        comboBox_S2_WT3000_Setting = uiThaiDianYaShanBian.comboBox_S2_WT3000_Setting.currentIndex()
        arrayRow2.append(comboBox_S2_WT3000_Setting)

        textEdit_S2_TIME = uiThaiDianYaShanBian.textEdit_S2_TIME.toPlainText()
        arrayRow2.append(textEdit_S2_TIME)

        comboBox_S2_TIME = uiThaiDianYaShanBian.comboBox_S2_TIME.currentIndex()
        arrayRow2.append(comboBox_S2_TIME)

        # step3
        if uiThaiDianYaShanBian.checkBox_S3.isChecked():
            checkBox_S3 = '1'
        else:
            checkBox_S3 = '0'
        arrayRow2.append(checkBox_S3)

        if uiThaiDianYaShanBian.checkBox_S3_DC1.isChecked():
            checkBox_S3_DC1 = '1'
        else:
            checkBox_S3_DC1 = '0'
        arrayRow2.append(checkBox_S3_DC1)

        comboBox_S3_DC1 = uiThaiDianYaShanBian.comboBox_S3_DC1.currentIndex()
        arrayRow2.append(comboBox_S3_DC1)

        if uiThaiDianYaShanBian.checkBox_S3_DC2.isChecked():
            checkBox_S3_DC2 = '1'
        else:
            checkBox_S3_DC2 = '0'
        arrayRow2.append(checkBox_S3_DC2)

        comboBox_S3_DC2 = uiThaiDianYaShanBian.comboBox_S3_DC2.currentIndex()
        arrayRow2.append(comboBox_S3_DC2)

        if uiThaiDianYaShanBian.checkBox_S3_DC3.isChecked():
            checkBox_S3_DC3 = '1'
        else:
            checkBox_S3_DC3 = '0'
        arrayRow2.append(checkBox_S3_DC3)

        comboBox_S3_DC3 = uiThaiDianYaShanBian.comboBox_S3_DC3.currentIndex()
        arrayRow2.append(comboBox_S3_DC3)

        if uiThaiDianYaShanBian.checkBox_S3_DC4.isChecked():
            checkBox_S3_DC4 = '1'
        else:
            checkBox_S3_DC4 = '0'
        arrayRow2.append(checkBox_S3_DC4)

        comboBox_S3_DC4 = uiThaiDianYaShanBian.comboBox_S3_DC4.currentIndex()
        arrayRow2.append(comboBox_S3_DC4)

        if uiThaiDianYaShanBian.checkBox_S3_DC1_2.isChecked():
            checkBox_S3_DC1_2 = '1'
        else:
            checkBox_S3_DC1_2 = '0'
        arrayRow2.append(checkBox_S3_DC1_2)

        comboBox_S3_DC1_2 = uiThaiDianYaShanBian.comboBox_S3_DC1_2.currentIndex()
        arrayRow2.append(comboBox_S3_DC1_2)

        if uiThaiDianYaShanBian.checkBox_S3_DC2_2.isChecked():
            checkBox_S3_DC2_2 = '1'
        else:
            checkBox_S3_DC2_2 = '0'
        arrayRow2.append(checkBox_S3_DC2_2)

        comboBox_S3_DC2_2 = uiThaiDianYaShanBian.comboBox_S3_DC2_2.currentIndex()
        arrayRow2.append(comboBox_S3_DC2_2)

        if uiThaiDianYaShanBian.checkBox_S3_DC3_2.isChecked():
            checkBox_S3_DC3_2 = '1'
        else:
            checkBox_S3_DC3_2 = '0'
        arrayRow2.append(checkBox_S3_DC3_2)

        comboBox_S3_DC3_2 = uiThaiDianYaShanBian.comboBox_S3_DC3_2.currentIndex()
        arrayRow2.append(comboBox_S3_DC3_2)

        if uiThaiDianYaShanBian.checkBox_S3_DC4_2.isChecked():
            checkBox_S3_DC4_2 = '1'
        else:
            checkBox_S3_DC4_2 = '0'
        arrayRow2.append(checkBox_S3_DC4_2)

        comboBox_S3_DC4_2 = uiThaiDianYaShanBian.comboBox_S3_DC4_2.currentIndex()
        arrayRow2.append(comboBox_S3_DC4_2)

        textEdit_S3_TIME = uiThaiDianYaShanBian.textEdit_S3_TIME.toPlainText()
        arrayRow2.append(textEdit_S3_TIME)

        comboBox_S3_TIME = uiThaiDianYaShanBian.comboBox_S3_TIME.currentIndex()
        arrayRow2.append(comboBox_S3_TIME)

        textEdit_S3_TIME_2 = uiThaiDianYaShanBian.textEdit_S3_TIME_2.toPlainText()
        arrayRow2.append(textEdit_S3_TIME_2)

        comboBox_S3_TIME_2 = uiThaiDianYaShanBian.comboBox_S3_TIME_2.currentIndex()
        arrayRow2.append(comboBox_S3_TIME_2)

        textEdit_S3_CYCLE_TIME = uiThaiDianYaShanBian.textEdit_S3_CYCLE_TIME.toPlainText()
        arrayRow2.append(textEdit_S3_CYCLE_TIME)

        # step4
        if uiThaiDianYaShanBian.checkBox_S4.isChecked():
            checkBox_S4 = '1'
        else:
            checkBox_S4 = '0'
        arrayRow2.append(checkBox_S4)

        comboBox_S4_WT3000_1 = uiThaiDianYaShanBian.comboBox_S4_WT3000_1.currentIndex()
        arrayRow2.append(comboBox_S4_WT3000_1)

        comboBox_S4_WT3000_2 = uiThaiDianYaShanBian.comboBox_S4_WT3000_2.currentIndex()
        arrayRow2.append(comboBox_S4_WT3000_2)

        comboBox_S4_WT3000_3 = uiThaiDianYaShanBian.comboBox_S4_WT3000_3.currentIndex()
        arrayRow2.append(comboBox_S4_WT3000_3)

        # step5
        if uiThaiDianYaShanBian.checkBox_S5.isChecked():
            checkBox_S5 = '1'
        else:
            checkBox_S5 = '0'
        arrayRow2.append(checkBox_S5)

        comboBox_S5_AC = uiThaiDianYaShanBian.comboBox_S5_AC.currentIndex()
        arrayRow2.append(comboBox_S5_AC)

        if uiThaiDianYaShanBian.checkBox_S5_DC1.isChecked():
            checkBox_S5_DC1 = '1'
        else:
            checkBox_S5_DC1 = '0'
        arrayRow2.append(checkBox_S5_DC1)

        comboBox_S5_DC1 = uiThaiDianYaShanBian.comboBox_S5_DC1.currentIndex()
        arrayRow2.append(comboBox_S5_DC1)

        if uiThaiDianYaShanBian.checkBox_S5_DC2.isChecked():
            checkBox_S5_DC2 = '1'
        else:
            checkBox_S5_DC2 = '0'
        arrayRow2.append(checkBox_S5_DC2)

        comboBox_S5_DC2 = uiThaiDianYaShanBian.comboBox_S5_DC2.currentIndex()
        arrayRow2.append(comboBox_S5_DC2)

        if uiThaiDianYaShanBian.checkBox_S5_DC3.isChecked():
            checkBox_S5_DC3 = '1'
        else:
            checkBox_S5_DC3 = '0'
        arrayRow2.append(checkBox_S5_DC3)

        comboBox_S5_DC3 = uiThaiDianYaShanBian.comboBox_S5_DC3.currentIndex()
        arrayRow2.append(comboBox_S5_DC3)

        if uiThaiDianYaShanBian.checkBox_S5_DC4.isChecked():
            checkBox_S5_DC4 = '1'
        else:
            checkBox_S5_DC4 = '0'
        arrayRow2.append(checkBox_S5_DC4)

        comboBox_S5_DC4 = uiThaiDianYaShanBian.comboBox_S5_DC4.currentIndex()
        arrayRow2.append(comboBox_S5_DC4)

        comboBox_S2_PER_FLICK_COUNT = uiThaiDianYaShanBian.comboBox_S2_PER_FLICK_COUNT.currentIndex()
        arrayRow2.append(comboBox_S2_PER_FLICK_COUNT)

        # 德威创模式配置
        dew_mode = getattr(uiThaiDianYaShanBian, '_mode', 'wt3000')
        arrayRow2.append(dew_mode)

        if uiThaiDianYaShanBian.checkBox_DEW_FlickerStandard.isChecked():
            arrayRow2.append('1')
        else:
            arrayRow2.append('0')

        arrayRow2.append(uiThaiDianYaShanBian.comboBox_DEW_WeightingType.currentIndex())
        arrayRow2.append(uiThaiDianYaShanBian.comboBox_DEW_MaxRefreshRate.currentIndex())
        arrayRow2.append(uiThaiDianYaShanBian.textEdit_DEW_NominalVoltage.toPlainText())
        arrayRow2.append(uiThaiDianYaShanBian.textEdit_DEW_ShortFlickerTime.toPlainText())
        arrayRow2.append(uiThaiDianYaShanBian.textEdit_DEW_LongFlickerTime.toPlainText())
        arrayRow2.append(uiThaiDianYaShanBian.textEdit_DEW_ShortCircuitPower.toPlainText())

        if uiThaiDianYaShanBian.checkBox_DEW_RollingCalc.isChecked():
            arrayRow2.append('1')
        else:
            arrayRow2.append('0')

        # 德威创导出设置
        arrayRow2.append(uiThaiDianYaShanBian.spinBox_DEW_DecimalPlaces.value())
        arrayRow2.append('1' if uiThaiDianYaShanBian.checkBox_DEW_RealtimeWaveform.isChecked() else '0')
        checked_fields = uiThaiDianYaShanBian.get_checked_export_fields()
        arrayRow2.append('|'.join(checked_fields))
        arrayRow2.append(uiThaiDianYaShanBian.lineEdit_DEW_StoreFileName.text())

        out = open(directory1[0], 'w+', newline='', encoding='utf-8-sig')
        csv_write = csv.writer(out, dialect="excel")
        csv_write.writerow(arrayRow1)
        csv_write.writerow(arrayRow2)
        out.close()
        QMessageBox.information(None, "实验设定提示信息", "电压闪变文件保存完成", QMessageBox.Ok, QMessageBox.Ok)

#泰国电压闪变读取设定
def Open_File_ThaiDianYaShanBian(dialog_windowTdianyashanbian, uiThaiDianYaShanBian):
    global last_opened_csv_path
    strFlag = "0"
    directory1 = QFileDialog.getOpenFileName(None, "单个文件选择", "./", "Text Files(*.csv)")
    if directory1[0] == '':
        print("请选择一个文件")
    else:
        last_opened_csv_path = directory1[0]

        try:
            f1 = open(directory1[0], 'r', encoding='utf-8-sig')
            f1.read(1)
            f1.seek(0)
        except UnicodeDecodeError:
            f1 = open(directory1[0], 'r', encoding='gbk')
        reader = csv.DictReader(f1)
        # print(reader)
        for i in reader:
            print(i)

        if arrayRow1[0] in i:
            if i[arrayRow1[0]] == "ThaiDianYaShanBian":
                # checkBox
                if strFlag == "0":
                    if arrayRow1[1] in i:
                        checkBox_S1 = i[arrayRow1[1]]
                        if checkBox_S1 == '1':
                            uiThaiDianYaShanBian.checkBox_S1.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S1.setChecked(False)
                    else:
                        strFlag = 1

                #comBox
                if strFlag == "0":
                    if arrayRow1[2] in i:
                        comboBox_S1_AC = i[arrayRow1[2]]
                        uiThaiDianYaShanBian.comboBox_S1_AC.setCurrentIndex(int(comboBox_S1_AC))
                    else:
                        strFlag = 1

                #textEdit
                if strFlag == "0":
                    if arrayRow1[3] in i:
                        textEdit_S1_AC_VOLT = i[arrayRow1[3]]
                        uiThaiDianYaShanBian.textEdit_S1_AC_VOLT.setText(textEdit_S1_AC_VOLT)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[4] in i:
                        textEdit_S1_AC_VOLT_2 = i[arrayRow1[4]]
                        uiThaiDianYaShanBian.textEdit_S1_AC_VOLT_2.setText(textEdit_S1_AC_VOLT_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[5] in i:
                        textEdit_S1_AC_VOLT_3 = i[arrayRow1[5]]
                        uiThaiDianYaShanBian.textEdit_S1_AC_VOLT_3.setText(textEdit_S1_AC_VOLT_3)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[6] in i:
                        textEdit_S1_AC_FR = i[arrayRow1[6]]
                        uiThaiDianYaShanBian.textEdit_S1_AC_FR.setText(textEdit_S1_AC_FR)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[7] in i:
                        comboBox_S1_AC_2 = i[arrayRow1[7]]
                        uiThaiDianYaShanBian.comboBox_S1_AC_2.setCurrentIndex(int(comboBox_S1_AC_2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[8] in i:
                        checkBox_S1_DC1 = i[arrayRow1[8]]
                        if checkBox_S1_DC1 == '1':
                            uiThaiDianYaShanBian.checkBox_S1_DC1.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S1_DC1.setChecked(False)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[9] in i:
                        comboBox_S1_DC1 = i[arrayRow1[9]]
                        uiThaiDianYaShanBian.comboBox_S1_DC1.setCurrentIndex(int(comboBox_S1_DC1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[10] in i:
                        textEdit_S1_DC1_VOLT = i[arrayRow1[10]]
                        uiThaiDianYaShanBian.textEdit_S1_DC1_VOLT.setText(textEdit_S1_DC1_VOLT)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[11] in i:
                        textEdit_S1_DC1_CURR = i[arrayRow1[11]]
                        uiThaiDianYaShanBian.textEdit_S1_DC1_CURR.setText(textEdit_S1_DC1_CURR)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[12] in i:
                        textEdit_S1_DC1_Voc = i[arrayRow1[12]]
                        uiThaiDianYaShanBian.textEdit_S1_DC1_Voc.setText(textEdit_S1_DC1_Voc)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[13] in i:
                        textEdit_S1_DC1_Isc = i[arrayRow1[13]]
                        uiThaiDianYaShanBian.textEdit_S1_DC1_Isc.setText(textEdit_S1_DC1_Isc)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[14] in i:
                        textEdit_S1_DC1_PF = i[arrayRow1[14]]
                        uiThaiDianYaShanBian.textEdit_S1_DC1_PF.setText(textEdit_S1_DC1_PF)
                    else:
                        strFlag = 1
                        
                if strFlag == "0":
                    if arrayRow1[15] in i:
                        checkBox_S1_DC2 = i[arrayRow1[15]]
                        if checkBox_S1_DC2 == '1':
                            uiThaiDianYaShanBian.checkBox_S1_DC2.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S1_DC2.setChecked(False)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[16] in i:
                        comboBox_S1_DC2 = i[arrayRow1[16]]
                        uiThaiDianYaShanBian.comboBox_S1_DC2.setCurrentIndex(int(comboBox_S1_DC2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[17] in i:
                        textEdit_S1_DC2_VOLT = i[arrayRow1[17]]
                        uiThaiDianYaShanBian.textEdit_S1_DC2_VOLT.setText(textEdit_S1_DC2_VOLT)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[18] in i:
                        textEdit_S1_DC2_CURR = i[arrayRow1[18]]
                        uiThaiDianYaShanBian.textEdit_S1_DC2_CURR.setText(textEdit_S1_DC2_CURR)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[19] in i:
                        textEdit_S1_DC2_Voc = i[arrayRow1[19]]
                        uiThaiDianYaShanBian.textEdit_S1_DC2_Voc.setText(textEdit_S1_DC2_Voc)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[20] in i:
                        textEdit_S1_DC2_Isc = i[arrayRow1[20]]
                        uiThaiDianYaShanBian.textEdit_S1_DC2_Isc.setText(textEdit_S1_DC2_Isc)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[21] in i:
                        textEdit_S1_DC2_PF = i[arrayRow1[21]]
                        uiThaiDianYaShanBian.textEdit_S1_DC2_PF.setText(textEdit_S1_DC2_PF)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[22] in i:
                        checkBox_S1_DC3 = i[arrayRow1[22]]
                        if checkBox_S1_DC3 == '1':
                            uiThaiDianYaShanBian.checkBox_S1_DC3.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S1_DC3.setChecked(False)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[23] in i:
                        comboBox_S1_DC3 = i[arrayRow1[23]]
                        uiThaiDianYaShanBian.comboBox_S1_DC3.setCurrentIndex(int(comboBox_S1_DC3))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[24] in i:
                        textEdit_S1_DC3_VOLT = i[arrayRow1[24]]
                        uiThaiDianYaShanBian.textEdit_S1_DC3_VOLT.setText(textEdit_S1_DC3_VOLT)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[25] in i:
                        textEdit_S1_DC3_CURR = i[arrayRow1[25]]
                        uiThaiDianYaShanBian.textEdit_S1_DC3_CURR.setText(textEdit_S1_DC3_CURR)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[26] in i:
                        textEdit_S1_DC3_Voc = i[arrayRow1[26]]
                        uiThaiDianYaShanBian.textEdit_S1_DC3_Voc.setText(textEdit_S1_DC3_Voc)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[27] in i:
                        textEdit_S1_DC3_Isc = i[arrayRow1[27]]
                        uiThaiDianYaShanBian.textEdit_S1_DC3_Isc.setText(textEdit_S1_DC3_Isc)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[28] in i:
                        textEdit_S1_DC3_PF = i[arrayRow1[28]]
                        uiThaiDianYaShanBian.textEdit_S1_DC3_PF.setText(textEdit_S1_DC3_PF)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[29] in i:
                        checkBox_S1_DC4 = i[arrayRow1[29]]
                        if checkBox_S1_DC4 == '1':
                            uiThaiDianYaShanBian.checkBox_S1_DC4.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S1_DC4.setChecked(False)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[30] in i:
                        comboBox_S1_DC4 = i[arrayRow1[30]]
                        uiThaiDianYaShanBian.comboBox_S1_DC4.setCurrentIndex(int(comboBox_S1_DC4))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[31] in i:
                        textEdit_S1_DC4_VOLT = i[arrayRow1[31]]
                        uiThaiDianYaShanBian.textEdit_S1_DC4_VOLT.setText(textEdit_S1_DC4_VOLT)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[32] in i:
                        textEdit_S1_DC4_CURR = i[arrayRow1[32]]
                        uiThaiDianYaShanBian.textEdit_S1_DC4_CURR.setText(textEdit_S1_DC4_CURR)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[33] in i:
                        textEdit_S1_DC4_Voc = i[arrayRow1[33]]
                        uiThaiDianYaShanBian.textEdit_S1_DC4_Voc.setText(textEdit_S1_DC4_Voc)
                    else:
                        strFlag = 1
                
                if strFlag == "0":
                    if arrayRow1[34] in i:
                        textEdit_S1_DC4_Isc = i[arrayRow1[34]]
                        uiThaiDianYaShanBian.textEdit_S1_DC4_Isc.setText(textEdit_S1_DC4_Isc)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[35] in i:
                        textEdit_S1_DC4_PF = i[arrayRow1[35]]
                        uiThaiDianYaShanBian.textEdit_S1_DC4_PF.setText(textEdit_S1_DC4_PF)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[36] in i:
                        textEdit_S1_ACWaitTIME = i[arrayRow1[36]]
                        uiThaiDianYaShanBian.textEdit_S1_ACWaitTIME.setText(textEdit_S1_ACWaitTIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[37] in i:
                        comboBox_S1_ACWaitTIME = i[arrayRow1[37]]
                        uiThaiDianYaShanBian.comboBox_S1_ACWaitTIME.setCurrentIndex(int(comboBox_S1_ACWaitTIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[38] in i:
                        textEdit_S1_TIME = i[arrayRow1[38]]
                        uiThaiDianYaShanBian.textEdit_S1_TIME.setText(textEdit_S1_TIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[39] in i:
                        comboBox_S1_TIME = i[arrayRow1[39]]
                        uiThaiDianYaShanBian.comboBox_S1_TIME.setCurrentIndex(int(comboBox_S1_TIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[40] in i:
                        checkBox_S2 = i[arrayRow1[40]]
                        if checkBox_S2 == '1':
                            uiThaiDianYaShanBian.checkBox_S2.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[41] in i:
                        comboBox_S2_WT = i[arrayRow1[41]]
                        uiThaiDianYaShanBian.comboBox_S2_WT.setCurrentIndex(int(comboBox_S2_WT))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[42] in i:
                        comboBox_S2_WT3000_Setting = i[arrayRow1[42]]
                        uiThaiDianYaShanBian.comboBox_S2_WT3000_Setting.setCurrentIndex(int(comboBox_S2_WT3000_Setting))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[43] in i:
                        textEdit_S2_TIME = i[arrayRow1[43]]
                        uiThaiDianYaShanBian.textEdit_S2_TIME.setText(textEdit_S2_TIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[44] in i:
                        comboBox_S2_TIME = i[arrayRow1[44]]
                        uiThaiDianYaShanBian.comboBox_S2_TIME.setCurrentIndex(int(comboBox_S2_TIME))
                    else:
                        strFlag = 1

                # step3
                if strFlag == "0":
                    if arrayRow1[45] in i:
                        checkBox_S3 = i[arrayRow1[45]]
                        if checkBox_S3 == '1':
                            uiThaiDianYaShanBian.checkBox_S3.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S3.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[46] in i:
                        checkBox_S3_DC1 = i[arrayRow1[46]]
                        if checkBox_S3_DC1 == '1':
                            uiThaiDianYaShanBian.checkBox_S3_DC1.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S3_DC1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[47] in i:
                        comboBox_S3_DC1 = i[arrayRow1[47]]
                        uiThaiDianYaShanBian.comboBox_S3_DC1.setCurrentIndex(int(comboBox_S3_DC1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[48] in i:
                        checkBox_S3_DC2 = i[arrayRow1[48]]
                        if checkBox_S3_DC2 == '1':
                            uiThaiDianYaShanBian.checkBox_S3_DC2.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S3_DC2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[49] in i:
                        comboBox_S3_DC2 = i[arrayRow1[49]]
                        uiThaiDianYaShanBian.comboBox_S3_DC2.setCurrentIndex(int(comboBox_S3_DC2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[50] in i:
                        checkBox_S3_DC3 = i[arrayRow1[50]]
                        if checkBox_S3_DC3 == '1':
                            uiThaiDianYaShanBian.checkBox_S3_DC3.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S3_DC3.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[51] in i:
                        comboBox_S3_DC3 = i[arrayRow1[51]]
                        uiThaiDianYaShanBian.comboBox_S3_DC3.setCurrentIndex(int(comboBox_S3_DC3))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[52] in i:
                        checkBox_S3_DC4 = i[arrayRow1[52]]
                        if checkBox_S3_DC4 == '1':
                            uiThaiDianYaShanBian.checkBox_S3_DC4.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S3_DC4.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[53] in i:
                        comboBox_S3_DC4 = i[arrayRow1[53]]
                        uiThaiDianYaShanBian.comboBox_S3_DC4.setCurrentIndex(int(comboBox_S3_DC4))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[54] in i:
                        checkBox_S3_DC1_2 = i[arrayRow1[54]]
                        if checkBox_S3_DC1_2 == '1':
                            uiThaiDianYaShanBian.checkBox_S3_DC1_2.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S3_DC1_2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[55] in i:
                        comboBox_S3_DC1_2 = i[arrayRow1[55]]
                        uiThaiDianYaShanBian.comboBox_S3_DC1_2.setCurrentIndex(int(comboBox_S3_DC1_2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[56] in i:
                        checkBox_S3_DC2_2 = i[arrayRow1[56]]
                        if checkBox_S3_DC2_2 == '1':
                            uiThaiDianYaShanBian.checkBox_S3_DC2_2.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S3_DC2_2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[57] in i:
                        comboBox_S3_DC2_2 = i[arrayRow1[57]]
                        uiThaiDianYaShanBian.comboBox_S3_DC2_2.setCurrentIndex(int(comboBox_S3_DC2_2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[58] in i:
                        checkBox_S3_DC3_2 = i[arrayRow1[58]]
                        if checkBox_S3_DC3_2 == '1':
                            uiThaiDianYaShanBian.checkBox_S3_DC3_2.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S3_DC3_2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[59] in i:
                        comboBox_S3_DC3_2 = i[arrayRow1[59]]
                        uiThaiDianYaShanBian.comboBox_S3_DC3_2.setCurrentIndex(int(comboBox_S3_DC3_2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[60] in i:
                        checkBox_S3_DC4_2 = i[arrayRow1[60]]
                        if checkBox_S3_DC4_2 == '1':
                            uiThaiDianYaShanBian.checkBox_S3_DC4_2.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S3_DC4_2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[61] in i:
                        comboBox_S3_DC4_2 = i[arrayRow1[61]]
                        uiThaiDianYaShanBian.comboBox_S3_DC4_2.setCurrentIndex(int(comboBox_S3_DC4_2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[62] in i:
                        textEdit_S3_TIME = i[arrayRow1[62]]
                        uiThaiDianYaShanBian.textEdit_S3_TIME.setText(textEdit_S3_TIME)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[63] in i:
                        comboBox_S3_TIME = i[arrayRow1[63]]
                        uiThaiDianYaShanBian.comboBox_S3_TIME.setCurrentIndex(int(comboBox_S3_TIME))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[64] in i:
                        textEdit_S3_TIME_2 = i[arrayRow1[64]]
                        uiThaiDianYaShanBian.textEdit_S3_TIME_2.setText(textEdit_S3_TIME_2)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[65] in i:
                        comboBox_S3_TIME_2 = i[arrayRow1[65]]
                        uiThaiDianYaShanBian.comboBox_S3_TIME_2.setCurrentIndex(int(comboBox_S3_TIME_2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[66] in i:
                        textEdit_S3_CYCLE_TIME = i[arrayRow1[66]]
                        uiThaiDianYaShanBian.textEdit_S3_CYCLE_TIME.setText(textEdit_S3_CYCLE_TIME)
                    else:
                        strFlag = 1

                # step4
                if strFlag == "0":
                    if arrayRow1[67] in i:
                        checkBox_S4 = i[arrayRow1[67]]
                        if checkBox_S4 == '1':
                            uiThaiDianYaShanBian.checkBox_S4.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S4.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[68] in i:
                        comboBox_S4_WT3000_1 = i[arrayRow1[68]]
                        uiThaiDianYaShanBian.comboBox_S4_WT3000_1.setCurrentIndex(int(comboBox_S4_WT3000_1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[69] in i:
                        comboBox_S4_WT3000_2 = i[arrayRow1[69]]
                        uiThaiDianYaShanBian.comboBox_S4_WT3000_2.setCurrentIndex(int(comboBox_S4_WT3000_2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[70] in i:
                        comboBox_S4_WT3000_3 = i[arrayRow1[70]]
                        uiThaiDianYaShanBian.comboBox_S4_WT3000_3.setCurrentIndex(int(comboBox_S4_WT3000_3))
                    else:
                        strFlag = 1

                # step5
                if strFlag == "0":
                    if arrayRow1[71] in i:
                        checkBox_S5 = i[arrayRow1[71]]
                        if checkBox_S5 == '1':
                            uiThaiDianYaShanBian.checkBox_S5.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S5.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[72] in i:
                        comboBox_S5_AC = i[arrayRow1[72]]
                        uiThaiDianYaShanBian.comboBox_S5_AC.setCurrentIndex(int(comboBox_S5_AC))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[73] in i:
                        checkBox_S5_DC1 = i[arrayRow1[73]]
                        if checkBox_S5_DC1 == '1':
                            uiThaiDianYaShanBian.checkBox_S5_DC1.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S5_DC1.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[74] in i:
                        comboBox_S5_DC1 = i[arrayRow1[74]]
                        uiThaiDianYaShanBian.comboBox_S5_DC1.setCurrentIndex(int(comboBox_S5_DC1))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[75] in i:
                        checkBox_S5_DC2 = i[arrayRow1[75]]
                        if checkBox_S5_DC2 == '1':
                            uiThaiDianYaShanBian.checkBox_S5_DC2.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S5_DC2.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[76] in i:
                        comboBox_S5_DC2 = i[arrayRow1[76]]
                        uiThaiDianYaShanBian.comboBox_S5_DC2.setCurrentIndex(int(comboBox_S5_DC2))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[77] in i:
                        checkBox_S5_DC3 = i[arrayRow1[77]]
                        if checkBox_S5_DC3 == '1':
                            uiThaiDianYaShanBian.checkBox_S5_DC3.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S5_DC3.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[78] in i:
                        comboBox_S5_DC3 = i[arrayRow1[78]]
                        uiThaiDianYaShanBian.comboBox_S5_DC3.setCurrentIndex(int(comboBox_S5_DC3))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[79] in i:
                        checkBox_S5_DC4 = i[arrayRow1[79]]
                        if checkBox_S5_DC4 == '1':
                            uiThaiDianYaShanBian.checkBox_S5_DC4.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.checkBox_S5_DC4.setChecked(False)
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[80] in i:
                        comboBox_S5_DC4 = i[arrayRow1[80]]
                        uiThaiDianYaShanBian.comboBox_S5_DC4.setCurrentIndex(int(comboBox_S5_DC4))
                    else:
                        strFlag = 1

                if strFlag == "0":
                    if arrayRow1[81] in i:
                        comboBox_S2_PER_FLICK_COUNT = i[arrayRow1[81]]
                        uiThaiDianYaShanBian.comboBox_S2_PER_FLICK_COUNT.setCurrentIndex(int(comboBox_S2_PER_FLICK_COUNT))
                    else:
                        strFlag = 1

                # 德威创模式配置（兼容旧文件：无 DEWETRON 字段时跳过）
                if strFlag == "0" and len(arrayRow1) > 82:
                    if arrayRow1[82] in i:
                        dew_mode = i[arrayRow1[82]]
                        if dew_mode == 'dewetron':
                            uiThaiDianYaShanBian.radio_dewetron.setChecked(True)
                        else:
                            uiThaiDianYaShanBian.radio_wt3000.setChecked(True)
                    else:
                        uiThaiDianYaShanBian.radio_wt3000.setChecked(True)

                if strFlag == "0" and len(arrayRow1) > 83:
                    if arrayRow1[83] in i:
                        val = i[arrayRow1[83]]
                        uiThaiDianYaShanBian.checkBox_DEW_FlickerStandard.setChecked(val == '1')

                if strFlag == "0" and len(arrayRow1) > 84:
                    if arrayRow1[84] in i:
                        uiThaiDianYaShanBian.comboBox_DEW_WeightingType.setCurrentIndex(int(i[arrayRow1[84]]))

                if strFlag == "0" and len(arrayRow1) > 85:
                    if arrayRow1[85] in i:
                        uiThaiDianYaShanBian.comboBox_DEW_MaxRefreshRate.setCurrentIndex(int(i[arrayRow1[85]]))

                if strFlag == "0" and len(arrayRow1) > 86:
                    if arrayRow1[86] in i:
                        uiThaiDianYaShanBian.textEdit_DEW_NominalVoltage.setText(i[arrayRow1[86]])

                if strFlag == "0" and len(arrayRow1) > 87:
                    if arrayRow1[87] in i:
                        uiThaiDianYaShanBian.textEdit_DEW_ShortFlickerTime.setText(i[arrayRow1[87]])

                if strFlag == "0" and len(arrayRow1) > 88:
                    if arrayRow1[88] in i:
                        uiThaiDianYaShanBian.textEdit_DEW_LongFlickerTime.setText(i[arrayRow1[88]])

                if strFlag == "0" and len(arrayRow1) > 89:
                    if arrayRow1[89] in i:
                        uiThaiDianYaShanBian.textEdit_DEW_ShortCircuitPower.setText(i[arrayRow1[89]])

                if strFlag == "0" and len(arrayRow1) > 90:
                    if arrayRow1[90] in i:
                        val = i[arrayRow1[90]]
                        uiThaiDianYaShanBian.checkBox_DEW_RollingCalc.setChecked(val == '1')

                # 德威创导出设置
                if strFlag == "0" and len(arrayRow1) > 91:
                    if arrayRow1[91] in i:
                        uiThaiDianYaShanBian.spinBox_DEW_DecimalPlaces.setValue(int(i[arrayRow1[91]]))

                if strFlag == "0" and len(arrayRow1) > 92:
                    if arrayRow1[92] in i:
                        uiThaiDianYaShanBian.checkBox_DEW_RealtimeWaveform.setChecked(i[arrayRow1[92]] == '1')

                if strFlag == "0" and len(arrayRow1) > 93:
                    if arrayRow1[93] in i:
                        fields_str = i[arrayRow1[93]]
                        if fields_str:
                            fields_list = [f.strip() for f in fields_str.split('|') if f.strip()]
                            uiThaiDianYaShanBian.set_checked_export_fields(fields_list)

                if strFlag == "0" and len(arrayRow1) > 94:
                    if arrayRow1[94] in i:
                        uiThaiDianYaShanBian.lineEdit_DEW_StoreFileName.setText(i[arrayRow1[94]])

        QMessageBox.information(None, "实验设定提示信息", "电压闪变文件读取完成", QMessageBox.Ok, QMessageBox.Ok)

def save_file_header():
    directory1 = [r"D:\\project\\photovoltaic_automation_t\\config_files\\project_step_configs\\dianyashanbian.csv"]
    if directory1[0] == '':
        print('请选择一个文件')
    else:
        out = open(directory1[0], 'w+', newline='', encoding='utf-8-sig')
        csv_write = csv.writer(out, dialect="excel")
        csv_write.writerow(arrayRow1)
        out.close()

if __name__ == "__main__":
    save_file_header()
    # print(len(arrayRow1))
