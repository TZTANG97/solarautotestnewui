# -*- coding: utf-8 -*-
"""Bluesight DC settings dialog (UI strings via chr()/UTF-8; avoids GBK-mojibake on Windows)."""

from __future__ import annotations

import html
from typing import Any, Callable, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from scpi_to_modbustcp import BluesightCurveSTC, BluesightTranslator


def _z(*codes: int) -> str:
    return "".join(chr(c) for c in codes)


# Rich-text styles (hint / banners)
_STYLE_BS = "background:#e3f2fd;color:#0d47a1;font-weight:600;padding:2px 7px;border-radius:4px;border:1px solid #90caf9;"
_STYLE_CHROMA = "background:#fff3e0;color:#bf360c;font-weight:600;padding:2px 7px;border-radius:4px;border:1px solid #ffcc80;"
_STYLE_PROTO = "color:#00695c;font-weight:600;"
_STYLE_PARAM = "color:#c62828;font-family:Consolas,monospace;font-weight:600;"
_STYLE_CLASS = "color:#5e35b1;font-family:Consolas,monospace;font-weight:600;"
_STYLE_ACTION = "padding:1px 8px;border-radius:4px;background:#ede7f6;color:#4527a0;font-weight:600;"


def _span(txt: str, style: str) -> str:
    return f'<span style="{style}">{html.escape(txt)}</span>'


def _format_model_banner_html(model_segment: str, ip_display: str) -> str:
    """??????????????IP????????????"""
    m = (model_segment or "").strip()
    ip = (ip_display or "").strip()
    if not ip:
        ip = "\u2014"
    lab_m = _z(0x578B, 0x53F7)
    # Avoid tiny empty row when model unknown
    show_m = html.escape(m) if m else _z(0x002D, 0x002D)
    show_ip = html.escape(ip)
    return (
        '<div style="background:linear-gradient(180deg,#fafcff 0%,#e8f4fc 100%);'
        'border:1px solid #90caf9;border-radius:8px;padding:8px 14px;">'
        '<table cellspacing="0" cellpadding="0" style="border:0;width:100%;">'
        "<tr>"
        '<td style="vertical-align:top;padding-right:16px;">'
        f'<span style="color:#607d8b;font-size:11px;">{lab_m}</span><br/>'
        f'<span style="font-size:14px;font-weight:700;color:#0d47a1;">{show_m}</span>'
        "</td>"
        '<td style="vertical-align:top;border-left:1px solid #b3d4fc;padding-left:16px;">'
        '<span style="color:#607d8b;font-size:11px;">IP</span><br/>'
        f'<span style="font-size:13px;font-family:Consolas,Segoe UI Mono,monospace;'
        f'font-weight:600;color:#1565c0;">{show_ip}</span>'
        "</td>"
        "</tr></table></div>"
    )


def _build_hint_rich_html() -> str:
    """???????Bluesight / Chroma ????????????????????"""
    z = _z
    p1 = (
        z(0x5F53, 0x524D, 0x901A, 0x9053, 0x5DF2, 0x8BC6, 0x522B, 0x4E3A)
        + _span("Bluesight", _STYLE_BS)
        + z(0xFF08)
        + _span("Modbus TCP", _STYLE_PROTO)
        + z(0xFF09, 0x3002)
        + _span("Chroma", _STYLE_CHROMA)
        + z(
            0x5BF9,
            0x8BDD,
            0x6846,
            0x4E2D,
            0x7684,
        )
        + _span("Vmp", _STYLE_PARAM)
        + z(0x3001)
        + _span("Imp", _STYLE_PARAM)
        + z(0x3001)
        + _span("Voc", _STYLE_PARAM)
        + z(0x3001)
        + _span("Isc", _STYLE_PARAM)
        + z(0x3001)
        + _span("PF", _STYLE_PARAM)
        + z(0x7B49, 0x4E3A, 0x9635, 0x5217)
        + _span("IV", _STYLE_CLASS)
        + z(0x53C2, 0x6570, 0xFF1B)
        + _span("Bluesight", _STYLE_BS)
        + z(0x66F2, 0x7EBF, 0x7531)
        + _span("STC", _STYLE_CLASS)
        + z(0x5BC4, 0x5B58, 0x5668, 0x5757, 0x4E0E)
        + _span("BluesightTranslator", _STYLE_CLASS)
        + z(0x6620, 0x5C04, 0xFF0C, 0x8BF7, 0x52FF, 0x6DF7, 0x7528, 0x3002)
    )
    p2 = (
        z(0x300C, 0x5E94, 0x7528, 0x6A21, 0x5F0F, 0x300D, 0xFF1A)
        + _span("SAS", _STYLE_CLASS)
        + z(0x0020, 0x53EF, 0x4E0B, 0x53D1)
        + _span("STC", _STYLE_CLASS)
        + z(0x0020, 0x66F2, 0x7EBF, 0xFF1B)
        + z(0x539F, 0x8F7D, 0x8BF7, 0x5148, 0x5E94, 0x7528, 0x6A21, 0x5F0F, 0x518D, 0x70B9, 0x51FB)
        + z(0x300C)
        + _span(z(0x53D1, 0x9001, 0x53C2, 0x6570), _STYLE_ACTION)
        + z(0x300D)
        + z(
            0x8BBE,
            0x7F6E,
            0x6052,
            0x538B,
            0x002F,
            0x6052,
            0x6D41,
            0x002F,
            0x6052,
            0x529F,
            0x7387,
            0x002F,
            0x6052,
            0x963B,
            0xFF1B,
        )
        + z(0x7535, 0x6C60, 0x6A21, 0x62DF, 0x5668, 0x6682, 0x672A, 0x5F00, 0x53D1, 0x3002)
    )
    p3 = z(
        0x4E0B,
        0x65B9,
        0x6309,
        0x94AE,
        0x4E0E,
        0x4E3B,
        0x754C,
        0x9762,
        0x6253,
        0x5F00,
        0x002F,
        0x5173,
        0x95ED,
        0x8F93,
        0x51FA,
        0x4E00,
        0x81F4,
        0x3002,
    )
    return (
        '<div style="color:#37474f;line-height:1.55;font-size:12px;">'
        f"<p style='margin:0 0 8px 0;'>{p1}</p>"
        f"<p style='margin:0 0 8px 0;'>{p2}</p>"
        f"<p style='margin:0;'>{p3}</p>"
        "</div>"
    )


def _configure_spin_edit(sb: QtWidgets.QDoubleSpinBox) -> None:
    """C locale: decimal point works on Chinese Windows; ensure line edit accepts typing."""
    sb.setLocale(QtCore.QLocale.c())
    sb.setFocusPolicy(QtCore.Qt.StrongFocus)
    sb.setReadOnly(False)
    le = sb.lineEdit()
    if le is not None:
        le.setReadOnly(False)


class Ui_Dialog_Bluesight_DC_Setting:
    def setupUi(self, Dialog: QtWidgets.QDialog) -> None:
        Dialog.setObjectName("Dialog_Bluesight_DC_Setting")
        Dialog.resize(560, 580)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(".\\ui_files\\logo.jpg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On,
        )
        Dialog.setWindowIcon(icon)
        self.label_model = QtWidgets.QLabel(Dialog)
        self.label_model.setGeometry(QtCore.QRect(20, 10, 520, 58))
        self.label_model.setObjectName("label_model")
        self.label_model.setTextFormat(QtCore.Qt.RichText)
        self.label_model.setWordWrap(True)
        self.label_mode_title = QtWidgets.QLabel(Dialog)
        self.label_mode_title.setGeometry(QtCore.QRect(20, 74, 400, 22))
        self.label_mode_title.setObjectName("label_mode_title")
        self.comboBox_mode = QtWidgets.QComboBox(Dialog)
        self.comboBox_mode.setGeometry(QtCore.QRect(20, 102, 200, 32))
        self.comboBox_mode.setObjectName("comboBox_mode")
        self.pushButton_apply_mode = QtWidgets.QPushButton(Dialog)
        self.pushButton_apply_mode.setGeometry(QtCore.QRect(240, 100, 120, 36))
        self.pushButton_apply_mode.setObjectName("pushButton_apply_mode")
        self.widget_sas_curve = QtWidgets.QWidget(Dialog)
        self.widget_sas_curve.setGeometry(QtCore.QRect(20, 142, 510, 158))
        self.widget_sas_curve.setObjectName("widget_sas_curve")
        self.label_pmpp = QtWidgets.QLabel(self.widget_sas_curve)
        self.label_pmpp.setGeometry(QtCore.QRect(0, 6, 200, 22))
        self.label_pmpp.setObjectName("label_pmpp")
        self.doubleSpin_pmpp = QtWidgets.QDoubleSpinBox(self.widget_sas_curve)
        self.doubleSpin_pmpp.setGeometry(QtCore.QRect(210, 2, 140, 30))
        self.doubleSpin_pmpp.setDecimals(3)
        # 原 65.535 为单字寄存器上限；现 Pmpp 按 uint32 编码，UI 放宽（以机台额定为准）
        self.doubleSpin_pmpp.setRange(0.001, 1000.0)
        self.doubleSpin_pmpp.setValue(8.0)
        self.doubleSpin_pmpp.setObjectName("doubleSpin_pmpp")
        _configure_spin_edit(self.doubleSpin_pmpp)
        self.label_umpp = QtWidgets.QLabel(self.widget_sas_curve)
        self.label_umpp.setGeometry(QtCore.QRect(0, 44, 200, 22))
        self.label_umpp.setObjectName("label_umpp")
        self.doubleSpin_umpp = QtWidgets.QDoubleSpinBox(self.widget_sas_curve)
        self.doubleSpin_umpp.setGeometry(QtCore.QRect(210, 40, 140, 30))
        self.doubleSpin_umpp.setDecimals(2)
        self.doubleSpin_umpp.setRange(0.0, 2000.0)
        self.doubleSpin_umpp.setValue(650.0)
        self.doubleSpin_umpp.setObjectName("doubleSpin_umpp")
        _configure_spin_edit(self.doubleSpin_umpp)
        self.label_ff = QtWidgets.QLabel(self.widget_sas_curve)
        self.label_ff.setGeometry(QtCore.QRect(0, 82, 200, 22))
        self.label_ff.setObjectName("label_ff")
        self.doubleSpin_ff = QtWidgets.QDoubleSpinBox(self.widget_sas_curve)
        self.doubleSpin_ff.setGeometry(QtCore.QRect(210, 78, 140, 30))
        self.doubleSpin_ff.setDecimals(2)
        self.doubleSpin_ff.setRange(0.25, 0.95)
        self.doubleSpin_ff.setSingleStep(0.01)
        self.doubleSpin_ff.setValue(0.8)
        self.doubleSpin_ff.setObjectName("doubleSpin_ff")
        _configure_spin_edit(self.doubleSpin_ff)
        self.pushButton_send_curve = QtWidgets.QPushButton(self.widget_sas_curve)
        self.pushButton_send_curve.setGeometry(QtCore.QRect(0, 118, 280, 36))
        self.pushButton_send_curve.setObjectName("pushButton_send_curve")
        self.widget_sas_curve.setVisible(False)
        self.widget_orig_load = QtWidgets.QWidget(Dialog)
        self.widget_orig_load.setGeometry(QtCore.QRect(20, 142, 510, 228))
        self.widget_orig_load.setObjectName("widget_orig_load")
        self.label_orig_outmode = QtWidgets.QLabel(self.widget_orig_load)
        self.label_orig_outmode.setGeometry(QtCore.QRect(0, 10, 120, 22))
        self.label_orig_outmode.setObjectName("label_orig_outmode")
        self.comboBox_orig_outmode = QtWidgets.QComboBox(self.widget_orig_load)
        self.comboBox_orig_outmode.setGeometry(QtCore.QRect(125, 6, 260, 30))
        self.comboBox_orig_outmode.setObjectName("comboBox_orig_outmode")
        self.stacked_orig_params = QtWidgets.QStackedWidget(self.widget_orig_load)
        self.stacked_orig_params.setGeometry(QtCore.QRect(0, 42, 510, 100))
        self.stacked_orig_params.setObjectName("stacked_orig_params")
        page_cv = QtWidgets.QWidget()
        page_cv.setObjectName("page_orig_cv")
        self.label_cv_volt = QtWidgets.QLabel(page_cv)
        self.label_cv_volt.setGeometry(QtCore.QRect(0, 6, 252, 22))
        self.label_cv_volt.setObjectName("label_cv_volt")
        self.doubleSpin_cv_volt = QtWidgets.QDoubleSpinBox(page_cv)
        self.doubleSpin_cv_volt.setGeometry(QtCore.QRect(262, 2, 140, 30))
        self.doubleSpin_cv_volt.setDecimals(3)
        self.doubleSpin_cv_volt.setRange(0.0, 2000.0)
        self.doubleSpin_cv_volt.setObjectName("doubleSpin_cv_volt")
        _configure_spin_edit(self.doubleSpin_cv_volt)
        self.label_cv_rint = QtWidgets.QLabel(page_cv)
        self.label_cv_rint.setGeometry(QtCore.QRect(0, 44, 252, 22))
        self.label_cv_rint.setObjectName("label_cv_rint")
        self.doubleSpin_cv_rint = QtWidgets.QDoubleSpinBox(page_cv)
        self.doubleSpin_cv_rint.setGeometry(QtCore.QRect(262, 40, 140, 30))
        self.doubleSpin_cv_rint.setDecimals(6)
        self.doubleSpin_cv_rint.setRange(0.0, 1000000000.0)
        self.doubleSpin_cv_rint.setObjectName("doubleSpin_cv_rint")
        _configure_spin_edit(self.doubleSpin_cv_rint)
        page_cc = QtWidgets.QWidget()
        page_cc.setObjectName("page_orig_cc")
        self.label_cc_amp = QtWidgets.QLabel(page_cc)
        self.label_cc_amp.setGeometry(QtCore.QRect(0, 12, 252, 22))
        self.label_cc_amp.setObjectName("label_cc_amp")
        self.doubleSpin_cc_amp = QtWidgets.QDoubleSpinBox(page_cc)
        self.doubleSpin_cc_amp.setGeometry(QtCore.QRect(262, 8, 140, 30))
        self.doubleSpin_cc_amp.setDecimals(4)
        self.doubleSpin_cc_amp.setRange(0.0, 10000.0)
        self.doubleSpin_cc_amp.setObjectName("doubleSpin_cc_amp")
        _configure_spin_edit(self.doubleSpin_cc_amp)
        page_cp = QtWidgets.QWidget()
        page_cp.setObjectName("page_orig_cp")
        self.label_cp_kw = QtWidgets.QLabel(page_cp)
        self.label_cp_kw.setGeometry(QtCore.QRect(0, 12, 252, 22))
        self.label_cp_kw.setObjectName("label_cp_kw")
        self.doubleSpin_cp_kw = QtWidgets.QDoubleSpinBox(page_cp)
        self.doubleSpin_cp_kw.setGeometry(QtCore.QRect(262, 8, 140, 30))
        self.doubleSpin_cp_kw.setDecimals(4)
        self.doubleSpin_cp_kw.setRange(0.0, 30.0)
        self.doubleSpin_cp_kw.setObjectName("doubleSpin_cp_kw")
        _configure_spin_edit(self.doubleSpin_cp_kw)
        page_cr = QtWidgets.QWidget()
        page_cr.setObjectName("page_orig_cr")
        self.label_cr_rload = QtWidgets.QLabel(page_cr)
        self.label_cr_rload.setGeometry(QtCore.QRect(0, 12, 252, 22))
        self.label_cr_rload.setObjectName("label_cr_rload")
        self.doubleSpin_cr_rload = QtWidgets.QDoubleSpinBox(page_cr)
        self.doubleSpin_cr_rload.setGeometry(QtCore.QRect(262, 8, 140, 30))
        self.doubleSpin_cr_rload.setDecimals(6)
        self.doubleSpin_cr_rload.setRange(0.0, 1000000000.0)
        self.doubleSpin_cr_rload.setObjectName("doubleSpin_cr_rload")
        _configure_spin_edit(self.doubleSpin_cr_rload)
        self.stacked_orig_params.addWidget(page_cv)
        self.stacked_orig_params.addWidget(page_cc)
        self.stacked_orig_params.addWidget(page_cp)
        self.stacked_orig_params.addWidget(page_cr)
        self.pushButton_orig_outmode = QtWidgets.QPushButton(self.widget_orig_load)
        self.pushButton_orig_outmode.setGeometry(QtCore.QRect(0, 152, 300, 36))
        self.pushButton_orig_outmode.setObjectName("pushButton_orig_outmode")
        self.widget_orig_load.setVisible(False)
        self.label_hint = QtWidgets.QLabel(Dialog)
        self.label_hint.setGeometry(QtCore.QRect(20, 356, 520, 118))
        self.label_hint.setObjectName("label_hint")
        self.label_hint.setTextFormat(QtCore.Qt.RichText)
        self.label_hint.setWordWrap(True)
        self.label_hint.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.pushButton_ON = QtWidgets.QPushButton(Dialog)
        self.pushButton_ON.setGeometry(QtCore.QRect(20, 510, 130, 42))
        self.pushButton_ON.setObjectName("pushButton_ON")
        self.pushButton_OFF = QtWidgets.QPushButton(Dialog)
        self.pushButton_OFF.setGeometry(QtCore.QRect(170, 510, 130, 42))
        self.pushButton_OFF.setObjectName("pushButton_OFF")
        self.pushButton_close = QtWidgets.QPushButton(Dialog)
        self.pushButton_close.setGeometry(QtCore.QRect(330, 510, 130, 42))
        self.pushButton_close.setObjectName("pushButton_close")
        self.retranslateUi(Dialog)

    def retranslateUi(self, Dialog: QtWidgets.QDialog) -> None:
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog_Bluesight_DC_Setting", _z(0x84DD, 0x70B9, 0x76F4, 0x6D41, 0x8BBE, 0x5B9A)))
        self.label_model.setText(_format_model_banner_html("", ""))
        self.label_mode_title.setText(
            _translate(
                "Dialog_Bluesight_DC_Setting",
                _z(0x8F93, 0x51FA, 0x5DE5, 0x4F5C, 0x6A21, 0x5F0F, 0xFF1A),
            )
        )
        self.comboBox_mode.clear()
        self.comboBox_mode.addItems(
            [
                _translate("Dialog_Bluesight_DC_Setting", _z(0x539F, 0x8F7D)),
                _translate("Dialog_Bluesight_DC_Setting", "SAS"),
                _translate("Dialog_Bluesight_DC_Setting", _z(0x7535, 0x6C60, 0x6A21, 0x62DF, 0x5668)),
            ]
        )
        self.pushButton_apply_mode.setText(_translate("Dialog_Bluesight_DC_Setting", _z(0x5E94, 0x7528, 0x6A21, 0x5F0F)))
        self.label_pmpp.setText(_translate("Dialog_Bluesight_DC_Setting", "Pmpp_stc (kW)"))
        self.label_umpp.setText(_translate("Dialog_Bluesight_DC_Setting", "Umpp_stc (V)"))
        self.label_ff.setText(_translate("Dialog_Bluesight_DC_Setting", _z(0x586B, 0x5145, 0x56E0, 0x5B50, 0xFF1A)))
        self.pushButton_send_curve.setText(
            _translate(
                "Dialog_Bluesight_DC_Setting",
                _z(
                    0x53D1,
                    0x9001,
                    0x53C2,
                    0x6570,
                    0x5230,
                    0x8BBE,
                    0x5907,
                    0x0028,
                    0x66F2,
                    0x7EBF,
                    0x0029,
                ),
            )
        )
        self.label_orig_outmode.setText(
            _translate("Dialog_Bluesight_DC_Setting", _z(0x8F93, 0x51FA, 0x6A21, 0x5F0F, 0xFF1A))
        )
        self.comboBox_orig_outmode.clear()
        self.comboBox_orig_outmode.addItems(
            [
                _translate("Dialog_Bluesight_DC_Setting", _z(0x6052, 0x538B)),
                _translate("Dialog_Bluesight_DC_Setting", _z(0x6052, 0x6D41)),
                _translate("Dialog_Bluesight_DC_Setting", _z(0x6052, 0x529F, 0x7387)),
                _translate("Dialog_Bluesight_DC_Setting", _z(0x6052, 0x963B)),
            ]
        )
        self.pushButton_orig_outmode.setText(
            _translate("Dialog_Bluesight_DC_Setting", _z(0x53D1, 0x9001, 0x53C2, 0x6570))
        )
        self.label_cv_volt.setText(
            _translate(
                "Dialog_Bluesight_DC_Setting",
                _z(0x8F93, 0x51FA, 0x7535, 0x538B, 0xFF08, 0x0056, 0xFF09, 0xFF1A),
            )
        )
        self.label_cv_rint.setText(
            _translate(
                "Dialog_Bluesight_DC_Setting",
                _z(0x7535, 0x6E90, 0x5185, 0x963B)
                + "("
                + chr(0x03A9)
                + ")"
                + _z(0xFF1A),
            )
        )
        self.label_cc_amp.setText(
            _translate(
                "Dialog_Bluesight_DC_Setting",
                _z(0x8F93, 0x51FA, 0x7535, 0x6D41, 0xFF08, 0x0041, 0xFF09, 0xFF1A),
            )
        )
        self.label_cp_kw.setText(
            _translate(
                "Dialog_Bluesight_DC_Setting",
                _z(0x8F93, 0x51FA, 0x529F, 0x7387, 0xFF08, 0x006B, 0x0057, 0xFF09, 0xFF1A),
            )
        )
        self.label_cr_rload.setText(
            _translate(
                "Dialog_Bluesight_DC_Setting",
                _z(0x8D1F, 0x8F7D, 0x7535, 0x963B) + "(" + chr(0x03A9) + ")" + _z(0xFF1A),
            )
        )
        self.pushButton_ON.setText(_translate("Dialog_Bluesight_DC_Setting", _z(0x6253, 0x5F00, 0x8F93, 0x51FA)))
        self.pushButton_OFF.setText(_translate("Dialog_Bluesight_DC_Setting", _z(0x5173, 0x95ED, 0x8F93, 0x51FA)))
        self.pushButton_close.setText(_translate("Dialog_Bluesight_DC_Setting", _z(0x5173, 0x95ED, 0x7A97, 0x53E3)))
        self.label_hint.setText(_build_hint_rich_html())


_STR_NOT_DEV = _z(0x6682, 0x672A, 0x5F00, 0x53D1)
_STR_HINT_TITLE = _z(0x63D0, 0x793A)
_STR_NO_MB = _z(
    0x672A,
    0x8FDE,
    0x63A5,
    0x0020,
    0x004D,
    0x006F,
    0x0064,
    0x0062,
    0x0075,
    0x0073,
    0xFF0C,
    0x65E0,
    0x6CD5,
    0x8BBE,
    0x7F6E,
    0x6A21,
    0x5F0F,
)
_STR_MODE_TITLE = _z(0x6A21, 0x5F0F, 0x4E0B, 0x53D1)
_PREFIX_MODEL_ERR = _z(0x578B, 0x53F7, 0x8BFB, 0x53D6, 0x5F02, 0x5E38, 0xFF1A)
_PREFIX_MODEL_FAIL = _z(0x578B, 0x53F7, 0x8BFB, 0x53D6, 0x5931, 0x8D25, 0xFF1A)
_PREFIX_NO_MB_MODEL = _z(0x578B, 0x53F7, 0xFF1A, 0x672A, 0x8FDE, 0x63A5, 0x0020, 0x004D, 0x006F, 0x0064, 0x0062, 0x0075, 0x0073, 0xFF0C, 0x65E0, 0x6CD5, 0x8BFB, 0x53D6)
_TITLE_BS_DC = _z(0x84DD, 0x70B9, 0x76F4, 0x6D41, 0x7535, 0x6E90, 0x0020, 0x0044, 0x0043)
_SUFFIX_SETTINGS = _z(0x8BBE, 0x5B9A)
_STR_SEND_CURVE_TITLE = _z(0x66F2, 0x7EBF, 0x53D1, 0x9001)
_STR_ERR_TITLE = _z(0x9519, 0x8BEF)
_STR_ORIG_OUT_TITLE = _z(0x539F, 0x8F7D, 0x8F93, 0x51FA)


def run_bluesight_dc_setting_dialog(
    parent: Optional[QtWidgets.QWidget],
    dc_display_number: int,
    on_open: Callable[[], None],
    on_close: Callable[[], None],
    *,
    modbus_client: Optional[Any] = None,
    device_id: int = 1,
    device_ip: Optional[str] = None,
) -> None:
    dlg = QtWidgets.QDialog(parent)
    ui = Ui_Dialog_Bluesight_DC_Setting()
    ui.setupUi(dlg)
    dlg.setWindowTitle(f"{_TITLE_BS_DC}{dc_display_number} {_SUFFIX_SETTINGS}")

    sas_applied: list[bool] = [False]
    orig_applied: list[bool] = [False]
    def set_mode_switching_enabled(enabled: bool) -> None:
        """?????????????????????/?????????????????????????"""
        ui.pushButton_apply_mode.setEnabled(enabled)
        ui.comboBox_mode.setEnabled(enabled)
        ui.comboBox_orig_outmode.setEnabled(enabled)

    def sync_orig_params_page() -> None:
        ui.stacked_orig_params.setCurrentIndex(ui.comboBox_orig_outmode.currentIndex())

    def update_panel_visibility() -> None:
        idx = ui.comboBox_mode.currentIndex()
        ui.widget_sas_curve.setVisible(idx == 1 and sas_applied[0])
        ui.widget_orig_load.setVisible(idx == 0 and orig_applied[0])
        if idx == 0 and orig_applied[0]:
            sync_orig_params_page()

    def refresh_model() -> None:
        if modbus_client is None:
            ui.label_model.setText(
                '<div style="padding:10px 14px;border-radius:8px;background:#fff3f0;'
                'border:1px solid #ffcdd2;color:#b71c1c;font-size:12px;">'
                + html.escape(_PREFIX_NO_MB_MODEL)
                + "</div>"
            )
            return
        try:
            tr = BluesightTranslator(modbus_client, device_id=device_id)
            ok, text = tr.translate("*IDN?")
            if ok:
                seg = text.split(",", 1)[0].strip()
                ui.label_model.setText(_format_model_banner_html(seg, device_ip or ""))
            else:
                ui.label_model.setText(
                    '<div style="padding:8px 12px;color:#c62828;font-size:12px;">'
                    + html.escape(_PREFIX_MODEL_FAIL + text)
                    + "</div>"
                )
        except Exception as ex:
            ui.label_model.setText(
                '<div style="padding:8px 12px;color:#c62828;font-size:12px;">'
                + html.escape(_PREFIX_MODEL_ERR + str(ex))
                + "</div>"
            )

    def on_apply_mode() -> None:
        idx = ui.comboBox_mode.currentIndex()
        if idx == 2:
            sas_applied[0] = False
            orig_applied[0] = False
            update_panel_visibility()
            QtWidgets.QMessageBox.information(dlg, _STR_HINT_TITLE, _STR_NOT_DEV)
            return
        if modbus_client is None:
            QtWidgets.QMessageBox.warning(dlg, _STR_HINT_TITLE, _STR_NO_MB)
            return
        try:
            tr = BluesightTranslator(modbus_client, device_id=device_id)
            if idx == 0:
                ok, msg = tr.translate("SYST:MODE 0")
                orig_applied[0] = bool(ok)
                sas_applied[0] = False
            else:
                ok, msg = tr.translate("SYST:MODE SAS")
                sas_applied[0] = bool(ok)
                orig_applied[0] = False
            update_panel_visibility()
            fn = QtWidgets.QMessageBox.information if ok else QtWidgets.QMessageBox.warning
            fn(dlg, _STR_MODE_TITLE, (msg or "")[:800])
        except Exception as ex:
            sas_applied[0] = False
            orig_applied[0] = False
            update_panel_visibility()
            QtWidgets.QMessageBox.critical(dlg, _STR_ERR_TITLE, str(ex))

    def on_combo_mode_changed(_i: int = 0) -> None:
        update_panel_visibility()

    def on_apply_orig_outmode() -> None:
        if modbus_client is None:
            QtWidgets.QMessageBox.warning(dlg, _STR_HINT_TITLE, _STR_NO_MB)
            return
        if ui.comboBox_mode.currentIndex() != 0 or not orig_applied[0]:
            return
        try:
            tr = BluesightTranslator(modbus_client, device_id=device_id)
            idx_o = ui.comboBox_orig_outmode.currentIndex()
            if idx_o == 0:
                ok, msg = tr.write_original_load_params(
                    0,
                    voltage_v=ui.doubleSpin_cv_volt.value(),
                    r_internal_ohm=ui.doubleSpin_cv_rint.value(),
                )
            elif idx_o == 1:
                ok, msg = tr.write_original_load_params(
                    1,
                    current_a=ui.doubleSpin_cc_amp.value(),
                )
            elif idx_o == 2:
                ok, msg = tr.write_original_load_params(
                    2,
                    power_kw=ui.doubleSpin_cp_kw.value(),
                )
            else:
                ok, msg = tr.write_original_load_params(
                    3,
                    r_load_ohm=ui.doubleSpin_cr_rload.value(),
                )
            fn = QtWidgets.QMessageBox.information if ok else QtWidgets.QMessageBox.warning
            fn(dlg, _STR_ORIG_OUT_TITLE, (msg or "")[:800])
        except Exception as ex:
            QtWidgets.QMessageBox.critical(dlg, _STR_ERR_TITLE, str(ex))

    def on_send_curve() -> None:
        if modbus_client is None:
            QtWidgets.QMessageBox.warning(dlg, _STR_HINT_TITLE, _STR_NO_MB)
            return
        if ui.comboBox_mode.currentIndex() != 1:
            return
        try:
            stc = BluesightCurveSTC(
                pmpp_stc_kw=ui.doubleSpin_pmpp.value(),
                umpp_stc_v=ui.doubleSpin_umpp.value(),
                fill_factor=ui.doubleSpin_ff.value(),
            )
            tr = BluesightTranslator(modbus_client, device_id=device_id)
            ok, msg = tr.write_curve_block(stc=stc)
            fn = QtWidgets.QMessageBox.information if ok else QtWidgets.QMessageBox.warning
            fn(dlg, _STR_SEND_CURVE_TITLE, (msg or "")[:800])
        except ValueError as ve:
            QtWidgets.QMessageBox.warning(dlg, _STR_HINT_TITLE, str(ve))
        except Exception as ex:
            QtWidgets.QMessageBox.critical(dlg, _STR_ERR_TITLE, str(ex))

    def wrapped_open_output() -> None:
        on_open()
        set_mode_switching_enabled(False)

    def wrapped_close_output() -> None:
        on_close()
        set_mode_switching_enabled(True)

    ui.comboBox_mode.setCurrentIndex(1)
    refresh_model()
    update_panel_visibility()
    set_mode_switching_enabled(True)
    ui.comboBox_mode.currentIndexChanged.connect(on_combo_mode_changed)
    ui.comboBox_orig_outmode.currentIndexChanged.connect(lambda _i=0: sync_orig_params_page())
    ui.pushButton_apply_mode.clicked.connect(on_apply_mode)
    ui.pushButton_send_curve.clicked.connect(on_send_curve)
    ui.pushButton_orig_outmode.clicked.connect(on_apply_orig_outmode)
    ui.pushButton_ON.clicked.connect(wrapped_open_output)
    ui.pushButton_OFF.clicked.connect(wrapped_close_output)
    ui.pushButton_close.clicked.connect(dlg.accept)
    dlg.exec_()
