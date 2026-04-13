import re
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, \
    QFileDialog, QMessageBox
import csv

arrayRow1 = ['Style',
    'comboBox_SigmA1',
        'comboBox_SigmA2',"comboBox_SigmB1", "comboBox_SigmB2",
        "comboBox_ReplaceRate", "comboBox_ProjectNum",
    "comboBox_AutoSave",
        "textEdit_StopTime", "textEdit_SavePath", "checkBox_AutoName",
    "textEdit_FileNameList",
    "checkBox_SetElement1", "checkBox_SetElement2", "checkBox_SetElement3",
        "checkBox_SetElement4",
    "checkBox_SetSigma", "checkBox_SetSigmaA", "checkBox_SetSigmaB",
    "checkBox_SetUrms", "checkBox_SetUmn", "checkBox_SetUdc", "checkBox_SetUrmn",
        "checkBox_SetUac", "checkBox_SetRngU", "checkBox_SetCfU",

    "checkBox_SetIrms", "checkBox_SetImn", "checkBox_SetIdc", "checkBox_SetIrmn", 
        "checkBox_SetIac", "checkBox_SetRngI", "checkBox_SetCfI",

    "checkBox_SetUppeak", "checkBox_SetUmpeak", "checkBox_SetIppeak", "checkBox_SetImpeak",
        "checkBox_SetPppeak", "checkBox_SetPmpeak",
    "checkBox_SetP", "checkBox_SetS", "checkBox_SetQ", "checkBox_SetPF",
        "checkBox_SetPhi","checkBox_SetPc",
    "checkBox_SetUfnd", "checkBox_SetIfnd", "checkBox_SetPfnd", "checkBox_SetSfnd",
        "checkBox_SetQfnd","checkBox_SetLambdafnd", "checkBox_SetPhifnd",

    "checkBox_SetFreqU", "checkBox_SetFreqI", "checkBox_SetFreq2U", "checkBox_SetFreq2I",

    "checkBox_SetTime", "checkBox_SetWP", "checkBox_SetWPPlus", "checkBox_SetWPMinus",
        "checkBox_Setq", "checkBox_SetqPlus", "checkBox_SetqMinus", "checkBox_SetWS", "checkBox_SetWQ",
    "checkBox_SetEta1", "checkBox_SetEta2", "checkBox_SetEta3", "checkBox_SetEta4",

    "checkBox_SetEvent1", "checkBox_SetEvent2", "checkBox_SetEvent3", "checkBox_SetEvent4",
        "checkBox_SetEvent5", "checkBox_SetEvent6", "checkBox_SetEvent7", "checkBox_SetEvent8",
    "textEdit_SetStart", "textEdit_SetStop",

    "checkBox_SetUk", "checkBox_SetIk", "checkBox_SetPk", "checkBox_SetSk", "checkBox_SetQk",
        "checkBox_SetPFk", "checkBox_SetFreqPLL1", "checkBox_SetFreqPLL2",

    "checkBox_SetPhik", "checkBox_SetPhiUk", "checkBox_SetPhiIk",
        "checkBox_SetUhdfk", "checkBox_SetIhdfk", "checkBox_SetPhdfk",
    'checkBox_SetZk', "checkBox_SetRsk", "checkBox_SetXsk", "checkBox_SetRpk", "checkBox_SetXpk",
    "checkBox_SetUthd", "checkBox_SetIthd", "checkBox_SetPthd", 'checkBox_SetUthf', 'checkBox_SetIthf',
    'checkBox_SetUtif', 'checkBox_SetItif', 'checkBox_Sethvf', 'checkBox_Sethcf', "checkBox_SetK_factor",
    'checkBox_SetPhiUi_Uj', 'checkBox_SetPhiUi_Uk', 'checkBox_SetPhiUi_Ii', "checkBox_SetPhiUi_Ij",
        "checkBox_SetPhiUi_Ik",
    'checkBox_SetDeltaU1', 'checkBox_SetDeltaU2', 'checkBox_SetDeltaU3', "checkBox_SetDeltaUSigma",
        "checkBox_SetDeltaI", "checkBox_SetDeltaP1", "checkBox_SetDeltaP2", "checkBox_SetDeltaP3",
        "checkBox_SetDeltaPSigma",
    "checkBox_SetTSDate", "checkBox_SetTSTime", "checkBox_SetTSSubsec",
    'checkBox_SetF01', 'checkBox_SetF02', 'checkBox_SetF03', 'checkBox_SetF04', 'checkBox_SetF05',
    'checkBox_SetF06', 'checkBox_SetF07', 'checkBox_SetF08', 'checkBox_SetF09', 'checkBox_SetF10',
    'checkBox_SetF11', 'checkBox_SetF12', 'checkBox_SetF13', 'checkBox_SetF14', 'checkBox_SetF15',
    'checkBox_SetF16', 'checkBox_SetF17', 'checkBox_SetF18', 'checkBox_SetF19', 'checkBox_SetF20',
]

# WT1806E配置保存设定
def Save_File_ThaiWT5000_Config(uiThiaWT5000):

    arrayRow2 = ['Thai_WT5000_Config']

    comboBox_SigmA1 = uiThiaWT5000.comboBox_SigmA1.currentIndex()
    arrayRow2.append(comboBox_SigmA1)

    comboBox_SigmA2 = uiThiaWT5000.comboBox_SigmA2.currentIndex()
    arrayRow2.append(comboBox_SigmA2)

    comboBox_SigmB1 = uiThiaWT5000.comboBox_SigmB1.currentIndex()
    arrayRow2.append(comboBox_SigmB1)

    comboBox_SigmB2 = uiThiaWT5000.comboBox_SigmB2.currentIndex()
    arrayRow2.append(comboBox_SigmB2)

    comboBox_ReplaceRate = uiThiaWT5000.comboBox_ReplaceRate.currentIndex()
    arrayRow2.append(comboBox_ReplaceRate)

    comboBox_ProjectNum = uiThiaWT5000.comboBox_ProjectNum.currentIndex()
    arrayRow2.append(comboBox_ProjectNum)

    comboBox_AutoSave = uiThiaWT5000.comboBox_AutoSave.currentIndex()
    arrayRow2.append(comboBox_AutoSave)

    textEdit_StopTime = uiThiaWT5000.textEdit_StopTime.toPlainText()
    arrayRow2.append(textEdit_StopTime)
    
    textEdit_SavePath = uiThiaWT5000.textEdit_SavePath.toPlainText()
    arrayRow2.append(textEdit_SavePath)

    if uiThiaWT5000.checkBox_AutoName.isChecked():
        checkBox_AutoName = '1'
    else:
        checkBox_AutoName = '0'
    arrayRow2.append(checkBox_AutoName)

    textEdit_FileNameList = uiThiaWT5000.textEdit_FileNameList.toPlainText()
    arrayRow2.append(textEdit_FileNameList)

    if uiThiaWT5000.checkBox_SetElement1.isChecked():
        checkBox_SetElement1 = '1'
    else:
        checkBox_SetElement1 = ''
    arrayRow2.append(checkBox_SetElement1)

    if uiThiaWT5000.checkBox_SetElement2.isChecked():
        checkBox_SetElement2 = '1'
    else:
        checkBox_SetElement2 = ''
    arrayRow2.append(checkBox_SetElement2)

    if uiThiaWT5000.checkBox_SetElement3.isChecked():
        checkBox_SetElement3 = '1'
    else:
        checkBox_SetElement3 = ''
    arrayRow2.append(checkBox_SetElement3)

    if uiThiaWT5000.checkBox_SetElement4.isChecked():
        checkBox_SetElement4 = '1'
    else:
        checkBox_SetElement4 = ''
    arrayRow2.append(checkBox_SetElement4)

    # line2
    if uiThiaWT5000.checkBox_SetSigma.isChecked():
        checkBox_SetSigma = '1'
    else:
        checkBox_SetSigma = ''
    arrayRow2.append(checkBox_SetSigma)

    if uiThiaWT5000.checkBox_SetSigmaA.isChecked():
        checkBox_SetSigmaA = '1'
    else:
        checkBox_SetSigmaA = ''
    arrayRow2.append(checkBox_SetSigmaA)

    if uiThiaWT5000.checkBox_SetSigmaB.isChecked():
        checkBox_SetSigmaB = '1'
    else:
        checkBox_SetSigmaB = ''
    arrayRow2.append(checkBox_SetSigmaB)

    # line3
    if uiThiaWT5000.checkBox_SetUrms.isChecked():
        checkBox_SetUrms = '1'
    else:
        checkBox_SetUrms = ''
    arrayRow2.append(checkBox_SetUrms)

    if uiThiaWT5000.checkBox_SetUmn.isChecked():
        checkBox_SetUmn = '1'
    else:
        checkBox_SetUmn = ''
    arrayRow2.append(checkBox_SetUmn)

    if uiThiaWT5000.checkBox_SetUdc.isChecked():
        checkBox_SetUdc = '1'
    else:
        checkBox_SetUdc = ''
    arrayRow2.append(checkBox_SetUdc)

    if uiThiaWT5000.checkBox_SetUrmn.isChecked():
        checkBox_SetUrmn = '1'
    else:
        checkBox_SetUrmn = ''
    arrayRow2.append(checkBox_SetUrmn)

    if uiThiaWT5000.checkBox_SetUac.isChecked():
        checkBox_SetUac = '1'
    else:
        checkBox_SetUac = ''
    arrayRow2.append(checkBox_SetUac)

    if uiThiaWT5000.checkBox_SetRngU.isChecked():
        checkBox_SetRngU = '1'
    else:
        checkBox_SetRngU = ''
    arrayRow2.append(checkBox_SetRngU)

    if uiThiaWT5000.checkBox_SetCfU.isChecked():
        checkBox_SetCfU = '1'
    else:
        checkBox_SetCfU = ''
    arrayRow2.append(checkBox_SetCfU)

    # line4
    if uiThiaWT5000.checkBox_SetIrms.isChecked():
        checkBox_SetIrms = '1'
    else:
        checkBox_SetIrms = ''
    arrayRow2.append(checkBox_SetIrms)

    if uiThiaWT5000.checkBox_SetImn.isChecked():
        checkBox_SetImn = '1'
    else:
        checkBox_SetImn = ''
    arrayRow2.append(checkBox_SetImn)

    if uiThiaWT5000.checkBox_SetIdc.isChecked():
        checkBox_SetIdc = '1'
    else:
        checkBox_SetIdc = ''
    arrayRow2.append(checkBox_SetIdc)

    if uiThiaWT5000.checkBox_SetIrmn.isChecked():
        checkBox_SetIrmn = '1'
    else:
        checkBox_SetIrmn = ''
    arrayRow2.append(checkBox_SetIrmn)

    if uiThiaWT5000.checkBox_SetIac.isChecked():
        checkBox_SetIac = '1'
    else:
        checkBox_SetIac = ''
    arrayRow2.append(checkBox_SetIac)

    if uiThiaWT5000.checkBox_SetRngI.isChecked():
        checkBox_SetRngI = '1'
    else:
        checkBox_SetRngI = ''
    arrayRow2.append(checkBox_SetRngI)

    if uiThiaWT5000.checkBox_SetCfI.isChecked():
        checkBox_SetCfI = '1'
    else:
        checkBox_SetCfI = ''
    arrayRow2.append(checkBox_SetCfI)

    # line5
    if uiThiaWT5000.checkBox_SetUppeak.isChecked():
        checkBox_SetUppeak = '1'
    else:
        checkBox_SetUppeak = ''
    arrayRow2.append(checkBox_SetUppeak)

    if uiThiaWT5000.checkBox_SetUmpeak.isChecked():
        checkBox_SetUmpeak = '1'
    else:
        checkBox_SetUmpeak = ''
    arrayRow2.append(checkBox_SetUmpeak)

    if uiThiaWT5000.checkBox_SetIppeak.isChecked():
        checkBox_SetIppeak = '1'
    else:
        checkBox_SetIppeak = ''
    arrayRow2.append(checkBox_SetIppeak)

    if uiThiaWT5000.checkBox_SetImpeak.isChecked():
        checkBox_SetImpeak = '1'
    else:
        checkBox_SetImpeak = ''
    arrayRow2.append(checkBox_SetImpeak)

    if uiThiaWT5000.checkBox_SetPppeak.isChecked():
        checkBox_SetPppeak = '1'
    else:
        checkBox_SetPppeak = ''
    arrayRow2.append(checkBox_SetPppeak)

    if uiThiaWT5000.checkBox_SetPmpeak.isChecked():
        checkBox_SetPmpeak = '1'
    else:
        checkBox_SetPmpeak = ''
    arrayRow2.append(checkBox_SetPmpeak)

    # line6
    if uiThiaWT5000.checkBox_SetP.isChecked():
        checkBox_SetP = '1'
    else:
        checkBox_SetP = ''
    arrayRow2.append(checkBox_SetP)

    if uiThiaWT5000.checkBox_SetS.isChecked():
        checkBox_SetS = '1'
    else:
        checkBox_SetS = ''
    arrayRow2.append(checkBox_SetS)

    if uiThiaWT5000.checkBox_SetQ.isChecked():
        checkBox_SetQ = '1'
    else:
        checkBox_SetQ = ''
    arrayRow2.append(checkBox_SetQ)

    if uiThiaWT5000.checkBox_SetPF.isChecked():
        checkBox_SetPF = '1'
    else:
        checkBox_SetPF = ''
    arrayRow2.append(checkBox_SetPF)

    if uiThiaWT5000.checkBox_SetPhi.isChecked():
        checkBox_SetPhi = '1'
    else:
        checkBox_SetPhi = ''
    arrayRow2.append(checkBox_SetPhi)

    if uiThiaWT5000.checkBox_SetPc.isChecked():
        checkBox_SetPc = '1'
    else:
        checkBox_SetPc = ''
    arrayRow2.append(checkBox_SetPc)

    # line7
    if uiThiaWT5000.checkBox_SetUfnd.isChecked():
        checkBox_SetUfnd = '1'
    else:
        checkBox_SetUfnd = ''
    arrayRow2.append(checkBox_SetUfnd)

    if uiThiaWT5000.checkBox_SetIfnd.isChecked():
        checkBox_SetIfnd = '1'
    else:
        checkBox_SetIfnd = ''
    arrayRow2.append(checkBox_SetIfnd)

    if uiThiaWT5000.checkBox_SetPfnd.isChecked():
        checkBox_SetPfnd = '1'
    else:
        checkBox_SetPfnd = ''
    arrayRow2.append(checkBox_SetPfnd)

    if uiThiaWT5000.checkBox_SetSfnd.isChecked():
        checkBox_SetSfnd = '1'
    else:
        checkBox_SetSfnd = ''
    arrayRow2.append(checkBox_SetSfnd)

    if uiThiaWT5000.checkBox_SetQfnd.isChecked():
        checkBox_SetQfnd = '1'
    else:
        checkBox_SetQfnd = ''
    arrayRow2.append(checkBox_SetQfnd)

    if uiThiaWT5000.checkBox_SetLambdafnd.isChecked():
        checkBox_SetLambdafnd = '1'
    else:
        checkBox_SetLambdafnd = ''
    arrayRow2.append(checkBox_SetLambdafnd)

    if uiThiaWT5000.checkBox_SetPhifnd.isChecked():
        checkBox_SetPhifnd = '1'
    else:
        checkBox_SetPhifnd = ''
    arrayRow2.append(checkBox_SetPhifnd)

    # line8
    if uiThiaWT5000.checkBox_SetFreqU.isChecked():
        checkBox_SetFreqU = '1'
    else:
        checkBox_SetFreqU = ''
    arrayRow2.append(checkBox_SetFreqU)

    if uiThiaWT5000.checkBox_SetFreqI.isChecked():
        checkBox_SetFreqI = '1'
    else:
        checkBox_SetFreqI = ''
    arrayRow2.append(checkBox_SetFreqI)

    if uiThiaWT5000.checkBox_SetFreq2U.isChecked():
        checkBox_SetFreq2U = '1'
    else:
        checkBox_SetFreq2U = ''
    arrayRow2.append(checkBox_SetFreq2U)

    if uiThiaWT5000.checkBox_SetFreq2I.isChecked():
        checkBox_SetFreq2I = '1'
    else:
        checkBox_SetFreq2I = ''
    arrayRow2.append(checkBox_SetFreq2I)

    # line9
    if uiThiaWT5000.checkBox_SetTime.isChecked():
        checkBox_SetTime = '1'
    else:
        checkBox_SetTime = ''
    arrayRow2.append(checkBox_SetTime)

    if uiThiaWT5000.checkBox_SetWP.isChecked():
        checkBox_SetWP = '1'
    else:
        checkBox_SetWP = ''
    arrayRow2.append(checkBox_SetWP)

    if uiThiaWT5000.checkBox_SetWPPlus.isChecked():
        checkBox_SetWPPlus = '1'
    else:
        checkBox_SetWPPlus = ''
    arrayRow2.append(checkBox_SetWPPlus)

    if uiThiaWT5000.checkBox_SetWPMinus.isChecked():
        checkBox_SetWPMinus = '1'
    else:
        checkBox_SetWPMinus = ''
    arrayRow2.append(checkBox_SetWPMinus)

    if uiThiaWT5000.checkBox_Setq.isChecked():
        checkBox_Setq = '1'
    else:
        checkBox_Setq = ''
    arrayRow2.append(checkBox_Setq)

    if uiThiaWT5000.checkBox_SetqPlus.isChecked():
        checkBox_SetqPlus = '1'
    else:
        checkBox_SetqPlus = ''
    arrayRow2.append(checkBox_SetqPlus)

    if uiThiaWT5000.checkBox_SetqMinus.isChecked():
        checkBox_SetqMinus = '1'
    else:
        checkBox_SetqMinus = ''
    arrayRow2.append(checkBox_SetqMinus)

    if uiThiaWT5000.checkBox_SetWS.isChecked():
        checkBox_SetWS = '1'
    else:
        checkBox_SetWS = ''
    arrayRow2.append(checkBox_SetWS)

    if uiThiaWT5000.checkBox_SetWQ.isChecked():
        checkBox_SetWQ = '1'
    else:
        checkBox_SetWQ = ''
    arrayRow2.append(checkBox_SetWQ)

    # line10
    if uiThiaWT5000.checkBox_SetEta1.isChecked():
        checkBox_SetEta1 = '1'
    else:
        checkBox_SetEta1 = ''
    arrayRow2.append(checkBox_SetEta1)

    if uiThiaWT5000.checkBox_SetEta2.isChecked():
        checkBox_SetEta2 = '1'
    else:
        checkBox_SetEta2 = ''
    arrayRow2.append(checkBox_SetEta2)

    if uiThiaWT5000.checkBox_SetEta3.isChecked():
        checkBox_SetEta3 = '1'
    else:
        checkBox_SetEta3 = ''
    arrayRow2.append(checkBox_SetEta3)

    if uiThiaWT5000.checkBox_SetEta4.isChecked():
        checkBox_SetEta4 = '1'
    else:
        checkBox_SetEta4 = ''
    arrayRow2.append(checkBox_SetEta4)

    # line11
    if uiThiaWT5000.checkBox_SetEvent1.isChecked():
        checkBox_SetEvent1 = '1'
    else:
        checkBox_SetEvent1 = ''
    arrayRow2.append(checkBox_SetEvent1)

    if uiThiaWT5000.checkBox_SetEvent2.isChecked():
        checkBox_SetEvent2 = '1'
    else:
        checkBox_SetEvent2 = ''
    arrayRow2.append(checkBox_SetEvent2)

    if uiThiaWT5000.checkBox_SetEvent3.isChecked():
        checkBox_SetEvent3 = '1'
    else:
        checkBox_SetEvent3 = ''
    arrayRow2.append(checkBox_SetEvent3)

    if uiThiaWT5000.checkBox_SetEvent4.isChecked():
        checkBox_SetEvent4 = '1'
    else:
        checkBox_SetEvent4 = ''
    arrayRow2.append(checkBox_SetEvent4)

    if uiThiaWT5000.checkBox_SetEvent5.isChecked():
        checkBox_SetEvent5 = '1'
    else:
        checkBox_SetEvent5 = ''
    arrayRow2.append(checkBox_SetEvent5)

    if uiThiaWT5000.checkBox_SetEvent6.isChecked():
        checkBox_SetEvent6 = '1'
    else:
        checkBox_SetEvent6 = ''
    arrayRow2.append(checkBox_SetEvent6)

    if uiThiaWT5000.checkBox_SetEvent7.isChecked():
        checkBox_SetEvent7 = '1'
    else:
        checkBox_SetEvent7 = ''
    arrayRow2.append(checkBox_SetEvent7)

    if uiThiaWT5000.checkBox_SetEvent8.isChecked():
        checkBox_SetEvent8 = '1'
    else:
        checkBox_SetEvent8 = ''
    arrayRow2.append(checkBox_SetEvent8)
    
    # line12
    textEdit_SetStart = uiThiaWT5000.textEdit_SetStart.toPlainText()
    arrayRow2.append(textEdit_SetStart)

    textEdit_SetStop = uiThiaWT5000.textEdit_SetStop.toPlainText()
    arrayRow2.append(textEdit_SetStop)

    # line13
    if uiThiaWT5000.checkBox_SetUk.isChecked():
        checkBox_SetUk = '1'
    else:
        checkBox_SetUk = ''
    arrayRow2.append(checkBox_SetUk)

    if uiThiaWT5000.checkBox_SetIk.isChecked():
        checkBox_SetIk = '1'
    else:
        checkBox_SetIk = ''
    arrayRow2.append(checkBox_SetIk)

    if uiThiaWT5000.checkBox_SetPk.isChecked():
        checkBox_SetPk = '1'
    else:
        checkBox_SetPk = ''
    arrayRow2.append(checkBox_SetPk)

    if uiThiaWT5000.checkBox_SetSk.isChecked():
        checkBox_SetSk = '1'
    else:
        checkBox_SetSk = ''
    arrayRow2.append(checkBox_SetSk)

    if uiThiaWT5000.checkBox_SetQk.isChecked():
        checkBox_SetQk = '1'
    else:
        checkBox_SetQk = ''
    arrayRow2.append(checkBox_SetQk)

    if uiThiaWT5000.checkBox_SetPFk.isChecked():
        checkBox_SetPFk = '1'
    else:
        checkBox_SetPFk = ''
    arrayRow2.append(checkBox_SetPFk)

    if uiThiaWT5000.checkBox_SetFreqPLL1.isChecked():
        checkBox_SetFreqPLL1 = '1'
    else:
        checkBox_SetFreqPLL1 = ''
    arrayRow2.append(checkBox_SetFreqPLL1)

    if uiThiaWT5000.checkBox_SetFreqPLL2.isChecked():
        checkBox_SetFreqPLL2 = '1'
    else:
        checkBox_SetFreqPLL2 = ''
    arrayRow2.append(checkBox_SetFreqPLL2)

    # line14
    if uiThiaWT5000.checkBox_SetPhik.isChecked():
        checkBox_SetPhik = '1'
    else:
        checkBox_SetPhik = ''
    arrayRow2.append(checkBox_SetPhik)

    if uiThiaWT5000.checkBox_SetPhiUk.isChecked():
        checkBox_SetPhiUk = '1'
    else:
        checkBox_SetPhiUk = ''
    arrayRow2.append(checkBox_SetPhiUk)

    if uiThiaWT5000.checkBox_SetPhiIk.isChecked():
        checkBox_SetPhiIk = '1'
    else:
        checkBox_SetPhiIk = ''
    arrayRow2.append(checkBox_SetPhiIk)

    if uiThiaWT5000.checkBox_SetUhdfk.isChecked():
        checkBox_SetUhdfk = '1'
    else:
        checkBox_SetUhdfk = ''
    arrayRow2.append(checkBox_SetUhdfk)

    if uiThiaWT5000.checkBox_SetIhdfk.isChecked():
        checkBox_SetIhdfk = '1'
    else:
        checkBox_SetIhdfk = ''
    arrayRow2.append(checkBox_SetIhdfk)

    if uiThiaWT5000.checkBox_SetPhdfk.isChecked():
        checkBox_SetPhdfk = '1'
    else:
        checkBox_SetPhdfk = ''
    arrayRow2.append(checkBox_SetPhdfk)

    # line15
    if uiThiaWT5000.checkBox_SetZk.isChecked():
        checkBox_SetZk = '1'
    else:
        checkBox_SetZk = ''
    arrayRow2.append(checkBox_SetZk)

    if uiThiaWT5000.checkBox_SetRsk.isChecked():
        checkBox_SetRsk = '1'
    else:
        checkBox_SetRsk = ''
    arrayRow2.append(checkBox_SetRsk)

    if uiThiaWT5000.checkBox_SetXsk.isChecked():
        checkBox_SetXsk = '1'
    else:
        checkBox_SetXsk = ''
    arrayRow2.append(checkBox_SetXsk)

    if uiThiaWT5000.checkBox_SetRpk.isChecked():
        checkBox_SetRpk = '1'
    else:
        checkBox_SetRpk = ''
    arrayRow2.append(checkBox_SetRpk)

    if uiThiaWT5000.checkBox_SetXpk.isChecked():
        checkBox_SetXpk = '1'
    else:
        checkBox_SetXpk = ''
    arrayRow2.append(checkBox_SetXpk)

    # line16
    if uiThiaWT5000.checkBox_SetUthd.isChecked():
        checkBox_SetUthd = '1'
    else:
        checkBox_SetUthd = ''
    arrayRow2.append(checkBox_SetUthd)

    if uiThiaWT5000.checkBox_SetIthd.isChecked():
        checkBox_SetIthd = '1'
    else:
        checkBox_SetIthd = ''
    arrayRow2.append(checkBox_SetIthd)

    if uiThiaWT5000.checkBox_SetPthd.isChecked():
        checkBox_SetPthd = '1'
    else:
        checkBox_SetPthd = ''
    arrayRow2.append(checkBox_SetPthd)

    if uiThiaWT5000.checkBox_SetUthf.isChecked():
        checkBox_SetUthf = '1'
    else:
        checkBox_SetUthf = ''
    arrayRow2.append(checkBox_SetUthf)

    if uiThiaWT5000.checkBox_SetIthf.isChecked():
        checkBox_SetIthf = '1'
    else:
        checkBox_SetIthf = ''
    arrayRow2.append(checkBox_SetIthf)

    # line17
    if uiThiaWT5000.checkBox_SetUtif.isChecked():
        checkBox_SetUtif = '1'
    else:
        checkBox_SetUtif = ''
    arrayRow2.append(checkBox_SetUtif)

    if uiThiaWT5000.checkBox_SetItif.isChecked():
        checkBox_SetItif = '1'
    else:
        checkBox_SetItif = ''
    arrayRow2.append(checkBox_SetItif)

    if uiThiaWT5000.checkBox_Sethvf.isChecked():
        checkBox_Sethvf = '1'
    else:
        checkBox_Sethvf = ''
    arrayRow2.append(checkBox_Sethvf)

    if uiThiaWT5000.checkBox_Sethcf.isChecked():
        checkBox_Sethcf = '1'
    else:
        checkBox_Sethcf = ''
    arrayRow2.append(checkBox_Sethcf)

    if uiThiaWT5000.checkBox_SetK_factor.isChecked():
        checkBox_SetK_factor = '1'
    else:
        checkBox_SetK_factor = ''
    arrayRow2.append(checkBox_SetK_factor)

    # line18
    if uiThiaWT5000.checkBox_SetPhiUi_Uj.isChecked():
        checkBox_SetPhiUi_Uj = '1'
    else:
        checkBox_SetPhiUi_Uj = ''
    arrayRow2.append(checkBox_SetPhiUi_Uj)

    if uiThiaWT5000.checkBox_SetPhiUi_Uk.isChecked():
        checkBox_SetPhiUi_Uk = '1'
    else:
        checkBox_SetPhiUi_Uk = ''
    arrayRow2.append(checkBox_SetPhiUi_Uk)

    if uiThiaWT5000.checkBox_SetPhiUi_Ii.isChecked():
        checkBox_SetPhiUi_Ii = '1'
    else:
        checkBox_SetPhiUi_Ii = ''
    arrayRow2.append(checkBox_SetPhiUi_Ii)

    if uiThiaWT5000.checkBox_SetPhiUi_Ij.isChecked():
        checkBox_SetPhiUi_Ij = '1'
    else:
        checkBox_SetPhiUi_Ij = ''
    arrayRow2.append(checkBox_SetPhiUi_Ij)

    if uiThiaWT5000.checkBox_SetPhiUi_Ik.isChecked():
        checkBox_SetPhiUi_Ik = '1'
    else:
        checkBox_SetPhiUi_Ik = ''
    arrayRow2.append(checkBox_SetPhiUi_Ik)

    # line19
    if uiThiaWT5000.checkBox_SetDeltaU1.isChecked():
        checkBox_SetDeltaU1 = '1'
    else:
        checkBox_SetDeltaU1 = ''
    arrayRow2.append(checkBox_SetDeltaU1)

    if uiThiaWT5000.checkBox_SetDeltaU2.isChecked():
        checkBox_SetDeltaU2 = '1'
    else:
        checkBox_SetDeltaU2 = ''
    arrayRow2.append(checkBox_SetDeltaU2)

    if uiThiaWT5000.checkBox_SetDeltaU3.isChecked():
        checkBox_SetDeltaU3 = '1'
    else:
        checkBox_SetDeltaU3 = ''
    arrayRow2.append(checkBox_SetDeltaU3)

    if uiThiaWT5000.checkBox_SetDeltaUSigma.isChecked():
        checkBox_SetDeltaUSigma = '1'
    else:
        checkBox_SetDeltaUSigma = ''
    arrayRow2.append(checkBox_SetDeltaUSigma)

    if uiThiaWT5000.checkBox_SetDeltaI.isChecked():
        checkBox_SetDeltaI = '1'
    else:
        checkBox_SetDeltaI = ''
    arrayRow2.append(checkBox_SetDeltaI)

    if uiThiaWT5000.checkBox_SetDeltaP1.isChecked():
        checkBox_SetDeltaP1 = '1'
    else:
        checkBox_SetDeltaP1 = ''
    arrayRow2.append(checkBox_SetDeltaP1)

    if uiThiaWT5000.checkBox_SetDeltaP2.isChecked():
        checkBox_SetDeltaP2 = '1'
    else:
        checkBox_SetDeltaP2 = ''
    arrayRow2.append(checkBox_SetDeltaP2)

    if uiThiaWT5000.checkBox_SetDeltaP3.isChecked():
        checkBox_SetDeltaP3 = '1'
    else:
        checkBox_SetDeltaP3 = ''
    arrayRow2.append(checkBox_SetDeltaP3)

    if uiThiaWT5000.checkBox_SetDeltaPSigma.isChecked():
        checkBox_SetDeltaPSigma = '1'
    else:
        checkBox_SetDeltaPSigma = ''
    arrayRow2.append(checkBox_SetDeltaPSigma)

    # line20
    if uiThiaWT5000.checkBox_SetTSDate.isChecked():
        checkBox_SetTSDate = '1'
    else:
        checkBox_SetTSDate = ''
    arrayRow2.append(checkBox_SetTSDate)

    if uiThiaWT5000.checkBox_SetTSTime.isChecked():
        checkBox_SetTSTime = '1'
    else:
        checkBox_SetTSTime = ''
    arrayRow2.append(checkBox_SetTSTime)

    if uiThiaWT5000.checkBox_SetTSSubsec.isChecked():
        checkBox_SetTSSubsec = '1'
    else:
        checkBox_SetTSSubsec = ''
    arrayRow2.append(checkBox_SetTSSubsec)

    # line21
    if uiThiaWT5000.checkBox_SetF01.isChecked():
        checkBox_SetF01 = '1'
    else:
        checkBox_SetF01 = ''
    arrayRow2.append(checkBox_SetF01)

    if uiThiaWT5000.checkBox_SetF02.isChecked():
        checkBox_SetF02 = '1'
    else:
        checkBox_SetF02 = ''
    arrayRow2.append(checkBox_SetF02)

    if uiThiaWT5000.checkBox_SetF03.isChecked():
        checkBox_SetF03 = '1'
    else:
        checkBox_SetF03 = ''
    arrayRow2.append(checkBox_SetF03)

    if uiThiaWT5000.checkBox_SetF04.isChecked():
        checkBox_SetF04 = '1'
    else:
        checkBox_SetF04 = ''
    arrayRow2.append(checkBox_SetF04)

    if uiThiaWT5000.checkBox_SetF05.isChecked():
        checkBox_SetF05 = '1'
    else:
        checkBox_SetF05 = ''
    arrayRow2.append(checkBox_SetF05)

    if uiThiaWT5000.checkBox_SetF06.isChecked():
        checkBox_SetF06 = '1'
    else:
        checkBox_SetF06 = ''
    arrayRow2.append(checkBox_SetF06)

    if uiThiaWT5000.checkBox_SetF07.isChecked():
        checkBox_SetF07 = '1'
    else:
        checkBox_SetF07 = ''
    arrayRow2.append(checkBox_SetF07)

    if uiThiaWT5000.checkBox_SetF08.isChecked():
        checkBox_SetF08 = '1'
    else:
        checkBox_SetF08 = ''
    arrayRow2.append(checkBox_SetF08)

    if uiThiaWT5000.checkBox_SetF09.isChecked():
        checkBox_SetF09 = '1'
    else:
        checkBox_SetF09 = ''
    arrayRow2.append(checkBox_SetF09)

    if uiThiaWT5000.checkBox_SetF10.isChecked():
        checkBox_SetF10 = '1'
    else:
        checkBox_SetF10 = ''
    arrayRow2.append(checkBox_SetF10)

    if uiThiaWT5000.checkBox_SetF11.isChecked():
        checkBox_SetF11 = '1'
    else:
        checkBox_SetF11 = ''
    arrayRow2.append(checkBox_SetF11)

    if uiThiaWT5000.checkBox_SetF12.isChecked():
        checkBox_SetF12 = '1'
    else:
        checkBox_SetF12 = ''
    arrayRow2.append(checkBox_SetF12)

    if uiThiaWT5000.checkBox_SetF13.isChecked():
        checkBox_SetF13 = '1'
    else:
        checkBox_SetF13 = ''
    arrayRow2.append(checkBox_SetF13)

    if uiThiaWT5000.checkBox_SetF14.isChecked():
        checkBox_SetF14 = '1'
    else:
        checkBox_SetF14 = ''
    arrayRow2.append(checkBox_SetF14)

    if uiThiaWT5000.checkBox_SetF15.isChecked():
        checkBox_SetF15 = '1'
    else:
        checkBox_SetF15 = ''
    arrayRow2.append(checkBox_SetF15)

    if uiThiaWT5000.checkBox_SetF16.isChecked():
        checkBox_SetF16 = '1'
    else:
        checkBox_SetF16 = ''
    arrayRow2.append(checkBox_SetF16)

    if uiThiaWT5000.checkBox_SetF17.isChecked():
        checkBox_SetF17 = '1'
    else:
        checkBox_SetF17 = ''
    arrayRow2.append(checkBox_SetF17)

    if uiThiaWT5000.checkBox_SetF18.isChecked():
        checkBox_SetF18 = '1'
    else:
        checkBox_SetF18 = ''
    arrayRow2.append(checkBox_SetF18)

    if uiThiaWT5000.checkBox_SetF19.isChecked():
        checkBox_SetF19 = '1'
    else:
        checkBox_SetF19 = ''
    arrayRow2.append(checkBox_SetF19)

    if uiThiaWT5000.checkBox_SetF20.isChecked():
        checkBox_SetF20 = '1'
    else:
        checkBox_SetF20 = ''
    arrayRow2.append(checkBox_SetF20)

    result_list = [arrayRow1, arrayRow2]

    return result_list

# WT1806E配置读取设定
def Open_File_ThaiWT5000_Config(uiThiaWT5000, wt_config_dict):
    strFlag  = "0"

    if arrayRow1[0] in wt_config_dict:
        if wt_config_dict[arrayRow1[0]] == "Thai_WT5000_Config":

            if strFlag == "0":
                if arrayRow1[1] in wt_config_dict:
                    comboBox_SigmA1 = wt_config_dict[arrayRow1[1]]
                    uiThiaWT5000.comboBox_SigmA1.setCurrentIndex(int(comboBox_SigmA1))
                else:
                    strFlag = 1

            #comBox
            if strFlag == "0":
                if arrayRow1[2] in wt_config_dict:
                    comboBox_SigmA2 = wt_config_dict[arrayRow1[2]]
                    uiThiaWT5000.comboBox_SigmA2.setCurrentIndex(int(comboBox_SigmA2))
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[3] in wt_config_dict:
                    comboBox_SigmB1 = wt_config_dict[arrayRow1[3]]
                    uiThiaWT5000.comboBox_SigmB1.setCurrentIndex(int(comboBox_SigmB1))
                else:
                    strFlag = 1

            #comBox
            if strFlag == "0":
                if arrayRow1[4] in wt_config_dict:
                    comboBox_SigmB2 = wt_config_dict[arrayRow1[4]]
                    uiThiaWT5000.comboBox_SigmB2.setCurrentIndex(int(comboBox_SigmB2))
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[5] in wt_config_dict:
                    comboBox_ReplaceRate = wt_config_dict[arrayRow1[5]]
                    uiThiaWT5000.comboBox_ReplaceRate.setCurrentIndex(int(comboBox_ReplaceRate))
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[6] in wt_config_dict:
                    comboBox_ProjectNum = wt_config_dict[arrayRow1[6]]
                    uiThiaWT5000.comboBox_ProjectNum.setCurrentIndex(int(comboBox_ProjectNum))
                else:
                    strFlag = 1

            #comBox
            if strFlag == "0":
                if arrayRow1[7] in wt_config_dict:
                    comboBox_AutoSave = wt_config_dict[arrayRow1[7]]
                    uiThiaWT5000.comboBox_AutoSave.setCurrentIndex(int(comboBox_AutoSave))
                else:
                    strFlag = 1

            #textEdit
            if strFlag == "0":
                if arrayRow1[8] in wt_config_dict:
                    textEdit_StopTime = wt_config_dict[arrayRow1[8]]
                    uiThiaWT5000.textEdit_StopTime.setText(textEdit_StopTime)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[9] in wt_config_dict:
                    textEdit_SavePath = wt_config_dict[arrayRow1[9]]
                    uiThiaWT5000.textEdit_SavePath.setText(textEdit_SavePath)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[10] in wt_config_dict:
                    checkBox_AutoName = wt_config_dict[arrayRow1[10]]
                    if checkBox_AutoName == '1':
                        uiThiaWT5000.checkBox_AutoName.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_AutoName.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[11] in wt_config_dict:
                    textEdit_FileNameList = wt_config_dict[arrayRow1[11]]
                    uiThiaWT5000.textEdit_FileNameList.setText(textEdit_FileNameList)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[12] in wt_config_dict:
                    checkBox_SetElement1 = wt_config_dict[arrayRow1[12]]
                    if checkBox_SetElement1 == '1':
                        uiThiaWT5000.checkBox_SetElement1.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetElement1.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[13] in wt_config_dict:
                    checkBox_SetElement2 = wt_config_dict[arrayRow1[13]]
                    if checkBox_SetElement2 == '1':
                        uiThiaWT5000.checkBox_SetElement2.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetElement2.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[14] in wt_config_dict:
                    checkBox_SetElement3 = wt_config_dict[arrayRow1[14]]
                    if checkBox_SetElement3 == '1':
                        uiThiaWT5000.checkBox_SetElement3.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetElement3.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[15] in wt_config_dict:
                    checkBox_SetElement4 = wt_config_dict[arrayRow1[15]]
                    if checkBox_SetElement4 == '1':
                        uiThiaWT5000.checkBox_SetElement4.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetElement4.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[16] in wt_config_dict:
                    checkBox_SetSigma = wt_config_dict[arrayRow1[16]]
                    if checkBox_SetSigma == '1':
                        uiThiaWT5000.checkBox_SetSigma.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetSigma.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[17] in wt_config_dict:
                    checkBox_SetSigmaA = wt_config_dict[arrayRow1[17]]
                    if checkBox_SetSigmaA == '1':
                        uiThiaWT5000.checkBox_SetSigmaA.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetSigmaA.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[18] in wt_config_dict:
                    checkBox_SetSigmaB = wt_config_dict[arrayRow1[18]]
                    if checkBox_SetSigmaB == '1':
                        uiThiaWT5000.checkBox_SetSigmaB.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetSigmaB.setChecked(False)
                else:
                    strFlag = 1

            # line3
            if strFlag == "0":
                if arrayRow1[19] in wt_config_dict:
                    checkBox_SetUrms = wt_config_dict[arrayRow1[19]]
                    if checkBox_SetUrms == '1':
                        uiThiaWT5000.checkBox_SetUrms.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetUrms.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[20] in wt_config_dict:
                    checkBox_SetUmn = wt_config_dict[arrayRow1[20]]
                    if checkBox_SetUmn == '1':
                        uiThiaWT5000.checkBox_SetUmn.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetUmn.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[21] in wt_config_dict:
                    checkBox_SetUdc = wt_config_dict[arrayRow1[21]]
                    if checkBox_SetUdc == '1':
                        uiThiaWT5000.checkBox_SetUdc.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetUdc.setChecked(False)
                else:
                    strFlag = 1
            if strFlag == "0":
                if arrayRow1[22] in wt_config_dict:
                    checkBox_SetUrmn = wt_config_dict[arrayRow1[22]]
                    if checkBox_SetUrmn == '1':
                        uiThiaWT5000.checkBox_SetUrmn.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetUrmn.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[23] in wt_config_dict:
                    checkBox_SetUac = wt_config_dict[arrayRow1[23]]
                    if checkBox_SetUac == '1':
                        uiThiaWT5000.checkBox_SetUac.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetUac.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[24] in wt_config_dict:
                    checkBox_SetRngU = wt_config_dict[arrayRow1[24]]
                    if checkBox_SetRngU == '1':
                        uiThiaWT5000.checkBox_SetRngU.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetRngU.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[25] in wt_config_dict:
                    checkBox_SetCfU = wt_config_dict[arrayRow1[25]]
                    if checkBox_SetCfU == '1':
                        uiThiaWT5000.checkBox_SetCfU.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetCfU.setChecked(False)
                else:
                    strFlag = 1

            # line4
            if strFlag == "0":
                if arrayRow1[26] in wt_config_dict:
                    checkBox_SetIrms = wt_config_dict[arrayRow1[26]]
                    if checkBox_SetIrms == '1':
                        uiThiaWT5000.checkBox_SetIrms.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetIrms.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[27] in wt_config_dict:
                    checkBox_SetImn = wt_config_dict[arrayRow1[27]]
                    if checkBox_SetImn == '1':
                        uiThiaWT5000.checkBox_SetImn.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetImn.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[28] in wt_config_dict:
                    checkBox_SetIdc = wt_config_dict[arrayRow1[28]]
                    if checkBox_SetIdc == '1':
                        uiThiaWT5000.checkBox_SetIdc.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetIdc.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[29] in wt_config_dict:
                    checkBox_SetIrmn = wt_config_dict[arrayRow1[29]]
                    if checkBox_SetIrmn == '1':
                        uiThiaWT5000.checkBox_SetIrmn.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetIrmn.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[30] in wt_config_dict:
                    checkBox_SetIac = wt_config_dict[arrayRow1[30]]
                    if checkBox_SetIac == '1':
                        uiThiaWT5000.checkBox_SetIac.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetIac.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[31] in wt_config_dict:
                    checkBox_SetRngI = wt_config_dict[arrayRow1[31]]
                    if checkBox_SetRngI == '1':
                        uiThiaWT5000.checkBox_SetRngI.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetRngI.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[32] in wt_config_dict:
                    checkBox_SetCfI = wt_config_dict[arrayRow1[32]]
                    if checkBox_SetCfI == '1':
                        uiThiaWT5000.checkBox_SetCfI.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetCfI.setChecked(False)
                else:
                    strFlag = 1

            # line5
            if strFlag == "0":
                if arrayRow1[33] in wt_config_dict:
                    checkBox_SetUppeak = wt_config_dict[arrayRow1[33]]
                    if checkBox_SetUppeak == '1':
                        uiThiaWT5000.checkBox_SetUppeak.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetUppeak.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[34] in wt_config_dict:
                    checkBox_SetUmpeak = wt_config_dict[arrayRow1[34]]
                    if checkBox_SetUmpeak == '1':
                        uiThiaWT5000.checkBox_SetUmpeak.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetUmpeak.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[35] in wt_config_dict:
                    checkBox_SetIppeak = wt_config_dict[arrayRow1[35]]
                    if checkBox_SetIppeak == '1':
                        uiThiaWT5000.checkBox_SetIppeak.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetIppeak.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[36] in wt_config_dict:
                    checkBox_SetImpeak = wt_config_dict[arrayRow1[36]]
                    if checkBox_SetImpeak == '1':
                        uiThiaWT5000.checkBox_SetImpeak.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetImpeak.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[37] in wt_config_dict:
                    checkBox_SetPppeak = wt_config_dict[arrayRow1[37]]
                    if checkBox_SetPppeak == '1':
                        uiThiaWT5000.checkBox_SetPppeak.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPppeak.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[38] in wt_config_dict:
                    checkBox_SetPmpeak = wt_config_dict[arrayRow1[38]]
                    if checkBox_SetPmpeak == '1':
                        uiThiaWT5000.checkBox_SetPmpeak.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPmpeak.setChecked(False)
                else:
                    strFlag = 1

            # line6
            if strFlag == "0":
                if arrayRow1[39] in wt_config_dict:
                    checkBox_SetP = wt_config_dict[arrayRow1[39]]
                    if checkBox_SetP == '1':
                        uiThiaWT5000.checkBox_SetP.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetP.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[40] in wt_config_dict:
                    checkBox_SetS = wt_config_dict[arrayRow1[40]]
                    if checkBox_SetS == '1':
                        uiThiaWT5000.checkBox_SetS.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetS.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[41] in wt_config_dict:
                    checkBox_SetQ = wt_config_dict[arrayRow1[41]]
                    if checkBox_SetQ == '1':
                        uiThiaWT5000.checkBox_SetQ.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetQ.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[42] in wt_config_dict:
                    checkBox_SetPF = wt_config_dict[arrayRow1[42]]
                    if checkBox_SetPF == '1':
                        uiThiaWT5000.checkBox_SetPF.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPF.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[43] in wt_config_dict:
                    checkBox_SetPhi = wt_config_dict[arrayRow1[43]]
                    if checkBox_SetPhi == '1':
                        uiThiaWT5000.checkBox_SetPhi.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPhi.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[44] in wt_config_dict:
                    checkBox_SetPc = wt_config_dict[arrayRow1[44]]
                    if checkBox_SetPc == '1':
                        uiThiaWT5000.checkBox_SetPc.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPc.setChecked(False)
                else:
                    strFlag = 1

            # line7
            if strFlag == "0":
                if arrayRow1[45] in wt_config_dict:
                    checkBox_SetUfnd = wt_config_dict[arrayRow1[45]]
                    if checkBox_SetUfnd == '1':
                        uiThiaWT5000.checkBox_SetUfnd.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetUfnd.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[46] in wt_config_dict:
                    checkBox_SetIfnd = wt_config_dict[arrayRow1[46]]
                    if checkBox_SetIfnd == '1':
                        uiThiaWT5000.checkBox_SetIfnd.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetIfnd.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[47] in wt_config_dict:
                    checkBox_SetPfnd = wt_config_dict[arrayRow1[47]]
                    if checkBox_SetPfnd == '1':
                        uiThiaWT5000.checkBox_SetPfnd.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPfnd.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[48] in wt_config_dict:
                    checkBox_SetSfnd = wt_config_dict[arrayRow1[48]]
                    if checkBox_SetSfnd == '1':
                        uiThiaWT5000.checkBox_SetSfnd.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetSfnd.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[49] in wt_config_dict:
                    checkBox_SetQfnd = wt_config_dict[arrayRow1[49]]
                    if checkBox_SetQfnd == '1':
                        uiThiaWT5000.checkBox_SetQfnd.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetQfnd.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[50] in wt_config_dict:
                    checkBox_SetLambdafnd = wt_config_dict[arrayRow1[50]]
                    if checkBox_SetLambdafnd == '1':
                        uiThiaWT5000.checkBox_SetLambdafnd.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetLambdafnd.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[51] in wt_config_dict:
                    checkBox_SetPhifnd = wt_config_dict[arrayRow1[51]]
                    if checkBox_SetPhifnd == '1':
                        uiThiaWT5000.checkBox_SetPhifnd.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPhifnd.setChecked(False)
                else:
                    strFlag = 1
            # line7
            if strFlag == "0":
                if arrayRow1[52] in wt_config_dict:
                    checkBox_SetFreqU = wt_config_dict[arrayRow1[52]]
                    if checkBox_SetFreqU == '1':
                        uiThiaWT5000.checkBox_SetFreqU.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetFreqU.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[53] in wt_config_dict:
                    checkBox_SetFreqI = wt_config_dict[arrayRow1[53]]
                    if checkBox_SetFreqI == '1':
                        uiThiaWT5000.checkBox_SetFreqI.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetFreqI.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[54] in wt_config_dict:
                    checkBox_SetFreq2U = wt_config_dict[arrayRow1[54]]
                    if checkBox_SetFreq2U == '1':
                        uiThiaWT5000.checkBox_SetFreq2U.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetFreq2U.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[55] in wt_config_dict:
                    checkBox_SetFreq2I = wt_config_dict[arrayRow1[55]]
                    if checkBox_SetFreq2I == '1':
                        uiThiaWT5000.checkBox_SetFreq2I.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetFreq2I.setChecked(False)
                else:
                    strFlag = 1

            # line8
            if strFlag == "0":
                if arrayRow1[56] in wt_config_dict:
                    checkBox_SetTime = wt_config_dict[arrayRow1[56]]
                    if checkBox_SetTime == '1':
                        uiThiaWT5000.checkBox_SetTime.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetTime.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[57] in wt_config_dict:
                    checkBox_SetWP = wt_config_dict[arrayRow1[57]]
                    if checkBox_SetWP == '1':
                        uiThiaWT5000.checkBox_SetWP.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetWP.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[58] in wt_config_dict:
                    checkBox_SetWPPlus = wt_config_dict[arrayRow1[58]]
                    if checkBox_SetWPPlus == '1':
                        uiThiaWT5000.checkBox_SetWPPlus.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetWPPlus.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[59] in wt_config_dict:
                    checkBox_SetWPMinus = wt_config_dict[arrayRow1[59]]
                    if checkBox_SetWPMinus == '1':
                        uiThiaWT5000.checkBox_SetWPMinus.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetWPMinus.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[60] in wt_config_dict:
                    checkBox_Setq = wt_config_dict[arrayRow1[60]]
                    if checkBox_Setq == '1':
                        uiThiaWT5000.checkBox_Setq.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_Setq.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[61] in wt_config_dict:
                    checkBox_SetqPlus = wt_config_dict[arrayRow1[61]]
                    if checkBox_SetqPlus == '1':
                        uiThiaWT5000.checkBox_SetqPlus.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetqPlus.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[62] in wt_config_dict:
                    checkBox_SetqMinus = wt_config_dict[arrayRow1[62]]
                    if checkBox_SetqMinus == '1':
                        uiThiaWT5000.checkBox_SetqMinus.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetqMinus.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[63] in wt_config_dict:
                    checkBox_SetWS = wt_config_dict[arrayRow1[63]]
                    if checkBox_SetWS == '1':
                        uiThiaWT5000.checkBox_SetWS.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetWS.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[64] in wt_config_dict:
                    checkBox_SetWQ = wt_config_dict[arrayRow1[64]]
                    if checkBox_SetWQ == '1':
                        uiThiaWT5000.checkBox_SetWQ.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetWQ.setChecked(False)
                else:
                    strFlag = 1

            # line9   
            if strFlag == "0":
                if arrayRow1[65] in wt_config_dict:
                    checkBox_SetEta1 = wt_config_dict[arrayRow1[65]]
                    if checkBox_SetEta1 == '1':
                        uiThiaWT5000.checkBox_SetEta1.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetEta1.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[66] in wt_config_dict:
                    checkBox_SetEta2 = wt_config_dict[arrayRow1[66]]
                    if checkBox_SetEta2 == '1':
                        uiThiaWT5000.checkBox_SetEta2.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetEta2.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[67] in wt_config_dict:
                    checkBox_SetEta3 = wt_config_dict[arrayRow1[67]]
                    if checkBox_SetEta3 == '1':
                        uiThiaWT5000.checkBox_SetEta3.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetEta3.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[68] in wt_config_dict:
                    checkBox_SetEta4 = wt_config_dict[arrayRow1[68]]
                    if checkBox_SetEta4 == '1':
                        uiThiaWT5000.checkBox_SetEta4.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetEta4.setChecked(False)
                else:
                    strFlag = 1

            # line10
            if strFlag == "0":
                if arrayRow1[69] in wt_config_dict:
                    checkBox_SetEvent1 = wt_config_dict[arrayRow1[69]]
                    if checkBox_SetEvent1 == '1':
                        uiThiaWT5000.checkBox_SetEvent1.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetEvent1.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[70] in wt_config_dict:
                    checkBox_SetEvent2 = wt_config_dict[arrayRow1[70]]
                    if checkBox_SetEvent2 == '1':
                        uiThiaWT5000.checkBox_SetEvent2.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetEvent2.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[71] in wt_config_dict:
                    checkBox_SetEvent3 = wt_config_dict[arrayRow1[71]]
                    if checkBox_SetEvent3 == '1':
                        uiThiaWT5000.checkBox_SetEvent3.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetEvent3.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[72] in wt_config_dict:
                    checkBox_SetEvent4 = wt_config_dict[arrayRow1[72]]
                    if checkBox_SetEvent4 == '1':
                        uiThiaWT5000.checkBox_SetEvent4.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetEvent4.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[73] in wt_config_dict:
                    checkBox_SetEvent5 = wt_config_dict[arrayRow1[73]]
                    if checkBox_SetEvent5 == '1':
                        uiThiaWT5000.checkBox_SetEvent5.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetEvent5.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[74] in wt_config_dict:
                    checkBox_SetEvent6 = wt_config_dict[arrayRow1[74]]
                    if checkBox_SetEvent6 == '1':
                        uiThiaWT5000.checkBox_SetEvent6.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetEvent6.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[75] in wt_config_dict:
                    checkBox_SetEvent7 = wt_config_dict[arrayRow1[75]]
                    if checkBox_SetEvent7 == '1':
                        uiThiaWT5000.checkBox_SetEvent7.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetEvent7.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[76] in wt_config_dict:
                    checkBox_SetEvent8 = wt_config_dict[arrayRow1[76]]
                    if checkBox_SetEvent8 == '1':
                        uiThiaWT5000.checkBox_SetEvent8.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetEvent8.setChecked(False)
                else:
                    strFlag = 1

            # line11
            if strFlag == "0":
                if arrayRow1[77] in wt_config_dict:
                    textEdit_SetStart = wt_config_dict[arrayRow1[77]]
                    uiThiaWT5000.textEdit_SetStart.setText(textEdit_SetStart)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[78] in wt_config_dict:
                    textEdit_SetStop = wt_config_dict[arrayRow1[78]]
                    uiThiaWT5000.textEdit_SetStop.setText(textEdit_SetStop)
                else:
                    strFlag = 1

            # line12
            if strFlag == "0":
                if arrayRow1[79] in wt_config_dict:
                    checkBox_SetUk = wt_config_dict[arrayRow1[79]]
                    if checkBox_SetUk == '1':
                        uiThiaWT5000.checkBox_SetUk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetUk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[80] in wt_config_dict:
                    checkBox_SetIk = wt_config_dict[arrayRow1[80]]
                    if checkBox_SetIk == '1':
                        uiThiaWT5000.checkBox_SetIk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetIk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[81] in wt_config_dict:
                    checkBox_SetPk = wt_config_dict[arrayRow1[81]]
                    if checkBox_SetPk == '1':
                        uiThiaWT5000.checkBox_SetPk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[82] in wt_config_dict:
                    checkBox_SetSk = wt_config_dict[arrayRow1[82]]
                    if checkBox_SetSk == '1':
                        uiThiaWT5000.checkBox_SetSk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetSk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[83] in wt_config_dict:
                    checkBox_SetQk = wt_config_dict[arrayRow1[83]]
                    if checkBox_SetQk == '1':
                        uiThiaWT5000.checkBox_SetQk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetQk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[84] in wt_config_dict:
                    checkBox_SetPFk = wt_config_dict[arrayRow1[84]]
                    if checkBox_SetPFk == '1':
                        uiThiaWT5000.checkBox_SetPFk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPFk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[85] in wt_config_dict:
                    checkBox_SetFreqPLL1 = wt_config_dict[arrayRow1[85]]
                    if checkBox_SetFreqPLL1 == '1':
                        uiThiaWT5000.checkBox_SetFreqPLL1.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetFreqPLL1.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[86] in wt_config_dict:
                    checkBox_SetFreqPLL2 = wt_config_dict[arrayRow1[86]]
                    if checkBox_SetFreqPLL2 == '1':
                        uiThiaWT5000.checkBox_SetFreqPLL2.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetFreqPLL2.setChecked(False)
                else:
                    strFlag = 1

            # line13
            if strFlag == "0":
                if arrayRow1[87] in wt_config_dict:
                    checkBox_SetPhik = wt_config_dict[arrayRow1[87]]
                    if checkBox_SetPhik == '1':
                        uiThiaWT5000.checkBox_SetPhik.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPhik.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[88] in wt_config_dict:
                    checkBox_SetPhiUk = wt_config_dict[arrayRow1[88]]
                    if checkBox_SetPhiUk == '1':
                        uiThiaWT5000.checkBox_SetPhiUk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPhiUk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[89] in wt_config_dict:
                    checkBox_SetPhiIk = wt_config_dict[arrayRow1[89]]
                    if checkBox_SetPhiIk == '1':
                        uiThiaWT5000.checkBox_SetPhiIk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPhiIk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[90] in wt_config_dict:
                    checkBox_SetUhdfk = wt_config_dict[arrayRow1[90]]
                    if checkBox_SetUhdfk == '1':
                        uiThiaWT5000.checkBox_SetUhdfk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetUhdfk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[91] in wt_config_dict:
                    checkBox_SetIhdfk = wt_config_dict[arrayRow1[91]]
                    if checkBox_SetIhdfk == '1':
                        uiThiaWT5000.checkBox_SetIhdfk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetIhdfk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[92] in wt_config_dict:
                    checkBox_SetPhdfk = wt_config_dict[arrayRow1[92]]
                    if checkBox_SetPhdfk == '1':
                        uiThiaWT5000.checkBox_SetPhdfk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPhdfk.setChecked(False)
                else:
                    strFlag = 1

            # line14
            if strFlag == "0":
                if arrayRow1[93] in wt_config_dict:
                    checkBox_SetZk = wt_config_dict[arrayRow1[93]]
                    if checkBox_SetZk == '1':
                        uiThiaWT5000.checkBox_SetZk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetZk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[94] in wt_config_dict:
                    checkBox_SetRsk = wt_config_dict[arrayRow1[94]]
                    if checkBox_SetRsk == '1':
                        uiThiaWT5000.checkBox_SetRsk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetRsk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[95] in wt_config_dict:
                    checkBox_SetXsk = wt_config_dict[arrayRow1[95]]
                    if checkBox_SetXsk == '1':
                        uiThiaWT5000.checkBox_SetXsk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetXsk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[96] in wt_config_dict:
                    checkBox_SetRpk = wt_config_dict[arrayRow1[96]]
                    if checkBox_SetRpk == '1':
                        uiThiaWT5000.checkBox_SetRpk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetRpk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[97] in wt_config_dict:
                    checkBox_SetXpk = wt_config_dict[arrayRow1[98]]
                    if checkBox_SetXpk == '1':
                        uiThiaWT5000.checkBox_SetXpk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetXpk.setChecked(False)
                else:
                    strFlag = 1

            # line15
            if strFlag == "0":
                if arrayRow1[98] in wt_config_dict:
                    checkBox_SetUthd = wt_config_dict[arrayRow1[98]]
                    if checkBox_SetUthd == '1':
                        uiThiaWT5000.checkBox_SetUthd.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetUthd.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[99] in wt_config_dict:
                    checkBox_SetIthd = wt_config_dict[arrayRow1[99]]
                    if checkBox_SetIthd == '1':
                        uiThiaWT5000.checkBox_SetIthd.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetIthd.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[100] in wt_config_dict:
                    checkBox_SetPthd = wt_config_dict[arrayRow1[100]]
                    if checkBox_SetPthd == '1':
                        uiThiaWT5000.checkBox_SetPthd.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPthd.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[101] in wt_config_dict:
                    checkBox_SetUthf = wt_config_dict[arrayRow1[101]]
                    if checkBox_SetUthf == '1':
                        uiThiaWT5000.checkBox_SetUthf.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetUthf.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[102] in wt_config_dict:
                    checkBox_SetIthf = wt_config_dict[arrayRow1[102]]
                    if checkBox_SetIthf == '1':
                        uiThiaWT5000.checkBox_SetIthf.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetIthf.setChecked(False)
                else:
                    strFlag = 1

            # line16
            if strFlag == "0":
                if arrayRow1[103] in wt_config_dict:
                    checkBox_SetUtif = wt_config_dict[arrayRow1[103]]
                    if checkBox_SetUtif == '1':
                        uiThiaWT5000.checkBox_SetUtif.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetUtif.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[104] in wt_config_dict:
                    checkBox_SetItif = wt_config_dict[arrayRow1[104]]
                    if checkBox_SetItif == '1':
                        uiThiaWT5000.checkBox_SetItif.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetItif.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[105] in wt_config_dict:
                    checkBox_Sethvf = wt_config_dict[arrayRow1[105]]
                    if checkBox_Sethvf == '1':
                        uiThiaWT5000.checkBox_Sethvf.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_Sethvf.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[106] in wt_config_dict:
                    checkBox_Sethcf = wt_config_dict[arrayRow1[106]]
                    if checkBox_Sethcf == '1':
                        uiThiaWT5000.checkBox_Sethcf.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_Sethcf.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[107] in wt_config_dict:
                    checkBox_Sethcf = wt_config_dict[arrayRow1[107]]
                    if checkBox_Sethcf == '1':
                        uiThiaWT5000.checkBox_Sethcf.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_Sethcf.setChecked(False)
                else:
                    strFlag = 1

            # line17
            if strFlag == "0":
                if arrayRow1[108] in wt_config_dict:
                    checkBox_SetPhiUi_Uj = wt_config_dict[arrayRow1[108]]
                    if checkBox_SetPhiUi_Uj == '1':
                        uiThiaWT5000.checkBox_SetPhiUi_Uj.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPhiUi_Uj.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[109] in wt_config_dict:
                    checkBox_SetPhiUi_Uk = wt_config_dict[arrayRow1[109]]
                    if checkBox_SetPhiUi_Uk == '1':
                        uiThiaWT5000.checkBox_SetPhiUi_Uk.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPhiUi_Uk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[110] in wt_config_dict:
                    checkBox_SetPhiUi_Ii = wt_config_dict[arrayRow1[110]]
                    if checkBox_SetPhiUi_Ii == '1':
                        uiThiaWT5000.checkBox_SetPhiUi_Ii.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPhiUi_Ii.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[111] in wt_config_dict:
                    checkBox_SetPhiUi_Ij = wt_config_dict[arrayRow1[111]]
                    if checkBox_SetPhiUi_Ij == '1':
                        uiThiaWT5000.checkBox_SetPhiUi_Ij.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPhiUi_Ij.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[112] in wt_config_dict:
                    checkBox_SetPhiUi_Ik = wt_config_dict[arrayRow1[112]]
                    if checkBox_SetPhiUi_Ik == '1':
                        uiThiaWT5000.checkBox_SetPhiUi_Ik.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetPhiUi_Ik.setChecked(False)
                else:
                    strFlag = 1

            # line18
            if strFlag == "0":
                if arrayRow1[113] in wt_config_dict:
                    checkBox_SetDeltaU1 = wt_config_dict[arrayRow1[113]]
                    if checkBox_SetDeltaU1 == '1':
                        uiThiaWT5000.checkBox_SetDeltaU1.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetDeltaU1.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[114] in wt_config_dict:
                    checkBox_SetDeltaU2 = wt_config_dict[arrayRow1[114]]
                    if checkBox_SetDeltaU2 == '1':
                        uiThiaWT5000.checkBox_SetDeltaU2.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetDeltaU2.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[115] in wt_config_dict:
                    checkBox_SetDeltaU3 = wt_config_dict[arrayRow1[115]]
                    if checkBox_SetDeltaU3 == '1':
                        uiThiaWT5000.checkBox_SetDeltaU3.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetDeltaU3.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[116] in wt_config_dict:
                    checkBox_SetDeltaUSigma = wt_config_dict[arrayRow1[116]]
                    if checkBox_SetDeltaUSigma == '1':
                        uiThiaWT5000.checkBox_SetDeltaUSigma.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetDeltaUSigma.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[117] in wt_config_dict:
                    checkBox_SetDeltaI = wt_config_dict[arrayRow1[117]]
                    if checkBox_SetDeltaI == '1':
                        uiThiaWT5000.checkBox_SetDeltaI.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetDeltaI.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[118] in wt_config_dict:
                    checkBox_SetDeltaP1 = wt_config_dict[arrayRow1[118]]
                    if checkBox_SetDeltaP1 == '1':
                        uiThiaWT5000.checkBox_SetDeltaP1.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetDeltaP1.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[119] in wt_config_dict:
                    checkBox_SetDeltaP2 = wt_config_dict[arrayRow1[119]]
                    if checkBox_SetDeltaP2 == '1':
                        uiThiaWT5000.checkBox_SetDeltaP2.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetDeltaP2.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[120] in wt_config_dict:
                    checkBox_SetDeltaP3 = wt_config_dict[arrayRow1[120]]
                    if checkBox_SetDeltaP3 == '1':
                        uiThiaWT5000.checkBox_SetDeltaP3.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetDeltaP3.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[121] in wt_config_dict:
                    checkBox_SetDeltaPSigma = wt_config_dict[arrayRow1[121]]
                    if checkBox_SetDeltaPSigma == '1':
                        uiThiaWT5000.checkBox_SetDeltaPSigma.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetDeltaPSigma.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[122] in wt_config_dict:
                    checkBox_SetTSDate = wt_config_dict[arrayRow1[122]]
                    if checkBox_SetTSDate == '1':
                        uiThiaWT5000.checkBox_SetTSDate.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetTSDate.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[123] in wt_config_dict:
                    checkBox_SetTSTime = wt_config_dict[arrayRow1[123]]
                    if checkBox_SetTSTime == '1':
                        uiThiaWT5000.checkBox_SetTSTime.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetTSTime.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[124] in wt_config_dict:
                    checkBox_SetTSSubsec = wt_config_dict[arrayRow1[124]]
                    if checkBox_SetTSSubsec == '1':
                        uiThiaWT5000.checkBox_SetTSSubsec.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetTSSubsec.setChecked(False)
                else:
                    strFlag = 1

            # line20
            if strFlag == "0":
                if arrayRow1[125] in wt_config_dict:
                    checkBox_SetF01 = wt_config_dict[arrayRow1[125]]
                    if checkBox_SetF01 == '1':
                        uiThiaWT5000.checkBox_SetF01.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF01.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[126] in wt_config_dict:
                    checkBox_SetF02 = wt_config_dict[arrayRow1[126]]
                    if checkBox_SetF02 == '1':
                        uiThiaWT5000.checkBox_SetF02.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF02.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[127] in wt_config_dict:
                    checkBox_SetF03 = wt_config_dict[arrayRow1[127]]
                    if checkBox_SetF03 == '1':
                        uiThiaWT5000.checkBox_SetF03.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF03.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[128] in wt_config_dict:
                    checkBox_SetF04 = wt_config_dict[arrayRow1[128]]
                    if checkBox_SetF04 == '1':
                        uiThiaWT5000.checkBox_SetF04.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF04.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[129] in wt_config_dict:
                    checkBox_SetF05 = wt_config_dict[arrayRow1[129]]
                    if checkBox_SetF05 == '1':
                        uiThiaWT5000.checkBox_SetF05.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF05.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[130] in wt_config_dict:
                    checkBox_SetF06 = wt_config_dict[arrayRow1[130]]
                    if checkBox_SetF06 == '1':
                        uiThiaWT5000.checkBox_SetF06.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF06.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[131] in wt_config_dict:
                    checkBox_SetF07 = wt_config_dict[arrayRow1[131]]
                    if checkBox_SetF07 == '1':
                        uiThiaWT5000.checkBox_SetF07.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF07.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[132] in wt_config_dict:
                    checkBox_SetF08 = wt_config_dict[arrayRow1[132]]
                    if checkBox_SetF08 == '1':
                        uiThiaWT5000.checkBox_SetF08.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF08.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[133] in wt_config_dict:
                    checkBox_SetF09 = wt_config_dict[arrayRow1[133]]
                    if checkBox_SetF09 == '1':
                        uiThiaWT5000.checkBox_SetF09.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF09.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[134] in wt_config_dict:
                    checkBox_SetF10 = wt_config_dict[arrayRow1[134]]
                    if checkBox_SetF10 == '1':
                        uiThiaWT5000.checkBox_SetF10.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF10.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[135] in wt_config_dict:
                    checkBox_SetF11 = wt_config_dict[arrayRow1[135]]
                    if checkBox_SetF11 == '1':
                        uiThiaWT5000.checkBox_SetF11.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF11.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[136] in wt_config_dict:
                    checkBox_SetF12 = wt_config_dict[arrayRow1[136]]
                    if checkBox_SetF12 == '1':
                        uiThiaWT5000.checkBox_SetF12.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF12.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[137] in wt_config_dict:
                    checkBox_SetF13 = wt_config_dict[arrayRow1[137]]
                    if checkBox_SetF13 == '1':
                        uiThiaWT5000.checkBox_SetF13.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF13.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[138] in wt_config_dict:
                    checkBox_SetF14 = wt_config_dict[arrayRow1[138]]
                    if checkBox_SetF14 == '1':
                        uiThiaWT5000.checkBox_SetF14.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF14.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[139] in wt_config_dict:
                    checkBox_SetF15 = wt_config_dict[arrayRow1[139]]
                    if checkBox_SetF15 == '1':
                        uiThiaWT5000.checkBox_SetF15.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF15.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[140] in wt_config_dict:
                    checkBox_SetF16 = wt_config_dict[arrayRow1[140]]
                    if checkBox_SetF16 == '1':
                        uiThiaWT5000.checkBox_SetF16.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF16.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[141] in wt_config_dict:
                    checkBox_SetF17 = wt_config_dict[arrayRow1[141]]
                    if checkBox_SetF17 == '1':
                        uiThiaWT5000.checkBox_SetF17.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF17.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[142] in wt_config_dict:
                    checkBox_SetF18 = wt_config_dict[arrayRow1[142]]
                    if checkBox_SetF18 == '1':
                        uiThiaWT5000.checkBox_SetF18.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF18.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[143] in wt_config_dict:
                    checkBox_SetF19 = wt_config_dict[arrayRow1[143]]
                    if checkBox_SetF19 == '1':
                        uiThiaWT5000.checkBox_SetF19.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF19.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[144] in wt_config_dict:
                    checkBox_SetF20 = wt_config_dict[arrayRow1[144]]
                    if checkBox_SetF20 == '1':
                        uiThiaWT5000.checkBox_SetF20.setChecked(True)
                    else:
                        uiThiaWT5000.checkBox_SetF20.setChecked(False)
                else:
                    strFlag = 1
            
            return 1

        else:
            print("no")
            strFlag = "1"

def WT5000_params_config(uiThiaWT5000):
    params_dict = {}
    params_dict.update({"Style":"Thai_WT5000_Config"})

    comboBox_SigmA1 = uiThiaWT5000.comboBox_SigmA1.currentIndex()
    params_dict.update({"comboBox_SigmA1":comboBox_SigmA1})

    comboBox_SigmA2 = uiThiaWT5000.comboBox_SigmA2.currentIndex()
    params_dict.update({"comboBox_SigmA2":comboBox_SigmA2})

    comboBox_SigmB1 = uiThiaWT5000.comboBox_SigmB1.currentIndex()
    params_dict.update({"comboBox_SigmB1":comboBox_SigmB1})

    comboBox_SigmB2 = uiThiaWT5000.comboBox_SigmB2.currentIndex()
    params_dict.update({"comboBox_SigmB2":comboBox_SigmB2})

    comboBox_ReplaceRate = uiThiaWT5000.comboBox_ReplaceRate.currentIndex()
    params_dict.update({"comboBox_ReplaceRate":comboBox_ReplaceRate})

    comboBox_ProjectNum = uiThiaWT5000.comboBox_ProjectNum.currentIndex()
    if comboBox_ProjectNum == 4:
        comboBox_ProjectNum = 5
    params_dict.update({"comboBox_ProjectNum":comboBox_ProjectNum})

    comboBox_AutoSave = uiThiaWT5000.comboBox_AutoSave.currentIndex()
    params_dict.update({"comboBox_AutoSave":comboBox_AutoSave})

    textEdit_StopTime = uiThiaWT5000.textEdit_StopTime.toPlainText()
    params_dict.update({"textEdit_StopTime":textEdit_StopTime})
    
    textEdit_SavePath = uiThiaWT5000.textEdit_SavePath.toPlainText()
    params_dict.update({"textEdit_SavePath":textEdit_SavePath})

    if uiThiaWT5000.checkBox_AutoName.isChecked():
        checkBox_AutoName = '1'
    else:
        checkBox_AutoName = '0'
    params_dict.update({"checkBox_AutoName":checkBox_AutoName})

    textEdit_FileNameList = uiThiaWT5000.textEdit_FileNameList.toPlainText()
    params_dict.update({"textEdit_FileNameList":textEdit_FileNameList})

    if uiThiaWT5000.checkBox_SetElement1.isChecked():
        checkBox_SetElement1 = '1'
    else:
        checkBox_SetElement1 = ''
    params_dict.update({"checkBox_SetElement1":checkBox_SetElement1})

    if uiThiaWT5000.checkBox_SetElement2.isChecked():
        checkBox_SetElement2 = '1'
    else:
        checkBox_SetElement2 = ''
    params_dict.update({"checkBox_SetElement2":checkBox_SetElement2})

    if uiThiaWT5000.checkBox_SetElement3.isChecked():
        checkBox_SetElement3 = '1'
    else:
        checkBox_SetElement3 = ''
    params_dict.update({"checkBox_SetElement3":checkBox_SetElement3})

    if uiThiaWT5000.checkBox_SetElement4.isChecked():
        checkBox_SetElement4 = '1'
    else:
        checkBox_SetElement4 = ''
    params_dict.update({"checkBox_SetElement4":checkBox_SetElement4})

    # line2
    if uiThiaWT5000.checkBox_SetSigma.isChecked():
        checkBox_SetSigma = '1'
    else:
        checkBox_SetSigma = ''
    params_dict.update({"checkBox_SetSigma":checkBox_SetSigma})

    if uiThiaWT5000.checkBox_SetSigmaA.isChecked():
        checkBox_SetSigmaA = '1'
    else:
        checkBox_SetSigmaA = ''
    params_dict.update({"checkBox_SetSigmaA":checkBox_SetSigmaA})

    if uiThiaWT5000.checkBox_SetSigmaB.isChecked():
        checkBox_SetSigmaB = '1'
    else:
        checkBox_SetSigmaB = ''
    params_dict.update({"checkBox_SetSigmaB":checkBox_SetSigmaB})

    # line3
    if uiThiaWT5000.checkBox_SetUrms.isChecked():
        checkBox_SetUrms = '1'
    else:
        checkBox_SetUrms = ''
    params_dict.update({"checkBox_SetUrms":checkBox_SetUrms})

    if uiThiaWT5000.checkBox_SetUmn.isChecked():
        checkBox_SetUmn = '1'
    else:
        checkBox_SetUmn = ''
    params_dict.update({"checkBox_SetUmn":checkBox_SetUmn})

    if uiThiaWT5000.checkBox_SetUdc.isChecked():
        checkBox_SetUdc = '1'
    else:
        checkBox_SetUdc = ''
    params_dict.update({"checkBox_SetUdc":checkBox_SetUdc})

    if uiThiaWT5000.checkBox_SetUrmn.isChecked():
        checkBox_SetUrmn = '1'
    else:
        checkBox_SetUrmn = ''
    params_dict.update({"checkBox_SetUrmn":checkBox_SetUrmn})

    if uiThiaWT5000.checkBox_SetUac.isChecked():
        checkBox_SetUac = '1'
    else:
        checkBox_SetUac = ''
    params_dict.update({"checkBox_SetUac":checkBox_SetUac})

    if uiThiaWT5000.checkBox_SetRngU.isChecked():
        checkBox_SetRngU = '1'
    else:
        checkBox_SetRngU = ''
    params_dict.update({"checkBox_SetRngU":checkBox_SetRngU})

    if uiThiaWT5000.checkBox_SetCfU.isChecked():
        checkBox_SetCfU = '1'
    else:
        checkBox_SetCfU = ''
    params_dict.update({"checkBox_SetCfU":checkBox_SetCfU})

    # line4
    if uiThiaWT5000.checkBox_SetIrms.isChecked():
        checkBox_SetIrms = '1'
    else:
        checkBox_SetIrms = ''
    params_dict.update({"checkBox_SetIrms":checkBox_SetIrms})

    if uiThiaWT5000.checkBox_SetImn.isChecked():
        checkBox_SetImn = '1'
    else:
        checkBox_SetImn = ''
    params_dict.update({"checkBox_SetImn":checkBox_SetImn})

    if uiThiaWT5000.checkBox_SetIdc.isChecked():
        checkBox_SetIdc = '1'
    else:
        checkBox_SetIdc = ''
    params_dict.update({"checkBox_SetIdc":checkBox_SetIdc})

    if uiThiaWT5000.checkBox_SetIrmn.isChecked():
        checkBox_SetIrmn = '1'
    else:
        checkBox_SetIrmn = ''
    params_dict.update({"checkBox_SetIrmn":checkBox_SetIrmn})

    if uiThiaWT5000.checkBox_SetIac.isChecked():
        checkBox_SetIac = '1'
    else:
        checkBox_SetIac = ''
    params_dict.update({"checkBox_SetIac":checkBox_SetIac})

    if uiThiaWT5000.checkBox_SetRngI.isChecked():
        checkBox_SetRngI = '1'
    else:
        checkBox_SetRngI = ''
    params_dict.update({"checkBox_SetRngI":checkBox_SetRngI})

    if uiThiaWT5000.checkBox_SetCfI.isChecked():
        checkBox_SetCfI = '1'
    else:
        checkBox_SetCfI = ''
    params_dict.update({"checkBox_SetCfI":checkBox_SetCfI})

    # line5
    if uiThiaWT5000.checkBox_SetUppeak.isChecked():
        checkBox_SetUppeak = '1'
    else:
        checkBox_SetUppeak = ''
    params_dict.update({"checkBox_SetUppeak":checkBox_SetUppeak})

    if uiThiaWT5000.checkBox_SetUmpeak.isChecked():
        checkBox_SetUmpeak = '1'
    else:
        checkBox_SetUmpeak = ''
    params_dict.update({"checkBox_SetUmpeak":checkBox_SetUmpeak})

    if uiThiaWT5000.checkBox_SetIppeak.isChecked():
        checkBox_SetIppeak = '1'
    else:
        checkBox_SetIppeak = ''
    params_dict.update({"checkBox_SetIppeak":checkBox_SetIppeak})

    if uiThiaWT5000.checkBox_SetImpeak.isChecked():
        checkBox_SetImpeak = '1'
    else:
        checkBox_SetImpeak = ''
    params_dict.update({"checkBox_SetImpeak":checkBox_SetImpeak})

    if uiThiaWT5000.checkBox_SetPppeak.isChecked():
        checkBox_SetPppeak = '1'
    else:
        checkBox_SetPppeak = ''
    params_dict.update({"checkBox_SetPppeak":checkBox_SetPppeak})

    if uiThiaWT5000.checkBox_SetPmpeak.isChecked():
        checkBox_SetPmpeak = '1'
    else:
        checkBox_SetPmpeak = ''
    params_dict.update({"checkBox_SetPmpeak":checkBox_SetPmpeak})

    # line6
    if uiThiaWT5000.checkBox_SetP.isChecked():
        checkBox_SetP = '1'
    else:
        checkBox_SetP = ''
    params_dict.update({"checkBox_SetP":checkBox_SetP})

    if uiThiaWT5000.checkBox_SetS.isChecked():
        checkBox_SetS = '1'
    else:
        checkBox_SetS = ''
    params_dict.update({"checkBox_SetS":checkBox_SetS})

    if uiThiaWT5000.checkBox_SetQ.isChecked():
        checkBox_SetQ = '1'
    else:
        checkBox_SetQ = ''
    params_dict.update({"checkBox_SetQ":checkBox_SetQ})

    if uiThiaWT5000.checkBox_SetPF.isChecked():
        checkBox_SetPF = '1'
    else:
        checkBox_SetPF = ''
    params_dict.update({"checkBox_SetPF":checkBox_SetPF})

    if uiThiaWT5000.checkBox_SetPhi.isChecked():
        checkBox_SetPhi = '1'
    else:
        checkBox_SetPhi = ''
    params_dict.update({"checkBox_SetPhi":checkBox_SetPhi})

    if uiThiaWT5000.checkBox_SetPc.isChecked():
        checkBox_SetPc = '1'
    else:
        checkBox_SetPc = ''
    params_dict.update({"checkBox_SetPc":checkBox_SetPc})

    if uiThiaWT5000.checkBox_SetUfnd.isChecked():
        checkBox_SetUfnd = '1'
    else:
        checkBox_SetUfnd = ''
    params_dict.update({"checkBox_SetUfnd":checkBox_SetUfnd})

    if uiThiaWT5000.checkBox_SetIfnd.isChecked():
        checkBox_SetIfnd = '1'
    else:
        checkBox_SetIfnd = ''
    params_dict.update({"checkBox_SetIfnd":checkBox_SetIfnd})

    if uiThiaWT5000.checkBox_SetPfnd.isChecked():
        checkBox_SetPfnd = '1'
    else:
        checkBox_SetPfnd = ''
    params_dict.update({"checkBox_SetPfnd":checkBox_SetPfnd})

    if uiThiaWT5000.checkBox_SetSfnd.isChecked():
        checkBox_SetSfnd = '1'
    else:
        checkBox_SetSfnd = ''
    params_dict.update({"checkBox_SetSfnd":checkBox_SetSfnd})

    if uiThiaWT5000.checkBox_SetQfnd.isChecked():
        checkBox_SetQfnd = '1'
    else:
        checkBox_SetQfnd = ''
    params_dict.update({"checkBox_SetQfnd":checkBox_SetQfnd})

    if uiThiaWT5000.checkBox_SetLambdafnd.isChecked():
        checkBox_SetLambdafnd = '1'
    else:
        checkBox_SetLambdafnd = ''
    params_dict.update({"checkBox_SetLambdafnd":checkBox_SetLambdafnd})

    if uiThiaWT5000.checkBox_SetPhifnd.isChecked():
        checkBox_SetPhifnd = '1'
    else:
        checkBox_SetPhifnd = ''
    params_dict.update({"checkBox_SetPhifnd":checkBox_SetPhifnd})

    # line7
    if uiThiaWT5000.checkBox_SetFreqU.isChecked():
        checkBox_SetFreqU = '1'
    else:
        checkBox_SetFreqU = ''
    params_dict.update({"checkBox_SetFreqU":checkBox_SetFreqU})

    if uiThiaWT5000.checkBox_SetFreqI.isChecked():
        checkBox_SetFreqI = '1'
    else:
        checkBox_SetFreqI = ''
    params_dict.update({"checkBox_SetFreqI":checkBox_SetFreqI})

    if uiThiaWT5000.checkBox_SetFreq2U.isChecked():
        checkBox_SetFreq2U = '1'
    else:
        checkBox_SetFreq2U = ''
    params_dict.update({"checkBox_SetFreq2U":checkBox_SetFreq2U})

    if uiThiaWT5000.checkBox_SetFreq2I.isChecked():
        checkBox_SetFreq2I = '1'
    else:
        checkBox_SetFreq2I = ''
    params_dict.update({"checkBox_SetFreq2I":checkBox_SetFreq2I})

    # line8
    if uiThiaWT5000.checkBox_SetTime.isChecked():
        checkBox_SetTime = '1'
    else:
        checkBox_SetTime = ''
    params_dict.update({"checkBox_SetTime":checkBox_SetTime})

    if uiThiaWT5000.checkBox_SetWP.isChecked():
        checkBox_SetWP = '1'
    else:
        checkBox_SetWP = ''
    params_dict.update({"checkBox_SetWP":checkBox_SetWP})

    if uiThiaWT5000.checkBox_SetWPPlus.isChecked():
        checkBox_SetWPPlus = '1'
    else:
        checkBox_SetWPPlus = ''
    params_dict.update({"checkBox_SetWPPlus":checkBox_SetWPPlus})

    if uiThiaWT5000.checkBox_SetWPMinus.isChecked():
        checkBox_SetWPMinus = '1'
    else:
        checkBox_SetWPMinus = ''
    params_dict.update({"checkBox_SetWPMinus":checkBox_SetWPMinus})

    if uiThiaWT5000.checkBox_Setq.isChecked():
        checkBox_Setq = '1'
    else:
        checkBox_Setq = ''
    params_dict.update({"checkBox_Setq":checkBox_Setq})

    if uiThiaWT5000.checkBox_SetqPlus.isChecked():
        checkBox_SetqPlus = '1'
    else:
        checkBox_SetqPlus = ''
    params_dict.update({"checkBox_SetqPlus":checkBox_SetqPlus})

    if uiThiaWT5000.checkBox_SetqMinus.isChecked():
        checkBox_SetqMinus = '1'
    else:
        checkBox_SetqMinus = ''
    params_dict.update({"checkBox_SetqMinus":checkBox_SetqMinus})

    if uiThiaWT5000.checkBox_SetWS.isChecked():
        checkBox_SetWS = '1'
    else:
        checkBox_SetWS = ''
    params_dict.update({"checkBox_SetWS":checkBox_SetWS})

    if uiThiaWT5000.checkBox_SetWQ.isChecked():
        checkBox_SetWQ = '1'
    else:
        checkBox_SetWQ = ''
    params_dict.update({"checkBox_SetWQ":checkBox_SetWQ})

    # line9
    if uiThiaWT5000.checkBox_SetEta1.isChecked():
        checkBox_SetEta1 = '1'
    else:
        checkBox_SetEta1 = ''
    params_dict.update({"checkBox_SetEta1":checkBox_SetEta1})

    if uiThiaWT5000.checkBox_SetEta2.isChecked():
        checkBox_SetEta2 = '1'
    else:
        checkBox_SetEta2 = ''
    params_dict.update({"checkBox_SetEta2":checkBox_SetEta2})

    if uiThiaWT5000.checkBox_SetEta3.isChecked():
        checkBox_SetEta3 = '1'
    else:
        checkBox_SetEta3 = ''
    params_dict.update({"checkBox_SetEta3":checkBox_SetEta3})

    if uiThiaWT5000.checkBox_SetEta4.isChecked():
        checkBox_SetEta4 = '1'
    else:
        checkBox_SetEta4 = ''
    params_dict.update({"checkBox_SetEta4":checkBox_SetEta4})

    # line10
    if uiThiaWT5000.checkBox_SetEvent1.isChecked():
        checkBox_SetEvent1 = '1'
    else:
        checkBox_SetEvent1 = ''
    params_dict.update({"checkBox_SetEvent1":checkBox_SetEvent1})

    if uiThiaWT5000.checkBox_SetEvent2.isChecked():
        checkBox_SetEvent2 = '1'
    else:
        checkBox_SetEvent2 = ''
    params_dict.update({"checkBox_SetEvent2":checkBox_SetEvent2})

    if uiThiaWT5000.checkBox_SetEvent3.isChecked():
        checkBox_SetEvent3 = '1'
    else:
        checkBox_SetEvent3 = ''
    params_dict.update({"checkBox_SetEvent3":checkBox_SetEvent3})

    if uiThiaWT5000.checkBox_SetEvent4.isChecked():
        checkBox_SetEvent4 = '1'
    else:
        checkBox_SetEvent4 = ''
    params_dict.update({"checkBox_SetEvent4":checkBox_SetEvent4})

    if uiThiaWT5000.checkBox_SetEvent5.isChecked():
        checkBox_SetEvent5 = '1'
    else:
        checkBox_SetEvent5 = ''
    params_dict.update({"checkBox_SetEvent5":checkBox_SetEvent5})

    if uiThiaWT5000.checkBox_SetEvent6.isChecked():
        checkBox_SetEvent6 = '1'
    else:
        checkBox_SetEvent6 = ''
    params_dict.update({"checkBox_SetEvent6":checkBox_SetEvent6})

    if uiThiaWT5000.checkBox_SetEvent7.isChecked():
        checkBox_SetEvent7 = '1'
    else:
        checkBox_SetEvent7 = ''
    params_dict.update({"checkBox_SetEvent7":checkBox_SetEvent7})

    if uiThiaWT5000.checkBox_SetEvent8.isChecked():
        checkBox_SetEvent8 = '1'
    else:
        checkBox_SetEvent8 = ''
    params_dict.update({"checkBox_SetEvent8":checkBox_SetEvent8})
    
    # line11
    textEdit_SetStart = uiThiaWT5000.textEdit_SetStart.toPlainText()
    params_dict.update({"textEdit_SetStart":textEdit_SetStart})

    textEdit_SetStop = uiThiaWT5000.textEdit_SetStop.toPlainText()
    params_dict.update({"textEdit_SetStop":textEdit_SetStop})

    # line12
    if uiThiaWT5000.checkBox_SetUk.isChecked():
        checkBox_SetUk = '1'
    else:
        checkBox_SetUk = ''
    params_dict.update({"checkBox_SetUk":checkBox_SetUk})

    if uiThiaWT5000.checkBox_SetIk.isChecked():
        checkBox_SetIk = '1'
    else:
        checkBox_SetIk = ''
    params_dict.update({"checkBox_SetIk":checkBox_SetIk})

    if uiThiaWT5000.checkBox_SetPk.isChecked():
        checkBox_SetPk = '1'
    else:
        checkBox_SetPk = ''
    params_dict.update({"checkBox_SetPk":checkBox_SetPk})

    if uiThiaWT5000.checkBox_SetSk.isChecked():
        checkBox_SetSk = '1'
    else:
        checkBox_SetSk = ''
    params_dict.update({"checkBox_SetSk":checkBox_SetSk})

    if uiThiaWT5000.checkBox_SetQk.isChecked():
        checkBox_SetQk = '1'
    else:
        checkBox_SetQk = ''
    params_dict.update({"checkBox_SetQk":checkBox_SetQk})

    if uiThiaWT5000.checkBox_SetPFk.isChecked():
        checkBox_SetPFk = '1'
    else:
        checkBox_SetPFk = ''
    params_dict.update({"checkBox_SetPFk":checkBox_SetPFk})

    if uiThiaWT5000.checkBox_SetFreqPLL1.isChecked():
        checkBox_SetFreqPLL1 = '1'
    else:
        checkBox_SetFreqPLL1 = ''
    params_dict.update({"checkBox_SetFreqPLL1":checkBox_SetFreqPLL1})

    if uiThiaWT5000.checkBox_SetFreqPLL2.isChecked():
        checkBox_SetFreqPLL2 = '1'
    else:
        checkBox_SetFreqPLL2 = ''
    params_dict.update({"checkBox_SetFreqPLL2":checkBox_SetFreqPLL2})

    # line14
    if uiThiaWT5000.checkBox_SetPhik.isChecked():
        checkBox_SetPhik = '1'
    else:
        checkBox_SetPhik = ''
    params_dict.update({"checkBox_SetPhik":checkBox_SetPhik})

    if uiThiaWT5000.checkBox_SetPhiUk.isChecked():
        checkBox_SetPhiUk = '1'
    else:
        checkBox_SetPhiUk = ''
    params_dict.update({"checkBox_SetPhiUk":checkBox_SetPhiUk})

    if uiThiaWT5000.checkBox_SetPhiIk.isChecked():
        checkBox_SetPhiIk = '1'
    else:
        checkBox_SetPhiIk = ''
    params_dict.update({"checkBox_SetPhiIk":checkBox_SetPhiIk})

    if uiThiaWT5000.checkBox_SetUhdfk.isChecked():
        checkBox_SetUhdfk = '1'
    else:
        checkBox_SetUhdfk = ''
    params_dict.update({"checkBox_SetUhdfk":checkBox_SetUhdfk})

    if uiThiaWT5000.checkBox_SetIhdfk.isChecked():
        checkBox_SetIhdfk = '1'
    else:
        checkBox_SetIhdfk = ''
    params_dict.update({"checkBox_SetIhdfk":checkBox_SetIhdfk})

    if uiThiaWT5000.checkBox_SetPhdfk.isChecked():
        checkBox_SetPhdfk = '1'
    else:
        checkBox_SetPhdfk = ''
    params_dict.update({"checkBox_SetPhdfk":checkBox_SetPhdfk})

    # line14
    if uiThiaWT5000.checkBox_SetZk.isChecked():
        checkBox_SetZk = '1'
    else:
        checkBox_SetZk = ''
    params_dict.update({"checkBox_SetZk":checkBox_SetZk})

    if uiThiaWT5000.checkBox_SetRsk.isChecked():
        checkBox_SetRsk = '1'
    else:
        checkBox_SetRsk = ''
    params_dict.update({"checkBox_SetRsk":checkBox_SetRsk})

    if uiThiaWT5000.checkBox_SetXsk.isChecked():
        checkBox_SetXsk = '1'
    else:
        checkBox_SetXsk = ''
    params_dict.update({"checkBox_SetXsk":checkBox_SetXsk})

    if uiThiaWT5000.checkBox_SetRpk.isChecked():
        checkBox_SetRpk = '1'
    else:
        checkBox_SetRpk = ''
    params_dict.update({"checkBox_SetRpk":checkBox_SetRpk})

    if uiThiaWT5000.checkBox_SetXpk.isChecked():
        checkBox_SetXpk = '1'
    else:
        checkBox_SetXpk = ''
    params_dict.update({"checkBox_SetXpk":checkBox_SetXpk})

    # line15
    if uiThiaWT5000.checkBox_SetUthd.isChecked():
        checkBox_SetUthd = '1'
    else:
        checkBox_SetUthd = ''
    params_dict.update({"checkBox_SetUthd":checkBox_SetUthd})

    if uiThiaWT5000.checkBox_SetIthd.isChecked():
        checkBox_SetIthd = '1'
    else:
        checkBox_SetIthd = ''
    params_dict.update({"checkBox_SetIthd":checkBox_SetIthd})

    if uiThiaWT5000.checkBox_SetPthd.isChecked():
        checkBox_SetPthd = '1'
    else:
        checkBox_SetPthd = ''
    params_dict.update({"checkBox_SetPthd":checkBox_SetPthd})

    if uiThiaWT5000.checkBox_SetUthf.isChecked():
        checkBox_SetUthf = '1'
    else:
        checkBox_SetUthf = ''
    params_dict.update({"checkBox_SetUthf":checkBox_SetUthf})

    if uiThiaWT5000.checkBox_SetIthf.isChecked():
        checkBox_SetIthf = '1'
    else:
        checkBox_SetIthf = ''
    params_dict.update({"checkBox_SetIthf":checkBox_SetIthf})

    # line16
    if uiThiaWT5000.checkBox_SetUtif.isChecked():
        checkBox_SetUtif = '1'
    else:
        checkBox_SetUtif = ''
    params_dict.update({"checkBox_SetUtif":checkBox_SetUtif})

    if uiThiaWT5000.checkBox_SetItif.isChecked():
        checkBox_SetItif = '1'
    else:
        checkBox_SetItif = ''
    params_dict.update({"checkBox_SetItif":checkBox_SetItif})

    if uiThiaWT5000.checkBox_Sethvf.isChecked():
        checkBox_Sethvf = '1'
    else:
        checkBox_Sethvf = ''
    params_dict.update({"checkBox_Sethvf":checkBox_Sethvf})

    if uiThiaWT5000.checkBox_Sethcf.isChecked():
        checkBox_Sethcf = '1'
    else:
        checkBox_Sethcf = ''
    params_dict.update({"checkBox_Sethcf":checkBox_Sethcf})

    if uiThiaWT5000.checkBox_SetK_factor.isChecked():
        checkBox_SetK_factor = '1'
    else:
        checkBox_SetK_factor = ''
    params_dict.update({"checkBox_SetK_factor":checkBox_SetK_factor})

    # line17
    if uiThiaWT5000.checkBox_SetPhiUi_Uj.isChecked():
        checkBox_SetPhiUi_Uj = '1'
    else:
        checkBox_SetPhiUi_Uj = ''
    params_dict.update({"checkBox_SetPhiUi_Uj":checkBox_SetPhiUi_Uj})

    if uiThiaWT5000.checkBox_SetPhiUi_Uk.isChecked():
        checkBox_SetPhiUi_Uk = '1'
    else:
        checkBox_SetPhiUi_Uk = ''
    params_dict.update({"checkBox_SetPhiUi_Uk":checkBox_SetPhiUi_Uk})

    if uiThiaWT5000.checkBox_SetPhiUi_Ii.isChecked():
        checkBox_SetPhiUi_Ii = '1'
    else:
        checkBox_SetPhiUi_Ii = ''
    params_dict.update({"checkBox_SetPhiUi_Ii":checkBox_SetPhiUi_Ii})

    if uiThiaWT5000.checkBox_SetPhiUi_Ij.isChecked():
        checkBox_SetPhiUi_Ij = '1'
    else:
        checkBox_SetPhiUi_Ij = ''
    params_dict.update({"checkBox_SetPhiUi_Ij":checkBox_SetPhiUi_Ij})

    if uiThiaWT5000.checkBox_SetPhiUi_Ik.isChecked():
        checkBox_SetPhiUi_Ik = '1'
    else:
        checkBox_SetPhiUi_Ik = ''
    params_dict.update({"checkBox_SetPhiUi_Ik":checkBox_SetPhiUi_Ik})

    # line18
    if uiThiaWT5000.checkBox_SetDeltaU1.isChecked():
        checkBox_SetDeltaU1 = '1'
    else:
        checkBox_SetDeltaU1 = ''
    params_dict.update({"checkBox_SetDeltaU1":checkBox_SetDeltaU1})

    if uiThiaWT5000.checkBox_SetDeltaU2.isChecked():
        checkBox_SetDeltaU2 = '1'
    else:
        checkBox_SetDeltaU2 = ''
    params_dict.update({"checkBox_SetDeltaU2":checkBox_SetDeltaU2})

    if uiThiaWT5000.checkBox_SetDeltaU3.isChecked():
        checkBox_SetDeltaU3 = '1'
    else:
        checkBox_SetDeltaU3 = ''
    params_dict.update({"checkBox_SetDeltaU3":checkBox_SetDeltaU3})

    if uiThiaWT5000.checkBox_SetDeltaUSigma.isChecked():
        checkBox_SetDeltaUSigma = '1'
    else:
        checkBox_SetDeltaUSigma = ''
    params_dict.update({"checkBox_SetDeltaUSigma":checkBox_SetDeltaUSigma})

    if uiThiaWT5000.checkBox_SetDeltaI.isChecked():
        checkBox_SetDeltaI = '1'
    else:
        checkBox_SetDeltaI = ''
    params_dict.update({"checkBox_SetDeltaI":checkBox_SetDeltaI})

    if uiThiaWT5000.checkBox_SetDeltaP1.isChecked():
        checkBox_SetDeltaP1 = '1'
    else:
        checkBox_SetDeltaP1 = ''
    params_dict.update({"checkBox_SetDeltaP1":checkBox_SetDeltaP1})

    if uiThiaWT5000.checkBox_SetDeltaP2.isChecked():
        checkBox_SetDeltaP2 = '1'
    else:
        checkBox_SetDeltaP2 = ''
    params_dict.update({"checkBox_SetDeltaP2":checkBox_SetDeltaP2})

    if uiThiaWT5000.checkBox_SetDeltaP3.isChecked():
        checkBox_SetDeltaP3 = '1'
    else:
        checkBox_SetDeltaP3 = ''
    params_dict.update({"checkBox_SetDeltaP3":checkBox_SetDeltaP3})

    if uiThiaWT5000.checkBox_SetDeltaPSigma.isChecked():
        checkBox_SetDeltaPSigma = '1'
    else:
        checkBox_SetDeltaPSigma = ''
    params_dict.update({"checkBox_SetDeltaPSigma":checkBox_SetDeltaPSigma})

    if uiThiaWT5000.checkBox_SetTSDate.isChecked():
        checkBox_SetTSDate = '1'
    else:
        checkBox_SetTSDate = ''
    params_dict.update({"checkBox_SetTSDate":checkBox_SetTSDate})

    if uiThiaWT5000.checkBox_SetTSTime.isChecked():
        checkBox_SetTSTime = '1'
    else:
        checkBox_SetTSTime = ''
    params_dict.update({"checkBox_SetTSTime":checkBox_SetTSTime})

    if uiThiaWT5000.checkBox_SetTSSubsec.isChecked():
        checkBox_SetTSSubsec = '1'
    else:
        checkBox_SetTSSubsec = ''
    params_dict.update({"checkBox_SetTSSubsec":checkBox_SetTSSubsec})

    # line19
    if uiThiaWT5000.checkBox_SetF01.isChecked():
        checkBox_SetF01 = '1'
    else:
        checkBox_SetF01 = ''
    params_dict.update({"checkBox_SetF01":checkBox_SetF01})

    if uiThiaWT5000.checkBox_SetF02.isChecked():
        checkBox_SetF02 = '1'
    else:
        checkBox_SetF02 = ''
    params_dict.update({"checkBox_SetF02":checkBox_SetF02})

    if uiThiaWT5000.checkBox_SetF03.isChecked():
        checkBox_SetF03 = '1'
    else:
        checkBox_SetF03 = ''
    params_dict.update({"checkBox_SetF03":checkBox_SetF03})

    if uiThiaWT5000.checkBox_SetF04.isChecked():
        checkBox_SetF04 = '1'
    else:
        checkBox_SetF04 = ''
    params_dict.update({"checkBox_SetF04":checkBox_SetF04})

    if uiThiaWT5000.checkBox_SetF05.isChecked():
        checkBox_SetF05 = '1'
    else:
        checkBox_SetF05 = ''
    params_dict.update({"checkBox_SetF05":checkBox_SetF05})

    if uiThiaWT5000.checkBox_SetF06.isChecked():
        checkBox_SetF06 = '1'
    else:
        checkBox_SetF06 = ''
    params_dict.update({"checkBox_SetF06":checkBox_SetF06})

    if uiThiaWT5000.checkBox_SetF07.isChecked():
        checkBox_SetF07 = '1'
    else:
        checkBox_SetF07 = ''
    params_dict.update({"checkBox_SetF07":checkBox_SetF07})

    if uiThiaWT5000.checkBox_SetF08.isChecked():
        checkBox_SetF08 = '1'
    else:
        checkBox_SetF08 = ''
    params_dict.update({"checkBox_SetF08":checkBox_SetF08})

    if uiThiaWT5000.checkBox_SetF09.isChecked():
        checkBox_SetF09 = '1'
    else:
        checkBox_SetF09 = ''
    params_dict.update({"checkBox_SetF09":checkBox_SetF09})

    if uiThiaWT5000.checkBox_SetF10.isChecked():
        checkBox_SetF10 = '1'
    else:
        checkBox_SetF10 = ''
    params_dict.update({"checkBox_SetF10":checkBox_SetF10})

    if uiThiaWT5000.checkBox_SetF11.isChecked():
        checkBox_SetF11 = '1'
    else:
        checkBox_SetF11 = ''
    params_dict.update({"checkBox_SetF11":checkBox_SetF11})

    if uiThiaWT5000.checkBox_SetF12.isChecked():
        checkBox_SetF12 = '1'
    else:
        checkBox_SetF12 = ''
    params_dict.update({"checkBox_SetF12":checkBox_SetF12})

    if uiThiaWT5000.checkBox_SetF13.isChecked():
        checkBox_SetF13 = '1'
    else:
        checkBox_SetF13 = ''
    params_dict.update({"checkBox_SetF13":checkBox_SetF13})

    if uiThiaWT5000.checkBox_SetF14.isChecked():
        checkBox_SetF14 = '1'
    else:
        checkBox_SetF14 = ''
    params_dict.update({"checkBox_SetF14":checkBox_SetF14})

    if uiThiaWT5000.checkBox_SetF15.isChecked():
        checkBox_SetF15 = '1'
    else:
        checkBox_SetF15 = ''
    params_dict.update({"checkBox_SetF15":checkBox_SetF15})

    if uiThiaWT5000.checkBox_SetF16.isChecked():
        checkBox_SetF16 = '1'
    else:
        checkBox_SetF16 = ''
    params_dict.update({"checkBox_SetF16":checkBox_SetF16})

    if uiThiaWT5000.checkBox_SetF17.isChecked():
        checkBox_SetF17 = '1'
    else:
        checkBox_SetF17 = ''
    params_dict.update({"checkBox_SetF17":checkBox_SetF17})

    if uiThiaWT5000.checkBox_SetF18.isChecked():
        checkBox_SetF18 = '1'
    else:
        checkBox_SetF18 = ''
    params_dict.update({"checkBox_SetF18":checkBox_SetF18})

    if uiThiaWT5000.checkBox_SetF19.isChecked():
        checkBox_SetF19 = '1'
    else:
        checkBox_SetF19 = ''
    params_dict.update({"checkBox_SetF19":checkBox_SetF19})

    if uiThiaWT5000.checkBox_SetF20.isChecked():
        checkBox_SetF20 = '1'
    else:
        checkBox_SetF20 = ''
    params_dict.update({"checkBox_SetF20":checkBox_SetF20})

    return params_dict


if __name__ == "__main__":
    print(len(arrayRow1))