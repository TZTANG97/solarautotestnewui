import re
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, \
    QFileDialog, QMessageBox
import csv

arrayRow1 = ['Style',
    'comboBox_SigmA1',
        'comboBox_SigmA2',"comboBox_SigmB1", "comboBox_SigmB2", "comboBox_UnitSet",
        "comboBox_WiringCom","comboBox_ReplaceRate", "comboBox_ProjectNum",
    "comboBox_AutoSave",
        "textEdit_StopTime", "textEdit_SavePath", "checkBox_AutoName",
    "textEdit_FileNameList",
    "checkBox_SetElement1", "checkBox_SetElement2", "checkBox_SetElement3", "checkBox_SetElement4",
    "checkBox_SetSigma", "checkBox_SetSigmaA", "checkBox_SetSigmaB",
    "checkBox_SetU", "checkBox_SetUrange", "checkBox_SetCfU",
    "checkBox_SetI", "checkBox_SetIrange", "checkBox_SetCfI",
    "checkBox_SetUppeak", "checkBox_SetUmpeak", "checkBox_SetIppeak", "checkBox_SetImpeak",
    "checkBox_SetP", "checkBox_SetS", "checkBox_SetQ", "checkBox_SetLambda",
        "checkBox_SetPhi","checkBox_SetPc",
    "checkBox_SetFreqU", "checkBox_SetFreqI", 
    "checkBox_SetTime", "checkBox_SetWP", "checkBox_SetWPPlus", "checkBox_SetWPMinus",
        "checkBox_Setq", "checkBox_SetqPlus", "checkBox_SetqMinus", "checkBox_SetWS", "checkBox_SetWQ",
    "checkBox_SetEta1", "checkBox_SetEta2", "checkBox_SetEta3", "checkBox_SetEta4",
    "textEdit_SetStart", "textEdit_SetStop",
    "checkBox_SetUk", "checkBox_SetIk", "checkBox_SetPk", "checkBox_SetSk", "checkBox_SetQk", "checkBox_SetPFk",
    "checkBox_SetPhik", "checkBox_SetPhiUk", "checkBox_SetPhiIk",
        "checkBox_SetUhdfk", "checkBox_SetIhdfk", "checkBox_SetPhdfk",
    'checkBox_SetZk', "checkBox_SetRsk", "checkBox_SetXsk", "checkBox_SetRpk", "checkBox_SetXpk",
    "checkBox_SetUthd", "checkBox_SetIthd", "checkBox_SetPthd", 'checkBox_SetUthf', 'checkBox_SetIthf',
    'checkBox_SetUtif', 'checkBox_SetItif', 'checkBox_Sethvf', 'checkBox_Sethcf',
    'checkBox_SetPhiUi_Uj', 'checkBox_SetPhiUi_Uk', 'checkBox_SetPhiUi_Ii', "checkBox_SetPhiUi_Ij",
        "checkBox_SetPhiUi_Ik",
    'checkBox_SetSpeed', 'checkBox_SetTorque', 'checkBox_SetSyncSp', "checkBox_SetSlip", "checkBox_SetPm",
    'checkBox_SetDeltaF1', 'checkBox_SetDeltaF2', 'checkBox_SetDeltaF3', "checkBox_SetDeltaF4",
    'checkBox_SetF01', 'checkBox_SetF02', 'checkBox_SetF03', 'checkBox_SetF04', 'checkBox_SetF05',
    'checkBox_SetF06', 'checkBox_SetF07', 'checkBox_SetF08', 'checkBox_SetF09', 'checkBox_SetF10',
    'checkBox_SetF11', 'checkBox_SetF12', 'checkBox_SetF13', 'checkBox_SetF14', 'checkBox_SetF15',
    'checkBox_SetF16', 'checkBox_SetF17', 'checkBox_SetF18', 'checkBox_SetF19', 'checkBox_SetF20',
]

# WT3000E配置保存设定
def Save_File_ThaiWT3000_Config(uiThiaWT3000E):
    print(f"[DEBUG-WT3000-SAVE] Save_File_ThaiWT3000_Config 被调用")
    print(f"[DEBUG-WT3000-SAVE] 参数类型: {type(uiThiaWT3000E)}")

    arrayRow2 = ['Thai_WT3000E_Config']

    comboBox_SigmA1 = uiThiaWT3000E.comboBox_SigmA1.currentIndex()
    print(f"[DEBUG-WT3000-SAVE] comboBox_SigmA1 currentIndex={comboBox_SigmA1}, objectName={uiThiaWT3000E.comboBox_SigmA1.objectName()}")
    arrayRow2.append(comboBox_SigmA1)

    comboBox_SigmA2 = uiThiaWT3000E.comboBox_SigmA2.currentIndex()
    print(f"[DEBUG-WT3000-SAVE] comboBox_SigmA2 currentIndex={comboBox_SigmA2}")
    arrayRow2.append(comboBox_SigmA2)

    comboBox_SigmB1 = uiThiaWT3000E.comboBox_SigmB1.currentIndex()
    print(f"[DEBUG-WT3000-SAVE] comboBox_SigmB1 currentIndex={comboBox_SigmB1}")
    arrayRow2.append(comboBox_SigmB1)

    comboBox_SigmB2 = uiThiaWT3000E.comboBox_SigmB2.currentIndex()
    print(f"[DEBUG-WT3000-SAVE] comboBox_SigmB2 currentIndex={comboBox_SigmB2}")
    arrayRow2.append(comboBox_SigmB2)

    comboBox_UnitSet = uiThiaWT3000E.comboBox_UnitSet.currentIndex()
    arrayRow2.append(comboBox_UnitSet)

    comboBox_WiringCom = uiThiaWT3000E.comboBox_WiringCom.currentIndex()
    arrayRow2.append(comboBox_WiringCom)

    comboBox_ReplaceRate = uiThiaWT3000E.comboBox_ReplaceRate.currentIndex()
    arrayRow2.append(comboBox_ReplaceRate)

    comboBox_ProjectNum = uiThiaWT3000E.comboBox_ProjectNum.currentIndex()
    arrayRow2.append(comboBox_ProjectNum)

    comboBox_AutoSave = uiThiaWT3000E.comboBox_AutoSave.currentIndex()
    arrayRow2.append(comboBox_AutoSave)

    textEdit_StopTime = uiThiaWT3000E.textEdit_StopTime.toPlainText()
    arrayRow2.append(textEdit_StopTime)
    
    textEdit_SavePath = uiThiaWT3000E.textEdit_SavePath.toPlainText()
    arrayRow2.append(textEdit_SavePath)

    if uiThiaWT3000E.checkBox_AutoName.isChecked():
        checkBox_AutoName = '1'
    else:
        checkBox_AutoName = '0'
    arrayRow2.append(checkBox_AutoName)

    textEdit_FileNameList = uiThiaWT3000E.textEdit_FileNameList.toPlainText()
    arrayRow2.append(textEdit_FileNameList)

    if uiThiaWT3000E.checkBox_SetElement1.isChecked():
        checkBox_SetElement1 = '1'
    else:
        checkBox_SetElement1 = ''
    arrayRow2.append(checkBox_SetElement1)

    if uiThiaWT3000E.checkBox_SetElement2.isChecked():
        checkBox_SetElement2 = '1'
    else:
        checkBox_SetElement2 = ''
    arrayRow2.append(checkBox_SetElement2)

    if uiThiaWT3000E.checkBox_SetElement3.isChecked():
        checkBox_SetElement3 = '1'
    else:
        checkBox_SetElement3 = ''
    arrayRow2.append(checkBox_SetElement3)

    if uiThiaWT3000E.checkBox_SetElement4.isChecked():
        checkBox_SetElement4 = '1'
    else:
        checkBox_SetElement4 = ''
    arrayRow2.append(checkBox_SetElement4)

    # line2
    if uiThiaWT3000E.checkBox_SetSigma.isChecked():
        checkBox_SetSigma = '1'
    else:
        checkBox_SetSigma = ''
    arrayRow2.append(checkBox_SetSigma)

    if uiThiaWT3000E.checkBox_SetSigmaA.isChecked():
        checkBox_SetSigmaA = '1'
    else:
        checkBox_SetSigmaA = ''
    arrayRow2.append(checkBox_SetSigmaA)

    if uiThiaWT3000E.checkBox_SetSigmaB.isChecked():
        checkBox_SetSigmaB = '1'
    else:
        checkBox_SetSigmaB = ''
    arrayRow2.append(checkBox_SetSigmaB)

    # line3
    if uiThiaWT3000E.checkBox_SetU.isChecked():
        checkBox_SetU = '1'
    else:
        checkBox_SetU = ''
    arrayRow2.append(checkBox_SetU)

    if uiThiaWT3000E.checkBox_SetUrange.isChecked():
        checkBox_SetUrange = '1'
    else:
        checkBox_SetUrange = ''
    arrayRow2.append(checkBox_SetUrange)

    if uiThiaWT3000E.checkBox_SetCfU.isChecked():
        checkBox_SetCfU = '1'
    else:
        checkBox_SetCfU = ''
    arrayRow2.append(checkBox_SetCfU)

    # line4
    if uiThiaWT3000E.checkBox_SetI.isChecked():
        checkBox_SetI = '1'
    else:
        checkBox_SetI = ''
    arrayRow2.append(checkBox_SetI)

    if uiThiaWT3000E.checkBox_SetIrange.isChecked():
        checkBox_SetIrange = '1'
    else:
        checkBox_SetIrange = ''
    arrayRow2.append(checkBox_SetIrange)

    if uiThiaWT3000E.checkBox_SetCfI.isChecked():
        checkBox_SetCfI = '1'
    else:
        checkBox_SetCfI = ''
    arrayRow2.append(checkBox_SetCfI)

    # line5
    if uiThiaWT3000E.checkBox_SetUppeak.isChecked():
        checkBox_SetUppeak = '1'
    else:
        checkBox_SetUppeak = ''
    arrayRow2.append(checkBox_SetUppeak)

    if uiThiaWT3000E.checkBox_SetUmpeak.isChecked():
        checkBox_SetUmpeak = '1'
    else:
        checkBox_SetUmpeak = ''
    arrayRow2.append(checkBox_SetUmpeak)

    if uiThiaWT3000E.checkBox_SetIppeak.isChecked():
        checkBox_SetIppeak = '1'
    else:
        checkBox_SetIppeak = ''
    arrayRow2.append(checkBox_SetIppeak)

    if uiThiaWT3000E.checkBox_SetImpeak.isChecked():
        checkBox_SetImpeak = '1'
    else:
        checkBox_SetImpeak = ''
    arrayRow2.append(checkBox_SetImpeak)

    # line6
    if uiThiaWT3000E.checkBox_SetP.isChecked():
        checkBox_SetP = '1'
    else:
        checkBox_SetP = ''
    arrayRow2.append(checkBox_SetP)

    if uiThiaWT3000E.checkBox_SetS.isChecked():
        checkBox_SetS = '1'
    else:
        checkBox_SetS = ''
    arrayRow2.append(checkBox_SetS)

    if uiThiaWT3000E.checkBox_SetQ.isChecked():
        checkBox_SetQ = '1'
    else:
        checkBox_SetQ = ''
    arrayRow2.append(checkBox_SetQ)

    if uiThiaWT3000E.checkBox_SetLambda.isChecked():
        checkBox_SetLambda = '1'
    else:
        checkBox_SetLambda = ''
    arrayRow2.append(checkBox_SetLambda)

    if uiThiaWT3000E.checkBox_SetPhi.isChecked():
        checkBox_SetPhi = '1'
    else:
        checkBox_SetPhi = ''
    arrayRow2.append(checkBox_SetPhi)

    if uiThiaWT3000E.checkBox_SetPc.isChecked():
        checkBox_SetPc = '1'
    else:
        checkBox_SetPc = ''
    arrayRow2.append(checkBox_SetPc)

    # line7
    if uiThiaWT3000E.checkBox_SetFreqU.isChecked():
        checkBox_SetFreqU = '1'
    else:
        checkBox_SetFreqU = ''
    arrayRow2.append(checkBox_SetFreqU)

    if uiThiaWT3000E.checkBox_SetFreqI.isChecked():
        checkBox_SetFreqI = '1'
    else:
        checkBox_SetFreqI = ''
    arrayRow2.append(checkBox_SetFreqI)

    # line8
    if uiThiaWT3000E.checkBox_SetTime.isChecked():
        checkBox_SetTime = '1'
    else:
        checkBox_SetTime = ''
    arrayRow2.append(checkBox_SetTime)

    if uiThiaWT3000E.checkBox_SetWP.isChecked():
        checkBox_SetWP = '1'
    else:
        checkBox_SetWP = ''
    arrayRow2.append(checkBox_SetWP)

    if uiThiaWT3000E.checkBox_SetWPPlus.isChecked():
        checkBox_SetWPPlus = '1'
    else:
        checkBox_SetWPPlus = ''
    arrayRow2.append(checkBox_SetWPPlus)

    if uiThiaWT3000E.checkBox_SetWPMinus.isChecked():
        checkBox_SetWPMinus = '1'
    else:
        checkBox_SetWPMinus = ''
    arrayRow2.append(checkBox_SetWPMinus)

    if uiThiaWT3000E.checkBox_Setq.isChecked():
        checkBox_Setq = '1'
    else:
        checkBox_Setq = ''
    arrayRow2.append(checkBox_Setq)

    if uiThiaWT3000E.checkBox_SetqPlus.isChecked():
        checkBox_SetqPlus = '1'
    else:
        checkBox_SetqPlus = ''
    arrayRow2.append(checkBox_SetqPlus)

    if uiThiaWT3000E.checkBox_SetqMinus.isChecked():
        checkBox_SetqMinus = '1'
    else:
        checkBox_SetqMinus = ''
    arrayRow2.append(checkBox_SetqMinus)

    if uiThiaWT3000E.checkBox_SetWS.isChecked():
        checkBox_SetWS = '1'
    else:
        checkBox_SetWS = ''
    arrayRow2.append(checkBox_SetWS)

    if uiThiaWT3000E.checkBox_SetWQ.isChecked():
        checkBox_SetWQ = '1'
    else:
        checkBox_SetWQ = ''
    arrayRow2.append(checkBox_SetWQ)

    # line9
    if uiThiaWT3000E.checkBox_SetEta1.isChecked():
        checkBox_SetEta1 = '1'
    else:
        checkBox_SetEta1 = ''
    arrayRow2.append(checkBox_SetEta1)

    if uiThiaWT3000E.checkBox_SetEta2.isChecked():
        checkBox_SetEta2 = '1'
    else:
        checkBox_SetEta2 = ''
    arrayRow2.append(checkBox_SetEta2)

    if uiThiaWT3000E.checkBox_SetEta3.isChecked():
        checkBox_SetEta3 = '1'
    else:
        checkBox_SetEta3 = ''
    arrayRow2.append(checkBox_SetEta3)

    if uiThiaWT3000E.checkBox_SetEta4.isChecked():
        checkBox_SetEta4 = '1'
    else:
        checkBox_SetEta4 = ''
    arrayRow2.append(checkBox_SetEta4)
    
    # line10
    textEdit_SetStart = uiThiaWT3000E.textEdit_SetStart.toPlainText()
    arrayRow2.append(textEdit_SetStart)

    textEdit_SetStop = uiThiaWT3000E.textEdit_SetStop.toPlainText()
    arrayRow2.append(textEdit_SetStop)

    # line11
    if uiThiaWT3000E.checkBox_SetUk.isChecked():
        checkBox_SetUk = '1'
    else:
        checkBox_SetUk = ''
    arrayRow2.append(checkBox_SetUk)

    if uiThiaWT3000E.checkBox_SetIk.isChecked():
        checkBox_SetIk = '1'
    else:
        checkBox_SetIk = ''
    arrayRow2.append(checkBox_SetIk)

    if uiThiaWT3000E.checkBox_SetPk.isChecked():
        checkBox_SetPk = '1'
    else:
        checkBox_SetPk = ''
    arrayRow2.append(checkBox_SetPk)

    if uiThiaWT3000E.checkBox_SetSk.isChecked():
        checkBox_SetSk = '1'
    else:
        checkBox_SetSk = ''
    arrayRow2.append(checkBox_SetSk)

    if uiThiaWT3000E.checkBox_SetQk.isChecked():
        checkBox_SetQk = '1'
    else:
        checkBox_SetQk = ''
    arrayRow2.append(checkBox_SetQk)

    if uiThiaWT3000E.checkBox_SetPFk.isChecked():
        checkBox_SetPFk = '1'
    else:
        checkBox_SetPFk = ''
    arrayRow2.append(checkBox_SetPFk)

    # line13
    if uiThiaWT3000E.checkBox_SetPhik.isChecked():
        checkBox_SetPhik = '1'
    else:
        checkBox_SetPhik = ''
    arrayRow2.append(checkBox_SetPhik)

    if uiThiaWT3000E.checkBox_SetPhiUk.isChecked():
        checkBox_SetPhiUk = '1'
    else:
        checkBox_SetPhiUk = ''
    arrayRow2.append(checkBox_SetPhiUk)

    if uiThiaWT3000E.checkBox_SetPhiIk.isChecked():
        checkBox_SetPhiIk = '1'
    else:
        checkBox_SetPhiIk = ''
    arrayRow2.append(checkBox_SetPhiIk)

    if uiThiaWT3000E.checkBox_SetUhdfk.isChecked():
        checkBox_SetUhdfk = '1'
    else:
        checkBox_SetUhdfk = ''
    arrayRow2.append(checkBox_SetUhdfk)

    if uiThiaWT3000E.checkBox_SetIhdfk.isChecked():
        checkBox_SetIhdfk = '1'
    else:
        checkBox_SetIhdfk = ''
    arrayRow2.append(checkBox_SetIhdfk)

    if uiThiaWT3000E.checkBox_SetPhdfk.isChecked():
        checkBox_SetPhdfk = '1'
    else:
        checkBox_SetPhdfk = ''
    arrayRow2.append(checkBox_SetPhdfk)

    # line14
    if uiThiaWT3000E.checkBox_SetZk.isChecked():
        checkBox_SetZk = '1'
    else:
        checkBox_SetZk = ''
    arrayRow2.append(checkBox_SetZk)

    if uiThiaWT3000E.checkBox_SetRsk.isChecked():
        checkBox_SetRsk = '1'
    else:
        checkBox_SetRsk = ''
    arrayRow2.append(checkBox_SetRsk)

    if uiThiaWT3000E.checkBox_SetXsk.isChecked():
        checkBox_SetXsk = '1'
    else:
        checkBox_SetXsk = ''
    arrayRow2.append(checkBox_SetXsk)

    if uiThiaWT3000E.checkBox_SetRpk.isChecked():
        checkBox_SetRpk = '1'
    else:
        checkBox_SetRpk = ''
    arrayRow2.append(checkBox_SetRpk)

    if uiThiaWT3000E.checkBox_SetXpk.isChecked():
        checkBox_SetXpk = '1'
    else:
        checkBox_SetXpk = ''
    arrayRow2.append(checkBox_SetXpk)

    # line15
    if uiThiaWT3000E.checkBox_SetUthd.isChecked():
        checkBox_SetUthd = '1'
    else:
        checkBox_SetUthd = ''
    arrayRow2.append(checkBox_SetUthd)

    if uiThiaWT3000E.checkBox_SetIthd.isChecked():
        checkBox_SetIthd = '1'
    else:
        checkBox_SetIthd = ''
    arrayRow2.append(checkBox_SetIthd)

    if uiThiaWT3000E.checkBox_SetPthd.isChecked():
        checkBox_SetPthd = '1'
    else:
        checkBox_SetPthd = ''
    arrayRow2.append(checkBox_SetPthd)

    if uiThiaWT3000E.checkBox_SetUthf.isChecked():
        checkBox_SetUthf = '1'
    else:
        checkBox_SetUthf = ''
    arrayRow2.append(checkBox_SetUthf)

    if uiThiaWT3000E.checkBox_SetIthf.isChecked():
        checkBox_SetIthf = '1'
    else:
        checkBox_SetIthf = ''
    arrayRow2.append(checkBox_SetIthf)

    # line16
    if uiThiaWT3000E.checkBox_SetUtif.isChecked():
        checkBox_SetUtif = '1'
    else:
        checkBox_SetUtif = ''
    arrayRow2.append(checkBox_SetUtif)

    if uiThiaWT3000E.checkBox_SetItif.isChecked():
        checkBox_SetItif = '1'
    else:
        checkBox_SetItif = ''
    arrayRow2.append(checkBox_SetItif)

    if uiThiaWT3000E.checkBox_Sethvf.isChecked():
        checkBox_Sethvf = '1'
    else:
        checkBox_Sethvf = ''
    arrayRow2.append(checkBox_Sethvf)

    if uiThiaWT3000E.checkBox_Sethcf.isChecked():
        checkBox_Sethcf = '1'
    else:
        checkBox_Sethcf = ''
    arrayRow2.append(checkBox_Sethcf)

    # line17
    if uiThiaWT3000E.checkBox_SetPhiUi_Uj.isChecked():
        checkBox_SetPhiUi_Uj = '1'
    else:
        checkBox_SetPhiUi_Uj = ''
    arrayRow2.append(checkBox_SetPhiUi_Uj)

    if uiThiaWT3000E.checkBox_SetPhiUi_Uk.isChecked():
        checkBox_SetPhiUi_Uk = '1'
    else:
        checkBox_SetPhiUi_Uk = ''
    arrayRow2.append(checkBox_SetPhiUi_Uk)

    if uiThiaWT3000E.checkBox_SetPhiUi_Ii.isChecked():
        checkBox_SetPhiUi_Ii = '1'
    else:
        checkBox_SetPhiUi_Ii = ''
    arrayRow2.append(checkBox_SetPhiUi_Ii)

    if uiThiaWT3000E.checkBox_SetPhiUi_Ij.isChecked():
        checkBox_SetPhiUi_Ij = '1'
    else:
        checkBox_SetPhiUi_Ij = ''
    arrayRow2.append(checkBox_SetPhiUi_Ij)

    if uiThiaWT3000E.checkBox_SetPhiUi_Ik.isChecked():
        checkBox_SetPhiUi_Ik = '1'
    else:
        checkBox_SetPhiUi_Ik = ''
    arrayRow2.append(checkBox_SetPhiUi_Ik)

    # line18
    if uiThiaWT3000E.checkBox_SetSpeed.isChecked():
        checkBox_SetSpeed = '1'
    else:
        checkBox_SetSpeed = ''
    arrayRow2.append(checkBox_SetSpeed)

    if uiThiaWT3000E.checkBox_SetTorque.isChecked():
        checkBox_SetTorque = '1'
    else:
        checkBox_SetTorque = ''
    arrayRow2.append(checkBox_SetTorque)

    if uiThiaWT3000E.checkBox_SetSyncSp.isChecked():
        checkBox_SetSyncSp = '1'
    else:
        checkBox_SetSyncSp = ''
    arrayRow2.append(checkBox_SetSyncSp)

    if uiThiaWT3000E.checkBox_SetSlip.isChecked():
        checkBox_SetSlip = '1'
    else:
        checkBox_SetSlip = ''
    arrayRow2.append(checkBox_SetSlip)

    if uiThiaWT3000E.checkBox_SetPm.isChecked():
        checkBox_SetPm = '1'
    else:
        checkBox_SetPm = ''
    arrayRow2.append(checkBox_SetPm)

    # line19
    if uiThiaWT3000E.checkBox_SetDeltaF1.isChecked():
        checkBox_SetDeltaF1 = '1'
    else:
        checkBox_SetDeltaF1 = ''
    arrayRow2.append(checkBox_SetDeltaF1)

    if uiThiaWT3000E.checkBox_SetDeltaF2.isChecked():
        checkBox_SetDeltaF2 = '1'
    else:
        checkBox_SetDeltaF2 = ''
    arrayRow2.append(checkBox_SetDeltaF2)

    if uiThiaWT3000E.checkBox_SetDeltaF3.isChecked():
        checkBox_SetDeltaF3 = '1'
    else:
        checkBox_SetDeltaF3 = ''
    arrayRow2.append(checkBox_SetDeltaF3)

    if uiThiaWT3000E.checkBox_SetDeltaF4.isChecked():
        checkBox_SetDeltaF4 = '1'
    else:
        checkBox_SetDeltaF4 = ''
    arrayRow2.append(checkBox_SetDeltaF4)

    # line20
    if uiThiaWT3000E.checkBox_SetF01.isChecked():
        checkBox_SetF01 = '1'
    else:
        checkBox_SetF01 = ''
    arrayRow2.append(checkBox_SetF01)

    if uiThiaWT3000E.checkBox_SetF02.isChecked():
        checkBox_SetF02 = '1'
    else:
        checkBox_SetF02 = ''
    arrayRow2.append(checkBox_SetF02)

    if uiThiaWT3000E.checkBox_SetF03.isChecked():
        checkBox_SetF03 = '1'
    else:
        checkBox_SetF03 = ''
    arrayRow2.append(checkBox_SetF03)

    if uiThiaWT3000E.checkBox_SetF04.isChecked():
        checkBox_SetF04 = '1'
    else:
        checkBox_SetF04 = ''
    arrayRow2.append(checkBox_SetF04)

    if uiThiaWT3000E.checkBox_SetF05.isChecked():
        checkBox_SetF05 = '1'
    else:
        checkBox_SetF05 = ''
    arrayRow2.append(checkBox_SetF05)

    if uiThiaWT3000E.checkBox_SetF06.isChecked():
        checkBox_SetF06 = '1'
    else:
        checkBox_SetF06 = ''
    arrayRow2.append(checkBox_SetF06)

    if uiThiaWT3000E.checkBox_SetF07.isChecked():
        checkBox_SetF07 = '1'
    else:
        checkBox_SetF07 = ''
    arrayRow2.append(checkBox_SetF07)

    if uiThiaWT3000E.checkBox_SetF08.isChecked():
        checkBox_SetF08 = '1'
    else:
        checkBox_SetF08 = ''
    arrayRow2.append(checkBox_SetF08)

    if uiThiaWT3000E.checkBox_SetF09.isChecked():
        checkBox_SetF09 = '1'
    else:
        checkBox_SetF09 = ''
    arrayRow2.append(checkBox_SetF09)

    if uiThiaWT3000E.checkBox_SetF10.isChecked():
        checkBox_SetF10 = '1'
    else:
        checkBox_SetF10 = ''
    arrayRow2.append(checkBox_SetF10)

    if uiThiaWT3000E.checkBox_SetF11.isChecked():
        checkBox_SetF11 = '1'
    else:
        checkBox_SetF11 = ''
    arrayRow2.append(checkBox_SetF11)

    if uiThiaWT3000E.checkBox_SetF12.isChecked():
        checkBox_SetF12 = '1'
    else:
        checkBox_SetF12 = ''
    arrayRow2.append(checkBox_SetF12)

    if uiThiaWT3000E.checkBox_SetF13.isChecked():
        checkBox_SetF13 = '1'
    else:
        checkBox_SetF13 = ''
    arrayRow2.append(checkBox_SetF13)

    if uiThiaWT3000E.checkBox_SetF14.isChecked():
        checkBox_SetF14 = '1'
    else:
        checkBox_SetF14 = ''
    arrayRow2.append(checkBox_SetF14)

    if uiThiaWT3000E.checkBox_SetF15.isChecked():
        checkBox_SetF15 = '1'
    else:
        checkBox_SetF15 = ''
    arrayRow2.append(checkBox_SetF15)

    if uiThiaWT3000E.checkBox_SetF16.isChecked():
        checkBox_SetF16 = '1'
    else:
        checkBox_SetF16 = ''
    arrayRow2.append(checkBox_SetF16)

    if uiThiaWT3000E.checkBox_SetF17.isChecked():
        checkBox_SetF17 = '1'
    else:
        checkBox_SetF17 = ''
    arrayRow2.append(checkBox_SetF17)

    if uiThiaWT3000E.checkBox_SetF18.isChecked():
        checkBox_SetF18 = '1'
    else:
        checkBox_SetF18 = ''
    arrayRow2.append(checkBox_SetF18)

    if uiThiaWT3000E.checkBox_SetF19.isChecked():
        checkBox_SetF19 = '1'
    else:
        checkBox_SetF19 = ''
    arrayRow2.append(checkBox_SetF19)

    if uiThiaWT3000E.checkBox_SetF20.isChecked():
        checkBox_SetF20 = '1'
    else:
        checkBox_SetF20 = ''
    arrayRow2.append(checkBox_SetF20)

    result_list = [arrayRow1, arrayRow2]

    return result_list

# WT3000E配置读取设定
def Open_File_ThaiWT3000_Config(uiThiaWT3000E, wt_config_dict):
    strFlag  = "0"

    if arrayRow1[0] in wt_config_dict:
        if wt_config_dict[arrayRow1[0]] == "Thai_WT3000E_Config":

            if strFlag == "0":
                if arrayRow1[1] in wt_config_dict:
                    comboBox_SigmA1 = wt_config_dict[arrayRow1[1]]
                    uiThiaWT3000E.comboBox_SigmA1.setCurrentIndex(int(comboBox_SigmA1))
                else:
                    strFlag = 1

            #comBox
            if strFlag == "0":
                if arrayRow1[2] in wt_config_dict:
                    comboBox_SigmA2 = wt_config_dict[arrayRow1[2]]
                    uiThiaWT3000E.comboBox_SigmA2.setCurrentIndex(int(comboBox_SigmA2))
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[3] in wt_config_dict:
                    comboBox_SigmB1 = wt_config_dict[arrayRow1[3]]
                    uiThiaWT3000E.comboBox_SigmB1.setCurrentIndex(int(comboBox_SigmB1))
                else:
                    strFlag = 1

            #comBox
            if strFlag == "0":
                if arrayRow1[4] in wt_config_dict:
                    comboBox_SigmB2 = wt_config_dict[arrayRow1[4]]
                    uiThiaWT3000E.comboBox_SigmB2.setCurrentIndex(int(comboBox_SigmB2))
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[5] in wt_config_dict:
                    comboBox_UnitSet = wt_config_dict[arrayRow1[5]]
                    uiThiaWT3000E.comboBox_UnitSet.setCurrentIndex(int(comboBox_UnitSet))
                else:
                    strFlag = 1

            #comBox
            if strFlag == "0":
                if arrayRow1[6] in wt_config_dict:
                    comboBox_WiringCom = wt_config_dict[arrayRow1[6]]
                    uiThiaWT3000E.comboBox_WiringCom.setCurrentIndex(int(comboBox_WiringCom))
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[7] in wt_config_dict:
                    comboBox_ReplaceRate = wt_config_dict[arrayRow1[7]]
                    uiThiaWT3000E.comboBox_ReplaceRate.setCurrentIndex(int(comboBox_ReplaceRate))
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[8] in wt_config_dict:
                    comboBox_ProjectNum = wt_config_dict[arrayRow1[8]]
                    uiThiaWT3000E.comboBox_ProjectNum.setCurrentIndex(int(comboBox_ProjectNum))
                else:
                    strFlag = 1

            #comBox
            if strFlag == "0":
                if arrayRow1[9] in wt_config_dict:
                    comboBox_AutoSave = wt_config_dict[arrayRow1[9]]
                    uiThiaWT3000E.comboBox_AutoSave.setCurrentIndex(int(comboBox_AutoSave))
                else:
                    strFlag = 1

            #textEdit
            if strFlag == "0":
                if arrayRow1[10] in wt_config_dict:
                    textEdit_StopTime = wt_config_dict[arrayRow1[10]]
                    uiThiaWT3000E.textEdit_StopTime.setText(textEdit_StopTime)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[11] in wt_config_dict:
                    textEdit_SavePath = wt_config_dict[arrayRow1[11]]
                    uiThiaWT3000E.textEdit_SavePath.setText(textEdit_SavePath)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[12] in wt_config_dict:
                    checkBox_AutoName = wt_config_dict[arrayRow1[12]]
                    if checkBox_AutoName == '1':
                        uiThiaWT3000E.checkBox_AutoName.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_AutoName.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[13] in wt_config_dict:
                    textEdit_FileNameList = wt_config_dict[arrayRow1[13]]
                    uiThiaWT3000E.textEdit_FileNameList.setText(textEdit_FileNameList)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[14] in wt_config_dict:
                    checkBox_SetElement1 = wt_config_dict[arrayRow1[14]]
                    if checkBox_SetElement1 == '1':
                        uiThiaWT3000E.checkBox_SetElement1.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetElement1.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[15] in wt_config_dict:
                    checkBox_SetElement2 = wt_config_dict[arrayRow1[15]]
                    if checkBox_SetElement2 == '1':
                        uiThiaWT3000E.checkBox_SetElement2.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetElement2.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[16] in wt_config_dict:
                    checkBox_SetElement3 = wt_config_dict[arrayRow1[16]]
                    if checkBox_SetElement3 == '1':
                        uiThiaWT3000E.checkBox_SetElement3.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetElement3.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[17] in wt_config_dict:
                    checkBox_SetElement4 = wt_config_dict[arrayRow1[17]]
                    if checkBox_SetElement4 == '1':
                        uiThiaWT3000E.checkBox_SetElement4.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetElement4.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[18] in wt_config_dict:
                    checkBox_SetSigma = wt_config_dict[arrayRow1[18]]
                    if checkBox_SetSigma == '1':
                        uiThiaWT3000E.checkBox_SetSigma.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetSigma.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[19] in wt_config_dict:
                    checkBox_SetSigmaA = wt_config_dict[arrayRow1[19]]
                    if checkBox_SetSigmaA == '1':
                        uiThiaWT3000E.checkBox_SetSigmaA.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetSigmaA.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[20] in wt_config_dict:
                    checkBox_SetSigmaB = wt_config_dict[arrayRow1[20]]
                    if checkBox_SetSigmaB == '1':
                        uiThiaWT3000E.checkBox_SetSigmaB.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetSigmaB.setChecked(False)
                else:
                    strFlag = 1
            # line3
            if strFlag == "0":
                if arrayRow1[21] in wt_config_dict:
                    checkBox_SetU = wt_config_dict[arrayRow1[21]]
                    if checkBox_SetU == '1':
                        uiThiaWT3000E.checkBox_SetU.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetU.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[22] in wt_config_dict:
                    checkBox_SetUrange = wt_config_dict[arrayRow1[22]]
                    if checkBox_SetUrange == '1':
                        uiThiaWT3000E.checkBox_SetUrange.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetUrange.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[23] in wt_config_dict:
                    checkBox_SetCfU = wt_config_dict[arrayRow1[23]]
                    if checkBox_SetCfU == '1':
                        uiThiaWT3000E.checkBox_SetCfU.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetCfU.setChecked(False)
                else:
                    strFlag = 1
            # line4
            if strFlag == "0":
                if arrayRow1[24] in wt_config_dict:
                    checkBox_SetI = wt_config_dict[arrayRow1[24]]
                    if checkBox_SetI == '1':
                        uiThiaWT3000E.checkBox_SetI.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetI.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[25] in wt_config_dict:
                    checkBox_SetIrange = wt_config_dict[arrayRow1[25]]
                    if checkBox_SetIrange == '1':
                        uiThiaWT3000E.checkBox_SetIrange.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetIrange.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[26] in wt_config_dict:
                    checkBox_SetCfI = wt_config_dict[arrayRow1[26]]
                    if checkBox_SetCfI == '1':
                        uiThiaWT3000E.checkBox_SetCfI.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetCfI.setChecked(False)
                else:
                    strFlag = 1
            # line5
            if strFlag == "0":
                if arrayRow1[27] in wt_config_dict:
                    checkBox_SetUppeak = wt_config_dict[arrayRow1[27]]
                    if checkBox_SetUppeak == '1':
                        uiThiaWT3000E.checkBox_SetUppeak.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetUppeak.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[28] in wt_config_dict:
                    checkBox_SetUmpeak = wt_config_dict[arrayRow1[28]]
                    if checkBox_SetUmpeak == '1':
                        uiThiaWT3000E.checkBox_SetUmpeak.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetUmpeak.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[29] in wt_config_dict:
                    checkBox_SetIppeak = wt_config_dict[arrayRow1[29]]
                    if checkBox_SetIppeak == '1':
                        uiThiaWT3000E.checkBox_SetIppeak.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetIppeak.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[30] in wt_config_dict:
                    checkBox_SetImpeak = wt_config_dict[arrayRow1[30]]
                    if checkBox_SetImpeak == '1':
                        uiThiaWT3000E.checkBox_SetImpeak.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetImpeak.setChecked(False)
                else:
                    strFlag = 1
            # line6
            if strFlag == "0":
                if arrayRow1[31] in wt_config_dict:
                    checkBox_SetP = wt_config_dict[arrayRow1[31]]
                    if checkBox_SetP == '1':
                        uiThiaWT3000E.checkBox_SetP.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetP.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[32] in wt_config_dict:
                    checkBox_SetS = wt_config_dict[arrayRow1[32]]
                    if checkBox_SetS == '1':
                        uiThiaWT3000E.checkBox_SetS.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetS.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[33] in wt_config_dict:
                    checkBox_SetQ = wt_config_dict[arrayRow1[33]]
                    if checkBox_SetQ == '1':
                        uiThiaWT3000E.checkBox_SetQ.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetQ.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[34] in wt_config_dict:
                    checkBox_SetLambda = wt_config_dict[arrayRow1[34]]
                    if checkBox_SetLambda == '1':
                        uiThiaWT3000E.checkBox_SetLambda.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetLambda.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[35] in wt_config_dict:
                    checkBox_SetPhi = wt_config_dict[arrayRow1[35]]
                    if checkBox_SetPhi == '1':
                        uiThiaWT3000E.checkBox_SetPhi.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPhi.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[36] in wt_config_dict:
                    checkBox_SetPc = wt_config_dict[arrayRow1[36]]
                    if checkBox_SetPc == '1':
                        uiThiaWT3000E.checkBox_SetPc.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPc.setChecked(False)
                else:
                    strFlag = 1
            # line7
            if strFlag == "0":
                if arrayRow1[37] in wt_config_dict:
                    checkBox_SetFreqU = wt_config_dict[arrayRow1[37]]
                    if checkBox_SetFreqU == '1':
                        uiThiaWT3000E.checkBox_SetFreqU.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetFreqU.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[38] in wt_config_dict:
                    checkBox_SetFreqI = wt_config_dict[arrayRow1[38]]
                    if checkBox_SetFreqI == '1':
                        uiThiaWT3000E.checkBox_SetFreqI.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetFreqI.setChecked(False)
                else:
                    strFlag = 1
            # line8
            if strFlag == "0":
                if arrayRow1[39] in wt_config_dict:
                    checkBox_SetTime = wt_config_dict[arrayRow1[39]]
                    if checkBox_SetTime == '1':
                        uiThiaWT3000E.checkBox_SetTime.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetTime.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[40] in wt_config_dict:
                    checkBox_SetWP = wt_config_dict[arrayRow1[40]]
                    if checkBox_SetWP == '1':
                        uiThiaWT3000E.checkBox_SetWP.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetWP.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[41] in wt_config_dict:
                    checkBox_SetWPPlus = wt_config_dict[arrayRow1[41]]
                    if checkBox_SetWPPlus == '1':
                        uiThiaWT3000E.checkBox_SetWPPlus.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetWPPlus.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[42] in wt_config_dict:
                    checkBox_SetWPMinus = wt_config_dict[arrayRow1[42]]
                    if checkBox_SetWPMinus == '1':
                        uiThiaWT3000E.checkBox_SetWPMinus.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetWPMinus.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[43] in wt_config_dict:
                    checkBox_Setq = wt_config_dict[arrayRow1[43]]
                    if checkBox_Setq == '1':
                        uiThiaWT3000E.checkBox_Setq.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_Setq.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[44] in wt_config_dict:
                    checkBox_SetqPlus = wt_config_dict[arrayRow1[44]]
                    if checkBox_SetqPlus == '1':
                        uiThiaWT3000E.checkBox_SetqPlus.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetqPlus.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[45] in wt_config_dict:
                    checkBox_SetqMinus = wt_config_dict[arrayRow1[45]]
                    if checkBox_SetqMinus == '1':
                        uiThiaWT3000E.checkBox_SetqMinus.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetqMinus.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[46] in wt_config_dict:
                    checkBox_SetWS = wt_config_dict[arrayRow1[46]]
                    if checkBox_SetWS == '1':
                        uiThiaWT3000E.checkBox_SetWS.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetWS.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[47] in wt_config_dict:
                    checkBox_SetWQ = wt_config_dict[arrayRow1[47]]
                    if checkBox_SetWQ == '1':
                        uiThiaWT3000E.checkBox_SetWQ.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetWQ.setChecked(False)
                else:
                    strFlag = 1
            # line9   
            if strFlag == "0":
                if arrayRow1[48] in wt_config_dict:
                    checkBox_SetEta1 = wt_config_dict[arrayRow1[48]]
                    if checkBox_SetEta1 == '1':
                        uiThiaWT3000E.checkBox_SetEta1.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetEta1.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[49] in wt_config_dict:
                    checkBox_SetEta2 = wt_config_dict[arrayRow1[49]]
                    if checkBox_SetEta2 == '1':
                        uiThiaWT3000E.checkBox_SetEta2.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetEta2.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[50] in wt_config_dict:
                    checkBox_SetEta3 = wt_config_dict[arrayRow1[50]]
                    if checkBox_SetEta3 == '1':
                        uiThiaWT3000E.checkBox_SetEta3.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetEta3.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[51] in wt_config_dict:
                    checkBox_SetEta4 = wt_config_dict[arrayRow1[51]]
                    if checkBox_SetEta4 == '1':
                        uiThiaWT3000E.checkBox_SetEta4.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetEta4.setChecked(False)
                else:
                    strFlag = 1
            # line10
            if strFlag == "0":
                if arrayRow1[52] in wt_config_dict:
                    textEdit_SetStart = wt_config_dict[arrayRow1[52]]
                    uiThiaWT3000E.textEdit_SetStart.setText(textEdit_SetStart)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[53] in wt_config_dict:
                    textEdit_SetStop = wt_config_dict[arrayRow1[53]]
                    uiThiaWT3000E.textEdit_SetStop.setText(textEdit_SetStop)
                else:
                    strFlag = 1
            # line11
            if strFlag == "0":
                if arrayRow1[54] in wt_config_dict:
                    checkBox_SetUk = wt_config_dict[arrayRow1[54]]
                    if checkBox_SetUk == '1':
                        uiThiaWT3000E.checkBox_SetUk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetUk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[55] in wt_config_dict:
                    checkBox_SetIk = wt_config_dict[arrayRow1[55]]
                    if checkBox_SetIk == '1':
                        uiThiaWT3000E.checkBox_SetIk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetIk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[56] in wt_config_dict:
                    checkBox_SetPk = wt_config_dict[arrayRow1[56]]
                    if checkBox_SetPk == '1':
                        uiThiaWT3000E.checkBox_SetPk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[57] in wt_config_dict:
                    checkBox_SetSk = wt_config_dict[arrayRow1[57]]
                    if checkBox_SetSk == '1':
                        uiThiaWT3000E.checkBox_SetSk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetSk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[58] in wt_config_dict:
                    checkBox_SetQk = wt_config_dict[arrayRow1[58]]
                    if checkBox_SetQk == '1':
                        uiThiaWT3000E.checkBox_SetQk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetQk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[59] in wt_config_dict:
                    checkBox_SetPFk = wt_config_dict[arrayRow1[59]]
                    if checkBox_SetPFk == '1':
                        uiThiaWT3000E.checkBox_SetPFk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPFk.setChecked(False)
                else:
                    strFlag = 1
            # line12
            if strFlag == "0":
                if arrayRow1[60] in wt_config_dict:
                    checkBox_SetPhik = wt_config_dict[arrayRow1[60]]
                    if checkBox_SetPhik == '1':
                        uiThiaWT3000E.checkBox_SetPhik.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPhik.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[61] in wt_config_dict:
                    checkBox_SetPhiUk = wt_config_dict[arrayRow1[61]]
                    if checkBox_SetPhiUk == '1':
                        uiThiaWT3000E.checkBox_SetPhiUk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPhiUk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[62] in wt_config_dict:
                    checkBox_SetPhiIk = wt_config_dict[arrayRow1[62]]
                    if checkBox_SetPhiIk == '1':
                        uiThiaWT3000E.checkBox_SetPhiIk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPhiIk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[63] in wt_config_dict:
                    checkBox_SetUhdfk = wt_config_dict[arrayRow1[63]]
                    if checkBox_SetUhdfk == '1':
                        uiThiaWT3000E.checkBox_SetUhdfk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetUhdfk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[64] in wt_config_dict:
                    checkBox_SetIhdfk = wt_config_dict[arrayRow1[64]]
                    if checkBox_SetIhdfk == '1':
                        uiThiaWT3000E.checkBox_SetIhdfk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetIhdfk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[65] in wt_config_dict:
                    checkBox_SetPhdfk = wt_config_dict[arrayRow1[65]]
                    if checkBox_SetPhdfk == '1':
                        uiThiaWT3000E.checkBox_SetPhdfk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPhdfk.setChecked(False)
                else:
                    strFlag = 1
            # line13
            if strFlag == "0":
                if arrayRow1[66] in wt_config_dict:
                    checkBox_SetZk = wt_config_dict[arrayRow1[66]]
                    if checkBox_SetZk == '1':
                        uiThiaWT3000E.checkBox_SetZk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetZk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[67] in wt_config_dict:
                    checkBox_SetRsk = wt_config_dict[arrayRow1[67]]
                    if checkBox_SetRsk == '1':
                        uiThiaWT3000E.checkBox_SetRsk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetRsk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[68] in wt_config_dict:
                    checkBox_SetXsk = wt_config_dict[arrayRow1[68]]
                    if checkBox_SetXsk == '1':
                        uiThiaWT3000E.checkBox_SetXsk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetXsk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[69] in wt_config_dict:
                    checkBox_SetRpk = wt_config_dict[arrayRow1[69]]
                    if checkBox_SetRpk == '1':
                        uiThiaWT3000E.checkBox_SetRpk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetRpk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[70] in wt_config_dict:
                    checkBox_SetXpk = wt_config_dict[arrayRow1[70]]
                    if checkBox_SetXpk == '1':
                        uiThiaWT3000E.checkBox_SetXpk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetXpk.setChecked(False)
                else:
                    strFlag = 1
            # line14
            if strFlag == "0":
                if arrayRow1[71] in wt_config_dict:
                    checkBox_SetUthd = wt_config_dict[arrayRow1[71]]
                    if checkBox_SetUthd == '1':
                        uiThiaWT3000E.checkBox_SetUthd.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetUthd.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[72] in wt_config_dict:
                    checkBox_SetIthd = wt_config_dict[arrayRow1[72]]
                    if checkBox_SetIthd == '1':
                        uiThiaWT3000E.checkBox_SetIthd.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetIthd.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[73] in wt_config_dict:
                    checkBox_SetPthd = wt_config_dict[arrayRow1[73]]
                    if checkBox_SetPthd == '1':
                        uiThiaWT3000E.checkBox_SetPthd.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPthd.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[74] in wt_config_dict:
                    checkBox_SetUthf = wt_config_dict[arrayRow1[74]]
                    if checkBox_SetUthf == '1':
                        uiThiaWT3000E.checkBox_SetUthf.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetUthf.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[75] in wt_config_dict:
                    checkBox_SetIthf = wt_config_dict[arrayRow1[75]]
                    if checkBox_SetIthf == '1':
                        uiThiaWT3000E.checkBox_SetIthf.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetIthf.setChecked(False)
                else:
                    strFlag = 1
            # line15
            if strFlag == "0":
                if arrayRow1[76] in wt_config_dict:
                    checkBox_SetUtif = wt_config_dict[arrayRow1[76]]
                    if checkBox_SetUtif == '1':
                        uiThiaWT3000E.checkBox_SetUtif.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetUtif.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[77] in wt_config_dict:
                    checkBox_SetItif = wt_config_dict[arrayRow1[77]]
                    if checkBox_SetItif == '1':
                        uiThiaWT3000E.checkBox_SetItif.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetItif.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[78] in wt_config_dict:
                    checkBox_Sethvf = wt_config_dict[arrayRow1[78]]
                    if checkBox_Sethvf == '1':
                        uiThiaWT3000E.checkBox_Sethvf.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_Sethvf.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[79] in wt_config_dict:
                    checkBox_Sethcf = wt_config_dict[arrayRow1[79]]
                    if checkBox_Sethcf == '1':
                        uiThiaWT3000E.checkBox_Sethcf.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_Sethcf.setChecked(False)
                else:
                    strFlag = 1
            # line16
            if strFlag == "0":
                if arrayRow1[80] in wt_config_dict:
                    checkBox_SetPhiUi_Uj = wt_config_dict[arrayRow1[80]]
                    if checkBox_SetPhiUi_Uj == '1':
                        uiThiaWT3000E.checkBox_SetPhiUi_Uj.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPhiUi_Uj.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[81] in wt_config_dict:
                    checkBox_SetPhiUi_Uk = wt_config_dict[arrayRow1[81]]
                    if checkBox_SetPhiUi_Uk == '1':
                        uiThiaWT3000E.checkBox_SetPhiUi_Uk.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPhiUi_Uk.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[82] in wt_config_dict:
                    checkBox_SetPhiUi_Ii = wt_config_dict[arrayRow1[82]]
                    if checkBox_SetPhiUi_Ii == '1':
                        uiThiaWT3000E.checkBox_SetPhiUi_Ii.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPhiUi_Ii.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[83] in wt_config_dict:
                    checkBox_SetPhiUi_Ij = wt_config_dict[arrayRow1[83]]
                    if checkBox_SetPhiUi_Ij == '1':
                        uiThiaWT3000E.checkBox_SetPhiUi_Ij.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPhiUi_Ij.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[84] in wt_config_dict:
                    checkBox_SetPhiUi_Ik = wt_config_dict[arrayRow1[84]]
                    if checkBox_SetPhiUi_Ik == '1':
                        uiThiaWT3000E.checkBox_SetPhiUi_Ik.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPhiUi_Ik.setChecked(False)
                else:
                    strFlag = 1
            # line17
            if strFlag == "0":
                if arrayRow1[85] in wt_config_dict:
                    checkBox_SetSpeed = wt_config_dict[arrayRow1[85]]
                    if checkBox_SetSpeed == '1':
                        uiThiaWT3000E.checkBox_SetSpeed.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetSpeed.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[86] in wt_config_dict:
                    checkBox_SetTorque = wt_config_dict[arrayRow1[86]]
                    if checkBox_SetTorque == '1':
                        uiThiaWT3000E.checkBox_SetTorque.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetTorque.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[87] in wt_config_dict:
                    checkBox_SetSyncSp = wt_config_dict[arrayRow1[87]]
                    if checkBox_SetSyncSp == '1':
                        uiThiaWT3000E.checkBox_SetSyncSp.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetSyncSp.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[88] in wt_config_dict:
                    checkBox_SetSlip = wt_config_dict[arrayRow1[88]]
                    if checkBox_SetSlip == '1':
                        uiThiaWT3000E.checkBox_SetSlip.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetSlip.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[89] in wt_config_dict:
                    checkBox_SetPm = wt_config_dict[arrayRow1[89]]
                    if checkBox_SetPm == '1':
                        uiThiaWT3000E.checkBox_SetPm.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetPm.setChecked(False)
                else:
                    strFlag = 1
            # line-
            if strFlag == "0":
                if arrayRow1[90] in wt_config_dict:
                    checkBox_SetDeltaF1 = wt_config_dict[arrayRow1[90]]
                    if checkBox_SetDeltaF1 == '1':
                        uiThiaWT3000E.checkBox_SetDeltaF1.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetDeltaF1.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[91] in wt_config_dict:
                    checkBox_SetDeltaF2 = wt_config_dict[arrayRow1[91]]
                    if checkBox_SetDeltaF2 == '1':
                        uiThiaWT3000E.checkBox_SetDeltaF2.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetDeltaF2.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[92] in wt_config_dict:
                    checkBox_SetDeltaF3 = wt_config_dict[arrayRow1[92]]
                    if checkBox_SetDeltaF3 == '1':
                        uiThiaWT3000E.checkBox_SetDeltaF3.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetDeltaF3.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[93] in wt_config_dict:
                    checkBox_SetDeltaF4 = wt_config_dict[arrayRow1[93]]
                    if checkBox_SetDeltaF4 == '1':
                        uiThiaWT3000E.checkBox_SetDeltaF4.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetDeltaF4.setChecked(False)
                else:
                    strFlag = 1
            # line18
            if strFlag == "0":
                if arrayRow1[94] in wt_config_dict:
                    checkBox_SetF01 = wt_config_dict[arrayRow1[94]]
                    if checkBox_SetF01 == '1':
                        uiThiaWT3000E.checkBox_SetF01.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF01.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[95] in wt_config_dict:
                    checkBox_SetF02 = wt_config_dict[arrayRow1[95]]
                    if checkBox_SetF02 == '1':
                        uiThiaWT3000E.checkBox_SetF02.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF02.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[96] in wt_config_dict:
                    checkBox_SetF03 = wt_config_dict[arrayRow1[96]]
                    if checkBox_SetF03 == '1':
                        uiThiaWT3000E.checkBox_SetF03.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF03.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[97] in wt_config_dict:
                    checkBox_SetF04 = wt_config_dict[arrayRow1[97]]
                    if checkBox_SetF04 == '1':
                        uiThiaWT3000E.checkBox_SetF04.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF04.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[98] in wt_config_dict:
                    checkBox_SetF05 = wt_config_dict[arrayRow1[98]]
                    if checkBox_SetF05 == '1':
                        uiThiaWT3000E.checkBox_SetF05.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF05.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[99] in wt_config_dict:
                    checkBox_SetF06 = wt_config_dict[arrayRow1[99]]
                    if checkBox_SetF06 == '1':
                        uiThiaWT3000E.checkBox_SetF06.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF06.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[100] in wt_config_dict:
                    checkBox_SetF07 = wt_config_dict[arrayRow1[100]]
                    if checkBox_SetF07 == '1':
                        uiThiaWT3000E.checkBox_SetF07.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF07.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[101] in wt_config_dict:
                    checkBox_SetF08 = wt_config_dict[arrayRow1[101]]
                    if checkBox_SetF08 == '1':
                        uiThiaWT3000E.checkBox_SetF08.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF08.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[102] in wt_config_dict:
                    checkBox_SetF09 = wt_config_dict[arrayRow1[102]]
                    if checkBox_SetF09 == '1':
                        uiThiaWT3000E.checkBox_SetF09.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF09.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[103] in wt_config_dict:
                    checkBox_SetF10 = wt_config_dict[arrayRow1[103]]
                    if checkBox_SetF10 == '1':
                        uiThiaWT3000E.checkBox_SetF10.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF10.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[104] in wt_config_dict:
                    checkBox_SetF11 = wt_config_dict[arrayRow1[104]]
                    if checkBox_SetF11 == '1':
                        uiThiaWT3000E.checkBox_SetF11.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF11.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[105] in wt_config_dict:
                    checkBox_SetF12 = wt_config_dict[arrayRow1[105]]
                    if checkBox_SetF12 == '1':
                        uiThiaWT3000E.checkBox_SetF12.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF12.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[106] in wt_config_dict:
                    checkBox_SetF13 = wt_config_dict[arrayRow1[106]]
                    if checkBox_SetF13 == '1':
                        uiThiaWT3000E.checkBox_SetF13.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF13.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[107] in wt_config_dict:
                    checkBox_SetF14 = wt_config_dict[arrayRow1[107]]
                    if checkBox_SetF14 == '1':
                        uiThiaWT3000E.checkBox_SetF14.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF14.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[108] in wt_config_dict:
                    checkBox_SetF15 = wt_config_dict[arrayRow1[108]]
                    if checkBox_SetF15 == '1':
                        uiThiaWT3000E.checkBox_SetF15.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF15.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[109] in wt_config_dict:
                    checkBox_SetF16 = wt_config_dict[arrayRow1[109]]
                    if checkBox_SetF16 == '1':
                        uiThiaWT3000E.checkBox_SetF16.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF16.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[110] in wt_config_dict:
                    checkBox_SetF17 = wt_config_dict[arrayRow1[110]]
                    if checkBox_SetF17 == '1':
                        uiThiaWT3000E.checkBox_SetF17.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF17.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[111] in wt_config_dict:
                    checkBox_SetF18 = wt_config_dict[arrayRow1[111]]
                    if checkBox_SetF18 == '1':
                        uiThiaWT3000E.checkBox_SetF18.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF18.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[112] in wt_config_dict:
                    checkBox_SetF19 = wt_config_dict[arrayRow1[112]]
                    if checkBox_SetF19 == '1':
                        uiThiaWT3000E.checkBox_SetF19.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF19.setChecked(False)
                else:
                    strFlag = 1

            if strFlag == "0":
                if arrayRow1[113] in wt_config_dict:
                    checkBox_SetF20 = wt_config_dict[arrayRow1[113]]
                    if checkBox_SetF20 == '1':
                        uiThiaWT3000E.checkBox_SetF20.setChecked(True)
                    else:
                        uiThiaWT3000E.checkBox_SetF20.setChecked(False)
                else:
                    strFlag = 1
            
            return 1

        else:
            print("no")
            strFlag = "1"

def WT3000E_params_config(uiThiaWT3000E):
    params_dict = {}
    params_dict.update({"Style":"Thai_WT3000E_Config"})

    comboBox_SigmA1 = uiThiaWT3000E.comboBox_SigmA1.currentIndex()
    params_dict.update({"comboBox_SigmA1":comboBox_SigmA1})

    comboBox_SigmA2 = uiThiaWT3000E.comboBox_SigmA2.currentIndex()
    params_dict.update({"comboBox_SigmA2":comboBox_SigmA2})

    comboBox_SigmB1 = uiThiaWT3000E.comboBox_SigmB1.currentIndex()
    params_dict.update({"comboBox_SigmB1":comboBox_SigmB1})

    comboBox_SigmB2 = uiThiaWT3000E.comboBox_SigmB2.currentIndex()
    params_dict.update({"comboBox_SigmB2":comboBox_SigmB2})

    comboBox_UnitSet = uiThiaWT3000E.comboBox_UnitSet.currentIndex()
    params_dict.update({"comboBox_UnitSet":comboBox_UnitSet})

    comboBox_WiringCom = uiThiaWT3000E.comboBox_WiringCom.currentIndex()
    params_dict.update({"comboBox_WiringCom":comboBox_WiringCom})

    comboBox_ReplaceRate = uiThiaWT3000E.comboBox_ReplaceRate.currentIndex()
    params_dict.update({"comboBox_ReplaceRate":comboBox_ReplaceRate})

    comboBox_ProjectNum = uiThiaWT3000E.comboBox_ProjectNum.currentIndex()
    params_dict.update({"comboBox_ProjectNum":comboBox_ProjectNum})

    comboBox_AutoSave = uiThiaWT3000E.comboBox_AutoSave.currentIndex()
    params_dict.update({"comboBox_AutoSave":comboBox_AutoSave})

    textEdit_StopTime = uiThiaWT3000E.textEdit_StopTime.toPlainText()
    params_dict.update({"textEdit_StopTime":textEdit_StopTime})
    
    textEdit_SavePath = uiThiaWT3000E.textEdit_SavePath.toPlainText()
    params_dict.update({"textEdit_SavePath":textEdit_SavePath})

    if uiThiaWT3000E.checkBox_AutoName.isChecked():
        checkBox_AutoName = '1'
    else:
        checkBox_AutoName = '0'
    params_dict.update({"checkBox_AutoName":checkBox_AutoName})

    textEdit_FileNameList = uiThiaWT3000E.textEdit_FileNameList.toPlainText()
    params_dict.update({"textEdit_FileNameList":textEdit_FileNameList})

    if uiThiaWT3000E.checkBox_SetElement1.isChecked():
        checkBox_SetElement1 = '1'
    else:
        checkBox_SetElement1 = ''
    params_dict.update({"checkBox_SetElement1":checkBox_SetElement1})

    if uiThiaWT3000E.checkBox_SetElement2.isChecked():
        checkBox_SetElement2 = '1'
    else:
        checkBox_SetElement2 = ''
    params_dict.update({"checkBox_SetElement2":checkBox_SetElement2})

    if uiThiaWT3000E.checkBox_SetElement3.isChecked():
        checkBox_SetElement3 = '1'
    else:
        checkBox_SetElement3 = ''
    params_dict.update({"checkBox_SetElement3":checkBox_SetElement3})

    if uiThiaWT3000E.checkBox_SetElement4.isChecked():
        checkBox_SetElement4 = '1'
    else:
        checkBox_SetElement4 = ''
    params_dict.update({"checkBox_SetElement4":checkBox_SetElement4})

    # line2
    if uiThiaWT3000E.checkBox_SetSigma.isChecked():
        checkBox_SetSigma = '1'
    else:
        checkBox_SetSigma = ''
    params_dict.update({"checkBox_SetSigma":checkBox_SetSigma})

    if uiThiaWT3000E.checkBox_SetSigmaA.isChecked():
        checkBox_SetSigmaA = '1'
    else:
        checkBox_SetSigmaA = ''
    params_dict.update({"checkBox_SetSigmaA":checkBox_SetSigmaA})

    if uiThiaWT3000E.checkBox_SetSigmaB.isChecked():
        checkBox_SetSigmaB = '1'
    else:
        checkBox_SetSigmaB = ''
    params_dict.update({"checkBox_SetSigmaB":checkBox_SetSigmaB})

    # line3
    if uiThiaWT3000E.checkBox_SetU.isChecked():
        checkBox_SetU = '1'
    else:
        checkBox_SetU = ''
    params_dict.update({"checkBox_SetU":checkBox_SetU})

    if uiThiaWT3000E.checkBox_SetUrange.isChecked():
        checkBox_SetUrange = '1'
    else:
        checkBox_SetUrange = ''
    params_dict.update({"checkBox_SetUrange":checkBox_SetUrange})

    if uiThiaWT3000E.checkBox_SetCfU.isChecked():
        checkBox_SetCfU = '1'
    else:
        checkBox_SetCfU = ''
    params_dict.update({"checkBox_SetCfU":checkBox_SetCfU})

    # line4
    if uiThiaWT3000E.checkBox_SetI.isChecked():
        checkBox_SetI = '1'
    else:
        checkBox_SetI = ''
    params_dict.update({"checkBox_SetI":checkBox_SetI})

    if uiThiaWT3000E.checkBox_SetIrange.isChecked():
        checkBox_SetIrange = '1'
    else:
        checkBox_SetIrange = ''
    params_dict.update({"checkBox_SetIrange":checkBox_SetIrange})

    if uiThiaWT3000E.checkBox_SetCfI.isChecked():
        checkBox_SetCfI = '1'
    else:
        checkBox_SetCfI = ''
    params_dict.update({"checkBox_SetCfI":checkBox_SetCfI})

    # line5
    if uiThiaWT3000E.checkBox_SetUppeak.isChecked():
        checkBox_SetUppeak = '1'
    else:
        checkBox_SetUppeak = ''
    params_dict.update({"checkBox_SetUppeak":checkBox_SetUppeak})

    if uiThiaWT3000E.checkBox_SetUmpeak.isChecked():
        checkBox_SetUmpeak = '1'
    else:
        checkBox_SetUmpeak = ''
    params_dict.update({"checkBox_SetUmpeak":checkBox_SetUmpeak})

    if uiThiaWT3000E.checkBox_SetIppeak.isChecked():
        checkBox_SetIppeak = '1'
    else:
        checkBox_SetIppeak = ''
    params_dict.update({"checkBox_SetIppeak":checkBox_SetIppeak})

    if uiThiaWT3000E.checkBox_SetImpeak.isChecked():
        checkBox_SetImpeak = '1'
    else:
        checkBox_SetImpeak = ''
    params_dict.update({"checkBox_SetImpeak":checkBox_SetImpeak})

    # line6
    if uiThiaWT3000E.checkBox_SetP.isChecked():
        checkBox_SetP = '1'
    else:
        checkBox_SetP = ''
    params_dict.update({"checkBox_SetP":checkBox_SetP})

    if uiThiaWT3000E.checkBox_SetS.isChecked():
        checkBox_SetS = '1'
    else:
        checkBox_SetS = ''
    params_dict.update({"checkBox_SetS":checkBox_SetS})

    if uiThiaWT3000E.checkBox_SetQ.isChecked():
        checkBox_SetQ = '1'
    else:
        checkBox_SetQ = ''
    params_dict.update({"checkBox_SetQ":checkBox_SetQ})

    if uiThiaWT3000E.checkBox_SetLambda.isChecked():
        checkBox_SetLambda = '1'
    else:
        checkBox_SetLambda = ''
    params_dict.update({"checkBox_SetLambda":checkBox_SetLambda})

    if uiThiaWT3000E.checkBox_SetPhi.isChecked():
        checkBox_SetPhi = '1'
    else:
        checkBox_SetPhi = ''
    params_dict.update({"checkBox_SetPhi":checkBox_SetPhi})

    if uiThiaWT3000E.checkBox_SetPc.isChecked():
        checkBox_SetPc = '1'
    else:
        checkBox_SetPc = ''
    params_dict.update({"checkBox_SetPc":checkBox_SetPc})

    # line7
    if uiThiaWT3000E.checkBox_SetFreqU.isChecked():
        checkBox_SetFreqU = '1'
    else:
        checkBox_SetFreqU = ''
    params_dict.update({"checkBox_SetFreqU":checkBox_SetFreqU})

    if uiThiaWT3000E.checkBox_SetFreqI.isChecked():
        checkBox_SetFreqI = '1'
    else:
        checkBox_SetFreqI = ''
    params_dict.update({"checkBox_SetFreqI":checkBox_SetFreqI})

    # line8
    if uiThiaWT3000E.checkBox_SetTime.isChecked():
        checkBox_SetTime = '1'
    else:
        checkBox_SetTime = ''
    params_dict.update({"checkBox_SetTime":checkBox_SetTime})

    if uiThiaWT3000E.checkBox_SetWP.isChecked():
        checkBox_SetWP = '1'
    else:
        checkBox_SetWP = ''
    params_dict.update({"checkBox_SetWP":checkBox_SetWP})

    if uiThiaWT3000E.checkBox_SetWPPlus.isChecked():
        checkBox_SetWPPlus = '1'
    else:
        checkBox_SetWPPlus = ''
    params_dict.update({"checkBox_SetWPPlus":checkBox_SetWPPlus})

    if uiThiaWT3000E.checkBox_SetWPMinus.isChecked():
        checkBox_SetWPMinus = '1'
    else:
        checkBox_SetWPMinus = ''
    params_dict.update({"checkBox_SetWPMinus":checkBox_SetWPMinus})

    if uiThiaWT3000E.checkBox_Setq.isChecked():
        checkBox_Setq = '1'
    else:
        checkBox_Setq = ''
    params_dict.update({"checkBox_Setq":checkBox_Setq})

    if uiThiaWT3000E.checkBox_SetqPlus.isChecked():
        checkBox_SetqPlus = '1'
    else:
        checkBox_SetqPlus = ''
    params_dict.update({"checkBox_SetqPlus":checkBox_SetqPlus})

    if uiThiaWT3000E.checkBox_SetqMinus.isChecked():
        checkBox_SetqMinus = '1'
    else:
        checkBox_SetqMinus = ''
    params_dict.update({"checkBox_SetqMinus":checkBox_SetqMinus})

    if uiThiaWT3000E.checkBox_SetWS.isChecked():
        checkBox_SetWS = '1'
    else:
        checkBox_SetWS = ''
    params_dict.update({"checkBox_SetWS":checkBox_SetWS})

    if uiThiaWT3000E.checkBox_SetWQ.isChecked():
        checkBox_SetWQ = '1'
    else:
        checkBox_SetWQ = ''
    params_dict.update({"checkBox_SetWQ":checkBox_SetWQ})

    # line9
    if uiThiaWT3000E.checkBox_SetEta1.isChecked():
        checkBox_SetEta1 = '1'
    else:
        checkBox_SetEta1 = ''
    params_dict.update({"checkBox_SetEta1":checkBox_SetEta1})

    if uiThiaWT3000E.checkBox_SetEta2.isChecked():
        checkBox_SetEta2 = '1'
    else:
        checkBox_SetEta2 = ''
    params_dict.update({"checkBox_SetEta2":checkBox_SetEta2})

    if uiThiaWT3000E.checkBox_SetEta3.isChecked():
        checkBox_SetEta3 = '1'
    else:
        checkBox_SetEta3 = ''
    params_dict.update({"checkBox_SetEta3":checkBox_SetEta3})

    if uiThiaWT3000E.checkBox_SetEta4.isChecked():
        checkBox_SetEta4 = '1'
    else:
        checkBox_SetEta4 = ''
    params_dict.update({"checkBox_SetEta4":checkBox_SetEta4})
    
    # line10
    textEdit_SetStart = uiThiaWT3000E.textEdit_SetStart.toPlainText()
    params_dict.update({"textEdit_SetStart":textEdit_SetStart})

    textEdit_SetStop = uiThiaWT3000E.textEdit_SetStop.toPlainText()
    params_dict.update({"textEdit_SetStop":textEdit_SetStop})

    # line11
    if uiThiaWT3000E.checkBox_SetUk.isChecked():
        checkBox_SetUk = '1'
    else:
        checkBox_SetUk = ''
    params_dict.update({"checkBox_SetUk":checkBox_SetUk})

    if uiThiaWT3000E.checkBox_SetIk.isChecked():
        checkBox_SetIk = '1'
    else:
        checkBox_SetIk = ''
    params_dict.update({"checkBox_SetIk":checkBox_SetIk})

    if uiThiaWT3000E.checkBox_SetPk.isChecked():
        checkBox_SetPk = '1'
    else:
        checkBox_SetPk = ''
    params_dict.update({"checkBox_SetPk":checkBox_SetPk})

    if uiThiaWT3000E.checkBox_SetSk.isChecked():
        checkBox_SetSk = '1'
    else:
        checkBox_SetSk = ''
    params_dict.update({"checkBox_SetSk":checkBox_SetSk})

    if uiThiaWT3000E.checkBox_SetQk.isChecked():
        checkBox_SetQk = '1'
    else:
        checkBox_SetQk = ''
    params_dict.update({"checkBox_SetQk":checkBox_SetQk})

    if uiThiaWT3000E.checkBox_SetPFk.isChecked():
        checkBox_SetPFk = '1'
    else:
        checkBox_SetPFk = ''
    params_dict.update({"checkBox_SetPFk":checkBox_SetPFk})

    # line13
    if uiThiaWT3000E.checkBox_SetPhik.isChecked():
        checkBox_SetPhik = '1'
    else:
        checkBox_SetPhik = ''
    params_dict.update({"checkBox_SetPhik":checkBox_SetPhik})

    if uiThiaWT3000E.checkBox_SetPhiUk.isChecked():
        checkBox_SetPhiUk = '1'
    else:
        checkBox_SetPhiUk = ''
    params_dict.update({"checkBox_SetPhiUk":checkBox_SetPhiUk})

    if uiThiaWT3000E.checkBox_SetPhiIk.isChecked():
        checkBox_SetPhiIk = '1'
    else:
        checkBox_SetPhiIk = ''
    params_dict.update({"checkBox_SetPhiIk":checkBox_SetPhiIk})

    if uiThiaWT3000E.checkBox_SetUhdfk.isChecked():
        checkBox_SetUhdfk = '1'
    else:
        checkBox_SetUhdfk = ''
    params_dict.update({"checkBox_SetUhdfk":checkBox_SetUhdfk})

    if uiThiaWT3000E.checkBox_SetIhdfk.isChecked():
        checkBox_SetIhdfk = '1'
    else:
        checkBox_SetIhdfk = ''
    params_dict.update({"checkBox_SetIhdfk":checkBox_SetIhdfk})

    if uiThiaWT3000E.checkBox_SetPhdfk.isChecked():
        checkBox_SetPhdfk = '1'
    else:
        checkBox_SetPhdfk = ''
    params_dict.update({"checkBox_SetPhdfk":checkBox_SetPhdfk})

    # line14
    if uiThiaWT3000E.checkBox_SetZk.isChecked():
        checkBox_SetZk = '1'
    else:
        checkBox_SetZk = ''
    params_dict.update({"checkBox_SetZk":checkBox_SetZk})

    if uiThiaWT3000E.checkBox_SetRsk.isChecked():
        checkBox_SetRsk = '1'
    else:
        checkBox_SetRsk = ''
    params_dict.update({"checkBox_SetRsk":checkBox_SetRsk})

    if uiThiaWT3000E.checkBox_SetXsk.isChecked():
        checkBox_SetXsk = '1'
    else:
        checkBox_SetXsk = ''
    params_dict.update({"checkBox_SetXsk":checkBox_SetXsk})

    if uiThiaWT3000E.checkBox_SetRpk.isChecked():
        checkBox_SetRpk = '1'
    else:
        checkBox_SetRpk = ''
    params_dict.update({"checkBox_SetRpk":checkBox_SetRpk})

    if uiThiaWT3000E.checkBox_SetXpk.isChecked():
        checkBox_SetXpk = '1'
    else:
        checkBox_SetXpk = ''
    params_dict.update({"checkBox_SetXpk":checkBox_SetXpk})

    # line15
    if uiThiaWT3000E.checkBox_SetUthd.isChecked():
        checkBox_SetUthd = '1'
    else:
        checkBox_SetUthd = ''
    params_dict.update({"checkBox_SetUthd":checkBox_SetUthd})

    if uiThiaWT3000E.checkBox_SetIthd.isChecked():
        checkBox_SetIthd = '1'
    else:
        checkBox_SetIthd = ''
    params_dict.update({"checkBox_SetIthd":checkBox_SetIthd})

    if uiThiaWT3000E.checkBox_SetPthd.isChecked():
        checkBox_SetPthd = '1'
    else:
        checkBox_SetPthd = ''
    params_dict.update({"checkBox_SetPthd":checkBox_SetPthd})

    if uiThiaWT3000E.checkBox_SetUthf.isChecked():
        checkBox_SetUthf = '1'
    else:
        checkBox_SetUthf = ''
    params_dict.update({"checkBox_SetUthf":checkBox_SetUthf})

    if uiThiaWT3000E.checkBox_SetIthf.isChecked():
        checkBox_SetIthf = '1'
    else:
        checkBox_SetIthf = ''
    params_dict.update({"checkBox_SetIthf":checkBox_SetIthf})

    # line16
    if uiThiaWT3000E.checkBox_SetUtif.isChecked():
        checkBox_SetUtif = '1'
    else:
        checkBox_SetUtif = ''
    params_dict.update({"checkBox_SetUtif":checkBox_SetUtif})

    if uiThiaWT3000E.checkBox_SetItif.isChecked():
        checkBox_SetItif = '1'
    else:
        checkBox_SetItif = ''
    params_dict.update({"checkBox_SetItif":checkBox_SetItif})

    if uiThiaWT3000E.checkBox_Sethvf.isChecked():
        checkBox_Sethvf = '1'
    else:
        checkBox_Sethvf = ''
    params_dict.update({"checkBox_Sethvf":checkBox_Sethvf})

    if uiThiaWT3000E.checkBox_Sethcf.isChecked():
        checkBox_Sethcf = '1'
    else:
        checkBox_Sethcf = ''
    params_dict.update({"checkBox_Sethcf":checkBox_Sethcf})

    # line17
    if uiThiaWT3000E.checkBox_SetPhiUi_Uj.isChecked():
        checkBox_SetPhiUi_Uj = '1'
    else:
        checkBox_SetPhiUi_Uj = ''
    params_dict.update({"checkBox_SetPhiUi_Uj":checkBox_SetPhiUi_Uj})

    if uiThiaWT3000E.checkBox_SetPhiUi_Uk.isChecked():
        checkBox_SetPhiUi_Uk = '1'
    else:
        checkBox_SetPhiUi_Uk = ''
    params_dict.update({"checkBox_SetPhiUi_Uk":checkBox_SetPhiUi_Uk})

    if uiThiaWT3000E.checkBox_SetPhiUi_Ii.isChecked():
        checkBox_SetPhiUi_Ii = '1'
    else:
        checkBox_SetPhiUi_Ii = ''
    params_dict.update({"checkBox_SetPhiUi_Ii":checkBox_SetPhiUi_Ii})

    if uiThiaWT3000E.checkBox_SetPhiUi_Ij.isChecked():
        checkBox_SetPhiUi_Ij = '1'
    else:
        checkBox_SetPhiUi_Ij = ''
    params_dict.update({"checkBox_SetPhiUi_Ij":checkBox_SetPhiUi_Ij})

    if uiThiaWT3000E.checkBox_SetPhiUi_Ik.isChecked():
        checkBox_SetPhiUi_Ik = '1'
    else:
        checkBox_SetPhiUi_Ik = ''
    params_dict.update({"checkBox_SetPhiUi_Ik":checkBox_SetPhiUi_Ik})

    # line18
    if uiThiaWT3000E.checkBox_SetSpeed.isChecked():
        checkBox_SetSpeed = '1'
    else:
        checkBox_SetSpeed = ''
    params_dict.update({"checkBox_SetSpeed":checkBox_SetSpeed})

    if uiThiaWT3000E.checkBox_SetTorque.isChecked():
        checkBox_SetTorque = '1'
    else:
        checkBox_SetTorque = ''
    params_dict.update({"checkBox_SetTorque":checkBox_SetTorque})

    if uiThiaWT3000E.checkBox_SetSyncSp.isChecked():
        checkBox_SetSyncSp = '1'
    else:
        checkBox_SetSyncSp = ''
    params_dict.update({"checkBox_SetSyncSp":checkBox_SetSyncSp})

    if uiThiaWT3000E.checkBox_SetSlip.isChecked():
        checkBox_SetSlip = '1'
    else:
        checkBox_SetSlip = ''
    params_dict.update({"checkBox_SetSlip":checkBox_SetSlip})

    if uiThiaWT3000E.checkBox_SetPm.isChecked():
        checkBox_SetPm = '1'
    else:
        checkBox_SetPm = ''
    params_dict.update({"checkBox_SetPm":checkBox_SetPm})

    # line19
    if uiThiaWT3000E.checkBox_SetDeltaF1.isChecked():
        checkBox_SetDeltaF1 = '1'
    else:
        checkBox_SetDeltaF1 = ''
    params_dict.update({"checkBox_SetDeltaF1":checkBox_SetDeltaF1})

    if uiThiaWT3000E.checkBox_SetDeltaF2.isChecked():
        checkBox_SetDeltaF2 = '1'
    else:
        checkBox_SetDeltaF2 = ''
    params_dict.update({"checkBox_SetDeltaF2":checkBox_SetDeltaF2})

    if uiThiaWT3000E.checkBox_SetDeltaF3.isChecked():
        checkBox_SetDeltaF3 = '1'
    else:
        checkBox_SetDeltaF3 = ''
    params_dict.update({"checkBox_SetDeltaF3":checkBox_SetDeltaF3})

    if uiThiaWT3000E.checkBox_SetDeltaF4.isChecked():
        checkBox_SetDeltaF4 = '1'
    else:
        checkBox_SetDeltaF4 = ''
    params_dict.update({"checkBox_SetDeltaF4":checkBox_SetDeltaF4})

    # line20
    if uiThiaWT3000E.checkBox_SetF01.isChecked():
        checkBox_SetF01 = '1'
    else:
        checkBox_SetF01 = ''
    params_dict.update({"checkBox_SetF01":checkBox_SetF01})

    if uiThiaWT3000E.checkBox_SetF02.isChecked():
        checkBox_SetF02 = '1'
    else:
        checkBox_SetF02 = ''
    params_dict.update({"checkBox_SetF02":checkBox_SetF02})

    if uiThiaWT3000E.checkBox_SetF03.isChecked():
        checkBox_SetF03 = '1'
    else:
        checkBox_SetF03 = ''
    params_dict.update({"checkBox_SetF03":checkBox_SetF03})

    if uiThiaWT3000E.checkBox_SetF04.isChecked():
        checkBox_SetF04 = '1'
    else:
        checkBox_SetF04 = ''
    params_dict.update({"checkBox_SetF04":checkBox_SetF04})

    if uiThiaWT3000E.checkBox_SetF05.isChecked():
        checkBox_SetF05 = '1'
    else:
        checkBox_SetF05 = ''
    params_dict.update({"checkBox_SetF05":checkBox_SetF05})

    if uiThiaWT3000E.checkBox_SetF06.isChecked():
        checkBox_SetF06 = '1'
    else:
        checkBox_SetF06 = ''
    params_dict.update({"checkBox_SetF06":checkBox_SetF06})

    if uiThiaWT3000E.checkBox_SetF07.isChecked():
        checkBox_SetF07 = '1'
    else:
        checkBox_SetF07 = ''
    params_dict.update({"checkBox_SetF07":checkBox_SetF07})

    if uiThiaWT3000E.checkBox_SetF08.isChecked():
        checkBox_SetF08 = '1'
    else:
        checkBox_SetF08 = ''
    params_dict.update({"checkBox_SetF08":checkBox_SetF08})

    if uiThiaWT3000E.checkBox_SetF09.isChecked():
        checkBox_SetF09 = '1'
    else:
        checkBox_SetF09 = ''
    params_dict.update({"checkBox_SetF09":checkBox_SetF09})

    if uiThiaWT3000E.checkBox_SetF10.isChecked():
        checkBox_SetF10 = '1'
    else:
        checkBox_SetF10 = ''
    params_dict.update({"checkBox_SetF10":checkBox_SetF10})

    if uiThiaWT3000E.checkBox_SetF11.isChecked():
        checkBox_SetF11 = '1'
    else:
        checkBox_SetF11 = ''
    params_dict.update({"checkBox_SetF11":checkBox_SetF11})

    if uiThiaWT3000E.checkBox_SetF12.isChecked():
        checkBox_SetF12 = '1'
    else:
        checkBox_SetF12 = ''
    params_dict.update({"checkBox_SetF12":checkBox_SetF12})

    if uiThiaWT3000E.checkBox_SetF13.isChecked():
        checkBox_SetF13 = '1'
    else:
        checkBox_SetF13 = ''
    params_dict.update({"checkBox_SetF13":checkBox_SetF13})

    if uiThiaWT3000E.checkBox_SetF14.isChecked():
        checkBox_SetF14 = '1'
    else:
        checkBox_SetF14 = ''
    params_dict.update({"checkBox_SetF14":checkBox_SetF14})

    if uiThiaWT3000E.checkBox_SetF15.isChecked():
        checkBox_SetF15 = '1'
    else:
        checkBox_SetF15 = ''
    params_dict.update({"checkBox_SetF15":checkBox_SetF15})

    if uiThiaWT3000E.checkBox_SetF16.isChecked():
        checkBox_SetF16 = '1'
    else:
        checkBox_SetF16 = ''
    params_dict.update({"checkBox_SetF16":checkBox_SetF16})

    if uiThiaWT3000E.checkBox_SetF17.isChecked():
        checkBox_SetF17 = '1'
    else:
        checkBox_SetF17 = ''
    params_dict.update({"checkBox_SetF17":checkBox_SetF17})

    if uiThiaWT3000E.checkBox_SetF18.isChecked():
        checkBox_SetF18 = '1'
    else:
        checkBox_SetF18 = ''
    params_dict.update({"checkBox_SetF18":checkBox_SetF18})

    if uiThiaWT3000E.checkBox_SetF19.isChecked():
        checkBox_SetF19 = '1'
    else:
        checkBox_SetF19 = ''
    params_dict.update({"checkBox_SetF19":checkBox_SetF19})

    if uiThiaWT3000E.checkBox_SetF20.isChecked():
        checkBox_SetF20 = '1'
    else:
        checkBox_SetF20 = ''
    params_dict.update({"checkBox_SetF20":checkBox_SetF20})

    return params_dict


