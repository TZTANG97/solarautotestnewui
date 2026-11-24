# -*- coding: utf-8 -*-
"""设备管理菜单里按需增加直流电源页。外观与接线逻辑对齐直流 1～4。"""
from __future__ import annotations

from PyQt5 import QtCore, QtWidgets

from components import ui_theme as theme
from utils.dc_channels import add_channel, channel_numbers, remove_channel


def install_extra_dc_pages(ui) -> None:
    """在「直流电源4」和 DL850 之间放「添加直流电源」，已有的第 5 路起补上菜单和配置页。"""
    if getattr(ui, "_extra_dc_installed", False):
        return
    layout = getattr(ui, "_dev_menu_layout", None)
    anchor = getattr(ui, "_dl850_nav_item", None)
    if layout is None or anchor is None or not hasattr(ui, "stackedWidget"):
        return
    ui._extra_dc_installed = True
    ui._extra_dc_pages = {}
    names = list(getattr(ui, "_extra_dc_combo_names", []) or [])
    ui._extra_dc_combo_names = names

    add_btn = QtWidgets.QPushButton("      ＋ 添加直流电源")
    add_btn.setObjectName("pushButton_AddDcDevicePage")
    add_btn.setCursor(QtCore.Qt.PointingHandCursor)
    base = getattr(anchor, "_nav_base_style", None) or theme.ITEM_STYLE
    add_btn.setStyleSheet(base)
    add_btn.clicked.connect(lambda: _add_next(ui))
    layout.insertWidget(_layout_index(layout, anchor), add_btn)
    ui._extra_dc_add_btn = add_btn

    for n in channel_numbers():
        if n > 4:
            _ensure_page(ui, n)


def _add_next(ui) -> None:
    n = add_channel()
    index = _ensure_page(ui, n)
    try:
        from components.dc_channel_rows import refresh_known_uis

        refresh_known_uis()
    except Exception as exc:
        print("[直流路] 试验页刷新失败: %s" % exc, flush=True)
    ui.stackedWidget.setCurrentIndex(index)
    activate = getattr(ui, "set_nav_active_by_key", None)
    if callable(activate):
        activate("直流电源%d" % n)


def _remove_page(ui, channel: int) -> None:
    channel = int(channel)
    if channel <= 4:
        return
    reply = QtWidgets.QMessageBox.question(
        None,
        "删除直流电源",
        "确定删除直流电源%d？试验页里这一路也会隐藏。" % channel,
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.No,
    )
    if reply != QtWidgets.QMessageBox.Yes:
        return
    try:
        remove_channel(channel)
    except ValueError as exc:
        QtWidgets.QMessageBox.warning(None, "无法删除", str(exc))
        return
    pages = getattr(ui, "_extra_dc_pages", {}) or {}
    info = pages.pop(channel, None)
    if info:
        item = info.get("item")
        page = info.get("page")
        layout = getattr(ui, "_dev_menu_layout", None)
        # 先从侧栏导航表注销，再 deleteLater，避免选中态遍历已销毁按钮
        unreg = getattr(ui, "unregister_nav", None)
        if callable(unreg):
            try:
                unreg(btn=item, key="直流电源%d" % channel)
            except Exception:
                pass
        if layout is not None and item is not None:
            layout.removeWidget(item)
            item.hide()
            item.deleteLater()
        if page is not None and hasattr(ui, "stackedWidget"):
            ui.stackedWidget.removeWidget(page)
            page.hide()
            page.deleteLater()
        # 删页后 stacked 索引变化：刷新仍保留的额外路导航键与索引
        for n, meta in list(pages.items()):
            pg = meta.get("page")
            if pg is None or not hasattr(ui, "stackedWidget"):
                continue
            try:
                new_idx = ui.stackedWidget.indexOf(pg)
            except Exception:
                new_idx = -1
            if new_idx < 0:
                continue
            meta["index"] = new_idx
            nav = meta.get("item")
            if nav is not None:
                try:
                    nav.setProperty("page", new_idx)
                except RuntimeError:
                    continue
                # 重新绑定点击到新索引（旧闭包仍指向删除前的 page_index）
                try:
                    nav.clicked.disconnect()
                except Exception:
                    pass
                try:
                    key = "直流电源%d" % n

                    def _on_nav(_c=False, idx=new_idx, k=key, host=ui):
                        try:
                            host.stackedWidget.setCurrentIndex(idx)
                        except Exception:
                            return
                        activate_fn = getattr(host, "set_nav_active_by_key", None)
                        if callable(activate_fn):
                            try:
                                activate_fn(k)
                            except RuntimeError:
                                pass

                    nav.clicked.connect(_on_nav)
                except RuntimeError:
                    pass
    for attr in (
        "comboBox_DC%d" % channel,
        "pushButton_ConnectEQUDC%d" % channel,
        "pushButton_SetDC%dOptions" % channel,
        "uiDC%dSetting" % channel,
    ):
        if hasattr(ui, attr):
            try:
                delattr(ui, attr)
            except Exception:
                setattr(ui, attr, None)
    names = list(getattr(ui, "_extra_dc_combo_names", []) or [])
    ui._extra_dc_combo_names = [n for n in names if n != ("comboBox_DC%d" % channel)]
    try:
        from components.dc_channel_rows import refresh_known_uis

        refresh_known_uis()
    except Exception as exc:
        print("[直流路] 删除后刷新试验页失败: %s" % exc, flush=True)
    activate = getattr(ui, "set_nav_active_by_key", None)
    if callable(activate):
        try:
            activate("直流电源4")
        except RuntimeError:
            pass
    if hasattr(ui, "stackedWidget"):
        # 直流电源4 在固定页索引 5（0=首页，1=AC，2~5=DC1~4）
        try:
            ui.stackedWidget.setCurrentIndex(5)
        except Exception:
            pass


def _ensure_page(ui, channel: int) -> int:
    pages = ui._extra_dc_pages
    if channel in pages:
        return int(pages[channel]["index"])
    page, setting = _build_page(ui, channel)
    ui.stackedWidget.addWidget(page)
    index = ui.stackedWidget.count() - 1
    item = ui.make_nav_item("直流电源%d" % channel, index, key="直流电源%d" % channel)
    layout = ui._dev_menu_layout
    layout.insertWidget(_layout_index(layout, ui._extra_dc_add_btn), item)
    pages[channel] = {
        "page": page,
        "index": index,
        "item": item,
        "setting": setting,
    }
    setattr(ui, "uiDC%dSetting" % channel, setting)
    _wire_page(ui, channel, page, setting)
    _copy_interface_list(ui, channel)
    return index


def _build_page(ui, channel: int):
    """与 SCPI_Test._make_device_page(use_grid=True) + Dialog_DC*_Setting 嵌入一致。"""
    combo_name = "comboBox_DC%d" % channel
    connect_name = "pushButton_ConnectEQUDC%d" % channel
    set_name = "pushButton_SetDC%dOptions" % channel

    page = QtWidgets.QWidget()
    page.setStyleSheet(theme.PAGE_STYLE)
    layout = QtWidgets.QVBoxLayout(page)
    layout.setContentsMargins(24, 16, 24, 16)
    layout.setSpacing(12)

    title_row = QtWidgets.QHBoxLayout()
    title = QtWidgets.QLabel("直流电源%d" % channel)
    title.setStyleSheet(
        "font-size: 18px; font-weight: 700; color: %s; background: transparent;" % theme.INK
    )
    title_row.addWidget(title)
    title_row.addStretch(1)
    del_btn = QtWidgets.QPushButton("删除此直流电源")
    del_btn.setObjectName("pushButton_RemoveDC%d" % channel)
    del_btn.setCursor(QtCore.Qt.PointingHandCursor)
    del_btn.setStyleSheet(
        "QPushButton { color: #b91c1c; background: transparent; border: 1px solid #fca5a5;"
        " border-radius: 6px; padding: 4px 10px; }"
        "QPushButton:hover { background: #fef2f2; }"
    )
    del_btn.clicked.connect(lambda _c=False, ch=channel, host=ui: _remove_page(host, ch))
    title_row.addWidget(del_btn)
    layout.addLayout(title_row)

    combo = QtWidgets.QComboBox()
    combo.setObjectName(combo_name)
    combo.setEditable(True)
    combo.setMinimumWidth(200)
    setattr(ui, combo_name, combo)
    ui._extra_dc_combo_names.append(combo_name)

    connect_btn = QtWidgets.QPushButton("连接设备")
    connect_btn.setObjectName(connect_name)
    connect_btn.setMinimumWidth(theme.px(108))
    setattr(ui, connect_name, connect_btn)

    set_btn = QtWidgets.QPushButton("设定")
    set_btn.setObjectName(set_name)
    set_btn.setMinimumWidth(theme.px(100))
    set_btn.setStyleSheet(
        """
        QPushButton {{ background-color: {ok}; color: white; border: none;
            border-radius: 8px; font-weight: 700; padding: 6px 12px; }}
        QPushButton:hover {{ background-color: {hover}; }}
        """.format(
            ok=theme.SUCCESS, hover=theme.SUCCESS_HOVER
        )
    )
    setattr(ui, set_name, set_btn)

    grid_container = QtWidgets.QWidget()
    grid_container.setObjectName("_grid_container")
    grid_container.setStyleSheet("background: transparent;")
    QtWidgets.QGridLayout(grid_container).setContentsMargins(0, 0, 0, 0)
    setattr(page, "_grid_%s" % combo_name, grid_container)
    setattr(page, "_connect_widgets_%s" % combo_name, (combo, connect_btn, set_btn))
    layout.addWidget(grid_container, 1)

    setting = _make_dc_setting_dialog(channel)
    from setup.main_setup import MainSetup

    grid_rows = [
        {"title": "设备连接", "widgets": "__connect_clean__"},
        {
            "title": "参数设置（IV 四点）",
            "widgets": [
                "label",
                "textEdit_Vmp",
                "label_3",
                "textEdit_Voc",
                "label_2",
                "textEdit_Imp",
                "label_4",
                "textEdit_Isc",
            ],
        },
        {"title": "功率设置（功率%）", "widgets": ["label_5", "textEdit_PF", "lineEdit_2"]},
        {
            "title": "输出控制",
            "widgets": [
                "pushButton_SetDC%dON" % channel,
                "pushButton_SetDC%dOFF" % channel,
            ],
        },
        {"title": "下发 IV 曲线（已连接可反复下发）", "widgets": ["pushButton_SendMessage"]},
        {"title": "单条命令查询", "widgets": ["lineEdit", "pushButton_SendQueryMessage"]},
        {"title": "操作日志", "widgets": "__log_widget__"},
    ]
    MainSetup.embed_dialog_content(
        setting._dialog, page, combo_name, layout_rows=grid_rows
    )

    # 嵌入后控件在 page 树上，也挂到 setting 上方便 SCPI 路径按 ui_setting 取数。
    for name in (
        "textEdit_Vmp",
        "textEdit_Voc",
        "textEdit_Imp",
        "textEdit_Isc",
        "textEdit_PF",
        "textEdit_ReturnMessage",
        "lineEdit",
        "pushButton_SendMessage",
        "pushButton_SendQueryMessage",
        "pushButton_SetDC%dON" % channel,
        "pushButton_SetDC%dOFF" % channel,
    ):
        widget = page.findChild(QtWidgets.QWidget, name)
        if widget is not None:
            setattr(setting, name, widget)
            setattr(page, name, widget)

    return page, setting


def _make_dc_setting_dialog(channel: int):
    """复用 DC1 的 Designer 设定页，只把开/关按钮名改成当前路号。"""
    from dialogs.Dialog_DC1_Setting import Ui_Dialog_DC1_Setting

    dialog = QtWidgets.QDialog()
    form = Ui_Dialog_DC1_Setting()
    form.setupUi(dialog)
    on_btn = dialog.findChild(QtWidgets.QPushButton, "pushButton_SetDC1ON")
    off_btn = dialog.findChild(QtWidgets.QPushButton, "pushButton_SetDC1OFF")
    if on_btn is not None:
        on_btn.setObjectName("pushButton_SetDC%dON" % channel)
    if off_btn is not None:
        off_btn.setObjectName("pushButton_SetDC%dOFF" % channel)
    select = dialog.findChild(QtWidgets.QComboBox, "comboBox_DC_Select")
    if select is not None:
        select.hide()
    # 暴露与 DC1～4 相同的属性名，供 _send_dc_iv_curve 读取。
    for name in (
        "textEdit_Vmp",
        "textEdit_Voc",
        "textEdit_Imp",
        "textEdit_Isc",
        "textEdit_PF",
        "textEdit_ReturnMessage",
        "lineEdit",
        "pushButton_SendMessage",
        "pushButton_SendQueryMessage",
        "comboBox_DC_Select",
    ):
        widget = dialog.findChild(QtWidgets.QWidget, name)
        if widget is not None:
            setattr(form, name, widget)
    setattr(form, "pushButton_SetDC%dON" % channel, on_btn)
    setattr(form, "pushButton_SetDC%dOFF" % channel, off_btn)
    form._dialog = dialog
    form._channel = channel
    return form


def _wire_page(ui, channel: int, page, setting) -> None:
    connect_btn = getattr(ui, "pushButton_ConnectEQUDC%d" % channel, None)
    if connect_btn is not None:
        connect_btn.clicked.connect(
            lambda _c=False, ch=channel, pg=page: _toggle_connect(ch, pg)
        )
    set_btn = getattr(ui, "pushButton_SetDC%dOptions" % channel, None)
    if set_btn is not None:
        set_btn.clicked.connect(lambda: None)  # 与 DC1～4 一致：设定已嵌入，无需弹窗

    on_btn = getattr(setting, "pushButton_SetDC%dON" % channel, None)
    off_btn = getattr(setting, "pushButton_SetDC%dOFF" % channel, None)
    if on_btn is not None:
        on_btn.clicked.connect(lambda _c=False, ch=channel, st=setting: _output(ch, st, True))
    if off_btn is not None:
        off_btn.clicked.connect(lambda _c=False, ch=channel, st=setting: _output(ch, st, False))

    send_btn = getattr(setting, "pushButton_SendMessage", None)
    if send_btn is not None:
        send_btn.clicked.connect(
            lambda _c=False, ch=channel, st=setting: _send_iv(ch, st)
        )
    query_btn = getattr(setting, "pushButton_SendQueryMessage", None)
    if query_btn is not None:
        query_btn.clicked.connect(
            lambda _c=False, ch=channel, st=setting: _query(ch, st)
        )


def _toggle_connect(channel: int, page) -> None:
    import SCPITestWave as wave

    wave.toggle_extra_dc_connection(channel, page)


def _output(channel: int, setting, turn_on: bool) -> None:
    import SCPITestWave as wave

    controller = wave._dc_controller_for(channel)
    label = "DC%d" % channel
    if controller is None:
        wave._show_connect_message("%s未连接" % label, setting)
        return
    if turn_on:
        controller.open_output(label, setting, wave.logger)
    else:
        controller.close_output(label, setting, wave.logger)


def _send_iv(channel: int, setting) -> None:
    import SCPITestWave as wave

    wave._send_dc_iv_curve(setting, "DC%d" % channel)


def _query(channel: int, setting) -> None:
    import SCPITestWave as wave

    controller = wave._dc_controller_for(channel)
    if controller is None:
        wave._show_connect_message("DC%d未连接" % channel, setting)
        return
    controller.query_message(setting, "DC%d" % channel, wave.logger)


def _copy_interface_list(ui, channel: int) -> None:
    target = getattr(ui, "comboBox_DC%d" % channel, None)
    source = getattr(ui, "comboBox_DC1", None)
    if target is None or source is None:
        return
    current = target.currentText()
    target.blockSignals(True)
    try:
        target.clear()
        for i in range(source.count()):
            target.addItem(source.itemText(i))
        if current:
            idx = target.findText(current)
            if idx >= 0:
                target.setCurrentIndex(idx)
    finally:
        target.blockSignals(False)


def _layout_index(layout, widget) -> int:
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item is not None and item.widget() is widget:
            return i
    return layout.count()
