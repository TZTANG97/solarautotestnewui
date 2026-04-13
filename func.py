import os
import ipaddress

def list_json_files(folder_path):
    """返回指定文件夹中所有.json文件的文件名"""
    folder_path = 'recordings/'+ folder_path
    try:
        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            return []
        
        if not os.path.isdir(folder_path):
            return []
        
        # 获取所有.json文件
        json_files = [f for f in os.listdir(folder_path) 
                     if f.endswith('.json') and os.path.isfile(os.path.join(folder_path, f))]
        
        if not json_files:
            return []
        
        return json_files
        
    except Exception as e:
        return f"读取文件夹时发生错误: {str(e)}"


# # 使用示例
# if __name__ == "__main__":
#     result = list_json_files('recordings')
#     print(result)

import json
import os

def modify_json_text_by_timestamp(file_path, new_text, target_timestamp, timestamp_tolerance=0.001, backup=True):
    """
    根据timestamp修改JSON宏文件中的text字段
    
    参数:
        file_path: str, JSON文件路径
        new_text: str, 新的文本内容
        target_timestamp: float, 目标timestamp值
        timestamp_tolerance: float, 时间戳容差范围（默认0.001秒）
        backup: bool, 是否创建备份文件
    """
    try:
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 创建备份
        if backup:
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 已创建备份: {backup_path}")
        
        # 查找匹配的text_input动作
        target_action = None
        action_index = -1
        
        for i, action in enumerate(data.get('actions', [])):
            if action.get('action_type') == 'text_input':
                action_timestamp = action.get('timestamp', 0)
                # 检查timestamp是否在容差范围内
                if abs(action_timestamp - target_timestamp) <= timestamp_tolerance:
                    target_action = action
                    action_index = i
                    break
        
        if target_action is None:
            print(f"❌ 错误: 未找到timestamp为 {target_timestamp} 的text_input动作")
            # 列出所有text_input的timestamp供参考
            text_inputs = [(i, a['timestamp']) for i, a in enumerate(data.get('actions', [])) 
                          if a.get('action_type') == 'text_input']
            if text_inputs:
                print("可用的text_input timestamp:")
                for idx, ts in text_inputs:
                    print(f"  - 动作索引{idx}: {ts}")
            return False
        
        # 修改文本
        old_text = target_action.get('text', '')
        data['actions'][action_index]['text'] = new_text
        
        # 保存修改后的JSON文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 修改成功!")
        print(f"📁 文件: {file_path}")
        print(f"⏱️  Timestamp: {target_timestamp}")
        print(f"📝 动作索引: {action_index}")
        print(f"🔤 旧文本: {old_text}")
        print(f"✨ 新文本: {new_text}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ 错误: 文件 '{file_path}' 不存在")
        return False
    except json.JSONDecodeError:
        print(f"❌ 错误: 文件 '{file_path}' 不是有效的JSON格式")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False




def is_ipv4_stdlib(ip_string):
    """
    使用Python标准库ipaddress，最严格的验证
    """
    if not isinstance(ip_string, str):
        return False
    
    try:
        # 尝试创建IPv4地址对象
        addr = ipaddress.ip_address(ip_string)
        # 确认是IPv4不是IPv6
        return isinstance(addr, ipaddress.IPv4Address)
    except ValueError:
        return False

# 使用示例
if __name__ == "__main__":
    # 修改timestamp为2.7635687351226808的text_input
    modify_json_text_by_timestamp(
        file_path="recordings/WT3000/test.json",
        new_text="111111",
        target_timestamp=45.15636858940125
    )
    
    # 如果有微小时间差，可以使用容差
    # modify_json_text_by_timestamp(
    #     file_path="your_file.json",
    #     new_text="新的路径",
    #     target_timestamp=2.76357,  # 略作四舍五入
    #     timestamp_tolerance=0.01   # 增大容差范围
    # )