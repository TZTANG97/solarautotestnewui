import socket
import threading
import pyvisa
import time


class ModbusVISA:
    def __init__(
        self,
        ip,
        port=502,
        *,
        on_session_renewed=None,
        strict_tcp_ack: bool = False,
        idle_reconnect_after_sec=None,
        fresh_socket_each_send: bool = False,
        use_plain_socket: bool = False,
    ):
        self.ip = ip
        self.port = port
        # True：用标准库 socket 收发 Modbus TCP。部分环境下 PyVISA TCPIP::SOCKET 的 read_raw
        # 长期 empty/timeout，而 Wireshark 可见正常应答时，可改用此路径（API 与 PyVISA 路径一致）。
        self.use_plain_socket = use_plain_socket
        self._sock: socket.socket | None = None
        self.rm = None if use_plain_socket else pyvisa.ResourceManager()
        self._trans_id = 0
        self.inst = None
        self._connected = False
        # True：写寄存器必须收到合法 Modbus TCP 应答（标准设备）。False：爱科等写后不回帧仍视为成功
        self.strict_tcp_ack = strict_tcp_ack
        # 每发一帧先断再连：适配对端「一问一关 TCP」；与 idle 二选一，开启时自动关闭空闲重连
        self.fresh_socket_each_send = fresh_socket_each_send
        # 若干秒无收发则先发制人重连（部分电源 ~25～30s 空闲掐线，可避免下次首包 CONN_LOST）
        self.idle_reconnect_after_sec = idle_reconnect_after_sec
        if self.fresh_socket_each_send:
            self.idle_reconnect_after_sec = 0.0
        elif self.idle_reconnect_after_sec is None:
            self.idle_reconnect_after_sec = 22.0
        self._last_io_mono = None
        # 须可重入：CONN_LOST 重连时会递归调用 send()；普通 Lock 在同线程内二次 acquire 会死锁卡死 UI
        self._io_lock = threading.RLock()
        self._on_session_renewed = on_session_renewed

    def _callback_session_handle(self):
        """同步给外部的「句柄」：PyVISA 路径为 ``inst``；``use_plain_socket`` 时为 ``self``。"""
        return self.inst if self.inst is not None else self

    def _get_next_trans_id(self):
        """获取下一个事务ID，范围1-65535循环"""
        self._trans_id = (self._trans_id % 65535) + 1
        return self._trans_id

    def connect(self, timeout=2000, quiet=False):
        """显式建立连接并验证"""
        try:
            if self.use_plain_socket:
                to_s = max(float(timeout) / 1000.0, 3.0)
                self._sock = socket.create_connection((self.ip, self.port), timeout=to_s)
                self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.inst = None
                test_cmd = bytes.fromhex("000000000006010300000001")
                self._sock.sendall(test_cmd)
                response = self._recv_modbus_tcp_adu(max(int(timeout), 300))
                self._connected = True
                self._last_io_mono = time.monotonic()
                if len(response) >= 9:
                    if not quiet:
                        print(f"[OK] 连接成功(socket): {self.ip}:{self.port}")
                else:
                    if not quiet:
                        print(
                            f"[OK] 连接建立(socket，设备可能不响应测试地址): {self.ip}:{self.port}"
                        )
                if self._on_session_renewed:
                    self._on_session_renewed(self._callback_session_handle())
                return True

            resource_str = f"TCPIP0::{self.ip}::{self.port}::SOCKET"
            self.inst = self.rm.open_resource(resource_str)
            self.inst.write_termination = ''
            self.inst.read_termination = ''
            self.inst.timeout = timeout
            
            # 验证连接：发送一个Modbus事务（读一个寄存器）
            test_cmd = "0000 0000 0006 01 03 0000 0001"
            self.inst.write_raw(bytes.fromhex(test_cmd.replace(" ", "")))
            response = b''
            try:
                response = self._recv_modbus_tcp_adu(max(int(timeout), 300))
            except pyvisa.errors.VisaIOError:
                pass
            self._connected = True
            self._last_io_mono = time.monotonic()
            if len(response) >= 9:
                if not quiet:
                    print(f"[OK] 连接成功: {self.ip}:{self.port}")
            else:
                if not quiet:
                    print(f"[OK] 连接建立（设备可能不响应测试地址）: {self.ip}:{self.port}")
            if self._on_session_renewed:
                self._on_session_renewed(self._callback_session_handle())
            return True

        except Exception as e:
            self._connected = False
            print(f"[ERROR] 连接失败: {e}")
            return False

    def disconnect(self, quiet=False):
        """关闭连接"""
        if self._sock:
            try:
                self._sock.close()
                if not quiet:
                    print("[OK] 连接已关闭(socket)")
            except Exception:
                pass
            finally:
                self._sock = None
        if self.inst:
            try:
                self.inst.close()
                if not quiet:
                    print("[OK] 连接已关闭")
            except:
                pass
            finally:
                self.inst = None
        self._connected = False
        self._last_io_mono = None

    def _maybe_refresh_stale_connection(self) -> bool:
        """空闲超时则静默重连，减轻对端已关 TCP、首字节 CONN_LOST。"""
        thr = self.idle_reconnect_after_sec
        if thr is None or thr <= 0:
            return True
        if self._last_io_mono is None:
            return True
        if time.monotonic() - self._last_io_mono <= thr:
            return True
        print(f'[ModbusVISA] 空闲超过 {thr:.0f}s，主动重连（避免对端空闲掐线）')
        with self._io_lock:
            self.disconnect(quiet=True)
        if not self.connect(timeout=2000, quiet=True):
            return False
        if self._on_session_renewed:
            self._on_session_renewed(self._callback_session_handle())
        self._last_io_mono = time.monotonic()
        return True

    def _silent_recover(self) -> bool:
        """断开并重新 open TCP，同步 on_session_renewed；用于失效会话或每帧新连接。"""
        try:
            with self._io_lock:
                self.disconnect(quiet=True)
        except Exception:
            pass
        if not self.connect(timeout=2000, quiet=True):
            return False
        if self._on_session_renewed:
            self._on_session_renewed(self._callback_session_handle())
        self._last_io_mono = time.monotonic()
        return True

    def _read_exact(self, n: int, timeout_ms: int) -> bytes:
        """从 SOCKET 读取恰好 n 字节（可能分多次到达）。

        PyVISA TCPIP SOCKET 上 ``read_raw`` 常在应答未到齐时先返回空块；若在首个空块就退出，
        会与 pymodbus 行为不一致（表现为 FC03/FC04 恒 empty）。因此在「总超时」内持续尝试，
        遇空块短时退让再继续读。
        """
        if n <= 0:
            return b''
        deadline = time.monotonic() + max(int(timeout_ms), 1) / 1000.0
        buf = b''
        while len(buf) < n:
            if time.monotonic() >= deadline:
                break
            remain_ms = int((deadline - time.monotonic()) * 1000)
            if remain_ms < 1:
                remain_ms = 1
            self.inst.timeout = remain_ms
            try:
                chunk = self.inst.read_raw(n - len(buf))
            except pyvisa.errors.VisaIOError:
                break
            if chunk:
                buf += chunk
            else:
                time.sleep(0.002)
        return buf

    def _read_exact_sock(self, sock: socket.socket, n: int, timeout_ms: int) -> bytes:
        """原生 TCP：按总超时凑满 n 字节；对端关闭时 recv 返回空。"""
        if n <= 0:
            return b""
        deadline = time.monotonic() + max(int(timeout_ms), 1) / 1000.0
        buf = b""
        while len(buf) < n:
            if time.monotonic() >= deadline:
                break
            remain_ms = int((deadline - time.monotonic()) * 1000)
            if remain_ms < 1:
                remain_ms = 1
            sock.settimeout(remain_ms / 1000.0)
            try:
                chunk = sock.recv(n - len(buf))
            except OSError:
                break
            if chunk:
                buf += chunk
            else:
                break
        return buf

    def _read_exact_any(self, n: int, timeout_ms: int) -> bytes:
        if self._sock is not None:
            return self._read_exact_sock(self._sock, n, timeout_ms)
        return self._read_exact(n, timeout_ms)

    def _send_raw_all(self, data: bytes) -> None:
        if self._sock is not None:
            self._sock.sendall(data)
            return
        self.inst.write_raw(data)

    def _recv_modbus_tcp_adu(self, timeout_ms: int) -> bytes:
        """按 Modbus TCP MBAP 读完整一帧应答（含 Unit + PDU）。"""
        hdr = self._read_exact_any(7, timeout_ms)
        if len(hdr) < 7:
            return hdr
        ln = (hdr[4] << 8) | hdr[5]
        if ln > 512:
            ln = 512
        if ln <= 1:
            return hdr
        pdu_rest = self._read_exact_any(ln - 1, timeout_ms)
        return hdr + pdu_rest

    def is_connected(self):
        """检查连接状态"""
        return self._connected and (self.inst is not None or self._sock is not None)

    @staticmethod
    def _should_retry_send(err_s: str) -> bool:
        """仅对真实断线重试；无应答不走重连（部分网关/爱科写后不回 Modbus 帧）。"""
        return '1073807194' in err_s or 'CONN_LOST' in err_s

    @staticmethod
    def _tcp_adu_pdu_fc(cmd_hex: str) -> int | None:
        """MBAP 后第 2 字节为 Modbus 功能码（读请求为 0x03/0x04）。"""
        try:
            b = bytes.fromhex(cmd_hex.replace(" ", ""))
            if len(b) < 8:
                return None
            return b[7]
        except ValueError:
            return None

    def send(self, cmd_hex, read_timeout=200, expect_response=True, _retry=True):
        """
        发送 Modbus TCP 帧；写后按 MBAP 长度读满一帧应答。
        VI_ERROR_CONN_LOST 时自动静默重连并重试一次（需配合 on_session_renewed 同步外部 handle）。
        """
        if self.fresh_socket_each_send:
            if not self._silent_recover():
                print('[ERROR] ModbusVISA 每帧重连失败')
                return None
        else:
            if not self.is_connected():
                print('[ModbusVISA] 会话失效，尝试静默恢复 TCP…')
                if not self._silent_recover():
                    print('[ERROR] 自动恢复失败，请点击连接或检查 IP/端口')
                    return None
            if not self._maybe_refresh_stale_connection():
                print('[ERROR] 空闲重连失败')
                self._connected = False
                return None

        cmd = bytes.fromhex(cmd_hex.replace(" ", ""))
        err = None
        err_s = ''
        with self._io_lock:
            try:
                to = max(int(read_timeout), 300)
                if self.inst is not None:
                    self.inst.timeout = to
                pdu_preview = cmd.hex().upper()
                if len(pdu_preview) > 80:
                    pdu_preview = pdu_preview[:80] + '…'
                transport = "socket" if self._sock is not None else "visa"
                print(
                    f'[ModbusVISA] TX {transport} ip={self.ip}:{self.port} expect_resp={expect_response} '
                    f'to_ms={to} adu={pdu_preview}'
                )
                self._send_raw_all(cmd)
                # 宽松写：爱科等常无 Modbus TCP 应答，若仍按 MBAP 读满一帧会长时间 empty，
                # 易诱发 PyVISA CONN_LOST；且写路径无需排空（对端不发应答则缓冲区无残留）。
                if not expect_response:
                    self._last_io_mono = time.monotonic()
                    print('[ModbusVISA] RX expect_resp=False (宽松写，不等待读应答)')
                    return True
                response = self._recv_modbus_tcp_adu(to)
                if response is None or len(response) == 0:
                    rx_s = 'empty/timeout'
                else:
                    hx = response.hex().upper()
                    rx_s = f'len={len(response)} hex={hx[:96]}' + ('…' if len(hx) > 96 else '')
                print(
                    f'[ModbusVISA] RX expect_resp={expect_response} {rx_s}'
                )
                # Modbus TCP 规定一问一答；应答过短/超时未读到完整帧时套接字往往已半开，下次必掉线
                if response is None or len(response) < 9:
                    raise IOError('MODBUS_EMPTY_RESPONSE: 应答缺失或过短，无法与设备帧同步')
                self._last_io_mono = time.monotonic()
                return response
            except Exception as e:
                err = e
                err_s = str(e)
                print(f'[ModbusVISA] send 异常: {type(e).__name__}: {e}')

        # 释放锁后再断开/重连，避免 connect() 阻塞时其它路径长时间拿不到锁；并避免在持锁时递归 send 依赖 RLock
        if err is not None and _retry and self._should_retry_send(err_s):
            print('[WARN] Modbus TCP 传输异常，自动重连并重试…')
            try:
                with self._io_lock:
                    self.disconnect(quiet=True)
            except Exception:
                pass
            if self.connect(timeout=2000, quiet=True):
                if self._on_session_renewed:
                    self._on_session_renewed(self._callback_session_handle())
                return self.send(cmd_hex, read_timeout, expect_response, _retry=False)

        if err is not None:
            # FC03/FC04 读超时：不断开 TCP，便于上层换地址/功能码重试（避免 *IDN? 一次失败就掉线）
            fc = self._tcp_adu_pdu_fc(cmd_hex)
            if (
                expect_response
                and 'MODBUS_EMPTY_RESPONSE' in err_s
                and fc in (0x03, 0x04)
            ):
                print('[WARN] Modbus 读应答为空或超时，保持连接（可重试 FC03/FC04）')
                return None

            print(f"[ERROR] 发送失败: {err}")
            try:
                with self._io_lock:
                    self.disconnect(quiet=True)
            except Exception:
                pass
            self._connected = False
            if self._on_session_renewed:
                try:
                    self._on_session_renewed(None)
                except Exception:
                    pass
            return None

    def read_holding_register(self, addr, quantity=1, unit=1, *, read_timeout_ms=3000):
        """读保持寄存器（功能码03）。默认读超时 3000ms，避免 FC03 长应答在 ~300ms 被误判为空。"""
        trans_id = self._get_next_trans_id()
        cmd = f"{trans_id:04X} 0000 0006 {unit:02X} 03 {addr:04X} {quantity:04X}"
        return self.send(cmd, read_timeout=read_timeout_ms, expect_response=True)

    def read_input_register(self, addr, quantity=1, unit=1, *, read_timeout_ms=3000):
        """读输入寄存器（功能码04）。默认读超时 3000ms，与现场 *IDN?/批量读 一致。"""
        trans_id = self._get_next_trans_id()
        cmd = f"{trans_id:04X} 0000 0006 {unit:02X} 04 {addr:04X} {quantity:04X}"
        return self.send(cmd, read_timeout=read_timeout_ms, expect_response=True)

    def write_register(self, addr, value, unit=1, verify=False, device_id=None):
        """
        写单个寄存器（功能码06）
        verify=True: 写后读取验证
        device_id: 与 pymodbus / ItechTranslator 一致，等价于 unit（单元地址）
        """
        if device_id is not None:
            unit = device_id
        trans_id = self._get_next_trans_id()
        cmd = f"{trans_id:04X} 0000 0006 {unit:02X} 06 {addr:04X} {value:04X}"
        if self.strict_tcp_ack:
            return self.send(cmd, read_timeout=2500, expect_response=True)
        # 宽松：仍尝试短读以排空可能存在的应答，无应答也视为写成功（与现场爱科 8080 行为一致）
        return self.send(cmd, read_timeout=800, expect_response=False)

    def write_registers(self, addr, values, unit=1, verify=False, device_id=None):
        """写多个寄存器（功能码10）；device_id 同 write_register。"""
        if device_id is not None:
            unit = device_id
        trans_id = self._get_next_trans_id()
        quantity = len(values)
        byte_count = quantity * 2
        data_hex = ''.join(f"{v:04X}" for v in values)
        pdu_length = 7 + byte_count
        
        cmd = f"{trans_id:04X} 0000 {pdu_length:04X} {unit:02X} 10 {addr:04X} {quantity:04X} {byte_count:02X} {data_hex}"
        if self.strict_tcp_ack:
            return self.send(cmd, read_timeout=2500, expect_response=True)
        return self.send(cmd, read_timeout=800, expect_response=False)

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