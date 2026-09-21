"""
蓝点直流源联调入口：实现逻辑见 ``scpi_to_modbustcp``（与爱科 ``ItechTranslator`` 同文件）。

- ``BluesightCurveSTC``：界面 STC 参数
- ``BluesightTranslator``：FC16 曲线块、离散寄存器、APPLY
"""

from scpi_to_modbustcp import BluesightCurveSTC, BluesightTranslator
from modbus_visa import ModbusVISA
# 联调用 IP/端口；接入主程序后改为配置或 UI
DEFAULT_HOST = "192.168.40.25"
DEFAULT_PORT = 502


def main() -> None:
    # 现场若 PyVISA SOCKET 读恒 empty、Wireshark 却有应答，改用原生 TCP（API 仍为 ModbusVISA）
    client = ModbusVISA(ip=DEFAULT_HOST, port=DEFAULT_PORT, use_plain_socket=True)
    if not client.connect():
        print("连接失败")
        return
    print("连接成功")

    try:
        obj = BluesightTranslator(client, device_id=1)
        res = obj.translate("*IDN?")
        print(res)
    except Exception as e:
        print(f"执行失败: {e}")
    finally:
        client.disconnect(quiet=True)
        print("已断开连接。")


if __name__ == "__main__":
    main()
