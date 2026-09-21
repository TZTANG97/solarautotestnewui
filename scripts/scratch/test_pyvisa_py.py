"""测试 pyvisa-py 后端：INSTR vs SOCKET 模式。"""
import pyvisa as visa

rm = visa.ResourceManager("@py")
print(f"Backend: {rm.visalib}")

# 试各种地址格式
addrs = [
    "TCPIP0::192.168.40.10::INSTR",
    "TCPIP0::192.168.40.10::5027::SOCKET",
    "TCPIP0::192.168.40.10::5025::SOCKET",
    "TCPIP0::192.168.40.10::30000::SOCKET",
    "TCPIP0::192.168.40.10::5000::SOCKET",
]

for addr in addrs:
    print(f"\n--- {addr} ---")
    try:
        h = rm.open_resource(addr)
        print(f"  Opened: {type(h).__name__}")
        # SOCKET 模式需要设终止符
        if "SOCKET" in addr:
            h.read_termination = "\n"
            h.write_termination = "\n"
        h.write("*IDN?")
        idn = h.read()
        print(f"  *IDN? => {idn}")
        h.close()
        print("  SUCCESS!")
        break
    except Exception as e:
        print(f"  Failed: {e}")
