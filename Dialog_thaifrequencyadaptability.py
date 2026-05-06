# -*- coding: utf-8 -*-

# 频率适应性项目配置界面：step1 与 Dialog_thaiguoqianpin_immun 同源；step2 为 WT；
# 过频 step3～step11、欠频 step12～step20：同一行左右两栏，各自独立勾选框与参数区。
# step_last：交流电源 + 四路直流电源 开启/关闭，与 Dialog_thaiguoqianpin_immun.groupBox_11 对齐。

from PyQt5 import QtCore, QtGui, QtWidgets

_FREQ_ADAPT_HTML_TPL = (
    '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
    '"http://www.w3.org/TR/REC-html40/strict.dtd">\n'
    '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
    "p, li { white-space: pre-wrap; }\n"
    "</style></head><body style=\" font-family:'宋体'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
    '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
    '-qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'SimSun\'; '
    'font-size:9pt;">%s</span></p></body></html>'
)


class Ui_Dialog_thaifrequencyadaptability(object):
    def setupUi(self, Dialog_thaifrequencyadaptability):
        Dialog_thaifrequencyadaptability.setObjectName("Dialog_thaifrequencyadaptability")
        Dialog_thaifrequencyadaptability.resize(1410, 1140)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaifrequencyadaptability.setWindowIcon(icon)
        self.groupBox = QtWidgets.QGroupBox(Dialog_thaifrequencyadaptability)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 911, 91))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.label_18 = QtWidgets.QLabel(self.groupBox)
        self.label_18.setGeometry(QtCore.QRect(880, 30, 20, 16))
        self.label_18.setObjectName("label_18")
        self.label_19 = QtWidgets.QLabel(self.groupBox)
        self.label_19.setGeometry(QtCore.QRect(780, 20, 41, 31))
        self.label_19.setObjectName("label_19")
        self.textEdit_S1_AC_FR = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit_S1_AC_FR.setGeometry(QtCore.QRect(830, 20, 41, 31))
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        self.comboBox_S1_AC_2 = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_S1_AC_2.setGeometry(QtCore.QRect(180, 60, 60, 21))
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItem("")
        self.comboBox_S1_AC_2.addItem("")
        self.label_107 = QtWidgets.QLabel(self.groupBox)
        self.label_107.setGeometry(QtCore.QRect(588, 28, 16, 16))
        self.label_107.setObjectName("label_107")
        self.label_113 = QtWidgets.QLabel(self.groupBox)
        self.label_113.setGeometry(QtCore.QRect(450, 19, 71, 31))
        self.label_113.setObjectName("label_113")
        self.comboBox_S1_AC = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_S1_AC.setGeometry(QtCore.QRect(180, 20, 60, 31))
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItem("")
        self.comboBox_S1_AC.addItem("")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(270, 19, 71, 31))
        self.label_4.setObjectName("label_4")
        self.label_123 = QtWidgets.QLabel(self.groupBox)
        self.label_123.setGeometry(QtCore.QRect(606, 25, 71, 21))
        self.label_123.setObjectName("label_123")
        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit_S1_AC_VOLT_2.setGeometry(QtCore.QRect(529, 19, 51, 31))
        self.textEdit_S1_AC_VOLT_2.setAcceptDrops(True)
        self.textEdit_S1_AC_VOLT_2.setUndoRedoEnabled(True)
        self.textEdit_S1_AC_VOLT_2.setReadOnly(False)
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit_S1_AC_VOLT.setGeometry(QtCore.QRect(350, 20, 51, 31))
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(410, 30, 16, 16))
        self.label_5.setObjectName("label_5")
        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit_S1_AC_VOLT_3.setGeometry(QtCore.QRect(690, 20, 51, 31))
        self.textEdit_S1_AC_VOLT_3.setReadOnly(False)
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(104, 25, 71, 20))
        self.label_3.setObjectName("label_3")
        self.checkBox_S1 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_S1.setGeometry(QtCore.QRect(20, 20, 81, 21))
        self.checkBox_S1.setChecked(True)
        self.checkBox_S1.setObjectName("checkBox_S1")
        self.label_102 = QtWidgets.QLabel(self.groupBox)
        self.label_102.setGeometry(QtCore.QRect(750, 30, 16, 16))
        self.label_102.setObjectName("label_102")
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog_thaifrequencyadaptability)
        self.groupBox_2.setGeometry(QtCore.QRect(0, 90, 961, 161))
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.label_17 = QtWidgets.QLabel(self.groupBox_2)
        self.label_17.setGeometry(QtCore.QRect(280, 90, 31, 20))
        self.label_17.setObjectName("label_17")
        self.textEdit_S1_DC2_Isc = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC2_Isc.setGeometry(QtCore.QRect(730, 43, 71, 31))
        self.textEdit_S1_DC2_Isc.setObjectName("textEdit_S1_DC2_Isc")
        self.textEdit_S1_DC2_PF = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC2_PF.setGeometry(QtCore.QRect(890, 44, 41, 31))
        self.textEdit_S1_DC2_PF.setObjectName("textEdit_S1_DC2_PF")
        self.textEdit_S1_DC3_Voc = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC3_Voc.setGeometry(QtCore.QRect(600, 84, 61, 31))
        self.textEdit_S1_DC3_Voc.setObjectName("textEdit_S1_DC3_Voc")
        self.textEdit_S1_DC3_Isc = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC3_Isc.setGeometry(QtCore.QRect(730, 83, 71, 31))
        self.textEdit_S1_DC3_Isc.setObjectName("textEdit_S1_DC3_Isc")
        self.label_110 = QtWidgets.QLabel(self.groupBox_2)
        self.label_110.setGeometry(QtCore.QRect(400, 13, 16, 20))
        self.label_110.setObjectName("label_110")
        self.textEdit_S1_DC1_Isc = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC1_Isc.setGeometry(QtCore.QRect(730, 3, 71, 31))
        self.textEdit_S1_DC1_Isc.setObjectName("textEdit_S1_DC1_Isc")
        self.label_125 = QtWidgets.QLabel(self.groupBox_2)
        self.label_125.setGeometry(QtCore.QRect(440, 133, 31, 16))
        self.label_125.setObjectName("label_125")
        self.label_128 = QtWidgets.QLabel(self.groupBox_2)
        self.label_128.setGeometry(QtCore.QRect(800, 53, 16, 16))
        self.label_128.setObjectName("label_128")
        self.label_112 = QtWidgets.QLabel(self.groupBox_2)
        self.label_112.setGeometry(QtCore.QRect(941, 55, 16, 16))
        self.label_112.setObjectName("label_112")
        self.textEdit_S1_DC1_VOLT = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC1_VOLT.setGeometry(QtCore.QRect(326, 7, 71, 31))
        self.textEdit_S1_DC1_VOLT.setObjectName("textEdit_S1_DC1_VOLT")
        self.label_55 = QtWidgets.QLabel(self.groupBox_2)
        self.label_55.setGeometry(QtCore.QRect(940, 13, 16, 16))
        self.label_55.setObjectName("label_55")
        self.label_116 = QtWidgets.QLabel(self.groupBox_2)
        self.label_116.setGeometry(QtCore.QRect(840, 94, 41, 16))
        self.label_116.setObjectName("label_116")
        self.comboBox_S1_DC4 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_S1_DC4.setGeometry(QtCore.QRect(196, 134, 60, 21))
        self.comboBox_S1_DC4.setObjectName("comboBox_S1_DC4")
        self.comboBox_S1_DC4.addItem("")
        self.comboBox_S1_DC4.addItem("")
        self.checkBox_S1_DC4 = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_S1_DC4.setGeometry(QtCore.QRect(76, 126, 111, 41))
        self.checkBox_S1_DC4.setChecked(True)
        self.checkBox_S1_DC4.setObjectName("checkBox_S1_DC4")
        self.label_109 = QtWidgets.QLabel(self.groupBox_2)
        self.label_109.setGeometry(QtCore.QRect(670, 13, 16, 16))
        self.label_109.setObjectName("label_109")
        self.label_57 = QtWidgets.QLabel(self.groupBox_2)
        self.label_57.setGeometry(QtCore.QRect(540, 94, 16, 16))
        self.label_57.setObjectName("label_57")
        self.label_105 = QtWidgets.QLabel(self.groupBox_2)
        self.label_105.setGeometry(QtCore.QRect(693, 132, 31, 16))
        self.label_105.setObjectName("label_105")
        self.textEdit_S1_DC3_VOLT = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC3_VOLT.setGeometry(QtCore.QRect(326, 86, 71, 31))
        self.textEdit_S1_DC3_VOLT.setObjectName("textEdit_S1_DC3_VOLT")
        self.label_120 = QtWidgets.QLabel(self.groupBox_2)
        self.label_120.setGeometry(QtCore.QRect(436, 14, 31, 21))
        self.label_120.setObjectName("label_120")
        self.label_14 = QtWidgets.QLabel(self.groupBox_2)
        self.label_14.setGeometry(QtCore.QRect(280, 49, 31, 20))
        self.label_14.setObjectName("label_14")
        self.label_59 = QtWidgets.QLabel(self.groupBox_2)
        self.label_59.setGeometry(QtCore.QRect(691, 52, 31, 16))
        self.label_59.setObjectName("label_59")
        self.label_13 = QtWidgets.QLabel(self.groupBox_2)
        self.label_13.setGeometry(QtCore.QRect(279, 13, 41, 21))
        self.label_13.setObjectName("label_13")
        self.label_53 = QtWidgets.QLabel(self.groupBox_2)
        self.label_53.setGeometry(QtCore.QRect(540, 54, 16, 16))
        self.label_53.setObjectName("label_53")
        self.comboBox_S1_DC1 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_S1_DC1.setGeometry(QtCore.QRect(196, 16, 60, 21))
        self.comboBox_S1_DC1.setObjectName("comboBox_S1_DC1")
        self.comboBox_S1_DC1.addItem("")
        self.comboBox_S1_DC1.addItem("")
        self.checkBox_S1_DC3 = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_S1_DC3.setGeometry(QtCore.QRect(76, 87, 111, 41))
        self.checkBox_S1_DC3.setChecked(True)
        self.checkBox_S1_DC3.setObjectName("checkBox_S1_DC3")
        self.textEdit_S1_DC4_VOLT = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC4_VOLT.setGeometry(QtCore.QRect(326, 125, 71, 31))
        self.textEdit_S1_DC4_VOLT.setObjectName("textEdit_S1_DC4_VOLT")
        self.label_58 = QtWidgets.QLabel(self.groupBox_2)
        self.label_58.setGeometry(QtCore.QRect(440, 94, 31, 16))
        self.label_58.setObjectName("label_58")
        self.label_129 = QtWidgets.QLabel(self.groupBox_2)
        self.label_129.setGeometry(QtCore.QRect(840, 53, 41, 16))
        self.label_129.setObjectName("label_129")
        self.comboBox_S1_DC2 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_S1_DC2.setGeometry(QtCore.QRect(196, 57, 60, 21))
        self.comboBox_S1_DC2.setObjectName("comboBox_S1_DC2")
        self.comboBox_S1_DC2.addItem("")
        self.comboBox_S1_DC2.addItem("")
        self.textEdit_S1_DC2_VOLT = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC2_VOLT.setGeometry(QtCore.QRect(326, 45, 71, 31))
        self.textEdit_S1_DC2_VOLT.setObjectName("textEdit_S1_DC2_VOLT")
        self.textEdit_S1_DC3_PF = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC3_PF.setGeometry(QtCore.QRect(890, 84, 41, 31))
        self.textEdit_S1_DC3_PF.setObjectName("textEdit_S1_DC3_PF")
        self.label_117 = QtWidgets.QLabel(self.groupBox_2)
        self.label_117.setGeometry(QtCore.QRect(940, 133, 16, 16))
        self.label_117.setObjectName("label_117")
        self.label_51 = QtWidgets.QLabel(self.groupBox_2)
        self.label_51.setGeometry(QtCore.QRect(670, 53, 16, 16))
        self.label_51.setObjectName("label_51")
        self.textEdit_S1_DC4_CURR = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC4_CURR.setGeometry(QtCore.QRect(470, 126, 71, 31))
        self.textEdit_S1_DC4_CURR.setObjectName("textEdit_S1_DC4_CURR")
        self.label_101 = QtWidgets.QLabel(self.groupBox_2)
        self.label_101.setGeometry(QtCore.QRect(693, 93, 31, 16))
        self.label_101.setObjectName("label_101")
        self.label_127 = QtWidgets.QLabel(self.groupBox_2)
        self.label_127.setGeometry(QtCore.QRect(400, 93, 16, 16))
        self.label_127.setObjectName("label_127")
        self.label_100 = QtWidgets.QLabel(self.groupBox_2)
        self.label_100.setGeometry(QtCore.QRect(840, 133, 41, 16))
        self.label_100.setObjectName("label_100")
        self.label_106 = QtWidgets.QLabel(self.groupBox_2)
        self.label_106.setGeometry(QtCore.QRect(689, 13, 31, 16))
        self.label_106.setObjectName("label_106")
        self.label_118 = QtWidgets.QLabel(self.groupBox_2)
        self.label_118.setGeometry(QtCore.QRect(540, 14, 16, 16))
        self.label_118.setObjectName("label_118")
        self.label_119 = QtWidgets.QLabel(self.groupBox_2)
        self.label_119.setGeometry(QtCore.QRect(670, 93, 16, 16))
        self.label_119.setObjectName("label_119")
        self.checkBox_S1_DC1 = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_S1_DC1.setGeometry(QtCore.QRect(80, 10, 111, 31))
        self.checkBox_S1_DC1.setChecked(True)
        self.checkBox_S1_DC1.setObjectName("checkBox_S1_DC1")
        self.label_54 = QtWidgets.QLabel(self.groupBox_2)
        self.label_54.setGeometry(QtCore.QRect(280, 129, 31, 20))
        self.label_54.setObjectName("label_54")
        self.comboBox_S1_DC3 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_S1_DC3.setGeometry(QtCore.QRect(196, 95, 60, 21))
        self.comboBox_S1_DC3.setObjectName("comboBox_S1_DC3")
        self.comboBox_S1_DC3.addItem("")
        self.comboBox_S1_DC3.addItem("")
        self.textEdit_S1_DC1_Voc = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC1_Voc.setGeometry(QtCore.QRect(600, 5, 61, 31))
        self.textEdit_S1_DC1_Voc.setObjectName("textEdit_S1_DC1_Voc")
        self.label_103 = QtWidgets.QLabel(self.groupBox_2)
        self.label_103.setGeometry(QtCore.QRect(540, 133, 16, 16))
        self.label_103.setObjectName("label_103")
        self.label_52 = QtWidgets.QLabel(self.groupBox_2)
        self.label_52.setGeometry(QtCore.QRect(438, 53, 31, 16))
        self.label_52.setObjectName("label_52")
        self.textEdit_S1_DC4_Isc = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC4_Isc.setGeometry(QtCore.QRect(730, 123, 71, 31))
        self.textEdit_S1_DC4_Isc.setObjectName("textEdit_S1_DC4_Isc")
        self.label_104 = QtWidgets.QLabel(self.groupBox_2)
        self.label_104.setGeometry(QtCore.QRect(840, 13, 41, 16))
        self.label_104.setObjectName("label_104")
        self.textEdit_S1_DC3_CURR = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC3_CURR.setGeometry(QtCore.QRect(470, 87, 71, 31))
        self.textEdit_S1_DC3_CURR.setObjectName("textEdit_S1_DC3_CURR")
        self.label_114 = QtWidgets.QLabel(self.groupBox_2)
        self.label_114.setGeometry(QtCore.QRect(800, 133, 16, 16))
        self.label_114.setObjectName("label_114")
        self.label_126 = QtWidgets.QLabel(self.groupBox_2)
        self.label_126.setGeometry(QtCore.QRect(400, 132, 16, 16))
        self.label_126.setObjectName("label_126")
        self.label_111 = QtWidgets.QLabel(self.groupBox_2)
        self.label_111.setGeometry(QtCore.QRect(670, 132, 16, 16))
        self.label_111.setObjectName("label_111")
        self.label_108 = QtWidgets.QLabel(self.groupBox_2)
        self.label_108.setGeometry(QtCore.QRect(569, 12, 31, 20))
        self.label_108.setObjectName("label_108")
        self.label_122 = QtWidgets.QLabel(self.groupBox_2)
        self.label_122.setGeometry(QtCore.QRect(570, 47, 31, 20))
        self.label_122.setObjectName("label_122")
        self.label_56 = QtWidgets.QLabel(self.groupBox_2)
        self.label_56.setGeometry(QtCore.QRect(800, 13, 16, 16))
        self.label_56.setObjectName("label_56")
        self.textEdit_S1_DC4_PF = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC4_PF.setGeometry(QtCore.QRect(890, 123, 41, 31))
        self.textEdit_S1_DC4_PF.setObjectName("textEdit_S1_DC4_PF")
        self.textEdit_S1_DC2_Voc = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC2_Voc.setGeometry(QtCore.QRect(600, 43, 61, 31))
        self.textEdit_S1_DC2_Voc.setObjectName("textEdit_S1_DC2_Voc")
        self.textEdit_S1_DC1_PF = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC1_PF.setGeometry(QtCore.QRect(890, 3, 41, 31))
        self.textEdit_S1_DC1_PF.setObjectName("textEdit_S1_DC1_PF")
        self.label_15 = QtWidgets.QLabel(self.groupBox_2)
        self.label_15.setGeometry(QtCore.QRect(400, 53, 16, 16))
        self.label_15.setObjectName("label_15")
        self.textEdit_S1_DC1_CURR = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC1_CURR.setGeometry(QtCore.QRect(470, 8, 71, 31))
        self.textEdit_S1_DC1_CURR.setObjectName("textEdit_S1_DC1_CURR")
        self.checkBox_S1_DC2 = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_S1_DC2.setGeometry(QtCore.QRect(77, 49, 111, 41))
        self.checkBox_S1_DC2.setChecked(True)
        self.checkBox_S1_DC2.setObjectName("checkBox_S1_DC2")
        self.label_130 = QtWidgets.QLabel(self.groupBox_2)
        self.label_130.setGeometry(QtCore.QRect(570, 88, 31, 20))
        self.label_130.setObjectName("label_130")
        self.label_124 = QtWidgets.QLabel(self.groupBox_2)
        self.label_124.setGeometry(QtCore.QRect(800, 93, 16, 16))
        self.label_124.setObjectName("label_124")
        self.label_121 = QtWidgets.QLabel(self.groupBox_2)
        self.label_121.setGeometry(QtCore.QRect(570, 127, 31, 20))
        self.label_121.setObjectName("label_121")
        self.label_115 = QtWidgets.QLabel(self.groupBox_2)
        self.label_115.setGeometry(QtCore.QRect(940, 94, 16, 16))
        self.label_115.setObjectName("label_115")
        self.textEdit_S1_DC2_CURR = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC2_CURR.setGeometry(QtCore.QRect(470, 46, 71, 31))
        self.textEdit_S1_DC2_CURR.setObjectName("textEdit_S1_DC2_CURR")
        self.textEdit_S1_DC4_Voc = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_S1_DC4_Voc.setGeometry(QtCore.QRect(600, 123, 61, 31))
        self.textEdit_S1_DC4_Voc.setObjectName("textEdit_S1_DC4_Voc")
        self.groupBox_4 = QtWidgets.QGroupBox(Dialog_thaifrequencyadaptability)
        self.groupBox_4.setGeometry(QtCore.QRect(960, 20, 451, 231))
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.comboBox_S1_TIME = QtWidgets.QComboBox(self.groupBox_4)
        self.comboBox_S1_TIME.setGeometry(QtCore.QRect(170, 190, 61, 21))
        self.comboBox_S1_TIME.setObjectName("comboBox_S1_TIME")
        self.comboBox_S1_TIME.addItem("")
        self.comboBox_S1_TIME.addItem("")
        self.comboBox_S1_TIME.addItem("")
        self.textEdit_S1_TIME = QtWidgets.QTextEdit(self.groupBox_4)
        self.textEdit_S1_TIME.setGeometry(QtCore.QRect(90, 184, 71, 31))
        self.textEdit_S1_TIME.setObjectName("textEdit_S1_TIME")
        self.label_132 = QtWidgets.QLabel(self.groupBox_4)
        self.label_132.setGeometry(QtCore.QRect(0, 190, 71, 20))
        self.label_132.setObjectName("label_132")
        self.comboBox_S1_ACWaitTIME = QtWidgets.QComboBox(self.groupBox_4)
        self.comboBox_S1_ACWaitTIME.setGeometry(QtCore.QRect(170, 10, 61, 21))
        self.comboBox_S1_ACWaitTIME.setObjectName("comboBox_S1_ACWaitTIME")
        self.comboBox_S1_ACWaitTIME.addItem("")
        self.comboBox_S1_ACWaitTIME.addItem("")
        self.comboBox_S1_ACWaitTIME.addItem("")
        self.label_131 = QtWidgets.QLabel(self.groupBox_4)
        self.label_131.setGeometry(QtCore.QRect(0, 13, 71, 20))
        self.label_131.setObjectName("label_131")
        self.textEdit_S1_ACWaitTIME = QtWidgets.QTextEdit(self.groupBox_4)
        self.textEdit_S1_ACWaitTIME.setGeometry(QtCore.QRect(90, 7, 71, 31))
        self.textEdit_S1_ACWaitTIME.setObjectName("textEdit_S1_ACWaitTIME")
        self.groupBox_wt = QtWidgets.QGroupBox(Dialog_thaifrequencyadaptability)
        self.groupBox_wt.setGeometry(QtCore.QRect(0, 270, 1400, 90))
        self.groupBox_wt.setTitle("")
        self.groupBox_wt.setObjectName("groupBox_wt")

        self.checkBox_S2 = QtWidgets.QCheckBox(self.groupBox_wt)
        self.checkBox_S2.setGeometry(QtCore.QRect(20, 32, 72, 22))
        self.checkBox_S2.setChecked(True)
        self.checkBox_S2.setObjectName("checkBox_S2")

        self.checkBox_S2_WT3000 = QtWidgets.QCheckBox(self.groupBox_wt)
        self.checkBox_S2_WT3000.setGeometry(QtCore.QRect(100, 32, 22, 22))
        self.checkBox_S2_WT3000.setChecked(True)
        self.checkBox_S2_WT3000.setText("")
        self.checkBox_S2_WT3000.setObjectName("checkBox_S2_WT3000")
        self.label_S2_WT3000 = QtWidgets.QLabel(self.groupBox_wt)
        self.label_S2_WT3000.setGeometry(QtCore.QRect(125, 32, 56, 22))
        self.label_S2_WT3000.setObjectName("label_S2_WT3000")
        self.pushButton_S2_WT_3000_CONFIG = QtWidgets.QPushButton(self.groupBox_wt)
        self.pushButton_S2_WT_3000_CONFIG.setGeometry(QtCore.QRect(185, 28, 118, 31))
        self.pushButton_S2_WT_3000_CONFIG.setObjectName("pushButton_S2_WT_3000_CONFIG")

        self.checkBox_S2_WT1800 = QtWidgets.QCheckBox(self.groupBox_wt)
        self.checkBox_S2_WT1800.setGeometry(QtCore.QRect(318, 32, 22, 22))
        self.checkBox_S2_WT1800.setChecked(True)
        self.checkBox_S2_WT1800.setText("")
        self.checkBox_S2_WT1800.setObjectName("checkBox_S2_WT1800")
        self.label_S2_WT1800 = QtWidgets.QLabel(self.groupBox_wt)
        self.label_S2_WT1800.setGeometry(QtCore.QRect(343, 32, 56, 22))
        self.label_S2_WT1800.setObjectName("label_S2_WT1800")
        self.pushButton_S2_WT_1800_CONFIG = QtWidgets.QPushButton(self.groupBox_wt)
        self.pushButton_S2_WT_1800_CONFIG.setGeometry(QtCore.QRect(403, 28, 118, 31))
        self.pushButton_S2_WT_1800_CONFIG.setObjectName("pushButton_S2_WT_1800_CONFIG")

        self.checkBox_S2_WT1806E = QtWidgets.QCheckBox(self.groupBox_wt)
        self.checkBox_S2_WT1806E.setGeometry(QtCore.QRect(536, 32, 22, 22))
        self.checkBox_S2_WT1806E.setChecked(True)
        self.checkBox_S2_WT1806E.setText("")
        self.checkBox_S2_WT1806E.setObjectName("checkBox_S2_WT1806E")
        self.label_S2_WT1806E = QtWidgets.QLabel(self.groupBox_wt)
        self.label_S2_WT1806E.setGeometry(QtCore.QRect(561, 32, 56, 22))
        self.label_S2_WT1806E.setObjectName("label_S2_WT1806E")
        self.pushButton_S2_WT_1806E_CONFIG = QtWidgets.QPushButton(self.groupBox_wt)
        self.pushButton_S2_WT_1806E_CONFIG.setGeometry(QtCore.QRect(621, 28, 118, 31))
        self.pushButton_S2_WT_1806E_CONFIG.setObjectName("pushButton_S2_WT_1806E_CONFIG")

        self.checkBox_S2_WT5000 = QtWidgets.QCheckBox(self.groupBox_wt)
        self.checkBox_S2_WT5000.setGeometry(QtCore.QRect(754, 32, 22, 22))
        self.checkBox_S2_WT5000.setChecked(True)
        self.checkBox_S2_WT5000.setText("")
        self.checkBox_S2_WT5000.setObjectName("checkBox_S2_WT5000")
        self.label_S2_WT5000 = QtWidgets.QLabel(self.groupBox_wt)
        self.label_S2_WT5000.setGeometry(QtCore.QRect(779, 32, 56, 22))
        self.label_S2_WT5000.setObjectName("label_S2_WT5000")
        self.pushButton_S2_WT_5000_CONFIG = QtWidgets.QPushButton(self.groupBox_wt)
        self.pushButton_S2_WT_5000_CONFIG.setGeometry(QtCore.QRect(839, 28, 118, 31))
        self.pushButton_S2_WT_5000_CONFIG.setObjectName("pushButton_S2_WT_5000_CONFIG")

        self.checkBox_S2_update_rate = QtWidgets.QCheckBox(self.groupBox_wt)
        self.checkBox_S2_update_rate.setGeometry(QtCore.QRect(980, 32, 22, 22))
        self.checkBox_S2_update_rate.setChecked(True)
        self.checkBox_S2_update_rate.setText("")
        self.checkBox_S2_update_rate.setObjectName("checkBox_S2_update_rate")
        self.label_S2_update_rate = QtWidgets.QLabel(self.groupBox_wt)
        self.label_S2_update_rate.setGeometry(QtCore.QRect(1005, 32, 48, 22))
        self.label_S2_update_rate.setObjectName("label_S2_update_rate")
        self.textEdit_S2_update_rate = QtWidgets.QTextEdit(self.groupBox_wt)
        self.textEdit_S2_update_rate.setGeometry(QtCore.QRect(1055, 28, 56, 31))
        self.textEdit_S2_update_rate.setObjectName("textEdit_S2_update_rate")
        self.comboBox_S2_update_rate = QtWidgets.QComboBox(self.groupBox_wt)
        self.comboBox_S2_update_rate.setGeometry(QtCore.QRect(1118, 32, 72, 22))
        self.comboBox_S2_update_rate.setObjectName("comboBox_S2_update_rate")
        self.comboBox_S2_update_rate.addItem("")
        self.comboBox_S2_update_rate.addItem("")
        self.comboBox_S2_update_rate.addItem("")

        # step3～step11 上方：过频 / 欠频 标题栏
        self.groupBox_band_titles = QtWidgets.QGroupBox(Dialog_thaifrequencyadaptability)
        self.groupBox_band_titles.setGeometry(QtCore.QRect(0, 362, 1400, 30))
        self.groupBox_band_titles.setTitle("")
        self.groupBox_band_titles.setObjectName("groupBox_band_titles")
        self.label_band_title_guopin = QtWidgets.QLabel(self.groupBox_band_titles)
        self.label_band_title_guopin.setGeometry(QtCore.QRect(100, 6, 520, 20))
        self.label_band_title_guopin.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
        )
        self.label_band_title_guopin.setObjectName("label_band_title_guopin")
        self.label_band_title_qianpin = QtWidgets.QLabel(self.groupBox_band_titles)
        self.label_band_title_qianpin.setGeometry(QtCore.QRect(702, 6, 520, 20))
        self.label_band_title_qianpin.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
        )
        self.label_band_title_qianpin.setObjectName("label_band_title_qianpin")

        def _freq_side_widgets(side_gb, step_n, x0, side_tag):
            """side_tag: 'guopin'（过频）或 'qianpin'（欠频）"""
            lbl_range = QtWidgets.QLabel(side_gb)
            lbl_range.setGeometry(QtCore.QRect(x0 + 8, 14, 72, 20))
            lbl_range.setObjectName(
                "label_S%d_freq_band_%s" % (step_n, side_tag),
            )

            te_f0 = QtWidgets.QTextEdit(side_gb)
            te_f0.setGeometry(QtCore.QRect(x0 + 92, 8, 54, 30))
            te_f0.setObjectName(
                "textEdit_S%d_freq_start_%s" % (step_n, side_tag),
            )

            lbl_tilde = QtWidgets.QLabel(side_gb)
            lbl_tilde.setGeometry(QtCore.QRect(x0 + 152, 14, 16, 20))
            lbl_tilde.setObjectName(
                "label_S%d_tilde_%s" % (step_n, side_tag),
            )

            te_f1 = QtWidgets.QTextEdit(side_gb)
            te_f1.setGeometry(QtCore.QRect(x0 + 174, 8, 54, 30))
            te_f1.setObjectName(
                "textEdit_S%d_freq_end_%s" % (step_n, side_tag),
            )

            lbl_hz = QtWidgets.QLabel(side_gb)
            lbl_hz.setGeometry(QtCore.QRect(x0 + 236, 14, 28, 20))
            lbl_hz.setObjectName(
                "label_S%d_freq_unit_%s" % (step_n, side_tag),
            )

            lbl_tdur = QtWidgets.QLabel(side_gb)
            lbl_tdur.setGeometry(QtCore.QRect(x0 + 272, 14, 80, 20))
            lbl_tdur.setObjectName(
                "label_S%d_test_time_cap_%s" % (step_n, side_tag),
            )

            te_td = QtWidgets.QTextEdit(side_gb)
            te_td.setGeometry(QtCore.QRect(x0 + 362, 8, 62, 30))
            te_td.setObjectName(
                "textEdit_S%d_test_duration_%s" % (step_n, side_tag),
            )

            cmu = QtWidgets.QComboBox(side_gb)
            cmu.setGeometry(QtCore.QRect(x0 + 434, 10, 80, 24))
            cmu.setObjectName(
                "comboBox_S%d_test_time_unit_%s" % (step_n, side_tag),
            )
            cmu.addItem("")
            cmu.addItem("")
            cmu.addItem("")

            return {
                "lbl_range": lbl_range,
                "freq_start": te_f0,
                "lbl_tilde": lbl_tilde,
                "freq_end": te_f1,
                "lbl_hz": lbl_hz,
                "lbl_tdur": lbl_tdur,
                "duration": te_td,
                "unit": cmu,
            }

        self._freq_adapt_band_rows = []
        _row_y0 = 396
        _row_h = 50
        for _i in range(9):
            _sn_gp = 3 + _i
            _sn_qp = 12 + _i
            _y = _row_y0 + _i * _row_h
            gb = QtWidgets.QGroupBox(Dialog_thaifrequencyadaptability)
            gb.setGeometry(QtCore.QRect(0, _y, 1400, 46))
            gb.setTitle("")
            gb.setObjectName("groupBox_freq_S%d_S%d" % (_sn_gp, _sn_qp))

            cb_gp = QtWidgets.QCheckBox(gb)
            cb_gp.setGeometry(QtCore.QRect(20, 12, 72, 22))
            cb_gp.setChecked(True)
            cb_gp.setObjectName("checkBox_S%d" % _sn_gp)

            guopin_block = _freq_side_widgets(gb, _sn_gp, 100, "guopin")

            cb_qp = QtWidgets.QCheckBox(gb)
            cb_qp.setGeometry(QtCore.QRect(622, 12, 72, 22))
            cb_qp.setChecked(True)
            cb_qp.setObjectName("checkBox_S%d" % _sn_qp)

            qianpin_block = _freq_side_widgets(gb, _sn_qp, 702, "qianpin")

            self._freq_adapt_band_rows.append({
                "sn_guopin": _sn_gp,
                "sn_qianpin": _sn_qp,
                "gb": gb,
                "check_guopin": cb_gp,
                "check_qianpin": cb_qp,
                "guopin": guopin_block,
                "qianpin": qianpin_block,
            })

        # step_last：试验结束断电/保持（与 Immun 同源布局）
        self.groupBox_End = QtWidgets.QGroupBox(Dialog_thaifrequencyadaptability)
        self.groupBox_End.setGeometry(QtCore.QRect(0, 848, 1400, 112))
        self.groupBox_End.setTitle("")
        self.groupBox_End.setObjectName("groupBox_End")

        self.checkBox_S_End = QtWidgets.QCheckBox(self.groupBox_End)
        self.checkBox_S_End.setGeometry(QtCore.QRect(20, 17, 111, 21))
        self.checkBox_S_End.setChecked(True)
        self.checkBox_S_End.setObjectName("checkBox_S_End")

        self.label_End_AC_cap = QtWidgets.QLabel(self.groupBox_End)
        self.label_End_AC_cap.setGeometry(QtCore.QRect(140, 20, 81, 16))
        self.label_End_AC_cap.setObjectName("label_End_AC_cap")

        self.comboBox_S_End_AC = QtWidgets.QComboBox(self.groupBox_End)
        self.comboBox_S_End_AC.setGeometry(QtCore.QRect(220, 20, 60, 21))
        self.comboBox_S_End_AC.setObjectName("comboBox_S_End_AC")
        self.comboBox_S_End_AC.addItem("")
        self.comboBox_S_End_AC.addItem("")

        self.checkBox_S_End_DC1 = QtWidgets.QCheckBox(self.groupBox_End)
        self.checkBox_S_End_DC1.setGeometry(QtCore.QRect(100, 62, 121, 21))
        self.checkBox_S_End_DC1.setChecked(True)
        self.checkBox_S_End_DC1.setObjectName("checkBox_S_End_DC1")
        self.comboBox_S_End_DC1 = QtWidgets.QComboBox(self.groupBox_End)
        self.comboBox_S_End_DC1.setGeometry(QtCore.QRect(220, 60, 60, 21))
        self.comboBox_S_End_DC1.setObjectName("comboBox_S_End_DC1")
        self.comboBox_S_End_DC1.addItem("")
        self.comboBox_S_End_DC1.addItem("")

        self.checkBox_S_End_DC2 = QtWidgets.QCheckBox(self.groupBox_End)
        self.checkBox_S_End_DC2.setGeometry(QtCore.QRect(311, 62, 111, 21))
        self.checkBox_S_End_DC2.setChecked(True)
        self.checkBox_S_End_DC2.setObjectName("checkBox_S_End_DC2")
        self.comboBox_S_End_DC2 = QtWidgets.QComboBox(self.groupBox_End)
        self.comboBox_S_End_DC2.setGeometry(QtCore.QRect(430, 60, 60, 21))
        self.comboBox_S_End_DC2.setObjectName("comboBox_S_End_DC2")
        self.comboBox_S_End_DC2.addItem("")
        self.comboBox_S_End_DC2.addItem("")

        self.checkBox_S_End_DC3 = QtWidgets.QCheckBox(self.groupBox_End)
        self.checkBox_S_End_DC3.setGeometry(QtCore.QRect(530, 60, 111, 21))
        self.checkBox_S_End_DC3.setChecked(True)
        self.checkBox_S_End_DC3.setObjectName("checkBox_S_End_DC3")
        self.comboBox_S_End_DC3 = QtWidgets.QComboBox(self.groupBox_End)
        self.comboBox_S_End_DC3.setGeometry(QtCore.QRect(650, 60, 60, 21))
        self.comboBox_S_End_DC3.setObjectName("comboBox_S_End_DC3")
        self.comboBox_S_End_DC3.addItem("")
        self.comboBox_S_End_DC3.addItem("")

        self.checkBox_S_End_DC4 = QtWidgets.QCheckBox(self.groupBox_End)
        self.checkBox_S_End_DC4.setGeometry(QtCore.QRect(740, 60, 121, 21))
        self.checkBox_S_End_DC4.setChecked(True)
        self.checkBox_S_End_DC4.setObjectName("checkBox_S_End_DC4")
        self.comboBox_S_End_DC4 = QtWidgets.QComboBox(self.groupBox_End)
        self.comboBox_S_End_DC4.setGeometry(QtCore.QRect(860, 60, 60, 21))
        self.comboBox_S_End_DC4.setObjectName("comboBox_S_End_DC4")
        self.comboBox_S_End_DC4.addItem("")
        self.comboBox_S_End_DC4.addItem("")

        self.pushButton_ReadSettingFile = QtWidgets.QPushButton(Dialog_thaifrequencyadaptability)
        self.pushButton_ReadSettingFile.setGeometry(QtCore.QRect(510, 1090, 93, 28))
        self.pushButton_ReadSettingFile.setObjectName("pushButton_ReadSettingFile")

        self.pushButton_SaveSettingFile = QtWidgets.QPushButton(Dialog_thaifrequencyadaptability)
        self.pushButton_SaveSettingFile.setGeometry(QtCore.QRect(630, 1090, 93, 28))
        self.pushButton_SaveSettingFile.setObjectName("pushButton_SaveSettingFile")

        self.pushButton_Send = QtWidgets.QPushButton(Dialog_thaifrequencyadaptability)
        self.pushButton_Send.setGeometry(QtCore.QRect(1050, 1050, 131, 61))
        self.pushButton_Send.setObjectName("pushButton_Send")

        self.groupBox_4.raise_()
        self.groupBox_2.raise_()
        self.groupBox.raise_()
        self.groupBox_wt.raise_()
        self.groupBox_band_titles.raise_()
        for _r in self._freq_adapt_band_rows:
            _r["gb"].raise_()
        self.groupBox_End.raise_()
        self.pushButton_Send.raise_()
        self.pushButton_SaveSettingFile.raise_()
        self.pushButton_ReadSettingFile.raise_()

        self.retranslateUi(Dialog_thaifrequencyadaptability)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaifrequencyadaptability)

    def retranslateUi(self, Dialog_thaifrequencyadaptability):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaifrequencyadaptability.setWindowTitle(
            _translate("Dialog_thaifrequencyadaptability", "频率适应性项目配置")
        )
        self.pushButton_Send.setText(_translate("Dialog_thaifrequencyadaptability", "提交"))
        self.pushButton_ReadSettingFile.setText(_translate("Dialog_thaifrequencyadaptability", "读取设定"))
        self.pushButton_SaveSettingFile.setText(_translate("Dialog_thaifrequencyadaptability", "保存设定"))
        self.label_18.setText(_translate("Dialog_thaifrequencyadaptability", "Hz"))
        self.label_19.setText(_translate("Dialog_thaifrequencyadaptability", "频率"))
        self.textEdit_S1_AC_FR.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">50</span></p></body></html>"))
        self.comboBox_S1_AC_2.setItemText(0, _translate("Dialog_thaifrequencyadaptability", "单相"))
        self.comboBox_S1_AC_2.setItemText(1, _translate("Dialog_thaifrequencyadaptability", "三相"))
        self.label_107.setText(_translate("Dialog_thaifrequencyadaptability", "V"))
        self.label_113.setText(_translate("Dialog_thaifrequencyadaptability", "交流电压2"))
        self.comboBox_S1_AC.setItemText(0, _translate("Dialog_thaifrequencyadaptability", "开启"))
        self.comboBox_S1_AC.setItemText(1, _translate("Dialog_thaifrequencyadaptability", "关闭"))
        self.label_4.setText(_translate("Dialog_thaifrequencyadaptability", "交流电压1"))
        self.label_123.setText(_translate("Dialog_thaifrequencyadaptability", "交流电压3"))
        self.textEdit_S1_AC_VOLT_2.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">230</span></p></body></html>"))
        self.textEdit_S1_AC_VOLT.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">230</span></p></body></html>"))
        self.label_5.setText(_translate("Dialog_thaifrequencyadaptability", "V"))
        self.textEdit_S1_AC_VOLT_3.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">230</span></p></body></html>"))
        self.label_3.setText(_translate("Dialog_thaifrequencyadaptability", "交流电源"))
        self.checkBox_S1.setText(_translate("Dialog_thaifrequencyadaptability", "step1"))
        self.label_102.setText(_translate("Dialog_thaifrequencyadaptability", "V"))
        self.label_17.setText(_translate("Dialog_thaifrequencyadaptability", "Vmp"))
        self.textEdit_S1_DC2_Isc.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">10</span></p></body></html>"))
        self.textEdit_S1_DC2_PF.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">100</span></p></body></html>"))
        self.textEdit_S1_DC3_Voc.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">220</span></p></body></html>"))
        self.textEdit_S1_DC3_Isc.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">10</span></p></body></html>"))
        self.label_110.setText(_translate("Dialog_thaifrequencyadaptability", "V"))
        self.textEdit_S1_DC1_Isc.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">10</span></p></body></html>"))
        self.label_125.setText(_translate("Dialog_thaifrequencyadaptability", "Imp"))
        self.label_128.setText(_translate("Dialog_thaifrequencyadaptability", "A"))
        self.label_112.setText(_translate("Dialog_thaifrequencyadaptability", "%"))
        self.textEdit_S1_DC1_VOLT.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">220</span></p></body></html>"))
        self.label_55.setText(_translate("Dialog_thaifrequencyadaptability", "%"))
        self.label_116.setText(_translate("Dialog_thaifrequencyadaptability", "功率"))
        self.comboBox_S1_DC4.setItemText(0, _translate("Dialog_thaifrequencyadaptability", "开启"))
        self.comboBox_S1_DC4.setItemText(1, _translate("Dialog_thaifrequencyadaptability", "关闭"))
        self.checkBox_S1_DC4.setText(_translate("Dialog_thaifrequencyadaptability", "直流电源4"))
        self.label_109.setText(_translate("Dialog_thaifrequencyadaptability", "V"))
        self.label_57.setText(_translate("Dialog_thaifrequencyadaptability", "A"))
        self.label_105.setText(_translate("Dialog_thaifrequencyadaptability", "Isc"))
        self.textEdit_S1_DC3_VOLT.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">220</span></p></body></html>"))
        self.label_120.setText(_translate("Dialog_thaifrequencyadaptability", "Imp"))
        self.label_14.setText(_translate("Dialog_thaifrequencyadaptability", "Vmp"))
        self.label_59.setText(_translate("Dialog_thaifrequencyadaptability", "Isc"))
        self.label_13.setText(_translate("Dialog_thaifrequencyadaptability", "Vmp"))
        self.label_53.setText(_translate("Dialog_thaifrequencyadaptability", "A"))
        self.comboBox_S1_DC1.setItemText(0, _translate("Dialog_thaifrequencyadaptability", "开启"))
        self.comboBox_S1_DC1.setItemText(1, _translate("Dialog_thaifrequencyadaptability", "关闭"))
        self.checkBox_S1_DC3.setText(_translate("Dialog_thaifrequencyadaptability", "直流电源3"))
        self.textEdit_S1_DC4_VOLT.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">220</span></p></body></html>"))
        self.label_58.setText(_translate("Dialog_thaifrequencyadaptability", "Imp"))
        self.label_129.setText(_translate("Dialog_thaifrequencyadaptability", "功率"))
        self.comboBox_S1_DC2.setItemText(0, _translate("Dialog_thaifrequencyadaptability", "开启"))
        self.comboBox_S1_DC2.setItemText(1, _translate("Dialog_thaifrequencyadaptability", "关闭"))
        self.textEdit_S1_DC2_VOLT.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">220</span></p></body></html>"))
        self.textEdit_S1_DC3_PF.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">100</span></p></body></html>"))
        self.label_117.setText(_translate("Dialog_thaifrequencyadaptability", "%"))
        self.label_51.setText(_translate("Dialog_thaifrequencyadaptability", "V"))
        self.textEdit_S1_DC4_CURR.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">10</span></p></body></html>"))
        self.label_101.setText(_translate("Dialog_thaifrequencyadaptability", "Isc"))
        self.label_127.setText(_translate("Dialog_thaifrequencyadaptability", "V"))
        self.label_100.setText(_translate("Dialog_thaifrequencyadaptability", "功率"))
        self.label_106.setText(_translate("Dialog_thaifrequencyadaptability", "Isc"))
        self.label_118.setText(_translate("Dialog_thaifrequencyadaptability", "A"))
        self.label_119.setText(_translate("Dialog_thaifrequencyadaptability", "V"))
        self.checkBox_S1_DC1.setText(_translate("Dialog_thaifrequencyadaptability", "直流电源1"))
        self.label_54.setText(_translate("Dialog_thaifrequencyadaptability", "Vmp"))
        self.comboBox_S1_DC3.setItemText(0, _translate("Dialog_thaifrequencyadaptability", "开启"))
        self.comboBox_S1_DC3.setItemText(1, _translate("Dialog_thaifrequencyadaptability", "关闭"))
        self.textEdit_S1_DC1_Voc.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">220</span></p></body></html>"))
        self.label_103.setText(_translate("Dialog_thaifrequencyadaptability", "A"))
        self.label_52.setText(_translate("Dialog_thaifrequencyadaptability", "Imp"))
        self.textEdit_S1_DC4_Isc.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">10</span></p></body></html>"))
        self.label_104.setText(_translate("Dialog_thaifrequencyadaptability", "功率"))
        self.textEdit_S1_DC3_CURR.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">10</span></p></body></html>"))
        self.label_114.setText(_translate("Dialog_thaifrequencyadaptability", "A"))
        self.label_126.setText(_translate("Dialog_thaifrequencyadaptability", "V"))
        self.label_111.setText(_translate("Dialog_thaifrequencyadaptability", "V"))
        self.label_108.setText(_translate("Dialog_thaifrequencyadaptability", "Voc"))
        self.label_122.setText(_translate("Dialog_thaifrequencyadaptability", "Voc"))
        self.label_56.setText(_translate("Dialog_thaifrequencyadaptability", "A"))
        self.textEdit_S1_DC4_PF.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">100</span></p></body></html>"))
        self.textEdit_S1_DC2_Voc.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">220</span></p></body></html>"))
        self.textEdit_S1_DC1_PF.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">100</span></p></body></html>"))
        self.label_15.setText(_translate("Dialog_thaifrequencyadaptability", "V"))
        self.textEdit_S1_DC1_CURR.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">10</span></p></body></html>"))
        self.checkBox_S1_DC2.setText(_translate("Dialog_thaifrequencyadaptability", "直流电源2"))
        self.label_130.setText(_translate("Dialog_thaifrequencyadaptability", "Voc"))
        self.label_124.setText(_translate("Dialog_thaifrequencyadaptability", "A"))
        self.label_121.setText(_translate("Dialog_thaifrequencyadaptability", "Voc"))
        self.label_115.setText(_translate("Dialog_thaifrequencyadaptability", "%"))
        self.textEdit_S1_DC2_CURR.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">10</span></p></body></html>"))
        self.textEdit_S1_DC4_Voc.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">220</span></p></body></html>"))
        self.comboBox_S1_TIME.setItemText(0, _translate("Dialog_thaifrequencyadaptability", "分钟"))
        self.comboBox_S1_TIME.setItemText(1, _translate("Dialog_thaifrequencyadaptability", "秒"))
        self.comboBox_S1_TIME.setItemText(2, _translate("Dialog_thaifrequencyadaptability", "毫秒"))
        self.textEdit_S1_TIME.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">5</span></p></body></html>"))
        self.label_132.setText(_translate("Dialog_thaifrequencyadaptability", "启机时间:"))
        self.comboBox_S1_ACWaitTIME.setItemText(0, _translate("Dialog_thaifrequencyadaptability", "秒"))
        self.comboBox_S1_ACWaitTIME.setItemText(1, _translate("Dialog_thaifrequencyadaptability", "分钟"))
        self.comboBox_S1_ACWaitTIME.setItemText(2, _translate("Dialog_thaifrequencyadaptability", "毫秒"))
        self.label_131.setText(_translate("Dialog_thaifrequencyadaptability", "等待时间:"))
        self.textEdit_S1_ACWaitTIME.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">3</span></p></body></html>"))
        self.groupBox_wt.setTitle(_translate("Dialog_thaifrequencyadaptability", ""))
        self.checkBox_S2.setText(_translate("Dialog_thaifrequencyadaptability", "step2"))
        self.label_S2_WT3000.setText(_translate("Dialog_thaifrequencyadaptability", "WT3000"))
        self.pushButton_S2_WT_3000_CONFIG.setText(_translate("Dialog_thaifrequencyadaptability", "WT_3000_config"))
        self.label_S2_WT1800.setText(_translate("Dialog_thaifrequencyadaptability", "WT1800"))
        self.pushButton_S2_WT_1800_CONFIG.setText(_translate("Dialog_thaifrequencyadaptability", "WT_1800_config"))
        self.label_S2_WT1806E.setText(_translate("Dialog_thaifrequencyadaptability", "WT1806E"))
        self.pushButton_S2_WT_1806E_CONFIG.setText(_translate("Dialog_thaifrequencyadaptability", "WT_1806E_config"))
        self.label_S2_WT5000.setText(_translate("Dialog_thaifrequencyadaptability", "WT5000"))
        self.pushButton_S2_WT_5000_CONFIG.setText(_translate("Dialog_thaifrequencyadaptability", "WT_5000_config"))
        self.label_S2_update_rate.setText(_translate("Dialog_thaifrequencyadaptability", "更新率"))
        self.textEdit_S2_update_rate.setHtml(_translate("Dialog_thaifrequencyadaptability", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'宋体\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">50</span></p></body></html>"))
        self.comboBox_S2_update_rate.setItemText(0, _translate("Dialog_thaifrequencyadaptability", "分钟"))
        self.comboBox_S2_update_rate.setItemText(1, _translate("Dialog_thaifrequencyadaptability", "秒"))
        self.comboBox_S2_update_rate.setItemText(2, _translate("Dialog_thaifrequencyadaptability", "毫秒"))
        self.comboBox_S2_update_rate.setCurrentIndex(2)
        self.groupBox_band_titles.setTitle(
            _translate("Dialog_thaifrequencyadaptability", ""),
        )
        self.label_band_title_guopin.setText(
            _translate("Dialog_thaifrequencyadaptability", "过频"),
        )
        self.label_band_title_qianpin.setText(
            _translate("Dialog_thaifrequencyadaptability", "欠频"),
        )

        def _translate_freq_side_widgets(block):
            block["lbl_range"].setText(
                _translate("Dialog_thaifrequencyadaptability", "频率区间"),
            )
            block["lbl_tilde"].setText(
                _translate("Dialog_thaifrequencyadaptability", "~"),
            )
            block["lbl_hz"].setText(
                _translate("Dialog_thaifrequencyadaptability", "Hz"),
            )
            block["lbl_tdur"].setText(
                _translate("Dialog_thaifrequencyadaptability", "测试时间："),
            )
            block["freq_start"].setHtml(
                _translate(
                    "Dialog_thaifrequencyadaptability",
                    _FREQ_ADAPT_HTML_TPL % "49.5",
                ),
            )
            block["freq_end"].setHtml(
                _translate(
                    "Dialog_thaifrequencyadaptability",
                    _FREQ_ADAPT_HTML_TPL % "50.5",
                ),
            )
            block["duration"].setHtml(
                _translate(
                    "Dialog_thaifrequencyadaptability",
                    _FREQ_ADAPT_HTML_TPL % "60",
                ),
            )
            block["unit"].setItemText(
                0,
                _translate("Dialog_thaifrequencyadaptability", "秒"),
            )
            block["unit"].setItemText(
                1,
                _translate("Dialog_thaifrequencyadaptability", "分钟"),
            )
            block["unit"].setItemText(
                2,
                _translate("Dialog_thaifrequencyadaptability", "小时"),
            )
            block["unit"].setCurrentIndex(0)

        for row in self._freq_adapt_band_rows:
            row["check_guopin"].setText(
                _translate(
                    "Dialog_thaifrequencyadaptability",
                    "step%d" % row["sn_guopin"],
                ),
            )
            row["check_qianpin"].setText(
                _translate(
                    "Dialog_thaifrequencyadaptability",
                    "step%d" % row["sn_qianpin"],
                ),
            )
            _translate_freq_side_widgets(row["guopin"])
            _translate_freq_side_widgets(row["qianpin"])

        self.groupBox_End.setTitle(_translate("Dialog_thaifrequencyadaptability", ""))
        self.checkBox_S_End.setText(
            _translate("Dialog_thaifrequencyadaptability", "step_last"),
        )
        self.label_End_AC_cap.setText(
            _translate("Dialog_thaifrequencyadaptability", "交流电源"),
        )
        self.comboBox_S_End_AC.setItemText(
            0,
            _translate("Dialog_thaifrequencyadaptability", "关闭"),
        )
        self.comboBox_S_End_AC.setItemText(
            1,
            _translate("Dialog_thaifrequencyadaptability", "开启"),
        )
        self.comboBox_S_End_AC.setCurrentIndex(0)

        self.checkBox_S_End_DC1.setText(
            _translate("Dialog_thaifrequencyadaptability", "直流电源1"),
        )
        self.checkBox_S_End_DC2.setText(
            _translate("Dialog_thaifrequencyadaptability", "直流电源2"),
        )
        self.checkBox_S_End_DC3.setText(
            _translate("Dialog_thaifrequencyadaptability", "直流电源3"),
        )
        self.checkBox_S_End_DC4.setText(
            _translate("Dialog_thaifrequencyadaptability", "直流电源4"),
        )
        for _cb in (
            self.comboBox_S_End_DC1,
            self.comboBox_S_End_DC2,
            self.comboBox_S_End_DC3,
            self.comboBox_S_End_DC4,
        ):
            _cb.setItemText(0, _translate("Dialog_thaifrequencyadaptability", "关闭"))
            _cb.setItemText(1, _translate("Dialog_thaifrequencyadaptability", "开启"))
            _cb.setCurrentIndex(0)
