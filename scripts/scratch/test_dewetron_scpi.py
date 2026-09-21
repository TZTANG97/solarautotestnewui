#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
德威创 SCPI 路径测试脚本
测试不同的文件路径格式，找出正确的设置方式。
"""
import time
import socket

DEWETRON_IP = "192.168.40.25"
DEWETRON_PORT = 10001


class DewetronSocket:
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.sock.connect((ip, port))
        try:
            welcome = self.sock.recv(4096).decode('ascii', errors='ignore')
            if welcome.strip():
                print(f"  设备: {welcome.strip()[:100]}")
        except socket.timeout:
            pass

    def query(self, cmd):
        self.sock.sendall((cmd + '\n').encode('ascii'))
        time.sleep(0.3)
        resp = b""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                resp += chunk
                if resp.endswith(b'\n'):
                    break
            except socket.timeout:
                break
        return resp.decode('ascii', errors='ignore').strip()

    def write(self, cmd):
        self.sock.sendall((cmd + '\n').encode('ascii'))

    def close(self):
        self.sock.close()


def test_path(dev, cmd, desc):
    print(f"\n  测试: {desc}")
    print(f"  发送: {cmd}")
    dev.write(cmd)
    time.sleep(0.5)
    resp = dev.query(':STORE:FILE:NAME?')
    print(f"  查询: {resp}")
    err = dev.query(':SYSTEM:ERROR:ALL?')
    print(f"  错误: {err}")
    return resp


def main():
    print(f"连接 {DEWETRON_IP}:{DEWETRON_PORT}...")
    dev = DewetronSocket(DEWETRON_IP, DEWETRON_PORT)
    print("[OK] 已连接\n")

    try:
        # 先停止一切
        dev.write(':ACQUISITION:STOP')
        time.sleep(0.5)
        dev.write(':STORE:STOP')
        time.sleep(0.5)

        print("=== 测试不同路径格式 ===")

        # 测试1: 纯目录
        test_path(dev, ':STORE:FILE:NAME "D:/dxl"', "纯目录 D:/dxl")

        # 测试2: 带反斜杠
        test_path(dev, ':STORE:FILE:NAME "D:\\dxl"', "反斜杠 D:\\dxl")

        # 测试3: 带文件名
        test_path(dev, ':STORE:FILE:NAME "D:/dxl/test.csv"', "带文件名 D:/dxl/test.csv")

        # 测试4: 带文件名无扩展名
        test_path(dev, ':STORE:FILE:NAME "D:/dxl/test"', "带文件名无扩展名")

        # 测试5: 只有盘符
        test_path(dev, ':STORE:FILE:NAME "D:/"', "只有盘符 D:/")

        # 测试6: 用单引号
        test_path(dev, ":STORE:FILE:NAME 'D:/dxl'", "单引号 D:/dxl")

        # 测试7: 不带引号
        test_path(dev, ":STORE:FILE:NAME D:/dxl", "不带引号")

        # 测试8: 查看有没有其他路径相关命令
        print("\n=== 查询路径相关命令 ===")
        for cmd in [":STORE:FILE:NAME?", ":STORE:FILE:NAME? DEFAULT",
                    ":STORE:FILE:PATH?", ":STORE:PATH?",
                    ":STORE:FILE:FORMAT?", ":STORE:FORMAT?"]:
            resp = dev.query(cmd)
            print(f"  {cmd} -> {resp}")

    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        dev.close()
        print("\n[INFO] 已断开")


if __name__ == "__main__":
    main()
