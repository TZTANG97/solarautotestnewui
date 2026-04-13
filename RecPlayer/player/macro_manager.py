import sys
import time
from pathlib import Path
from .src.models import MacroConfig
from .src.player import MacroPlayer
import configparser

config = configparser.ConfigParser()

# 读取INI文件（文件路径可以是相对路径或绝对路径）
config.read('config_files/config.ini', encoding='utf-8')
PATH_RECORDINGS_WT3000 = config.get('PATH', 'recordings_wt3000') 

class MacroManager:
    """宏播放器管理类，封装宏加载、执行和控制逻辑"""
    
    def __init__(self, config_file: str = None, path = PATH_RECORDINGS_WT3000, repeat: int = 1, smooth_move: bool = True):
        """
        初始化宏管理器
        
        :param config_file: 配置文件路径（可选，可在play_file中指定）
        :param path: 录制文件路径,默认WT3000
        :param repeat: 默认重复执行次数
        :param smooth_move: 默认是否启用平滑移动
        """
        self.config_file = config_file
        self.repeat = repeat
        self.smooth_move = smooth_move
        self.player = None
        self.config = None
        self.RECORDING_PATH = path

    def change_wt_type(self, type: str):
        try:
            self.RECORDING_PATH = config.get('PATH', f'recordings_{type.lower()}')
        except Exception as e:
            print(f"Error changing WT type: {e}")
        else:
            print(f"已切换到WT{type}")
    

    @classmethod
    def play_file(cls, filename: str, repeat: int = 1, smooth_move: bool = True) -> bool:
        """
        快速载入并播放宏文件（类方法，无需创建实例）
        
        示例:
            MacroManager.play_file("test.json")
            MacroManager.play_file("test.json", repeat=3, smooth_move=False)
        """
        # 创建临时实例并执行
        instance = cls(filename, repeat, smooth_move)
        return instance.execute()
    
    def load_config(self, filename: str = None) -> bool:
        """
        加载宏配置文件
        
        :param filename: 配置文件路径，如果为None则使用self.config_file
        """
        config_path = filename or self.config_file
        
        if not config_path:
            print("错误: 未指定配置文件路径")
            return False
            
        print(f"加载配置文件: {config_path}")
        
        if not Path(config_path).exists():
            print(f"错误: 配置文件 {config_path} 不存在")
            return False
            
        try:
            self.config = MacroConfig.load_from_file(config_path)
            # 更新配置路径
            self.config_file = config_path
            print(f"成功加载 {len(self.config.actions)} 个动作")
            print(f"总时长: {self.config.total_duration:.2f} 秒")
            return True
        except Exception as e:
            print(f"加载配置失败: {e}")
            return False
    
    def initialize_player(self):
        """初始化播放器实例"""
        if not self.config:
            print("错误: 未加载配置，请先调用load_config()")
            return False
        
        self.player = MacroPlayer()
        self.player.load_config(self.config)
        
        # 设置完成回调
        def on_playback_stopped():
            print("\n复刻完成！")
        self.player.on_playback_stopped = on_playback_stopped
        return True
    
    def execute(self, filename: str = None) -> bool:

        """
        执行宏播放
        
        :param filename: 可选的配置文件路径，如果指定则重新加载配置
        :return: 执行成功返回True，否则返回False
        """
        # 如果指定了新文件或尚未加载配置，则加载配置
        
        if filename or not self.config:
            if not self.load_config(self.RECORDING_PATH + filename):
                return False
        
        # 初始化播放器（如果尚未初始化或配置已更改）
        if not self.player or filename:
            if not self.initialize_player():
                return False
        
        # 开始执行
        print("\n执行中...")
        success = self.player.start_playback(
            repeat_count=self.repeat, 
            enable_smooth_movement=self.smooth_move
        )
        
        if not success:
            print("启动失败！")
            return False
        
        # 等待完成或中断
        return self._wait_for_completion()
    
    def _wait_for_completion(self) -> bool:
        """等待播放完成或用户中断"""
        try:
            while self.player.is_playback_active():
                time.sleep(0.1)
            return True
        except KeyboardInterrupt:
            print("\n用户中断，停止复刻...")
            self.stop()
            return False
    
    def stop(self):
        """停止当前播放"""
        if self.player and self.player.is_playback_active():
            self.player.stop_playback()
    
    def is_active(self) -> bool:
        """检查是否正在播放"""
        return self.player is not None and self.player.is_playback_active()


# 使用示例
if __name__ == "__main__":
    # 示例1: 快速播放（类方法，推荐）
    # print("=== 方式1: 类方法快速播放 ===")
    # MacroManager.play_file("RecPlayer/player/test.json", repeat=1, smooth_move=True)
    
    # 示例2: 复用实例，连续播放不同文件
    print("\n=== 方式2: 复用实例 ===")
    manager = MacroManager(repeat=1, smooth_move=True)
    
    # 播放文件1
    manager.execute("打开WT.json")
    
    # 播放文件2（复用同一个manager实例）
    manager.execute("打开WT并开始连接.json")
    
    # # 示例3: 先加载，后多次执行
    # print("\n=== 方式3: 先加载后多次执行 ===")
    # manager2 = MacroManager()
    
    # # 加载配置（不执行）
    # if manager2.load_config("RecPlayer/player/test.json"):
    #     # 可以查看配置信息等
    #     print(f"已加载 {len(manager2.config.actions)} 个动作")
        
    #     # 执行第一次
    #     manager2.execute()
        
    #     # 修改参数后再次执行（无需重新加载配置）
    #     manager2.repeat = 3
    #     manager2.execute()