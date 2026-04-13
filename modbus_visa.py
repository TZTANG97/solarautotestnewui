import pyvisa
import time


class ModbusVISA:
    def __init__(self, ip, port=502):
        self.ip = ip
        self.port = port
        self.rm = pyvisa.ResourceManager()
        self._trans_id = 0
        self.inst = None
        self._connected = False

    def _get_next_trans_id(self):
        """获取下一个事务ID，范围1-65535循环"""
        self._trans_id = (self._trans_id % 65535) + 1
        return self._trans_id

    def connect(self, timeout=2000):
        """显式建立连接并验证"""
        try:
            resource_str = f"TCPIP0::{self.ip}::{self.port}::SOCKET"
            self.inst = self.rm.open_resource(resource_str)
            self.inst.write_termination = ''
            self.inst.read_termination = ''
            self.inst.timeout = timeout
            
            # 验证连接：发送一个Modbus事务（读一个寄存器）
            test_cmd = "0000 0000 0006 01 03 0000 0001"
            self.inst.write_raw(bytes.fromhex(test_cmd.replace(" ", "")))
            
            try:
                response = self.inst.read_raw(1024)
                if len(response) >= 9:
                    self._connected = True
                    print(f"[OK] 连接成功: {self.ip}:{self.port}")
                    return True
            except pyvisa.errors.VisaIOError:
                # 超时但TCP连接已建立
                self._connected = True
                print(f"[OK] 连接建立（设备可能不响应测试地址）: {self.ip}:{self.port}")
                return True
                
        except Exception as e:
            self._connected = False
            print(f"[ERROR] 连接失败: {e}")
            return False

    def disconnect(self):
        """关闭连接"""
        if self.inst:
            try:
                self.inst.close()
                print("[OK] 连接已关闭")
            except:
                pass
            finally:
                self.inst = None
                self._connected = False

    def is_connected(self):
        """检查连接状态"""
        return self._connected and self.inst is not None

    def send(self, cmd_hex, read_timeout=200, expect_response=True):
        """
        发送Modbus命令
        返回: bytes(响应数据) 或 None(错误) 或 True(写操作成功无响应)
        """
        if not self.is_connected():
            print("[ERROR] 未连接，请先调用 connect()")
            return None
            
        cmd = bytes.fromhex(cmd_hex.replace(" ", ""))
        
        try:
            self.inst.timeout = read_timeout
            self.inst.write_raw(cmd)
            
            if not expect_response:
                return True  # 明确不需要响应的写操作
                
            try:
                time.sleep(0.05)
                response = self.inst.read_raw(1024)
                return response  # 返回实际字节数据
            except pyvisa.errors.VisaIOError:
                # 读超时 - 对于写操作这是正常的，对于读操作需要处理
                return b''  # 返回空字节而不是True，便于统一处理
                
        except Exception as e:
            print(f"[ERROR] 发送失败: {e}")
            self._connected = False
            return None

    def read_holding_register(self, addr, quantity=1, unit=1):
        """读保持寄存器（功能码03）"""
        trans_id = self._get_next_trans_id()
        cmd = f"{trans_id:04X} 0000 0006 {unit:02X} 03 {addr:04X} {quantity:04X}"
        return self.send(cmd, expect_response=True)

    def read_input_register(self, addr, quantity=1, unit=1):
        """读输入寄存器（功能码04）"""
        trans_id = self._get_next_trans_id()
        cmd = f"{trans_id:04X} 0000 0006 {unit:02X} 04 {addr:04X} {quantity:04X}"
        return self.send(cmd, expect_response=True)

    def write_register(self, addr, value, unit=1, verify=False):
        """
        写单个寄存器（功能码06）
        verify=True: 写后读取验证
        """
        trans_id = self._get_next_trans_id()
        cmd = f"{trans_id:04X} 0000 0006 {unit:02X} 06 {addr:04X} {value:04X}"
        
        if verify:
            return self.send(cmd, expect_response=True)
        else:
            return self.send(cmd, expect_response=False)

    def write_registers(self, addr, values, unit=1, verify=False):
        """写多个寄存器（功能码10）"""
        trans_id = self._get_next_trans_id()
        quantity = len(values)
        byte_count = quantity * 2
        data_hex = ''.join(f"{v:04X}" for v in values)
        pdu_length = 7 + byte_count
        
        cmd = f"{trans_id:04X} 0000 {pdu_length:04X} {unit:02X} 10 {addr:04X} {quantity:04X} {byte_count:02X} {data_hex}"
        
        if verify:
            return self.send(cmd, expect_response=True)
        else:
            return self.send(cmd, expect_response=False)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


# ============ 使用示例 ============

def format_response(resp):
    """格式化响应数据用于显示"""
    if resp is None:
        return "错误/无连接"
    elif resp == b'':
        return "超时/无响应"
    elif isinstance(resp, bytes):
        return resp.hex()
    else:
        return str(resp)


if __name__ == "__main__":
    # 方式1：显式连接管理
    mb = ModbusVISA("192.168.40.40")

    if mb.connect():
        # 读输入寄存器
        resp = mb.read_input_register(0x0BB8)
        print(f"读输入寄存器: {format_response(resp)}")
        
        # 读保持寄存器
        resp = mb.read_holding_register(0x0000, quantity=2)
        print(f"读保持寄存器: {format_response(resp)}")
        
        # 写寄存器（不等待响应）
        result = mb.write_register(0x0BB8, 0x0055)
        print(f"写寄存器结果: {'成功' if result else '失败'}")
        
        # 写寄存器并验证（等待响应）
        resp = mb.write_register(0x0BB9, 0x00AA, verify=True)
        print(f"写寄存器验证: {format_response(resp)}")
        
        mb.disconnect()

    # 方式2：使用上下文管理器
    print("\n--- 使用 with 语句 ---")
    with ModbusVISA("192.168.40.40") as mb:
        if mb.is_connected():
            resp = mb.read_holding_register(0x0000, quantity=2)
            print(f"读取结果: {format_response(resp)}")