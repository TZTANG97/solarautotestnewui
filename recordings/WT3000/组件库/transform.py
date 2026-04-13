#!/usr/bin/env python3
"""
鼠标宏录制器JSON格式转换工具
将旧格式（timestamp）批量转换为新格式（id + duration）
自动处理当前目录及子目录中的所有JSON文件

用法: python convert_to_new_format.py [--no-backup]
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

def detect_format(data: dict) -> str:
    """检测JSON格式类型"""
    if not data or 'actions' not in data:
        return 'invalid'
    
    if not data['actions']:
        return 'empty'
    
    first_action = data['actions'][0]
    if 'duration' in first_action:
        return 'new'
    elif 'timestamp' in first_action:
        return 'old'
    else:
        return 'unknown'

def convert_old_to_new(old_data: dict) -> dict:
    """将旧格式数据转换为新格式"""
    actions = old_data['actions']
    if not actions:
        return old_data
    
    # 构建新格式
    new_data = {
        "version": old_data.get("version", "1.0"),
        "created_at": old_data.get("created_at", datetime.now().isoformat()),
        "total_duration": old_data.get("total_duration", 0.0),
        "recorded_resolution": old_data.get("recorded_resolution", {"width": 0, "height": 0}),
        "action_count": len(actions),
        "actions": []
    }
    
    # 转换每个动作
    last_timestamp = 0.0
    for idx, action in enumerate(actions, 1):
        current_timestamp = action.get('timestamp', 0.0)
        duration = current_timestamp - last_timestamp
        last_timestamp = current_timestamp
        
        # 构建新动作
        new_action = {
            "id": idx,
            "action_type": action.get('action_type'),
            "duration": round(duration, 6)
        }
        
        # 复制其他字段（除了timestamp）
        for key, value in action.items():
            if key not in ['timestamp', 'action_type']:
                new_action[key] = value
        
        new_data['actions'].append(new_action)
    
    return new_data

def process_file(file_path: Path, backup: bool = True) -> bool:
    """处理单个文件"""
    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检测格式
        fmt = detect_format(data)
        if fmt == 'invalid':
            print(f"❌ 无效的JSON文件: {file_path}")
            return False
        elif fmt == 'empty':
            print(f"⚠️  文件为空，跳过: {file_path}")
            return True
        elif fmt == 'new':
            print(f"✅ 已经是新格式，跳过: {file_path}")
            return True
        elif fmt == 'unknown':
            print(f"❌ 无法识别的格式: {file_path}")
            return False
        
        # 转换格式
        print(f"🔄 正在转换: {file_path}")
        new_data = convert_old_to_new(data)
        
        # 备份原文件
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            file_path.rename(backup_path)
            print(f"   💾 已备份: {backup_path.name}")
        
        # 写入新文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ 转换成功: {file_path.name}")
        return True
        
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False

def main():
    """主函数 - 自动扫描当前目录及子目录"""
    if '--help' in sys.argv:
        print("=" * 60)
        print("鼠标宏录制器 - JSON格式转换工具")
        print("=" * 60)
        print("功能: 自动将当前目录及子目录中所有旧格式JSON")
        print("      转换为新格式(id+duration)")
        print("用法: python convert_to_new_format.py [选项]")
        print("选项:")
        print("  --no-backup  不创建备份文件（直接覆盖）")
        print("  --help       显示帮助信息")
        print("=" * 60)
        sys.exit(0)
    
    # 解析参数
    backup = '--no-backup' not in sys.argv
    
    # 扫描当前目录及子目录下的所有JSON文件
    current_dir = Path('.')
    json_files = list(current_dir.rglob('*.json'))
    
    # 排除备份文件
    json_files = [f for f in json_files if not f.suffix.endswith('.bak')]
    
    if not json_files:
        print("=" * 60)
        print("🔍 未找到需要转换的JSON文件")
        print("=" * 60)
        sys.exit(0)
    
    print("=" * 60)
    print(f"📂 扫描目录: {current_dir.absolute()}")
    print(f"🔍 发现 {len(json_files)} 个JSON文件")
    print("=" * 60)
    print("🚀 开始自动转换...")
    print("-" * 60)
    
    # 批量转换
    success_count = 0
    skip_count = 0
    for json_file in json_files:
        result = process_file(json_file, backup)
        if result:
            # 检查是否真的转换了
            fmt = detect_format(json.loads(json_file.read_text(encoding='utf-8')))  # 修改这里
            if fmt == 'new':
                success_count += 1
            else:
                skip_count += 1
    
    print("-" * 60)
    print("=" * 60)
    print(f"🎉 转换完成！")
    print(f"   成功转换: {success_count} 个文件")
    print(f"   跳过文件: {skip_count} 个文件")
    if backup:
        print(f"💡 所有旧文件已备份为 .bak 文件")
        print(f"   如需恢复，请手动将 .bak 文件重命名为 .json")
    print("=" * 60)

if __name__ == '__main__':
    main()