from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow,QApplication,QDialog,QFileDialog, QMessageBox
import csv
from utils.Open_Save_ThaiWT3000_Config import Save_File_ThaiWT3000_Config, Open_File_ThaiWT3000_Config
from utils.Open_Save_ThaiWT1800_Config import Save_File_ThaiWT1800_Config, Open_File_ThaiWT1800_Config
from utils.Open_Save_ThaiWT1806E_Config import Save_File_ThaiWT1806E_Config, Open_File_ThaiWT1806E_Config
from utils.Open_Save_ThaiWT5000_Config import Save_File_ThaiWT5000_Config, Open_File_ThaiWT5000_Config


class _PageWidgetFinder:
    """代理对象，通过 findChild 在正确的 stacked page 中按 objectName 查找 widget。
    解决 4 个 build_wt*_content(self) 共享 self 导致同名属性被覆盖的问题。"""

    def __init__(self, page_widget):
        self._page = page_widget

    def __getattr__(self, name):
        # 先在 page 子树中按 objectName 查找
        w = self._page.findChild(QtWidgets.QWidget, name)
        if w is not None:
            return w
        raise AttributeError(f"Widget '{name}' not found in stacked page")

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
    print("=" * 80)
    print("[DEBUG-SAVE] ==================== 开始保存谐波电流配置 ====================")
    dialog_windowxiebodianliu = kwargs['dialog_windowxiebodianliu']
    uiThaiXieBoDianLiu = kwargs['uiThaiXieBoDianLiu']
    uiThiaWT3000E = kwargs['uiThiaWT3000E']
    uiThiaWT1800 = kwargs['uiThiaWT1800']
    uiThiaWT1806E = kwargs['uiThiaWT1806E']
    uiThiaWT5000 = kwargs['uiThiaWT5000']
    print(f"[DEBUG-SAVE] uiThaiXieBoDianLiu type: {type(uiThaiXieBoDianLiu)}")
    print(f"[DEBUG-SAVE] has _wtStacked: {hasattr(uiThaiXieBoDianLiu, '_wtStacked')}")
    if hasattr(uiThaiXieBoDianLiu, '_wtStacked'):
        print(f"[DEBUG-SAVE] _wtStacked count: {uiThaiXieBoDianLiu._wtStacked.count()}, current: {uiThaiXieBoDianLiu._wtStacked.currentIndex()}")
    result = []
    directory1 = QFileDialog.getSaveFileName(None, "单个文件保存", "./", "Text Files(*.csv)")
    if directory1[0] == '':
        print('[DEBUG-SAVE] 用户取消了文件选择')
    else:
        print(f"[DEBUG-SAVE] 保存到文件: {directory1[0]}")
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

        print(f"[DEBUG-SAVE] step1 数据收集完成，arrayRow2 列数: {len(arrayRow2)}")
        print(f"[DEBUG-SAVE] step1: checkBox_S1={checkBox_S1}, AC={comboBox_S1_AC}, DC1={checkBox_S1_DC1}, DC2={checkBox_S1_DC2}, DC3={checkBox_S1_DC3}, DC4={checkBox_S1_DC4}")

        # step2
        if uiThaiXieBoDianLiu.checkBox_S2.isChecked():
            checkBox_S2 = '1'
        else:
            checkBox_S2 = '0'
        arrayRow2.append(checkBox_S2)

        if uiThaiXieBoDianLiu.radioButton_S2_WT3000.isChecked():
            checkBox_S2_WT3000 = '1'
        else:
            checkBox_S2_WT3000 = '0'
        arrayRow2.append(checkBox_S2_WT3000)

        if uiThaiXieBoDianLiu.radioButton_S2_WT1800.isChecked():
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

        if uiThaiXieBoDianLiu.radioButton_S2_WT1806E.isChecked():
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

        if uiThaiXieBoDianLiu.radioButton_S2_WT5000.isChecked():
            checkBox_S2_WT5000 = '1'
        else:
            checkBox_S2_WT5000 = '0'
        arrayRow2.append(checkBox_S2_WT5000)

        print(f"[DEBUG-SAVE] step2/3 数据收集完成，arrayRow2 总列数: {len(arrayRow2)}")
        print(f"[DEBUG-SAVE] step2: checkBox_S2={checkBox_S2}, WT3000={checkBox_S2_WT3000}, WT1800={checkBox_S2_WT1800}, WT1806E={checkBox_S2_WT1806E}, WT5000={checkBox_S2_WT5000}")

        # 根据选中的 radio 保存对应的 WT 配置
        print(f"[DEBUG-SAVE] --- 开始保存 WT 配置 ---")
        print(f"[DEBUG-SAVE] WT3000 radio checked: {uiThaiXieBoDianLiu.radioButton_S2_WT3000.isChecked()}")
        print(f"[DEBUG-SAVE] WT1800 radio checked: {uiThaiXieBoDianLiu.radioButton_S2_WT1800.isChecked()}")
        print(f"[DEBUG-SAVE] WT1806E radio checked: {uiThaiXieBoDianLiu.radioButton_S2_WT1806E.isChecked()}")
        print(f"[DEBUG-SAVE] WT5000 radio checked: {uiThaiXieBoDianLiu.radioButton_S2_WT5000.isChecked()}")

        if uiThaiXieBoDianLiu.radioButton_S2_WT3000.isChecked():
            print("[DEBUG-SAVE] 调用 Save_File_ThaiWT3000_Config (page index=0)")
            page = uiThaiXieBoDianLiu._wtStacked.widget(0)
            finder = _PageWidgetFinder(page)
            # 测试 finder 能否找到 combobox
            try:
                test_combo = finder.comboBox_SigmA1
                print(f"[DEBUG-SAVE] finder.comboBox_SigmA1 找到: {test_combo}, currentIndex={test_combo.currentIndex()}, items={test_combo.count()}")
            except Exception as e:
                print(f"[DEBUG-SAVE] finder.comboBox_SigmA1 找不到: {e}")
            result = Save_File_ThaiWT3000_Config(finder)
            print(f"[DEBUG-SAVE] WT3000 保存结果: {'有数据' if len(result) > 0 else '空'}, 行数={len(result)}")

        if uiThaiXieBoDianLiu.radioButton_S2_WT1800.isChecked():
            print("[DEBUG-SAVE] 调用 Save_File_ThaiWT1800_Config (page index=1)")
            page = uiThaiXieBoDianLiu._wtStacked.widget(1)
            finder = _PageWidgetFinder(page)
            try:
                test_combo = finder.comboBox_SigmA1
                print(f"[DEBUG-SAVE] finder.comboBox_SigmA1 找到: {test_combo}, currentIndex={test_combo.currentIndex()}, items={test_combo.count()}")
            except Exception as e:
                print(f"[DEBUG-SAVE] finder.comboBox_SigmA1 找不到: {e}")
            result = Save_File_ThaiWT1800_Config(finder)
            print(f"[DEBUG-SAVE] WT1800 保存结果: {'有数据' if len(result) > 0 else '空'}, 行数={len(result)}")

        if uiThaiXieBoDianLiu.radioButton_S2_WT1806E.isChecked():
            print("[DEBUG-SAVE] 调用 Save_File_ThaiWT1806E_Config (page index=2)")
            page = uiThaiXieBoDianLiu._wtStacked.widget(2)
            finder = _PageWidgetFinder(page)
            try:
                test_combo = finder.comboBox_SigmA1
                print(f"[DEBUG-SAVE] finder.comboBox_SigmA1 找到: {test_combo}, currentIndex={test_combo.currentIndex()}, items={test_combo.count()}")
            except Exception as e:
                print(f"[DEBUG-SAVE] finder.comboBox_SigmA1 找不到: {e}")
            result = Save_File_ThaiWT1806E_Config(finder)
            print(f"[DEBUG-SAVE] WT1806E 保存结果: {'有数据' if len(result) > 0 else '空'}, 行数={len(result)}")

        if uiThaiXieBoDianLiu.radioButton_S2_WT5000.isChecked():
            print("[DEBUG-SAVE] 调用 Save_File_ThaiWT5000_Config (page index=3)")
            page = uiThaiXieBoDianLiu._wtStacked.widget(3)
            finder = _PageWidgetFinder(page)
            try:
                test_combo = finder.comboBox_SigmA1
                print(f"[DEBUG-SAVE] finder.comboBox_SigmA1 找到: {test_combo}, currentIndex={test_combo.currentIndex()}, items={test_combo.count()}")
            except Exception as e:
                print(f"[DEBUG-SAVE] finder.comboBox_SigmA1 找不到: {e}")
            result = Save_File_ThaiWT5000_Config(finder)
            print(f"[DEBUG-SAVE] WT5000 保存结果: {'有数据' if len(result) > 0 else '空'}, 行数={len(result)}")

        print(f"[DEBUG-SAVE] --- 写入 CSV 文件 ---")
        print(f"[DEBUG-SAVE] arrayRow1 列数: {len(arrayRow1)}")
        print(f"[DEBUG-SAVE] arrayRow2 列数: {len(arrayRow2)}")
        if len(result) > 0:
            print(f"[DEBUG-SAVE] result[0] (WT header) 列数: {len(result[0])}")
            print(f"[DEBUG-SAVE] result[1] (WT data) 列数: {len(result[1])}")
            print(f"[DEBUG-SAVE] result[1] 前10项: {result[1][:10]}")
        else:
            print("[DEBUG-SAVE] result 为空，不写入 WT 配置行")

        out = open(directory1[0], 'w+', newline='', encoding='utf-8-sig')
        csv_write = csv.writer(out, dialect="excel")
        csv_write.writerow(arrayRow1)
        csv_write.writerow(arrayRow2)
        if len(result) > 0:
            csv_write.writerow(result[0])
            csv_write.writerow(result[1])
        out.close()
        print(f"[DEBUG-SAVE] 文件写入完成: {directory1[0]}")
        print("=" * 80)
        out.close()
        QMessageBox.information(None, "实验设定提示信息", "谐波电流文件保存完成", QMessageBox.Ok, QMessageBox.Ok)

#谐波电流读取设定
def Open_File_ThaiXieBoDianLiu(kwargs):
    print("=" * 80)
    print("[DEBUG-LOAD] ==================== 开始加载谐波电流配置 ====================")
    print(f"[DEBUG-LOAD] kwargs keys: {kwargs.keys()}")
    dialog_windowxiebodianliu = kwargs['dialog_windowxiebodianliu']
    uiThaiXieBoDianLiu = kwargs['uiThaiXieBoDianLiu']
    uiThiaWT3000E = kwargs['uiThiaWT3000E']
    uiThiaWT1800 = kwargs['uiThiaWT1800']
    uiThiaWT1806E = kwargs['uiThiaWT1806E']
    uiThiaWT5000 = kwargs['uiThiaWT5000']
    print(f"[DEBUG-LOAD] dialog_windowxiebodianliu type: {type(dialog_windowxiebodianliu)}")
    print(f"[DEBUG-LOAD] uiThaiXieBoDianLiu type: {type(uiThaiXieBoDianLiu)}")
    print(f"[DEBUG-LOAD] uiThaiXieBoDianLiu has _wtStacked: {hasattr(uiThaiXieBoDianLiu, '_wtStacked')}")
    if hasattr(uiThaiXieBoDianLiu, '_wtStacked'):
        print(f"[DEBUG-LOAD] _wtStacked count: {uiThaiXieBoDianLiu._wtStacked.count()}")
        print(f"[DEBUG-LOAD] _wtStacked current index: {uiThaiXieBoDianLiu._wtStacked.currentIndex()}")
        print(f"[DEBUG-LOAD] _wtStacked current widget: {uiThaiXieBoDianLiu._wtStacked.currentWidget()}")
    print(f"[DEBUG-LOAD] uiThiaWT3000E type: {type(uiThiaWT3000E)}")
    print(f"[DEBUG-LOAD] uiThiaWT1800 type: {type(uiThiaWT1800)}")
    print(f"[DEBUG-LOAD] uiThiaWT1806E type: {type(uiThiaWT1806E)}")
    print(f"[DEBUG-LOAD] uiThiaWT5000 type: {type(uiThiaWT5000)}")
    strFlag  = "0"
    result_list = []
    config_dict = {}
    wt_config_dict = {}
    print("[DEBUG-LOAD] 打开文件选择对话框...")
    directory1 = QFileDialog.getOpenFileName(None, "单个文件选择", "./", "Text Files(*.csv)")
    print(f"[DEBUG-LOAD] 选择的文件: {directory1[0]}")
    if directory1[0] == '':
        print("[DEBUG-LOAD] 用户取消了文件选择")
        return
    else:
        print(f"[DEBUG-LOAD] 读取文件: {directory1[0]}")
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

        print(f"[DEBUG-LOAD] CSV 总行数: {len(result_list)}")
        if len(result_list) > 0:
            print(f"[DEBUG-LOAD] 第1行（header1）列数: {len(result_list[0])}")
        if len(result_list) > 1:
            print(f"[DEBUG-LOAD] 第2行（data1）列数: {len(result_list[1])}")
        if len(result_list) > 2:
            print(f"[DEBUG-LOAD] 第3行（header2）列数: {len(result_list[2])}")
        if len(result_list) > 3:
            print(f"[DEBUG-LOAD] 第4行（data2）列数: {len(result_list[3])}")

        if len(result_list) == 2:
            print("[DEBUG-LOAD] 检测到 2 行格式（仅 step1）")
            delta_len = int(len(result_list[0]) - len(result_list[1]))
            if delta_len > 0:
                print(f"[DEBUG-LOAD] 补齐 data1 缺失的 {delta_len} 列")
                extend_list = ['' for k in range(delta_len)]
                result_list[1].extend(extend_list)
            config_dict = dict(zip(result_list[0],result_list[1]))
            print(f"[DEBUG-LOAD] config_dict 列数: {len(config_dict)}")
        if len(result_list) == 4:
            print("[DEBUG-LOAD] 检测到 4 行格式（step1 + WT config）")
            delta_len1 = int(len(result_list[0]) - len(result_list[1]))
            if delta_len1 > 0:
                print(f"[DEBUG-LOAD] 补齐 data1 缺失的 {delta_len1} 列")
                extend_list1 = ['' for k in range(delta_len1)]
                result_list[1].extend(extend_list1)
            delta_len2 = int(len(result_list[2]) - len(result_list[3]))
            if delta_len2 > 0:
                print(f"[DEBUG-LOAD] 补齐 data2 缺失的 {delta_len2} 列")
                extend_list2 = ['' for k in range(delta_len2)]
                result_list[3].extend(extend_list2)
            config_dict = dict(zip(result_list[0],result_list[1]))
            wt_config_dict = dict(zip(result_list[2],result_list[3]))
            print(f"[DEBUG-LOAD] config_dict 列数: {len(config_dict)}")
            print(f"[DEBUG-LOAD] wt_config_dict 列数: {len(wt_config_dict)}")
            print(f"[DEBUG-LOAD] wt_config_dict Style: {wt_config_dict.get('Style', 'N/A')}")
            print(f"[DEBUG-LOAD] config_dict Style: {config_dict.get('Style', 'N/A')}")

        if config_dict != {}:
            if arrayRow1[0] in config_dict:
                if config_dict[arrayRow1[0]] == "ThaiXieBoDianLiu":
                    print("[DEBUG-LOAD] Style 匹配: ThaiXieBoDianLiu，开始加载 step1...")
                    # step1
                    if strFlag == "0":
                        if arrayRow1[1] in config_dict:
                            checkBox_S1 = config_dict[arrayRow1[1]]
                            print(f"[DEBUG-LOAD] checkBox_S1: 从 {uiThaiXieBoDianLiu.checkBox_S1.isChecked()} 改为 {checkBox_S1}")
                            if checkBox_S1 == '1':
                                uiThaiXieBoDianLiu.checkBox_S1.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1.setChecked(False)
                            print(f"[DEBUG-LOAD] checkBox_S1 设置后: {uiThaiXieBoDianLiu.checkBox_S1.isChecked()}")
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[2] in config_dict:
                            comboBox_S1_AC = config_dict[arrayRow1[2]]
                            print(f"[DEBUG-LOAD] comboBox_S1_AC: 从 {uiThaiXieBoDianLiu.comboBox_S1_AC.currentIndex()} 改为 {comboBox_S1_AC}")
                            uiThaiXieBoDianLiu.comboBox_S1_AC.setCurrentIndex(int(comboBox_S1_AC))
                            print(f"[DEBUG-LOAD] comboBox_S1_AC 设置后: {uiThaiXieBoDianLiu.comboBox_S1_AC.currentIndex()}")
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[3] in config_dict:
                            textEdit_S1_AC_VOLT = config_dict[arrayRow1[3]]
                            print(f"[DEBUG-LOAD] textEdit_S1_AC_VOLT: 设置为 {textEdit_S1_AC_VOLT}")
                            uiThaiXieBoDianLiu.textEdit_S1_AC_VOLT.setText(textEdit_S1_AC_VOLT)
                            print(f"[DEBUG-LOAD] textEdit_S1_AC_VOLT 设置后: {uiThaiXieBoDianLiu.textEdit_S1_AC_VOLT.toPlainText()}")
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[4] in config_dict:
                            textEdit_S1_AC_VOLT_2 = config_dict[arrayRow1[4]]
                            print(f"[DEBUG-LOAD] textEdit_S1_AC_VOLT_2: 设置为 {textEdit_S1_AC_VOLT_2}")
                            uiThaiXieBoDianLiu.textEdit_S1_AC_VOLT_2.setText(textEdit_S1_AC_VOLT_2)
                            print(f"[DEBUG-LOAD] textEdit_S1_AC_VOLT_2 设置后: {uiThaiXieBoDianLiu.textEdit_S1_AC_VOLT_2.toPlainText()}")
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[5] in config_dict:
                            textEdit_S1_AC_VOLT_3 = config_dict[arrayRow1[5]]
                            print(f"[DEBUG-LOAD] textEdit_S1_AC_VOLT_3: 设置为 {textEdit_S1_AC_VOLT_3}")
                            uiThaiXieBoDianLiu.textEdit_S1_AC_VOLT_3.setText(textEdit_S1_AC_VOLT_3)
                            print(f"[DEBUG-LOAD] textEdit_S1_AC_VOLT_3 设置后: {uiThaiXieBoDianLiu.textEdit_S1_AC_VOLT_3.toPlainText()}")
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
                                uiThaiXieBoDianLiu.radioButton_S2_WT3000.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.radioButton_S2_WT3000.setChecked(False)
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[42] in config_dict:
                            checkBox_S2_WT1800 = config_dict[arrayRow1[42]]
                            if checkBox_S2_WT1800 == '1':
                                uiThaiXieBoDianLiu.radioButton_S2_WT1800.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.radioButton_S2_WT1800.setChecked(False)
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
                            print(f"[DEBUG-LOAD] checkBox_S2_WT1806E: 从 {uiThaiXieBoDianLiu.radioButton_S2_WT1806E.isChecked()} 改为 {checkBox_S2_WT1806E}")
                            if checkBox_S2_WT1806E == '1':
                                uiThaiXieBoDianLiu.radioButton_S2_WT1806E.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.radioButton_S2_WT1806E.setChecked(False)
                            print(f"[DEBUG-LOAD] checkBox_S2_WT1806E 设置后: {uiThaiXieBoDianLiu.radioButton_S2_WT1806E.isChecked()}")
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[124] in config_dict:
                            checkBox_S1_Integral = config_dict[arrayRow1[124]]
                            print(f"[DEBUG-LOAD] checkBox_S1_Integral: 从 {uiThaiXieBoDianLiu.checkBox_S1_Integral.isChecked()} 改为 {checkBox_S1_Integral}")
                            if checkBox_S1_Integral == '1':
                                uiThaiXieBoDianLiu.checkBox_S1_Integral.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.checkBox_S1_Integral.setChecked(False)
                            print(f"[DEBUG-LOAD] checkBox_S1_Integral 设置后: {uiThaiXieBoDianLiu.checkBox_S1_Integral.isChecked()}")
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[125] in config_dict:
                            comboBox_S1_Integral = config_dict[arrayRow1[125]]
                            print(f"[DEBUG-LOAD] comboBox_S1_Integral: 从 {uiThaiXieBoDianLiu.comboBox_S1_Integral.currentIndex()} 改为 {comboBox_S1_Integral}")
                            uiThaiXieBoDianLiu.comboBox_S1_Integral.setCurrentIndex(int(comboBox_S1_Integral))
                            print(f"[DEBUG-LOAD] comboBox_S1_Integral 设置后: {uiThaiXieBoDianLiu.comboBox_S1_Integral.currentIndex()}")
                        else:
                            strFlag = 1

                    if strFlag == "0":
                        if arrayRow1[126] in config_dict:
                            checkBox_S2_WT5000 = config_dict[arrayRow1[126]]
                            print(f"[DEBUG-LOAD] checkBox_S2_WT5000: 从 {uiThaiXieBoDianLiu.radioButton_S2_WT5000.isChecked()} 改为 {checkBox_S2_WT5000}")
                            if checkBox_S2_WT5000 == '1':
                                uiThaiXieBoDianLiu.radioButton_S2_WT5000.setChecked(True)
                            else:
                                uiThaiXieBoDianLiu.radioButton_S2_WT5000.setChecked(False)
                            print(f"[DEBUG-LOAD] checkBox_S2_WT5000 设置后: {uiThaiXieBoDianLiu.radioButton_S2_WT5000.isChecked()}")
                        else:
                            strFlag = 1

                    print(f"[DEBUG-LOAD] ==================== 开始加载 step2 WT 配置 ====================")
                    print(f"[DEBUG-LOAD] config_dict keys count: {len(config_dict)}")
                    print(f"[DEBUG-LOAD] wt_config_dict keys count: {len(wt_config_dict)}")
                    print(f"[DEBUG-LOAD] arrayRow1[41]={arrayRow1[41]}, in config_dict: {arrayRow1[41] in config_dict}")
                    print(f"[DEBUG-LOAD] arrayRow1[42]={arrayRow1[42]}, in config_dict: {arrayRow1[42] in config_dict}")
                    print(f"[DEBUG-LOAD] has _wtStacked: {hasattr(uiThaiXieBoDianLiu, '_wtStacked')}")
                    if arrayRow1[41] in config_dict:
                        checkBox_S2_WT3000 = config_dict[arrayRow1[41]]
                        print(f"[DEBUG] checkBox_S2_WT3000={checkBox_S2_WT3000}")
                        if checkBox_S2_WT3000 == '1':
                            print(f"[DEBUG] WT3000: 设置前 radio checked={uiThaiXieBoDianLiu.radioButton_S2_WT3000.isChecked()}")
                            uiThaiXieBoDianLiu.radioButton_S2_WT3000.setChecked(True)
                            print(f"[DEBUG] WT3000: 设置后 radio checked={uiThaiXieBoDianLiu.radioButton_S2_WT3000.isChecked()}")
                            print(f"[DEBUG] WT3000: 设置前 stacked index={uiThaiXieBoDianLiu._wtStacked.currentIndex()}")
                            uiThaiXieBoDianLiu._wtStacked.setCurrentIndex(0)
                            print(f"[DEBUG] WT3000: 设置后 stacked index={uiThaiXieBoDianLiu._wtStacked.currentIndex()}")
                            page0 = uiThaiXieBoDianLiu._wtStacked.widget(0)
                            print(f"[DEBUG] WT3000: page0 visible={page0.isVisible()}, geometry={page0.geometry()}")
                            uiThaiXieBoDianLiu._wtStacked.repaint()
                            QApplication.processEvents()
                            Open_File_ThaiWT3000_Config(_PageWidgetFinder(page0), wt_config_dict)

                    else:
                        strFlag = 1

                    if arrayRow1[42] in config_dict:
                        checkBox_S2_WT1800 = config_dict[arrayRow1[42]]
                        print(f"[DEBUG] checkBox_S2_WT1800={checkBox_S2_WT1800}")
                        if checkBox_S2_WT1800 == '1':
                            print(f"[DEBUG] WT1800: 设置前 radio checked={uiThaiXieBoDianLiu.radioButton_S2_WT1800.isChecked()}")
                            uiThaiXieBoDianLiu.radioButton_S2_WT1800.setChecked(True)
                            print(f"[DEBUG] WT1800: 设置后 radio checked={uiThaiXieBoDianLiu.radioButton_S2_WT1800.isChecked()}")
                            print(f"[DEBUG] WT1800: 设置前 stacked index={uiThaiXieBoDianLiu._wtStacked.currentIndex()}")
                            uiThaiXieBoDianLiu._wtStacked.setCurrentIndex(1)
                            print(f"[DEBUG] WT1800: 设置后 stacked index={uiThaiXieBoDianLiu._wtStacked.currentIndex()}")
                            page1 = uiThaiXieBoDianLiu._wtStacked.widget(1)
                            print(f"[DEBUG] WT1800: page1 visible={page1.isVisible()}, geometry={page1.geometry()}")
                            print(f"[DEBUG] WT1800: page1 size={page1.size()}, minimumSize={page1.minimumSize()}")
                            uiThaiXieBoDianLiu._wtStacked.repaint()
                            QApplication.processEvents()
                            Open_File_ThaiWT1800_Config(_PageWidgetFinder(page1), wt_config_dict)
                    else:
                        strFlag = 1

                    if arrayRow1[123] in config_dict:
                        checkBox_S2_WT1806E = config_dict[arrayRow1[123]]
                        if checkBox_S2_WT1806E == '1':
                            print(f"[DEBUG] WT1806E: 设置前 radio checked={uiThaiXieBoDianLiu.radioButton_S2_WT1806E.isChecked()}")
                            uiThaiXieBoDianLiu.radioButton_S2_WT1806E.setChecked(True)
                            print(f"[DEBUG] WT1806E: 设置后 radio checked={uiThaiXieBoDianLiu.radioButton_S2_WT1806E.isChecked()}")
                            uiThaiXieBoDianLiu._wtStacked.setCurrentIndex(2)
                            print(f"[DEBUG] WT1806E: stacked index={uiThaiXieBoDianLiu._wtStacked.currentIndex()}")
                            page2 = uiThaiXieBoDianLiu._wtStacked.widget(2)
                            print(f"[DEBUG] WT1806E: page2 visible={page2.isVisible()}, geometry={page2.geometry()}")
                            uiThaiXieBoDianLiu._wtStacked.repaint()
                            QApplication.processEvents()
                            Open_File_ThaiWT1806E_Config(_PageWidgetFinder(page2), wt_config_dict)

                    if arrayRow1[126] in config_dict:
                        checkBox_S2_WT5000 = config_dict[arrayRow1[126]]
                        if checkBox_S2_WT5000 == '1':
                            print(f"[DEBUG] WT5000: 设置前 radio checked={uiThaiXieBoDianLiu.radioButton_S2_WT5000.isChecked()}")
                            uiThaiXieBoDianLiu.radioButton_S2_WT5000.setChecked(True)
                            print(f"[DEBUG] WT5000: 设置后 radio checked={uiThaiXieBoDianLiu.radioButton_S2_WT5000.isChecked()}")
                            uiThaiXieBoDianLiu._wtStacked.setCurrentIndex(3)
                            print(f"[DEBUG] WT5000: stacked index={uiThaiXieBoDianLiu._wtStacked.currentIndex()}")
                            page3 = uiThaiXieBoDianLiu._wtStacked.widget(3)
                            print(f"[DEBUG] WT5000: page3 visible={page3.isVisible()}, geometry={page3.geometry()}")
                            uiThaiXieBoDianLiu._wtStacked.repaint()
                            QApplication.processEvents()
                            Open_File_ThaiWT5000_Config(_PageWidgetFinder(page3), wt_config_dict)
                    else:
                        strFlag = 1

        # 加载完成后的最终状态检查
        print("=" * 80)
        print("[DEBUG-FINAL] 加载完成后的最终状态检查:")
        print(f"[DEBUG-FINAL] 当前 stacked index: {uiThaiXieBoDianLiu._wtStacked.currentIndex()}")
        print(f"[DEBUG-FINAL] stacked 总页数: {uiThaiXieBoDianLiu._wtStacked.count()}")
        print(f"[DEBUG-FINAL] 当前显示的 widget: {uiThaiXieBoDianLiu._wtStacked.currentWidget()}")
        print(f"[DEBUG-FINAL] 当前 widget 类型: {type(uiThaiXieBoDianLiu._wtStacked.currentWidget())}")
        if uiThaiXieBoDianLiu._wtStacked.currentWidget():
            print(f"[DEBUG-FINAL] 当前 widget visible: {uiThaiXieBoDianLiu._wtStacked.currentWidget().isVisible()}")
            print(f"[DEBUG-FINAL] 当前 widget geometry: {uiThaiXieBoDianLiu._wtStacked.currentWidget().geometry()}")
            print(f"[DEBUG-FINAL] 当前 widget size: {uiThaiXieBoDianLiu._wtStacked.currentWidget().size()}")
            if hasattr(uiThaiXieBoDianLiu._wtStacked.currentWidget(), 'widget'):
                scroll_area = uiThaiXieBoDianLiu._wtStacked.currentWidget()
                print(f"[DEBUG-FINAL] ScrollArea widget: {scroll_area.widget()}")
                print(f"[DEBUG-FINAL] ScrollArea widget visible: {scroll_area.widget().isVisible()}")
                print(f"[DEBUG-FINAL] ScrollArea widget size: {scroll_area.widget().size()}")
        print(f"[DEBUG-FINAL] radioButton_S2_WT3000 checked: {uiThaiXieBoDianLiu.radioButton_S2_WT3000.isChecked()}")
        print(f"[DEBUG-FINAL] radioButton_S2_WT1800 checked: {uiThaiXieBoDianLiu.radioButton_S2_WT1800.isChecked()}")
        print(f"[DEBUG-FINAL] radioButton_S2_WT1806E checked: {uiThaiXieBoDianLiu.radioButton_S2_WT1806E.isChecked()}")
        print(f"[DEBUG-FINAL] radioButton_S2_WT5000 checked: {uiThaiXieBoDianLiu.radioButton_S2_WT5000.isChecked()}")
        print("=" * 80)

        # 加载完成后切换到 step2 让用户看到 WT 配置回显
        if hasattr(uiThaiXieBoDianLiu, '_switch_step'):
            print("[DEBUG-FINAL] 自动切换到 step2...")
            uiThaiXieBoDianLiu._switch_step(1)
            QApplication.processEvents()

        # 强制更新 UI 后再显示提示
        QApplication.processEvents()
        QMessageBox.information(None, "实验设定提示信息", "谐波电流文件读取完成", QMessageBox.Ok, QMessageBox.Ok)

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