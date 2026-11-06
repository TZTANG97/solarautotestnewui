# -*- coding: utf-8 -*-
"""One-shot patch: thaifixedpfSend measure/shutdown to ASYNC / split, no json."""
from pathlib import Path

path = Path(r"E:\solarautotestnewui\SCPITestWave.py")
text = path.read_text(encoding="utf-8")

old_names = '''        file_names = []
        for s in range(4, 9):
            if getattr(uiThaiFixedPF, f"checkBox_S{s}").isChecked():
                name = getattr(uiThaiFixedPF, f"lE_S{s}_filename").toPlainText().strip()
                if name:
                    file_names.append(name)
        if file_names:'''

new_names = '''        from utils.wt_recording_mode import (
            combo_index_to_mode, fixed_pf_recommended_filenames, apply_filename_list_to_wt_pages,
        )
        _pf_percents = []
        for s in range(4, 9):
            if getattr(uiThaiFixedPF, f"checkBox_S{s}").isChecked():
                raw = getattr(uiThaiFixedPF, f"textEdit_S1_DC1_PF_{s}").toPlainText().strip()
                try:
                    _pf_percents.append(float(raw))
                except ValueError:
                    _pf_percents.append(float(s))
        _rec_mode = combo_index_to_mode(uiThaiFixedPF.comboBox_S3_record_mode.currentIndex())
        file_names = fixed_pf_recommended_filenames(_pf_percents, _rec_mode)
        apply_filename_list_to_wt_pages(uiThaiFixedPF._wtStacked, file_names)
        if file_names:'''

if old_names not in text:
    raise SystemExit("file_names block not found")
text = text.replace(old_names, new_names, 1)

start = text.find("    # 共享时间参数（来自 Step3 测量设置）")
end = text.find("    # step14\n    S14_time = get_time_dynamic(\"S14\",1)")
if start < 0 or end < 0 or end <= start:
    raise SystemExit(f"markers not found start={start} end={end}")

new_mid = r'''    from utils.wt_recording_mode import MODE_CONTINUOUS, combo_index_to_mode
    from utils.matrix_recording_commands import maybe_async_start, maybe_async_end, get_record_mode

    f_collect = get_time("textEdit_S3_TIME_2", "comboBox_S3_TIME_2")
    f_wait = get_time("textEdit_S3_TIME_3", "comboBox_S3_TIME_3")
    record_mode = get_record_mode(uiThaiFixedPF)
    wt_continuous = record_mode == MODE_CONTINUOUS
    enabled_steps = [s for s in range(4, 9) if getattr(uiThaiFixedPF, f"checkBox_S{s}").isChecked()]
    wt_on = bool(uiThaiFixedPF.checkBox_S2.isChecked() and (not _fixedpf_dew_mode))
    if wt_on and enabled_steps:
        if wt_continuous:
            total_save_file = total_save_file + 1
        else:
            total_save_file = total_save_file + len(enabled_steps)

    dc_params = {}
    try:
        if uiThaiFixedPF.checkBox_S1_DC1.isChecked():
            dc_params[1] = (S1DC1Vmp, S1DC1Imp, S1DC1Voc, S1DC1Isc)
        if uiThaiFixedPF.checkBox_S1_DC2.isChecked():
            dc_params[2] = (S1DC2Vmp, S1DC2Imp, S1DC2Voc, S1DC2Isc)
        if uiThaiFixedPF.checkBox_S1_DC3.isChecked():
            dc_params[3] = (S1DC3Vmp, S1DC3Imp, S1DC3Voc, S1DC3Isc)
        if uiThaiFixedPF.checkBox_S1_DC4.isChecked():
            dc_params[4] = (S1DC4Vmp, S1DC4Imp, S1DC4Voc, S1DC4Isc)
    except NameError:
        dc_params = {}

    err_map = {1: ("1", "2"), 2: ("3", "4"), 3: ("5", "6"), 4: ("7", "8")}
    point_index = 0
    for s in enabled_steps:
        strArrayTestStepSingle = []
        pf_text = getattr(uiThaiFixedPF, f"textEdit_S1_DC1_PF_{s}").toPlainText()
        for dc_n, params in dc_params.items():
            step_dc = getattr(uiThaiFixedPF, f"checkBox_S1_DC{dc_n}_{s}")
            if not step_dc.isChecked():
                continue
            a = DCGetIVValueFunction(params[0], params[1], params[2], params[3], pf_text, dc_n - 1)
            if a == "1":
                strShowErrorMessageBoxFlag = err_map[dc_n][0]
            elif a == "2":
                strShowErrorMessageBoxFlag = err_map[dc_n][1]
            elif a == "3":
                strShowErrorMessageBoxFlag = "brand"
            else:
                strArrayTestStepSingle = DC_IV_Commands_Set(strArrayTestStepSingle, a, f"DC{dc_n}")

        if wt_on and wt_continuous and point_index == 0:
            row = ["" for _ in range(10)]
            row[0], row[1], row[2], row[6] = "AC", "query", "*IDN?", "ASYNC_START"
            strArrayTest.append(row)
            strArrayTestStepSingle.append(row)

        row = ["" for _ in range(10)]
        row[0], row[1], row[2] = "AC", "query", "*IDN?"
        row[9] = f_wait
        strArrayTest.append(row)
        strArrayTestStepSingle.append(row)

        row = ["" for _ in range(10)]
        row[0], row[1], row[2] = "AC", "query", "*IDN?"
        if wt_continuous:
            row[9] = f_collect
        else:
            row[7] = f_collect
        strArrayTest.append(row)
        strArrayTestStepSingle.append(row)

        if not wt_continuous:
            row = ["" for _ in range(10)]
            row[0], row[1], row[2] = "AC", "query", "*IDN?"
            row[8] = 10
            strArrayTest.append(row)
            strArrayTestStepSingle.append(row)

        strArrayTestStep.append(strArrayTestStepSingle)
        point_index += 1

    if wt_on and wt_continuous and enabled_steps:
        row = ["" for _ in range(10)]
        row[0], row[1], row[2], row[6] = "AC", "query", "*IDN?", "WAIT_END"
        strArrayTest.append(row)

    # step14
'''

text = text[:start] + new_mid + text[end + len("    # step14\n    S14_time = get_time_dynamic(\"S14\",1)"):]

old_json = '''        # json
        
        if uiThaiFixedPF.checkBox_S14_2.isChecked():
            json_1 = uiThaiFixedPF.cB_S14_json_14.currentText()
            strArraySingle = ["" for _ in range(10)]
            strArraySingle[0] = "WT"
            strArraySingle[1] = json_1
            strArraySingle[7] = S14_time
            strArrayTest.append(strArraySingle)
            strArrayTestStepSingle.append(strArraySingle)
            strArrayTestStep.append(strArrayTestStepSingle)
'''
if old_json not in text:
    raise SystemExit("shutdown json block not found")
text = text.replace(old_json, "", 1)

old_wt_change = '''def thai_fixedpf_wt_change():
    global uiThaiFixedPF
    if uiThaiFixedPF.radioButton_S2_WT3000.isChecked():
        wt_type = "WT3000"
    elif uiThaiFixedPF.radioButton_S2_WT1800.isChecked():
        wt_type = "WT1800"
    elif uiThaiFixedPF.radioButton_S2_WT1806E.isChecked():
        wt_type = "WT1806E"
    elif uiThaiFixedPF.radioButton_S2_WT5000.isChecked():
        wt_type = "WT5000"
    else:
        wt_type = "WT3000"
    uiThaiFixedPF.cB_S14_json_14.clear()
    for s in range(4, 9):
        for i in range(1, 4):
            getattr(uiThaiFixedPF, f'cB_S{s}_json_{i}').clear()

    uiThaiFixedPF.cB_S14_json_14.addItems(list_json_files(wt_type))
    uiThaiFixedPF.cB_S14_json_14.setCurrentIndex(0)
    for s in range(4, 9):
        for i in range(1, 4):
            combo = getattr(uiThaiFixedPF, f'cB_S{s}_json_{i}')
            combo.addItems(list_json_files(wt_type))
            combo.setCurrentIndex(0)

def thaifixedpf_ui_init():
    global uiThaiFixedPF
    global config
    thai_fixedpf_wt_change()
    wt_file_save_path = config['PATH']['wt_file_save_path']
    if hasattr(uiThaiFixedPF, "_wtStacked"):
        for i in range(uiThaiFixedPF._wtStacked.count()):
            page = uiThaiFixedPF._wtStacked.widget(i)
            te = page.findChild(QtWidgets.QTextEdit, "textEdit_SavePath")
            if te is not None:
                te.setPlainText(wt_file_save_path)
'''

new_wt_change = '''def thai_fixedpf_wt_change():
    global uiThaiFixedPF
    if not hasattr(uiThaiFixedPF, "_wtStacked") or uiThaiFixedPF._radio_group is None:
        return
    btn = uiThaiFixedPF._radio_group.checkedButton()
    if btn is not None:
        uiThaiFixedPF._wtStacked.setCurrentIndex(uiThaiFixedPF._radio_group.id(btn))

def thaifixedpf_ui_init():
    global uiThaiFixedPF
    global config
    wt_file_save_path = config['PATH']['wt_file_save_path']
    if hasattr(uiThaiFixedPF, "_wtStacked"):
        for i in range(uiThaiFixedPF._wtStacked.count()):
            page = uiThaiFixedPF._wtStacked.widget(i)
            te = page.findChild(QtWidgets.QTextEdit, "textEdit_SavePath")
            if te is not None:
                te.setPlainText(wt_file_save_path)
'''

if old_wt_change not in text:
    raise SystemExit("thai_fixedpf_wt_change block not found")
text = text.replace(old_wt_change, new_wt_change, 1)

path.write_text(text, encoding="utf-8")
print("patched", path)
