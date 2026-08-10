# -*- coding: utf-8 -*-

# V1.1 工业风格侧边栏布局
# 手动编写（非 pyuic5 生成），保留所有原始 widget 名称以兼容 SCPITestWave.py

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setEnabled(True)
        Dialog.setFixedSize(1600, 900)
        import os as _os_icon
        _icon_path = _os_icon.path.join(_os_icon.path.dirname(_os_icon.path.abspath(__file__)), "logo.jpg")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)

        # ── 全局样式 ──
        Dialog.setStyleSheet("""
            QMainWindow { background-color: #e2e5ea; }
            QWidget#centralWidget { background-color: #e2e5ea; }
        """)

        # ── 主布局 ──
        centralWidget = QtWidgets.QWidget(Dialog)
        Dialog.setCentralWidget(centralWidget)
        mainLayout = QtWidgets.QHBoxLayout(centralWidget)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # ══════════════════════════════════════
        # 左侧边栏 — 两级可折叠菜单
        # ══════════════════════════════════════
        sidebar = QtWidgets.QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QWidget#sidebar {
                background-color: #e2e5ea;
                border-right: 1px solid #e2e8f0;
            }
        """)
        sidebar.setObjectName("sidebar")
        sidebarLayout = QtWidgets.QVBoxLayout(sidebar)
        sidebarLayout.setContentsMargins(0, 0, 0, 0)
        sidebarLayout.setSpacing(0)

        # ── 样式常量 ──
        _HEADER_STYLE = """
            QPushButton {
                background-color: #e5e7eb; color: #374151; border: none;
                border-bottom: 1px solid #d1d5db;
                text-align: left; padding: 10px 12px;
                font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { background-color: #d1d5db; color: #1f2937; }
        """
        _SUBHEADER_STYLE = """
            QPushButton {
                background-color: #e8eaee; color: #4b5563; border: none;
                border-bottom: 1px solid #d8dde5;
                text-align: left; padding: 7px 8px 7px 16px;
                font-size: 11px; font-weight: bold;
            }
            QPushButton:hover { background-color: #dbe0e8; color: #1f2937; }
        """
        _ITEM_STYLE = """
            QPushButton {
                background-color: #e2e5ea; color: #374151; border: none;
                border-left: 3px solid transparent;
                text-align: left; padding: 9px 12px 9px 20px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #e5e7eb; color: #1f2937; }
        """
        _ITEM_ACTIVE_STYLE = """
            QPushButton {
                background-color: #dbeafe; color: #1d4ed8; border: none;
                border-left: 3px solid #2563eb;
                text-align: left; padding: 9px 12px 9px 20px;
                font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background-color: #bfdbfe; color: #1e40af; }
        """
        _NESTED_ITEM_STYLE = """
            QPushButton {
                background-color: #e2e5ea; color: #374151; border: none;
                border-left: 3px solid transparent;
                text-align: left; padding: 8px 10px 8px 28px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #e5e7eb; color: #1f2937; }
        """
        _NESTED_ITEM_ACTIVE_STYLE = """
            QPushButton {
                background-color: #dbeafe; color: #1d4ed8; border: none;
                border-left: 3px solid #2563eb;
                text-align: left; padding: 8px 10px 8px 28px;
                font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { background-color: #bfdbfe; color: #1e40af; }
        """

        # 侧栏选中态（首页/设备/Auto_Test/其他 共用）
        self._nav_buttons = []
        self._nav_by_key = {}
        self._auto_test_categories = {}

        def _set_nav_active(btn):
            if btn is None:
                return
            for b in self._nav_buttons:
                base = getattr(b, "_nav_base_style", _ITEM_STYLE)
                if b is btn:
                    b.setStyleSheet(getattr(b, "_nav_active_style", _ITEM_ACTIVE_STYLE))
                else:
                    b.setStyleSheet(base)

        def _register_nav(btn, key=None, base_style=None, active_style=None):
            btn._nav_base_style = base_style or _ITEM_STYLE
            btn._nav_active_style = active_style or _ITEM_ACTIVE_STYLE
            self._nav_buttons.append(btn)
            if key:
                self._nav_by_key[key] = btn
            return btn

        self.set_nav_active = _set_nav_active
        self.set_nav_active_by_key = lambda key: _set_nav_active(self._nav_by_key.get(key))

        # ── 辅助函数 ──
        def _make_header(text, icon_name=None):
            btn = QtWidgets.QPushButton(f"  ▾  {text}")
            btn.setStyleSheet(_HEADER_STYLE)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            if icon_name:
                _icon = btn.style().standardIcon(getattr(QtWidgets.QStyle, icon_name))
                btn.setIcon(_icon)
                btn.setIconSize(QtCore.QSize(16, 16))
            return btn

        def _make_item(text, page_index, *, key=None):
            btn = QtWidgets.QPushButton(f"      {text}")
            btn.setStyleSheet(_ITEM_STYLE)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            _register_nav(btn, key=key or text)

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

        def _bind_toggle(header, container, default_text, *, style=_HEADER_STYLE, indent="  "):
            def toggle():
                vis = container.isVisible()
                container.setVisible(not vis)
                arrow = "▾" if not vis else "▸"
                header.setText(f"{indent}{arrow}  {default_text}")
            header.clicked.connect(toggle)
            header.setStyleSheet(style)

        # ══════════════════════════════════════
        # 可滚动菜单区
        # ══════════════════════════════════════
        _scrollArea = QtWidgets.QScrollArea()
        _scrollArea.setWidgetResizable(True)
        _scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        _scrollArea.setStyleSheet("""
            QScrollArea { border: none; background: #e2e5ea; }
            QScrollBar:vertical {
                background: #e2e5ea; width: 8px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #c1c9d2; border-radius: 4px; min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #9ca3af; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        _scrollContent = QtWidgets.QWidget()
        _scrollContent.setStyleSheet("background: #e2e5ea;")
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

        # ── 一级菜单: 设备管理 ──
        _sec_dev = _make_header("设备管理", "SP_ComputerIcon")
        _scrollLayout.addWidget(_sec_dev)

        _dev_container, _dev_layout = _make_container()
        for i, name in enumerate(["交流电源", "直流电源1", "直流电源2", "直流电源3",
                                    "直流电源4", "DL850", "WT3000", "DEWETRON"]):
            _dev_layout.addWidget(_make_item(name, i + 1, key=name))
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
            header.setStyleSheet(_SUBHEADER_STYLE)
            header.setCursor(QtCore.Qt.PointingHandCursor)
            cat_w, cat_lay = _make_container()
            _auto_layout.addWidget(header)
            _auto_layout.addWidget(cat_w)
            _bind_toggle(header, cat_w, category, style=_SUBHEADER_STYLE, indent="    ")
            self._auto_test_categories[category] = {
                "header": header,
                "container": cat_w,
                "layout": cat_lay,
            }
            return cat_lay

        def _add_auto_test_item(text, page_index=9, setting_key=None, category=None):
            parent_layout = _auto_layout
            base_style = _ITEM_STYLE
            active_style = _ITEM_ACTIVE_STYLE
            label = f"      {text}"
            if category:
                parent_layout = _add_auto_test_category(category)
                base_style = _NESTED_ITEM_STYLE
                active_style = _NESTED_ITEM_ACTIVE_STYLE
                label = f"        {text}"

            item = QtWidgets.QPushButton(label)
            item.setStyleSheet(base_style)
            item.setCursor(QtCore.Qt.PointingHandCursor)
            tip = f"{category} / {text}" if category else text
            item.setToolTip(tip)
            _register_nav(item, key=text, base_style=base_style, active_style=active_style)

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

        # ══════════════════════════════════════
        # 底部固定区（分隔线 + 刷新按钮）
        # ══════════════════════════════════════
        _sep = QtWidgets.QFrame()
        _sep.setFrameShape(QtWidgets.QFrame.HLine)
        _sep.setStyleSheet("color: #d1d5db; max-height: 1px; margin: 0 12px;")
        sidebarLayout.addWidget(_sep)

        bottomBar = QtWidgets.QWidget()
        bottomBar.setStyleSheet("background: transparent;")
        bottomLayout = QtWidgets.QHBoxLayout(bottomBar)
        bottomLayout.setContentsMargins(16, 8, 16, 12)
        bottomLayout.setSpacing(8)

        self.pushButton_ReConnectEQU = QtWidgets.QPushButton()
        self.pushButton_ReConnectEQU.setFixedSize(36, 36)
        self.pushButton_ReConnectEQU.setToolTip("刷新设备")
        self.pushButton_ReConnectEQU.setObjectName("pushButton_ReConnectEQU")
        _refresh_icon = self.pushButton_ReConnectEQU.style().standardIcon(
            QtWidgets.QStyle.SP_BrowserReload)
        self.pushButton_ReConnectEQU.setIcon(_refresh_icon)
        self.pushButton_ReConnectEQU.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_ReConnectEQU.setStyleSheet("""
            QPushButton {
                background-color: #e5e7eb; color: #374151; border: 1px solid #d1d5db;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #d1d5db; color: #1f2937; }
        """)
        bottomLayout.addWidget(self.pushButton_ReConnectEQU)

        sidebarLayout.addWidget(bottomBar)
        mainLayout.addWidget(sidebar)

        # ══════════════════════════════════════
        # 右侧内容区
        # ══════════════════════════════════════
        rightPanel = QtWidgets.QWidget()
        rightPanel.setStyleSheet("background-color: #e2e5ea;")
        rightLayout = QtWidgets.QVBoxLayout(rightPanel)
        rightLayout.setContentsMargins(0, 0, 0, 0)
        rightLayout.setSpacing(0)

        # -- QStackedWidget --
        self.stackedWidget = QtWidgets.QStackedWidget()
        self.stackedWidget.setStyleSheet("""
            QStackedWidget { background-color: #e2e5ea; border: none; }
        """)

        _pageStyle = """
            QWidget { background-color: #e2e5ea; }
            QLabel { color: #374151; font-size: 13px; background: transparent; }
            QPushButton {
                background-color: #3b82f6; color: white; border: none;
                border-radius: 6px; padding: 8px 16px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2563eb; }
            QPushButton:pressed { background-color: #1d4ed8; }
            QPushButton:disabled { background-color: #94a3b8; color: #e2e8f0; }
            QComboBox {
                background-color: #ffffff; border: 1px solid #9ca3af; border-radius: 4px;
                padding: 4px 24px 4px 8px; font-size: 13px; color: #1e293b;
            }
            QComboBox:hover { border-color: #3b82f6; }
            QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: center right;
                width: 24px; border: none; }
            QComboBox::down-arrow { image: none; border-left: 5px solid transparent;
                border-right: 5px solid transparent; border-top: 6px solid #374151; }
            QComboBox QAbstractItemView {
                background-color: #ffffff; color: #111827;
                border: 2px solid #3b82f6; selection-background-color: #3b82f6;
                selection-color: #ffffff; outline: none;
            }
            QComboBox QAbstractItemView::item { padding: 6px 12px; min-height: 28px;
                border-bottom: 1px solid #e5e7eb; }
        """
        _cardStyle = """
            QWidget#card {
                background-color: #eaecf0; border: 1px solid #d5d8de;
                border-radius: 10px; padding: 16px;
            }
        """
        _logStyle = """
            QTextEdit {
                background-color: #1e293b; color: #e2e8f0;
                border: 1px solid #334155; border-radius: 6px;
                font-family: Consolas, monospace; font-size: 12px; padding: 8px;
            }
        """

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
            lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b; background: transparent;")
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
            connectBtn.setFixedWidth(90)
            setattr(self, connect_btn_name, connectBtn)

            setBtn = None
            if set_btn_name:
                setBtn = QtWidgets.QPushButton("设定")
                setBtn.setObjectName(set_btn_name)
                setBtn.setFixedWidth(90)
                setBtn.setStyleSheet("""
                    QPushButton { background-color: #10b981; color: white; }
                    QPushButton:hover { background-color: #059669; }
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
                log_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b; background: transparent;")
                layout.addWidget(log_label)

                log_edit = QtWidgets.QTextEdit()
                log_edit.setObjectName(f"log_{combo_name}")
                log_edit.setReadOnly(True)
                log_edit.setMaximumHeight(120)
                log_edit.setStyleSheet(
                    "QTextEdit { background-color: #1e293b; color: #a0aec0; "
                    "border: 1px solid #4a5568; border-radius: 4px; "
                    "font-family: Consolas; font-size: 12px; padding: 4px; }"
                )
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

        homeTitle = QtWidgets.QLabel("首页")
        homeTitle.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b; background: transparent;")
        homeLayout.addWidget(homeTitle)

        # -- 设备状态网格 (2x4，8个设备写死) --
        _devGridTitle = QtWidgets.QLabel("设备状态")
        _devGridTitle.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b; background: transparent;")
        homeLayout.addWidget(_devGridTitle)

        _CARD_QSS = """
            QWidget#deviceCard {
                background-color: #eaecf0; border: 1px solid #d5d8de;
                border-radius: 8px;
            }
            QWidget#deviceCard:hover {
                background-color: #eff6ff; border-color: #3b82f6;
            }
        """
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
            _nl.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b; background: transparent;")
            _tr.addWidget(_nl)
            _tr.addStretch(1)
            _dot = QtWidgets.QLabel()
            _dot.setFixedSize(10, 10)
            _dot.setStyleSheet("background-color: #ef4444; border-radius: 5px;")
            _tr.addWidget(_dot)
            _cl.addLayout(_tr)
            # 第二行：资源地址
            _rl = QtWidgets.QLabel("未配置")
            _rl.setStyleSheet("font-size: 10px; color: #9ca3af; background: transparent;")
            _rl.setWordWrap(True)
            _cl.addWidget(_rl)
            # 第三行：上次连接时间
            _tl = QtWidgets.QLabel("")
            _tl.setStyleSheet("font-size: 9px; color: #9ca3af; background: transparent;")
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
        _testCardTitle.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b; background: transparent;")
        _testCardLayout.addWidget(_testCardTitle)
        self.home_project_name = QtWidgets.QLabel("暂无测试项目")
        self.home_project_name.setStyleSheet("font-size: 13px; color: #6b7280; background: transparent;")
        _testCardLayout.addWidget(self.home_project_name)
        _statusRow = QtWidgets.QHBoxLayout()
        _statusRow.setSpacing(12)
        _statusLabel = QtWidgets.QLabel("状态:")
        _statusLabel.setStyleSheet("font-size: 12px; color: #6b7280; background: transparent;")
        _statusRow.addWidget(_statusLabel)
        self.home_status = QtWidgets.QLabel("未开始")
        self.home_status.setStyleSheet("font-size: 12px; font-weight: bold; color: #9ca3af; background: transparent;")
        _statusRow.addWidget(self.home_status)
        _statusRow.addStretch(1)
        _testCardLayout.addLayout(_statusRow)
        self.home_progress = QtWidgets.QProgressBar()
        self.home_progress.setRange(0, 100)
        self.home_progress.setValue(0)
        self.home_progress.setFixedHeight(18)
        self.home_progress.setStyleSheet("""
            QProgressBar { border: 1px solid #d1d5db; border-radius: 4px; background: #dde0e5; text-align: center; font-size: 11px; }
            QProgressBar::chunk { background-color: #3b82f6; border-radius: 3px; }
        """)
        _testCardLayout.addWidget(self.home_progress)
        _timeRow = QtWidgets.QHBoxLayout()
        _timeRow.setSpacing(24)
        _startLabel = QtWidgets.QLabel("开始时间:")
        _startLabel.setStyleSheet("font-size: 12px; color: #6b7280; background: transparent;")
        _timeRow.addWidget(_startLabel)
        self.home_start_time = QtWidgets.QLabel("--")
        self.home_start_time.setStyleSheet("font-size: 12px; color: #6b7280; background: transparent;")
        _timeRow.addWidget(self.home_start_time)
        _endLabel = QtWidgets.QLabel("预估结束:")
        _endLabel.setStyleSheet("font-size: 12px; color: #6b7280; background: transparent;")
        _timeRow.addWidget(_endLabel)
        self.home_estimated_end_time = QtWidgets.QLabel("--")
        self.home_estimated_end_time.setStyleSheet("font-size: 12px; color: #6b7280; background: transparent;")
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
            # 更新设备卡片
            for _dev in _data.get("devices", []):
                _name = _dev["name"]
                if _name in self._home_dots:
                    _color = "#22c55e" if _dev.get("connected") else "#ef4444"
                    self._home_dots[_name].setStyleSheet(
                        f"background-color: {_color}; border-radius: 5px;")
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
                self.home_project_name.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b; background: transparent;")
                _status = _proj.get("status", "未开始")
                _color_map = {"未开始": "#9ca3af", "进行中": "#3b82f6", "已结束": "#22c55e"}
                self.home_status.setText(_status)
                self.home_status.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {_color_map.get(_status, '#9ca3af')}; background: transparent;")
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

        projTitle = QtWidgets.QLabel("项目配置")
        projTitle.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b; background: transparent;")
        projectPageLayout.addWidget(projTitle)

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
        self.pushButton_ConTest = QtWidgets.QPushButton("继续运行试验")
        self.pushButton_ConTest.setObjectName("pushButton_ConTest")
        self.pushButton_ConTest.setVisible(False)
        testBtnLayout.addWidget(self.pushButton_ConTest)
        self.pushButton_EndTest = QtWidgets.QPushButton("结束试验")
        self.pushButton_EndTest.setObjectName("pushButton_EndTest")
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
        self.pushButton_ClearMessage.setStyleSheet("""
            QPushButton { background-color: #6b7280; color: white; }
            QPushButton:hover { background-color: #4b5563; }
        """)
        projectPageLayout.addWidget(self.pushButton_ClearMessage, 0, QtCore.Qt.AlignRight)

        self.stackedWidget.addWidget(projectPage)

        # ── 页面 10: 命令文件（嵌入 FileManagerDialog 内容） ──
        import os as _os
        from DialogFileManager import FileListWidget
        cmdPage = QtWidgets.QWidget()
        cmdPage.setStyleSheet(_pageStyle)
        cmdPageLayout = QtWidgets.QVBoxLayout(cmdPage)
        cmdPageLayout.setContentsMargins(24, 16, 24, 16)
        cmdPageLayout.setSpacing(12)
        cmdTitle = QtWidgets.QLabel("命令文件")
        cmdTitle.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b; background: transparent;")
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
            "font-size: 16px; font-weight: bold; color: #1e293b; background: transparent;"
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
        self.label_run_progress.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #1e293b; background: transparent;"
        )
        progressLayout.addWidget(self.label_run_progress)

        self.progressBar_run = QtWidgets.QProgressBar()
        self.progressBar_run.setObjectName("progressBar_run")
        self.progressBar_run.setRange(0, 100)
        self.progressBar_run.setValue(0)
        self.progressBar_run.setFixedHeight(22)
        self.progressBar_run.setFormat("%p%")
        self.progressBar_run.setStyleSheet("""
            QProgressBar { border: 1px solid #d1d5db; border-radius: 4px; background: #dde0e5;
                           text-align: center; font-size: 12px; }
            QProgressBar::chunk { background-color: #3b82f6; border-radius: 3px; }
        """)
        progressLayout.addWidget(self.progressBar_run)

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

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "自动化测试"))
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
        self.pushButton_ConTest.setText(_translate("Dialog", "继续运行试验"))
        self.pushButton_ClearMessage.setText(_translate("Dialog", "清空消息"))
        self.btn_test.setText(_translate("Dialog", "test"))
