# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from config_manager.thaifixedPF_config_manager import ThaiFixedPF_ConfigManager


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
