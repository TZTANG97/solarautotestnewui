"""应用运行时上下文。

这个模块用于集中保存主程序运行期间共享的对象和状态，
避免继续把大量全局变量散落在 `SCPITestWave.py` 中。

当前阶段只做“状态集中”，不改变业务逻辑。
后续可以逐步把启动装配、事件绑定、页面状态也迁移到 `app/` 下。
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AppContext:
    """应用运行时上下文。

    说明：
    - 这里保存的是程序启动后会被多个模块共享的对象。
    - 先做集中管理，后续再逐步细化为 state / facade / bootstrap。
    - 不建议在业务逻辑里继续新增散落的全局变量，优先往这里放。
    """

    # 主界面与日志
    ui: Any = None
    logger: Any = None
    rm: Any = None

    # 设备控制器
    ac_controller: Any = None
    dc1_controller: Any = None
    dc2_controller: Any = None
    dc3_controller: Any = None
    dc4_controller: Any = None
    dl850_controller: Any = None
    dewetron_controller: Any = None
    wt3000_controller: Any = None

    # 设置窗口 / 子窗口
    dialog_windowACSetting: Any = None
    dialog_windowDC1Setting: Any = None
    dialog_windowDC2Setting: Any = None
    dialog_windowDC3Setting: Any = None
    dialog_windowDC4Setting: Any = None
    dialog_windowDLSetting: Any = None
    dialog_windowDewetronSetting: Any = None
    uiDewetronSetting: Any = None
    WT3000_setting_window: Any = None
    uiWT3000Setting: Any = None

    # 设备连接与运行状态
    WT3000_baud_rate: str = "9600"
    per_dc_factor: dict = field(default_factory=lambda: {"0": "", "1": "", "2": "", "3": ""})
    command_list_DC: dict = field(default_factory=dict)
    DC_num: dict = field(default_factory=lambda: {"DC1": "0", "DC2": "1", "DC3": "2", "DC4": "3"})
    ArrayfDCCurrValue: list = field(default_factory=list)
    ArrayfDCPowValue: list = field(default_factory=list)
    WT_is_checked: str = ""
    flicker_is_test: str = ""
    heading_handle: Any = None
    connected_equ_resources: set = field(default_factory=set)

    # 兼容旧流程时常用的标记位
    strFlagOfSendDCCommandTestLog: str = ""
    strFlagSendDCCommandInfomation: str = ""
    strConnectDL850: str = "0"
    strConnectDEWETRON: str = "0"
    strConnectWT3000: str = "0"

    def reset_connection_flags(self) -> None:
        """重置连接状态相关标记。

        这个方法只负责恢复状态值，不会主动断开设备。
        适合在全局结束、重连或异常恢复时调用。
        """
        self.strConnectDL850 = "0"
        self.strConnectDEWETRON = "0"
        self.strConnectWT3000 = "0"
        self.strFlagOfSendDCCommandTestLog = ""
        self.strFlagSendDCCommandInfomation = ""
        self.per_dc_factor = {"0": "", "1": "", "2": "", "3": ""}
        self.connected_equ_resources.clear()


# 过渡期兼容：如果某些旧代码还暂时需要直接引用上下文对象，
# 可以先通过这个单例入口拿到统一的运行时状态。
app_context: Optional[AppContext] = None


def get_app_context() -> AppContext:
    """获取全局应用上下文。

    如果上下文尚未创建，则在这里懒初始化。
    这样可以先不改动所有启动路径，逐步迁移。
    """
    global app_context
    if app_context is None:
        app_context = AppContext()
    return app_context
