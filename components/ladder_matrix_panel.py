# -*- coding: utf-8 -*-
"""功率档 × 内层阶梯：cartesian（外×内）或 pair（一一对应）。"""

from __future__ import annotations

from PyQt5 import QtCore, QtWidgets

from components.comma_segment_edit import CommaSegmentEdit

# cartesian：每个功率档完整扫一遍内层（固定Q / Qin / Qacc 等）
# pair：第 i 点功率配第 i 点电压（动态 Q(U)）
MODE_CARTESIAN = "cartesian"
MODE_PAIR = "pair"


def _split(csv_text: str) -> list:
    return [p for p in str(csv_text or "").split(",") if p.strip()]


def plan_preview_text(
    outer_csv: str,
    inner_csv: str,
    *,
    outer_name: str,
    inner_name: str,
    mode: str = MODE_CARTESIAN,
) -> str:
    outer = _split(outer_csv)
    inner = _split(inner_csv)
    if mode == MODE_PAIR:
        if not inner:
            return f"请先填写{inner_name}阶梯。"
        if not outer:
            return (
                f"功率留空：整段{inner_name}阶梯都用步骤①的功率 "
                f"（共 {len(inner)} 点）。"
            )
        if len(outer) == 1:
            return (
                f"固定功率 {outer[0]}%：只改{inner_name} "
                f"{' → '.join(inner[:4])}{' → …' if len(inner) > 4 else ''} "
                f"（共 {len(inner)} 点）。"
            )
        if len(outer) != len(inner):
            return (
                f"点数不一致：功率 {len(outer)} 点、{inner_name} {len(inner)} 点。"
                f"请改成相同点数（第 1 行功率配第 1 行{inner_name}），"
                f"或功率只填 1 个、或功率留空。"
            )
        samples = []
        for i in range(min(3, len(inner))):
            samples.append(f"{inner_name}={inner[i]}% → 功率={outer[i]}%")
        more = "；…" if len(inner) > 3 else ""
        return (
            f"一一对应：共 {len(inner)} 点。"
            f"例如 {samples[0]}"
            + (f"；然后 {samples[1]}" if len(samples) > 1 else "")
            + more
            + "。不是「每个功率把电压 list 全扫一遍」。"
        )

    if not inner:
        return f"请先填写{inner_name}阶梯。"
    if not outer:
        return (
            f"未填{outer_name}：只按步骤①功率扫一遍{inner_name} "
            f"（{len(inner)} 点）。"
        )
    sample_outer = outer[0]
    sample_inner = " → ".join(inner[:3]) + (" → …" if len(inner) > 3 else "")
    return (
        f"组合扫：每个{outer_name}档完整扫一遍{inner_name}。"
        f"共 {len(outer)}×{len(inner)}={len(outer) * len(inner)} 点。"
        f"例如 {outer_name}={sample_outer}% 时：{inner_name} {sample_inner}；"
        f"再换成 {outer_name}={outer[1] if len(outer) > 1 else sample_outer}% 重扫同一{inner_name} list。"
    )


class LadderMatrixPanel(QtWidgets.QWidget):
    """左侧功率，右侧电压/Q；mode=cartesian 外×内，mode=pair 一一对应。"""

    changed = QtCore.pyqtSignal()

    def __init__(
        self,
        parent=None,
        *,
        mode: str = MODE_CARTESIAN,
        outer_header: str = "功率",
        outer_unit: str = "%",
        outer_object_name: str = "textEdit_PowerLadder",
        outer_default: str = "100,70,50,20",
        outer_placeholder: str = "功率档",
        outer_tip: str = "",
        inner_header: str = "电压 Un%",
        inner_unit: str = "%",
        inner_object_name: str = "textEdit_VoltageLadder",
        inner_default: str = "",
        inner_placeholder: str = "Un%",
        inner_tip: str = "",
    ):
        super().__init__(parent)
        self._mode = MODE_PAIR if mode == MODE_PAIR else MODE_CARTESIAN
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        row = QtWidgets.QHBoxLayout()
        row.setSpacing(12)

        if self._mode == MODE_PAIR:
            left_title = f"{outer_header}%（与右侧同行配对）"
            right_title = f"{inner_header}（与左侧同行配对）"
            default_outer_tip = "第 i 行功率配第 i 行电压。留空=用步骤①功率；只填 1 个=全程固定该功率。"
            default_inner_tip = "电压按序改网压；功率按左表同行取值。"
        else:
            left_title = f"{outer_header}档（外循环）"
            right_title = f"{inner_header}（内循环）"
            default_outer_tip = "先改直流功率，再进入右侧阶梯。"
            default_inner_tip = "同一功率档内按序改网压/设定。"

        left = QtWidgets.QGroupBox(left_title)
        left.setStyleSheet(
            "QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; "
            "margin-top: 8px; padding-top: 8px; font-weight: 600; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }"
        )
        left_lay = QtWidgets.QVBoxLayout(left)
        left_lay.setContentsMargins(10, 14, 10, 10)
        self.outer = CommaSegmentEdit(value_header=outer_header, unit=outer_unit)
        self.outer.setObjectName(outer_object_name)
        self.outer.setPlaceholderText(outer_placeholder)
        self.outer.setText(outer_default)
        left_lay.addWidget(self.outer)
        left_tip = QtWidgets.QLabel(outer_tip or default_outer_tip)
        left_tip.setWordWrap(True)
        left_tip.setStyleSheet("color:#64748b;font-size:11px;font-weight:normal;")
        left_lay.addWidget(left_tip)
        row.addWidget(left, 1)

        right = QtWidgets.QGroupBox(right_title)
        right.setStyleSheet(left.styleSheet())
        right_lay = QtWidgets.QVBoxLayout(right)
        right_lay.setContentsMargins(10, 14, 10, 10)
        self.inner = CommaSegmentEdit(value_header=inner_header, unit=inner_unit)
        self.inner.setObjectName(inner_object_name)
        self.inner.setPlaceholderText(inner_placeholder)
        self.inner.setText(inner_default)
        right_lay.addWidget(self.inner)
        right_tip_lbl = QtWidgets.QLabel(inner_tip or default_inner_tip)
        right_tip_lbl.setWordWrap(True)
        right_tip_lbl.setStyleSheet("color:#64748b;font-size:11px;font-weight:normal;")
        right_lay.addWidget(right_tip_lbl)
        row.addWidget(right, 2)

        root.addLayout(row)

        self.preview = QtWidgets.QLabel()
        self.preview.setObjectName("labelLadderPlanPreview")
        self.preview.setWordWrap(True)
        self.preview.setStyleSheet(
            "background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;"
            "color:#334155;font-size:12px;padding:8px 10px;"
        )
        root.addWidget(self.preview)

        self._outer_name = outer_header
        self._inner_name = inner_header
        self.outer.textChanged.connect(self._refresh)
        self.inner.textChanged.connect(self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        self.preview.setText(
            plan_preview_text(
                self.outer.toPlainText(),
                self.inner.toPlainText(),
                outer_name=self._outer_name,
                inner_name=self._inner_name,
                mode=self._mode,
            )
        )
        self.changed.emit()
