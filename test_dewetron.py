# -*- coding: utf-8 -*-
"""
DEWETRON 测试脚本 — 独立于 Qt 程序，用于验证 TCP/SCPI 连接和命令。

使用方法：
    python test_dewetron.py
    python test_dewetron.py 192.168.40.21
    python test_dewetron.py 192.168.40.21 10001

确保：
    - 你的电脑和德威创设备在同一局域网
    - 德威创设备已开机且网络正常
"""

import sys
import argparse
import time

try:
    import pyvisa
except ImportError:
    print("请先安装 pyvisa: pip install pyvisa")
    sys.exit(1)


def try_raw_socket(ip, port, timeout=5):
    """先用原生 socket 测试 TCP 连接是否可达。"""
    import socket

    print(f"\n--- 测试 TCP 连接: {ip}:{port} ---")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        print(f"[OK] TCP 连接成功")

        # 尝试发送 SCPI 查询
        sock.sendall(b"*IDN?\r\n")
        time.sleep(1)
        response = sock.recv(1024)
        print(f"[OK] 收到响应: {response.decode('ascii', errors='replace').strip()}")

        sock.close()
        return True
    except socket.timeout:
        print(f"[FAIL] 连接超时，请检查设备 IP 和网络")
        return False
    except ConnectionRefusedError:
        print(f"[FAIL] 连接被拒绝，端口 {port} 可能不对")
        return False
    except Exception as e:
        print(f"[FAIL] 连接失败: {e}")
        return False


def try_visa_connect(visa_addr, port=10001):
    """用 PyVISA 连接德威创并测试基本命令。"""
    print(f"\n--- 测试 VISA 连接: {visa_addr} ---")

    rm = pyvisa.ResourceManager()
    try:
        handle = rm.open_resource(visa_addr)
        handle.timeout = 10000
        handle.read_termination = '\n'
        handle.write_termination = '\n'
        # ASCII 编码
        try:
            handle.encoding = 'ascii'
        except Exception:
            pass
        print(f"[OK] VISA 连接成功")
        print(f"  resource_name: {handle.resource_name}")
        print(f"  timeout: {handle.timeout}")

        # 测试命令 1: *IDN? 查询设备信息
        print("\n--- 测试命令: *IDN? ---")
        test_cmds(handle)

        # 提示用户可以手动输入命令
        print("\n" + "=" * 50)
        print("交互式命令模式（输入命令后回车，输入 quit 退出）")
        print("=" * 50)
        while True:
            try:
                cmd = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n退出")
                break
            if not cmd or cmd.lower() == 'quit' or cmd.lower() == 'exit':
                print("退出")
                break
            try:
                handle.write(cmd)
                time.sleep(0.5)
                resp = handle.read()
                print(f"  响应: {resp.strip() if resp.strip() else '(无回显)'}")
            except Exception as e:
                print(f"  错误: {e}")

        return True

    except pyvisa.VisaIOError as e:
        print(f"[FAIL] VISA 连接失败: {e}")
        print("\n可能的原因：")
        print("  1. 设备 IP 或端口不对")
        print("  2. 设备已开机但网络不通（试试 ping")
        print("  3. 端口 10001 不是 SCPI 端口")
        print("  4. 远程桌面客户端还占着连接（德威创只允许 1 个客户端）")
        print("  5. 防火墙阻断了 TCP 连接")
        return False
    except Exception as e:
        print(f"[FAIL] 未知错误: {e}")
        return False
    finally:
        try:
            rm.close()
        except Exception:
            pass

def test_cmds(handle):
    """
    测试命令函数
    """
    # 1. 查询所有通道
    channels = []
    try:
        handle.write("*IDN?")
        print("保存配置信息xml到: E://dewetron.xml")
        handle.write("SETUP:SAVE 'E://dewetron.xml'")
        time.sleep(0.5)
        resp = handle.read()
        channels = [ch.strip() for ch in resp.split(',') if ch.strip()]
        print(f"[OK] 查询通道成功: {channels}")
    except Exception as e:
        print(f"[FAIL] 查询通道失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="DEWETRON 测试脚本")
    parser.add_argument("ip", nargs="?", default="192.168.40.21", help="德威创设备 IP（默认 192.168.40.21）")
    parser.add_argument("port", type=int, nargs="?", default=10001, help="SCPI 端口（默认 10001）")
    parser.add_argument("--no-socket", action="store_true", help="跳过原生 socket 测试，只使用 VISA")
    args = parser.parse_args()

    print("=" * 50)
    print("DEWETRON 测试工具")
    print(f"  IP: {args.ip}")
    print(f"  端口: {args.port}")
    print("=" * 50)
    print()


    # 第二步：VISA 连接和命令测试
    visa_addr = f"TCPIP0::{args.ip}::{args.port}::SOCKET"
    success = try_visa_connect(visa_addr, args.port)

    if success:
        print("\n所有测试通过！")
    else:
        print("\n测试失败，请检查设备和网络。")
        sys.exit(1)


if __name__ == "__main__":
    main()
