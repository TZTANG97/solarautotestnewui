# -*- coding: utf-8 -*-
"""
DEWETRON 功率分析仪设置对话框（手写 UI，无需 .ui 文件）。

布局：QTabWidget
  Tab 1: 接线图 — 顶部接线类型按钮 + 左侧通道列表 + 中间输入框列 + 右侧图片背景接线图
  Tab 2: 设置 — 基本配置 + 采样与测量配置 + 比例系数配置
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QButtonGroup, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLineEdit


class DraggableCheckBox(QCheckBox):
    """可拖拽的 CheckBox，拖拽时携带通道名文本。"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._drag_start = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_start = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_start is None:
            return
        if (event.pos() - self._drag_start).manhattanLength() > QtWidgets.QApplication.startDragDistance():
            drag = QtWidgets.QDrag(self)
            mime = QtCore.QMimeData()
            mime.setText(self.text())
            drag.setMimeData(mime)
            drag.exec_(QtCore.Qt.CopyAction)
            self._drag_start = None

    def mouseReleaseEvent(self, event):
        self._drag_start = None
        super().mouseReleaseEvent(event)


class DraggableInputBox(QLineEdit):
    """可接收拖拽通道的输入框，一个框只允许一个通道。"""

    channelChanged = QtCore.pyqtSignal(str, str)  # (slot_name, channel_text)

    def __init__(self, slot_name, parent=None):
        super().__init__(parent)
        self._slot_name = slot_name
        self._channel = ''
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFont(QtGui.QFont("Arial", 9))
        self.setPlaceholderText(slot_name)
        self.setReadOnly(True)
        self.setAcceptDrops(True)
        self.setMinimumWidth(120)
        self.setMaximumWidth(180)
        self.setMinimumHeight(28)
        self._update_style()

    def _update_style(self):
        if self._channel:
            self.setStyleSheet(
                "QLineEdit { background: #e8f0fe; border: 2px solid #0078d4; }"
            )
        else:
            self.setStyleSheet(
                "QLineEdit { background: white; border: 1px solid #999; }"
                "QLineEdit:focus { border: 2px solid #0078d4; }"
            )

    def set_channel(self, channel_text):
        self._channel = channel_text
        self.setText(channel_text)
        self._update_style()
        self.channelChanged.emit(self._slot_name, channel_text)

    def clear_channel(self):
        self._channel = ''
        self.clear()
        self._update_style()
        self.channelChanged.emit(self._slot_name, '')

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        text = event.mimeData().text()
        if text:
            self.set_channel(text)
        event.acceptProposedAction()

    def mouseDoubleClickEvent(self, event):
        self.clear_channel()


# ================================================================
# WiringDiagramCanvas — 图片背景 + 输入框叠加的接线图画布
# ================================================================

import os

class WiringDiagramCanvas(QWidget):
    """接线图画布：纯图片背景显示接线图。"""

    IMAGE_FILES = {
        0: '1p2w_preview.png',
        1: '1p3w_preview.png',
        2: '2v2a_preview.png',
        3: '3p3w_preview.png',
        4: '3p4w_preview.png',
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._wiring_type = 0
        self._images = {}  # type_id → QPixmap
        self.setMinimumSize(700, 500)

    def set_wiring_type(self, type_id):
        self._wiring_type = type_id
        self._load_image(type_id)
        self.update()

    def _load_image(self, type_id):
        if type_id in self._images:
            return
        filename = self.IMAGE_FILES.get(type_id)
        if not filename:
            return
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_dir, 'dewetron_media', filename)
        if os.path.exists(img_path):
            self._images[type_id] = QtGui.QPixmap(img_path)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(self.rect(), QtCore.Qt.white)

        pixmap = self._images.get(self._wiring_type)
        if pixmap and not pixmap.isNull():
            scaled = pixmap.scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            painter.setPen(QtCore.Qt.gray)
            painter.setFont(QtGui.QFont("Arial", 12))
            painter.drawText(self.rect(), QtCore.Qt.AlignCenter, "接线图（待补充）")


# ================================================================
# 主 UI 类
# ================================================================

class Ui_Dialog_DEWETRON_Setting(object):
    """DEWETRON 设置对话框 UI 类。"""

    def setupUi(self, Dialog_DEWETRON_Setting):
        Dialog_DEWETRON_Setting.setObjectName("Dialog_DEWETRON_Setting")
        Dialog_DEWETRON_Setting.setFixedSize(1400, 900)
        Dialog_DEWETRON_Setting.setWindowTitle("DEWETRON 设置")

        # ============================================================
        # QTabWidget 占满整个对话框
        # ============================================================
        self.tabWidget = QTabWidget(Dialog_DEWETRON_Setting)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1400, 900))

        # ============================================================
        # Tab 1: 接线图
        # ============================================================
        self.tab_wiring = QWidget()
        tab1_layout = QVBoxLayout(self.tab_wiring)
        tab1_layout.setContentsMargins(8, 8, 8, 8)
        tab1_layout.setSpacing(6)

        # --- 顶部：接线类型按钮栏 ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)

        self.buttonGroup_wiringType = QButtonGroup(self.tab_wiring)
        self.buttonGroup_wiringType.setExclusive(True)

        wiring_types = [
            (0, "btn_wiring_1P2W", "1P2W", "1相\n2线"),
            (1, "btn_wiring_1P3W", "1P3W", "1相\n3线"),
            (2, "btn_wiring_2V2A", "2V2A", "3相\n3线"),
            (3, "btn_wiring_3P3W", "3P3W", "3相\n3线"),
            (4, "btn_wiring_3P4W", "3P4W", "3相\n4线"),
        ]
        self._wiring_buttons = []
        for type_id, attr_name, label, desc in wiring_types:
            btn = QtWidgets.QPushButton(self.tab_wiring)
            btn.setText(f"{label}\n{desc}")
            btn.setCheckable(True)
            btn.setMinimumSize(160, 80)
            btn.setMaximumSize(200, 90)
            btn.setStyleSheet(
                "QPushButton { border: 2px solid #aaa; border-radius: 4px; "
                "font-size: 11px; padding: 4px; }"
                "QPushButton:checked { border: 2px solid #0078d4; background-color: #e8f0fe; }"
                "QPushButton:hover { border: 2px solid #666; }"
            )
            setattr(self, attr_name, btn)
            self.buttonGroup_wiringType.addButton(btn, type_id)
            btn_layout.addWidget(btn)
            self._wiring_buttons.append((type_id, btn))

        # 默认选中 1P2W
        self.btn_wiring_1P2W.setChecked(True)

        tab1_layout.addLayout(btn_layout)

        # --- 中间区域：左(通道树) + 中(接线图+输入框) + 右(输出标签) + 下(对应关系) ---
        main_area = QHBoxLayout()
        main_area.setSpacing(4)

        # -- 左列：通道树列表 --
        left_panel = QVBoxLayout()
        left_panel.setSpacing(2)
        ch_title = QtWidgets.QLabel("通道")
        ch_title.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        left_panel.addWidget(ch_title)

        self.treeWidget_channels = QtWidgets.QTreeWidget()
        self.treeWidget_channels.setHeaderLabel("通道列表")
        self.treeWidget_channels.setMinimumWidth(160)
        self.treeWidget_channels.setMaximumWidth(220)
        # 构建通道树
        power_group = QtWidgets.QTreeWidgetItem(self.treeWidget_channels, ["Power Groups"])
        power_group.setExpanded(True)
        pw0 = QtWidgets.QTreeWidgetItem(power_group, ["POWER/0"])
        pw0.setExpanded(True)

        # 电压通道 (U)
        voltage_group = QtWidgets.QTreeWidgetItem(pw0, ["电压 (U)"])
        voltage_group.setExpanded(True)
        for ch in ["AI 1/U1", "AI 1/U2", "AI 1/U3", "AI 1/U4"]:
            item = QtWidgets.QTreeWidgetItem(voltage_group, [ch])
            item.setFlags(item.flags() | QtCore.Qt.ItemIsDragEnabled)

        # 电流通道 (I)
        current_group = QtWidgets.QTreeWidgetItem(pw0, ["电流 (I)"])
        current_group.setExpanded(True)
        for ch in ["AI 1/l1", "AI 1/l2", "AI 1/l3", "AI 1/l4"]:
            item = QtWidgets.QTreeWidgetItem(current_group, [ch])
            item.setFlags(item.flags() | QtCore.Qt.ItemIsDragEnabled)

        left_panel.addWidget(self.treeWidget_channels, 1)

        # 保留 checkbox 用于信号绑定（隐藏）
        self.checkBox_ch_l1 = DraggableCheckBox("AI 1/l1")
        self.checkBox_ch_l1.setChecked(True)
        self.checkBox_ch_l1.setVisible(False)
        self.checkBox_ch_l2 = DraggableCheckBox("AI 1/l2")
        self.checkBox_ch_l2.setVisible(False)
        self.checkBox_ch_l3 = DraggableCheckBox("AI 1/l3")
        self.checkBox_ch_l3.setVisible(False)
        self.checkBox_ch_l4 = DraggableCheckBox("AI 1/l4")
        self.checkBox_ch_l4.setVisible(False)
        self.checkBox_ch_u1 = DraggableCheckBox("AI 1/U1")
        self.checkBox_ch_u1.setChecked(True)
        self.checkBox_ch_u1.setVisible(False)
        self.checkBox_ch_u2 = DraggableCheckBox("AI 1/U2")
        self.checkBox_ch_u2.setVisible(False)
        self.checkBox_ch_u3 = DraggableCheckBox("AI 1/U3")
        self.checkBox_ch_u3.setVisible(False)
        self.checkBox_ch_u4 = DraggableCheckBox("AI 1/U4")
        self.checkBox_ch_u4.setVisible(False)
        left_panel.addWidget(self.checkBox_ch_l1)

        main_area.addLayout(left_panel)

        # -- 中间：接线图画布 + 输入框叠加 --
        center_panel = QVBoxLayout()
        center_panel.setSpacing(2)
        diagram_title = QtWidgets.QLabel("接线图")
        diagram_title.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        center_panel.addWidget(diagram_title)

        self.wiringDiagramCanvas = WiringDiagramCanvas(self.tab_wiring)
        self.wiringDiagramCanvas.setMinimumHeight(500)
        center_panel.addWidget(self.wiringDiagramCanvas, 1)

        # 输入框列（在图片下方）
        self._slot_list_layout = QHBoxLayout()
        self._slot_list_layout.setSpacing(8)
        self._slot_input_widgets = {}
        center_panel.addLayout(self._slot_list_layout)

        main_area.addLayout(center_panel, 1)

        # -- 右列：输出标签 (L1/L2/L3/N + N/A) --
        right_panel = QVBoxLayout()
        right_panel.setSpacing(4)
        out_title = QtWidgets.QLabel("输出")
        out_title.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        right_panel.addWidget(out_title)
        self._output_labels = {}
        for name in ['L1', 'L2', 'L3', 'N']:
            row = QHBoxLayout()
            lbl = QtWidgets.QLabel(name)
            lbl.setFixedWidth(30)
            lbl.setFont(QtGui.QFont("Arial", 10))
            row.addWidget(lbl)
            val = QtWidgets.QLabel("N/A")
            val.setStyleSheet("color: gray;")
            val.setFont(QtGui.QFont("Arial", 10))
            row.addWidget(val)
            row.addStretch()
            right_panel.addLayout(row)
            self._output_labels[name] = val
        right_panel.addStretch()
        main_area.addLayout(right_panel)

        tab1_layout.addLayout(main_area, 1)

        # -- 底部：对应关系 + 操作按钮 --
        bottom_layout = QHBoxLayout()

        # 对应关系
        mapping_group = QtWidgets.QGroupBox("对应关系")
        mapping_group.setMaximumHeight(120)
        self._mapping_layout = QtWidgets.QFormLayout(mapping_group)
        self._mapping_layout.setSpacing(4)
        self._mapping_labels = {}
        bottom_layout.addWidget(mapping_group, 1)

        # 默认加载 1P2W
        self.wiringDiagramCanvas.set_wiring_type(0)
        self._create_slot_inputs(0)
        self._update_mapping_display()

        # 操作按钮
        btn_col = QVBoxLayout()
        btn_col.setSpacing(6)
        self.pushButton_ApplySettings = QtWidgets.QPushButton(self.tab_wiring)
        self.pushButton_ApplySettings.setText("保存")
        self.pushButton_ApplySettings.setMinimumSize(130, 36)
        btn_col.addWidget(self.pushButton_ApplySettings)
        btn_col.addStretch()
        bottom_layout.addLayout(btn_col)

        tab1_layout.addLayout(bottom_layout)

        # -- 日志区域 --
        log_group = QtWidgets.QGroupBox("日志")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(4, 4, 4, 4)
        self.textEdit_log = QtWidgets.QTextEdit()
        self.textEdit_log.setReadOnly(True)
        self.textEdit_log.setMaximumHeight(120)
        self.textEdit_log.setFont(QtGui.QFont("Consolas", 9))
        self.textEdit_log.setStyleSheet("QTextEdit { background: #1e1e1e; color: #d4d4d4; }")
        log_layout.addWidget(self.textEdit_log)
        tab1_layout.addWidget(log_group)

        self.tabWidget.addTab(self.tab_wiring, "接线图")

        # ============================================================
        # Tab 2: 设置
        # ============================================================
        self.tab_settings = QWidget()
        tab2_layout = QHBoxLayout(self.tab_settings)
        tab2_layout.setContentsMargins(10, 10, 10, 10)
        tab2_layout.setSpacing(10)

        # --- 左列：基本配置 + 采样与测量配置 ---
        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        # GroupBox 1: 基本配置
        self.groupBox_basicConfig = QtWidgets.QGroupBox("基本配置")
        self.groupBox_basicConfig.setMinimumHeight(190)
        bc_layout = QtWidgets.QFormLayout(self.groupBox_basicConfig)
        bc_layout.setSpacing(8)

        self.lineEdit_deviceIP = QtWidgets.QLineEdit("192.168.40.21")
        bc_layout.addRow("设备IP:", self.lineEdit_deviceIP)

        self.lineEdit_port = QtWidgets.QLineEdit("10001")
        self.lineEdit_port.setMaximumWidth(120)
        bc_layout.addRow("端口号:", self.lineEdit_port)

        file_row = QHBoxLayout()
        self.pushButton_selectConfigFile = QtWidgets.QPushButton("选择文件...")
        self.pushButton_selectConfigFile.setMaximumWidth(90)
        file_row.addWidget(self.pushButton_selectConfigFile)
        self.label_configFilePath = QtWidgets.QLabel("")
        self.label_configFilePath.setStyleSheet("color: gray;")
        file_row.addWidget(self.label_configFilePath, 1)
        bc_layout.addRow("配置文件:", file_row)

        left_col.addWidget(self.groupBox_basicConfig)

        # GroupBox 2: 采样与测量配置
        self.groupBox_samplingConfig = QtWidgets.QGroupBox("采样与测量配置")
        sc_layout = QtWidgets.QVBoxLayout(self.groupBox_samplingConfig)
        sc_layout.setSpacing(4)

        # 采样率
        sr_row = QHBoxLayout()
        sr_row.addWidget(QtWidgets.QLabel("采样率:"))
        self.comboBox_samplingRate = QtWidgets.QComboBox()
        self.comboBox_samplingRate.addItems(["10ms", "50ms", "100ms", "500ms", "1000ms"])
        self.comboBox_samplingRate.setCurrentText("100ms")
        self.comboBox_samplingRate.setMaximumWidth(120)
        sr_row.addWidget(self.comboBox_samplingRate)
        sr_row.addStretch()
        sc_layout.addLayout(sr_row)

        # 测量通道
        sc_layout.addWidget(QtWidgets.QLabel("测量通道:"))
        ch_grid = QtWidgets.QGridLayout()
        ch_grid.setSpacing(4)

        self.checkBox_uTRMS = QtWidgets.QCheckBox("电压有效值 (U_tRMS)")
        self.checkBox_uTRMS.setChecked(True)
        ch_grid.addWidget(self.checkBox_uTRMS, 0, 0)

        self.checkBox_S = QtWidgets.QCheckBox("视在功率 (S)")
        ch_grid.addWidget(self.checkBox_S, 0, 1)

        self.checkBox_iTRMS = QtWidgets.QCheckBox("电流有效值 (I_tRMS)")
        self.checkBox_iTRMS.setChecked(True)
        ch_grid.addWidget(self.checkBox_iTRMS, 1, 0)

        self.checkBox_Q = QtWidgets.QCheckBox("无功功率 (Q)")
        ch_grid.addWidget(self.checkBox_Q, 1, 1)

        self.checkBox_Pt = QtWidgets.QCheckBox("有功功率 (P_t)")
        self.checkBox_Pt.setChecked(True)
        ch_grid.addWidget(self.checkBox_Pt, 2, 0)

        self.checkBox_PF = QtWidgets.QCheckBox("功率因数 (PF)")
        ch_grid.addWidget(self.checkBox_PF, 2, 1)

        self.checkBox_F = QtWidgets.QCheckBox("频率 (F)")
        ch_grid.addWidget(self.checkBox_F, 3, 0)

        sc_layout.addLayout(ch_grid)

        # 录制设置
        rec_row = QHBoxLayout()
        rec_row.addWidget(QtWidgets.QLabel("录制设置:"))
        self.checkBox_enableRecording = QtWidgets.QCheckBox("启用录制")
        self.checkBox_enableRecording.setChecked(True)
        rec_row.addWidget(self.checkBox_enableRecording)
        rec_row.addStretch()
        sc_layout.addLayout(rec_row)

        fn_row = QHBoxLayout()
        fn_row.addWidget(QtWidgets.QLabel("文件名:"))
        self.lineEdit_recordingFileName = QtWidgets.QLineEdit("电力测量")
        self.lineEdit_recordingFileName.setMaximumWidth(200)
        fn_row.addWidget(self.lineEdit_recordingFileName)
        fn_row.addStretch()
        sc_layout.addLayout(fn_row)

        left_col.addWidget(self.groupBox_samplingConfig)
        left_col.addStretch()

        tab2_layout.addLayout(left_col, 1)

        # --- 右列：比例系数配置 ---
        right_col = QVBoxLayout()
        right_col.setSpacing(8)

        # GroupBox: 比例系数配置
        self.groupBox_ratioConfig = QtWidgets.QGroupBox("比例系数配置")
        rc_layout = QtWidgets.QFormLayout(self.groupBox_ratioConfig)
        rc_layout.setSpacing(8)

        self.doubleSpinBox_vRatio = QtWidgets.QDoubleSpinBox()
        self.doubleSpinBox_vRatio.setMinimum(0.001)
        self.doubleSpinBox_vRatio.setMaximum(9999.0)
        self.doubleSpinBox_vRatio.setDecimals(3)
        self.doubleSpinBox_vRatio.setValue(1.0)
        rc_layout.addRow("电压比例系数:", self.doubleSpinBox_vRatio)

        self.doubleSpinBox_iRatio = QtWidgets.QDoubleSpinBox()
        self.doubleSpinBox_iRatio.setMinimum(0.001)
        self.doubleSpinBox_iRatio.setMaximum(9999.0)
        self.doubleSpinBox_iRatio.setDecimals(3)
        self.doubleSpinBox_iRatio.setValue(1.0)
        rc_layout.addRow("电流比例系数:", self.doubleSpinBox_iRatio)

        self.spinBox_ctRatio = QtWidgets.QSpinBox()
        self.spinBox_ctRatio.setMinimum(1)
        self.spinBox_ctRatio.setMaximum(9999)
        self.spinBox_ctRatio.setValue(1)
        rc_layout.addRow("CT变比:", self.spinBox_ctRatio)

        self.spinBox_ptRatio = QtWidgets.QSpinBox()
        self.spinBox_ptRatio.setMinimum(1)
        self.spinBox_ptRatio.setMaximum(9999)
        self.spinBox_ptRatio.setValue(1)
        rc_layout.addRow("PT变比:", self.spinBox_ptRatio)

        right_col.addWidget(self.groupBox_ratioConfig)
        right_col.addStretch()

        tab2_layout.addLayout(right_col, 1)

        self.tabWidget.addTab(self.tab_settings, "设置")

        # ============================================================
        # 信号连接
        # ============================================================
        self.buttonGroup_wiringType.buttonClicked.connect(self._on_wiring_type_changed)

        # 通道树点击 → 切换对应 checkbox
        self.treeWidget_channels.itemClicked.connect(self._on_tree_item_clicked)
        # 通道树右键 → 弹出输入框选择菜单
        self.treeWidget_channels.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget_channels.customContextMenuRequested.connect(self._on_tree_context_menu)

        # 通道 checkbox 切换 → 自动填入对应输入框
        ch_boxes = [
            self.checkBox_ch_l1, self.checkBox_ch_l2,
            self.checkBox_ch_l3, self.checkBox_ch_l4,
            self.checkBox_ch_u1, self.checkBox_ch_u2,
            self.checkBox_ch_u3, self.checkBox_ch_u4,
        ]
        for cb in ch_boxes:
            cb.toggled.connect(lambda checked, text=cb.text(): self._on_channel_toggled(checked, text))

        QtCore.QMetaObject.connectSlotsByName(Dialog_DEWETRON_Setting)

    # ================================================================
    # 信号处理
    # ================================================================
    def _on_wiring_type_changed(self, btn):
        for type_id, b in self._wiring_buttons:
            if b.isChecked():
                self.wiringDiagramCanvas.set_wiring_type(type_id)
                self._create_slot_inputs(type_id)
                self._update_mapping_display()
                self._highlight_bound_channels()
                break

    def _on_tree_item_clicked(self, item, column):
        """通道树点击 → 切换对应 checkbox 状态。"""
        text = item.text(0)
        ch_map = {
            'AI 1/l1': self.checkBox_ch_l1, 'AI 1/l2': self.checkBox_ch_l2,
            'AI 1/l3': self.checkBox_ch_l3, 'AI 1/l4': self.checkBox_ch_l4,
            'AI 1/U1': self.checkBox_ch_u1, 'AI 1/U2': self.checkBox_ch_u2,
            'AI 1/U3': self.checkBox_ch_u3, 'AI 1/U4': self.checkBox_ch_u4,
        }
        cb = ch_map.get(text)
        if cb:
            cb.setChecked(not cb.isChecked())

    def _on_tree_context_menu(self, pos):
        """通道树右键 → 弹出输入框选择菜单，选中后绑定通道到该输入框。
        过滤规则：I 通道只显示 I 槽位，U 通道只显示 U 槽位。
        树结构: Power Groups > POWER/0 > 电流/电压 > 通道"""
        item = self.treeWidget_channels.itemAt(pos)
        # 检查是否为通道叶子节点（需要有 parent > parent > parent）
        if not item or not item.parent() or not item.parent().parent() or not item.parent().parent().parent():
            return
        ch_text = item.text(0)

        # 根据通道名判断类型：AI 1/U* → U 槽位，AI 1/l* / AI 1/I* → I 槽位
        is_voltage = '/U' in ch_text
        is_current = '/l' in ch_text or '/I' in ch_text

        menu = QtWidgets.QMenu(self.treeWidget_channels)
        menu.setStyleSheet("QMenu { font-size: 11px; padding: 4px; }")

        # 槽位 -> 组号映射
        slot_group_map = {'U1': '1', 'I1': '1', 'U2': '2', 'I2': '2', 'U3': '3', 'I3': '3'}

        # 检查此通道是否已被某个槽位占用
        occupied_slot = None
        for sname, sle in self._slot_input_widgets.items():
            if sle._channel == ch_text:
                occupied_slot = sname
                break

        for slot_name, le in self._slot_input_widgets.items():
            # 过滤：U 通道只显示 U 槽位，I 通道只显示 I 槽位
            if is_voltage and not slot_name.startswith('U'):
                continue
            if is_current and not slot_name.startswith('I'):
                continue
            # 如果通道已被占用，只显示占用的那个槽位
            if occupied_slot and slot_name != occupied_slot:
                continue
            # 如果通道未被占用，跳过已有其他通道的槽位
            if not occupied_slot and le._channel:
                continue
            group = slot_group_map.get(slot_name, '?')
            if le._channel:
                label = f"组{group} {slot_name}  (当前: {le._channel})"
            else:
                label = f"组{group} {slot_name}"
            action = menu.addAction(label)
            action.setData(slot_name)

        action = menu.exec_(self.treeWidget_channels.viewport().mapToGlobal(pos))
        if action:
            slot_name = action.data()
            if slot_name and slot_name in self._slot_input_widgets:
                self._slot_input_widgets[slot_name].set_channel(ch_text)
                self._highlight_bound_channels()

    def _create_slot_inputs(self, type_id):
        """根据接线类型创建对应的输入框（水平排列在图片下方），每组前加组号标签。"""
        # 清除旧的输入框
        while self._slot_list_layout.count():
            item = self._slot_list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        self._slot_input_widgets.clear()

        # 每个接线类型的分组定义: [(group_label, [slot_defs])]
        group_defs = {
            0: [('1', [('U1', 'U1'), ('I1', 'I1')])],                                                    # 1P2W
            1: [('1', [('U1', 'U1'), ('I1', 'I1')]),
                ('2', [('U2', 'U2'), ('I2', 'I2')])],                                                     # 1P3W
            2: [('1', [('U1', 'U1'), ('I1', 'I1')]),
                ('3', [('U3', 'U3'), ('I3', 'I3')])],                                                     # 2V2A
            3: [('1', [('U1', 'U1'), ('I1', 'I1')]),
                ('2', [('U2', 'U2'), ('I2', 'I2')]),
                ('3', [('U3', 'U3'), ('I3', 'I3')])],                                                     # 3P3W
            4: [('1', [('U1', 'U1'), ('I1', 'I1')]),
                ('2', [('U2', 'U2'), ('I2', 'I2')]),
                ('3', [('U3', 'U3'), ('I3', 'I3')])],                                                     # 3P4W
        }
        groups = group_defs.get(type_id, [])

        for group_label, slots in groups:
            # 组号标签
            lbl = QtWidgets.QLabel(f"组{group_label}")
            lbl.setFont(QtGui.QFont("Arial", 9, QtGui.QFont.Bold))
            lbl.setStyleSheet("color: #555; padding: 0 4px;")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self._slot_list_layout.addWidget(lbl)
            # 该组的输入框
            for slot_name, placeholder in slots:
                le = DraggableInputBox(slot_name)
                le.setPlaceholderText(placeholder)
                le.channelChanged.connect(lambda *_: self._update_mapping_display())
                le.channelChanged.connect(lambda *_: self._highlight_bound_channels())
                self._slot_input_widgets[slot_name] = le
                self._slot_list_layout.addWidget(le)

        self._slot_list_layout.addStretch()
        self._update_mapping_display()

    def _on_channel_toggled(self, checked, text):
        """checkbox 勾选/取消时，自动映射到对应输入框。"""
        # 确定映射的 slot
        slot = None
        if text == 'AI 1/l1': slot = 'I1'
        elif text == 'AI 1/l2': slot = 'I2'
        elif text == 'AI 1/l3': slot = 'I3'
        elif text == 'AI 1/l4': slot = 'I4'
        elif text == 'AI 1/U1': slot = 'U1'
        elif text == 'AI 1/U2': slot = 'U2'
        elif text == 'AI 1/U3': slot = 'U3'
        elif text == 'AI 1/U4': slot = 'U4'

        if slot and slot in self._slot_input_widgets:
            le = self._slot_input_widgets[slot]
            if checked:
                le.set_channel(text)
            else:
                le.clear_channel()
            self._update_mapping_display()
            self._highlight_bound_channels()

    def _update_mapping_display(self):
        """更新底部对应关系表格。"""
        # 清除旧行
        while self._mapping_layout.rowCount():
            self._mapping_layout.removeRow(0)
        self._mapping_labels.clear()

        for slot_name, le in self._slot_input_widgets.items():
            ch = le._channel or ''
            display = ch if ch else 'N/A'
            row_label = QtWidgets.QLabel(f"{slot_name}:")
            row_label.setFont(QtGui.QFont("Arial", 9, QtGui.QFont.Bold))
            row_val = QtWidgets.QLabel(display)
            row_val.setFont(QtGui.QFont("Arial", 9))
            if not ch:
                row_val.setStyleSheet("color: gray;")
            self._mapping_layout.addRow(row_label, row_val)
            self._mapping_labels[slot_name] = row_val

    def log(self, message):
        """向日志区域追加一行消息。"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.textEdit_log.append(f"[{timestamp}] {message}")
        # 自动滚动到底部
        sb = self.textEdit_log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def show_device_mapping(self, input_channels, channel_id_map):
        """显示设备原始 InputChannels 映射到对应关系区域。

        Args:
            input_channels: dict {slot: channel_id}，设备原始映射
            channel_id_map: dict {short_id: channel_id}，通道名到 ID 的映射
        """
        # 清除旧行
        while self._mapping_layout.rowCount():
            self._mapping_layout.removeRow(0)
        self._mapping_labels.clear()

        # 反向映射: channel_id -> short_id
        id_to_short = {cid: sid for sid, cid in channel_id_map.items()}

        for slot_name in sorted(input_channels.keys()):
            ch_id = input_channels[slot_name]
            if ch_id and ch_id != 18446744073709551615:  # UNUSED_CHANNEL_ID
                ch_name = id_to_short.get(ch_id, f'ID={ch_id}')
            else:
                ch_name = 'N/A'

            row_label = QtWidgets.QLabel(f"{slot_name}:")
            row_label.setFont(QtGui.QFont("Arial", 9, QtGui.QFont.Bold))
            row_val = QtWidgets.QLabel(ch_name)
            row_val.setFont(QtGui.QFont("Arial", 9))
            if ch_name == 'N/A':
                row_val.setStyleSheet("color: gray;")
            self._mapping_layout.addRow(row_label, row_val)
            self._mapping_labels[slot_name] = row_val

    def _highlight_bound_channels(self):
        """高亮通道树中已被绑定的通道，清除未绑定的高亮。"""
        # 收集所有已绑定的通道
        bound_channels = set()
        for le in self._slot_input_widgets.values():
            if le._channel:
                bound_channels.add(le._channel)

        # 遍历树中所有叶子节点（结构: Power Groups > POWER/0 > 电流/电压 > 通道）
        root = self.treeWidget_channels.invisibleRootItem()
        for i in range(root.childCount()):
            group = root.child(i)
            for j in range(group.childCount()):
                pw = group.child(j)
                for k in range(pw.childCount()):
                    subgroup = pw.child(k)
                    for m in range(subgroup.childCount()):
                        item = subgroup.child(m)
                        ch_text = item.text(0)
                        if ch_text in bound_channels:
                            item.setBackground(0, QtGui.QColor(200, 230, 255))
                        else:
                            item.setBackground(0, QtCore.Qt.transparent)
