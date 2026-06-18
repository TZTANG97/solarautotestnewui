"""原生 TCP Socket SCPI 通信封装。

绕过 PyVISA/NI-VISA，直接用 Python socket 发送 SCPI 命令。
适用于 NI-VISA 不支持 TCPIP 资源的场景。
"""

import socket
import threading
import time

# Chroma 等 SCPI 仪器常用端口，按优先级排列
# 2101 = Chroma 61800 系列 Ethernet TCP 端口（手册 8.1.4 节）
_COMMON_SCPI_PORTS = [2101, 5027, 5025, 30000, 5000, 5001]


class ScpiSocket:
    """通过原生 TCP Socket 发送 SCPI 命令的封装类。

    提供与 PyVISA Instrument 兼容的 write/query/read 接口。
    支持 TCP keepalive 和断线自动重连。
    """

    def __init__(self, host, port=None, timeout=10):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock = None
        self._lock = threading.RLock()
        self._connected = False
        self.resource_name = f"TCP::{host}::{port or 'auto'}"

    def _create_socket(self):
        """创建并配置 TCP socket，启用 keepalive。"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
        except (AttributeError, OSError):
            pass
        return sock

    def connect(self):
        """建立 TCP 连接。port=None 时自动探测常见端口。"""
        if self.port is not None:
            self._try_connect(self.port)
            return
        # 自动探测
        for p in _COMMON_SCPI_PORTS:
            try:
                self._try_connect(p)
                print(f"[ScpiSocket] 自动探测到端口 {p}")
                return
            except (ConnectionRefusedError, OSError, socket.timeout):
                continue
        raise ConnectionError(f"无法连接 {self.host}：所有常见 SCPI 端口均被拒绝")

    def _try_connect(self, port):
        """尝试连接指定端口。"""
        self._sock = self._create_socket()
        self._sock.connect((self.host, port))
        self.port = port
        self._connected = True
        self.resource_name = f"TCP::{self.host}::{port}"

    def _reconnect(self):
        """断线重连。"""
        self.close()
        time.sleep(0.5)
        self._try_connect(self.port)

    def close(self):
        """关闭 TCP 连接。"""
        self._connected = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def write(self, cmd):
        """发送 SCPI 命令（不读取响应）。自动重连一次。"""
        with self._lock:
            data = (cmd.strip() + "\n").encode("ascii")
            try:
                self._sock.sendall(data)
            except (OSError, AttributeError):
                self._reconnect()
                self._sock.sendall(data)

    def query(self, cmd, read_timeout=None):
        """发送 SCPI 命令并读取响应。自动重连一次。"""
        with self._lock:
            data = (cmd.strip() + "\n").encode("ascii")
            try:
                self._sock.sendall(data)
            except (OSError, AttributeError):
                self._reconnect()
                self._sock.sendall(data)
            return self._recv_response(read_timeout)

    def _recv_response(self, read_timeout=None):
        """接收一行响应（以 \\n 结尾）。"""
        self._sock.settimeout(read_timeout or self.timeout)
        chunks = []
        while True:
            try:
                chunk = self._sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
                if chunk.endswith(b"\n"):
                    break
            except socket.timeout:
                break
        return b"".join(chunks).decode("ascii", errors="replace").strip()

    def read(self):
        """读取响应。"""
        with self._lock:
            return self._recv_response()

    @property
    def connected(self):
        """检查连接状态。"""
        if self._sock is None or not self._connected:
            return False
        try:
            self._sock.getpeername()
            return True
        except OSError:
            return False
