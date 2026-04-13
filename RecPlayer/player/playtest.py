#!/usr/bin/env python3
"""
复刻器使用示例
直接加载配置文件并执行宏
"""

import sys
import time
from pathlib import Path

from src.player import MacroPlayer
from src.models import MacroConfig


def play_macro(config_file: str, repeat: int = 1, smooth_move: bool = True):
    """
    加载并执行宏
    
    :param config_file: 配置文件路径
    :param repeat: 重复执行次数
    :param smooth_move: 是否启用平滑移动
    """
    print(f"加载配置文件: {config_file}")
    
    # 加载配置
    config = MacroConfig.load_from_file(config_file)
    print(f"成功加载 {len(config.actions)} 个动作")
    print(f"总时长: {config.total_duration:.2f} 秒")
    
    # 创建播放器
    player = MacroPlayer()
    player.load_config(config)
    
    # 连接回调（可选）
    def on_playback_started(total_actions: int, repeat_count: int):
        print(f"\n开始复刻: {total_actions} 个动作, 重复 {repeat_count} 次")
        if smooth_move:
            print("平滑移动: 已启用")
    
    def on_action_executed(action, index: int):
        action_type = action.action_type.value
        if action.x is not None and action.y is not None:
            print(f"  [{index+1}] {action_type} ({action.x}, {action.y})")
        else:
            print(f"  [{index+1}] {action_type} {action.key}")
    
    def on_playback_stopped():
        print("\n复刻完成！")
    
    player.on_playback_started = on_playback_started
    player.on_action_executed = on_action_executed
    player.on_playback_stopped = on_playback_stopped
    
    # 开始复刻
    print("\n执行中...")
    success = player.start_playback(repeat_count=repeat, enable_smooth_movement=smooth_move)
    
    if not success:
        print("启动失败！")
        return False
    
    # 等待复刻完成
    try:
        while player.is_playback_active():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n用户中断，停止复刻...")
        player.stop_playback()
    
    return True


if __name__ == "__main__":
    # 示例1: 播放默认配置文123asd件
    config_path = "RecPlayer/player/test.json"
    
    
    if not Path(config_path).exists():
        print(f"错误: 配置文件 {config_path} 不存在")
        print("请确保 config.json 在当前目录下")
        sys.exit(1)
    
    # 执行
    play_macro(
        config_file=config_path,
        repeat=1,  # 重复次数
        smooth_move=True  # 启用平滑移动
    )
