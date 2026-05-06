import logging
from typing import Any, Optional

from pymodbus.client import ModbusTcpClient

logger = logging.getLogger(__name__)


class ItechTranslator:
    """爱科协议转换器（SCPI转Modbus）"""

    # 爱科寄存器地址映射
    REG_CONTROL = 0x0909      # 开关机控制
    REG_SAVE_PARAM = 0x090B   # 保存参数
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

    def __init__(self, client: ModbusTcpClient):
        self.AC_client = client
        self.edit_mode = "ALL"        # ALL/EACH
        self.phase_mode = "THREE"     # THREE/SINGLE
        self.current_phase = 1        # 1=A, 2=B, 3=C
        self.auto_save = True         # 设置参数后自动保存

    def translate(self, text: str) -> bool:
        """SCPI转爱科Modbus命令"""
        if not self.AC_client:
            logger.error("爱科电源未连接")
            return False

        text = text.strip().upper()

        try:
            # ==================== 系统命令 ====================
            if text == "*RST":
                return self._send_control(self.CMD_RESET, "复位")

            elif text == "*CLS":
                # 清除状态（爱科无直接对应，模拟为刷新状态）
                logger.info("爱科: 清除状态(模拟)")
                return True

            # ==================== 输出控制 ====================
            elif text == "OUTP ON":
                return self._send_control(self.CMD_OUTPUT_ON, "输出吸合")

            elif text == "OUTP OFF":
                return self._send_control(self.CMD_OUTPUT_OFF, "输出断开")

            # ==================== 模式设置 ====================
            elif text == "INST:PHASE THREE":
                self.phase_mode = "THREE"
                logger.info("爱科: 设置三相模式")
                return True

            elif text == "INST:PHASE SINGLE":
                self.phase_mode = "SINGLE"
                self.edit_mode = "EACH"  # 单相模式下强制单相编辑
                logger.info("爱科: 设置单相模式")
                return True

            # ==================== 编辑模式 ====================
            elif text == "INST:EDIT EACH":
                self.edit_mode = "EACH"
                logger.info("爱科: 单相独立编辑模式")
                return True

            elif text == "INST:EDIT ALL":
                if self.phase_mode == "SINGLE":
                    logger.warning("爱科: 单相模式不支持多相同时编辑")
                    return False
                self.edit_mode = "ALL"
                logger.info("爱科: 多相同步编辑模式")
                return True

            # ==================== 相位选择 ====================
            elif text.startswith("INST:NSEL"):
                phase = int(text.split()[-1])
                if phase not in [1, 2, 3]:
                    logger.error(f"爱科: 无效相位 {phase}")
                    return False
                self.current_phase = phase
                # 选择相位时自动切换到单相编辑
                if self.edit_mode == "ALL":
                    self.edit_mode = "EACH"
                    logger.info(f"爱科: 选择相位 {phase}，自动切换单相编辑")
                else:
                    logger.info(f"爱科: 选择相位 {phase}")
                return True

            # ==================== 电压设置 ====================
            elif text.startswith("VOLT"):
                parts = text.split()
                volt_val = float(parts[1])

                # 三相模式 + 多相编辑 = 同时设置三相
                if self.phase_mode == "THREE" and self.edit_mode == "ALL":
                    return self._set_voltage_all(volt_val)
                else:
                    # 单相模式或单相编辑 = 只设置当前相
                    return self._set_voltage_single(self.current_phase, volt_val)

            # ==================== 频率设置 ====================
            elif text.startswith("FREQ"):
                parts = text.split()
                freq_val = float(parts[1])
                return self._set_frequency(freq_val)

            # ==================== 爱科特有扩展命令 ====================
            elif text == "SYST:POWER ON":      # 开机
                return self._send_control(self.CMD_ON, "开机")

            elif text == "SYST:POWER OFF":     # 关机
                return self._send_control(self.CMD_OFF, "关机")

            elif text == "SYST:RUN":           # 运行
                return self._send_control(self.CMD_RUN, "运行")

            elif text == "SYST:STANDBY":       # 待机
                return self._send_control(self.CMD_STANDBY, "待机")

            elif text == "SYST:DISCHARGE":     # 放电
                return self._send_control(self.CMD_DISCHARGE, "放电")

            elif text == "SYST:SAVE":          # 保存参数
                return self._save_parameters()

            else:
                logger.warning(f"未支持的SCPI命令: {text}")
                return False

        except Exception as e:
            logger.error(f"爱科命令转换错误: {e}")
            return False

    # ==================== 内部方法 ====================

    def _send_control(self, cmd_val: int, cmd_name: str) -> bool:
        """发送控制命令"""
        self.AC_client.write_register(self.REG_CONTROL, cmd_val, slave=1)
        logger.info(f"爱科: {cmd_name}")
        return True

    def _set_voltage_all(self, volt_val: float) -> bool:
        """设置三相电压"""
        reg_val = int(volt_val * 100)  # 0.01V精度
        data = [0x0000, reg_val]

        # 同时写入三相
        self.AC_client.write_registers(self.REG_VOLT_A, data, slave=1)
        self.AC_client.write_registers(self.REG_VOLT_B, data, slave=1)
        self.AC_client.write_registers(self.REG_VOLT_C, data, slave=1)

        logger.info(f"爱科: 设置三相电压 {volt_val}V")

        if self.auto_save:
            self._save_parameters()
        return True

    def _set_voltage_single(self, phase: int, volt_val: float) -> bool:
        """设置单相电压"""
        addr_map = {1: self.REG_VOLT_A, 2: self.REG_VOLT_B, 3: self.REG_VOLT_C}
        if phase not in addr_map:
            return False

        reg_val = int(volt_val * 100)
        self.AC_client.write_registers(addr_map[phase], [0x0000, reg_val], slave=1)

        phase_name = ['A', 'B', 'C'][phase - 1]
        logger.info(f"爱科: 设置{phase_name}相电压 {volt_val}V")

        if self.auto_save:
            self._save_parameters()
        return True

    def _set_frequency(self, freq_val: float) -> bool:
        """设置频率"""
        reg_val = int(freq_val * 1000)  # 0.001Hz精度
        self.AC_client.write_registers(self.REG_FREQ, [0x0000, reg_val], slave=1)
        logger.info(f"爱科: 设置频率 {freq_val}Hz")

        if self.auto_save:
            self._save_parameters()
        return True

    def _save_parameters(self) -> bool:
        """保存参数到设备"""
        self.AC_client.write_register(self.REG_SAVE_PARAM, 0x0001, slave=1)
        logger.info("爱科: 参数已保存")
        return True


# ==================== 模块级连接状态 ====================

AC_client: Optional[ModbusTcpClient] = None
HandleEquAC: Any = None
itech_translator: Optional[ItechTranslator] = None

# 可选：主程序在启动时注册，便于无参调用 ConnectEQUAC()
_ui: Any = None
_rm: Any = None


def configure_itech_ac_globals(ui: Any = None, rm: Any = None) -> None:
    """注册 Qt 主界面与 PyVISA ResourceManager，供 ConnectEQUAC() 无参使用。"""
    global _ui, _rm
    if ui is not None:
        _ui = ui
    if rm is not None:
        _rm = rm


def ConnectEQUAC(ui: Any = None, rm: Any = None) -> None:
    """连接设备时初始化转换器。

    :param ui: 含 comboBox_AC 的 Qt 对象；缺省则使用 configure_itech_ac_globals 注册的 _ui
    :param rm: PyVISA ResourceManager；Chroma 路径必填，缺省则使用 configure_itech_ac_globals 注册的 _rm
    """
    global AC_client, itech_translator, HandleEquAC

    ui_obj = ui if ui is not None else _ui
    rm_obj = rm if rm is not None else _rm

    if ui_obj is None:
        logger.error("ConnectEQUAC: 缺少 ui，请传入 ui= 或先调用 configure_itech_ac_globals(ui=..., rm=...)")
        return

    tcp_addr = ui_obj.comboBox_AC.currentText()

    if tcp_addr.startswith("192.168"):
        HandleEquAC = None
        # 爱科Modbus连接
        try:
            ip, port = tcp_addr.split(":")
            AC_client = ModbusTcpClient(host=ip, port=int(port), timeout=5, retries=3)

            if AC_client.connect():
                itech_translator = ItechTranslator(AC_client)
                logger.info(f"爱科电源连接成功: {tcp_addr}")
            else:
                logger.error("爱科电源连接失败")
                AC_client = None
                itech_translator = None
        except Exception as e:
            logger.error(f"连接异常: {e}")
            AC_client = None
            itech_translator = None
    else:
        # Chroma VISA连接
        if rm_obj is None:
            logger.error("ConnectEQUAC: Chroma 路径需要 rm（PyVISA ResourceManager）")
            return
        try:
            AC_client = None
            itech_translator = None
            HandleEquAC = rm_obj.open_resource(tcp_addr)
            logger.info("Chroma交流电源连接成功")
        except Exception as e:
            logger.error(f"Chroma连接失败: {e}")


def translate_to_Itech(text: str) -> bool:
    """统一调用接口"""
    global HandleEquAC

    if itech_translator:
        return itech_translator.translate(text)

    if HandleEquAC is not None:
        try:
            HandleEquAC.write(text)
            return True
        except Exception as e:
            logger.error(f"SCPI发送失败: {e}")
            return False
    logger.error("电源未连接")
    return False
