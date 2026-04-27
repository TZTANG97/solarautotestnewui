"""试验设定抽象基类。

这个文件定义各类试验设定模块的共同接口，不承载具体业务逻辑。

未来计划：
- 统一读取试验参数
- 统一做参数校验与转换
- 统一生成命令序列
- 统一保存/加载命令文件
- 作为各具体试验设定模块的公共入口

注意：
- 当前阶段只定义抽象契约
- 不改变现有主程序的初始化顺序和业务行为
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseSetup(ABC):
    """试验设定的抽象入口。"""

    @abstractmethod
    def initialize(self, app_ctx: Any) -> Dict[str, Any]:
        """初始化试验设定窗口，并同步到应用上下文。"""

    @staticmethod
    @abstractmethod
    def initialize_windows(app_ctx: Any) -> Dict[str, Any]:
        """兼容旧流程的窗口初始化入口。"""

    @abstractmethod
    def build_setup(self, setup_input: Any) -> Dict[str, Any]:
        """根据输入参数构建试验设定数据。"""

    @abstractmethod
    def build_commands(self, setup_data: Dict[str, Any]) -> Any:
        """根据设定数据生成命令序列。"""

    @abstractmethod
    def save_commands(self, commands: Any, save_path: str) -> str:
        """保存命令文件并返回保存结果或路径。"""

    @abstractmethod
    def load_commands(self, load_path: str) -> Any:
        """从命令文件读取试验设定或命令内容。"""
