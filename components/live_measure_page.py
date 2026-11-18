# -*- coding: utf-8 -*-
"""设备管理里的实时测量页：勾选通道，看数字和曲线。不写文件。"""
from __future__ import annotations

import threading
from typing import Dict, List, Tuple

from PyQt5 import QtCore, QtGui, QtWidgets

from components import ui_theme as theme
from utils.live_measure_chart import (
    group_series,
    series_color,
    short_label,
    y_range,
)
from utils.live_measure_read import (
    append_history,
    read_dewetron_item_names,
    read_snapshot,
    read_wt_checks,
)

PAGE_INDEX = 13

# 和功率分析仪 WT3000 测量勾选同一套。量程、F01–F20 不是实时数值，不放进来。
_WT_GROUPS = (
    (
        "元素",
        (
            ("checkBox_SetElement1", "Element1", True),
            ("checkBox_SetElement2", "Element2", False),
            ("checkBox_SetElement3", "Element3", False),
            ("checkBox_SetElement4", "Element4", False),
            ("checkBox_SetElement5", "Element5（1800/1806）", False),
            ("checkBox_SetElement6", "Element6（1800/1806）", False),
            ("checkBox_SetSigma", "Σ", True),
        ),
    ),
    (
        "基本量",
        (
            ("checkBox_SetU", "U", True),
            ("checkBox_SetI", "I", True),
            ("checkBox_SetCfU", "CfU", False),
            ("checkBox_SetCfI", "CfI", False),
            ("checkBox_SetUppeak", "Uppeak", False),
            ("checkBox_SetUmpeak", "Umpeak", False),
            ("checkBox_SetIppeak", "Ippeak", False),
            ("checkBox_SetImpeak", "Impeak", False),
            ("checkBox_SetP", "P", True),
            ("checkBox_SetS", "S", False),
            ("checkBox_SetQ", "Q", False),
            ("checkBox_SetLambda", "λ", True),
            ("checkBox_SetPhi", "φ", False),
            ("checkBox_SetPc", "Pc", False),
            ("checkBox_SetFreqU", "FreqU", True),
            ("checkBox_SetFreqI", "FreqI", False),
        ),
    ),
    (
        "功率 / 电能",
        (
            ("checkBox_SetTime", "Time", False),
            ("checkBox_SetWP", "WP", False),
            ("checkBox_SetWPPlus", "WP+", False),
            ("checkBox_SetWPMinus", "WP-", False),
            ("checkBox_Setq", "q", False),
            ("checkBox_SetqPlus", "q+", False),
            ("checkBox_SetqMinus", "q-", False),
            ("checkBox_SetWS", "WS", False),
            ("checkBox_SetWQ", "WQ", False),
            ("checkBox_SetEta1", "η1", False),
            ("checkBox_SetEta2", "η2", False),
            ("checkBox_SetEta3", "η3", False),
            ("checkBox_SetEta4", "η4", False),
        ),
    ),
    (
        "谐波",
        (
            ("checkBox_SetUk", "Uk", False),
            ("checkBox_SetIk", "Ik", False),
            ("checkBox_SetPk", "Pk", False),
            ("checkBox_SetSk", "Sk", False),
            ("checkBox_SetQk", "Qk", False),
            ("checkBox_SetPFk", "PFk", False),
        ),
    ),
    (
        "THD / 相位差",
        (
            ("checkBox_SetUthd", "Uthd", False),
            ("checkBox_SetIthd", "Ithd", False),
            ("checkBox_SetPthd", "Pthd", False),
            ("checkBox_SetUthf", "Uthf", False),
            ("checkBox_SetIthf", "Ithf", False),
            ("checkBox_SetUtif", "Utif", False),
            ("checkBox_SetItif", "Itif", False),
            ("checkBox_Sethvf", "HVF", False),
            ("checkBox_Sethcf", "HCF", False),
            ("checkBox_SetPhiUi_Uj", "φUi-Uj", False),
            ("checkBox_SetPhiUi_Uk", "φUi-Uk", False),
            ("checkBox_SetPhiUi_Ii", "φUi-Ii", False),
        ),
    ),
    (
        "基波（WT5000）",
        (
            ("checkBox_SetUfnd", "Ufnd", False),
            ("checkBox_SetIfnd", "Ifnd", False),
            ("checkBox_SetPfnd", "Pfnd", False),
            ("checkBox_SetLambdafnd", "λfnd", False),
        ),
    ),
)


class _ValueTile(QtWidgets.QFrame):
    """Soft Panel 风格数字块：色点 + 短名 + 大数字。"""

    def __init__(self, name: str, color: str, parent=None):
        super().__init__(parent)
        self.setObjectName("liveValueTile")
        self.setStyleSheet(
            f"""
            QFrame#liveValueTile {{
                background: {theme.PANEL};
                border: 1px solid {theme.LINE};
                border-radius: {theme.px(8)}px;
            }}
            """
        )
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)
        head = QtWidgets.QHBoxLayout()
        dot = QtWidgets.QLabel("●")
        dot.setStyleSheet(f"color: {color}; font-size: 11px; background: transparent;")
        title = QtWidgets.QLabel(short_label(name))
        title.setStyleSheet(
            f"font-size: 11px; color: {theme.MUTED}; background: transparent;"
        )
        head.addWidget(dot)
        head.addWidget(title)
        head.addStretch(1)
        layout.addLayout(head)
        self.value = QtWidgets.QLabel("--")
        self.value.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {theme.INK}; background: transparent;"
        )
        layout.addWidget(self.value)


class _TrendChart(QtWidgets.QWidget):
    """按量纲分栏画曲线（Oxygen 多轨思路），每栏独立纵轴。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._series: Dict[str, List[float]] = {}
        self._color_of: Dict[str, str] = {}
        self.setMinimumHeight(theme.px(280))
        self.setStyleSheet(
            f"background: #ffffff; border: 1px solid {theme.LINE}; border-radius: 8px;"
        )

    def set_series(self, series: Dict[str, List[float]], colors: Dict[str, str] | None = None) -> None:
        self._series = dict(series or {})
        self._color_of = dict(colors or {})
        self.update()

    def paintEvent(self, event):  # noqa: N802
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(self.rect(), QtGui.QColor("#ffffff"))
        names = [name for name, values in self._series.items() if values]
        if not names:
            painter.setPen(QtGui.QColor(theme.MUTED))
            painter.drawText(self.rect(), QtCore.Qt.AlignCenter, "开始查看后，曲线显示在这里")
            painter.end()
            return

        groups = group_series(names)
        margin = 10
        legend_h = 22
        gap = 8
        plot_top = margin
        plot_bottom = self.height() - margin - legend_h
        usable = max(plot_bottom - plot_top - gap * (len(groups) - 1), 40)
        pane_h = usable / max(len(groups), 1)
        left = margin + 44
        right = self.width() - margin - 8
        width = max(right - left, 20)

        for pane_index, (title, group_names) in enumerate(groups):
            top = plot_top + pane_index * (pane_h + gap)
            bottom = top + pane_h
            pane = QtCore.QRectF(left, top + 4, width, max(pane_h - 8, 20))
            painter.fillRect(
                QtCore.QRectF(margin, top, self.width() - 2 * margin, pane_h),
                QtGui.QColor("#f8fafc" if pane_index % 2 else "#ffffff"),
            )
            painter.setPen(QtGui.QColor(theme.MUTED))
            font = painter.font()
            font.setPointSize(8)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(
                QtCore.QRectF(margin, top + 2, 42, 16),
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
                title.split()[0],
            )

            count = max(len(self._series.get(name, [])) for name in group_names)
            # 同组量程接近用共用轴；P/Q 差太多时各曲线自缩放（看趋势）
            ranges = {name: y_range(self._series.get(name) or []) for name in group_names}
            spans = [max(high - low, 1e-12) for low, high in ranges.values()]
            mags = [max(abs(low), abs(high), 1e-12) for low, high in ranges.values()]
            # 量级差大（如 P≈5k 与 Q≈100）也各自缩放，不只看波动幅度
            shared = (max(spans) / min(spans) < 8.0) and (max(mags) / min(mags) < 8.0)
            if shared:
                all_vals = [
                    value
                    for name in group_names
                    for value in self._series.get(name, [])
                    if value == value
                ]
                shared_low, shared_high = y_range(all_vals)
            else:
                shared_low = shared_high = 0.0

            painter.setPen(QtGui.QPen(QtGui.QColor("#e2e8f0"), 1))
            for frac in (0.0, 0.5, 1.0):
                y = pane.bottom() - frac * pane.height()
                painter.drawLine(QtCore.QPointF(pane.left(), y), QtCore.QPointF(pane.right(), y))
            font.setBold(False)
            painter.setFont(font)
            painter.setPen(QtGui.QColor(theme.MUTED))
            if shared:
                painter.drawText(
                    QtCore.QRectF(margin, pane.top() - 2, 42, 14),
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter,
                    f"{shared_high:.3g}",
                )
                painter.drawText(
                    QtCore.QRectF(margin, pane.bottom() - 12, 42, 14),
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter,
                    f"{shared_low:.3g}",
                )
            else:
                painter.drawText(
                    QtCore.QRectF(margin, pane.top() + pane.height() / 2 - 7, 42, 14),
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter,
                    "自缩",
                )

            for name in group_names:
                values = self._series.get(name) or []
                low, high = (shared_low, shared_high) if shared else ranges[name]
                span = high - low if high != low else 1.0
                path = QtGui.QPainterPath()
                started = False
                for step, value in enumerate(values):
                    if value != value:
                        started = False
                        continue
                    x = pane.left() + (step / max(count - 1, 1)) * pane.width()
                    y = pane.bottom() - ((value - low) / span) * pane.height()
                    if not started:
                        path.moveTo(x, y)
                        started = True
                    else:
                        path.lineTo(x, y)
                color = self._color_of.get(name) or series_color(names.index(name))
                pen = QtGui.QPen(QtGui.QColor(color))
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawPath(path)

        # 底部图例：色块 + 短名，自动换行
        legend_y = self.height() - legend_h + 2
        x = margin
        font = painter.font()
        font.setPointSize(8)
        font.setBold(False)
        painter.setFont(font)
        for name in names:
            label = short_label(name)
            color = self._color_of.get(name) or series_color(names.index(name))
            metrics = painter.fontMetrics()
            text_w = metrics.horizontalAdvance(label) + 18
            if x + text_w > self.width() - margin:
                break
            painter.fillRect(QtCore.QRectF(x, legend_y + 4, 8, 8), QtGui.QColor(color))
            painter.setPen(QtGui.QColor(theme.INK))
            painter.drawText(x + 11, legend_y + 12, label)
            x += text_w + 10
        painter.end()


class LiveMeasurePage(QtWidgets.QWidget):
    """勾选测量项，看实时数字和曲线。"""

    _sample_ready = QtCore.pyqtSignal(object, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("liveMeasurePage")
        self.setStyleSheet(theme.PAGE_STYLE)
        self._boxes: Dict[str, QtWidgets.QCheckBox] = {}
        self._tiles: Dict[str, _ValueTile] = {}
        self._history: Dict[str, List[float]] = {}
        self._color_of: Dict[str, str] = {}
        self._polling = False
        self._worker: threading.Thread | None = None
        self._kind = "wt"
        self._sample_ready.connect(self._apply_sample)

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)
        root.setSpacing(12)

        title = QtWidgets.QLabel("数据测量")
        title.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {theme.INK}; background: transparent;"
        )
        root.addWidget(title)
        hint = QtWidgets.QLabel(
            "勾选要看的量。数字区像 Soft Panel，曲线按量纲分栏（U/I/P/λ/F），不写文件。"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"font-size: 12px; color: {theme.MUTED}; background: transparent;")
        root.addWidget(hint)

        switch = QtWidgets.QHBoxLayout()
        self.radio_wt = QtWidgets.QRadioButton("WT")
        self.radio_dew = QtWidgets.QRadioButton("德威创")
        self.radio_wt.setChecked(True)
        self.radio_wt.toggled.connect(self._on_kind_changed)
        switch.addWidget(self.radio_wt)
        switch.addWidget(self.radio_dew)
        switch.addStretch(1)
        self.btn_fields = QtWidgets.QPushButton("读取字段")
        self.btn_fields.setVisible(False)
        self.btn_fields.clicked.connect(self._load_dew_fields)
        self.btn_start = QtWidgets.QPushButton("开始查看")
        self.btn_start.clicked.connect(self._toggle)
        switch.addWidget(self.btn_fields)
        switch.addWidget(self.btn_start)
        root.addLayout(switch)

        body = QtWidgets.QHBoxLayout()
        self._checks = QtWidgets.QWidget()
        self._check_layout = QtWidgets.QVBoxLayout(self._checks)
        self._check_layout.setContentsMargins(0, 0, 0, 0)
        self._check_layout.addStretch(1)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._checks)
        scroll.setFixedWidth(theme.px(260))
        body.addWidget(scroll)

        right = QtWidgets.QVBoxLayout()
        self._values_host = QtWidgets.QWidget()
        self._values = QtWidgets.QGridLayout(self._values_host)
        self._values.setContentsMargins(0, 0, 0, 0)
        self._values.setHorizontalSpacing(8)
        self._values.setVerticalSpacing(8)
        right.addWidget(self._values_host)
        self.chart = _TrendChart()
        right.addWidget(self.chart, 1)
        body.addLayout(right, 1)
        root.addLayout(body, 1)

        self.status = QtWidgets.QLabel("未开始")
        self.status.setStyleSheet(f"font-size: 12px; color: {theme.MUTED}; background: transparent;")
        root.addWidget(self.status)

        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(500)
        self._timer.timeout.connect(self._kick)
        self._fill_wt_checks()

    def showEvent(self, event):  # noqa: N802
        super().showEvent(event)
        self._pick_default_kind()

    def hideEvent(self, event):  # noqa: N802
        self._stop()
        super().hideEvent(event)

    def _pick_default_kind(self) -> None:
        try:
            from app.context import get_app_context

            ctx = get_app_context()
        except Exception:
            return
        wt_on = str(getattr(ctx, "strConnectWT3000", "0")) == "1"
        dew_on = str(getattr(ctx, "strConnectDEWETRON", "0")) == "1"
        if dew_on and not wt_on:
            self.radio_dew.setChecked(True)
        elif wt_on:
            self.radio_wt.setChecked(True)

    def _on_kind_changed(self) -> None:
        self._stop()
        self._kind = "wt" if self.radio_wt.isChecked() else "dew"
        self.btn_fields.setVisible(self._kind == "dew")
        self._history.clear()
        self._color_of.clear()
        self.chart.set_series({})
        if self._kind == "wt":
            self._fill_wt_checks()
        else:
            self._clear_checks()
            self.status.setText("德威创请先点读取字段，再勾选要看的量")

    def _clear_checks(self) -> None:
        while self._check_layout.count():
            item = self._check_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._boxes.clear()
        self._clear_values()
        self._check_layout.addStretch(1)

    def _clear_values(self) -> None:
        while self._values.count():
            item = self._values.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._tiles.clear()

    def _add_section(self, text: str) -> None:
        label = QtWidgets.QLabel(text)
        label.setStyleSheet(
            f"font-size: 12px; font-weight: 700; color: {theme.INK}; background: transparent; padding-top: 6px;"
        )
        stretch = self._check_layout.takeAt(self._check_layout.count() - 1)
        self._check_layout.addWidget(label)
        if stretch is not None:
            self._check_layout.addItem(stretch)

    def _wt_config(self) -> Dict[str, str]:
        """只交勾选。型号在读数时按 *IDN? 填，3000 与 1800 的命令不一样。"""
        config = {"textEdit_SetStart": "1", "textEdit_SetStop": "1"}
        for key, box in self._boxes.items():
            config[key] = "1" if box.isChecked() else "0"
        return config

    def _add_check(self, token: str, text: str, checked: bool) -> None:
        box = QtWidgets.QCheckBox(text)
        box.setChecked(checked)
        box.setProperty("token", token)
        self._boxes[token] = box
        stretch = self._check_layout.takeAt(self._check_layout.count() - 1)
        self._check_layout.addWidget(box)
        if stretch is not None:
            self._check_layout.addItem(stretch)

    def _fill_wt_checks(self) -> None:
        self._clear_checks()
        for title, rows in _WT_GROUPS:
            self._add_section(title)
            for key, text, checked in rows:
                self._add_check(key, text, checked)
        self.status.setText("未开始。先勾元素，再勾要看的量")

    def _selected(self) -> List[str]:
        if self._kind != "wt":
            return [token for token, box in self._boxes.items() if box.isChecked()]
        config = self._wt_config()
        picked = any(
            box.isChecked() and not key.startswith(("checkBox_SetElement", "checkBox_SetSigma"))
            for key, box in self._boxes.items()
        )
        if not picked:
            return []
        from utils.live_measure_read import items_for_wt_checks

        return items_for_wt_checks(config, "3000")

    def _load_dew_fields(self) -> None:
        names, message = read_dewetron_item_names()
        self._clear_checks()
        for name in names:
            self._add_check(name, name, True)
        self.status.setText(message)

    def _toggle(self) -> None:
        if self._polling:
            self._stop()
            return
        if not self._selected():
            self.status.setText("先勾选测量项")
            return
        self._polling = True
        self._history.clear()
        self._color_of.clear()
        self.btn_start.setText("停止查看")
        self._timer.start()
        self._kick()

    def _stop(self) -> None:
        self._polling = False
        self._timer.stop()
        self.btn_start.setText("开始查看")

    def _kick(self) -> None:
        if not self._polling:
            return
        if self._worker is not None and self._worker.is_alive():
            return
        kind = self._kind
        items = [] if kind == "wt" else self._selected()
        wt_config = self._wt_config() if kind == "wt" else None

        def _run() -> None:
            try:
                if kind == "wt":
                    sample, message = read_wt_checks(wt_config or {})
                else:
                    sample, message = read_snapshot(kind, items)
            except Exception as exc:
                sample, message = {}, str(exc)
            self._sample_ready.emit(sample, message)

        self._worker = threading.Thread(target=_run, name="LiveMeasure", daemon=True)
        self._worker.start()

    def _ensure_colors(self, names: List[str]) -> None:
        for name in names:
            if name not in self._color_of:
                self._color_of[name] = series_color(len(self._color_of))

    def _apply_sample(self, sample: object, message: str) -> None:
        if not self._polling:
            return
        data = dict(sample or {})
        if data:
            append_history(self._history, data)
            self._ensure_colors(list(data.keys()))
            self._render_values(data)
            self.chart.set_series(
                {key: self._history.get(key, []) for key in data},
                self._color_of,
            )
        self.status.setText(message or "实时")

    def _render_values(self, sample: Dict[str, float]) -> None:
        if set(sample) != set(self._tiles):
            self._clear_values()
            cols = 4
            for index, name in enumerate(sample):
                color = self._color_of.get(name) or series_color(index)
                tile = _ValueTile(name, color)
                self._values.addWidget(tile, index // cols, index % cols)
                self._tiles[name] = tile
        for name, value in sample.items():
            tile = self._tiles.get(name)
            if tile is not None:
                tile.value.setText(f"{value:.4g}")
