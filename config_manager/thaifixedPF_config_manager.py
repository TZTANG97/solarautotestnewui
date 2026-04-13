from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QDialog, QFileDialog, QMessageBox, 
    QCheckBox, QComboBox, QTextEdit
)
from PyQt5.QtCore import QSettings
import os
import sys

class ThaiFixedPF_ConfigManager:
    """泰国固定PF配置管理器"""
    
    # 配置结构定义：步骤 -> (控件名称, 控件类型, 设置键名)
    CONFIG_STRUCTURE = {
        "UI_State": [
            ('cB_wt_json', 'combobox_text', 'wt_json'),
            ('cB_S3_json_1', 'combobox_text', 'S3_json_1'),
            ('cB_S3_json_2', 'combobox_text', 'S3_json_2'),
            ('cB_S3_json_3', 'combobox_text', 'S3_json_3'),
            ('cB_S4_json_1', 'combobox_text', 'S4_json_1'),
            ('cB_S4_json_2', 'combobox_text', 'S4_json_2'),
            ('cB_S4_json_3', 'combobox_text', 'S4_json_3'),
            ('cB_S5_json_1', 'combobox_text', 'S5_json_1'),
            ('cB_S5_json_2', 'combobox_text', 'S5_json_2'),
            ('cB_S5_json_3', 'combobox_text', 'S5_json_3'),
            ('cB_S6_json_1', 'combobox_text', 'S6_json_1'),
            ('cB_S6_json_2', 'combobox_text', 'S6_json_2'),
            ('cB_S6_json_3', 'combobox_text', 'S6_json_3'),
            ('cB_S7_json_1', 'combobox_text', 'S7_json_1'),
            ('cB_S7_json_2', 'combobox_text', 'S7_json_2'),
            ('cB_S7_json_3', 'combobox_text', 'S7_json_3'),
            ('cB_S14_json_14', 'combobox_text', 'S14_json_14'),
            
        ],

        "Step1": [
            ('checkBox_S1', 'checkbox', 'S1_Enabled'),
            ('comboBox_S1_AC', 'combobox', 'S1_AC_Type'),
            ('textEdit_S1_AC_VOLT', 'textedit', 'S1_AC_Voltage1'),
            ('textEdit_S1_AC_VOLT_2', 'textedit', 'S1_AC_Voltage2'),
            ('textEdit_S1_AC_VOLT_3', 'textedit', 'S1_AC_Voltage3'),
            ('textEdit_S1_AC_FR', 'textedit', 'S1_AC_Frequency'),
            ('comboBox_S1_AC_2', 'combobox', 'S1_AC_Mode'),
            ('checkBox_S1_DC1', 'checkbox', 'S1_DC1_Enabled'),
            ('comboBox_S1_DC1', 'combobox', 'S1_DC1_Type'),
            ('textEdit_S1_DC1_VOLT', 'textedit', 'S1_DC1_Voltage'),
            ('textEdit_S1_DC1_CURR', 'textedit', 'S1_DC1_Current'),
            ('textEdit_S1_DC1_Voc', 'textedit', 'S1_DC1_Voc'),
            ('textEdit_S1_DC1_Isc', 'textedit', 'S1_DC1_Isc'),
            ('textEdit_S1_DC1_PF', 'textedit', 'S1_DC1_PF'),
            ('checkBox_S1_DC2', 'checkbox', 'S1_DC2_Enabled'),
            ('comboBox_S1_DC2', 'combobox', 'S1_DC2_Type'),
            ('textEdit_S1_DC2_VOLT', 'textedit', 'S1_DC2_Voltage'),
            ('textEdit_S1_DC2_CURR', 'textedit', 'S1_DC2_Current'),
            ('textEdit_S1_DC2_Voc', 'textedit', 'S1_DC2_Voc'),
            ('textEdit_S1_DC2_Isc', 'textedit', 'S1_DC2_Isc'),
            ('textEdit_S1_DC2_PF', 'textedit', 'S1_DC2_PF'),
            ('checkBox_S1_DC3', 'checkbox', 'S1_DC3_Enabled'),
            ('comboBox_S1_DC3', 'combobox', 'S1_DC3_Type'),
            ('textEdit_S1_DC3_VOLT', 'textedit', 'S1_DC3_Voltage'),
            ('textEdit_S1_DC3_CURR', 'textedit', 'S1_DC3_Current'),
            ('textEdit_S1_DC3_Voc', 'textedit', 'S1_DC3_Voc'),
            ('textEdit_S1_DC3_Isc', 'textedit', 'S1_DC3_Isc'),
            ('textEdit_S1_DC3_PF', 'textedit', 'S1_DC3_PF'),
            ('checkBox_S1_DC4', 'checkbox', 'S1_DC4_Enabled'),
            ('comboBox_S1_DC4', 'combobox', 'S1_DC4_Type'),
            ('textEdit_S1_DC4_VOLT', 'textedit', 'S1_DC4_Voltage'),
            ('textEdit_S1_DC4_CURR', 'textedit', 'S1_DC4_Current'),
            ('textEdit_S1_DC4_Voc', 'textedit', 'S1_DC4_Voc'),
            ('textEdit_S1_DC4_Isc', 'textedit', 'S1_DC4_Isc'),
            ('textEdit_S1_DC4_PF', 'textedit', 'S1_DC4_PF'),
            ('textEdit_S1_ACWaitTIME', 'textedit', 'S1_ACWaitTime'),
            ('comboBox_S1_ACWaitTIME', 'combobox', 'S1_ACWaitTime_Unit'),
            ('textEdit_S1_TIME', 'textedit', 'S1_Duration'),
            ('comboBox_S1_TIME', 'combobox', 'S1_Duration_Unit'),
        ],
        "Step2": [
            ('checkBox_S2', 'checkbox', 'S2_Enabled'),
            ('lE_wt_save_path','lineedit','S2_Path'),
        ],
        "Step3": [
            ('checkBox_S3', 'checkbox', 'S3_Enabled'),
            ('checkBox_S1_DC1_3', 'checkbox', 'S3_DC1_Enabled'),
            ('checkBox_S1_DC2_3', 'checkbox', 'S3_DC2_Enabled'),
            ('checkBox_S1_DC3_3', 'checkbox', 'S3_DC3_Enabled'),
            ('checkBox_S1_DC4_3', 'checkbox', 'S3_DC4_Enabled'),
            ('textEdit_S1_DC1_PF_3', 'textedit', 'S3_PF'),

            ('lE_S3_filename', 'lineedit', 'S3_Filename'),  # 新增
            ('lE_S3_1', 'lineedit', 'S3_time_1'),
            ('lE_S3_2', 'lineedit', 'S3_time_2'),
            ('lE_S3_3', 'lineedit', 'S3_time_3'),
            ('lE_S3_4', 'lineedit', 'S3_time_4'),

            ('cB_S3_unit_1', 'combobox', 'S3_time_Unit_1'),
            ('cB_S3_unit_2', 'combobox', 'S3_time_Unit_2'),
            ('cB_S3_unit_3', 'combobox', 'S3_time_Unit_3'),
            ('cB_S3_unit_4', 'combobox', 'S3_time_Unit_4'),
            
        ],
        "Step4": [
            ('checkBox_S4', 'checkbox', 'S4_Enabled'),
            ('checkBox_S1_DC1_4', 'checkbox', 'S4_DC1_Enabled'),
            ('checkBox_S1_DC2_4', 'checkbox', 'S4_DC2_Enabled'),
            ('checkBox_S1_DC3_4', 'checkbox', 'S4_DC3_Enabled'),
            ('checkBox_S1_DC4_4', 'checkbox', 'S4_DC4_Enabled'),
            ('textEdit_S1_DC1_PF_4', 'textedit', 'S4_PF'),

            ('lE_S4_filename', 'lineedit', 'S4_Filename'),  # 新增
            ('lE_S4_1', 'lineedit', 'S4_time_1'),
            ('lE_S4_2', 'lineedit', 'S4_time_2'),
            ('lE_S4_3', 'lineedit', 'S4_time_3'),
            ('lE_S4_4', 'lineedit', 'S4_time_4'),

            ('cB_S4_unit_1', 'combobox', 'S4_time_Unit_1'),
            ('cB_S4_unit_2', 'combobox', 'S4_time_Unit_2'),
            ('cB_S4_unit_3', 'combobox', 'S4_time_Unit_3'),
            ('cB_S4_unit_4', 'combobox', 'S4_time_Unit_4'),
        ],
        "Step5": [
            ('checkBox_S5', 'checkbox', 'S5_Enabled'),
            ('checkBox_S1_DC1_5', 'checkbox', 'S5_DC1_Enabled'),
            ('checkBox_S1_DC2_5', 'checkbox', 'S5_DC2_Enabled'),
            ('checkBox_S1_DC3_5', 'checkbox', 'S5_DC3_Enabled'),
            ('checkBox_S1_DC4_5', 'checkbox', 'S5_DC4_Enabled'),
            ('textEdit_S1_DC1_PF_5', 'textedit', 'S5_PF'),

            ('lE_S5_filename', 'lineedit', 'S5_Filename'),  # 新增
            ('lE_S5_1', 'lineedit', 'S5_time_1'),
            ('lE_S5_2', 'lineedit', 'S5_time_2'),
            ('lE_S5_3', 'lineedit', 'S5_time_3'),
            ('lE_S5_4', 'lineedit', 'S5_time_4'),

            ('cB_S5_unit_1', 'combobox', 'S5_time_Unit_1'),
            ('cB_S5_unit_2', 'combobox', 'S5_time_Unit_2'),
            ('cB_S5_unit_3', 'combobox', 'S5_time_Unit_3'),
            ('cB_S5_unit_4', 'combobox', 'S5_time_Unit_4'),
        ],
        "Step6": [
            ('checkBox_S6', 'checkbox', 'S6_Enabled'),
            ('checkBox_S1_DC1_6', 'checkbox', 'S6_DC1_Enabled'),
            ('checkBox_S1_DC2_6', 'checkbox', 'S6_DC2_Enabled'),
            ('checkBox_S1_DC3_6', 'checkbox', 'S6_DC3_Enabled'),
            ('checkBox_S1_DC4_6', 'checkbox', 'S6_DC4_Enabled'),
            ('textEdit_S1_DC1_PF_6', 'textedit', 'S6_PF'),

            ('lE_S6_filename', 'lineedit', 'S6_Filename'),  # 新增
            ('lE_S6_1', 'lineedit', 'S6_time_1'),
            ('lE_S6_2', 'lineedit', 'S6_time_2'),
            ('lE_S6_3', 'lineedit', 'S6_time_3'),
            ('lE_S6_4', 'lineedit', 'S6_time_4'),

            ('cB_S6_unit_1', 'combobox', 'S6_time_Unit_1'),
            ('cB_S6_unit_2', 'combobox', 'S6_time_Unit_2'),
            ('cB_S6_unit_3', 'combobox', 'S6_time_Unit_3'),
            ('cB_S6_unit_4', 'combobox', 'S6_time_Unit_4'),
        ],
        "Step7": [
            ('checkBox_S7', 'checkbox', 'S7_Enabled'),
            ('checkBox_S1_DC1_7', 'checkbox', 'S7_DC1_Enabled'),
            ('checkBox_S1_DC2_7', 'checkbox', 'S7_DC2_Enabled'),
            ('checkBox_S1_DC3_7', 'checkbox', 'S7_DC3_Enabled'),
            ('checkBox_S1_DC4_7', 'checkbox', 'S7_DC4_Enabled'),
            ('textEdit_S1_DC1_PF_7', 'textedit', 'S7_PF'),
            
            ('lE_S7_filename', 'lineedit', 'S7_Filename'),  # 新增
            ('lE_S7_1', 'lineedit', 'S7_time_1'),
            ('lE_S7_2', 'lineedit', 'S7_time_2'),
            ('lE_S7_3', 'lineedit', 'S7_time_3'),
            ('lE_S7_4', 'lineedit', 'S7_time_4'),

            ('cB_S7_unit_1', 'combobox', 'S7_time_Unit_1'),
            ('cB_S7_unit_2', 'combobox', 'S7_time_Unit_2'),
            ('cB_S7_unit_3', 'combobox', 'S7_time_Unit_3'),
            ('cB_S7_unit_4', 'combobox', 'S7_time_Unit_4'),
        ],
        # "Step8": [
        #     ('checkBox_S8', 'checkbox', 'S8_Enabled'),
        #     ('checkBox_S1_DC1_8', 'checkbox', 'S8_DC1_Enabled'),
        #     ('checkBox_S1_DC2_8', 'checkbox', 'S8_DC2_Enabled'),
        #     ('checkBox_S1_DC3_8', 'checkbox', 'S8_DC3_Enabled'),
        #     ('checkBox_S1_DC4_8', 'checkbox', 'S8_DC4_Enabled'),
        #     ('textEdit_S1_DC1_PF_8', 'textedit', 'S8_PF'),
        #     ('lE_S8_filename', 'lineedit', 'S8_Filename'),  # 新增
        # ],
        # "Step9": [
        #     ('checkBox_S9', 'checkbox', 'S9_Enabled'),
        #     ('checkBox_S1_DC1_9', 'checkbox', 'S9_DC1_Enabled'),
        #     ('checkBox_S1_DC2_9', 'checkbox', 'S9_DC2_Enabled'),
        #     ('checkBox_S1_DC3_9', 'checkbox', 'S9_DC3_Enabled'),
        #     ('checkBox_S1_DC4_9', 'checkbox', 'S9_DC4_Enabled'),
        #     ('textEdit_S1_DC1_PF_9', 'textedit', 'S9_PF'),
        #     ('lE_S9_filename', 'lineedit', 'S9_Filename'),  # 新增
        # ],
        # "Step10": [
        #     ('checkBox_S10', 'checkbox', 'S10_Enabled'),
        #     ('checkBox_S1_DC1_10', 'checkbox', 'S10_DC1_Enabled'),
        #     ('checkBox_S1_DC2_10', 'checkbox', 'S10_DC2_Enabled'),
        #     ('checkBox_S1_DC3_10', 'checkbox', 'S10_DC3_Enabled'),
        #     ('checkBox_S1_DC4_10', 'checkbox', 'S10_DC4_Enabled'),
        #     ('textEdit_S1_DC1_PF_10', 'textedit', 'S10_PF'),
        #     ('lE_S10_filename', 'lineedit', 'S10_Filename'),  # 新增
        # ],
        # "Step11": [
        #     ('checkBox_S11', 'checkbox', 'S11_Enabled'),
        #     ('checkBox_S1_DC1_11', 'checkbox', 'S11_DC1_Enabled'),
        #     ('checkBox_S1_DC2_11', 'checkbox', 'S11_DC2_Enabled'),
        #     ('checkBox_S1_DC3_11', 'checkbox', 'S11_DC3_Enabled'),
        #     ('checkBox_S1_DC4_11', 'checkbox', 'S11_DC4_Enabled'),
        #     ('textEdit_S1_DC1_PF_11', 'textedit', 'S11_PF'),
        #     ('lE_S11_filename', 'lineedit', 'S11_Filename'),  # 新增
        # ],
        # "Step12": [
        #     ('checkBox_S12', 'checkbox', 'S12_Enabled'),
        #     ('checkBox_S1_DC1_12', 'checkbox', 'S12_DC1_Enabled'),
        #     ('checkBox_S1_DC2_12', 'checkbox', 'S12_DC2_Enabled'),
        #     ('checkBox_S1_DC3_12', 'checkbox', 'S12_DC3_Enabled'),
        #     ('checkBox_S1_DC4_12', 'checkbox', 'S12_DC4_Enabled'),
        #     ('textEdit_S1_DC1_PF_12', 'textedit', 'S12_PF'),
        #     ('lE_S12_filename', 'lineedit', 'S12_Filename'),  # 新增
        # ],
        # "Step13": [
        #     ('checkBox_S13', 'checkbox', 'S13_Enabled'),
        #     ('checkBox_S1_DC1_13', 'checkbox', 'S13_DC1_Enabled'),
        #     ('checkBox_S1_DC2_13', 'checkbox', 'S13_DC2_Enabled'),
        #     ('checkBox_S1_DC3_13', 'checkbox', 'S13_DC3_Enabled'),
        #     ('checkBox_S1_DC4_13', 'checkbox', 'S13_DC4_Enabled'),
        #     ('textEdit_S1_DC1_PF_13', 'textedit', 'S13_PF'),
        #     ('lE_S13_filename', 'lineedit', 'S13_Filename'),  # 新增

        # ],
        "batch_set": [
            ('lE_time_1', 'lineedit', 'batch_time_1'),
            ('lE_time_2', 'lineedit', 'batch_time_2'),
            ('lE_time_3', 'lineedit', 'batch_time_3'),
            ('lE_time_4', 'lineedit', 'batch_time_4'),
            ('cB_time_unit_1', 'combobox', 'batch_time_unit_1'),
            ('cB_time_unit_2', 'combobox', 'batch_time_unit_2'),
            ('cB_time_unit_3', 'combobox', 'batch_time_unit_3'),
            ('cB_time_unit_4', 'combobox', 'batch_time_unit_4'),
        ],

        "Step14": [
            ('checkBox_S14', 'checkbox', 'S14_Enabled'),
            ('comboBox_S5_AC', 'combobox', 'S14_AC_Type'),
            ('checkBox_S5_DC1', 'checkbox', 'S14_DC1_Enabled'),
            ('comboBox_S5_DC1', 'combobox', 'S14_DC1_Type'),
            ('checkBox_S5_DC2', 'checkbox', 'S14_DC2_Enabled'),
            ('comboBox_S5_DC2', 'combobox', 'S14_DC2_Type'),
            ('checkBox_S5_DC3', 'checkbox', 'S14_DC3_Enabled'),
            ('comboBox_S5_DC3', 'combobox', 'S14_DC3_Type'),
            ('checkBox_S5_DC4', 'checkbox', 'S14_DC4_Enabled'),
            ('comboBox_S5_DC4', 'combobox', 'S14_DC4_Type'),

            ('checkBox_S14_2', 'checkbox', 'S14_json_Enabled'),
            ('lE_S14_1', 'lineedit', 'S14_time_1'),
            ('cB_S14_unit_1', 'combobox', 'S14_time_unit_1'),
        ],
    }
    
    def __init__(self, ui_fixedpf):
        self.ui = ui_fixedpf
        self.script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.settings_dir = os.path.join(self.script_dir, "settings", "ThaiFixedPF")
        
    def get_settings_path(self, filename=None):
        """获取配置文件路径"""
        os.makedirs(self.settings_dir, exist_ok=True)
        if filename:
            return os.path.join(self.settings_dir, filename)
        return self.settings_dir
    
    def save_config(self):
        """保存配置（使用QFileDialog选择路径）"""
        # 1. 确保settings目录存在
        settings_dir = self.get_settings_path()
        
        # 2. 弹出文件保存对话框，默认定位到settings目录
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "保存配置",
            settings_dir,  # 默认打开settings目录
            "配置文件 (*.ini)"
        )
        
        if not file_path:  # 用户取消
            return False
        
        # 3. 确保文件名以.ini结尾
        if not file_path.endswith('.ini'):
            file_path += '.ini'
        
        # 4. 创建QSettings对象并保存
        settings = QSettings(file_path, QSettings.IniFormat)
        
        try:
            for step_name, fields in self.CONFIG_STRUCTURE.items():
                settings.beginGroup(step_name)
                for widget_name, widget_type, key in fields:
                    widget = getattr(self.ui, widget_name)
                    
                    if widget_type == 'checkbox':
                        settings.setValue(key, widget.isChecked())
                    elif widget_type == 'combobox':
                        # 【固定选项】保存索引
                        settings.setValue(key, widget.currentIndex())
                    elif widget_type == 'combobox_text':
                        # 【动态填充】保存文本内容
                        settings.setValue(key, widget.currentText())
                    elif widget_type == 'textedit':
                        settings.setValue(key, widget.toPlainText())
                    elif widget_type == 'lineedit':
                        settings.setValue(key, widget.text())
                
                settings.endGroup()
            
            QMessageBox.information(None, "成功", f"配置已保存到:\n{file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(None, "错误", f"保存配置失败: {str(e)}")
            return False
    
    def load_config(self):
        """加载配置（从settings文件夹选择文件）"""
        # 1. 确保settings目录存在
        settings_dir = self.get_settings_path()
        
        # 2. 弹出文件选择对话框，默认定位到settings目录
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "选择配置文件",
            settings_dir,  # 默认打开settings目录
            "配置文件 (*.ini)"
        )
        
        if not file_path:  # 用户取消
            return False
        
        # 3. 检查文件是否存在
        if not os.path.exists(file_path):
            QMessageBox.warning(None, "错误", "配置文件不存在")
            return False
        
        # 4. 创建QSettings对象并加载
        settings = QSettings(file_path, QSettings.IniFormat)
        
        try:
            for step_name, fields in self.CONFIG_STRUCTURE.items():
                settings.beginGroup(step_name)
                for widget_name, widget_type, key in fields:
                    if not settings.contains(key):
                        continue
                    
                    widget = getattr(self.ui, widget_name)
                    
                    if widget_type == 'checkbox':
                        widget.setChecked(settings.value(key, type=bool))
                    elif widget_type == 'combobox':
                        # 【固定选项】加载索引
                        widget.setCurrentIndex(settings.value(key, type=int))
                    elif widget_type == 'combobox_text':
                        # 【动态填充】安全加载文本
                        saved_text = settings.value(key, type=str)
                        self._set_combo_text_safely(widget, saved_text)
                    elif widget_type == 'textedit':
                        widget.setPlainText(settings.value(key, type=str))
                    elif widget_type == 'lineedit':
                        widget.setText(settings.value(key, type=str))
                
                settings.endGroup()
            
            QMessageBox.information(None, "成功", f"配置加载完成！\n{os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            QMessageBox.critical(None, "错误", f"加载配置失败: {str(e)}")
            return False
        
    def _set_combo_text_safely(self, combo_box, saved_text):
        """安全设置 ComboBox 选择项（验证文本是否存在）"""
        if not saved_text:
            combo_box.setCurrentIndex(-1)  # 清空选择
            return
        
        # 查找文本在当前列表中的索引
        index = combo_box.findText(saved_text)
        if index >= 0:
            combo_box.setCurrentIndex(index)
        else:
            # 文本不存在时的处理策略（推荐：清空选择）
            combo_box.setCurrentIndex(-1)
            print(f"⚠️ 警告：保存的配置项 '{saved_text}' 已不存在于当前列表中")


