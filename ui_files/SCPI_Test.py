# -*- coding: utf-8 -*-

# V1.2 深色导航 + 现代工作台壳层
# 手动编写（非 pyuic5 生成），保留所有原始 widget 名称以兼容 SCPITestWave.py

from PyQt5 import QtCore, QtGui, QtWidgets

from components import ui_theme as theme


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setEnabled(True)
        # 不再 setFixedSize：实验室各机分辨率不同，启动后由 fit_window_to_screen 适配
        Dialog.setMinimumSize(1100, 700)
        Dialog.resize(1600, 900)
        import os as _os_icon
        _icon_path = _os_icon.path.join(_os_icon.path.dirname(_os_icon.path.abspath(__file__)), "logo.jpg")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)

        # ── 全局样式（壳层）──
        Dialog.setStyleSheet(theme.app_shell_qss())

        # ── 主布局 ──
        centralWidget = QtWidgets.QWidget(Dialog)
        centralWidget.setObjectName("centralWidget")
        Dialog.setCentralWidget(centralWidget)
        mainLayout = QtWidgets.QHBoxLayout(centralWidget)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # ══════════════════════════════════════
        # 左侧边栏 — 两级可折叠菜单
        # ══════════════════════════════════════
        sidebar = QtWidgets.QWidget()
        sidebar.setFixedWidth(theme.px(280))
        sidebar.setStyleSheet(theme.sidebar_qss())
        sidebar.setObjectName("sidebar")
        sidebar.setProperty("collapsed", False)
        sidebarLayout = QtWidgets.QVBoxLayout(sidebar)
        sidebarLayout.setContentsMargins(0, 0, 0, 0)
        sidebarLayout.setSpacing(0)
        self._sidebar = sidebar
        self._sidebar_expanded = True

        # Brand strip
        _brand = QtWidgets.QWidget()
        _brand.setObjectName("sidebarBrand")
        _brand.setStyleSheet(
            f"QWidget#sidebarBrand {{ background-color: {theme.SIDEBAR}; "
            f"border-bottom: 1px solid {theme.SIDEBAR_ELEVATED}; }}"
        )
        _brand_lay = QtWidgets.QVBoxLayout(_brand)
        _brand_lay.setContentsMargins(16, 18, 16, 16)
        _brand_lay.setSpacing(2)
        _brand_title = QtWidgets.QLabel("SolarAutoTest")
        _brand_title.setStyleSheet(
            "color: #f8fafc; font-size: 16px; font-weight: 700; background: transparent;"
        )
        _brand_sub = QtWidgets.QLabel("光伏并网试验台架")
        _brand_sub.setStyleSheet(
            f"color: {theme.NAV_MUTED}; font-size: 11px; background: transparent;"
        )
        from utils.app_version import read_app_version

        _app_ver = read_app_version()
        _brand_ver = QtWidgets.QLabel("版本 " + _app_ver)
        _brand_ver.setObjectName("label_app_version")
        _brand_ver.setStyleSheet(
            "color: #f8fafc; font-size: 13px; font-weight: 700; background: transparent;"
        )
        _brand_lay.addWidget(_brand_title)
        _brand_lay.addWidget(_brand_sub)
        _brand_lay.addWidget(_brand_ver)
        self._app_version_text = _app_ver
        self.label_app_version = _brand_ver
        sidebarLayout.addWidget(_brand)
        self._sidebar_brand = _brand
        self._sidebar_brand_title = _brand_title
        self._sidebar_brand_sub = _brand_sub

        # ── 样式常量（深色导航）──
        _HEADER_STYLE = theme.HEADER_STYLE
        _SUBHEADER_STYLE = theme.SUBHEADER_STYLE
        _ITEM_STYLE = theme.ITEM_STYLE
        _ITEM_ACTIVE_STYLE = theme.ITEM_ACTIVE_STYLE
        _NESTED_ITEM_STYLE = theme.NESTED_ITEM_STYLE
        _NESTED_ITEM_ACTIVE_STYLE = theme.NESTED_ITEM_ACTIVE_STYLE

        # 侧栏选中态（首页/设备/Auto_Test/其他 共用）
        self._nav_buttons = []
        self._nav_by_key = {}
        self._auto_test_categories = {}

        def _set_nav_active(btn):
            if btn is None:
                return
            for b in self._nav_buttons:
                kind = b.property("navKind") or "item"
                if b is btn:
                    b.setStyleSheet(
                        theme.NESTED_ITEM_ACTIVE_STYLE
                        if kind == "nested"
                        else theme.ITEM_ACTIVE_STYLE
                    )
                    b.setProperty("navActive", True)
                else:
                    b.setStyleSheet(
                        theme.NESTED_ITEM_STYLE if kind == "nested" else theme.ITEM_STYLE
                    )
                    b.setProperty("navActive", False)

        def _register_nav(btn, key=None, base_style=None, active_style=None, *, kind="item"):
            btn.setProperty("navKind", kind)
            btn.setProperty("navActive", False)
            btn.setProperty("navRole", "nested" if kind == "nested" else "item")
            btn._nav_base_style = base_style or (
                theme.NESTED_ITEM_STYLE if kind == "nested" else theme.ITEM_STYLE
            )
            btn._nav_active_style = active_style or (
                theme.NESTED_ITEM_ACTIVE_STYLE if kind == "nested" else theme.ITEM_ACTIVE_STYLE
            )
            self._nav_buttons.append(btn)
            if key:
                self._nav_by_key[key] = btn
            return btn

        self.set_nav_active = _set_nav_active
        self.set_nav_active_by_key = lambda key: _set_nav_active(self._nav_by_key.get(key))

        # ── 辅助函数 ──
        def _make_header(text, icon_name=None):
            btn = QtWidgets.QPushButton(f"  ▾  {text}")
            btn.setProperty("navRole", "header")
            btn.setStyleSheet(theme.HEADER_STYLE)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            if icon_name:
                _icon = btn.style().standardIcon(getattr(QtWidgets.QStyle, icon_name))
                btn.setIcon(_icon)
                btn.setIconSize(QtCore.QSize(theme.px(16), theme.px(16)))
            return btn

        def _make_item(text, page_index, *, key=None):
            btn = QtWidgets.QPushButton(f"      {text}")
            btn.setStyleSheet(theme.ITEM_STYLE)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            _register_nav(btn, key=key or text, kind="item")

            def _on_click(_checked=False, idx=page_index, b=btn):
                self.stackedWidget.setCurrentIndex(idx)
                _set_nav_active(b)

            btn.clicked.connect(_on_click)
            return btn

        def _make_container():
            w = QtWidgets.QWidget()
            w.setStyleSheet("background: transparent;")
            lay = QtWidgets.QVBoxLayout(w)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(0)
            return w, lay

        def _bind_toggle(header, container, default_text, *, style=None, indent="  "):
            def toggle():
                vis = container.isVisible()
                container.setVisible(not vis)
                arrow = "▾" if not vis else "▸"
                header.setText(f"{indent}{arrow}  {default_text}")
            header.clicked.connect(toggle)
            header.setStyleSheet(style or theme.HEADER_STYLE)

        # ══════════════════════════════════════
        # 可滚动菜单区
        # ══════════════════════════════════════
        _scrollArea = QtWidgets.QScrollArea()
        _scrollArea.setWidgetResizable(True)
        _scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        _scrollArea.setStyleSheet(theme.sidebar_scroll_qss())
        _scrollContent = QtWidgets.QWidget()
        _scrollContent.setStyleSheet(f"background: {theme.SIDEBAR};")
        _scrollLayout = QtWidgets.QVBoxLayout(_scrollContent)
        _scrollLayout.setContentsMargins(0, 0, 0, 0)
        _scrollLayout.setSpacing(0)

        # ── 首页（无二级菜单，直接点击切换） ──
        _home_item = _make_item("首页", 0, key="首页")
        _home_icon = _home_item.style().standardIcon(QtWidgets.QStyle.SP_FileDialogInfoView)
        _home_item.setIcon(_home_icon)
        _home_item.setIconSize(QtCore.QSize(16, 16))
        _scrollLayout.addWidget(_home_item)
        _set_nav_active(_home_item)  # 启动默认选中首页

        # ── 测试进度（首页下方独立菜单，对应 stacked 页 11）──
        _progress_item = _make_item("测试进度", 11, key="测试进度")
        _progress_icon = _progress_item.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekForward)
        _progress_item.setIcon(_progress_icon)
        _progress_item.setIconSize(QtCore.QSize(16, 16))
        _scrollLayout.addWidget(_progress_item)

        # ── Agent 日志（页 12）──
        _agent_log_item = _make_item("Agent 日志", 12, key="Agent 日志")
        _agent_log_icon = _agent_log_item.style().standardIcon(
            QtWidgets.QStyle.SP_FileDialogDetailedView
        )
        _agent_log_item.setIcon(_agent_log_icon)
        _agent_log_item.setIconSize(QtCore.QSize(16, 16))
        _agent_log_item.setToolTip("IOT Agent 通信信息与运行日志")
        _scrollLayout.addWidget(_agent_log_item)

        # ── 一级菜单: 设备管理 ──
        _sec_dev = _make_header("设备管理", "SP_ComputerIcon")
        _scrollLayout.addWidget(_sec_dev)

        _dev_container, _dev_layout = _make_container()
        self._dev_menu_layout = _dev_layout
        self.make_nav_item = _make_item
        self._dl850_nav_item = None
        for i, name in enumerate(["交流电源", "直流电源1", "直流电源2", "直流电源3",
                                    "直流电源4", "DL850", "WT3000", "DEWETRON"]):
            item = _make_item(name, i + 1, key=name)
            if name == "DL850":
                self._dl850_nav_item = item
            _dev_layout.addWidget(item)
        _dev_layout.addWidget(_make_item("数据测量", 13, key="数据测量"))
        _scrollLayout.addWidget(_dev_container)
        _bind_toggle(_sec_dev, _dev_container, "设备管理")

        # ── 一级菜单: Auto_Test（其下再按试验现象分子类）──
        _sec_auto = _make_header("Auto_Test", "SP_MediaPlay")
        _scrollLayout.addWidget(_sec_auto)

        _auto_container, _auto_layout = _make_container()
        _scrollLayout.addWidget(_auto_container)
        _bind_toggle(_sec_auto, _auto_container, "Auto_Test")

        def _add_auto_test_category(category):
            """在 Auto_Test 下添加可折叠子分类；重复调用返回已有 layout。"""
            if category in self._auto_test_categories:
                return self._auto_test_categories[category]["layout"]
            header = QtWidgets.QPushButton(f"    ▾  {category}")
            header.setProperty("navRole", "subheader")
            header.setStyleSheet(theme.SUBHEADER_STYLE)
            header.setCursor(QtCore.Qt.PointingHandCursor)
            cat_w, cat_lay = _make_container()
            _auto_layout.addWidget(header)
            _auto_layout.addWidget(cat_w)
            _bind_toggle(header, cat_w, category, style=theme.SUBHEADER_STYLE, indent="    ")
            self._auto_test_categories[category] = {
                "header": header,
                "container": cat_w,
                "layout": cat_lay,
            }
            return cat_lay

        def _add_auto_test_item(text, page_index=9, setting_key=None, category=None):
            parent_layout = _auto_layout
            kind = "item"
            label = f"      {text}"
            if category:
                parent_layout = _add_auto_test_category(category)
                kind = "nested"
                label = f"        {text}"

            item = QtWidgets.QPushButton(label)
            item.setStyleSheet(
                theme.NESTED_ITEM_STYLE if kind == "nested" else theme.ITEM_STYLE
            )
            item.setCursor(QtCore.Qt.PointingHandCursor)
            tip = f"{category} / {text}" if category else text
            item.setToolTip(tip)
            _register_nav(item, key=text, kind=kind)

            def _on_click(_checked=False, b=item, proj=text, sk=setting_key, idx=page_index):
                self.stackedWidget.setCurrentIndex(idx)
                idx_p = self.comboBox_P.findText("Auto_Test")
                if idx_p >= 0:
                    self.comboBox_P.setCurrentIndex(idx_p)
                idx_ps = self.comboBox_PS.findText(proj)
                if idx_ps >= 0:
                    self.comboBox_PS.setCurrentIndex(idx_ps)
                if sk and hasattr(self, "settingStack"):
                    pages = getattr(self.settingStack, "_pages", {})
                    if sk in pages:
                        self.settingStack.setCurrentWidget(pages[sk])
                    elif hasattr(self.settingStack, "_blank_page"):
                        self.settingStack.setCurrentWidget(self.settingStack._blank_page)
                _set_nav_active(b)

            item.clicked.connect(_on_click)
            parent_layout.addWidget(item)

        self.add_auto_test_category = _add_auto_test_category
        self.add_auto_test_item = _add_auto_test_item

        # ── 一级菜单: 其他 ──
        _sec_other = _make_header("其他", "SP_FileDialogDetailedView")
        _scrollLayout.addWidget(_sec_other)

        _other_container, _other_layout = _make_container()
        _other_layout.addWidget(_make_item("命令文件", 10, key="命令文件"))
        _scrollLayout.addWidget(_other_container)
        _bind_toggle(_sec_other, _other_container, "其他")

        _scrollLayout.addStretch(1)
        _scrollArea.setWidget(_scrollContent)
        sidebarLayout.addWidget(_scrollArea, 1)
        self._sidebar_scroll = _scrollArea

        # ══════════════════════════════════════
        # 底部固定区（分隔线 + 刷新按钮）
        # ══════════════════════════════════════
        _sep = QtWidgets.QFrame()
        _sep.setFrameShape(QtWidgets.QFrame.HLine)
        _sep.setStyleSheet(
            f"color: {theme.SIDEBAR_ELEVATED}; background: {theme.SIDEBAR_ELEVATED}; "
            f"max-height: 1px; margin: 0 12px;"
        )
        sidebarLayout.addWidget(_sep)

        bottomBar = QtWidgets.QWidget()
        bottomBar.setStyleSheet("background: transparent;")
        bottomLayout = QtWidgets.QHBoxLayout(bottomBar)
        bottomLayout.setContentsMargins(12, 8, 12, 12)
        bottomLayout.setSpacing(8)

        self.pushButton_ToggleSidebar = QtWidgets.QPushButton("«")
        self.pushButton_ToggleSidebar.setObjectName("pushButton_ToggleSidebar")
        self.pushButton_ToggleSidebar.setFixedSize(36, 36)
        self.pushButton_ToggleSidebar.setToolTip("收起 / 展开导航栏")
        self.pushButton_ToggleSidebar.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.SIDEBAR_ELEVATED}; color: {theme.NAV_TEXT};
                border: 1px solid #334155; border-radius: 8px; font-size: 16px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: #334155; color: #f8fafc; }}
        """)
        bottomLayout.addWidget(self.pushButton_ToggleSidebar)

        self.pushButton_ReConnectEQU = QtWidgets.QPushButton()
        self.pushButton_ReConnectEQU.setFixedSize(36, 36)
        self.pushButton_ReConnectEQU.setToolTip("刷新设备")
        self.pushButton_ReConnectEQU.setObjectName("pushButton_ReConnectEQU")
        _refresh_icon = self.pushButton_ReConnectEQU.style().standardIcon(
            QtWidgets.QStyle.SP_BrowserReload)
        self.pushButton_ReConnectEQU.setIcon(_refresh_icon)
        self.pushButton_ReConnectEQU.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_ReConnectEQU.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.SIDEBAR_ELEVATED}; color: {theme.NAV_TEXT};
                border: 1px solid #334155; border-radius: 8px;
            }}
            QPushButton:hover {{ background-color: #334155; color: #f8fafc; }}
        """)
        bottomLayout.addWidget(self.pushButton_ReConnectEQU)
        self.pushButton_FindDevicesSidebar = QtWidgets.QPushButton()
        self.pushButton_FindDevicesSidebar.setFixedSize(36, 36)
        self.pushButton_FindDevicesSidebar.setToolTip("扫描并连接设备")
        self.pushButton_FindDevicesSidebar.setObjectName("pushButton_FindDevicesSidebar")
        _find_icon = self.pushButton_FindDevicesSidebar.style().standardIcon(
            QtWidgets.QStyle.SP_FileDialogContentsView)
        self.pushButton_FindDevicesSidebar.setIcon(_find_icon)
        self.pushButton_FindDevicesSidebar.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_FindDevicesSidebar.setStyleSheet(f"""
            QPushButton {{
                background-color: #134e4a; color: #99f6e4;
                border: 1px solid {theme.ACCENT}; border-radius: 8px;
            }}
            QPushButton:hover {{ background-color: #115e59; color: #ccfbf1; }}
        """)
        bottomLayout.addWidget(self.pushButton_FindDevicesSidebar)
        bottomLayout.addStretch(1)

        sidebarLayout.addWidget(bottomBar)
        self._sidebar_bottom = bottomBar
        mainLayout.addWidget(sidebar)

        def _apply_sidebar_collapsed(collapsed: bool) -> None:
            self._sidebar_expanded = not collapsed
            sidebar.setProperty("collapsed", bool(collapsed))
            if collapsed:
                sidebar.setFixedWidth(theme.px(64))
                _brand_title.setText("S")
                _brand_sub.setVisible(False)
                _brand_lay.setContentsMargins(8, 12, 8, 8)
                for btn in self._nav_buttons:
                    tip = btn.toolTip() or (btn.property("_nav_full_text") or btn.text() or "").strip()
                    if tip:
                        btn.setToolTip(str(tip).lstrip("▾▸ "))
                    t = (btn.text() or "").strip()
                    if t:
                        btn.setProperty("_nav_full_text", t)
                    btn.setText("")
                    btn.setFixedHeight(theme.px(40))
                for header in sidebar.findChildren(QtWidgets.QPushButton):
                    role = header.property("navRole")
                    if role in ("header", "subheader"):
                        ht = (header.text() or "").strip()
                        if ht:
                            header.setProperty("_nav_full_text", ht)
                        header.setText("")
                        header.setFixedHeight(theme.px(28))
                self.pushButton_ToggleSidebar.setText("»")
                self.pushButton_ToggleSidebar.setToolTip("展开导航栏")
                # 窄栏时竖排底部按钮，避免挤出
                while bottomLayout.count():
                    item = bottomLayout.takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)
                bottom_v = getattr(self, "_sidebar_bottom_v", None)
                if bottom_v is None:
                    wrap = QtWidgets.QWidget()
                    wrap.setStyleSheet("background: transparent;")
                    bottom_v = QtWidgets.QVBoxLayout(wrap)
                    bottom_v.setContentsMargins(0, 0, 0, 0)
                    bottom_v.setSpacing(6)
                    self._sidebar_bottom_v = bottom_v
                    self._sidebar_bottom_wrap = wrap
                for b in (
                    self.pushButton_ToggleSidebar,
                    self.pushButton_ReConnectEQU,
                    self.pushButton_FindDevicesSidebar,
                ):
                    bottom_v.addWidget(b)
                bottomLayout.setContentsMargins(10, 8, 10, 12)
                bottomLayout.addWidget(self._sidebar_bottom_wrap)
            else:
                sidebar.setFixedWidth(theme.px(280))
                _brand_title.setText("SolarAutoTest")
                _brand_sub.setVisible(True)
                _brand_lay.setContentsMargins(16, 18, 16, 16)
                for btn in sidebar.findChildren(QtWidgets.QPushButton):
                    full = btn.property("_nav_full_text")
                    if full:
                        btn.setText(str(full))
                    btn.setMinimumHeight(0)
                    btn.setMaximumHeight(16777215)
                self.pushButton_ToggleSidebar.setText("«")
                self.pushButton_ToggleSidebar.setToolTip("收起导航栏")
                # 恢复横排
                wrap = getattr(self, "_sidebar_bottom_wrap", None)
                if wrap is not None:
                    bottomLayout.removeWidget(wrap)
                    wrap.setParent(None)
                while bottomLayout.count():
                    item = bottomLayout.takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)
                bottomLayout.setContentsMargins(12, 8, 12, 12)
                bottomLayout.addWidget(self.pushButton_ToggleSidebar)
                bottomLayout.addWidget(self.pushButton_ReConnectEQU)
                bottomLayout.addWidget(self.pushButton_FindDevicesSidebar)
                bottomLayout.addStretch(1)

        def _toggle_sidebar():
            _apply_sidebar_collapsed(self._sidebar_expanded)

        self.pushButton_ToggleSidebar.clicked.connect(_toggle_sidebar)
        self.set_sidebar_collapsed = _apply_sidebar_collapsed

        # ══════════════════════════════════════
        # 右侧内容区
        # ══════════════════════════════════════
        rightPanel = QtWidgets.QWidget()
        rightPanel.setStyleSheet(f"background-color: {theme.BG};")
        rightLayout = QtWidgets.QVBoxLayout(rightPanel)
        rightLayout.setContentsMargins(0, 0, 0, 0)
        rightLayout.setSpacing(0)

        # -- QStackedWidget --
        self.stackedWidget = QtWidgets.QStackedWidget()
        self.stackedWidget.setStyleSheet(
            f"QStackedWidget {{ background-color: {theme.BG}; border: none; }}"
        )

        _pageStyle = theme.PAGE_STYLE
        _cardStyle = theme.CARD_STYLE
        _logStyle = theme.LOG_STYLE

        def _make_device_page(label_text, connect_btn_name, set_btn_name=None,
                              combo_name=None, has_editable=True, use_grid=False,
                              use_ip_input=False):
            """构造设备页面：标题 + 连接区 + 日志，并将控件存为 Ui_Dialog 实例属性。

            use_grid=True 时，创建 QGridLayout 容器供 embed_dialog_content 填充，
            连接控件和日志区由 embed_dialog_content 统一放入网格。
            use_ip_input=True 时，使用IP地址输入框替代comboBox（用于DEWETRON等TCP设备）。
            """
            page = QtWidgets.QWidget()
            page.setStyleSheet(_pageStyle)
            layout = QtWidgets.QVBoxLayout(page)
            layout.setContentsMargins(24, 16, 24, 16)
            layout.setSpacing(12)

            # 标题
            lbl = QtWidgets.QLabel(label_text)
            lbl.setStyleSheet(
                f"font-size: 18px; font-weight: 700; color: {theme.INK}; background: transparent;"
            )
            layout.addWidget(lbl)

            # 创建连接控件
            combo = None
            ip_edit = None
            port_edit = None

            if use_ip_input:
                # IP输入模式：用于DEWETRON等TCP设备
                ip_edit = QtWidgets.QLineEdit()
                ip_edit.setObjectName(f"lineEdit_{combo_name}_IP" if combo_name else "lineEdit_IP")
                ip_edit.setPlaceholderText("IP地址 (如 192.168.40.21)")
                ip_edit.setMinimumWidth(160)
                port_edit = QtWidgets.QLineEdit()
                port_edit.setObjectName(f"lineEdit_{combo_name}_Port" if combo_name else "lineEdit_Port")
                port_edit.setPlaceholderText("端口 (默认10001)")
                port_edit.setMinimumWidth(100)
                setattr(self, f"lineEdit_{combo_name}_IP" if combo_name else "lineEdit_IP", ip_edit)
                setattr(self, f"lineEdit_{combo_name}_Port" if combo_name else "lineEdit_Port", port_edit)
            else:
                # ComboBox模式
                combo = QtWidgets.QComboBox()
                combo.setObjectName(combo_name)
                combo.setEditable(has_editable)
                combo.setMinimumWidth(200)
                setattr(self, combo_name, combo)

            connectBtn = QtWidgets.QPushButton("连接设备")
            connectBtn.setObjectName(connect_btn_name)
            connectBtn.setMinimumWidth(theme.px(108))
            connectBtn.setSizePolicy(
                QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
            )
            setattr(self, connect_btn_name, connectBtn)

            setBtn = None
            if set_btn_name:
                setBtn = QtWidgets.QPushButton("设定")
                setBtn.setObjectName(set_btn_name)
                setBtn.setMinimumWidth(theme.px(100))
                setBtn.setSizePolicy(
                    QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
                )
                setBtn.setStyleSheet(f"""
                    QPushButton {{ background-color: {theme.SUCCESS}; color: white; border: none;
                        border-radius: 8px; font-weight: 700; padding: 6px 12px; }}
                    QPushButton:hover {{ background-color: {theme.SUCCESS_HOVER}; }}
                """)
                setattr(self, set_btn_name, setBtn)

            if use_grid:
                # Grid 模式：创建网格容器，由 embed_dialog_content 填充
                grid_container = QtWidgets.QWidget()
                grid_container.setObjectName("_grid_container")
                grid_container.setStyleSheet("background: transparent;")
                grid_layout = QtWidgets.QGridLayout(grid_container)
                grid_layout.setContentsMargins(0, 0, 0, 0)
                grid_layout.setSpacing(4)
                setattr(page, f"_grid_{combo_name}", grid_container)
                setattr(page, f"_connect_widgets_{combo_name}", (combo, connectBtn, setBtn))
                layout.addWidget(grid_container, 1)
            else:
                # 原始模式：连接卡片 + 设置区 + 日志区

                card = QtWidgets.QWidget()
                card.setObjectName("card")
                card.setStyleSheet(_cardStyle)
                cardLayout = QtWidgets.QVBoxLayout(card)
                cardLayout.setContentsMargins(16, 12, 16, 12)
                cardLayout.setSpacing(10)

                row = QtWidgets.QHBoxLayout()
                row.setSpacing(8)

                if use_ip_input:
                    # IP输入模式：显示IP地址和端口输入框
                    ipLabel = QtWidgets.QLabel("IP地址:")
                    ipLabel.setStyleSheet("font-size: 13px; background: transparent;")
                    row.addWidget(ipLabel)
                    row.addWidget(ip_edit)
                    portLabel = QtWidgets.QLabel("端口:")
                    portLabel.setStyleSheet("font-size: 13px; background: transparent;")
                    row.addWidget(portLabel)
                    row.addWidget(port_edit)
                else:
                    # ComboBox模式：显示接口下拉框
                    interfaceLabel = QtWidgets.QLabel("接口:")
                    interfaceLabel.setStyleSheet("font-size: 13px; background: transparent;")
                    row.addWidget(interfaceLabel)
                    row.addWidget(combo, 1)

                row.addWidget(connectBtn)
                if setBtn is not None:
                    row.addWidget(setBtn)
                cardLayout.addLayout(row)
                layout.addWidget(card)

                _settings_area = QtWidgets.QWidget()
                _settings_area.setObjectName("_settings_area")
                _settings_area.setStyleSheet("background: transparent;")
                _settings_area.setMinimumHeight(400)
                _settings_area_lay = QtWidgets.QVBoxLayout(_settings_area)
                _settings_area_lay.setContentsMargins(0, 0, 0, 0)
                # 对于use_ip_input模式，使用固定属性名
                _settings_key = combo_name if combo_name else "comboBox_DEWETRON"
                setattr(page, f"_settings_{_settings_key}", _settings_area)
                layout.addWidget(_settings_area, 1)

                log_label = QtWidgets.QLabel("操作日志:")
                log_label.setStyleSheet(
                    f"font-size: 13px; font-weight: 700; color: {theme.INK}; background: transparent;"
                )
                layout.addWidget(log_label)

                log_edit = QtWidgets.QTextEdit()
                log_edit.setObjectName(f"log_{combo_name}")
                log_edit.setReadOnly(True)
                log_edit.setMaximumHeight(120)
                log_edit.setStyleSheet(theme.LOG_QSS)
                _log_key = combo_name if combo_name else "comboBox_DEWETRON"
                setattr(page, f"_log_{_log_key}", log_edit)
                layout.addWidget(log_edit)

            return page

        # ── 页面 0: 首页 ──
        homePage = QtWidgets.QWidget()
        homePage.setStyleSheet(_pageStyle)
        homeLayout = QtWidgets.QVBoxLayout(homePage)
        homeLayout.setContentsMargins(24, 16, 24, 16)
        homeLayout.setSpacing(12)

        homeTitle = QtWidgets.QLabel("工作台")
        homeTitle.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {theme.INK}; background: transparent;"
        )
        homeLayout.addWidget(homeTitle)
        homeSub = QtWidgets.QLabel("设备连接 · 试验项目 · 运行状态")
        homeSub.setStyleSheet(
            f"font-size: 12px; color: {theme.MUTED}; background: transparent; margin-bottom: 4px;"
        )
        homeLayout.addWidget(homeSub)

        # IOT Agent：软件启动后静默拉起；首页仅显示状态（可停止）
        _iotRow = QtWidgets.QHBoxLayout()
        _iotRow.setSpacing(8)
        self.label_IotAgentStatus = QtWidgets.QLabel("IOT Agent: —")
        self.label_IotAgentStatus.setObjectName("label_IotAgentStatus")
        self.label_IotAgentStatus.setStyleSheet(
            f"font-size: 12px; color: {theme.MUTED}; background: transparent;"
        )
        _iotRow.addWidget(self.label_IotAgentStatus)
        self.pushButton_StopIotAgent = QtWidgets.QPushButton("停止 Agent")
        self.pushButton_StopIotAgent.setObjectName("pushButton_StopIotAgent")
        self.pushButton_StopIotAgent.setFixedHeight(32)
        self.pushButton_StopIotAgent.setToolTip("一般无需操作；Agent 会在软件启动时后台自动拉起")
        self.pushButton_StopIotAgent.setStyleSheet(
            f"QPushButton {{ background:{theme.PANEL}; color:{theme.INK}; border:1px solid {theme.LINE_STRONG}; "
            f"border-radius:8px; padding:0 12px; font-size:12px; }}"
            f"QPushButton:hover {{ background:{theme.NEUTRAL}; }}"
        )
        _iotRow.addWidget(self.pushButton_StopIotAgent)
        self.pushButton_FindDevices = QtWidgets.QPushButton("扫描并连接设备")
        self.pushButton_FindDevices.setObjectName("pushButton_FindDevices")
        self.pushButton_FindDevices.setFixedHeight(34)
        self.pushButton_FindDevices.setToolTip("扫描局域网/上次地址，勾选后连接电源、示波器、功率分析仪、德威创")
        self.pushButton_FindDevices.setStyleSheet(
            f"QPushButton {{ background:{theme.ACCENT}; color:white; border:none; border-radius:8px; "
            f"padding:0 16px; font-size:13px; font-weight:700; }}"
            f"QPushButton:hover {{ background:{theme.ACCENT_HOVER}; }}"
        )
        _iotRow.addWidget(self.pushButton_FindDevices)
        self.pushButton_OpenIotAgentLog = QtWidgets.QPushButton("Agent 日志")
        self.pushButton_OpenIotAgentLog.setObjectName("pushButton_OpenIotAgentLog")
        self.pushButton_OpenIotAgentLog.setFixedHeight(32)
        self.pushButton_OpenIotAgentLog.setToolTip("查看设备号、通信参数与 Agent 运行日志")
        self.pushButton_OpenIotAgentLog.setStyleSheet(
            f"QPushButton {{ background:{theme.PANEL}; color:{theme.INK}; border:1px solid {theme.LINE_STRONG}; "
            f"border-radius:8px; padding:0 12px; font-size:12px; }}"
            f"QPushButton:hover {{ background:{theme.NEUTRAL}; }}"
        )
        _iotRow.addWidget(self.pushButton_OpenIotAgentLog)
        _iotRow.addStretch(1)
        homeLayout.addLayout(_iotRow)

        # -- 设备状态网格 (2x4，8个设备写死) --
        _devGridTitle = QtWidgets.QLabel("设备状态")
        _devGridTitle.setStyleSheet(
            f"font-size: 14px; font-weight: 700; color: {theme.INK}; background: transparent;"
        )
        homeLayout.addWidget(_devGridTitle)

        _CARD_QSS = theme.CARD_STYLE
        # 设备名 → 对应页面索引
        _dev_page_map = {
            "交流电源": 1, "直流电源1": 2, "直流电源2": 3, "直流电源3": 4,
            "直流电源4": 5, "DL850": 6, "WT3000": 7, "DEWETRON": 8
        }
        _home_dev_names = list(_dev_page_map.keys())
        self.home_device_cards = QtWidgets.QGridLayout()
        self.home_device_cards.setSpacing(12)
        self.home_device_cards.setContentsMargins(0, 0, 0, 0)
        homeLayout.addLayout(self.home_device_cards)

        # 存储每个设备的状态点和资源标签，供后续更新
        self._home_dots = {}
        self._home_res_labels = {}
        self._home_time_labels = {}
        self._home_cards = {}

        for _idx, _dev_name in enumerate(_home_dev_names):
            _r, _c = _idx // 2, _idx % 2
            _card = QtWidgets.QWidget()
            _card.setObjectName("deviceCard")
            _card.setStyleSheet(_CARD_QSS)
            _card.setFixedHeight(90)
            _card.setCursor(QtCore.Qt.PointingHandCursor)
            # 点击跳转到对应设备页面
            _page_idx = _dev_page_map[_dev_name]
            _card.mousePressEvent = lambda event, idx=_page_idx: self.stackedWidget.setCurrentIndex(idx)
            _cl = QtWidgets.QVBoxLayout(_card)
            _cl.setContentsMargins(14, 10, 14, 10)
            _cl.setSpacing(4)
            # 第一行：设备名 + 状态点
            _tr = QtWidgets.QHBoxLayout()
            _tr.setSpacing(6)
            _nl = QtWidgets.QLabel(_dev_name)
            _nl.setStyleSheet(
                f"font-size: 13px; font-weight: 700; color: {theme.INK}; background: transparent;"
            )
            _tr.addWidget(_nl)
            _tr.addStretch(1)
            # Connection status: text badge (not a 10×10 color block — those got
            # mistaken for compact inputs and blown into huge red rectangles).
            _dot = QtWidgets.QLabel("未连接")
            _dot.setObjectName("deviceStatusBadge")
            _dot.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            _dot.setStyleSheet(
                f"QLabel#deviceStatusBadge {{ color: {theme.DANGER}; font-size: 11px; "
                f"font-weight: bold; background-color: transparent; padding: 0px; }}"
            )
            _tr.addWidget(_dot)
            _cl.addLayout(_tr)
            # 第二行：资源地址
            _rl = QtWidgets.QLabel("未配置")
            _rl.setStyleSheet(
                f"font-size: 11px; color: {theme.MUTED}; background: transparent;"
            )
            _rl.setWordWrap(True)
            _cl.addWidget(_rl)
            # 第三行：上次连接时间
            _tl = QtWidgets.QLabel("")
            _tl.setStyleSheet(
                f"font-size: 10px; color: {theme.MUTED}; background: transparent;"
            )
            _cl.addWidget(_tl)
            _cl.addStretch()
            self.home_device_cards.addWidget(_card, _r, _c)
            self._home_dots[_dev_name] = _dot
            self._home_res_labels[_dev_name] = _rl
            self._home_time_labels[_dev_name] = _tl
            self._home_cards[_dev_name] = _card

        # -- 当前测试项目卡片 --
        _testCard = QtWidgets.QWidget()
        _testCard.setObjectName("card")
        _testCard.setStyleSheet(_cardStyle)
        _testCardLayout = QtWidgets.QVBoxLayout(_testCard)
        _testCardLayout.setContentsMargins(16, 12, 16, 12)
        _testCardLayout.setSpacing(8)
        _testCardTitle = QtWidgets.QLabel("当前测试项目")
        _testCardTitle.setStyleSheet(
            f"font-size: 14px; font-weight: 700; color: {theme.INK}; background: transparent;"
        )
        _testCardLayout.addWidget(_testCardTitle)
        self.home_project_name = QtWidgets.QLabel("暂无测试项目")
        self.home_project_name.setStyleSheet(
            f"font-size: 13px; color: {theme.MUTED}; background: transparent;"
        )
        _testCardLayout.addWidget(self.home_project_name)
        _statusRow = QtWidgets.QHBoxLayout()
        _statusRow.setSpacing(12)
        _statusLabel = QtWidgets.QLabel("状态:")
        _statusLabel.setStyleSheet(
            f"font-size: 12px; color: {theme.MUTED}; background: transparent;"
        )
        _statusRow.addWidget(_statusLabel)
        self.home_status = QtWidgets.QLabel("未开始")
        self.home_status.setStyleSheet(
            f"font-size: 12px; font-weight: 700; color: {theme.MUTED}; background: transparent;"
        )
        _statusRow.addWidget(self.home_status)
        _statusRow.addStretch(1)
        _testCardLayout.addLayout(_statusRow)
        self.home_progress = QtWidgets.QProgressBar()
        self.home_progress.setRange(0, 100)
        self.home_progress.setValue(0)
        self.home_progress.setFixedHeight(18)
        self.home_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {theme.LINE}; border-radius: 8px;
                background: #eef2f7; text-align: center; font-size: 11px; color: {theme.INK};
            }}
            QProgressBar::chunk {{ background-color: {theme.ACCENT}; border-radius: 7px; }}
        """)
        _testCardLayout.addWidget(self.home_progress)
        _timeRow = QtWidgets.QHBoxLayout()
        _timeRow.setSpacing(24)
        _startLabel = QtWidgets.QLabel("开始时间:")
        _startLabel.setStyleSheet(
            f"font-size: 12px; color: {theme.MUTED}; background: transparent;"
        )
        _timeRow.addWidget(_startLabel)
        self.home_start_time = QtWidgets.QLabel("--")
        self.home_start_time.setStyleSheet(
            f"font-size: 12px; color: {theme.MUTED}; background: transparent;"
        )
        _timeRow.addWidget(self.home_start_time)
        _endLabel = QtWidgets.QLabel("预估结束:")
        _endLabel.setStyleSheet(
            f"font-size: 12px; color: {theme.MUTED}; background: transparent;"
        )
        _timeRow.addWidget(_endLabel)
        self.home_estimated_end_time = QtWidgets.QLabel("--")
        self.home_estimated_end_time.setStyleSheet(
            f"font-size: 12px; color: {theme.MUTED}; background: transparent;"
        )
        _timeRow.addWidget(self.home_estimated_end_time)
        _timeRow.addStretch(1)
        _testCardLayout.addLayout(_timeRow)
        homeLayout.addWidget(_testCard, 1)

        self.stackedWidget.insertWidget(0, homePage)

        # ── 加载 status.json 更新首页 ──
        def _load_home_status():
            import json as _json
            import os as _os2
            _status_file = _os2.path.join(_os2.path.dirname(_os2.path.abspath(__file__)), "..", "status.json")
            try:
                with open(_status_file, "r", encoding="utf-8") as f:
                    _data = _json.load(f)
            except Exception:
                return
            # 冷启动：上次「进行中」已无试验线程，先标中止再展示（避免首页残留进度）
            try:
                from utils.status_json_devices import mark_stale_in_flight_project

                _data, _stale = mark_stale_in_flight_project(_data)
                if _stale:
                    with open(_status_file, "w", encoding="utf-8") as f:
                        _json.dump(_data, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            # 更新设备卡片
            for _dev in _data.get("devices", []):
                _name = _dev["name"]
                if _name in self._home_dots:
                    _ok = bool(_dev.get("connected"))
                    _color = theme.SUCCESS if _ok else theme.DANGER
                    _text = "已连接" if _ok else "未连接"
                    self._home_dots[_name].setText(_text)
                    self._home_dots[_name].setStyleSheet(
                        f"QLabel#deviceStatusBadge {{ color: {_color}; font-size: 11px; "
                        f"font-weight: bold; background-color: transparent; padding: 0px; }}"
                    )
                if _name in self._home_res_labels:
                    _res = _dev.get("resource", "") or "未配置"
                    self._home_res_labels[_name].setText(_res)
                if _name in self._home_time_labels:
                    _last = _dev.get("last_connected", "")
                    self._home_time_labels[_name].setText(f"上次连接: {_last}" if _last else "")
            # 更新项目信息
            _proj = _data.get("project", {})
            if _proj:
                self.home_project_name.setText(_proj.get("name", "暂无测试项目"))
                self.home_project_name.setStyleSheet(
                    f"font-size: 13px; font-weight: 700; color: {theme.INK}; background: transparent;"
                )
                _status = _proj.get("status", "未开始")
                _color_map = {
                    "未开始": theme.MUTED,
                    "进行中": theme.ACCENT,
                    "已结束": theme.SUCCESS,
                    "已中止": theme.DANGER,
                }
                self.home_status.setText(_status)
                self.home_status.setStyleSheet(
                    f"font-size: 12px; font-weight: 700; color: {_color_map.get(_status, theme.MUTED)}; "
                    f"background: transparent;"
                )
                self.home_progress.setValue(_proj.get("progress", 0))
                self.home_start_time.setText(_proj.get("start_time", "--"))
                self.home_estimated_end_time.setText(_proj.get("estimated_end_time", "--"))
        _load_home_status()

        # ── 页面 1: 交流电源 ──
        self.stackedWidget.addWidget(
            _make_device_page("交流电源", "pushButton_ConnectEQUAC",
                              "pushButton_SetACOptions", "comboBox_AC",
                              use_grid=True))

        # ── 页面 2~5: 直流电源 ──
        for i in range(1, 5):
            self.stackedWidget.addWidget(
                _make_device_page(f"直流电源{i}", f"pushButton_ConnectEQUDC{i}",
                                  f"pushButton_SetDC{i}Options", f"comboBox_DC{i}",
                                  use_grid=True))

        # ── 页面 5: DL850 ──
        self.stackedWidget.addWidget(
            _make_device_page("DL850 示波器", "pushButton_ConnectEQUDL850",
                              "pushButton_SetDL850Options", "comboBox_DL850",
                              has_editable=False, use_grid=True))

        # ── 页面 6: WT3000 ──
        self.stackedWidget.addWidget(
            _make_device_page("WT3000 功率分析仪", "pushButton_ConnectEQUWT3000",
                              "pushButton_SetWT3000Options", "comboBox_WT3000",
                              has_editable=False, use_grid=True))

        # ── 页面 7: DEWETRON ──
        self.stackedWidget.addWidget(
            _make_device_page("德威创", "pushButton_ConnectEQUDEWETRON",
                              use_ip_input=True))

        # ── 页面 9: 项目配置 ──
        projectPage = QtWidgets.QWidget()
        projectPage.setStyleSheet(_pageStyle)
        projectPageLayout = QtWidgets.QVBoxLayout(projectPage)
        projectPageLayout.setContentsMargins(24, 16, 24, 16)
        projectPageLayout.setSpacing(12)

        projTitleRow = QtWidgets.QHBoxLayout()
        projTitle = QtWidgets.QLabel("项目配置")
        projTitle.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {theme.INK}; background: transparent;"
        )
        projVer = QtWidgets.QLabel("版本 " + getattr(self, "_app_version_text", ""))
        projVer.setObjectName("label_project_app_version")
        projVer.setStyleSheet(
            f"font-size: 15px; font-weight: 700; color: {theme.INK}; background: transparent;"
        )
        projTitleRow.addWidget(projTitle)
        projTitleRow.addStretch(1)
        projTitleRow.addWidget(projVer)
        projectPageLayout.addLayout(projTitleRow)
        self.label_project_app_version = projVer

        # 保留comboBox定义但隐藏（供其他代码引用）
        self.comboBox_P = QtWidgets.QComboBox()
        self.comboBox_P.setObjectName("comboBox_P")
        self.comboBox_P.setVisible(False)
        self.comboBox_PS = QtWidgets.QComboBox()
        self.comboBox_PS.setObjectName("comboBox_PS")
        self.comboBox_PS.setVisible(False)

        # 设置对话框内嵌区域（无边框，直接显示）
        self.settingStack = QtWidgets.QStackedWidget()
        self.settingStack.setObjectName("settingStack")
        self.settingStack.setStyleSheet("QStackedWidget { border: none; background: transparent; }")
        projectPageLayout.addWidget(self.settingStack, 1)  # 占据主要空间

        # 保留设定内容按钮（隐藏，供其他代码引用）
        self.pushButton_ShowSettingDetail = QtWidgets.QPushButton("设定内容")
        self.pushButton_ShowSettingDetail.setObjectName("pushButton_ShowSettingDetail")
        self.pushButton_ShowSettingDetail.setVisible(False)

        # 试验控制卡片
        testCard = QtWidgets.QWidget()
        testCard.setObjectName("card")
        testCard.setStyleSheet(_cardStyle)
        testLayout = QtWidgets.QVBoxLayout(testCard)
        testLayout.setContentsMargins(16, 12, 16, 12)
        testLayout.setSpacing(10)
        testBtnLayout = QtWidgets.QHBoxLayout()
        testBtnLayout.setSpacing(10)
        self.pushButton_StartTest = QtWidgets.QPushButton("开始试验")
        self.pushButton_StartTest.setObjectName("pushButton_StartTest")
        testBtnLayout.addWidget(self.pushButton_StartTest)
        self.pushButton_StopTest = QtWidgets.QPushButton("暂停试验")
        self.pushButton_StopTest.setObjectName("pushButton_StopTest")
        self.pushButton_StopTest.setVisible(False)
        testBtnLayout.addWidget(self.pushButton_StopTest)
        self.pushButton_ConTest = QtWidgets.QPushButton("继续试验")
        self.pushButton_ConTest.setObjectName("pushButton_ConTest")
        self.pushButton_ConTest.setVisible(False)
        self.pushButton_ConTest.setToolTip(
            "本项试验结束后若勾选了「后续试验暂停」，改完逆变器/上位机后点此继续下一项。"
        )
        self.pushButton_ConTest.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.SUCCESS}; color: white; border: none;
                border-radius: 8px; padding: 8px 18px; font-size: 14px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {theme.SUCCESS_HOVER}; }}
        """)
        testBtnLayout.addWidget(self.pushButton_ConTest)
        self.pushButton_EndTest = QtWidgets.QPushButton("结束试验")
        self.pushButton_EndTest.setObjectName("pushButton_EndTest")
        self.pushButton_EndTest.setToolTip(
            "结束当前试验：停止流程，并按规则关闭电源输出。"
        )
        testBtnLayout.addWidget(self.pushButton_EndTest)
        self.pushButton_ShowMultiSettingDetail = QtWidgets.QPushButton("测试追加")
        self.pushButton_ShowMultiSettingDetail.setObjectName("pushButton_ShowMultiSettingDetail")
        self.pushButton_ShowMultiSettingDetail.setVisible(False)
        self.pushButton_ShowMultiSettingDetail.setStyleSheet("""
            QPushButton { background-color: #8b5cf6; color: white; border: none; border-radius: 4px; padding: 8px 16px; font-size: 13px; }
            QPushButton:hover { background-color: #7c3aed; }
        """)
        testBtnLayout.addWidget(self.pushButton_ShowMultiSettingDetail)
        testLayout.addLayout(testBtnLayout)
        self.btn_test = QtWidgets.QPushButton("test")
        self.btn_test.setObjectName("btn_test")
        self.btn_test.setFixedWidth(60)
        self.btn_test.setVisible(False)  # 隐藏测试按钮
        testLayout.addWidget(self.btn_test, 0, QtCore.Qt.AlignLeft)
        projectPageLayout.addWidget(testCard)

        # 项目日志
        logLabel = QtWidgets.QLabel("操作日志:")
        logLabel.setStyleSheet("font-size: 12px; color: #6b7280; background: transparent;")
        projectPageLayout.addWidget(logLabel)
        self.textEdit_ReturnMessage = QtWidgets.QTextEdit()
        self.textEdit_ReturnMessage.setObjectName("textEdit_ReturnMessage")
        self.textEdit_ReturnMessage.setReadOnly(True)
        self.textEdit_ReturnMessage.setStyleSheet(_logStyle)
        self.textEdit_ReturnMessage.setMinimumHeight(100)
        self.textEdit_ReturnMessage.setMaximumHeight(160)
        projectPageLayout.addWidget(self.textEdit_ReturnMessage, 0)
        self.pushButton_ClearMessage = QtWidgets.QPushButton("清空消息")
        self.pushButton_ClearMessage.setObjectName("pushButton_ClearMessage")
        self.pushButton_ClearMessage.setFixedWidth(90)
        self.pushButton_ClearMessage.setStyleSheet(f"""
            QPushButton {{ background-color: #475569; color: white; border: none; border-radius: 8px; }}
            QPushButton:hover {{ background-color: #334155; }}
        """)
        projectPageLayout.addWidget(self.pushButton_ClearMessage, 0, QtCore.Qt.AlignRight)

        self.stackedWidget.addWidget(projectPage)

        # ── 页面 10: 命令文件（嵌入 FileManagerDialog 内容） ──
        import os as _os
        from dialogs.DialogFileManager import FileListWidget
        cmdPage = QtWidgets.QWidget()
        cmdPage.setStyleSheet(_pageStyle)
        cmdPageLayout = QtWidgets.QVBoxLayout(cmdPage)
        cmdPageLayout.setContentsMargins(24, 16, 24, 16)
        cmdPageLayout.setSpacing(12)
        cmdTitle = QtWidgets.QLabel("命令文件")
        cmdTitle.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {theme.INK}; background: transparent;"
        )
        cmdPageLayout.addWidget(cmdTitle)
        _cmdTabs = QtWidgets.QTabWidget()
        _cmd_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                 "..", "command_save_files", "command_data")
        _cmdTabs.addTab(FileListWidget(directory=_cmd_dir,
                                        file_filter=('*.csv', '*.xlsx'),
                                        preview_type='csv'), "自动化命令")
        _dew_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                 "..", "command_save_files", "dewetron_data")
        _cmdTabs.addTab(FileListWidget(directory=_dew_dir,
                                        file_filter=('*.xml',),
                                        preview_type='xml'), "DEWETRON 配置")
        cmdPageLayout.addWidget(_cmdTabs)
        self.stackedWidget.addWidget(cmdPage)

        # ── 页面 11: 测试进度（从项目配置拆出，独立全页展示）──
        progressPage = QtWidgets.QWidget()
        progressPage.setStyleSheet(_pageStyle)
        progressPageLayout = QtWidgets.QVBoxLayout(progressPage)
        progressPageLayout.setContentsMargins(24, 16, 24, 16)
        progressPageLayout.setSpacing(12)

        progressTitle = QtWidgets.QLabel("测试进度")
        progressTitle.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {theme.INK}; background: transparent;"
        )
        progressPageLayout.addWidget(progressTitle)

        progressCard = QtWidgets.QWidget()
        progressCard.setObjectName("card")
        progressCard.setStyleSheet(_cardStyle)
        progressLayout = QtWidgets.QVBoxLayout(progressCard)
        progressLayout.setContentsMargins(16, 14, 16, 14)
        progressLayout.setSpacing(10)

        self.label_run_progress = QtWidgets.QLabel("试验进度：未开始")
        self.label_run_progress.setObjectName("label_run_progress")
        self.label_run_progress.setWordWrap(True)
        self.label_run_progress.setMinimumHeight(96)
        self.label_run_progress.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.label_run_progress.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {theme.INK}; background: transparent;"
        )
        progressLayout.addWidget(self.label_run_progress)

        self.label_operator_pause = QtWidgets.QLabel("")
        self.label_operator_pause.setObjectName("label_operator_pause")
        self.label_operator_pause.setWordWrap(True)
        self.label_operator_pause.setVisible(False)
        self.label_operator_pause.setStyleSheet(
            "QLabel { color: #92400e; background: #fef3c7; border: 1px solid #f59e0b; "
            "border-radius: 8px; padding: 10px 12px; font-size: 13px; font-weight: 700; }"
        )
        progressLayout.addWidget(self.label_operator_pause)

        self.progressBar_run = QtWidgets.QProgressBar()
        self.progressBar_run.setObjectName("progressBar_run")
        self.progressBar_run.setRange(0, 100)
        self.progressBar_run.setValue(0)
        self.progressBar_run.setFixedHeight(22)
        self.progressBar_run.setFormat("%p%")
        self.progressBar_run.setToolTip("进度百分比；运行中会显示估算剩余时间")
        self.progressBar_run.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {theme.LINE}; border-radius: 8px; background: #eef2f7;
                text-align: center; font-size: 12px; color: {theme.INK};
            }}
            QProgressBar::chunk {{ background-color: {theme.ACCENT}; border-radius: 7px; }}
        """)
        progressLayout.addWidget(self.progressBar_run)

        queueTitle = QtWidgets.QLabel("试验队列（多项追加）")
        queueTitle.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {theme.INK}; background: transparent;"
        )
        progressLayout.addWidget(queueTitle)

        self.tableWidget_test_queue = QtWidgets.QTableWidget(0, 5)
        self.tableWidget_test_queue.setObjectName("tableWidget_test_queue")
        self.tableWidget_test_queue.setHorizontalHeaderLabels(
            ["序号", "试验项目", "状态", "预估时长", "结束后暂停"]
        )
        self.tableWidget_test_queue.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_test_queue.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents
        )
        self.tableWidget_test_queue.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch
        )
        self.tableWidget_test_queue.horizontalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents
        )
        self.tableWidget_test_queue.verticalHeader().setVisible(False)
        self.tableWidget_test_queue.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_test_queue.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget_test_queue.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget_test_queue.setAlternatingRowColors(True)
        self.tableWidget_test_queue.setMaximumHeight(220)
        self.tableWidget_test_queue.setStyleSheet("""
            QTableWidget { background: #ffffff; border: 1px solid #e2e8f0; font-size: 13px; }
            QHeaderView::section { background: #f1f5f9; padding: 6px; border: none;
                                   border-bottom: 1px solid #e2e8f0; font-weight: bold; }
        """)
        progressLayout.addWidget(self.tableWidget_test_queue)

        recTitle = QtWidgets.QLabel("录波轮次")
        recTitle.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {theme.INK}; background: transparent;"
        )
        progressLayout.addWidget(recTitle)

        self.tableWidget_run_progress = QtWidgets.QTableWidget(0, 4)
        self.tableWidget_run_progress.setObjectName("tableWidget_run_progress")
        self.tableWidget_run_progress.setHorizontalHeaderLabels(
            ["轮次", "保存文件名", "状态", "备注"]
        )
        self.tableWidget_run_progress.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_run_progress.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents
        )
        self.tableWidget_run_progress.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch
        )
        self.tableWidget_run_progress.horizontalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents
        )
        self.tableWidget_run_progress.verticalHeader().setVisible(False)
        self.tableWidget_run_progress.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_run_progress.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget_run_progress.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget_run_progress.setAlternatingRowColors(True)
        self.tableWidget_run_progress.setStyleSheet("""
            QTableWidget { background: #ffffff; border: 1px solid #e2e8f0; font-size: 13px; }
            QHeaderView::section { background: #f1f5f9; padding: 6px; border: none;
                                   border-bottom: 1px solid #e2e8f0; font-weight: bold; }
        """)
        progressLayout.addWidget(self.tableWidget_run_progress, 1)
        progressPageLayout.addWidget(progressCard, 1)
        self.stackedWidget.addWidget(progressPage)

        # ── 页面 12: IOT Agent 日志 ──
        from components.iot_agent_log_panel import IotAgentLogPage

        self.iotAgentLogPage = IotAgentLogPage()
        self.stackedWidget.addWidget(self.iotAgentLogPage)

        # ── 页面 13: 数据测量（不改前面页码）──
        from components.live_measure_page import LiveMeasurePage

        self.liveMeasurePage = LiveMeasurePage()
        self.stackedWidget.addWidget(self.liveMeasurePage)

        rightLayout.addWidget(self.stackedWidget, 1)
        mainLayout.addWidget(rightPanel, 1)

        # ── 隐藏不需要的原始 label ──
        self.label = QtWidgets.QLabel()
        self.label.setObjectName("label")
        self.label.hide()
        self.label_2 = QtWidgets.QLabel()
        self.label_2.setObjectName("label_2")
        self.label_2.hide()
        self.label_4 = QtWidgets.QLabel()
        self.label_4.setObjectName("label_4")
        self.label_4.hide()
        self.label_5 = QtWidgets.QLabel()
        self.label_5.setObjectName("label_5")
        self.label_5.hide()
        self.label_6 = QtWidgets.QLabel()
        self.label_6.setObjectName("label_6")
        self.label_6.hide()
        self.label_7 = QtWidgets.QLabel()
        self.label_7.setObjectName("label_7")
        self.label_7.hide()
        self.label_8 = QtWidgets.QLabel()
        self.label_8.setObjectName("label_8")
        self.label_8.hide()
        self.label_9 = QtWidgets.QLabel()
        self.label_9.setObjectName("label_9")
        self.label_9.hide()
        self.label_10 = QtWidgets.QLabel()
        self.label_10.setObjectName("label_10")
        self.label_10.hide()
        self.label_11 = QtWidgets.QLabel()
        self.label_11.setObjectName("label_11")
        self.label_11.hide()
        self.label_12 = QtWidgets.QLabel()
        self.label_12.setObjectName("label_12")
        self.label_12.hide()

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        try:
            from components.extra_dc_pages import install_extra_dc_pages

            install_extra_dc_pages(self)
        except Exception as exc:
            print("[直流路] 左侧菜单页安装失败: %s" % exc, flush=True)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(
            _translate("Dialog", "自动化测试  " + getattr(self, "_app_version_text", ""))
        )
        self.pushButton_ConnectEQUAC.setText(_translate("Dialog", "连接设备"))
        self.pushButton_ConnectEQUDC1.setText(_translate("Dialog", "连接设备"))
        self.pushButton_ConnectEQUDC2.setText(_translate("Dialog", "连接设备"))
        self.pushButton_ConnectEQUDC3.setText(_translate("Dialog", "连接设备"))
        self.pushButton_ConnectEQUDC4.setText(_translate("Dialog", "连接设备"))
        self.pushButton_ConnectEQUDL850.setText(_translate("Dialog", "连接设备"))
        self.pushButton_ConnectEQUWT3000.setText(_translate("Dialog", "连接设备"))
        self.pushButton_ConnectEQUDEWETRON.setText(_translate("Dialog", "连接设备"))
        self.pushButton_SetACOptions.setText(_translate("Dialog", "设定交流电源"))
        self.pushButton_SetDC1Options.setText(_translate("Dialog", "设定直流电源"))
        self.pushButton_SetDC2Options.setText(_translate("Dialog", "设定直流电源"))
        self.pushButton_SetDC3Options.setText(_translate("Dialog", "设定直流电源"))
        self.pushButton_SetDC4Options.setText(_translate("Dialog", "设定直流电源"))
        self.pushButton_SetDL850Options.setText(_translate("Dialog", "设定DL850"))
        self.pushButton_SetWT3000Options.setText(_translate("Dialog", "设定WT3000"))
        self.pushButton_ShowSettingDetail.setText(_translate("Dialog", "设定内容"))
        self.pushButton_ShowMultiSettingDetail.setText(_translate("Dialog", "测试追加"))
        self.pushButton_StartTest.setText(_translate("Dialog", "开始试验"))
        self.pushButton_StopTest.setText(_translate("Dialog", "暂停试验"))
        self.pushButton_EndTest.setText(_translate("Dialog", "结束试验"))
        self.pushButton_ConTest.setText(_translate("Dialog", "继续试验"))
        self.pushButton_ClearMessage.setText(_translate("Dialog", "清空消息"))
        self.btn_test.setText(_translate("Dialog", "test"))
