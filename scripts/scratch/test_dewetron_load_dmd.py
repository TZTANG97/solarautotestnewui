#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""加载 DMD 文件后读取 XML，查看存储路径相关属性"""
import time
import socket
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

DEWETRON_IP = "192.168.40.25"
DEWETRON_PORT = 10001
DMD_FILE = "D:/m_20260706_155013.dmd"

def query(sock, cmd):
    sock.sendall((cmd + '\n').encode('ascii'))
    time.sleep(0.5)
    resp = b""
    while True:
        try:
            chunk = sock.recv(65536)
            if not chunk:
                break
            resp += chunk
            if resp.endswith(b'\n'):
                break
        except socket.timeout:
            break
    return resp.decode('ascii', errors='ignore').strip()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((DEWETRON_IP, DEWETRON_PORT))
    try:
        welcome = sock.recv(4096).decode('ascii', errors='ignore')
        print(f"连接成功: {welcome.strip()[:100]}")
    except socket.timeout:
        print("连接成功")

    # 读取当前 XML（未加载 DMD 前）
    print("\n=== 加载 DMD 前 ===")
    response = query(sock, ":SETUP:READ?")
    xml_start = response.find('<?xml')
    if xml_start < 0:
        xml_start = response.find('<MeasurementConfig')
    xml_before = response[xml_start:] if xml_start >= 0 else response

    # 查找 RecordingSettings 中的属性
    idx = xml_before.find('<RecordingSettings>')
    if idx >= 0:
        end = xml_before.find('</RecordingSettings>', idx)
        chunk = xml_before[idx:end+len('</RecordingSettings>')]
        print("RecordingSettings 中的属性:")
        for m in re.finditer(r'<Property name="([^"]+)">\s*<(\w+)>([^<]*)</\2>', chunk):
            print(f"  {m.group(1)} = {m.group(3)} ({m.group(2)})")
        for m in re.finditer(r'<Property name="([^"]+)">\s*<ScalarValue>\s*<Value>([^<]+)</Value>\s*<Unit>([^<]+)</Unit>', chunk):
            print(f"  {m.group(1)} = {m.group(2)} {m.group(3)} (ScalarValue)")

    # 尝试加载 DMD 文件
    print(f"\n=== 尝试加载 DMD 文件: {DMD_FILE} ===")
    result = query(sock, f':SETUP:LOAD "{DMD_FILE}"')
    print(f"LOAD 结果: {result}")
    time.sleep(2)

    # 读取加载后的 XML
    print("\n=== 加载 DMD 后 ===")
    response = query(sock, ":SETUP:READ?")
    xml_start = response.find('<?xml')
    if xml_start < 0:
        xml_start = response.find('<MeasurementConfig')
    xml_after = response[xml_start:] if xml_start >= 0 else response

    # 查找 RecordingSettings 中的属性
    idx = xml_after.find('<RecordingSettings>')
    if idx >= 0:
        end = xml_after.find('</RecordingSettings>', idx)
        chunk = xml_after[idx:end+len('</RecordingSettings>')]
        print("RecordingSettings 中的属性:")
        for m in re.finditer(r'<Property name="([^"]+)">\s*<(\w+)>([^<]*)</\2>', chunk):
            print(f"  {m.group(1)} = {m.group(3)} ({m.group(2)})")
        for m in re.finditer(r'<Property name="([^"]+)">\s*<ScalarValue>\s*<Value>([^<]+)</Value>\s*<Unit>([^<]+)</Unit>', chunk):
            print(f"  {m.group(1)} = {m.group(2)} {m.group(3)} (ScalarValue)")

    # 搜索 D:/ 和 m_ 相关内容
    print("\n=== 搜索路径和文件名 ===")
    for m in re.finditer(r'<Property name="([^"]+)">\s*<StringValue[^>]*>([^<]*)</StringValue>', xml_after):
        name = m.group(1)
        val = m.group(2)
        if '/' in val or 'D:' in val or 'd:' in val or 'm_' in val:
            if '/' not in name:
                print(f"  {name} = {val}")

    # 保存加载后的 XML
    with open('dewetron_after_load_dmd.xml', 'w', encoding='utf-8') as f:
        f.write(xml_after)
    print(f"\n加载后的 XML 已保存到 dewetron_after_load_dmd.xml ({len(xml_after)} 字节)")

    sock.close()

if __name__ == "__main__":
    main()
