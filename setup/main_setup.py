"""主程序试验设定装配模块。

这个模块负责把 `SCPITestWave.py` 中与“试验设定初始化”相关的
窗口创建、上下文同步、默认状态整理等逻辑集中起来。

注意：
- 这里只做模块化抽象，不改变原有业务逻辑。
- 代码仍然按照主程序原有顺序初始化，便于平滑迁移。
"""

from typing import Any, Dict

from PyQt5.QtWidgets import QDialog, QWidget

from setup.base_setup import BaseSetup

from Dialog_AC_Setting import Ui_Dialog_AC_Setting
from Dialog_DC1_Setting import Ui_Dialog_DC1_Setting
from Dialog_DC2_Setting import Ui_Dialog_DC2_Setting
from Dialog_DC3_Setting import Ui_Dialog_DC3_Setting
from Dialog_DC4_Setting import Ui_Dialog_DC4_Setting
from Dialog_DL850_Setting import Ui_Dialog_DL850_Setting
from Dialog_DEWETRON_Setting import Ui_Dialog_DEWETRON_Setting
from Dialog_thaichonglian import Ui_Dialog_thaichonglian
from Dialog_thaiguodianyashanbian import Ui_Dialog_thaiguodianyashanbian
from Dialog_thaixiebodianliu import Ui_Dialog_thaixiebodianliu
from Dialog_thaizhiliufenliang import Ui_Dialog_thaizhiliufenliang
from Dialog_thaivoltprotect10min import Ui_Dialog_thaivoltprotect10min
from Dialog_thaiguopinjiangzai import Ui_Dialog_thaiguopinjiangzai
from Dialog_thaitestPU import Ui_Dialog_thaitestPU
from Dialog_thaiguoqianya_pin import Ui_Dialog_thaiguoqianya_pin
from Dialog_thaifixedPF import Ui_Dialog_thaifixedPF
from Dialog_thaioverloads import Ui_Dialog_thaioverloads
from Dialog_thaicosPhi_Brazil import Ui_Dialog_thaicosPhi_Brazil
from Dialog_thaiguoqianpin_immun import Ui_Dialog_thaiguoqianpin_immun
from Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU
from Dialog_thaistaticcosPhi import Ui_Dialog_thaistaticcosPhi
from Dialog_thaistaticmppttest import Ui_Dialog_thaistaticmppttest
from Dialog_thaifrequencyadaptability import Ui_Dialog_thaifrequencyadaptability
from Dialog_thaiWT3000E import Ui_Dialog_thai_WT3000E
from Dialog_thaiWT1806E import Ui_Dialog_thai_WT1806E
from Dialog_thaiWT1800 import Ui_Dialog_thai_WT1800
from Dialog_thaiWT5000 import Ui_Dialog_thai_WT5000


class MainSetup(BaseSetup):
    """主程序试验设定装配实现。"""

    def initialize(self, app_ctx: Any) -> Dict[str, Any]:
        return self.initialize_windows(app_ctx)

    @staticmethod
    def _build_dialog(ui_cls: Any, container=None) -> tuple:
        if container is None:
            container = QDialog()
        ui = ui_cls()
        ui.setupUi(container)
        return container, ui

    @staticmethod
    def embed_dialog_content(dialog, page_widget, settings_attr_name):
        """将 dialog 的内容嵌入到 page_widget 的 _settings_{name} 占位区域。"""
        settings_area = getattr(page_widget, f"_settings_{settings_attr_name}", None)
        if settings_area is None:
            return
        target_layout = settings_area.layout()

        dlg_layout = dialog.layout()
        if dlg_layout is not None:
            # 布局型对话框（如 DEWETRON）：提取布局中的所有控件
            while dlg_layout.count():
                item = dlg_layout.takeAt(0)
                w = item.widget()
                if w is not None:
                    target_layout.addWidget(w)
        else:
            # 绝对定位型对话框（pyuic5 生成）：重新设置父控件
            for child in list(dialog.findChildren(QWidget)):
                if child.parent() is dialog:
                    child.setParent(settings_area)
                    target_layout.addWidget(child)

    @staticmethod
    def _register_window(created: Dict[str, Any], app_ctx: Any, dialog_key: str, ui_key: str, dialog: QDialog, ui: Any, sync_dialog_attr: str | None = None, sync_ui_attr: str | None = None) -> None:
        """统一登记窗口对象。

        这里只做“登记 + 可选同步到上下文”，不改变原有业务逻辑。
        """
        created[dialog_key] = dialog
        created[ui_key] = ui
        if sync_dialog_attr is not None:
            setattr(app_ctx, sync_dialog_attr, dialog)
        if sync_ui_attr is not None:
            setattr(app_ctx, sync_ui_attr, ui)

    @staticmethod
    def initialize_windows(app_ctx: Any) -> Dict[str, Any]:
        """创建主程序的试验设定窗口，并同步到应用上下文。"""
        # 这里只负责“创建并登记窗口对象”，不改变任何试验业务逻辑。
        created: Dict[str, Any] = {}

        dialog_WT3000E, uiThiaWT3000E = MainSetup._build_dialog(Ui_Dialog_thai_WT3000E)
        MainSetup._register_window(created, app_ctx, "dialog_WT3000E", "uiThiaWT3000E", dialog_WT3000E, uiThiaWT3000E, sync_dialog_attr="WT3000_setting_window")

        dialog_WT1806E, uiThiaWT1806E = MainSetup._build_dialog(Ui_Dialog_thai_WT1806E)
        MainSetup._register_window(created, app_ctx, "dialog_WT1806E", "uiThiaWT1806E", dialog_WT1806E, uiThiaWT1806E)

        # 旧主程序中 WT3000 的“波特率设置”窗口仍由主流程保留，这里只集中试验设定窗口。
        dialog_WT1800, uiThiaWT1800 = MainSetup._build_dialog(Ui_Dialog_thai_WT1800)
        MainSetup._register_window(created, app_ctx, "dialog_WT1800", "uiThiaWT1800", dialog_WT1800, uiThiaWT1800)

        dialog_WT5000, uiThiaWT5000 = MainSetup._build_dialog(Ui_Dialog_thai_WT5000)
        MainSetup._register_window(created, app_ctx, "dialog_WT5000", "uiThiaWT5000", dialog_WT5000, uiThiaWT5000)

        dialog_window, uithaichonglian = MainSetup._build_dialog(Ui_Dialog_thaichonglian)
        MainSetup._register_window(created, app_ctx, "dialog_window", "uithaichonglian", dialog_window, uithaichonglian)

        dialog_windowxiebodianliu, uiThaiXieBoDianLiu = MainSetup._build_dialog(Ui_Dialog_thaixiebodianliu)
        MainSetup._register_window(created, app_ctx, "dialog_windowxiebodianliu", "uiThaiXieBoDianLiu", dialog_windowxiebodianliu, uiThaiXieBoDianLiu)

        dialog_windowzhiliufenliang, uiThaiZhiLiuFenLiang = MainSetup._build_dialog(Ui_Dialog_thaizhiliufenliang)
        MainSetup._register_window(created, app_ctx, "dialog_windowzhiliufenliang", "uiThaiZhiLiuFenLiang", dialog_windowzhiliufenliang, uiThaiZhiLiuFenLiang)

        dialog_windowstaticQU, uiThaiStaticQU = MainSetup._build_dialog(Ui_Dialog_thaiStaticQU)
        MainSetup._register_window(created, app_ctx, "dialog_windowstaticQU", "uiThaiStaticQU", dialog_windowstaticQU, uiThaiStaticQU)

        dialog_windowstaticcosPhi, uiThaiStaticCosPhi = MainSetup._build_dialog(Ui_Dialog_thaistaticcosPhi)
        MainSetup._register_window(created, app_ctx, "dialog_windowstaticcosPhi", "uiThaiStaticCosPhi", dialog_windowstaticcosPhi, uiThaiStaticCosPhi)

        dialog_windowvoltprotect10min, uiThaiVoltProtect10min = MainSetup._build_dialog(Ui_Dialog_thaivoltprotect10min)
        MainSetup._register_window(created, app_ctx, "dialog_windowvoltprotect10min", "uiThaiVoltProtect10min", dialog_windowvoltprotect10min, uiThaiVoltProtect10min)

        dialog_windowguopinjiangzai, uiThaiGuoPinJiangZai = MainSetup._build_dialog(Ui_Dialog_thaiguopinjiangzai)
        MainSetup._register_window(created, app_ctx, "dialog_windowguopinjiangzai", "uiThaiGuoPinJiangZai", dialog_windowguopinjiangzai, uiThaiGuoPinJiangZai)

        dialog_windowtestPU, uiThaiTestPU = MainSetup._build_dialog(Ui_Dialog_thaitestPU)
        MainSetup._register_window(created, app_ctx, "dialog_windowtestPU", "uiThaiTestPU", dialog_windowtestPU, uiThaiTestPU)

        dialog_windowguoqianya_pin, uiThaiGuoQianYa_Pin = MainSetup._build_dialog(Ui_Dialog_thaiguoqianya_pin)
        MainSetup._register_window(created, app_ctx, "dialog_windowguoqianya_pin", "uiThaiGuoQianYa_Pin", dialog_windowguoqianya_pin, uiThaiGuoQianYa_Pin)

        dialog_windowDLSetting, uiDL850Setting = MainSetup._build_dialog(Ui_Dialog_DL850_Setting)
        MainSetup._register_window(created, app_ctx, "dialog_windowDLSetting", "uiDL850Setting", dialog_windowDLSetting, uiDL850Setting, sync_dialog_attr="dialog_windowDLSetting")

        dialog_windowDewetronSetting, uiDewetronSetting = MainSetup._build_dialog(Ui_Dialog_DEWETRON_Setting)
        MainSetup._register_window(created, app_ctx, "dialog_windowDewetronSetting", "uiDewetronSetting", dialog_windowDewetronSetting, uiDewetronSetting, sync_dialog_attr="dialog_windowDewetronSetting", sync_ui_attr="uiDewetronSetting")

        dialog_windowACSetting, uiACSetting = MainSetup._build_dialog(Ui_Dialog_AC_Setting)
        MainSetup._register_window(created, app_ctx, "dialog_windowACSetting", "uiACSetting", dialog_windowACSetting, uiACSetting, sync_dialog_attr="dialog_windowACSetting", sync_ui_attr="uiACSetting")

        dialog_windowDC1Setting, uiDC1Setting = MainSetup._build_dialog(Ui_Dialog_DC1_Setting)
        MainSetup._register_window(created, app_ctx, "dialog_windowDC1Setting", "uiDC1Setting", dialog_windowDC1Setting, uiDC1Setting)

        dialog_windowDC2Setting, uiDC2Setting = MainSetup._build_dialog(Ui_Dialog_DC2_Setting)
        MainSetup._register_window(created, app_ctx, "dialog_windowDC2Setting", "uiDC2Setting", dialog_windowDC2Setting, uiDC2Setting)

        dialog_windowDC3Setting, uiDC3Setting = MainSetup._build_dialog(Ui_Dialog_DC3_Setting)
        MainSetup._register_window(created, app_ctx, "dialog_windowDC3Setting", "uiDC3Setting", dialog_windowDC3Setting, uiDC3Setting)

        dialog_windowDC4Setting, uiDC4Setting = MainSetup._build_dialog(Ui_Dialog_DC4_Setting)
        MainSetup._register_window(created, app_ctx, "dialog_windowDC4Setting", "uiDC4Setting", dialog_windowDC4Setting, uiDC4Setting)

        dialog_windowTdianyashanbian, uiThaiDianYaShanBian = MainSetup._build_dialog(Ui_Dialog_thaiguodianyashanbian)
        MainSetup._register_window(created, app_ctx, "dialog_windowTdianyashanbian", "uiThaiDianYaShanBian", dialog_windowTdianyashanbian, uiThaiDianYaShanBian)

        dialog_windowfixedpf, uiThaiFixedPF = MainSetup._build_dialog(Ui_Dialog_thaifixedPF)
        MainSetup._register_window(created, app_ctx, "dialog_windowfixedpf", "uiThaiFixedPF", dialog_windowfixedpf, uiThaiFixedPF)

        dialog_windowoverloads, uiThaiOverLoads = MainSetup._build_dialog(Ui_Dialog_thaioverloads)
        MainSetup._register_window(created, app_ctx, "dialog_windowoverloads", "uiThaiOverLoads", dialog_windowoverloads, uiThaiOverLoads)

        dialog_windowcosPhiBrazil, uiThaiCosPhiBrazil = MainSetup._build_dialog(Ui_Dialog_thaicosPhi_Brazil)
        MainSetup._register_window(created, app_ctx, "dialog_windowcosPhiBrazil", "uiThaiCosPhiBrazil", dialog_windowcosPhiBrazil, uiThaiCosPhiBrazil)

        dialog_windowguoqianpin_immun, uiThaiGuoQianPin_Immun = MainSetup._build_dialog(Ui_Dialog_thaiguoqianpin_immun)
        MainSetup._register_window(created, app_ctx, "dialog_windowguoqianpin_immun", "uiThaiGuoQianPin_Immun", dialog_windowguoqianpin_immun, uiThaiGuoQianPin_Immun)

        dialog_windowstaticmppttest, uiThaiStaticMPPTTest = MainSetup._build_dialog(Ui_Dialog_thaistaticmppttest)
        MainSetup._register_window(created, app_ctx, "dialog_windowstaticmppttest", "uiThaiStaticMPPTTest", dialog_windowstaticmppttest, uiThaiStaticMPPTTest)

        dialog_windowfrequencyadaptability, uiThaiFrequencyAdaptability = MainSetup._build_dialog(
            Ui_Dialog_thaifrequencyadaptability
        )
        MainSetup._register_window(
            created,
            app_ctx,
            "dialog_windowfrequencyadaptability",
            "uiThaiFrequencyAdaptability",
            dialog_windowfrequencyadaptability,
            uiThaiFrequencyAdaptability,
        )

        return created


initialize_setup_windows = MainSetup.initialize_windows
