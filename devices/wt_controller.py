import time

from devices.scpi_common import _configure_scpi_resource
from devices.wt3000_legacy_ethernet import parse_socket_resource, try_idn_over_legacy
from devices.wt_scpi_rate import (
    is_serial_resource,
    parse_rate_ms,
    rate_command,
    rates_match_ms,
    serial_too_slow_for_rate,
    snap_rate_ms,
)


# 502/2101/8080 是电源口。写一串 ASCII 也能“成功”，不能当成 WT 已连接。
_WT_POWER_PORTS = frozenset({502, 2101, 8080})
# 裸 SCPI 探测要短：WT3000 网口同时只允许 1 个连接，探 10 秒会把后续旧协议顶成「积极拒绝」。
_WT_SOCKET_IDN_TIMEOUT_MS = 2000


def _is_timeout_error(exc) -> bool:
    text = str(exc or "").upper()
    return "TMO" in text or "TIMEOUT" in text or "TIMED OUT" in text


def _is_connection_refused(exc) -> bool:
    text = str(exc or "")
    upper = text.upper()
    return (
        "10061" in text
        or "积极拒绝" in text
        or "ACTIVELY REFUSED" in upper
        or "CONNECTION REFUSED" in upper
        or "WSAECONNREFUSED" in upper
    )


def _is_rsrc_nfound(exc) -> bool:
    text = str(exc or "")
    return "RSRC_NFOUND" in text.upper() or "-1073807343" in text


def choose_wt_connect_error(last_error, socket_timeout_error=None, opened_idn_error=None):
    """后面的 INSTR 资源找不到时，保留已经打开的网口上的 *IDN? 结果。"""
    if socket_timeout_error is not None and (
        last_error is None or _is_rsrc_nfound(last_error)
    ):
        return socket_timeout_error
    if opened_idn_error and (last_error is None or _is_rsrc_nfound(last_error)):
        if isinstance(opened_idn_error, BaseException):
            return opened_idn_error
        return Exception(str(opened_idn_error))
    if last_error is not None:
        return last_error
    return Exception("WT3000连接失败")


class WT3000Controller:
    """WT3000 控制器，统一管理连接、断开和基础命令。"""

    def __init__(self, logger, show_message, rm, baud_rate="9600"):
        self.logger = logger
        self.show_message = show_message
        self.rm = rm
        self.baud_rate = baud_rate
        self.handle = None
        self.connected = False
        self.resource = ''
        self.last_rate_ms = None

    def _candidate_resources(self, tcp_addr):
        """生成 VISA 候选。横河网口常见 SOCKET(5025) / VXI-11 INSTR，缺一易报 RSRC_NFOUND。"""
        if not tcp_addr:
            return []
        text = str(tcp_addr).strip()
        resources = []
        upper = text.upper()
        ip, port = "", ""
        if upper.startswith("TCPIP"):
            parts = [p.strip() for p in text.split("::") if p.strip()]
            if len(parts) >= 2:
                ip = parts[1]
            if len(parts) >= 3 and parts[2].isdigit():
                port = parts[2]
        elif ":" in text:
            ip, port = text.split(":", 1)
            ip, port = ip.strip(), port.strip()
        elif text.count(".") == 3:
            ip, port = text.strip(), ""

        given_port = int(port) if str(port).isdigit() else None
        keep_given = upper.startswith(("GPIB", "ASRL", "USB")) or (
            upper.startswith("TCPIP") and given_port not in _WT_POWER_PORTS
        )
        if keep_given:
            resources.append(text)

        if ip:
            ports = []
            # 用户写了哪个命令口就先试哪个。5025 是裸 SCPI，10001 是带登录的旧协议。
            # 不按型号改口；另一个口只放在后面，前面失败再试。
            if port and port.isdigit() and int(port) not in _WT_POWER_PORTS:
                ports.append(port)
            for p in ("5025", "5024", "10001"):
                if p not in ports:
                    ports.append(p)
            # SOCKET 优先（纯 TCP，NI-VISA/pyvisa-py 都较稳）
            for p in ports:
                resources.append(f"TCPIP0::{ip}::{p}::SOCKET")
            # VXI-11 / INSTR（部分固件只认这个）
            resources.extend(
                [
                    f"TCPIP0::{ip}::INSTR",
                    f"TCPIP0::{ip}::inst0::INSTR",
                ]
            )
            for p in ports:
                resources.append(f"TCPIP0::{ip}::{p}::INSTR")
        elif text and text not in resources:
            resources.append(text)

        seen = set()
        ordered = []
        for item in resources:
            if item and item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered

    def _try_open(self, rm, resource_string):
        handle = rm.open_resource(resource_string)
        _configure_scpi_resource(handle)
        handle.timeout = 10000
        # 网口会话写波特率会让随后的 *IDN? 一直超时。只对串口设置。
        if not is_serial_resource(resource_string):
            return handle
        try:
            handle.baud_rate = int(self.baud_rate)
            handle.data_bits = 8
            handle.parity = __import__("pyvisa").constants.Parity.none
            handle.stop_bits = __import__("pyvisa").constants.StopBits.one
            handle.flow_control = __import__("pyvisa").constants.VI_ASRL_FLOW_NONE
        except Exception as serial_cfg_err:
            self.logger.info(f"WT3000串口参数设置失败: {serial_cfg_err}")
            print(f"WT3000串口参数设置失败: {serial_cfg_err}")
        return handle

    def _close_quiet(self, handle):
        if handle is None:
            return
        try:
            handle.close()
        except Exception:
            pass

    def _idn_text_is_wt(self, idn: str) -> bool:
        """电源口会接受 TCP 写入。必须读到横河功率分析仪 IDN 才算连上。"""
        upper = str(idn or "").upper()
        if "WT" in upper or "YOKOGAWA" in upper:
            self.logger.info(f"WT3000 IDN: {idn}")
            print(f"WT3000 IDN: {idn}")
            return True
        print(f"WT3000 拒绝非功率分析仪: {idn}")
        return False

    def _open_identified(self, rm, resource_string):
        """打开资源并读 *IDN?。

        网口先用 LF，超时后换一次新连接再用 CR+LF。
        返回 (handle, None) 表示已确认是 WT。
        返回 (None, 说明) 表示口已打开但身份不是功率分析仪。
        打不开或两次身份查询都超时则抛出异常。
        """
        is_socket = str(resource_string).upper().endswith("::SOCKET")
        # 网口裸 SCPI 只试 LF；WT3000 无应答时由 connect() 改走横河旧协议，避免再空等一轮 CRLF。
        terms = ("\n",) if is_socket else ("\n",)
        timeout_ms = _WT_SOCKET_IDN_TIMEOUT_MS if is_socket else 4000
        for term in terms:
            handle = None
            try:
                handle = self._try_open(rm, resource_string)
                handle.timeout = timeout_ms
                handle.write_termination = term
                handle.read_termination = "\n"
                idn = str(handle.query("*IDN?")).strip()
            except Exception as exc:
                self._close_quiet(handle)
                self.logger.info(f"WT3000 *IDN? 失败({term!r}): {exc}")
                print(f"WT3000 *IDN? 失败({term!r}): {exc}")
                if _is_timeout_error(exc) and term != terms[-1]:
                    continue
                raise
            if self._idn_text_is_wt(idn):
                return handle, None
            self._close_quiet(handle)
            return None, f"端口已打开，但 *IDN? 不是功率分析仪: {idn}"
        raise Exception("WT3000 *IDN? 失败")

    def _is_legacy_socket(self, resource_string) -> bool:
        """10001 是横河旧协议口，不看型号。5025/5024 仍走裸 SCPI。"""
        if not str(resource_string).upper().endswith("::SOCKET"):
            return False
        _host, port = parse_socket_resource(resource_string)
        return int(port) == 10001

    def _try_legacy_ethernet(self, resource_string, tried_keys: set):
        """10001：anonymous 登录 + 组帧后再 *IDN?。其它口不走这里。"""
        if not self._is_legacy_socket(resource_string):
            return None
        host, port = parse_socket_resource(resource_string)
        if not host:
            return None
        key = (host, int(port))
        if key in tried_keys:
            return None
        tried_keys.add(key)
        self.logger.info(f"WT3000尝试横河旧协议: {host}:{port}")
        print(f"WT3000尝试横河旧协议: {host}:{port}")
        handle, idn_or_err = try_idn_over_legacy(host, port, timeout_s=10.0)
        if handle is None:
            self.logger.info(f"WT3000 旧协议失败: {idn_or_err}")
            print(f"WT3000 旧协议失败: {idn_or_err}")
            raise TimeoutError(f"WT3000 legacy ethernet failed: {idn_or_err}")
        if not self._idn_text_is_wt(idn_or_err):
            self._close_quiet(handle)
            return None, f"旧协议已登录，但 *IDN? 不是功率分析仪: {idn_or_err}"
        return handle, None

    def _legacy_first_resource(self, tcp_addr):
        """地址写明 10001 时，第一候选就是旧协议口。裸 IP / 5025 不提前占 10001。"""
        text = str(tcp_addr or "").strip()
        upper = text.upper()
        if ":5025" in text or "::5025::" in upper or "::5024::" in upper or ":5024" in text:
            return ""
        if not (":" in text or upper.startswith("TCPIP")):
            return ""
        host, port = parse_socket_resource(text)
        if not host or host.count(".") != 3:
            return ""
        if int(port) != 10001:
            return ""
        return f"TCPIP0::{host}::10001::SOCKET"

    def _visa_managers(self):
        managers = []
        if self.rm is not None:
            managers.append(self.rm)
        try:
            import pyvisa as visa

            py_rm = visa.ResourceManager("@py")
            if all(py_rm is not item for item in managers):
                managers.append(py_rm)
        except Exception as py_exc:
            self.logger.info(f"WT3000 pyvisa-py 不可用: {py_exc}")
        return managers

    def _open_socket_identified(self, resource_string):
        """同一个口先 NI-VISA，资源找不到再试 pyvisa-py。

        口已经打开却超时，说明仪器会话还在，不能换后端再连一次。
        """
        last = None
        for rm in self._visa_managers():
            backend = getattr(rm, "visalib", None)
            backend_name = type(backend).__name__ if backend is not None else "default"
            self.logger.info(f"WT3000尝试连接[{backend_name}]: {resource_string}")
            print(f"WT3000尝试连接[{backend_name}]: {resource_string}")
            try:
                return self._open_identified(rm, resource_string)
            except Exception as exc:
                last = exc
                if _is_rsrc_nfound(exc):
                    continue
                raise
        if last is not None:
            raise last
        raise Exception("WT3000连接失败")

    def _accept_found(self, found, idn_error, resource_string):
        if found is not None:
            return found, resource_string, None, False
        if idn_error:
            return None, "", Exception(idn_error), True
        return None, "", None, False

    def connect(self, tcp_addr):
        """连接 WT3000，并应用串口参数。"""
        last_error = None
        socket_timeout_error = None
        opened_idn_error = None
        handle = None
        used_resource = ""
        legacy_tried = set()
        # 10001 一旦接通就只剩这一个名额。登录没完成时再开 5025 / VXI-11，
        # 仪器屏幕会弹出「忙碌」。拒绝连接（口上没人听）才可以试下一个口。
        session_held = False
        candidates = self._candidate_resources(tcp_addr)
        socket_resources = [
            item for item in candidates if str(item).upper().endswith("::SOCKET")
        ]
        instr_resources = [
            item for item in candidates if "::INSTR" in str(item).upper()
        ]

        for resource_string in socket_resources:
            if self._is_legacy_socket(resource_string):
                try:
                    legacy = self._try_legacy_ethernet(resource_string, legacy_tried)
                except Exception as legacy_exc:
                    last_error = legacy_exc
                    socket_timeout_error = legacy_exc
                    self.logger.info(f"WT3000 connect error {legacy_exc}")
                    print(f"WT3000 connect error {legacy_exc}")
                    handle = None
                    if not _is_connection_refused(legacy_exc):
                        session_held = True
                        break
                    continue
                if legacy is None:
                    continue
                found, idn_error = legacy
                got, used, err, held = self._accept_found(
                    found, idn_error, resource_string
                )
                if got is not None:
                    handle = got
                    used_resource = used
                    break
                if err is not None:
                    opened_idn_error = str(err)
                    last_error = err
                if held:
                    session_held = True
                    break
                handle = None
                continue
            try:
                found, idn_error = self._open_socket_identified(resource_string)
            except Exception as exc:
                last_error = exc
                self.logger.info(f"WT3000 connect error {exc}")
                print(f"WT3000 connect error {exc}")
                handle = None
                if _is_timeout_error(exc):
                    socket_timeout_error = exc
                    session_held = True
                    break
                continue
            got, used, err, held = self._accept_found(
                found, idn_error, resource_string
            )
            if got is not None:
                handle = got
                used_resource = used
                break
            if err is not None:
                opened_idn_error = str(err)
                last_error = err
            if held:
                session_held = True
                break
            handle = None

        if handle is None and not session_held:
            for resource_string in instr_resources:
                try:
                    found, idn_error = self._open_socket_identified(resource_string)
                except Exception as exc:
                    last_error = exc
                    self.logger.info(f"WT3000 connect error {exc}")
                    print(f"WT3000 connect error {exc}")
                    if _is_timeout_error(exc):
                        socket_timeout_error = exc
                        session_held = True
                        break
                    continue
                got, used, err, held = self._accept_found(
                    found, idn_error, resource_string
                )
                if got is not None:
                    handle = got
                    used_resource = used
                    break
                if err is not None:
                    opened_idn_error = str(err)
                    last_error = err
                if held:
                    session_held = True
                    break
        if handle is None:
            try:
                raise choose_wt_connect_error(
                    last_error, socket_timeout_error, opened_idn_error
                )
            except Exception as e:
                self.logger.info(f"WT3000 connect error {e}")
                print(f"WT3000 connect error {e}")
                hint = ""
                if _is_rsrc_nfound(e):
                    hint = (
                        "\n提示：资源未找到。命令口填 5025 或 10001，"
                        "不要填 502/2101/8080。"
                    )
                elif _is_connection_refused(e):
                    hint = (
                        "\n仪器拒绝了这次 TCP。请先退出 WT 上位机"
                        "（网口同时只允许 1 个连接）。命令口是 5025 或 10001。"
                    )
                elif _is_timeout_error(e):
                    hint = (
                        "\n仪器屏幕上的「忙碌」就是这次连接还占着唯一的网口。"
                        "请先关掉 WT 上位机，等忙碌消失后再连，不要连续点。"
                        "10001 会先用 anonymous、空密码登录。"
                    )
                if session_held:
                    time.sleep(0.8)
                self.show_message(f"WT3000连接失败：{e}{hint}", None)
                self.connected = False
                self.handle = None
                self.resource = ""
                return None, "0"
        try:
            handle.write(":NUMERIC:FORMAT ASCII")
        except Exception as e:
            self.logger.info("command :NUMERIC:FORMAT ASCII send failed")
            print(f"command :NUMERIC:FORMAT ASCII send failed: {e}")
        else:
            self.logger.info("WT3000 发送ASCII 命令连接成功")
            print("WT3000 发送ASCII 命令连接成功")
        # 连接时不强制 REMote：多数试验走 WTViewer 宏，由上位机接管远程。
        # 闪变 SCPI 路径在开测序列 / START 前单独发 :COMMunicate:REMote ON。
        self.handle = handle
        self.connected = True
        self.resource = used_resource or tcp_addr
        return self.handle, "1"

    def disconnect(self, safe_close_handle):
        """断开 WT3000 连接。"""
        safe_close_handle(self.handle)
        self.handle = None
        self.connected = False
        self.resource = ''
        self.last_rate_ms = None
        return None, '0'

    def write(self, command):
        if self.handle is None:
            raise RuntimeError("WT SCPI 未连接")
        self.handle.write(command)

    def query(self, command):
        if self.handle is None:
            raise RuntimeError("WT SCPI 未连接")
        return str(self.handle.query(command)).strip()

    def set_rate_ms(self, rate_ms, verify=True):
        """Set instrument data-update rate and optionally verify via ``:RATE?``.

        Returns (ok, actual_ms, warning_or_empty).
        """
        if self.handle is None:
            return False, None, "WT SCPI 未连接"
        target = snap_rate_ms(int(rate_ms))
        warning = ""
        resource = self.resource or getattr(self.handle, "resource_name", "")
        if serial_too_slow_for_rate(resource, target):
            warning = (
                f"串口链路难以稳定达到 {target}ms，建议改用以太网；"
                "否则采样间隔常会卡在约 180–250ms"
            )
            self.logger.info(warning)
            print(warning)
        cmd = rate_command(target)
        try:
            self.handle.write(cmd)
        except Exception as exc:
            msg = f"{cmd} 发送失败: {exc}"
            self.logger.info(msg)
            print(msg)
            return False, None, msg
        if not verify:
            self.last_rate_ms = target
            return True, target, warning
        try:
            reply = self.query(":RATE?")
        except Exception as exc:
            msg = f":RATE? 失败: {exc}"
            self.logger.info(msg)
            print(msg)
            return False, None, msg
        actual = parse_rate_ms(reply)
        self.last_rate_ms = actual
        if not rates_match_ms(target, actual, tol_ms=10):
            msg = f"RATE 回读 {actual}ms != 目标 {target}ms (reply={reply!r})"
            self.logger.info(msg)
            print(msg)
            return False, actual, msg
        info = f"WT RATE OK: {actual}ms (resource={resource}, serial={is_serial_resource(resource)})"
        self.logger.info(info)
        print(info)
        return True, actual, warning


def connect_wt3000(tcp_addr, rm, logger, show_message, baud_rate):
    controller = WT3000Controller(logger, show_message, rm, baud_rate)
    return controller.connect(tcp_addr)


def disconnect_wt3000(handle, safe_close_handle):
    safe_close_handle(handle)
    return None, '0'
