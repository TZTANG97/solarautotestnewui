#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从 DEWETRON 读取 XML，查找 HarmonicsType 枚举值"""
import time
import socket
import re

DEWETRON_IP = "192.168.40.25"
DEWETRON_PORT = 10001

def query(sock, cmd):
    sock.sendall((cmd + '\n').encode('ascii'))
    time.sleep(0.3)
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

    # 先设置 grouping type 为 "类型1"，然后读取 XML 看实际值
    print("\n设置 HarmonicsType 为 TYPE1_5_6_9...")
    query(sock, ":STOP")

    # 读取当前 XML
    print("读取 XML...")
    response = query(sock, ":SETUP:READ?")

    xml_start = response.find('<?xml')
    if xml_start < 0:
        xml_start = response.find('<MeasurementConfig')
    xml = response[xml_start:] if xml_start >= 0 else response

    # 查找 HarmonicsType 相关内容
    print("\n" + "=" * 60)
    print("HarmonicsType 相关内容:")
    print("=" * 60)

    # 找所有 HarmonicsType 出现的位置
    for m in re.finditer(r'HarmonicsType[^<]*<[^>]*>[^<]*</[^>]*>', xml):
        print(f"  {m.group()}")

    # 找 enum 定义
    for m in re.finditer(r'enum="HarmonicsType"[^>]*>([^<]*)', xml):
        print(f"  enum值: {m.group(1)}")

    # 找 Property name 包含 Harmonics 的
    print("\n" + "=" * 60)
    print("所有 Harmonics 相关属性:")
    print("=" * 60)
    for m in re.finditer(r'<Property name="([^"]*[Hh]armonics[^"]*)">\s*<(\w+)>([^<]*)</\2>', xml):
        print(f"  {m.group(1)} = {m.group(3)} (类型: {m.group(2)})")

    # 保存 XML 供分析
    with open('dewetron_harmonics_latest.xml', 'w', encoding='utf-8') as f:
        f.write(xml)
    print(f"\nXML 已保存到 dewetron_harmonics_latest.xml ({len(xml)} 字节)")

    sock.close()

if __name__ == "__main__":
    main()
