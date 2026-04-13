import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMessageBox, QTableWidgetItem, 
    QPushButton, QAbstractItemView, QHeaderView, QFileDialog
)
from PyQt5.QtCore import Qt
from dialogs.Dialog_thaistaticQU.ui.Ui_Dialog_thaistaticQU_vol_config import Ui_Dialog_QU_config

class QU_config(QDialog):
    # ===== 常量集中管理 =====
    COL_PERCENT, COL_VOLTAGE, COL_SET, COL_BTN = range(4)
    ROLE_CONFIRMED = Qt.UserRole + 1
    ROLE_ORIGINAL = Qt.UserRole + 2
    DECIMALS = {COL_PERCENT: 2, COL_VOLTAGE: 1, COL_SET: 1}
    COL_WIDTHS = [100, 100, 100, 80]
    HEADERS = ["目标百分比", "目标电压", "设定电压", "新建"]

    def __init__(self, logger=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog_QU_config()
        self.ui.setupUi(self)
        self.logger = logger
        self.parent = parent
        
        self.Un = None
        self._auto_filling = False
        
        self.QU_config = {
            'target_percentages': [],
            'target_voltages': [],
            'set_voltages': []
        }
        
        self._connect_signals()
        self._init_ui()

    def _connect_signals(self):
        """统一连接所有信号"""
        self.ui.le_Un.textChanged.connect(self._on_un_changed)
        self.ui.tw_main.cellChanged.connect(self._on_cell_changed)
        self.ui.btn_save.clicked.connect(self._on_btn_save_clicked)
        self.ui.btn_read.clicked.connect(self._on_btn_read_clicked)
        
        # ===== 新增：连接清除按钮信号 =====
        self.ui.btn_clear.clicked.connect(self._on_btn_clear_clicked)

    def _init_ui(self):
        """初始化表格"""
        tw = self.ui.tw_main
        tw.setColumnCount(len(self.HEADERS))
        tw.setHorizontalHeaderLabels(self.HEADERS)
        
        for i, width in enumerate(self.COL_WIDTHS):
            tw.setColumnWidth(i, width)
        
        tw.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tw.setEnabled(False)
        tw.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._add_row()

    def _parse_number(self, text, allow_empty=False):
        """纯数字解析（不转换）"""
        text = text.strip()
        if not text:
            return (None, "" if allow_empty else None)
        try:
            return (float(text), text)
        except ValueError:
            return (None, None)

    def _format_value(self, value, col):
        """统一格式化"""
        return f"{value:.{self.DECIMALS[col]}f}"

    def _predict_percentage(self, row):
        """预测目标百分比（基于前两行）"""
        if row < 2:
            return None
            
        tw = self.ui.tw_main
        prev1_item = tw.item(row - 1, self.COL_PERCENT)
        prev2_item = tw.item(row - 2, self.COL_PERCENT)
        
        if not (prev1_item and prev2_item):
            return None
            
        prev1_text = prev1_item.text().strip()
        prev2_text = prev2_item.text().strip()
        
        if not (prev1_text and prev2_text):
            return None
            
        if not (prev1_item.data(self.ROLE_CONFIRMED) and 
                prev2_item.data(self.ROLE_CONFIRMED)):
            return None
            
        try:
            prev1_val = float(prev1_text)
            prev2_val = float(prev2_text)
            diff = prev1_val - prev2_val
            return prev1_val + diff
        except ValueError:
            return None

    def _calc_coefficient(self, row):
        """计算设定电压系数"""
        if row == 0:
            return None
            
        tw = self.ui.tw_main
        prev_perc = tw.item(row - 1, self.COL_PERCENT)
        prev_set = tw.item(row - 1, self.COL_SET)
        
        if not (prev_perc and prev_set):
            return None
            
        try:
            perc_val, _ = self._parse_number(prev_perc.text())
            set_val, _ = self._parse_number(prev_set.text())
            if perc_val and set_val and perc_val != 0:
                return set_val / perc_val
        except:
            pass
        return None

    def _update_row_data(self, row, percent_val):
        """批量更新单行UI"""
        if not percent_val or not self.Un:
            return
            
        tw = self.ui.tw_main
        self._auto_filling = True
        
        try:
            tw.blockSignals(True)
            
            tw.item(row, self.COL_PERCENT).setText(
                self._format_value(percent_val, self.COL_PERCENT)
            )
            
            tw.item(row, self.COL_VOLTAGE).setText(
                self._format_value(percent_val * self.Un, self.COL_VOLTAGE)
            )
            
            coeff = self._calc_coefficient(row)
            if coeff:
                tw.item(row, self.COL_SET).setText(
                    self._format_value(percent_val * coeff, self.COL_SET)
                )
                
        finally:
            tw.blockSignals(False)
            self._auto_filling = False

    def _on_un_changed(self, text):
        """Un值变化处理"""
        val, _ = self._parse_number(text, allow_empty=True)
        self.Un = val
        self.ui.tw_main.setEnabled(val is not None)

    def _on_cell_changed(self, row, col):
        """单元格变化处理"""
        if self._auto_filling or col != self.COL_PERCENT:
            return
            
        item = self.ui.tw_main.item(row, self.COL_PERCENT)
        val, raw = self._parse_number(item.text())
        
        if raw is None:
            return
        
        if val and val > 10:
            val = val / 100
            
        self._update_row_data(row, val)
        item.setData(self.ROLE_ORIGINAL, item.text())

    def _on_btn_save_clicked(self):
        """保存配置到CSV文件"""
        self.QU_config = {
            'target_percentages': [],
            'target_voltages': [],
            'set_voltages': []
        }
        
        tw = self.ui.tw_main
        for row in range(tw.rowCount()):
            item = tw.item(row, self.COL_PERCENT)
            if item and item.data(self.ROLE_CONFIRMED):
                try:
                    perc = float(item.text())
                    volt = float(tw.item(row, self.COL_VOLTAGE).text())
                    set_v = float(tw.item(row, self.COL_SET).text())
                    
                    self.QU_config['target_percentages'].append(perc)
                    self.QU_config['target_voltages'].append(volt)
                    self.QU_config['set_voltages'].append(set_v)
                except:
                    continue
        
        if not self.QU_config['target_percentages']:
            QMessageBox.warning(self, "无数据", "没有可保存的已确认数据！")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存配置文件",
            "./QU_config.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['目标百分比', '目标电压', '设定电压'])
                for i in range(len(self.QU_config['target_percentages'])):
                    writer.writerow([
                        self.QU_config['target_percentages'][i],
                        self.QU_config['target_voltages'][i],
                        self.QU_config['set_voltages'][i]
                    ])
            
            QMessageBox.information(self, "保存成功", f"配置已保存到:\n{file_path}")
            if self.logger:
                self.logger.info(f"配置保存成功: {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存文件时出错:\n{str(e)}")
            if self.logger:
                self.logger.error(f"配置保存失败: {e}")

    def _on_btn_read_clicked(self):
        """从CSV文件读取配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "打开配置文件",
            "./",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            tw = self.ui.tw_main
            tw.setRowCount(0)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # 跳过表头
                
                for row_data in reader:
                    if len(row_data) < 3:
                        continue
                    
                    try:
                        perc = float(row_data[0])
                        volt = float(row_data[1])
                        set_v = float(row_data[2])
                        
                        self._add_row()
                        current_row = tw.rowCount() - 1
                        tw.item(current_row, self.COL_PERCENT).setText(str(perc))
                        tw.item(current_row, self.COL_VOLTAGE).setText(str(volt))
                        tw.item(current_row, self.COL_SET).setText(str(set_v))
                        
                        for col in range(self.COL_BTN):
                            item = tw.item(current_row, col)
                            item.setData(self.ROLE_CONFIRMED, True)
                            item.setData(self.ROLE_ORIGINAL, item.text())
                        
                        tw.cellWidget(current_row, self.COL_BTN).setText("删除")
                        
                    except:
                        continue
            
            self._add_row()
            
            QMessageBox.information(self, "读取成功", f"配置已从文件加载:\n{file_path}")
            if self.logger:
                self.logger.info(f"配置读取成功: {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "读取失败", f"读取文件时出错:\n{str(e)}")
            if self.logger:
                self.logger.error(f"配置读取失败: {e}")

    # ===== 新增：一键清除所有行 =====
    def _on_btn_clear_clicked(self):
        """一键清除所有行记录"""
        reply = QMessageBox.question(
            self,
            "确认清除",
            "确定要清除所有配置数据吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 清空表格
            self.ui.tw_main.setRowCount(0)
            
            # 重置配置字典
            self.QU_config = {
                'target_percentages': [],
                'target_voltages': [],
                'set_voltages': []
            }
            
            # 添加一个空白行
            self._add_row()
            
            # 提示清除完成
            QMessageBox.information(self, "清除完成", "所有配置数据已清除！")
            
            if self.logger:
                self.logger.info("用户清除所有配置数据")

    def _on_add_clicked(self):
        """按钮点击处理"""
        if not self.Un:
            QMessageBox.warning(self, "错误", "请先输入基准电压")
            return
            
        btn = self.sender()
        row = next((i for i in range(self.ui.tw_main.rowCount()) 
                   if self.ui.tw_main.cellWidget(i, self.COL_BTN) == btn), None)
        if row is None:
            return
            
        if btn.text() == "添加":
            self._confirm_row(row, btn)
        else:
            self._delete_row(row)

    def _confirm_row(self, row, btn):
        """确认行"""
        tw = self.ui.tw_main
        
        empty = [name for col, name in [(self.COL_PERCENT, "目标百分比"), (self.COL_SET, "设定电压")]
                 if not tw.item(row, col).text().strip()]
        
        if empty:
            QMessageBox.warning(self, "数据不完整", f"以下列为空：{', '.join(empty)}")
            return
            
        self._format_row(row)
        for c in range(self.COL_BTN):
            item = tw.item(row, c)
            item.setData(self.ROLE_CONFIRMED, True)
            item.setData(self.ROLE_ORIGINAL, item.text())
            
        btn.setText("删除")
        self._add_row()

    def _delete_row(self, row):
        """删除行"""
        self.ui.tw_main.removeRow(row)
        self._renumber_rows()

    def _format_row(self, row):
        """格式化一行"""
        tw = self.ui.tw_main
        for col in (self.COL_PERCENT, self.COL_VOLTAGE, self.COL_SET):
            item = tw.item(row, col)
            if item and item.text().strip():
                try:
                    val = float(item.text())
                    if col == self.COL_PERCENT and val > 10:
                        val /= 100
                    item.setText(self._format_value(val, col))
                except:
                    pass

    def _add_row(self):
        """添加新行"""
        tw = self.ui.tw_main
        row = tw.rowCount()
        tw.insertRow(row)
        tw.setVerticalHeaderItem(row, QTableWidgetItem(f"no.{row + 1}"))
        
        btn = QPushButton("添加")
        btn.clicked.connect(self._on_add_clicked)
        tw.setCellWidget(row, self.COL_BTN, btn)
        
        for col in range(self.COL_BTN):
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignCenter)
            item.setData(self.ROLE_CONFIRMED, False)
            item.setData(self.ROLE_ORIGINAL, "")
            if col == self.COL_VOLTAGE:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            else:
                item.setFlags(item.flags() | Qt.ItemIsEditable)
            tw.setItem(row, col, item)
        
        if row >= 2:
            predicted = self._predict_percentage(row)
            if predicted is not None:
                self._auto_filling = True
                try:
                    tw.blockSignals(True)
                    tw.item(row, self.COL_PERCENT).setText(str(predicted))
                    self._update_row_data(row, predicted)
                finally:
                    tw.blockSignals(False)
                    self._auto_filling = False

    def _renumber_rows(self):
        """重新编号"""
        tw = self.ui.tw_main
        for row in range(tw.rowCount()):
            tw.setVerticalHeaderItem(row, QTableWidgetItem(f"no.{row + 1}"))
            btn = tw.cellWidget(row, self.COL_BTN)
            btn.clicked.disconnect()
            btn.clicked.connect(self._on_add_clicked)

    def closeEvent(self, event):
        """关闭检查"""
        if not self.Un:
            event.ignore() if QMessageBox.No == QMessageBox.warning(
                self, "未输入基准电压", "基准电压 (Un) 未输入，确定要关闭窗口吗？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            ) else None
        
        unconfirmed = [str(r+1) for r in range(self.ui.tw_main.rowCount() - 1)
                      if not self.ui.tw_main.item(r, self.COL_PERCENT).data(self.ROLE_CONFIRMED)]
        
        if unconfirmed:
            event.ignore() if QMessageBox.No == QMessageBox.warning(
                self, "未确认的数据", f"以下行尚未添加：{', '.join(unconfirmed)}\n确定要关闭窗口吗？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            ) else None
        else:
            event.accept()


# ===== 测试入口 =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = QU_config()
    dialog.show()
    sys.exit(app.exec_())