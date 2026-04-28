"""
数据模型模块
定义录制动作、配置文件等核心数据结构
"""
import json
import time
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime


class ActionType(Enum):
    """动作类型枚举"""
    MOUSE_CLICK = "mouse_click"
    MOUSE_RELEASE = "mouse_release"
    MOUSE_MOVE = "mouse_move"
    MOUSE_SCROLL = "mouse_scroll"
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    TEXT_INPUT = "text_input"  # 文本输入动作


@dataclass
class RecordedAction:
    """录制的动作数据类"""
    action_type: ActionType
    timestamp: float  # 相对时间戳（秒）
    x: Optional[int] = None  # 鼠标X坐标
    y: Optional[int] = None  # 鼠标Y坐标
    button: Optional[str] = None  # 鼠标按键 'left', 'right', 'middle'
    dx: Optional[int] = None  # 滚轮水平滚动量
    dy: Optional[int] = None  # 滚轮垂直滚动量
    key: Optional[str] = None  # 键盘按键
    is_drag: bool = False  # 是否为拖拽动作
    text: Optional[str] = None  # 文本内容（用于TEXT_INPUT动作）

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['action_type'] = self.action_type.value
        return {k: v for k, v in data.items() if v is not None or k in ['is_drag']}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecordedAction':
        """从字典创建对象"""
        data = data.copy()
        # 兼容字段：
        # - 外部/旧宏可能包含 id、duration 等 RecordedAction 未声明字段
        # - 这些字段不参与回放逻辑，加载时直接忽略，避免 __init__ unexpected keyword
        allowed_keys = {
            "action_type",
            "timestamp",
            "x",
            "y",
            "button",
            "dx",
            "dy",
            "key",
            "is_drag",
            "text",
        }
        filtered = {k: v for k, v in data.items() if k in allowed_keys}

        filtered['action_type'] = ActionType(filtered['action_type'])
        if 'is_drag' not in filtered:
            filtered['is_drag'] = False
        return cls(**filtered)


class MacroConfig:
    """宏配置文件管理类"""
    
    def __init__(self):
        self.version = "1.0"
        self.created_at = datetime.now().isoformat()
        self.actions: List[RecordedAction] = []
        self.total_duration = 0.0
        self.recorded_resolution = {"width": 0, "height": 0}
        self.enable_smooth_movement = True

    def add_action(self, action: RecordedAction):
        """添加一个动作"""
        self.actions.append(action)
        if action.timestamp > self.total_duration:
            self.total_duration = action.timestamp
    
    def get_actions(self) -> List[RecordedAction]:
        """获取所有动作"""
        return sorted(self.actions, key=lambda a: a.timestamp)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "version": self.version,
            "created_at": self.created_at,
            "total_duration": self.total_duration,
            "recorded_resolution": self.recorded_resolution,
            "actions": [action.to_dict() for action in self.get_actions()],
            "action_count": len(self.actions)
        }
    
    def save_to_file(self, filepath: str):
        """保存到JSON文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"保存配置文件失败: {str(e)}")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'MacroConfig':
        """从JSON文件加载"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = cls()
            config.version = data.get("version", "1.0")
            config.created_at = data.get("created_at", datetime.now().isoformat())
            config.total_duration = data.get("total_duration", 0.0)
            config.recorded_resolution = data.get("recorded_resolution", {"width": 0, "height": 0})
            
            # 加载动作列表
            # 兼容两种格式：
            # - 旧格式：action 内带 timestamp (秒)
            # - 新格式：action 内带 duration (秒)，不带 timestamp
            last_timestamp = 0.0
            for action_data in data.get("actions", []):
                print("新模式")
                if "timestamp" not in action_data and "duration" in action_data:
                    # duration -> timestamp（累加）
                    last_timestamp = float(last_timestamp) + float(action_data.get("duration", 0.0))
                    action_data = dict(action_data)
                    action_data["timestamp"] = last_timestamp
                else:
                    print("旧模式")
                    # 即使是旧格式，也维护 last_timestamp，便于混合格式文件
                    last_timestamp = float(action_data.get("timestamp", last_timestamp))

                action = RecordedAction.from_dict(action_data)
                config.actions.append(action)
            
            return config
        except Exception as e:
            raise Exception(f"加载配置文件失败: {str(e)}")
    
    def clear(self):
        """清空所有动作"""
        self.actions.clear()
        self.total_duration = 0.0
        self.created_at = datetime.now().isoformat()
    
    def get_summary(self) -> Dict[str, Any]:
        """获取录制摘要"""
        action_counts = {}
        for action in self.actions:
            action_type = action.action_type.value
            if action_type not in action_counts:
                action_counts[action_type] = 0
            action_counts[action_type] += 1
        
        return {
            "total_actions": len(self.actions),
            "total_duration": round(self.total_duration, 2),
            "duration_minutes": round(self.total_duration / 60, 2),
            "action_breakdown": action_counts,
            "created_at": self.created_at
        }