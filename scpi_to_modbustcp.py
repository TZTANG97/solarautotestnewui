"""SCPI ↔ Modbus 转换：爱科交流（ItechTranslator）、蓝点直流（BluesightTranslator）等。"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from pymodbus.client import ModbusTcpClient

logger = logging.getLogger(__name__)


def _parse_itech_setpoint(text: str, heads: tuple[str, ...]) -> float | None:
    """解析「HEAD <number>」设定值；拒绝 HEAD:XXX 等带冒号的致茂扩展。

    text 须已 strip+upper。成功返回 float，否则 None。
    """
    parts = text.split()
    if len(parts) != 2:
        return None
    head, raw = parts[0], parts[1]
    if head not in heads:
        return None
    # VOLT:OFFS 一类会变成 head=VOLT:OFFS，已被 heads 拦住；双保险
    if ":" in head:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


class ItechTranslator:
    """爱科协议转换器（SCPI转Modbus）"""

    # 爱科寄存器地址映射
    REG_CONTROL = 0x0909      # 开关机控制
    REG_SAVE_PARAM = 0x090B   # 保存参数
    REG_PHASE_MODE = 0x0C48   # 仅两种：独立(含单) / 三相联动（保存前写入）
    REG_VOLT_A = 0x0C00       # A相电压
    REG_VOLT_B = 0x0C02       # B相电压
    REG_VOLT_C = 0x0C04       # C相电压
    REG_FREQ = 0x0C0F         # 频率

    # 控制命令值
    CMD_OFF = 0x0001          # 关机
    CMD_ON = 0x0002           # 开机
    CMD_RUN = 0x0003          # 运行
    CMD_STANDBY = 0x0004      # 待机
    CMD_DISCHARGE = 0x0005    # 放电

    CMD_RESET = 0x0007        # 复位
    CMD_OUTPUT_ON = 0x0008    # 输出吸合
    CMD_OUTPUT_OFF = 0x0009   # 输出断开

    # 查询状态信息
    CMD_QUERY_STATUS = 0x0014  # 查询状态信息

    @staticmethod
    def _format_fc06_pdu(addr: int, value: int, device_id: int = 1) -> str:
        """Modbus TCP 的 PDU（不含 MBAP 头）：功能码 06 + 地址 + 值。"""
        pdu = bytes(
            [0x06, (addr >> 8) & 0xFF, addr & 0xFF, (value >> 8) & 0xFF, value & 0xFF]
        )
        return (
            f"FC06 写单寄存器 addr=0x{addr:04X} value=0x{value:04X} device_id={device_id} | "
            f"PDU(hex)={pdu.hex().upper()}"
        )

    @staticmethod
    def _format_fc10_pdu(addr: int, values: list[int], device_id: int = 1) -> str:
        """Modbus TCP 的 PDU：功能码 10 + 起始地址 + 数量 + 字节数 + 各寄存器大端。"""
        qty = len(values)
        bcnt = qty * 2
        parts = [
            0x10,
            (addr >> 8) & 0xFF,
            addr & 0xFF,
            (qty >> 8) & 0xFF,
            qty & 0xFF,
            bcnt,
        ]
        for v in values:
            parts.extend([(v >> 8) & 0xFF, v & 0xFF])
        pdu = bytes(parts)
        words = ",".join(f"0x{v:04X}" for v in values)
        return (
            f"FC10 写多寄存器 addr=0x{addr:04X} quantity={qty} words=[{words}] device_id={device_id} | "
            f"PDU(hex)={pdu.hex().upper()}"
        )

    def __init__(self, client: ModbusTcpClient):
        self.AC_client = client
        self.edit_mode = "ALL"        # ALL/EACH
        self.phase_mode = "THREE"     # THREE/SINGLE
        self.current_phase = 1        # 1=A, 2=B, 3=C
        self.auto_save = True         # 设置参数后自动保存

    def translate(self, text: str) -> tuple[bool, list[str]]:
        """SCPI 转爱科 Modbus；返回 (是否成功, 本帧组装的 Modbus PDU 描述列表)。"""
        if not self.AC_client:
            logger.error("爱科电源未连接")
            return False, []

        text = text.strip().upper()
        # 界面/致茂路径常用 INST:PHAS，爱科寄存器逻辑按 INST:PHASE 解析（勿用 replace 误伤 INST:PHASE）
        if text.startswith("INST:PHAS "):
            text = "INST:PHASE " + text[10:]
        self._modbus_trace: list[str] = []

        def _out(ok: bool) -> tuple[bool, list[str]]:
            return ok, list(self._modbus_trace)

        try:
            # ==================== 系统命令 ====================
            if text == "*RST":
                return _out(self._send_control(self.CMD_RESET, "复位"))

            elif text == "*CLS":
                # 清除状态（爱科无直接对应，模拟为刷新状态）
                logger.info("爱科: 清除状态(模拟)")
                return _out(True)
            
            elif text == "*STATUS":
                return _out(self._send_control(self.CMD_QUERY_STATUS, "查询状态信息"))
                logger.info("爱科: 查询状态信息")
                return _out(True)

            # ==================== 输出控制 ====================
            elif text == "OUTP ON":
                return _out(self._send_control(self.CMD_OUTPUT_ON, "输出吸合"))

            elif text == "OUTP OFF":
                return _out(self._send_control(self.CMD_OUTPUT_OFF, "输出断开"))

            # ==================== 模式设置 ====================
            elif text == "INST:PHASE THREE":
                self.phase_mode = "THREE"
                logger.info("爱科: 设置三相模式")
                return _out(True)

            elif text == "INST:PHASE SINGLE":
                self.phase_mode = "SINGLE"
                self.edit_mode = "EACH"  # 单相模式下强制单相编辑
                # 刚从三相操作时 current_phase 可能仍为 2/3，后续单条 VOLT 会误写到 B/C 相寄存器
                self.current_phase = 1
                logger.info("爱科: 设置单相模式")
                # 与 INST:EDIT EACH 一致：必须写 0x0C48=独立(含单)，否则设备仍按三相联动逻辑，常见现象为电压不写、频率仍可变
                self._modbus_trace.append(
                    self._format_fc06_pdu(self.REG_PHASE_MODE, 0x0002, device_id=1)
                )
                if self.AC_client.write_register(self.REG_PHASE_MODE, 0x0002, device_id=1) is None:
                    logger.error("爱科: 单相模式写 REG_PHASE_MODE(0x0C48) 失败")
                    return _out(False)
                return _out(True)

            # ==================== 编辑模式 ====================
            elif text == "INST:EDIT EACH":
                self.edit_mode = "EACH"
                logger.info("爱科: 单相独立编辑模式")
                self.AC_client.write_register(self.REG_PHASE_MODE, 0x0002, device_id=1)
                return _out(True)

            elif text == "INST:EDIT ALL":
                if self.phase_mode == "SINGLE":
                    # 单相下 INST:PHASE SINGLE 已写 0x0C48=独立编辑；测试脚本仍发 INST:EDIT ALL（致茂 SCPI 习惯），此处按空操作成功处理
                    logger.info("爱科: 单相模式忽略 INST:EDIT ALL（已由 SINGLE 配置独立编辑）")
                    return _out(True)
                self.edit_mode = "ALL"
                logger.info("爱科: 多相同步编辑模式")
                return _out(True)

            # ==================== 相位选择 ====================
            # 仅接受「INST:NSEL <1|2|3>」，避免 INST:NSELxxx 误匹配
            elif text.startswith("INST:NSEL ") or text == "INST:NSEL":
                parts = text.split()
                if len(parts) != 2:
                    logger.error(f"爱科: INST:NSEL 格式错误: {text}")
                    return _out(False)
                try:
                    phase = int(parts[1])
                except ValueError:
                    logger.error(f"爱科: 无效相位 {parts[1]!r}")
                    return _out(False)
                if phase not in [1, 2, 3]:
                    logger.error(f"爱科: 无效相位 {phase}")
                    return _out(False)
                self.current_phase = phase
                # 选择相位时自动切换到单相编辑
                if self.edit_mode == "ALL":
                    self.edit_mode = "EACH"
                    logger.info(f"爱科: 选择相位 {phase}，自动切换单相编辑")
                else:
                    logger.info(f"爱科: 选择相位 {phase}")
                return _out(True)

            # ==================== 电压设置 ====================
            # 仅接受「VOLT|VOLTAGE <数值>」；拒绝 VOLT:OFFS / VOLT:MODE LIST 等致茂扩展
            elif text.startswith("VOLT ") or text.startswith("VOLTAGE "):
                volt_val = _parse_itech_setpoint(text, ("VOLT", "VOLTAGE"))
                if volt_val is None:
                    logger.warning(f"未支持的SCPI命令: {text}")
                    return _out(False)

                # 三相模式 + 多相编辑 = 同时设置三相
                if self.phase_mode == "THREE" and self.edit_mode == "ALL":
                    print(f"爱科: 设置三相电压 {volt_val}V")
                    return _out(self._set_voltage_all(volt_val))
                else:
                    # 单相模式或单相编辑 = 只设置当前相
                    print(f"爱科: 设置{self.current_phase}相电压 {volt_val}V")
                    return _out(self._set_voltage_single(self.current_phase, volt_val))

            # ==================== 频率设置 ====================
            elif text.startswith("FREQ ") or text.startswith("FREQUENCY "):
                freq_val = _parse_itech_setpoint(text, ("FREQ", "FREQUENCY"))
                if freq_val is None:
                    logger.warning(f"未支持的SCPI命令: {text}")
                    return _out(False)
                return _out(self._set_frequency(freq_val))

            # ==================== 爱科特有扩展命令 ====================
            elif text == "SYST:POWER ON":      # 开机
                return _out(self._send_control(self.CMD_ON, "开机"))

            elif text == "SYST:POWER OFF":     # 关机
                return _out(self._send_control(self.CMD_OFF, "关机"))

            elif text == "SYST:RUN":           # 运行
                return _out(self._send_control(self.CMD_RUN, "运行"))

            elif text == "SYST:STANDBY":       # 待机
                return _out(self._send_control(self.CMD_STANDBY, "待机"))

            elif text == "SYST:DISCHARGE":     # 放电
                return _out(self._send_control(self.CMD_DISCHARGE, "放电"))

            elif text == "SYST:SAVE":          # 保存参数
                return _out(self._save_parameters())

            else:
                logger.warning(f"未支持的SCPI命令: {text}")
                return _out(False)

        except Exception as e:
            logger.error(f"爱科命令转换错误: {e}")
            return _out(False)

    # ==================== 内部方法 ====================

    def _send_control(self, cmd_val: int, cmd_name: str) -> bool:
        """发送控制命令"""
        self._modbus_trace.append(
            self._format_fc06_pdu(self.REG_CONTROL, cmd_val, device_id=1)
        )
        print(
            f"[Itech] _send_control {cmd_name} REG_CONTROL=0x{self.REG_CONTROL:04X} "
            f"cmd_val=0x{cmd_val:04X} client={type(self.AC_client).__name__}"
        )
        ret = self.AC_client.write_register(self.REG_CONTROL, cmd_val, device_id=1)
        print(f"[Itech] _send_control {cmd_name} write_register ret={ret!r}")
        if ret is None:
            logger.error(f"爱科: {cmd_name} Modbus 写入失败")
            return False
        logger.info(f"爱科: {cmd_name}")
        return True

    def _set_voltage_all(self, volt_val: float) -> bool:
        """设置三相电压"""
        reg_val = int(volt_val * 100)  # 0.01V精度
        data = [0x0000, reg_val]

        # 同时写入三相
        for reg_base in (self.REG_VOLT_A, self.REG_VOLT_B, self.REG_VOLT_C):
            self._modbus_trace.append(self._format_fc10_pdu(reg_base, data, device_id=1))
        for reg_base in (self.REG_VOLT_A, self.REG_VOLT_B, self.REG_VOLT_C):
            if self.AC_client.write_registers(reg_base, data, device_id=1) is None:
                logger.error(f"爱科: 设置三相电压失败 reg=0x{reg_base:04X}")
                return False

        logger.info(f"爱科: 设置三相电压 {volt_val}V")

        if self.auto_save:
            return self._save_parameters()
        return True

    def _set_voltage_single(self, phase: int, volt_val: float) -> bool:
        """设置单相电压"""
        addr_map = {1: self.REG_VOLT_A, 2: self.REG_VOLT_B, 3: self.REG_VOLT_C}
        print("addr_map", addr_map)
        print("phase", phase)
        print("res", addr_map[phase])
        if phase not in addr_map:
            return False
        reg_val = int(volt_val * 100)
        regs = [0x0000, reg_val]
        self._modbus_trace.append(
            self._format_fc10_pdu(addr_map[phase], regs, device_id=1)
        )
        if self.AC_client.write_registers(addr_map[phase], regs, device_id=1) is None:
            logger.error(f"爱科: 设置{phase}相电压 Modbus 失败")
            return False

        phase_name = ['A', 'B', 'C'][phase - 1]
        print(f"爱科: 设置{phase_name}相电压 {volt_val}V")

        if self.auto_save:
            return self._save_parameters()
        return True

    def _set_frequency(self, freq_val: float) -> bool:
        """设置频率"""
        reg_val = int(freq_val * 1000)  # 0.001Hz精度
        regs = [0x0000, reg_val]
        self._modbus_trace.append(self._format_fc10_pdu(self.REG_FREQ, regs, device_id=1))
        if self.AC_client.write_registers(self.REG_FREQ, regs, device_id=1) is None:
            logger.error(f"爱科: 设置频率 Modbus 失败")
            return False
        logger.info(f"爱科: 设置频率 {freq_val}Hz")

        if self.auto_save:
            return self._save_parameters()
        return True

    def _save_parameters(self) -> bool:
        """保存参数到设备"""
        self._modbus_trace.append(
            self._format_fc06_pdu(self.REG_SAVE_PARAM, 0x0001, device_id=1)
        )
        ret = self.AC_client.write_register(self.REG_SAVE_PARAM, 0x0001, device_id=1)
        if ret is None:
            logger.error("爱科: 保存参数 Modbus 失败")
            return False
        logger.info("爱科: 参数已保存")
        return True


# =============================================================================
# 蓝点直流 Modbus（STC 曲线块 0x1B61×9 + APPLY，与爱科并列）
# =============================================================================


@dataclass
class BluesightCurveSTC:
    """蓝点「输入参数」界面 STC；由 ``BluesightTranslator.build_curve_words`` 转成 9 个保持寄存器。"""

    pmpp_stc_kw: float = 8.0
    umpp_stc_v: float = 650.0
    irradiance_wm2: float = 1000.0
    temp_c: float = 25.0
    fill_factor: float = 0.8
    custom_mode: int = 0x0002
    flags_word: int = 0x0001

    def validate(self) -> None:
        if not (0.25 <= self.fill_factor <= 0.95):
            raise ValueError(f"填充因子须在 0.25~0.95，当前 {self.fill_factor}")
        # Pmpp/Umpp 按 uint32 LE 写入（与 translate Vmp/Pmp 一致），勿按单字 65535 截断
        p_raw = int(round(self.pmpp_stc_kw * 1000.0))
        u_raw = int(round(self.umpp_stc_v * 100.0))
        if p_raw < 0 or p_raw > 0xFFFFFFFF:
            raise ValueError(f"Pmpp(kW)×1000 越界: {p_raw}")
        if u_raw < 0 or u_raw > 0xFFFFFFFF:
            raise ValueError(f"Umpp(V)×100 越界: {u_raw}")


class BluesightTranslator:
    """蓝点：STC 曲线块 + 离散寄存器（OUTP/Vmp/Pmp/FF/APPLY）。client 需支持 pymodbus 风格 ``write_register``/``write_registers``。"""

    REG_CURVE_BLOCK_START = 0x1B61
    REG_CURVE_BLOCK_COUNT = 9
    REG_APPLY = 0x1B75
    VAL_APPLY = 0x0055

    REG_OUTP = 0x0BB8
    OUTP_ON = 0x00AA
    OUTP_OFF = 0x0055

    # 输出工作模式：FC06 写保持寄存器 0x0F95（手册：0=原载，1=SAS，2=电池模拟器）
    REG_OUTPUT_MODE = 0x0F95
    MODE_ORIGINAL_LOAD = 0x0000
    MODE_SAS = 0x0001
    MODE_BATTERY_SIMULATOR = 0x0002

    # 原载参数：CV 先 FC06 再 FC16 0x0FAA×4；CC 先 FC16 0x0FAE×2 再 FC06；CP 先 FC06 再 FC16 0x0FB0×2；CR 先 FC16 0x0FB2×2 再 FC06
    REG_ORIG_SUBMODE = 0x0FA9
    REG_ORIG_PARAM_BLOCK_START = 0x0FAA
    REG_ORIG_PARAM_BLOCK_COUNT = 4
    REG_ORIG_CC_PARAM_START = 0x0FAE
    REG_ORIG_CC_PARAM_COUNT = 2
    REG_ORIG_CP_PARAM_START = 0x0FB0
    REG_ORIG_CR_PARAM_START = 0x0FB2
    # 恒功率输出功率上限（kW），与界面一致
    ORIG_CP_MAX_KW = 30.0
    ORIG_LOAD_FUNC_CV = 0x0000
    ORIG_LOAD_FUNC_CC = 0x0001
    ORIG_LOAD_FUNC_CP = 0x0002
    ORIG_LOAD_FUNC_CR = 0x0003

    # *IDN?：抓包校验 FC04 读输入寄存器 — 订货型号 / 固件信息串（蓝点与上位机一致）
    REG_IDN_MODEL = 0x09D3
    REG_IDN_MODEL_COUNT = 8
    # 个别版本型号串在输入寄存器另一起始地址（与抓包 0x104C 一致时可读到）
    REG_IDN_MODEL_ALT = 0x104C
    REG_FW_STRING_BLOCK = 0x0A15
    REG_FW_STRING_COUNT = 0x4B  # 75

    def __init__(self, client: Any, *, device_id: int = 1):
        self.client = client
        self._device_id = device_id
        self.command_map = {
            "OUTP ON": (0x0BB8, False, 0x00AA),
            "OUTP OFF": (0x0BB8, False, 0x0055),
            "Vmp": (0x1B64, True, 0),
            "Pmp": (0x1B62, True, 0),
            "FF": (0x1B69, False, 800),
            "APPLY": (0x1B75, False, 0x0055),
        }

    def _write_register(self, address: int, value: int) -> Any:
        try:
            return self.client.write_register(address, value, device_id=self._device_id)
        except TypeError:
            return self.client.write_register(address, value, slave=self._device_id)

    def _write_registers(self, address: int, values: list[int]) -> Any:
        try:
            return self.client.write_registers(address, values, device_id=self._device_id)
        except TypeError:
            return self.client.write_registers(address, values, slave=self._device_id)

    @staticmethod
    def _u32_le_words(raw: int) -> list[int]:
        """uint32 → Modbus 低字在前、高字在后（与 ``translate`` 中 Vmp/Pmp 一致）。"""
        if raw < 0 or raw > 0xFFFFFFFF:
            raise ValueError(f"uint32 越界: {raw}")
        return [raw & 0xFFFF, (raw >> 16) & 0xFFFF]

    @staticmethod
    def _scaled_u32(value: float, scale: float, label: str) -> int:
        raw = int(round(float(value) * scale))
        if raw < 0 or raw > 0xFFFFFFFF:
            raise ValueError(f"{label} 编码越界: value={value} scale={scale} raw={raw}")
        return raw

    @staticmethod
    def _regs_high_low_ascii(regs: list[int]) -> bytes:
        return b"".join(bytes([(w >> 8) & 0xFF, w & 0xFF]) for w in regs)

    @staticmethod
    def _ascii_ztrim(blob: bytes) -> str:
        return blob.decode("latin-1", errors="replace").split("\x00")[0].strip()

    @staticmethod
    def _fc0304_tcp_response_to_registers(resp: bytes) -> list[int] | None:
        """解析 Modbus TCP 应答为寄存器列表（FC03/FC04 读寄存器正常应答，PDU 结构相同）。"""
        if resp is None or len(resp) < 9:
            return None
        pdu_fc = resp[7]
        if pdu_fc & 0x80:
            return None
        if pdu_fc not in (0x03, 0x04):
            return None
        bc = resp[8]
        data = resp[9 : 9 + bc]
        out: list[int] = []
        for i in range(0, len(data) - 1, 2):
            out.append((data[i] << 8) | data[i + 1])
        return out

    def _read_input_registers(self, address: int, count: int) -> list[int] | None:
        """FC04；兼容 pymodbus ``read_input_registers`` 与 ``ModbusVISA.read_input_register``（返回整帧 bytes）。"""
        c = self.client
        if hasattr(c, "read_input_registers"):
            rr = None
            try:
                rr = c.read_input_registers(address, count=count, device_id=self._device_id)
            except TypeError:
                try:
                    rr = c.read_input_registers(address, count=count, slave=self._device_id)
                except TypeError:
                    rr = c.read_input_registers(address, count)
            if rr is None or getattr(rr, "isError", lambda: False)():
                return None
            regs = getattr(rr, "registers", None)
            if not regs:
                return None
            return list(regs)
        ri = getattr(c, "read_input_register", None)
        if callable(ri):
            raw = ri(address, quantity=count, unit=self._device_id)
            if raw is None:
                return None
            if isinstance(raw, (bytes, bytearray)):
                return self._fc0304_tcp_response_to_registers(bytes(raw))
        return None

    def _read_holding_registers(self, address: int, count: int) -> list[int] | None:
        """FC03；兼容 pymodbus ``read_holding_registers`` 与 ``ModbusVISA.read_holding_register``。"""
        c = self.client
        if hasattr(c, "read_holding_registers"):
            rr = None
            try:
                rr = c.read_holding_registers(address, count=count, device_id=self._device_id)
            except TypeError:
                try:
                    rr = c.read_holding_registers(address, count=count, slave=self._device_id)
                except TypeError:
                    rr = c.read_holding_registers(address, count)
            if rr is None or getattr(rr, "isError", lambda: False)():
                return None
            regs = getattr(rr, "registers", None)
            if not regs:
                return None
            return list(regs)
        rh = getattr(c, "read_holding_register", None)
        if callable(rh):
            raw = rh(address, quantity=count, unit=self._device_id)
            if raw is None:
                return None
            if isinstance(raw, (bytes, bytearray)):
                return self._fc0304_tcp_response_to_registers(bytes(raw))
        return None

    def _translate_idn(self) -> tuple[bool, str]:
        """*IDN? → 型号字符串 + 可选固件版本串（与 SCPI query 返回一行识别信息对齐）。"""
        # 部分机台型号在保持寄存器或备用地址；依次尝试 FC04 / FC03 / 备用地址 FC04
        regs = self._read_input_registers(self.REG_IDN_MODEL, self.REG_IDN_MODEL_COUNT)
        tried = f"FC04 0x{self.REG_IDN_MODEL:04X}×{self.REG_IDN_MODEL_COUNT}"
        if not regs:
            regs = self._read_holding_registers(self.REG_IDN_MODEL, self.REG_IDN_MODEL_COUNT)
            tried += f" | FC03 0x{self.REG_IDN_MODEL:04X}×{self.REG_IDN_MODEL_COUNT}"
        if not regs:
            regs = self._read_input_registers(self.REG_IDN_MODEL_ALT, self.REG_IDN_MODEL_COUNT)
            tried += f" | FC04 0x{self.REG_IDN_MODEL_ALT:04X}×{self.REG_IDN_MODEL_COUNT}"
        if not regs:
            err = f"*IDN?: 读型号失败（已试 {tried}），请确认 IP/端口、站号=1 及手册寄存器区"
            logger.warning(f"蓝点 {err}")
            return False, err

        model = self._ascii_ztrim(self._regs_high_low_ascii(regs))

        fw_tail = ""
        fw_regs = self._read_input_registers(self.REG_FW_STRING_BLOCK, self.REG_FW_STRING_COUNT)
        if fw_regs:
            blob = self._regs_high_low_ascii(fw_regs)
            chunks = [self._ascii_ztrim(x) for x in blob.split(b"\x00")]
            pieces = [x for x in chunks if len(x) >= 6]
            if pieces:
                joined = "; ".join(pieces[:8])
                if len(joined) > 400:
                    joined = joined[:397] + "..."
                fw_tail = joined

        if model and fw_tail:
            line = f"{model}, {fw_tail}"
        elif model:
            line = model
        elif fw_tail:
            line = fw_tail
        else:
            return False, "*IDN?: 应答中无有效 ASCII 型号/版本"

        logger.info("蓝点 *IDN? -> %s", line[:120] + ("..." if len(line) > 120 else ""))
        return True, line

    def _translate_output_mode(self, text: str) -> tuple[bool, str]:
        """SYST:MODE → 先 FC06 写 ``REG_OUTPUT_MODE``（0x0F95），再写 ``REG_APPLY`` 触发生效（与曲线参数一致）。"""
        s = text.strip()
        key = "SYST:MODE"
        if len(s) < len(key) or s[: len(key)].upper() != key:
            return False, "内部错误: 非 SYST:MODE"
        # 允许 SYST:MODE:1 / SYST:MODE :2（MODE 后多一个冒号时不再得到 ':1'）
        tail = s[len(key) :].strip().lstrip(":").strip()
        if not tail:
            return (
                False,
                "SYST:MODE 须带模式：0=原载，1=SAS，2=电池模拟器（例 SYST:MODE 0 / SAS / 电池模拟器）",
            )

        tu = tail.upper()
        if tail in ("0", "原载") or tu in ("ORIG", "LOAD", "ORIGINAL"):
            mode_val = self.MODE_ORIGINAL_LOAD
            if tail == "0":
                label = "原载(0)"
            elif tail == "原载":
                label = "原载"
            else:
                label = f"原载({tu})"
        elif tail in ("1",) or tu == "SAS":
            mode_val = self.MODE_SAS
            label = "SAS(1)" if tail == "1" else "SAS"
        elif tail in ("2",) or tail == "电池模拟器" or tu in ("BAT", "BATTERY", "BATTSIM", "BATTERY_SIM"):
            mode_val = self.MODE_BATTERY_SIMULATOR
            if tail == "2":
                label = "电池模拟器(2)"
            elif tail == "电池模拟器":
                label = "电池模拟器"
            else:
                label = f"电池模拟器({tu})"
        else:
            return (
                False,
                f"未知 SYST:MODE 参数: {tail!r}；有效：0/原载/ORIG，1/SAS，2/电池模拟器/BAT",
            )

        res = self._write_register(self.REG_OUTPUT_MODE, mode_val)
        if getattr(res, "isError", lambda: False)():
            return False, f"SYST:MODE 写入 0x{self.REG_OUTPUT_MODE:04X}={mode_val} 失败: {res}"

        r_apply = self._write_register(self.REG_APPLY, self.VAL_APPLY)
        if getattr(r_apply, "isError", lambda: False)():
            return (
                False,
                f"SYST:MODE 已写入 0x{self.REG_OUTPUT_MODE:04X}，但 APPLY 0x{self.REG_APPLY:04X} 失败: {r_apply}",
            )

        logger.info(
            "蓝点 SYST:MODE %s -> 0x%04X=0x%04X + APPLY 0x%04X",
            label,
            self.REG_OUTPUT_MODE,
            mode_val,
            self.REG_APPLY,
        )
        return (
            True,
            f"成功: SYST:MODE {label} -> 0x{self.REG_OUTPUT_MODE:04X}=0x{mode_val:04X}, APPLY 0x{self.REG_APPLY:04X}=0x{self.VAL_APPLY:04X}",
        )

    @staticmethod
    def build_curve_words(stc: BluesightCurveSTC) -> list[int]:
        """0x1B61 起连续 9 字；Pmpp/Umpp 为 uint32 LE（低字在前），与 ``Vmp``/``Pmp`` 一致。"""
        stc.validate()
        w0 = stc.custom_mode & 0xFFFF
        p_lo, p_hi = BluesightTranslator._u32_le_words(
            BluesightTranslator._scaled_u32(stc.pmpp_stc_kw, 1000.0, "Pmpp(kW)×1000")
        )
        u_lo, u_hi = BluesightTranslator._u32_le_words(
            BluesightTranslator._scaled_u32(stc.umpp_stc_v, 100.0, "Umpp(V)×100")
        )
        w5 = int(round(stc.irradiance_wm2 * 10.0)) & 0xFFFF
        w6 = int(round(stc.temp_c * 10.0)) & 0xFFFF
        w7 = stc.flags_word & 0xFFFF
        w8 = int(round(stc.fill_factor * 1000.0)) & 0xFFFF
        return [w0, p_lo, p_hi, u_lo, u_hi, w5, w6, w7, w8]

    def write_curve_block(
        self,
        words: list[int] | None = None,
        *,
        stc: BluesightCurveSTC | None = None,
        auto_apply: bool = True,
    ) -> tuple[bool, str]:
        if words is None:
            if stc is None:
                raise ValueError("须传入 stc=BluesightCurveSTC(...) 或 words=[9个uint16]")
            try:
                words = self.build_curve_words(stc)
            except ValueError as exc:
                return False, f"曲线参数编码失败: {exc}"
        if len(words) != self.REG_CURVE_BLOCK_COUNT:
            return False, f"曲线块须 {self.REG_CURVE_BLOCK_COUNT} 字，当前 {len(words)}"
        for w in words:
            if w < 0 or w > 0xFFFF:
                return False, f"单字越界: {w}"

        res = self._write_registers(self.REG_CURVE_BLOCK_START, words)
        if getattr(res, "isError", lambda: False)():
            return False, f"FC16 曲线块失败: {res}"

        if not auto_apply:
            return True, "FC16 曲线块已写，未执行 APPLY"

        r2 = self._write_register(self.REG_APPLY, self.VAL_APPLY)
        if getattr(r2, "isError", lambda: False)():
            return False, f"曲线块已写但 APPLY 失败: {r2}"
        return True, "FC16 曲线块 + APPLY 成功"

    def build_original_load_param_words(
        self,
        func_index: int,
        *,
        voltage_v: float | None = None,
        r_internal_ohm: float | None = None,
        current_a: float | None = None,
        power_kw: float | None = None,
        r_load_ohm: float | None = None,
    ) -> list[int]:
        """原载保持寄存器内容（量纲×系数后按 **uint32 低字在前** 拆成字，与 Vmp/Pmp 一致）。

        恒压：4 字 ``0x0FAA``：``[U×100_lo, U×100_hi, R内×100_lo, R内×100_hi]``
        （例：860V → ``0x4FF0, 0x0001``；低电压时高字为 0，与旧抓包 ``[U×100, 0, …]`` 兼容）。
        恒流：2 字 ``0x0FAE``：``[I×100_lo, I×100_hi]``（20A → ``0x07D0, 0x0000``）。
        恒功率：2 字 ``0x0FB0``：``[P_kW×1000_lo, hi]``（上限 ``ORIG_CP_MAX_KW``）。
        恒阻：2 字 ``0x0FB2``：``[R负载×100_lo, hi]``（2Ω → ``0x00C8, 0x0000``）。
        """
        if func_index == 0:
            v_lo, v_hi = self._u32_le_words(
                self._scaled_u32(float(voltage_v or 0.0), 100.0, "恒压电压(V)×100")
            )
            r_lo, r_hi = self._u32_le_words(
                self._scaled_u32(float(r_internal_ohm or 0.0), 100.0, "恒压内阻(Ω)×100")
            )
            return [v_lo, v_hi, r_lo, r_hi]
        if func_index == 1:
            return self._u32_le_words(
                self._scaled_u32(float(current_a or 0.0), 100.0, "恒流电流(A)×100")
            )
        if func_index == 2:
            pk = min(max(0.0, float(power_kw or 0.0)), self.ORIG_CP_MAX_KW)
            return self._u32_le_words(
                self._scaled_u32(pk, 1000.0, "恒功率(kW)×1000")
            )
        if func_index == 3:
            return self._u32_le_words(
                self._scaled_u32(float(r_load_ohm or 0.0), 100.0, "恒阻(Ω)×100")
            )
        return [0, 0, 0, 0]

    def write_original_load_params(
        self,
        func_index: int,
        *,
        voltage_v: float | None = None,
        r_internal_ohm: float | None = None,
        current_a: float | None = None,
        power_kw: float | None = None,
        r_load_ohm: float | None = None,
    ) -> tuple[bool, str]:
        """原载下发（与上位机抓包一致）；无额外 APPLY。
        恒压：FC06 ``0x0FA9`` 再 FC16 ``0x0FAA``×4。
        恒流：FC16 ``0x0FAE``×2 再 FC06。
        恒功率：FC06 ``0x0FA9`` 再 FC16 ``0x0FB0``×2。
        恒阻：FC16 ``0x0FB2``×2 再 FC06。
        """
        if func_index < 0 or func_index > 3:
            return False, f"原载输出模式须在 0~3（恒压/恒流/恒功率/恒阻），当前 {func_index}"
        names = ("CV/恒压", "CC/恒流", "CP/恒功率", "CR/恒阻")
        label = names[func_index]
        try:
            words = self.build_original_load_param_words(
                func_index,
                voltage_v=voltage_v,
                r_internal_ohm=r_internal_ohm,
                current_a=current_a,
                power_kw=power_kw,
                r_load_ohm=r_load_ohm,
            )
        except ValueError as exc:
            return False, f"原载 {label} 参数编码失败: {exc}"
        sub = func_index & 0xFFFF

        def _fc06_then_fc16(addr: int, wds: list[int], addr_label: str) -> tuple[bool, str]:
            r_a = self._write_register(self.REG_ORIG_SUBMODE, sub)
            if getattr(r_a, "isError", lambda: False)():
                return False, f"FC06 原载子模式 0x{self.REG_ORIG_SUBMODE:04X}={sub} 失败: {r_a}"
            r_b = self._write_registers(addr, wds)
            if getattr(r_b, "isError", lambda: False)():
                return False, f"FC16 {addr_label} 0x{addr:04X}×{len(wds)} 失败: {r_b}"
            logger.info(
                "蓝点 原载 %s -> FC06 0x%04X=0x%04X then FC16 0x%04X words=%s",
                label,
                self.REG_ORIG_SUBMODE,
                sub,
                addr,
                [f"0x{w:04X}" for w in wds],
            )
            return (
                True,
                f"成功: 原载 {label} FC06 0x{self.REG_ORIG_SUBMODE:04X}=0x{sub:04X} "
                f"FC16 0x{addr:04X}=[{','.join(f'0x{w:04X}' for w in wds)}]",
            )

        def _fc16_then_fc06(addr: int, wds: list[int], addr_label: str) -> tuple[bool, str]:
            r_a = self._write_registers(addr, wds)
            if getattr(r_a, "isError", lambda: False)():
                return False, f"FC16 {addr_label} 0x{addr:04X}×{len(wds)} 失败: {r_a}"
            r_b = self._write_register(self.REG_ORIG_SUBMODE, sub)
            if getattr(r_b, "isError", lambda: False)():
                return False, f"FC06 原载子模式 0x{self.REG_ORIG_SUBMODE:04X}={sub} 失败: {r_b}"
            logger.info(
                "蓝点 原载 %s -> FC16 0x%04X words=%s then FC06 0x%04X=0x%04X",
                label,
                addr,
                [f"0x{w:04X}" for w in wds],
                self.REG_ORIG_SUBMODE,
                sub,
            )
            return (
                True,
                f"成功: 原载 {label} FC16 0x{addr:04X}="
                f"[{','.join(f'0x{w:04X}' for w in wds)}] "
                f"FC06 0x{self.REG_ORIG_SUBMODE:04X}=0x{sub:04X}",
            )

        if func_index == 0:
            if len(words) != self.REG_ORIG_PARAM_BLOCK_COUNT:
                return False, f"恒压参数须 {self.REG_ORIG_PARAM_BLOCK_COUNT} 字"
            return _fc06_then_fc16(self.REG_ORIG_PARAM_BLOCK_START, words, "恒压")

        if func_index == 1:
            if len(words) != self.REG_ORIG_CC_PARAM_COUNT:
                return False, f"恒流参数须 {self.REG_ORIG_CC_PARAM_COUNT} 字"
            return _fc16_then_fc06(self.REG_ORIG_CC_PARAM_START, words, "恒流")

        if func_index == 2:
            if len(words) != self.REG_ORIG_CC_PARAM_COUNT:
                return False, f"恒功率参数须 {self.REG_ORIG_CC_PARAM_COUNT} 字"
            return _fc06_then_fc16(self.REG_ORIG_CP_PARAM_START, words, "恒功率")

        if func_index == 3:
            if len(words) != self.REG_ORIG_CC_PARAM_COUNT:
                return False, f"恒阻参数须 {self.REG_ORIG_CC_PARAM_COUNT} 字"
            return _fc16_then_fc06(self.REG_ORIG_CR_PARAM_START, words, "恒阻")

        return False, f"未知原载模式: {func_index}"

    def write_original_load_output_func(self, func_index: int) -> tuple[bool, str]:
        """兼容：仅写子模式 + 全零参数块（无 UI 数值时使用）。"""
        return self.write_original_load_params(
            func_index,
            voltage_v=0.0,
            r_internal_ohm=0.0,
            current_a=0.0,
            power_kw=0.0,
            r_load_ohm=0.0,
        )

    def translate(self, text: str, value: Any = None) -> tuple[bool, str]:
        t = text.strip()
        u = t.upper()

        if u in ("*CLS", "*RST"):
            return True, f"noop: {t}（无 Modbus 映射，跳过）"

        if u == "*IDN?":
            return self._translate_idn()

        if len(t) >= len("SYST:MODE") and t[: len("SYST:MODE")].upper() == "SYST:MODE":
            return self._translate_output_mode(t)

        if t not in self.command_map:
            return False, f"未知指令: {text!r}；曲线下发请用 write_curve_block()"

        addr, is_32bit, default_val = self.command_map[t]

        if value is None:
            val_int = int(default_val)
        elif t == "FF":
            if isinstance(value, float) and 0 < value <= 1:
                val_int = int(round(value * 1000.0))
            else:
                val_int = int(value)
        elif t == "Pmp":
            val_int = int(float(value) * 1000)
        elif t == "Vmp":
            val_int = int(round(float(value) * 100))
        else:
            val_int = int(value)

        if is_32bit:
            registers = [val_int & 0xFFFF, (val_int >> 16) & 0xFFFF]
            res = self._write_registers(addr, registers)
        else:
            if val_int < 0 or val_int > 0xFFFF:
                return False, f"单寄存器值越界: {val_int}"
            res = self._write_register(addr, val_int & 0xFFFF)

        if getattr(res, "isError", lambda: False)():
            return False, f"写入失败: {res}"

        if t in ("Vmp", "Pmp", "FF"):
            r_apply = self._write_register(self.REG_APPLY, self.VAL_APPLY)
            if getattr(r_apply, "isError", lambda: False)():
                return False, f"参数已写但 APPLY 失败: {r_apply}"

        return True, f"成功: {t} -> raw={val_int}"
