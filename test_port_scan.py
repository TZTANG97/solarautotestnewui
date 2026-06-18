"""扫描 Chroma AC 源的常用 SCPI 端口，找出哪个在监听。"""
import socket
import sys

host = sys.argv[1] if len(sys.argv) > 1 else "192.168.40.10"

# 扫描范围：常见 SCPI/仪器端口 + 1024~10000 常用段
ports = (
    [2101]  # Chroma 61800 Ethernet TCP port (manual 8.1.4)
    + list(range(5000, 5010))
    + list(range(5020, 5030))
    + list(range(10000, 10010))
    + list(range(30000, 30010))
    + [4000, 4001, 8080, 8888, 9000, 9090, 12345, 50000]
)

print(f"扫描 {host} ...")
open_ports = []
for p in sorted(set(ports)):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex((host, p))
        if result == 0:
            open_ports.append(p)
            print(f"  端口 {p} OPEN")
        s.close()
    except Exception:
        pass

if open_ports:
    print(f"\n发现 {len(open_ports)} 个开放端口: {open_ports}")
    # 尝试对每个开放端口发 *IDN?
    for p in open_ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((host, p))
            s.sendall(b"*IDN?\n")
            resp = s.recv(4096)
            print(f"  端口 {p} *IDN? => {resp.decode('ascii', errors='replace').strip()}")
            s.close()
        except Exception as e:
            print(f"  端口 {p} *IDN? 失败: {e}")
else:
    print("未发现开放端口")
