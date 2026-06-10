"""主程序试验设定装配模块。

这个模块负责把 `SCPITestWave.py` 中与“试验设定初始化”相关的
窗口创建、上下文同步、默认状态整理等逻辑集中起来。

注意：
- 这里只做模块化抽象，不改变原有业务逻辑。
- 代码仍然按照主程序原有顺序初始化，便于平滑迁移。
"""

from typing import Any, Dict

from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QScrollArea, QComboBox)
from components.buttons import ButtonStyle, apply_button_style
from components.timeline import build_timeline

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
    def embed_dialog_content(dialog, page_widget, settings_attr_name, layout_rows=None):
        """将 dialog 的内容嵌入到 page_widget 中。

        支持两种模式：
        1. Grid 模式：page 有 _grid_{name} 属性时，layout_rows 为 dict 列表，
           每个 dict 含 "title" 和 "widgets"，填充 QGridLayout。
        2. Scroll 模式：page 有 _settings_{name} 属性时，layout_rows 为 list 列表，
           每行是 objectName 列表，填充 QScrollArea。
        3. Auto 模式：layout_rows 为 None，按控件类型自动分组。
        """
        from PyQt5.QtWidgets import (QScrollArea, QFormLayout,
                                      QHBoxLayout, QVBoxLayout, QLabel,
                                      QTextEdit)
        from PyQt5 import QtCore

        # 样式常量
        _BTN_QSS = """
            QPushButton { color: #1e293b; background-color: #d1d5db; border: 1px solid #9ca3af;
                border-radius: 4px; padding: 6px 14px; font-size: 13px; }
            QPushButton:hover { background-color: #bcc3ce; }
        """
        _INPUT_QSS = """
            QTextEdit { color: #1e293b; background-color: #ffffff;
                border: 1px solid #d1d5db; border-radius: 4px; padding: 4px; font-size: 13px; }
            QComboBox { color: #1e293b; background-color: #ffffff;
                border: 1px solid #9ca3af; border-radius: 4px; padding: 4px 24px 4px 8px;
                font-size: 13px; }
            QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: center right;
                width: 24px; border: none; }
            QComboBox::down-arrow { image: none; border-left: 5px solid transparent;
                border-right: 5px solid transparent; border-top: 6px solid #374151; }
            QComboBox QAbstractItemView { background-color: #ffffff; color: #111827;
                border: 2px solid #3b82f6; selection-background-color: #3b82f6;
                selection-color: #ffffff; outline: none; }
            QComboBox QAbstractItemView::item { padding: 6px 12px; min-height: 28px;
                border-bottom: 1px solid #e5e7eb; }
        """
        _CONNECT_BTN_QSS = """
            QPushButton { color: #1e293b; background-color: #d1d5db; border: 1px solid #9ca3af;
                border-radius: 4px; padding: 6px 14px; font-size: 13px; }
            QPushButton:hover { background-color: #bcc3ce; }
        """
        _LABEL_QSS = "color: #1e293b; font-size: 13px; background: transparent;"
        _TITLE_QSS = "color: #1e293b; font-size: 13px; font-weight: bold; background: transparent;"

        def _style_widget(w):
            cls = type(w).__name__
            if cls == 'QPushButton':
                w.setStyleSheet(_BTN_QSS)
                w.setCursor(QtCore.Qt.PointingHandCursor)
            elif cls in ('QTextEdit', 'QComboBox', 'QLineEdit'):
                w.setStyleSheet(_INPUT_QSS)
            elif cls == 'QLabel':
                w.setStyleSheet(_LABEL_QSS)

        # 构建 objectName -> widget 索引（dialog 的直接子控件）
        all_widgets = {}
        for child in dialog.findChildren(QWidget):
            if child.parent() is dialog:
                all_widgets[child.objectName()] = child

        # 合并页面上预置的额外控件（如 WT3000 波特率下拉框）
        extra = getattr(page_widget, f"_extra_widgets_{settings_attr_name}", None)
        if extra:
            all_widgets.update(extra)

        # ── Grid 模式：时间线布局 ──
        grid_container = getattr(page_widget, f"_grid_{settings_attr_name}", None)
        if grid_container is not None and layout_rows is not None:
            grid_layout = grid_container.layout()
            connect_widgets = getattr(page_widget, f"_connect_widgets_{settings_attr_name}", None)

            # 日志控件：优先 textEdit_AC（AC），其次 textEdit_ReturnMessage（DC/DL850）
            log_edit = all_widgets.get("textEdit_AC")
            log_widget_name = None
            if log_edit is not None:
                log_edit.setReadOnly(True)
                log_edit.setStyleSheet(
                    "QTextEdit { background-color: #1e293b; color: #a0aec0; "
                    "border: 1px solid #4a5568; border-radius: 4px; "
                    "font-family: Consolas; font-size: 12px; padding: 4px; }"
                )
                setattr(page_widget, f"_log_{settings_attr_name}", log_edit)
            elif "textEdit_ReturnMessage" in all_widgets:
                log_widget_name = "textEdit_ReturnMessage"
                setattr(page_widget, f"_log_{settings_attr_name}",
                        all_widgets["textEdit_ReturnMessage"])

            # 通用按钮样式：ON=SUCCESS, OFF=DANGER, 命令=PRIMARY
            _btn_styles = {}
            for obj_name, w in all_widgets.items():
                if type(w).__name__ != 'QPushButton':
                    continue
                if "ON" in obj_name.upper() and "OFF" not in obj_name.upper():
                    _btn_styles[obj_name] = ButtonStyle.SUCCESS
                elif "OFF" in obj_name.upper():
                    _btn_styles[obj_name] = ButtonStyle.DANGER
                elif "SendMessage" in obj_name or "SendQuery" in obj_name:
                    _btn_styles[obj_name] = ButtonStyle.PRIMARY

            timeline = build_timeline(
                layout_rows, all_widgets,
                connect_widgets=connect_widgets,
                log_widget=log_edit,
                log_widget_name=log_widget_name,
                btn_styles=_btn_styles,
            )
            # 无日志步骤时，时间线不撑满（WT3000 等少步骤页面）
            _has_log = any(
                s.get("widgets") in ("__log__", "__log_widget__") or
                (isinstance(s.get("widgets"), list) and "__log__" in s.get("widgets"))
                for s in layout_rows
            )
            scroll = QScrollArea()
            scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
            if _has_log:
                scroll.setWidgetResizable(True)
            else:
                from PyQt5.QtWidgets import QSizePolicy
                scroll.setWidgetResizable(False)
                timeline.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            scroll.setWidget(timeline)
            grid_layout.addWidget(scroll, 0, 0)

            if not _has_log:
                parent_layout = grid_container.parent().layout()
                if parent_layout is not None:
                    for i in range(parent_layout.count()):
                        item = parent_layout.itemAt(i)
                        if item and item.widget() is grid_container:
                            parent_layout.setStretchFactor(grid_container, 0)
                            break
            return

        # ── Scroll 模式 ──
        settings_area = getattr(page_widget, f"_settings_{settings_attr_name}", None)
        if settings_area is None:
            return
        target_layout = settings_area.layout()

        # 给页面上的接口下拉框应用统一样式（AC/DC/DEWETRON 共用）
        _combo_qss = (
            "QComboBox { color: #1e293b; background-color: #ffffff; "
            "border: 1px solid #9ca3af; border-radius: 4px; padding: 4px 24px 4px 8px; "
            "font-size: 13px; }"
            "QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: center right; "
            "width: 24px; border: none; }"
            "QComboBox::down-arrow { image: none; border-left: 5px solid transparent; "
            "border-right: 5px solid transparent; border-top: 6px solid #374151; }"
            "QComboBox QAbstractItemView { background-color: #ffffff; color: #111827; "
            "border: 2px solid #3b82f6; selection-background-color: #3b82f6; "
            "selection-color: #ffffff; outline: none; }"
        )
        for _ch in page_widget.findChildren(QComboBox):
            if _ch.objectName() == settings_attr_name:
                _ch.setStyleSheet(_combo_qss)
                break

        # 布局型对话框（如 DEWETRON）：直接提取布局中的控件
        dlg_layout = dialog.layout()
        if dlg_layout is not None and layout_rows is None:
            # 移除页面底部的"操作日志"区域（对话框自带日志）
            page_layout = page_widget.layout()
            if page_layout is not None:
                for i in range(page_layout.count() - 1, -1, -1):
                    item = page_layout.itemAt(i)
                    w = item.widget() if item else None
                    if w is not None:
                        obj_name = w.objectName()
                        if (type(w).__name__ == 'QLabel' and w.text() == "操作日志:") or \
                           (type(w).__name__ == 'QTextEdit' and obj_name.startswith("log_")):
                            page_layout.removeWidget(w)
                            w.deleteLater()
            while dlg_layout.count():
                item = dlg_layout.takeAt(0)
                w = item.widget()
                if w is not None:
                    target_layout.addWidget(w)
            return

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(16, 8, 16, 8)
        container_layout.setSpacing(12)

        if layout_rows is not None:
            # 设备专用布局：按指定行顺序放置控件
            for row in layout_rows:
                row_widgets = []
                for name in row:
                    w = all_widgets.get(name)
                    if w is not None:
                        row_widgets.append(w)
                if not row_widgets:
                    continue
                if len(row_widgets) == 1:
                    w = row_widgets[0]
                    _style_widget(w)
                    container_layout.addWidget(w)
                else:
                    h = QHBoxLayout()
                    h.setSpacing(10)
                    for w in row_widgets:
                        _style_widget(w)
                        h.addWidget(w)
                    h.addStretch(1)
                    container_layout.addLayout(h)
        else:
            # 通用布局：按控件类型自动分组
            buttons = []
            form_pairs = []
            text_edits = []
            combos = []
            for w in all_widgets.values():
                cls = type(w).__name__
                if cls == 'QPushButton':
                    buttons.append(w)
                elif cls == 'QComboBox':
                    combos.append(w)
                elif cls == 'QTextEdit':
                    text_edits.append(w)

            seen_labels = set()
            for child in dialog.findChildren(QLabel):
                if child.parent() is not dialog:
                    continue
                lbl_name = child.objectName()
                if lbl_name in seen_labels:
                    continue
                lbl_geo = child.geometry()
                best_widget = None
                best_dist = 999999
                for inp in text_edits + combos:
                    if inp.parent() is not dialog:
                        continue
                    inp_geo = inp.geometry()
                    dy = abs(inp_geo.y() - lbl_geo.y())
                    dx = inp_geo.x() - lbl_geo.x()
                    if dy < 40 and 0 < dx < 200:
                        if dx < best_dist:
                            best_dist = dx
                            best_widget = inp
                if best_widget is not None:
                    form_pairs.append((child, best_widget))
                    seen_labels.add(lbl_name)

            if buttons:
                btn_row = QHBoxLayout()
                btn_row.setSpacing(10)
                for btn in buttons:
                    _style_widget(btn)
                    btn_row.addWidget(btn)
                btn_row.addStretch(1)
                container_layout.addLayout(btn_row)

            if form_pairs:
                form = QFormLayout()
                form.setSpacing(10)
                for lbl, inp in form_pairs:
                    _style_widget(lbl)
                    _style_widget(inp)
                    inp.setMinimumWidth(100)
                    form.addRow(lbl, inp)
                container_layout.addLayout(form)

            combo_set = {id(c) for _, c in form_pairs}
            orphan_combos = [c for c in combos if id(c) not in combo_set]
            if orphan_combos:
                combo_row = QHBoxLayout()
                combo_row.setSpacing(10)
                for c in orphan_combos:
                    _style_widget(c)
                    combo_row.addWidget(c)
                combo_row.addStretch(1)
                container_layout.addLayout(combo_row)

            text_edit_set = {id(t) for _, t in form_pairs}
            for te in text_edits:
                if id(te) not in text_edit_set:
                    _style_widget(te)
                    te.setMinimumHeight(100)
                    container_layout.addWidget(te, 1)

        container_layout.addStretch(1)
        scroll.setWidget(container)
        target_layout.addWidget(scroll)

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
