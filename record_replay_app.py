import sys
import os
import time
import json
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTabWidget, QPushButton, QLabel, QLineEdit, QComboBox,
    QTextEdit, QGroupBox, QCheckBox, QSpinBox, QFileDialog,
    QListWidget, QListWidgetItem, QSplitter, QMessageBox, QProgressBar
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QRect, QPoint, QSize
)
from PyQt5.QtGui import (
    QPixmap, QImage, QPainter, QPen, QColor, QFont, QBrush
)
import pyautogui
import keyboard
from PIL import ImageGrab

# 设置pyautogui的安全性设置
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01

class ActionRecorder(QThread):
    """动作录制线程"""
    action_recorded = pyqtSignal(dict)
    recording_stopped = pyqtSignal()
    
    def __init__(self, mode="simple"):
        super().__init__()
        self.mode = mode
        self.is_recording = False
        self.start_time = 0
        self.actions = []
        self.pressed_modifiers = set()  # 记录当前按下的修饰键
        
    def run(self):
        self.is_recording = True
        self.start_time = time.time()
        self.actions = []
        self.pressed_modifiers = set()
        
        # 记录初始分辨率
        self.screen_width, self.screen_height = pyautogui.size()
        
        # 监听鼠标事件
        def on_mouse_move(x, y):
            if self.is_recording:
                elapsed = time.time() - self.start_time
                action = {
                    "action_type": "mouse_move",
                    "timestamp": elapsed,
                    "x": x,
                    "y": y,
                    "button": None,
                    "dx": None,
                    "dy": None,
                    "key": None
                }
                self.actions.append(action)
                self.action_recorded.emit(action)
        
        def on_mouse_click(x, y, button, pressed):
            if self.is_recording and pressed:
                elapsed = time.time() - self.start_time
                action = {
                    "action_type": "mouse_click",
                    "timestamp": elapsed,
                    "x": x,
                    "y": y,
                    "button": button,
                    "dx": None,
                    "dy": None,
                    "key": None
                }
                self.actions.append(action)
                self.action_recorded.emit(action)
        
        def on_mouse_scroll(x, y, dx, dy):
            if self.is_recording:
                elapsed = time.time() - self.start_time
                action = {
                    "action_type": "mouse_scroll",
                    "timestamp": elapsed,
                    "x": x,
                    "y": y,
                    "button": None,
                    "dx": dx,
                    "dy": dy,
                    "key": None
                }
                self.actions.append(action)
                self.action_recorded.emit(action)
        
        def on_key_event(event):
            if not self.is_recording:
                return
            
            elapsed = time.time() - self.start_time
            key = event.name
            
            # 处理修饰键
            modifiers = {"ctrl", "alt", "shift", "cmd"}
            
            if event.event_type == "down":
                if key in modifiers:
                    self.pressed_modifiers.add(key)
                else:
                    # 普通键按下，直接记录
                    action = {
                        "action_type": "key_press",
                        "timestamp": elapsed,
                        "x": None,
                        "y": None,
                        "button": None,
                        "dx": None,
                        "dy": None,
                        "key": key
                    }
                    self.actions.append(action)
                    self.action_recorded.emit(action)
            
            elif event.event_type == "up":
                if key in modifiers:
                    # 修饰键释放，检查是否还有其他修饰键按下
                    if key in self.pressed_modifiers:
                        self.pressed_modifiers.remove(key)
                    
                    # 如果没有其他修饰键按下，记录修饰键释放
                    if not self.pressed_modifiers:
                        action = {
                            "action_type": "key_release",
                            "timestamp": elapsed,
                            "x": None,
                            "y": None,
                            "button": None,
                            "dx": None,
                            "dy": None,
                            "key": key
                        }
                        self.actions.append(action)
                        self.action_recorded.emit(action)
                else:
                    # 普通键释放，不需要记录
                    pass
        
        # 注册监听器
        keyboard.hook(on_key_event)
        
        # 鼠标事件监听循环
        last_x, last_y = pyautogui.position()
        while self.is_recording:
            current_x, current_y = pyautogui.position()
            if current_x != last_x or current_y != last_y:
                on_mouse_move(current_x, current_y)
                last_x, last_y = current_x, current_y
            time.sleep(0.01)
        
        # 清理监听器
        keyboard.unhook_all()
        self.recording_stopped.emit()
    
    def stop(self):
        self.is_recording = False
    
    def get_actions(self):
        return self.actions
    
    def get_screen_resolution(self):
        return (self.screen_width, self.screen_height)

class ActionReplayer(QThread):
    """动作复刻线程"""
    replay_progress = pyqtSignal(int)
    replay_finished = pyqtSignal()
    replay_error = pyqtSignal(str)
    
    def __init__(self, actions, recorded_resolution):
        super().__init__()
        self.actions = actions
        self.recorded_resolution = recorded_resolution
        self.is_replaying = False
    
    def run(self):
        self.is_replaying = True
        
        # 获取当前屏幕分辨率
        current_width, current_height = pyautogui.size()
        
        # 计算分辨率缩放比例
        scale_x = current_width / self.recorded_resolution[0]
        scale_y = current_height / self.recorded_resolution[1]
        
        try:
            total_actions = len(self.actions)
            for i, action in enumerate(self.actions):
                if not self.is_replaying:
                    break
                
                # 更新进度
                progress = int((i + 1) / total_actions * 100)
                self.replay_progress.emit(progress)
                
                # 计算延迟
                if i > 0:
                    delay = action["timestamp"] - self.actions[i-1]["timestamp"]
                    time.sleep(max(0, delay))
                
                # 根据动作类型执行不同的操作
                action_type = action["action_type"]
                
                if action_type == "mouse_move":
                    x = int(action["x"] * scale_x)
                    y = int(action["y"] * scale_y)
                    pyautogui.moveTo(x, y)
                
                elif action_type == "mouse_click":
                    x = int(action["x"] * scale_x)
                    y = int(action["y"] * scale_y)
                    button = action["button"]
                    pyautogui.click(x, y, button=button)
                
                elif action_type == "mouse_scroll":
                    dx = action["dx"]
                    dy = action["dy"]
                    pyautogui.scroll(dy)
                
                elif action_type == "key_press":
                    key = action["key"]
                    keyboard.press(key)
                
                elif action_type == "key_release":
                    key = action["key"]
                    keyboard.release(key)
            
            self.replay_finished.emit()
        except Exception as e:
            self.replay_error.emit(str(e))
    
    def stop(self):
        self.is_replaying = False

class CVRecognizer:
    """CV识别类，用于图像匹配"""
    
    @staticmethod
    def find_image_on_screen(template_path, threshold=0.8):
        """在屏幕上查找指定图像"""
        # 截取当前屏幕
        screen = np.array(ImageGrab.grab())
        screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        
        # 读取模板图像
        template = cv2.imread(template_path, 0)
        if template is None:
            return None
        
        # 模板匹配
        res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        
        # 返回第一个匹配位置
        if len(loc[0]) > 0:
            return (int(loc[1][0]), int(loc[0][0]))
        return None
    
    @staticmethod
    def capture_screen_region(region=None):
        """捕获屏幕区域"""
        if region:
            screen = np.array(ImageGrab.grab(bbox=region))
        else:
            screen = np.array(ImageGrab.grab())
        return screen

class StepWidget(QWidget):
    """序列模式中的步骤组件"""
    step_changed = pyqtSignal(dict)
    
    def __init__(self, step_data=None, parent=None):
        super().__init__(parent)
        self.step_data = step_data or {
            "id": str(time.time()),
            "name": f"Step_{int(time.time())}",
            "reference_origin": "global",
            "operation_mode": "mouse",
            "operation_time": 0,
            "delay_time": 1,
            "action": {},
            "screenshot_path": "",
            "click_type": "single"
        }
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QGridLayout()
        
        basic_layout.addWidget(QLabel("步骤名称:"), 0, 0)
        self.name_edit = QLineEdit(self.step_data["name"])
        self.name_edit.textChanged.connect(self.on_step_changed)
        basic_layout.addWidget(self.name_edit, 0, 1)
        
        basic_layout.addWidget(QLabel("参考坐标原点:"), 1, 0)
        self.origin_combo = QComboBox()
        self.origin_combo.addItem("global")
        # TODO: 动态添加截图选项
        self.origin_combo.setCurrentText(self.step_data["reference_origin"])
        self.origin_combo.currentTextChanged.connect(self.on_step_changed)
        basic_layout.addWidget(self.origin_combo, 1, 1)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 操作设置
        operation_group = QGroupBox("操作设置")
        operation_layout = QGridLayout()
        
        operation_layout.addWidget(QLabel("操作模式:"), 0, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["mouse", "keyboard"])
        self.mode_combo.setCurrentText(self.step_data["operation_mode"])
        self.mode_combo.currentTextChanged.connect(self.on_step_changed)
        self.mode_combo.currentTextChanged.connect(self.update_operation_fields)
        operation_layout.addWidget(self.mode_combo, 0, 1)
        
        operation_layout.addWidget(QLabel("延迟时间(秒):"), 1, 0)
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 60)
        self.delay_spin.setValue(self.step_data["delay_time"])
        self.delay_spin.valueChanged.connect(self.on_step_changed)
        operation_layout.addWidget(self.delay_spin, 1, 1)
        
        # 鼠标操作字段
        self.mouse_group = QGroupBox("鼠标操作")
        mouse_layout = QVBoxLayout()
        
        self.click_type_combo = QComboBox()
        self.click_type_combo.addItems(["single", "double"])
        self.click_type_combo.setCurrentText(self.step_data.get("click_type", "single"))
        self.click_type_combo.currentTextChanged.connect(self.on_step_changed)
        mouse_layout.addWidget(QLabel("点击类型:"))
        mouse_layout.addWidget(self.click_type_combo)
        
        self.screenshot_check = QCheckBox("使用截图进行CV识别")
        self.screenshot_check.stateChanged.connect(self.on_step_changed)
        mouse_layout.addWidget(self.screenshot_check)
        
        self.screenshot_btn = QPushButton("截取屏幕")
        self.screenshot_btn.clicked.connect(self.capture_screenshot)
        mouse_layout.addWidget(self.screenshot_btn)
        
        self.screenshot_label = QLabel("截图预览")
        self.screenshot_label.setAlignment(Qt.AlignCenter)
        self.screenshot_label.setFixedHeight(100)
        mouse_layout.addWidget(self.screenshot_label)
        
        self.test_btn = QPushButton("测试操作")
        self.test_btn.clicked.connect(self.test_operation)
        mouse_layout.addWidget(self.test_btn)
        
        self.mouse_group.setLayout(mouse_layout)
        
        # 键盘操作字段
        self.keyboard_group = QGroupBox("键盘操作")
        keyboard_layout = QVBoxLayout()
        
        self.keyboard_mode_combo = QComboBox()
        self.keyboard_mode_combo.addItems(["输入字符串", "功能键操作"])
        self.keyboard_mode_combo.currentTextChanged.connect(self.on_step_changed)
        self.keyboard_mode_combo.currentTextChanged.connect(self.update_keyboard_fields)
        keyboard_layout.addWidget(QLabel("键盘操作模式:"))
        keyboard_layout.addWidget(self.keyboard_mode_combo)
        
        # 输入字符串模式
        self.text_input_group = QGroupBox("输入字符串")
        text_input_layout = QVBoxLayout()
        self.text_edit = QLineEdit()
        text_input_layout.addWidget(self.text_edit)
        self.text_input_group.setLayout(text_input_layout)
        
        # 功能键操作模式
        self.hotkey_group = QGroupBox("功能键操作")
        hotkey_layout = QVBoxLayout()
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setReadOnly(True)
        hotkey_layout.addWidget(self.hotkey_edit)
        self.record_hotkey_btn = QPushButton("录制快捷键")
        self.record_hotkey_btn.clicked.connect(self.record_hotkey)
        hotkey_layout.addWidget(self.record_hotkey_btn)
        self.hotkey_group.setLayout(hotkey_layout)
        
        keyboard_layout.addWidget(self.text_input_group)
        keyboard_layout.addWidget(self.hotkey_group)
        self.keyboard_group.setLayout(keyboard_layout)
        
        operation_layout.addWidget(self.mouse_group, 2, 0, 1, 2)
        operation_layout.addWidget(self.keyboard_group, 3, 0, 1, 2)
        
        operation_group.setLayout(operation_layout)
        layout.addWidget(operation_group)
        
        self.setLayout(layout)
        
        # 初始更新字段显示
        self.update_operation_fields()
        self.update_keyboard_fields()
        
        # 更新截图预览
        if self.step_data.get("screenshot_path"):
            self.update_screenshot_preview(self.step_data["screenshot_path"])
    
    def update_operation_fields(self):
        """根据操作模式更新显示字段"""
        mode = self.mode_combo.currentText()
        self.mouse_group.setVisible(mode == "mouse")
        self.keyboard_group.setVisible(mode == "keyboard")
    
    def update_keyboard_fields(self):
        """根据键盘操作模式更新显示字段"""
        mode = self.keyboard_mode_combo.currentText()
        self.text_input_group.setVisible(mode == "输入字符串")
        self.hotkey_group.setVisible(mode == "功能键操作")
    
    def on_step_changed(self):
        """步骤数据变化时更新"""
        self.step_data["name"] = self.name_edit.text()
        self.step_data["reference_origin"] = self.origin_combo.currentText()
        self.step_data["operation_mode"] = self.mode_combo.currentText()
        self.step_data["delay_time"] = self.delay_spin.value()
        
        if self.step_data["operation_mode"] == "mouse":
            self.step_data["click_type"] = self.click_type_combo.currentText()
            self.step_data["use_screenshot"] = self.screenshot_check.isChecked()
        else:
            keyboard_mode = self.keyboard_mode_combo.currentText()
            if keyboard_mode == "输入字符串":
                self.step_data["keyboard_action"] = {
                    "type": "text",
                    "value": self.text_edit.text()
                }
            else:
                self.step_data["keyboard_action"] = {
                    "type": "hotkey",
                    "value": self.hotkey_edit.text()
                }
        
        self.step_changed.emit(self.step_data)
    
    def capture_screenshot(self):
        """截取屏幕"""
        # TODO: 实现截图功能
        screenshot_dir = "screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        
        timestamp = int(time.time())
        screenshot_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
        
        # 截取全屏
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        
        self.step_data["screenshot_path"] = screenshot_path
        self.update_screenshot_preview(screenshot_path)
        self.on_step_changed()
    
    def update_screenshot_preview(self, screenshot_path):
        """更新截图预览"""
        if os.path.exists(screenshot_path):
            pixmap = QPixmap(screenshot_path)
            # 缩放截图以适应预览区域
            scaled_pixmap = pixmap.scaled(
                self.screenshot_label.width(), self.screenshot_label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.screenshot_label.setPixmap(scaled_pixmap)
    
    def test_operation(self):
        """测试当前操作"""
        if self.step_data["operation_mode"] == "mouse":
            # TODO: 实现鼠标操作测试
            QMessageBox.information(self, "测试", "鼠标操作测试功能待实现")
        else:
            # TODO: 实现键盘操作测试
            QMessageBox.information(self, "测试", "键盘操作测试功能待实现")
    
    def record_hotkey(self):
        """录制快捷键"""
        # TODO: 实现快捷键录制功能
        QMessageBox.information(self, "录制快捷键", "快捷键录制功能待实现")

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("录制/复刻鼠标键盘操作")
        self.setGeometry(100, 100, 1000, 700)
        
        # 初始化变量
        self.current_mode = "simple"  # simple or sequence
        self.recording_thread = None
        self.replaying_thread = None
        self.current_sequence = []
        self.recorded_actions = []
        self.recorded_resolution = pyautogui.size()
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 简易模式标签
        self.simple_tab = QWidget()
        self.tab_widget.addTab(self.simple_tab, "简易模式")
        self.init_simple_mode_ui()
        
        # 序列模式标签
        self.sequence_tab = QWidget()
        self.tab_widget.addTab(self.sequence_tab, "序列模式")
        self.init_sequence_mode_ui()
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def init_simple_mode_ui(self):
        """初始化简易模式UI"""
        layout = QVBoxLayout(self.simple_tab)
        
        # 控制面板
        control_group = QGroupBox("录制控制")
        control_layout = QHBoxLayout()
        
        self.start_record_btn = QPushButton("开始录制")
        self.start_record_btn.clicked.connect(self.start_recording)
        control_layout.addWidget(self.start_record_btn)
        
        self.stop_record_btn = QPushButton("停止录制")
        self.stop_record_btn.setEnabled(False)
        self.stop_record_btn.clicked.connect(self.stop_recording)
        control_layout.addWidget(self.stop_record_btn)
        
        self.save_btn = QPushButton("保存录制")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_recording)
        control_layout.addWidget(self.save_btn)
        
        self.load_btn = QPushButton("加载录制")
        self.load_btn.clicked.connect(self.load_recording)
        control_layout.addWidget(self.load_btn)
        
        self.replay_btn = QPushButton("开始复刻")
        self.replay_btn.setEnabled(False)
        self.replay_btn.clicked.connect(self.start_replaying)
        control_layout.addWidget(self.replay_btn)
        
        self.stop_replay_btn = QPushButton("停止复刻")
        self.stop_replay_btn.setEnabled(False)
        self.stop_replay_btn.clicked.connect(self.stop_replaying)
        control_layout.addWidget(self.stop_replay_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 录制信息
        info_layout = QHBoxLayout()
        
        self.duration_label = QLabel("录制时长: 0.0秒")
        info_layout.addWidget(self.duration_label)
        
        self.actions_count_label = QLabel("动作数量: 0")
        info_layout.addWidget(self.actions_count_label)
        
        self.resolution_label = QLabel(f"屏幕分辨率: {pyautogui.size()[0]}x{pyautogui.size()[1]}")
        info_layout.addWidget(self.resolution_label)
        
        layout.addLayout(info_layout)
        
        # 动作列表
        actions_group = QGroupBox("录制的动作")
        actions_layout = QVBoxLayout()
        
        self.actions_list = QTextEdit()
        self.actions_list.setReadOnly(True)
        actions_layout.addWidget(self.actions_list)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
    
    def init_sequence_mode_ui(self):
        """初始化序列模式UI"""
        layout = QVBoxLayout(self.sequence_tab)
        
        # 顶部控制栏
        top_layout = QHBoxLayout()
        
        self.new_sequence_btn = QPushButton("新建序列")
        self.new_sequence_btn.clicked.connect(self.new_sequence)
        top_layout.addWidget(self.new_sequence_btn)
        
        self.save_sequence_btn = QPushButton("保存序列")
        self.save_sequence_btn.clicked.connect(self.save_sequence)
        top_layout.addWidget(self.save_sequence_btn)
        
        self.load_sequence_btn = QPushButton("加载序列")
        self.load_sequence_btn.clicked.connect(self.load_sequence)
        top_layout.addWidget(self.load_sequence_btn)
        
        self.run_sequence_btn = QPushButton("运行序列")
        self.run_sequence_btn.clicked.connect(self.run_sequence)
        top_layout.addWidget(self.run_sequence_btn)
        
        layout.addLayout(top_layout)
        
        # 主分割器
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧步骤列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_group = QGroupBox("步骤列表")
        left_group_layout = QVBoxLayout()
        
        self.steps_list = QListWidget()
        self.steps_list.itemSelectionChanged.connect(self.on_step_selected)
        left_group_layout.addWidget(self.steps_list)
        
        steps_control_layout = QHBoxLayout()
        
        self.add_step_btn = QPushButton("添加步骤")
        self.add_step_btn.clicked.connect(self.add_step)
        steps_control_layout.addWidget(self.add_step_btn)
        
        self.remove_step_btn = QPushButton("删除步骤")
        self.remove_step_btn.clicked.connect(self.remove_step)
        steps_control_layout.addWidget(self.remove_step_btn)
        
        left_group_layout.addLayout(steps_control_layout)
        left_group.setLayout(left_group_layout)
        
        left_layout.addWidget(left_group)
        splitter.addWidget(left_widget)
        
        # 右侧步骤编辑
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.step_edit_widget = QWidget()
        self.step_edit_layout = QVBoxLayout(self.step_edit_widget)
        
        self.no_step_label = QLabel("请选择或添加一个步骤")
        self.no_step_label.setAlignment(Qt.AlignCenter)
        self.step_edit_layout.addWidget(self.no_step_label)
        
        right_layout.addWidget(self.step_edit_widget)
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setSizes([200, 600])
    
    def start_recording(self):
        """开始录制"""
        self.recording_thread = ActionRecorder(mode=self.current_mode)
        self.recording_thread.action_recorded.connect(self.on_action_recorded)
        self.recording_thread.recording_stopped.connect(self.on_recording_stopped)
        self.recording_thread.start()
        
        self.start_record_btn.setEnabled(False)
        self.stop_record_btn.setEnabled(True)
        self.statusBar().showMessage("正在录制...")
        
        # 清空之前的动作列表
        self.actions_list.clear()
        self.recorded_actions = []
    
    def stop_recording(self):
        """停止录制"""
        if self.recording_thread:
            self.recording_thread.stop()
            self.recording_thread.wait()
    
    def on_action_recorded(self, action):
        """记录动作"""
        self.recorded_actions.append(action)
        
        # 更新动作列表显示
        action_str = f"[{action['timestamp']:.2f}] {action['action_type']}"
        if action['action_type'] == 'mouse_move':
            action_str += f" - 位置: ({action['x']}, {action['y']})"
        elif action['action_type'] == 'mouse_click':
            action_str += f" - 位置: ({action['x']}, {action['y']}), 按钮: {action['button']}"
        elif action['action_type'] == 'key_press' or action['action_type'] == 'key_release':
            action_str += f" - 键: {action['key']}"
        
        self.actions_list.append(action_str)
        
        # 更新统计信息
        self.actions_count_label.setText(f"动作数量: {len(self.recorded_actions)}")
        if self.recorded_actions:
            duration = self.recorded_actions[-1]['timestamp']
            self.duration_label.setText(f"录制时长: {duration:.2f}秒")
    
    def on_recording_stopped(self):
        """录制停止时的处理"""
        self.start_record_btn.setEnabled(True)
        self.stop_record_btn.setEnabled(False)
        self.save_btn.setEnabled(True)
        self.replay_btn.setEnabled(True)
        self.statusBar().showMessage("录制完成")
        
        if self.recording_thread:
            self.recorded_resolution = self.recording_thread.get_screen_resolution()
    
    def save_recording(self):
        """保存录制"""
        if not self.recorded_actions:
            QMessageBox.warning(self, "警告", "没有可保存的录制内容")
            return
        
        # 选择保存文件
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存录制", "", "JSON Files (*.json)"
        )
        
        if file_path:
            # 构建配置文件
            config = {
                "version": "1.0",
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "total_duration": self.recorded_actions[-1]['timestamp'] if self.recorded_actions else 0,
                "recorded_resolution": {
                    "width": self.recorded_resolution[0],
                    "height": self.recorded_resolution[1]
                },
                "actions": self.recorded_actions
            }
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "成功", f"录制已保存到 {file_path}")
    
    def load_recording(self):
        """加载录制"""
        # 选择加载文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载录制", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.recorded_actions = config.get("actions", [])
                self.recorded_resolution = (
                    config["recorded_resolution"]["width"],
                    config["recorded_resolution"]["height"]
                )
                
                # 更新UI
                self.actions_list.clear()
                for action in self.recorded_actions:
                    self.on_action_recorded(action)
                
                self.save_btn.setEnabled(True)
                self.replay_btn.setEnabled(True)
                self.statusBar().showMessage(f"已加载 {len(self.recorded_actions)} 个动作")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载录制失败: {str(e)}")
    
    def start_replaying(self):
        """开始复刻"""
        if not self.recorded_actions:
            QMessageBox.warning(self, "警告", "没有可复刻的录制内容")
            return
        
        self.replaying_thread = ActionReplayer(self.recorded_actions, self.recorded_resolution)
        self.replaying_thread.replay_progress.connect(self.on_replay_progress)
        self.replaying_thread.replay_finished.connect(self.on_replay_finished)
        self.replaying_thread.replay_error.connect(self.on_replay_error)
        self.replaying_thread.start()
        
        self.replay_btn.setEnabled(False)
        self.stop_replay_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.statusBar().showMessage("正在复刻...")
    
    def stop_replaying(self):
        """停止复刻"""
        if self.replaying_thread:
            self.replaying_thread.stop()
            self.replaying_thread.wait()
    
    def on_replay_progress(self, progress):
        """复刻进度更新"""
        self.progress_bar.setValue(progress)
    
    def on_replay_finished(self):
        """复刻完成"""
        self.replay_btn.setEnabled(True)
        self.stop_replay_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("复刻完成")
    
    def on_replay_error(self, error):
        """复刻错误"""
        self.replay_btn.setEnabled(True)
        self.stop_replay_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("复刻失败")
        QMessageBox.critical(self, "错误", f"复刻失败: {error}")
    
    def new_sequence(self):
        """新建序列"""
        self.current_sequence = []
        self.steps_list.clear()
        self.update_step_edit_widget(None)
        self.statusBar().showMessage("已新建序列")
    
    def save_sequence(self):
        """保存序列"""
        if not self.current_sequence:
            QMessageBox.warning(self, "警告", "序列为空，无需保存")
            return
        
        # 选择保存文件
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存序列", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                # 构建序列配置
                sequence_config = {
                    "version": "1.0",
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    "steps": self.current_sequence
                }
                
                # 保存到文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(sequence_config, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "成功", f"序列已保存到 {file_path}")
                self.statusBar().showMessage(f"序列已保存到 {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存序列失败: {str(e)}")
    
    def load_sequence(self):
        """加载序列"""
        # 选择加载文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载序列", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    sequence_config = json.load(f)
                
                self.current_sequence = sequence_config.get("steps", [])
                self.update_steps_list()
                self.statusBar().showMessage(f"已加载序列，包含 {len(self.current_sequence)} 个步骤")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载序列失败: {str(e)}")
    
    def run_sequence(self):
        """运行序列"""
        if not self.current_sequence:
            QMessageBox.warning(self, "警告", "序列为空，无法运行")
            return
        
        # TODO: 实现序列运行功能
        QMessageBox.information(self, "提示", "序列运行功能待实现")
    
    def add_step(self):
        """添加步骤"""
        step_data = {
            "id": str(time.time()),
            "name": f"步骤 {len(self.current_sequence) + 1}",
            "reference_origin": "global",
            "operation_mode": "mouse",
            "operation_time": 0,
            "delay_time": 1,
            "click_type": "single",
            "use_screenshot": False
        }
        
        self.current_sequence.append(step_data)
        self.update_steps_list()
        
        # 选中新添加的步骤
        self.steps_list.setCurrentRow(len(self.current_sequence) - 1)
    
    def remove_step(self):
        """删除步骤"""
        current_row = self.steps_list.currentRow()
        if current_row >= 0:
            del self.current_sequence[current_row]
            self.update_steps_list()
            self.update_step_edit_widget(None)
    
    def update_steps_list(self):
        """更新步骤列表"""
        self.steps_list.clear()
        for step in self.current_sequence:
            item = QListWidgetItem(step["name"])
            item.setData(Qt.UserRole, step)
            self.steps_list.addItem(item)
    
    def on_step_selected(self):
        """选中步骤时更新编辑区域"""
        selected_items = self.steps_list.selectedItems()
        if selected_items:
            step_data = selected_items[0].data(Qt.UserRole)
            self.update_step_edit_widget(step_data)
        else:
            self.update_step_edit_widget(None)
    
    def update_step_edit_widget(self, step_data):
        """更新步骤编辑部件"""
        # 清空当前布局
        for i in reversed(range(self.step_edit_layout.count())):
            widget = self.step_edit_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        if step_data:
            # 创建步骤编辑组件
            step_widget = StepWidget(step_data)
            step_widget.step_changed.connect(self.on_step_changed)
            self.step_edit_layout.addWidget(step_widget)
        else:
            # 重新创建无步骤提示标签
            self.no_step_label = QLabel("请选择或添加一个步骤")
            self.no_step_label.setAlignment(Qt.AlignCenter)
            self.step_edit_layout.addWidget(self.no_step_label)
    
    def on_step_changed(self, step_data):
        """步骤数据变化时更新"""
        # 找到对应的步骤并更新
        for i, step in enumerate(self.current_sequence):
            if step["id"] == step_data["id"]:
                self.current_sequence[i] = step_data
                # 更新列表项
                item = self.steps_list.item(i)
                if item:
                    item.setText(step_data["name"])
                    item.setData(Qt.UserRole, step_data)
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())