# -*- coding: utf-8 -*-
"""从 DEWETRON 设备读取 XML，查找谐波相关元素位置"""
import socket
import re
import time

def send_command(sock, cmd, timeout=5):
    """发送 SCPI 命令并读取响应"""
    sock.sendall((cmd + '\n').encode('ascii'))
    time.sleep(0.3)
    sock.settimeout(timeout)
    response = b''
    while True:
        try:
            chunk = sock.recv(65536)
            if not chunk:
                break
            response += chunk
            # 检查是否收到完整响应
            if response.endswith(b'\r\n') or response.endswith(b'\n'):
                break
        except socket.timeout:
            break
    return response.decode('ascii', errors='replace').strip()

def main():
    # 连接设备
    IP = "192.168.1.100"  # 根据实际设备修改
    PORT = 10001

    print(f"连接 DEWETRON: {IP}:{PORT}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((IP, PORT))
    print("连接成功")

    # 读取 XML
    print("读取 XML 配置...")
    response = send_command(sock, ":SETUP:READ?", timeout=30)

    # 找到 XML 起始位置
    xml_start = response.find('<?xml')
    if xml_start < 0:
        xml_start = response.find('<MeasurementConfig')
    if xml_start < 0:
        print(f"未找到 XML 起始，响应前200字符: {response[:200]}")
        sock.close()
        return

    xml = response[xml_start:]
    print(f"XML 长度: {len(xml)} 字节")

    # 保存完整 XML 到文件
    with open('dewetron_harmonic_full.xml', 'w', encoding='utf-8') as f:
        f.write(xml)
    print("已保存完整 XML 到 dewetron_harmonic_full.xml")

    # 查找谐波相关元素
    print("\n" + "=" * 80)
    print("查找谐波相关元素")
    print("=" * 80)

    # 1. Features/Harmonic
    patterns = [
        ("POWER/Features/Harmonic", r'<Property name="POWER/Features/Harmonic">\s*<BooleanValue>(True|False)</BooleanValue>'),
        ("POWER/Harmonic/MaxOrder", r'<Property name="POWER/Harmonic/MaxOrder">\s*<ScalarValue>\s*<Value>([^<]+)</Value>'),
        ("POWER/Harmonic/THDOrder", r'<Property name="POWER/Harmonic/THDOrder">\s*<ScalarValue>\s*<Value>([^<]+)</Value>'),
        ("POWER/Harmonic/GroupingType", r'<Property name="POWER/Harmonic/GroupingType">\s*<EnumValue enum="GroupingType">([^<]+)</EnumValue>'),
        ("POWER/MaxUpdateRate", r'<Property name="POWER/MaxUpdateRate">\s*<StringValue>"?([^"<]+)"?</StringValue>'),
    ]

    for name, pattern in patterns:
        matches = list(re.finditer(pattern, xml))
        if matches:
            for m in matches:
                # 找到位置对应的行号
                pos = m.start()
                line_num = xml[:pos].count('\n') + 1
                print(f"\n[找到] {name}")
                print(f"  值: {m.group(1)}")
                print(f"  位置: 字符 {m.start()} - {m.end()}")
                print(f"  行号: ~{line_num}")
                # 显示上下文
                ctx_start = max(0, m.start() - 50)
                ctx_end = min(len(xml), m.end() + 50)
                context = xml[ctx_start:ctx_end].replace('\n', '\\n')
                print(f"  上下文: ...{context}...")
        else:
            print(f"\n[未找到] {name}")

    # 查找所有包含 Harmonic 的属性
    print("\n" + "=" * 80)
    print("所有包含 'Harmonic' 的 XML 属性")
    print("=" * 80)
    for m in re.finditer(r'<Property name="([^"]*[Hh]armonic[^"]*)"', xml):
        pos = m.start()
        line_num = xml[:pos].count('\n') + 1
        print(f"  行~{line_num}: {m.group(1)}")

    # 查找所有包含 Grouping 的属性
    print("\n" + "=" * 80)
    print("所有包含 'Grouping' 的 XML 属性")
    print("=" * 80)
    for m in re.finditer(r'<Property name="([^"]*[Gg]rouping[^"]*)"', xml):
        pos = m.start()
        line_num = xml[:pos].count('\n') + 1
        print(f"  行~{line_num}: {m.group(1)}")

    # 查找所有包含 THD 的属性
    print("\n" + "=" * 80)
    print("所有包含 'THD' 的 XML 属性")
    print("=" * 80)
    for m in re.finditer(r'<Property name="([^"]*THD[^"]*)"', xml):
        pos = m.start()
        line_num = xml[:pos].count('\n') + 1
        print(f"  行~{line_num}: {m.group(1)}")

    sock.close()
    print("\n完成")

if __name__ == "__main__":
    main()
