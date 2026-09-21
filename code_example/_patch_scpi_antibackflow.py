# -*- coding: utf-8 -*-
"""Patch SCPITestWave.py to wire 防逆流测试 (antibackflow)."""
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "SCPITestWave.py"
text = path.read_text(encoding="utf-8")
orig = text

# 1) import Dialog
needle = "from Dialog_thaiactiveP import Ui_Dialog_thaiactiveP\n"
insert = needle + "from Dialog_thaantibackflow import Ui_Dialog_thaantibackflow\n"
if "from Dialog_thaantibackflow import" not in text:
    text = text.replace(needle, insert, 1)

# 2) Open_Save import
needle = "Open_Save_ThaiActiveP)"
if "Open_Save_ThaiAntiBackflow" not in text:
    text = text.replace(needle, "Open_Save_ThaiActiveP, Open_Save_ThaiAntiBackflow)", 1)

# 3) build plan import
needle = "from utils.active_p_commands import build_active_p_plan\n"
if "build_antibackflow_plan" not in text:
    text = text.replace(
        needle,
        needle + "from utils.antibackflow_commands import build_antibackflow_plan\n",
        1,
    )

# 4) menu list
needle = "'有功调度', '过载能力测试',"
if "'防逆流测试'" not in text.split("projectSecondList")[1][:800]:
    text = text.replace(needle, "'有功调度', '防逆流测试', '过载能力测试',", 1)

# 5) _dewetron_project_ui map (search for '有功调度': uiThaiActiveP)
needle = "        '有功调度': uiThaiActiveP,\n"
if "'防逆流测试': uiThaiAntiBackflow" not in text:
    text = text.replace(needle, needle + "        '防逆流测试': uiThaiAntiBackflow,\n", 1)

# 6) append_count in globals lists — add antibackflow_append_count next to activeP
text = text.replace(
    "activeP_append_count, chonglian_append_count",
    "activeP_append_count, antibackflow_append_count, chonglian_append_count",
)

# Also shorter globals that only have activeP without chonglian
# careful: may over-replace. Check occurrences.
# The pattern above should hit the long global lines.

# 7) _sync_start_end_buttons branch after 有功调度
sync_block = """    elif current == '有功调度':
        if 'activeP_append_count' not in globals():
            activeP_append_count = 0
        count = activeP_append_count
"""
sync_ins = """    elif current == '有功调度':
        if 'activeP_append_count' not in globals():
            activeP_append_count = 0
        count = activeP_append_count
    elif current == '防逆流测试':
        if 'antibackflow_append_count' not in globals():
            antibackflow_append_count = 0
        count = antibackflow_append_count
"""
if "elif current == '防逆流测试':" not in text:
    if sync_block not in text:
        raise SystemExit("sync block not found")
    text = text.replace(sync_block, sync_ins, 1)

# 8) reset count after activeP
reset_block = """    elif current == '有功调度':
        activeP_append_count = 0
        uiThaiActiveP.label_append_count.setText("0")
"""
reset_ins = """    elif current == '有功调度':
        activeP_append_count = 0
        uiThaiActiveP.label_append_count.setText("0")
    elif current == '防逆流测试':
        antibackflow_append_count = 0
        uiThaiAntiBackflow.label_append_count.setText("0")
"""
if "antibackflow_append_count = 0" not in text.split("_reset_current_project_count")[1][:2500]:
    # find first occurrence in reset function - replace once after activeP reset
    idx = text.find("def _reset_current_project_count")
    if idx < 0:
        raise SystemExit("reset fn missing")
    sub = text[idx : idx + 4000]
    if reset_block not in sub:
        raise SystemExit("reset block missing in fn")
    text = text[:idx] + sub.replace(reset_block, reset_ins, 1) + text[idx + 4000 :]

# 9) chooseDetailDialog / addtestDialog — insert after 有功调度 show blocks
show_block = """        elif currentSecond == '有功调度':
            if 'activeP_append_count' not in globals():
                activeP_append_count = 0
            uiThaiActiveP.label_append_count.setText(str(activeP_append_count))
            _sync_start_end_buttons()
            dialog_windowactiveP.show()
"""
show_ins = """        elif currentSecond == '有功调度':
            if 'activeP_append_count' not in globals():
                activeP_append_count = 0
            uiThaiActiveP.label_append_count.setText(str(activeP_append_count))
            _sync_start_end_buttons()
            dialog_windowactiveP.show()
        elif currentSecond == '防逆流测试':
            if 'antibackflow_append_count' not in globals():
                antibackflow_append_count = 0
            uiThaiAntiBackflow.label_append_count.setText(str(antibackflow_append_count))
            _sync_start_end_buttons()
            dialog_windowantibackflow.show()
"""
# replace both occurrences (choose + add)
count_show = text.count(show_block)
if count_show < 1:
    raise SystemExit("show block not found count=%s" % count_show)
text = text.replace(show_block, show_ins)

# 10) Append/Send/Open/Save functions after ActiveP Save
marker = "def SaveFileDialogThaiActiveP():"
idx = text.find(marker)
if idx < 0:
    raise SystemExit("SaveFileDialogThaiActiveP missing")
# find end of SaveFileDialogThaiActiveP — next def after the function body
# Locate Open_Save_ThaiActiveP.Save_File... then next blank+def
end_marker = "    Open_Save_ThaiActiveP.Save_File_ThaiActiveP(kwargs)\n"
end_idx = text.find(end_marker, idx)
if end_idx < 0:
    raise SystemExit("Save ActiveP call missing")
end_idx = end_idx + len(end_marker)

funcs = r'''

def thaiantibackflowAppend():
    global strAddTestFlag, antibackflow_append_count
    if 'antibackflow_append_count' not in globals():
        antibackflow_append_count = 0
    strAddTestFlag = "0" if antibackflow_append_count == 0 else "1"
    mode = "覆盖" if antibackflow_append_count == 0 else "追加"
    ui.textEdit_ReturnMessage.append(f"[防逆流测试] 第{antibackflow_append_count + 1}次{mode}模式，开始生成命令...")
    snapshot = _snapshot_dewetron_append('防逆流测试')
    before_count = antibackflow_append_count
    thaiantibackflowSend()
    if not _normalize_generated_dewetron_rows('防逆流测试', snapshot):
        antibackflow_append_count = before_count
        uiThaiAntiBackflow.label_append_count.setText(str(before_count))
        _sync_start_end_buttons()


def thaiantibackflowSend():
    global uiThaiAntiBackflow, dialog_windowantibackflow, strArrayTest
    global strSettingTestFlag, strArrayTestStep
    global strAddTestFlag, total_save_file, WT_is_checked, test_program
    global project_change, wt_config_nums
    global uiThiaWT3000E, uiThiaWT1800, uiThiaWT1806E, uiThiaWT5000
    global command_save_file_path, wt_type
    global antibackflow_append_count
    if 'antibackflow_append_count' not in globals():
        antibackflow_append_count = 0

    wt_config_dict = {}
    if strAddTestFlag == "0" or (strAddTestFlag == '1' and project_change == '1'):
        if uiThaiAntiBackflow.radioButton_S2_WT3000.isChecked():
            wt_config_dict = WT3000E_params_config(_PageWidgetFinder(uiThaiAntiBackflow._wtStacked.widget(0)))
        elif uiThaiAntiBackflow.radioButton_S2_WT1800.isChecked():
            wt_config_dict = WT1800_params_config(_PageWidgetFinder(uiThaiAntiBackflow._wtStacked.widget(1)))
        elif uiThaiAntiBackflow.radioButton_S2_WT1806E.isChecked():
            wt_config_dict = WT1806E_params_config(_PageWidgetFinder(uiThaiAntiBackflow._wtStacked.widget(2)))
        elif uiThaiAntiBackflow.radioButton_S2_WT5000.isChecked():
            wt_config_dict = WT5000_params_config(_PageWidgetFinder(uiThaiAntiBackflow._wtStacked.widget(3)))

    def _dc_iv_bridge(vmp, imp, voc, isc, pf, dc_num):
        from utils.dc_brand_cmd_guard import resolve_dc_iv_with_bridge
        return resolve_dc_iv_with_bridge(
            vmp, imp, voc, isc, pf, dc_num,
            get_iv_fn=DCGetIVValueFunction,
            per_dc_factor=per_dc_factor,
            command_list_dc=command_list_DC,
        )

    existing = [] if strAddTestFlag == "0" else list(strArrayTest)
    plan = build_antibackflow_plan(
        uiThaiAntiBackflow,
        wt_config_dict=wt_config_dict,
        str_add_flag=strAddTestFlag,
        project_change=project_change,
        existing_commands=existing,
        dc_iv_resolver=_dc_iv_bridge,
    )

    if not plan["ok"]:
        QMessageBox.information(None, "错误提示信息", plan["error"], QMessageBox.Ok, QMessageBox.Ok)
        return

    strArrayTest = plan["commands"]
    strArrayTestStep = plan["steps"]
    if plan["wt_is_checked"] == "1":
        WT_is_checked = "1"
    if plan["wt_type"]:
        wt_type = plan["wt_type"]
    if strAddTestFlag == "0":
        test_program = list(plan["test_program"])
    else:
        test_program.extend(plan["test_program"])
    if strAddTestFlag == '1' and project_change == '1':
        wt_config_nums = wt_config_nums + 1

    if plan["dc_errors"]:
        all_errors = "\n".join(["%d. %s" % (i + 1, msg) for i, msg in enumerate(plan["dc_errors"])])
        QMessageBox.information(None, "错误提示信息", all_errors, QMessageBox.Ok, QMessageBox.Ok)
    else:
        if strAddTestFlag == "0":
            total_save_file = 0
        file_names = plan.get("file_names") or []
        if plan.get("wt_is_checked") == "1" and file_names:
            file_list_text = ",".join(file_names)
            stop_str = ""
            if plan.get("wt_continuous"):
                dwell_01s = int(plan.get("dwell_01s") or 0)
                stop_sec = int(round(dwell_01s / 10.0 + 90))
                if stop_sec < 20:
                    stop_sec = 20
                stop_str = _seconds_to_stoptime_str(stop_sec)
            for cfg_row in strArrayTest:
                if cfg_row and cfg_row[0] == "Upper_WT_Config" and isinstance(cfg_row[4], dict):
                    cfg_row[4]["textEdit_FileNameList"] = file_list_text
                    if stop_str:
                        cfg_row[4]["textEdit_StopTime"] = stop_str
                    if cfg_row[4].get("comboBox_AutoSave", 0) == 0:
                        cfg_row[4]["comboBox_AutoSave"] = 1
                    break
            try:
                for page_idx in range(uiThaiAntiBackflow._wtStacked.count()):
                    page = uiThaiAntiBackflow._wtStacked.widget(page_idx)
                    te = page.findChild(QtWidgets.QTextEdit, "textEdit_FileNameList")
                    if te is not None:
                        te.setPlainText(file_list_text)
                    if stop_str:
                        st = page.findChild(QtWidgets.QTextEdit, "textEdit_StopTime")
                        if st is not None:
                            st.setPlainText(stop_str)
                    combo = page.findChild(QtWidgets.QComboBox, "comboBox_AutoSave")
                    if combo is not None and combo.currentIndex() == 0:
                        combo.setCurrentIndex(1)
            except Exception as e:
                _append_debug_log(f"[antibackflow] update WT FileNameList failed: {e}")
            wt_rounds = int(plan.get("wt_rounds") or len(file_names) or 0)
            total_save_file = total_save_file + wt_rounds
            if plan.get("wt_continuous"):
                ui.textEdit_ReturnMessage.append(
                    "[防逆流测试] 一条线连续录，单文件 %s，StopTime %s"
                    % (file_names[0], stop_str or "-")
                )
            else:
                ui.textEdit_ReturnMessage.append(
                    f"[防逆流测试] 工况共 {len(file_names)} 段逐点存盘"
                )

        strtimenow = now_to_datenow()
        if strAddTestFlag == "0":
            try:
                logger.info(strtimenow + "    设定实验内容完成")
            except NameError:
                pass
            print(strtimenow + "    设定实验内容完成")
        else:
            try:
                logger.info(strtimenow + "    累加设定实验内容完成")
            except NameError:
                pass
            print(strtimenow + "    累加设定实验内容完成")
            project_change = '0'
        strSettingTestFlag = "1"
        reset_wt_automation_state()
        now_time = time.strftime(r"%Y_%m_%d_%H", time.localtime(time.time()))
        commands_file_name = f'antibackflow_commands{now_time}.csv'
        directory1 = [f"{command_save_file_path}/command_data/{commands_file_name}"]
        if directory1[0] == '':
            print('请选择一个文件')
        else:
            out = open(directory1[0], 'w+', newline='')
            csv_write = csv.writer(out, dialect="excel")
            for i in range(len(strArrayTest)):
                csv_write.writerow(strArrayTest[i])
            out.close()

        dialog_windowantibackflow.close()

    if 'antibackflow_append_count' not in globals():
        antibackflow_append_count = 0
    antibackflow_append_count += 1
    uiThaiAntiBackflow.label_append_count.setText(str(antibackflow_append_count))
    _sync_start_end_buttons()
    ui.textEdit_ReturnMessage.append(
        f"[防逆流测试] 追加完成，当前计数: {antibackflow_append_count}，开始/结束试验按钮已启用"
    )


def OpenFileDialogThaiAntiBackflow():
    global dialog_windowantibackflow, uiThaiAntiBackflow
    global uiThiaWT3000E, uiThiaWT1800, uiThiaWT1806E, uiThiaWT5000
    kwargs = {
        'dialog_windowantibackflow': dialog_windowantibackflow,
        'uiThaiAntiBackflow': uiThaiAntiBackflow,
        'uiThiaWT3000E': uiThiaWT3000E,
        'uiThiaWT1800': uiThiaWT1800,
        'uiThiaWT1806E': uiThiaWT1806E,
        'uiThiaWT5000': uiThiaWT5000,
    }
    Open_Save_ThaiAntiBackflow.Open_File_ThaiAntiBackflow(kwargs)


def SaveFileDialogThaiAntiBackflow():
    global dialog_windowantibackflow, uiThaiAntiBackflow
    global uiThiaWT3000E, uiThiaWT1800, uiThiaWT1806E, uiThiaWT5000
    kwargs = {
        'dialog_windowantibackflow': dialog_windowantibackflow,
        'uiThaiAntiBackflow': uiThaiAntiBackflow,
        'uiThiaWT3000E': uiThiaWT3000E,
        'uiThiaWT1800': uiThiaWT1800,
        'uiThiaWT1806E': uiThiaWT1806E,
        'uiThiaWT5000': uiThiaWT5000,
    }
    Open_Save_ThaiAntiBackflow.Save_File_ThaiAntiBackflow(kwargs)

'''

if "def thaiantibackflowAppend():" not in text:
    text = text[:end_idx] + funcs + text[end_idx:]

# 11) setup_windows unpack
needle = '            uiThaiActiveP = setup_windows["uiThaiActiveP"]\n'
if 'uiThaiAntiBackflow = setup_windows["uiThaiAntiBackflow"]' not in text:
    text = text.replace(
        needle,
        needle
        + '            dialog_windowantibackflow = setup_windows["dialog_windowantibackflow"]\n'
        + '            uiThaiAntiBackflow = setup_windows["uiThaiAntiBackflow"]\n',
        1,
    )

# 12) _auto_test_dialogs map
needle = "                '有功调度': (dialog_windowactiveP, uiThaiActiveP),\n"
if "'防逆流测试': (dialog_windowantibackflow" not in text:
    text = text.replace(
        needle,
        needle + "                '防逆流测试': (dialog_windowantibackflow, uiThaiAntiBackflow),\n",
        1,
    )

# 13) button wiring after activeP
wire = '''            _safe_click(uiThaiActiveP, "pushButton_SaveSettingFile", SaveFileDialogThaiActiveP)

            # overloads
'''
wire_ins = '''            _safe_click(uiThaiActiveP, "pushButton_SaveSettingFile", SaveFileDialogThaiActiveP)

            # 防逆流测试（UNE 217001）
            _when_ui_ready(uiThaiAntiBackflow, lambda u: u.pushButton_Send.clicked.connect(thaiantibackflowSend))
            _safe_click(uiThaiAntiBackflow, "pushButton_TestAppend", thaiantibackflowAppend)

            def reset_antibackflow_count():
                global antibackflow_append_count
                antibackflow_append_count = 0
                uiThaiAntiBackflow.label_append_count.setText("0")
                _reset_dewetron_append_fingerprint('防逆流测试')
                _sync_start_end_buttons()
                ui.textEdit_ReturnMessage.append("[防逆流测试] 计数器已重置为0")
            _safe_click(uiThaiAntiBackflow, "pushButton_ResetCount", reset_antibackflow_count)
            _safe_click(uiThaiAntiBackflow, "pushButton_ReadSettingFile", OpenFileDialogThaiAntiBackflow)
            _safe_click(uiThaiAntiBackflow, "pushButton_SaveSettingFile", SaveFileDialogThaiAntiBackflow)

            # overloads
'''
if "thaiantibackflowAppend" not in text.split("# overloads")[0][-800:]:
    if wire not in text:
        raise SystemExit("wire marker missing")
    text = text.replace(wire, wire_ins, 1)

# 14) init antibackflow_append_count near activeP init blocks — add to the short global inits
# After: if 'activeP_append_count' not in globals():\n        activeP_append_count = 0
# in chooseDetailDialog - already handled by show branch.

# Also need global declarations that list activeP_append_count without antibackflow
# We already replaced "activeP_append_count, chonglian_append_count" globally.

# Fix shorter globals: "activeP_append_count\n" alone in some functions
for needle in [
    "    global fixedpf_append_count, reactiveQcap_append_count, fixedQ_append_count, reactiveQin_append_count, reactiveQacc_append_count, activeP_append_count\n",
]:
    if needle in text and "antibackflow_append_count\n" not in needle:
        text = text.replace(
            needle,
            needle.replace(
                "activeP_append_count\n",
                "activeP_append_count, antibackflow_append_count\n",
            ),
        )

if text == orig:
    raise SystemExit("no changes made")
path.write_text(text, encoding="utf-8")
print("patched", path, "delta", len(text) - len(orig))
