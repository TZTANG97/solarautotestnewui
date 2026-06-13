# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from config_manager.thaifixedPF_config_manager import ThaiFixedPF_ConfigManager


def _refresh_json_combos(uiThaiFixedPF):
    """加载配置后刷新所有 JSON 下拉框（根据当前 WT 型号），保留已保存的选择"""
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

    # 延迟导入避免循环依赖
    from func import list_json_files

    def _reload_combo(combo, saved_text):
        """清空并重新加载 combo，尝试恢复保存的选择"""
        combo.clear()
        items = list_json_files(wt_type)
        combo.addItems(items)
        if saved_text:
            idx = combo.findText(saved_text)
            combo.setCurrentIndex(idx if idx >= 0 else 0)
        else:
            combo.setCurrentIndex(0)

    # 刷新前保存当前选择
    saved_wt_json = uiThaiFixedPF.cB_wt_json.currentText()
    saved_s14_json = uiThaiFixedPF.cB_S14_json_14.currentText()
    saved_s_json = {}
    for s in range(4, 9):
        for i in range(1, 4):
            saved_s_json[f'cB_S{s}_json_{i}'] = getattr(uiThaiFixedPF, f'cB_S{s}_json_{i}').currentText()

    _reload_combo(uiThaiFixedPF.cB_wt_json, saved_wt_json)
    _reload_combo(uiThaiFixedPF.cB_S14_json_14, saved_s14_json)
    for s in range(4, 9):
        for i in range(1, 4):
            combo = getattr(uiThaiFixedPF, f'cB_S{s}_json_{i}')
            _reload_combo(combo, saved_s_json.get(f'cB_S{s}_json_{i}', ''))


def Save_File_ThaiFixedPF(kwargs):
    """保存固定PF=1配置（委托给 ConfigManager）"""
    uiThaiFixedPF = kwargs['uiThaiFixedPF']
    config_manager = ThaiFixedPF_ConfigManager(uiThaiFixedPF)
    config_manager.save_config()


def Open_File_ThaiFixedPF(kwargs):
    """读取固定PF=1配置（委托给 ConfigManager）"""
    uiThaiFixedPF = kwargs['uiThaiFixedPF']
    config_manager = ThaiFixedPF_ConfigManager(uiThaiFixedPF)
    config_manager.load_config()
    _refresh_json_combos(uiThaiFixedPF)
