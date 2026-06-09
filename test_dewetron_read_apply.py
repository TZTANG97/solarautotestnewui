"""测试：从 DEWETRON 读取 XML，原样发回，验证设备是否接受。
用法: python test_dewetron_read_apply.py [IP地址] [端口]
例如: python test_dewetron_read_apply.py 192.168.40.21
"""
import argparse
import pyvisa
import time
import re

parser = argparse.ArgumentParser(description="DEWETRON Read-Apply 测试")
parser.add_argument("ip", nargs="?", default="192.168.40.21", help="设备 IP（默认 192.168.40.21）")
parser.add_argument("port", type=int, nargs="?", default=10001, help="端口（默认 10001）")
args = parser.parse_args()

IP = args.ip
PORT = args.port

rm = pyvisa.ResourceManager()
visa_addr = f"TCPIP0::{IP}::{PORT}::SOCKET"
print(f"连接: {visa_addr}")
handle = rm.open_resource(visa_addr)
handle.encoding = 'utf-8'
handle.read_termination = '\r\n'
handle.write_termination = '\r\n'
handle.timeout = 30000
print("连接成功\n")

# 1. 读取设备当前配置
print("=== 1. 读取 :SETUP:READ? ===")
xml = handle.query(":SETUP:READ?")
print(f"读取到 {len(xml)} 字符")

# 去掉 SCPI 前缀
decl_pos = xml.find('<?xml')
if decl_pos > 0:
    xml = xml[decl_pos:]
    print(f"去掉前缀后: {len(xml)} 字符")

# 保存到文件
with open("config_files/dewetron_test_read.xml", "w", encoding="utf-8") as f:
    f.write(xml)
print("已保存: config_files/dewetron_test_read.xml\n")

# 2. 检查 InputChannels
import re
print("=== 2. InputChannels 映射 ===")
for m in re.finditer(r'POWER/InputChannels/([A-Z]+\d+)"><ChannelID>(\d+)</ChannelID>', xml):
    slot, cid = m.group(1), m.group(2)
    if cid != "18446744073709551615":
        print(f"  {slot} -> {cid} (已映射)")
print("  (只显示已映射的槽位)\n")

# 3. 原样发回
print("=== 3. 原样发送 :SETUP:APPLY ===")
xml_bytes = xml.encode('utf-8')
xml_len = len(xml_bytes)
num_digits = len(str(xml_len))
full_cmd = f":SETUP:APPLY #{num_digits}{xml_len}" + xml
print(f"发送: XML {xml_len} 字节, header: #{num_digits}{xml_len}")
handle.write(full_cmd)
time.sleep(3)

# 4. 检查错误
print("\n=== 4. 检查设备错误 ===")
try:
    err = handle.query(":SYSTEM:ERROR:ALL?")
    print(f"错误: {err.strip()}")
except Exception as e:
    print(f"查询错误: {e}")

# 5. 重新读回验证
print("\n=== 5. 重新读回验证 ===")
read_back = handle.query(":SETUP:READ?")
print(f"读回 {len(read_back)} 字符")
decl_pos = read_back.find('<?xml')
if decl_pos > 0:
    read_back = read_back[decl_pos:]

# 比较 InputChannels
print("\n=== 6. 比较 InputChannels ===")
orig_ic = {}
for m in re.finditer(r'POWER/InputChannels/([A-Z]+\d+)"><ChannelID>(\d+)</ChannelID>', xml):
    orig_ic[m.group(1)] = m.group(2)
back_ic = {}
for m in re.finditer(r'POWER/InputChannels/([A-Z]+\d+)"><ChannelID>(\d+)</ChannelID>', read_back):
    back_ic[m.group(1)] = m.group(2)

all_match = True
for slot in sorted(set(list(orig_ic.keys()) + list(back_ic.keys()))):
    o = orig_ic.get(slot, 'N/A')
    b = back_ic.get(slot, 'N/A')
    if o != b:
        print(f"  {slot}: 发送={o} 读回={b} [不同!]")
        all_match = False
if all_match:
    print("  所有 InputChannels 匹配 [OK]")

handle.close()
print("\n测试完成")
