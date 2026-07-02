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


def try_visa_connect(visa_addr, port=10001):
    """用 PyVISA 连接德威创并测试基本命令。"""
    print(f"\n--- 测试 VISA 连接: {visa_addr} ---")

    rm = pyvisa.ResourceManager()
    try:
        handle = rm.open_resource(visa_addr)
        handle.timeout = 15000
        handle.read_termination = '\r\n'
        handle.write_termination = '\r\n'
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
    """测试 SCPI 命令，下载当前配置 XML。"""
    # 1. *IDN? 查询设备信息
    try:
        resp = handle.query("*IDN?")
        print(f"[OK] *IDN? -> {resp.strip()}")
    except Exception as e:
        print(f"[FAIL] *IDN? 失败: {e}")

    # 2. :SYSTEM:VERSION? 查询固件版本
    try:
        resp = handle.query(":SYSTEM:VERSION?")
        print(f"[OK] :SYSTEM:VERSION? -> {resp.strip()}")
    except Exception as e:
        print(f"[FAIL] :SYSTEM:VERSION? 失败: {e}")

    # 3. 清空错误队列
    try:
        handle.write("*CLS")
        time.sleep(0.5)
        print(f"[OK] *CLS 错误队列已清空")
    except Exception as e:
        print(f"[FAIL] *CLS 失败: {e}")

    # 4. 基本查询
    print("\n--- 基本查询 ---")
    try:
        resp = handle.query(":SETUP:NAME?")
        print(f"  :SETUP:NAME? -> {resp.strip()}")
    except Exception as e:
        print(f"  :SETUP:NAME? -> {str(e)[:80]}")

    # 5. :SETUP:READ? 下载当前配置
    try:
        handle.encoding = 'utf-8'
        resp = handle.query(":SETUP:READ?")
        handle.encoding = 'ascii'
        print(f"[OK] :SETUP:READ? -> 长度 {len(resp)} 字符")
        with open("config_files/dewetron.xml", "w", encoding="utf-8") as f:
            f.write(resp)
        print(f"  已保存到: dewetron_config_read.xml")
    except Exception as e:
        print(f"[FAIL] :SETUP:READ? 失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="DEWETRON 测试脚本")
    parser.add_argument("ip", nargs="?", default="192.168.40.25", help="德威创设备 IP（默认 192.168.40.21）")
    parser.add_argument("port", type=int, nargs="?", default=10001, help="SCPI 端口（默认 10001）")
    args = parser.parse_args()

    print("=" * 50)
    print("DEWETRON 测试工具")
    print(f"  IP: {args.ip}")
    print(f"  端口: {args.port}")
    print("=" * 50)
    print()


    # VISA 连接和命令测试
    visa_addr = f"TCPIP0::{args.ip}::{args.port}::SOCKET"
    success = try_visa_connect(visa_addr, args.port)

    if success:
        print("\n所有测试通过！")
    else:
        print("\n测试失败，请检查设备和网络。")
        sys.exit(1)


if __name__ == "__main__":
    main()
