import time
import threading
import win32api
import win32con
import win32gui
from typing import Optional, Callable, Tuple, List
import ctypes
from ctypes import windll, wintypes, Structure, c_long, byref
import pyperclip  # 确保已安装: pip install pyperclip

from .models import RecordedAction, ActionType, MacroConfig


class MouseSimulator:
    """鼠标模拟器"""
    
    @staticmethod
    def move_to(x: int, y: int, duration: float = 0.0):
        """移动鼠标到指定位置"""
        if duration > 0:
            start_x, start_y = MouseSimulator.get_cursor_pos()
            steps = int(duration * 100)
            
            for i in range(steps):
                t = i / steps
                t = t * t * (3.0 - 2.0 * t)  # ease-in-out
                curr_x = int(start_x + (x - start_x) * t)
                curr_y = int(start_y + (y - start_y) * t)
                windll.user32.SetCursorPos(curr_x, curr_y)
                time.sleep(duration / steps)
        else:
            windll.user32.SetCursorPos(x, y)
    
    @staticmethod
    def get_cursor_pos() -> Tuple[int, int]:
        """获取当前鼠标位置"""
        class Point(Structure):
            _fields_ = [("x", c_long), ("y", c_long)]
        
        pt = Point()
        windll.user32.GetCursorPos(byref(pt))
        return pt.x, pt.y
    
    @staticmethod
    def click(x: int, y: int, button: str = "left"):
        """在指定位置点击鼠标"""
        MouseSimulator.move_to(x, y)
        time.sleep(0.01)
        
        if button == "left":
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.01)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        elif button == "right":
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.01)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        elif button == "middle":
            win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)
            time.sleep(0.01)
            win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)
    
    @staticmethod
    def scroll(x: int, y: int, dx: int = 0, dy: int = 0):
        """滚动鼠标滚轮"""
        MouseSimulator.move_to(x, y)
        time.sleep(0.01)
        
        if dy != 0:
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, dy * 120, 0)
        
        if dx != 0:
            win32api.mouse_event(win32con.MOUSEEVENTF_HWHEEL, 0, 0, dx * 120, 0)
    
    @staticmethod
    def button_down(button: str = "left"):
        """按下鼠标按钮"""
        if button == "left":
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        elif button == "right":
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        elif button == "middle":
            win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)
    
    @staticmethod
    def button_up(button: str = "left"):
        """释放鼠标按钮"""
        if button == "left":
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        elif button == "right":
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        elif button == "middle":
            win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)
    
    @staticmethod
    def drag_to(x: int, y: int, duration: float = 0.2):
        """拖拽到指定位置"""
        if duration > 0:
            start_x, start_y = MouseSimulator.get_cursor_pos()
            steps = int(duration * 100)
            
            for i in range(steps):
                t = i / steps
                curr_x = int(start_x + (x - start_x) * t)
                curr_y = int(start_y + (y - start_y) * t)
                windll.user32.SetCursorPos(curr_x, curr_y)
                time.sleep(duration / steps)
        else:
            windll.user32.SetCursorPos(x, y)
    
    @staticmethod
    def _ease_in_out(t: float) -> float:
        """缓动函数"""
        return t * t * (3.0 - 2.0 * t)


class KeyboardSimulator:
    """键盘模拟器"""
    
    VK_CODE_MAP = {
        'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46,
        'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C,
        'm': 0x4D, 'n': 0x4E, 'o': 0x4F, 'p': 0x50, 'q': 0x51, 'r': 0x52,
        's': 0x53, 't': 0x54, 'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58,
        'y': 0x59, 'z': 0x5A,
        '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
        '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
        'enter': 0x0D, 'esc': 0x1B, 'space': 0x20, 'tab': 0x09, 'backspace': 0x08,
        'caps_lock': 0x14, 'num_lock': 0x90, 'scroll_lock': 0x91,
        'ctrl': 0x11, 'shift': 0x10, 'alt': 0x12, 'win': 0x5B,
        'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,
        'delete': 0x2E, 'insert': 0x2D, 'home': 0x24, 'end': 0x23,
        'pageup': 0x21, 'pagedown': 0x22,
        'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74,
        'f6': 0x75, 'f7': 0x76, 'f8': 0x77, 'f9': 0x78, 'f10': 0x79,
        'f11': 0x7A, 'f12': 0x7B,
    }
    
    LOCK_KEYS = [0x14, 0x90, 0x91]
    
    @staticmethod
    def key_down(vk_code: int):
        """按下按键"""
        if vk_code in KeyboardSimulator.LOCK_KEYS:
            win32api.keybd_event(vk_code, 0, 0, 0)
            time.sleep(0.02)
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.03)
        else:
            win32api.keybd_event(vk_code, 0, 0, 0)
    
    @staticmethod
    def key_up(vk_code: int):
        """释放按键"""
        if vk_code not in KeyboardSimulator.LOCK_KEYS:
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    @staticmethod
    def paste_text_via_clipboard(text: str):
        """通过剪贴板粘贴文本"""
        try:
            print("📋 正在使用剪贴板粘贴...")
            
            # 保存原始剪贴板内容
            old_clipboard = pyperclip.paste()
            time.sleep(0.05)
            
            # 复制新文本到剪贴板
            pyperclip.copy(text)
            time.sleep(0.1)
            
            # 发送 Ctrl+V
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            time.sleep(0.02)
            win32api.keybd_event(0x56, 0, 0, 0)  # V
            time.sleep(0.02)
            win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
            
            # 恢复原始剪贴板内容
            pyperclip.copy(old_clipboard)
            print("✅ 剪贴板粘贴成功")
        except Exception as e:
            print(f"❌ 剪贴板粘贴失败: {e}")


class ActionPlayer:
    """动作播放器"""
    
    def __init__(self, enable_smooth_movement: bool = False):
        self.mouse_sim = MouseSimulator()
        self.keyboard_sim = KeyboardSimulator()
        self._last_drag_pos = None
        self.enable_smooth_movement = enable_smooth_movement
        self._last_mouse_pos = None
    
    def execute_action(self, action: RecordedAction):
        """执行单个动作"""
        try:
            if (self.enable_smooth_movement and 
                self._last_mouse_pos is not None and 
                action.x is not None and action.y is not None):
                current_x, current_y = self._last_mouse_pos
                target_x, target_y = action.x, action.y
                distance = ((target_x - current_x)**2 + (target_y - current_y)**2)**0.5
                if distance > 10:
                    duration = min(0.5, max(0.2, distance / 1500))
                    self.mouse_sim.move_to(target_x, target_y, duration=duration)
                else:
                    self.mouse_sim.move_to(target_x, target_y, duration=0)
            
            if action.action_type == ActionType.MOUSE_CLICK:
                self._execute_mouse_click(action)
            elif action.action_type == ActionType.MOUSE_MOVE:
                self._execute_mouse_move(action)
            elif action.action_type == ActionType.MOUSE_RELEASE:
                self._execute_mouse_release(action)
            elif action.action_type == ActionType.MOUSE_SCROLL:
                self._execute_mouse_scroll(action)
            elif action.action_type == ActionType.KEY_PRESS:
                self._execute_key_press(action)
            elif action.action_type == ActionType.KEY_RELEASE:
                self._execute_key_release(action)
            elif action.action_type == ActionType.TEXT_INPUT:
                self._execute_text_input(action)
            
            if action.x is not None and action.y is not None:
                self._last_mouse_pos = (action.x, action.y)
        
        except Exception as e:
            print(f"执行动作失败: {action.action_type}, 错误: {e}")
    
    def _execute_mouse_click(self, action: RecordedAction):
        if action.x is not None and action.y is not None and action.button:
            if action.is_drag:
                self.mouse_sim.move_to(action.x, action.y)
                self.mouse_sim.button_down(action.button)
                self._last_drag_pos = (action.x, action.y)
            else:
                self.mouse_sim.click(action.x, action.y, action.button)
    
    def _execute_mouse_release(self, action: RecordedAction):
        if action.x is not None and action.y is not None and action.button:
            if action.is_drag and self._last_drag_pos:
                start_x, start_y = self._last_drag_pos
                self.mouse_sim.drag_to(action.x, action.y, duration=0.2)
                self.mouse_sim.button_up(action.button)
                self._last_drag_pos = None
            else:
                self.mouse_sim.move_to(action.x, action.y)
    
    def _execute_mouse_move(self, action: RecordedAction):
        if action.x is not None and action.y is not None:
            self.mouse_sim.move_to(action.x, action.y)
    
    def _execute_mouse_scroll(self, action: RecordedAction):
        if action.x is not None and action.y is not None:
            self.mouse_sim.scroll(action.x, action.y, action.dx or 0, action.dy or 0)
    
    def _execute_key_press(self, action: RecordedAction):
        if not action.key:
            return
        
        if '+' in action.key:
            self._execute_combination_key_press(action.key)
        else:
            vk_code = None
            try:
                vk_code = int(action.key)
            except ValueError:
                vk_code = KeyboardSimulator.VK_CODE_MAP.get(action.key.lower())
            
            if vk_code is not None:
                self.keyboard_sim.key_down(vk_code)
            else:
                print(f"无法识别的按键: {action.key}")
    
    def _execute_key_release(self, action: RecordedAction):
        if not action.key:
            return
        
        if '+' in action.key:
            self._execute_combination_key_release(action.key)
        else:
            vk_code = None
            try:
                vk_code = int(action.key)
            except ValueError:
                vk_code = KeyboardSimulator.VK_CODE_MAP.get(action.key.lower())
            
            if vk_code is not None:
                self.keyboard_sim.key_up(vk_code)
            else:
                print(f"无法识别的按键: {action.key}")
    
    def _execute_combination_key_press(self, key_combination: str):
        parts = key_combination.lower().split('+')
        modifiers = []
        main_key = None
        
        for part in parts:
            part = part.strip()
            if part in ['ctrl', 'shift', 'alt', 'win']:
                modifiers.append(part)
            else:
                main_key = part
        
        for modifier in modifiers:
            vk_code = KeyboardSimulator.VK_CODE_MAP.get(modifier)
            if vk_code is not None:
                self.keyboard_sim.key_down(vk_code)
                time.sleep(0.005)
        
        if main_key:
            vk_code = None
            try:
                vk_code = int(main_key)
            except ValueError:
                vk_code = KeyboardSimulator.VK_CODE_MAP.get(main_key.lower())
            
            if vk_code is not None:
                time.sleep(0.005)
                self.keyboard_sim.key_down(vk_code)
            else:
                print(f"无法识别的组合键主键: {main_key}")
    
    def _execute_combination_key_release(self, key_combination: str):
        parts = key_combination.lower().split('+')
        modifiers = []
        main_key = None
        
        for part in parts:
            part = part.strip()
            if part in ['ctrl', 'shift', 'alt', 'win']:
                modifiers.append(part)
            else:
                main_key = part
        
        if main_key:
            vk_code = None
            try:
                vk_code = int(main_key)
            except ValueError:
                vk_code = KeyboardSimulator.VK_CODE_MAP.get(main_key.lower())
            
            if vk_code is not None:
                self.keyboard_sim.key_up(vk_code)
                time.sleep(0.005)
            else:
                print(f"无法识别的组合键主键: {main_key}")
        
        for modifier in reversed(modifiers):
            vk_code = KeyboardSimulator.VK_CODE_MAP.get(modifier)
            if vk_code is not None:
                time.sleep(0.005)
                self.keyboard_sim.key_up(vk_code)
    
    def _execute_text_input(self, action: RecordedAction):
        """执行文本输入（使用剪贴板粘贴）"""
        if not action.text:
            return
        
        # 先移动到指定位置
        if action.x is not None and action.y is not None:
            self.mouse_sim.move_to(action.x, action.y)
            time.sleep(0.05)
        
        print(f"📋 正在粘贴文本: {action.text}")
        # 直接调用剪贴板粘贴方法
        self.keyboard_sim.paste_text_via_clipboard(action.text)
        time.sleep(len(action.text) * 0.02 + 0.15)


class MacroPlayer:
    """宏播放器"""
    
    def __init__(self):
        self.action_player = None
        self.is_playing = False
        self.is_paused = False
        self.play_thread = None
        self.current_action_index = 0
        self.config: Optional[MacroConfig] = None
        
        self.on_playback_started: Optional[Callable] = None
        self.on_playback_stopped: Optional[Callable] = None
        self.on_playback_paused: Optional[Callable] = None
        self.on_action_executed: Optional[Callable] = None
        self.on_progress_update: Optional[Callable] = None
    
    def load_config(self, config: MacroConfig):
        self.config = config
    
    def start_playback(self, repeat_count: int = 1, enable_smooth_movement: bool = False):
        if not self.config or not self.config.actions:
            print("没有可复刻的动作")
            return False
        
        if self.is_playing:
            return False
        
        self.is_playing = True
        self.is_paused = False
        self.current_action_index = 0
        
        self.action_player = ActionPlayer(enable_smooth_movement)
        
        if self.on_playback_started:
            self.on_playback_started(len(self.config.actions), repeat_count)
        
        self.play_thread = threading.Thread(
            target=self._playback_loop,
            args=(repeat_count,),
            daemon=True
        )
        self.play_thread.start()
        
        return True
    
    def stop_playback(self):
        self.is_playing = False
        self.is_paused = False
        if self.play_thread:
            self.play_thread.join(timeout=1)
        
        if self.on_playback_stopped:
            self.on_playback_stopped()
    
    def pause_playback(self):
        if self.is_playing and not self.is_paused:
            self.is_paused = True
            if self.on_playback_paused:
                self.on_playback_paused(True)
    
    def resume_playback(self):
        if self.is_playing and self.is_paused:
            self.is_paused = False
            if self.on_playback_paused:
                self.on_playback_paused(False)
    
    def _playback_loop(self, repeat_count: int):
        try:
            for repeat in range(repeat_count):
                if not self.is_playing:
                    break
                
                actions = self.config.get_actions()
                last_timestamp = 0
                
                for i, action in enumerate(actions):
                    if not self.is_playing:
                        break
                    
                    while self.is_paused and self.is_playing:
                        time.sleep(0.1)
                    
                    if not self.is_playing:
                        break
                    
                    wait_time = action.timestamp - last_timestamp
                    if wait_time > 0:
                        time.sleep(wait_time)
                    
                    last_timestamp = action.timestamp
                    
                    while self.is_paused and self.is_playing:
                        time.sleep(0.1)
                    
                    if not self.is_playing:
                        break
                    
                    if self.action_player is None:
                        print("错误: ActionPlayer 未初始化")
                        break
                    
                    self.action_player.execute_action(action)
                    self.current_action_index = i
                    
                    if self.on_progress_update:
                        progress = ((repeat * len(actions) + i + 1) / 
                                  (repeat_count * len(actions))) * 100
                        self.on_progress_update(progress, i + 1, len(actions))
                    
                    if self.on_action_executed:
                        self.on_action_executed(action, i)
        
        except Exception as e:
            print(f"复刻执行错误: {e}")
        finally:
            self.is_playing = False
            if self.on_playback_stopped:
                self.on_playback_stopped()
    
    def is_playback_active(self) -> bool:
        return self.is_playing
    
    def is_playback_paused(self) -> bool:
        return self.is_paused