# -*- coding: utf-8 -*-
"""
DEWETRON 功率分析仪设置对话框（手写 UI，无需 .ui 文件）。

布局：QTabWidget
  Tab 1: 接线图 — 顶部接线类型按钮 + 左侧通道列表 + 中间输入框列 + 右侧图片背景接线图
  Tab 2: 设置 — 基本配置 + 采样与测量配置 + 比例系数配置
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QButtonGroup, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLineEdit, QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation


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
        # 主布局（单页，不再使用 QTabWidget）
        # ============================================================
        self.tab_wiring = QWidget()
        tab1_layout = QVBoxLayout(self.tab_wiring)
        tab1_layout.setContentsMargins(8, 8, 8, 8)
        tab1_layout.setSpacing(6)

        main_layout = QVBoxLayout(Dialog_DEWETRON_Setting)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.tab_wiring)

        # --- 顶部：接线类型按钮栏 ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

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
            btn.setMinimumHeight(80)
            btn.setStyleSheet(
                "QPushButton { border: 2px solid #aaa; border-radius: 4px; "
                "font-size: 11px; padding: 4px; color: #333; }"
                "QPushButton:checked { border: 2px solid #0078d4; background-color: #e8f0fe; color: #000; }"
                "QPushButton:hover { border: 2px solid #666; }"
            )
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            setattr(self, attr_name, btn)
            self.buttonGroup_wiringType.addButton(btn, type_id)
            btn_layout.addWidget(btn)
            self._wiring_buttons.append((type_id, btn))

        # 默认选中 1P2W
        self.btn_wiring_1P2W.setChecked(True)

        tab1_layout.addLayout(btn_layout)

        # --- 使用提示（轮播 + 渐变 + 悬停展开） ---
        tips_bar = QtWidgets.QWidget()
        tips_bar.setStyleSheet(
            "background: #fff7e6; border: 1px solid #ffd591; border-left: 3px solid #fa8c16; "
            "border-radius: 3px;"
        )
        tips_layout = QtWidgets.QHBoxLayout(tips_bar)
        tips_layout.setContentsMargins(10, 5, 10, 5)
        tips_layout.setSpacing(6)
        tips_title = QtWidgets.QLabel("使用说明：")
        tips_title.setFont(QtGui.QFont("Microsoft YaHei", 9, QtGui.QFont.Bold))
        tips_title.setStyleSheet("color: #d4380d; background: transparent; border: none;")
        tips_layout.addWidget(tips_title)
        self._tips_text = QtWidgets.QLabel()
        self._tips_text.setFont(QtGui.QFont("Microsoft YaHei", 9))
        self._tips_text.setStyleSheet("color: #333; background: transparent; border: none;")
        tips_layout.addWidget(self._tips_text, 1)

        # 感叹号按钮 — 悬停时展示全部说明
        self._tips_all_btn = QtWidgets.QLabel("!")
        self._tips_all_btn.setFont(QtGui.QFont("Arial", 9, QtGui.QFont.Bold))
        self._tips_all_btn.setFixedSize(20, 20)
        self._tips_all_btn.setAlignment(QtCore.Qt.AlignCenter)
        self._tips_all_btn.setStyleSheet(
            "color: #fff; background: #fa8c16; border-radius: 10px;"
        )
        self._tips_all_btn.setCursor(QtCore.Qt.PointingHandCursor)
        all_tips_text = (
            "<b>使用说明</b><br>"
            "① 双击左侧通道列表中的电压/电流项，按顺序自动加入组1→组2→组3<br>"
            "② 右键点击通道可自由选择加入指定组<br>"
            "③ 双击下方输入框中已设置的通道可取消绑定"
        )
        self._tips_all_btn.setToolTip(all_tips_text)
        self._tips_all_btn.setStyleSheet(
            "color: #fff; background: #fa8c16; border-radius: 10px;"
            "QToolTip { background: #fff7e6; color: #333; border: 1px solid #ffd591; "
            "font-size: 11px; padding: 8px; }"
        )
        tips_layout.addWidget(self._tips_all_btn)
        tab1_layout.addWidget(tips_bar)

        # 轮播内容 + 渐变动画
        self._tips_list = [
            "双击左侧通道列表中的电压/电流项，按顺序自动加入组1 → 组2 → 组3",
            "右键点击通道可自由选择加入指定组",
            "双击下方输入框中已设置的通道可取消绑定",
        ]
        self._tips_index = 0
        self._tips_text.setText(self._tips_list[0])

        # 透明度效果 + 淡入动画
        self._tips_opacity = QGraphicsOpacityEffect(self._tips_text)
        self._tips_text.setGraphicsEffect(self._tips_opacity)
        self._tips_opacity.setOpacity(1.0)

        self._tips_fade_in = QPropertyAnimation(self._tips_opacity, b"opacity")
        self._tips_fade_in.setDuration(400)
        self._tips_fade_in.setStartValue(0.0)
        self._tips_fade_in.setEndValue(1.0)

        self._tips_timer = QtCore.QTimer()
        self._tips_timer.timeout.connect(self._rotate_tips)
        self._tips_timer.start(3000)

        # ================================================================
        # 左右布局：左侧（通道+接线图+对应关系） | 右侧（设备参数+日志）
        # ================================================================
        content_area = QHBoxLayout()
        content_area.setSpacing(8)

        # ============================================================
        # 左侧：通道树 + 接线图 + 输出标签 + 对应关系 + 按钮
        # ============================================================
        left_side = QVBoxLayout()
        left_side.setSpacing(4)

        # --- 中间区域：左(通道树) + 中(接线图+输入框) + 右(输出标签) ---
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
        power_group = QtWidgets.QTreeWidgetItem(self.treeWidget_channels, ["Power Groups"])
        power_group.setExpanded(True)
        pw0 = QtWidgets.QTreeWidgetItem(power_group, ["POWER/0"])
        pw0.setExpanded(True)

        voltage_group = QtWidgets.QTreeWidgetItem(pw0, ["电压 (U)"])
        voltage_group.setExpanded(True)
        for ch in ["AI 1/U1", "AI 1/U2", "AI 1/U3", "AI 1/U4"]:
            item = QtWidgets.QTreeWidgetItem(voltage_group, [ch])
            item.setFlags(item.flags() | QtCore.Qt.ItemIsDragEnabled)

        current_group = QtWidgets.QTreeWidgetItem(pw0, ["电流 (I)"])
        current_group.setExpanded(True)
        for ch in ["AI 1/l1", "AI 1/l2", "AI 1/l3", "AI 1/l4"]:
            item = QtWidgets.QTreeWidgetItem(current_group, [ch])
            item.setFlags(item.flags() | QtCore.Qt.ItemIsDragEnabled)

        left_panel.addWidget(self.treeWidget_channels, 1)

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

        left_side.addLayout(main_area, 1)

        # -- 底部：对应关系 + 操作按钮 --
        bottom_layout = QHBoxLayout()

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

        btn_col = QVBoxLayout()
        btn_col.setSpacing(6)
        self.pushButton_ApplySettings = QtWidgets.QPushButton(self.tab_wiring)
        self.pushButton_ApplySettings.setText("保存")
        self.pushButton_ApplySettings.setMinimumSize(130, 36)
        btn_col.addWidget(self.pushButton_ApplySettings)
        self.pushButton_BuildTestPage = QtWidgets.QPushButton(self.tab_wiring)
        self.pushButton_BuildTestPage.setText("测试界面构造")
        self.pushButton_BuildTestPage.setMinimumSize(130, 36)
        btn_col.addWidget(self.pushButton_BuildTestPage)
        btn_col.addStretch()
        bottom_layout.addLayout(btn_col)

        left_side.addLayout(bottom_layout)
        content_area.addLayout(left_side, 1)

        # ============================================================
        # 右侧：设备参数 + 日志
        # ============================================================
        right_side_widget = QWidget()
        right_side = QVBoxLayout(right_side_widget)
        right_side.setSpacing(6)
        right_side.setContentsMargins(0, 0, 0, 0)
        right_side_widget.setMaximumWidth(320)

        # -- 设备参数 --
        params_group = QtWidgets.QGroupBox("设备参数")
        params_layout = QtWidgets.QFormLayout(params_group)
        params_layout.setSpacing(8)

        ip_row = QtWidgets.QHBoxLayout()
        self.lineEdit_deviceIP = QtWidgets.QLineEdit("192.168.40.21")
        self.lineEdit_deviceIP.setMaximumWidth(160)
        ip_row.addWidget(self.lineEdit_deviceIP)
        port_lbl = QtWidgets.QLabel("  端口:")
        port_lbl.setFont(QtGui.QFont("Arial", 9))
        ip_row.addWidget(port_lbl)
        self.lineEdit_port = QtWidgets.QLineEdit("10001")
        self.lineEdit_port.setMaximumWidth(80)
        ip_row.addWidget(self.lineEdit_port)
        ip_row.addStretch()
        params_layout.addRow("设备IP:", ip_row)

        self.comboBox_frequencyChannel = QtWidgets.QComboBox()
        self.comboBox_frequencyChannel.addItems(["AI 1/U1", "AI 1/U2", "AI 1/U3", "AI 1/U4"])
        self.comboBox_frequencyChannel.setCurrentText("AI 1/U1")
        self.comboBox_frequencyChannel.setMaximumWidth(200)
        params_layout.addRow("输入通道:", self.comboBox_frequencyChannel)

        self.comboBox_maxRefreshRate = QtWidgets.QComboBox()
        self.comboBox_maxRefreshRate.addItems(["Default", "100", "50", "20", "10", "5", "2", "1"])
        self.comboBox_maxRefreshRate.setCurrentText("Default")
        self.comboBox_maxRefreshRate.setMaximumWidth(150)
        params_layout.addRow("最大刷新率:", self.comboBox_maxRefreshRate)

        self.comboBox_downsampling = QtWidgets.QComboBox()
        self.comboBox_downsampling.addItems(["Auto", "关", "2", "3", "4", "5"])
        self.comboBox_downsampling.setCurrentText("Auto")
        self.comboBox_downsampling.setMaximumWidth(150)
        params_layout.addRow("通道二次采样:", self.comboBox_downsampling)

        right_side.addWidget(params_group)

        # -- 加载配置按钮 --
        self.pushButton_LoadLastConfig = QtWidgets.QPushButton(self.tab_wiring)
        self.pushButton_LoadLastConfig.setText("加载配置文件")
        self.pushButton_LoadLastConfig.setMinimumSize(130, 36)
        self.pushButton_LoadLastConfig.setStyleSheet(
            "QPushButton { color: #1e293b; background-color: #d1d5db; border: 1px solid #9ca3af; "
            "border-radius: 4px; padding: 6px 14px; font-size: 13px; }"
            "QPushButton:hover { background-color: #bcc3ce; }"
        )
        right_side.addWidget(self.pushButton_LoadLastConfig)

        right_side.addStretch()

        content_area.addWidget(right_side_widget)
        tab1_layout.addLayout(content_area, 1)

        # -- 日志（底部） --
        log_group = QtWidgets.QGroupBox("日志")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(4, 4, 4, 4)
        self.textEdit_log = QtWidgets.QTextEdit()
        self.textEdit_log.setReadOnly(True)
        self.textEdit_log.setFont(QtGui.QFont("Consolas", 9))
        self.textEdit_log.setStyleSheet("QTextEdit { background: #1e1e1e; color: #d4d4d4; }")
        self.textEdit_log.setMinimumHeight(80)
        self.textEdit_log.setMaximumHeight(120)
        log_layout.addWidget(self.textEdit_log)
        tab1_layout.addWidget(log_group)

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
                # 更新输入通道下拉框：默认选择组1的U通道
                self._update_frequency_channel_default()
                break

    def _update_frequency_channel_default(self):
        """根据当前接线类型，更新输入通道下拉框的默认值（组1的U通道）。"""
        # 组1的U通道始终是 U1
        self.comboBox_frequencyChannel.setCurrentText("AI 1/U1")

    def _on_u1_channel_changed(self, slot_name, channel_text):
        """组1 U通道变化时，同步更新输入通道下拉框。"""
        if channel_text:
            # 检查通道是否在下拉框选项中
            idx = self.comboBox_frequencyChannel.findText(channel_text)
            if idx >= 0:
                self.comboBox_frequencyChannel.setCurrentIndex(idx)

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
                # U1 变化时同步更新输入通道下拉框
                if slot_name == 'U1':
                    le.channelChanged.connect(self._on_u1_channel_changed)
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

    def _rotate_tips(self):
        """轮播切换使用说明（渐变效果）。"""
        self._tips_index = (self._tips_index + 1) % len(self._tips_list)
        self._tips_fade_in.stop()
        self._tips_opacity.setOpacity(0.0)
        self._tips_text.setText(self._tips_list[self._tips_index])
        self._tips_fade_in.start()

    def show_config_list(self):
        """弹出配置文件列表，选择后加载到 UI。"""
        import os, re

        base_dir = os.path.dirname(os.path.abspath(__file__))
        save_dir = os.path.join(base_dir, 'command_save_files', 'dewetron_data')

        # 获取配置文件列表（排除 verify_ 文件）
        if not os.path.isdir(save_dir):
            self.log("配置目录不存在")
            return
        files = [f for f in os.listdir(save_dir)
                 if f.startswith('dewetron_') and not f.startswith('dewetron_verify_') and f.endswith('.xml')]
        if not files:
            self.log("无已保存的配置文件")
            return
        files.sort(reverse=True)

        # 弹出选择对话框
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem
        dialog = QDialog(self._tab_parent() if hasattr(self, '_tab_parent') else None)
        dialog.setWindowTitle("选择配置文件")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        hint = QLabel("选择要加载的配置文件（仅回显 UI，不触发保存）：")
        hint.setFont(QtGui.QFont("Microsoft YaHei", 9))
        layout.addWidget(hint)

        list_widget = QListWidget()
        list_widget.setFont(QtGui.QFont("Consolas", 10))
        for f in files:
            # 解析日期显示
            from DialogFileManager import _parse_date_from_filename
            dt = _parse_date_from_filename(f)
            date_str = dt.strftime("%Y-%m-%d %H:%M") if dt else "未知日期"
            item = QListWidgetItem(f"  {f}    ({date_str})")
            item.setData(QtCore.Qt.UserRole, os.path.join(save_dir, f))
            list_widget.addItem(item)
        list_widget.setCurrentRow(0)
        layout.addWidget(list_widget, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        rename_btn = QPushButton("另存为")
        rename_btn.setMinimumSize(80, 30)
        rename_btn.setStyleSheet("color: #1890ff;")
        load_btn = QPushButton("加载")
        load_btn.setMinimumSize(80, 30)
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumSize(80, 30)
        btn_row.addWidget(rename_btn)
        btn_row.addWidget(load_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        def refresh_list():
            """刷新文件列表。"""
            list_widget.clear()
            nonlocal files
            files = [f for f in os.listdir(save_dir)
                     if f.startswith('dewetron_') and not f.startswith('dewetron_verify_') and f.endswith('.xml')]
            files.sort(reverse=True)
            for f in files:
                from DialogFileManager import _parse_date_from_filename
                dt = _parse_date_from_filename(f)
                date_str = dt.strftime("%Y-%m-%d %H:%M") if dt else "未知日期"
                item = QListWidgetItem(f"  {f}    ({date_str})")
                item.setData(QtCore.Qt.UserRole, os.path.join(save_dir, f))
                list_widget.addItem(item)
            if list_widget.count() > 0:
                list_widget.setCurrentRow(0)

        def on_rename():
            item = list_widget.currentItem()
            if not item:
                return
            old_path = item.data(QtCore.Qt.UserRole)
            old_name = os.path.basename(old_path)
            # 提取日期时间部分，如 dewetron_20260610_09
            import re as _re
            m = _re.match(r'(dewetron_\d{8}_\d{2})', old_name)
            prefix = m.group(1) if m else "dewetron_copy"

            from PyQt5.QtWidgets import QInputDialog, QMessageBox
            new_name, ok = QInputDialog.getText(
                dialog, "另存为", f"输入配置名称（将自动加前缀 {prefix}_）：\n（当前: {old_name}）",
                text=""
            )
            if ok and new_name:
                if not new_name.endswith('.xml'):
                    new_name += '.xml'
                final_name = f"{prefix}_{new_name}"
                new_path = os.path.join(save_dir, final_name)
                if os.path.exists(new_path):
                    QMessageBox.warning(dialog, "失败", f"文件 {final_name} 已存在")
                    return
                try:
                    import shutil
                    shutil.copy2(old_path, new_path)
                    self.log(f"复制配置: {old_name} -> {final_name}")
                    refresh_list()
                except Exception as e:
                    self.log(f"复制失败: {e}")

        def on_load():
            item = list_widget.currentItem()
            if item:
                filepath = item.data(QtCore.Qt.UserRole)
                dialog.accept()
                self._load_config_file(filepath)
        def on_cancel():
            dialog.reject()

        rename_btn.clicked.connect(on_rename)
        load_btn.clicked.connect(on_load)
        cancel_btn.clicked.connect(on_cancel)
        list_widget.itemDoubleClicked.connect(lambda: on_load())

        dialog.exec_()

    def _load_config_file(self, filepath):
        """加载指定配置文件，回显到 UI（不触发保存）。"""
        import os, re

        with open(filepath, 'r', encoding='utf-8') as f:
            xml = f.read()
        self.log(f"加载配置: {os.path.basename(filepath)}")

        # 接线类型
        WIRING_MAP = {'AC_1P2W': 0, 'AC_1P3W': 1, 'AC_2V2A': 2, 'AC_3P3W': 3, 'AC_3P4W': 4}
        wiring_match = re.search(r'POWER/WiringType"><EnumValue enum="PowerWiringType">([^<]+)', xml)
        if wiring_match:
            wiring_str = wiring_match.group(1)
            wiring_id = WIRING_MAP.get(wiring_str, 0)
            for type_id, btn in self._wiring_buttons:
                if type_id == wiring_id:
                    btn.setChecked(True)
                    self._on_wiring_type_changed(btn)
                    self.log(f"  接线类型: {wiring_str}")
                    break

        # InputChannels 映射 → 延迟回填（等接线图初始化完成）
        QtCore.QTimer.singleShot(100, lambda: self._fill_channels_from_xml(xml))

        # 输入通道 (FrequencyChannel)
        fc_match = re.search(r'POWER/FrequencyChannel"><ChannelID>(\d+)</ChannelID>', xml)
        if fc_match:
            fc_id = int(fc_match.group(1))
            for ch_match in re.finditer(r'<Channel id="(\d+)">(.*?)</Channel>', xml, re.DOTALL):
                if int(ch_match.group(1)) == fc_id:
                    sid = re.search(r'ShortId"><StringValue>"([^"]+)"', ch_match.group(2))
                    if sid:
                        ch_name = sid.group(1)
                        idx = self.comboBox_frequencyChannel.findText(ch_name)
                        if idx >= 0:
                            self.comboBox_frequencyChannel.setCurrentIndex(idx)
                            self.log(f"  输入通道: {ch_name}")
                        break

        # 最大刷新率
        rate_match = re.search(r'POWER/MaxUpdateRate"><StringValue>"?(\d+)"?', xml)
        if rate_match:
            rate_val = rate_match.group(1)
            idx = self.comboBox_maxRefreshRate.findText(rate_val)
            if idx >= 0:
                self.comboBox_maxRefreshRate.setCurrentIndex(idx)
                self.log(f"  最大刷新率: {rate_val}")

        # 通道二次采样
        DS_REVERSE = {'Off': '关', 'Auto': 'Auto'}
        ds_match = re.search(r'POWER/DataSubsampling"><StringValue>"?([^"<]+)"?', xml)
        if ds_match:
            ds_xml = ds_match.group(1)
            ds_ui = DS_REVERSE.get(ds_xml, ds_xml)
            idx = self.comboBox_downsampling.findText(ds_ui)
            if idx >= 0:
                self.comboBox_downsampling.setCurrentIndex(idx)
                self.log(f"  通道二次采样: {ds_ui}")

        self.log("配置加载完成")

    def _fill_channels_from_xml(self, xml):
        """从 XML 的 InputChannels 回填通道输入框。"""
        import re

        # 收集所有 ChannelID -> ShortId 映射
        id_to_name = {}
        for ch_match in re.finditer(r'<Channel id="(\d+)">(.*?)</Channel>', xml, re.DOTALL):
            ch_id = int(ch_match.group(1))
            sid = re.search(r'ShortId"><StringValue>"([^"]+)"', ch_match.group(2))
            if sid:
                id_to_name[ch_id] = sid.group(1)

        # 解析 InputChannels
        for m in re.finditer(r'POWER/InputChannels/(U\d|I\d)"><ChannelID>(\d+)</ChannelID>', xml):
            slot = m.group(1)
            ch_id = int(m.group(2))
            if slot in self._slot_input_widgets:
                if ch_id != 18446744073709551615:  # UNUSED
                    ch_name = id_to_name.get(ch_id, '')
                    if ch_name:
                        self._slot_input_widgets[slot].set_channel(ch_name)
                        self.log(f"  {slot} <- {ch_name}")
                else:
                    self._slot_input_widgets[slot].clear_channel()

        self._update_mapping_display()
        self._highlight_bound_channels()
        # 同步输入通道到组1的U
        if 'U1' in self._slot_input_widgets:
            u1_ch = self._slot_input_widgets['U1']._channel
            if u1_ch:
                idx = self.comboBox_frequencyChannel.findText(u1_ch)
                if idx >= 0:
                    self.comboBox_frequencyChannel.setCurrentIndex(idx)
