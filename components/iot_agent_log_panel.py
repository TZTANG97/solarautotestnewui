# -*- coding: utf-8 -*-
"""IOT Agent 日志与通信信息页（诊断用）。"""
from __future__ import annotations

from typing import Callable, Optional

from PyQt5 import QtCore, QtWidgets

from components import ui_theme as theme


def _info_label(text: str = "—") -> QtWidgets.QLabel:
    lab = QtWidgets.QLabel(text)
    lab.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
    lab.setWordWrap(True)
    lab.setStyleSheet(
        f"font-size: 13px; color: {theme.INK}; background: transparent; font-weight: 600;"
    )
    return lab


def _muted_label(text: str) -> QtWidgets.QLabel:
    lab = QtWidgets.QLabel(text)
    lab.setStyleSheet(
        f"font-size: 11px; color: {theme.MUTED}; background: transparent;"
    )
    return lab


class IotAgentLogPage(QtWidgets.QWidget):
    """上方通信摘要 + 启停按钮 + 滚动日志。"""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setObjectName("iotAgentLogPage")
        self.setStyleSheet(theme.PAGE_STYLE)
        self._auto_scroll = True

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)
        root.setSpacing(12)

        title = QtWidgets.QLabel("IOT Agent 日志")
        title.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {theme.INK}; background: transparent;"
        )
        root.addWidget(title)
        sub = QtWidgets.QLabel(
            "查看设备号 / 通信参数与 Agent 运行日志，便于判断上线与任务问题"
        )
        sub.setStyleSheet(
            f"font-size: 12px; color: {theme.MUTED}; background: transparent;"
        )
        root.addWidget(sub)

        info_card = QtWidgets.QWidget()
        info_card.setObjectName("card")
        info_card.setStyleSheet(theme.CARD_STYLE)
        info_lay = QtWidgets.QGridLayout(info_card)
        info_lay.setContentsMargins(16, 14, 16, 14)
        info_lay.setHorizontalSpacing(24)
        info_lay.setVerticalSpacing(8)

        self.label_agent_status = _info_label("—")
        self.label_pythonid = _info_label("—")
        self.label_machine_id = _info_label("—")
        self.label_iot_base = _info_label("—")
        self.label_token = _info_label("—")
        self.label_mode = _info_label("—")
        self.label_log_path = _info_label("—")
        self.label_log_path.setStyleSheet(
            f"font-size: 11px; color: {theme.MUTED}; background: transparent;"
        )

        rows = [
            ("运行状态", self.label_agent_status),
            ("设备号 (pythonid)", self.label_pythonid),
            ("本机 machine_id", self.label_machine_id),
            ("IOT 地址", self.label_iot_base),
            ("令牌", self.label_token),
            ("执行模式 / 版本", self.label_mode),
        ]
        for i, (caption, widget) in enumerate(rows):
            r, c = divmod(i, 2)
            box = QtWidgets.QVBoxLayout()
            box.setSpacing(2)
            box.addWidget(_muted_label(caption))
            box.addWidget(widget)
            info_lay.addLayout(box, r, c)
        path_box = QtWidgets.QVBoxLayout()
        path_box.setSpacing(2)
        path_box.addWidget(_muted_label("日志文件"))
        path_box.addWidget(self.label_log_path)
        info_lay.addLayout(path_box, 3, 0, 1, 2)
        root.addWidget(info_card)

        row = QtWidgets.QHBoxLayout()
        row.setSpacing(8)
        self.pushButton_StartIotAgentPage = QtWidgets.QPushButton("启动 Agent")
        self.pushButton_StartIotAgentPage.setObjectName("pushButton_StartIotAgentPage")
        self.pushButton_StartIotAgentPage.setFixedHeight(34)
        self.pushButton_StartIotAgentPage.setStyleSheet(theme.CONNECT_BTN_QSS)
        row.addWidget(self.pushButton_StartIotAgentPage)

        self.pushButton_StopIotAgentPage = QtWidgets.QPushButton("停止 Agent")
        self.pushButton_StopIotAgentPage.setObjectName("pushButton_StopIotAgentPage")
        self.pushButton_StopIotAgentPage.setFixedHeight(34)
        self.pushButton_StopIotAgentPage.setStyleSheet(
            f"QPushButton {{ background:{theme.PANEL}; color:{theme.INK}; "
            f"border:1px solid {theme.LINE_STRONG}; border-radius:8px; padding:0 14px; "
            f"font-size:13px; font-weight:600; }}"
            f"QPushButton:hover {{ background:{theme.NEUTRAL}; }}"
        )
        row.addWidget(self.pushButton_StopIotAgentPage)

        self.pushButton_RefreshIotAgentLog = QtWidgets.QPushButton("刷新日志")
        self.pushButton_RefreshIotAgentLog.setObjectName("pushButton_RefreshIotAgentLog")
        self.pushButton_RefreshIotAgentLog.setFixedHeight(34)
        self.pushButton_RefreshIotAgentLog.setStyleSheet(
            f"QPushButton {{ background:{theme.PANEL}; color:{theme.INK}; "
            f"border:1px solid {theme.LINE_STRONG}; border-radius:8px; padding:0 14px; "
            f"font-size:13px; }}"
            f"QPushButton:hover {{ background:{theme.NEUTRAL}; }}"
        )
        row.addWidget(self.pushButton_RefreshIotAgentLog)

        self.checkBox_IotAgentAutoScroll = QtWidgets.QCheckBox("自动滚到底")
        self.checkBox_IotAgentAutoScroll.setChecked(True)
        self.checkBox_IotAgentAutoScroll.setStyleSheet(
            f"color: {theme.MUTED}; background: transparent;"
        )
        self.checkBox_IotAgentAutoScroll.toggled.connect(self._on_auto_scroll_toggled)
        row.addWidget(self.checkBox_IotAgentAutoScroll)
        row.addStretch(1)
        root.addLayout(row)

        self.textEdit_IotAgentLog = QtWidgets.QPlainTextEdit()
        self.textEdit_IotAgentLog.setObjectName("textEdit_IotAgentLog")
        self.textEdit_IotAgentLog.setReadOnly(True)
        self.textEdit_IotAgentLog.setMaximumBlockCount(2500)
        self.textEdit_IotAgentLog.setStyleSheet(theme.LOG_QSS)
        self.textEdit_IotAgentLog.setPlaceholderText("Agent 日志将显示在这里…")
        root.addWidget(self.textEdit_IotAgentLog, 1)

        self._last_log_text = ""
        self._refreshing = False

    def _on_auto_scroll_toggled(self, checked: bool) -> None:
        self._auto_scroll = bool(checked)
        if checked:
            cursor = self.textEdit_IotAgentLog.textCursor()
            cursor.movePosition(cursor.End)
            self.textEdit_IotAgentLog.setTextCursor(cursor)

    def refresh_from_agent(self) -> None:
        """从 process_control 拉取通信信息与日志尾部。"""
        if self._refreshing:
            return
        self._refreshing = True
        try:
            self._refresh_from_agent_impl()
        finally:
            self._refreshing = False

    def _refresh_from_agent_impl(self) -> None:
        try:
            from agent.process_control import read_agent_comm_info, tail_agent_log
        except Exception as exc:
            self.label_agent_status.setText(f"读取失败: {exc}")
            return

        info = read_agent_comm_info()
        self.label_agent_status.setText(str(info.get("status") or "—"))
        self.label_pythonid.setText(str(info.get("pythonid") or "（未分配）"))
        self.label_machine_id.setText(str(info.get("machine_id") or "（无）"))
        self.label_iot_base.setText(str(info.get("iot_base") or "（未配置）"))
        self.label_token.setText(str(info.get("agent_token_masked") or "—"))
        mode = str(info.get("execution_mode") or "—")
        ver = str(info.get("agent_version") or "")
        poll = str(info.get("poll_interval_sec") or "")
        hb = str(info.get("heartbeat_interval_sec") or "")
        extras = []
        if ver:
            extras.append(f"v{ver}")
        if poll:
            extras.append(f"poll={poll}s")
        if hb:
            extras.append(f"hb={hb}s")
        self.label_mode.setText(mode + ((" · " + " ".join(extras)) if extras else ""))
        self.label_log_path.setText(str(info.get("log_path") or ""))

        # 日志页只取较短尾部，避免大段 setPlainText 卡死 UI
        text = tail_agent_log(max_bytes=80_000)
        if text == self._last_log_text:
            return
        prev = self._last_log_text
        self._last_log_text = text
        # 仅追加增量时更轻；滑窗外的尾部变化则整页替换
        if prev and text.startswith(prev):
            delta = text[len(prev) :]
            if delta:
                self.textEdit_IotAgentLog.appendPlainText(delta.lstrip("\n"))
        else:
            self.textEdit_IotAgentLog.setPlainText(text)
        if self._auto_scroll:
            cursor = self.textEdit_IotAgentLog.textCursor()
            cursor.movePosition(cursor.End)
            self.textEdit_IotAgentLog.setTextCursor(cursor)
            self.textEdit_IotAgentLog.ensureCursorVisible()


def wire_iot_agent_log_page(
    page: IotAgentLogPage,
    *,
    on_start: Optional[Callable[[], None]] = None,
    on_stop: Optional[Callable[[], None]] = None,
    parent_for_timer: Optional[QtCore.QObject] = None,
) -> QtCore.QTimer:
    """绑定启停与定时刷新；返回 timer（调用方需持有引用）。"""
    if on_start is not None:
        page.pushButton_StartIotAgentPage.clicked.connect(on_start)
    if on_stop is not None:
        page.pushButton_StopIotAgentPage.clicked.connect(on_stop)
    page.pushButton_RefreshIotAgentLog.clicked.connect(page.refresh_from_agent)

    timer = QtCore.QTimer(parent_for_timer or page)
    timer.setInterval(2000)

    def _tick():
        try:
            if page.isVisible():
                page.refresh_from_agent()
        except Exception:
            pass

    timer.timeout.connect(_tick)
    timer.start()
    page.refresh_from_agent()
    return timer
