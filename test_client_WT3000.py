"""
测试WT3000的SCPI命令
"""

import pyvisa as visa


rm = visa.ResourceManager()
print("可用VISA资源:")
for resource in rm.list_resources():
    print(" -", resource)

# WT3000_RESOURCE = "ASRL8::INSTR"
# WT3000_BAUDRATE = 19200
DC = "USB0::0x0A69::0x084B::S50000002328::INSTR"
# 开起DC电流
handler = rm.open_resource(DC)
handler.write("OUTP ON")


# class WT3000Client:

#     def __init__(self, resource):
#         self.resource = resource
#         self.handle = None

#     def connect(self):
#         try:
#             handle = rm.open_resource(self.resource, baud_rate=WT3000_BAUDRATE)
#             self.handle = handle
#             self.handle.timeout = 10000
#             self.handle.read_termination = "\n"
#             self.handle.write_termination = "\n"
#             print(f"已连接: {self.resource}")
#             print("*IDN? ->", self.handle.query("*IDN?"))
#         except Exception as e:
#             print(f"连接WT3000失败: {e}")
#             return False
#         return True

#     def disconnect(self):
#         if self.handle:
#             self.handle.close()
#             self.handle = None
#             return True
#         return False

#     def send(self, command):
#         if not self.handle:
#             raise RuntimeError("WT3000未连接")
#         self.handle.write(command)
#         print(f"WT3000 WRITE -> {command}")

#     def query(self, command):
#         if not self.handle:
#             raise RuntimeError("WT3000未连接")
#         result = self.handle.query(command)
#         print(f"WT3000 QUERY -> {command} | {result}")
#         return result


# if __name__ == "__main__":
    # test = WT3000Client(WT3000_RESOURCE)
    # if test.connect():
    #     print(11111111)
    #     commands = [
    #         "*IDN?",
    #         "DISPLAY:MODE FLICker",
    #         # "FLICKER:DISPLAY:ELEMENT 1",
    #         # "FLICKER:ELEMENT1 ON",
    #         # "FLICKER:RESET",
    #         # "FLICKER:COUNT 10",
    #         # "FLICker:UN:VALue 230",
    #         # "FLICKER:FREQuency 50",
    #         # "FLICKER:INIT",
    #         # "FLICKER:STAR",
    #         # "STATus:ERRor"
    #     ]

    #     for command in commands:
    #         print("开始发送命令")
    #         try:
    #             test.send(command)
    #         except Exception as e:
    #             print(f"发送失败: {command} -> {e}")
    #             break

        # try:
        #     print("*IDN? ->", test.query("*IDN?"))
        # except Exception as e:
        #     print(f"查询*IDN?失败: {e}")
