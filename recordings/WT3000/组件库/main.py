import os
import json
from datetime import datetime

def merge_json_files(output_filename="fixedPF-3P4W.json"):
    """
    按顺序合并JSON宏文件
    """
    # 需要合并的文件列表（按顺序）
    json_files = [
        "点击设定.json",
        "选择相.json",
        "设置更新率为100.json",
        "点击测量.json",
        "点击测量-进行设置.json",
        "点击测量-进行设置-项目配置12.json",
        "点击测量-进行设置-自动保存-修改停止时间.json",
        "第一次修改文件保存路径.json",
        "第一次更改文件名.json",
        "数值详细设置-项目设置初始化.json",
        "数值详细设置-项目设置-3P4W-模板A.json"
    ]
    
    merged_actions = []
    total_duration = 0.0
    last_timestamp = 0.0
    resolution = None
    
    print("开始合并JSON文件...")
    
    for i, filename in enumerate(json_files, 1):
        if not os.path.exists(filename):
            print(f"❌ 警告: 文件 '{filename}' 不存在，跳过该文件")
            continue
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 记录分辨率（使用第一个文件的）
            if resolution is None and 'recorded_resolution' in data:
                resolution = data['recorded_resolution']
            
            # 调整动作的时间戳
            for action in data.get('actions', []):
                adjusted_action = action.copy()
                adjusted_action['timestamp'] = total_duration + action['timestamp']
                merged_actions.append(adjusted_action)
            
            # 累加总时长
            file_duration = data.get('total_duration', 0)
            total_duration += file_duration
            
            print(f"✅ [{i}/10] 已合并: {filename} (时长: {file_duration:.3f}s, 动作数: {data.get('action_count', 0)})")
            
        except Exception as e:
            print(f"❌ 错误: 无法处理文件 '{filename}': {e}")
    
    # 创建合并后的JSON结构
    merged_data = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "total_duration": total_duration,
        "recorded_resolution": resolution or {"width": 1920, "height": 1080},
        "actions": merged_actions,
        "action_count": len(merged_actions),
        "merged_files": json_files
    }
    
    # 保存为新的JSON文件
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✨ 合并完成！")
    print(f"📁 输出文件: {output_filename}")
    print(f"⏱️  总时长: {total_duration:.3f} 秒")
    print(f"👆 总动作数: {len(merged_actions)}")
    
    return merged_data

# 执行合并
if __name__ == "__main__":
    merge_json_files()