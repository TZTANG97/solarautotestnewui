# -*- coding: ascii -*-
"""Bluesight DC settings dialog (ASCII source + chr() for UI text; avoids GBK-mojibake on Windows)."""

from __future__ import annotations

from typing import Any, Callable, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from scpi_to_modbustcp import BluesightCurveSTC, BluesightTranslator


def _z(*codes: int) -> str:
    return "".join(chr(c) for c in codes)


class Ui_Dialog_Bluesight_DC_Setting:
    def setupUi(self, Dialog: QtWidgets.QDialog) -> None:
        Dialog.setObjectName("Dialog_Bluesight_DC_Setting")
        Dialog.resize(560, 470)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(".\\ui_files\\logo.jpg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On,
        )
        Dialog.setWindowIcon(icon)
        self.label_model = QtWidgets.QLabel(Dialog)
        self.label_model.setGeometry(QtCore.QRect(20, 12, 480, 40))
        self.label_model.setObjectName("label_model")
        self.label_mode_title = QtWidgets.QLabel(Dialog)
        self.label_mode_title.setGeometry(QtCore.QRect(20, 56, 380, 22))
        self.label_mode_title.setObjectName("label_mode_title")
        self.comboBox_mode = QtWidgets.QComboBox(Dialog)
        self.comboBox_mode.setGeometry(QtCore.QRect(20, 82, 200, 32))
        self.comboBox_mode.setObjectName("comboBox_mode")
        self.pushButton_apply_mode = QtWidgets.QPushButton(Dialog)
        self.pushButton_apply_mode.setGeometry(QtCore.QRect(240, 80, 120, 36))
        self.pushButton_apply_mode.setObjectName("pushButton_apply_mode")
        self.widget_sas_curve = QtWidgets.QWidget(Dialog)
        self.widget_sas_curve.setGeometry(QtCore.QRect(20, 118, 510, 158))
        self.widget_sas_curve.setObjectName("widget_sas_curve")
        self.label_pmpp = QtWidgets.QLabel(self.widget_sas_curve)
        self.label_pmpp.setGeometry(QtCore.QRect(0, 6, 200, 22))
        self.label_pmpp.setObjectName("label_pmpp")
        self.doubleSpin_pmpp = QtWidgets.QDoubleSpinBox(self.widget_sas_curve)
        self.doubleSpin_pmpp.setGeometry(QtCore.QRect(210, 2, 140, 30))
        self.doubleSpin_pmpp.setDecimals(3)
        self.doubleSpin_pmpp.setRange(0.001, 65.535)
        self.doubleSpin_pmpp.setValue(8.0)
        self.doubleSpin_pmpp.setObjectName("doubleSpin_pmpp")
        self.label_umpp = QtWidgets.QLabel(self.widget_sas_curve)
        self.label_umpp.setGeometry(QtCore.QRect(0, 44, 200, 22))
        self.label_umpp.setObjectName("label_umpp")
        self.doubleSpin_umpp = QtWidgets.QDoubleSpinBox(self.widget_sas_curve)
        self.doubleSpin_umpp.setGeometry(QtCore.QRect(210, 40, 140, 30))
        self.doubleSpin_umpp.setDecimals(2)
        self.doubleSpin_umpp.setRange(0.0, 2000.0)
        self.doubleSpin_umpp.setValue(650.0)
        self.doubleSpin_umpp.setObjectName("doubleSpin_umpp")
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
        self.pushButton_send_curve = QtWidgets.QPushButton(self.widget_sas_curve)
        self.pushButton_send_curve.setGeometry(QtCore.QRect(0, 118, 280, 36))
        self.pushButton_send_curve.setObjectName("pushButton_send_curve")
        self.widget_sas_curve.setVisible(False)
        self.label_hint = QtWidgets.QLabel(Dialog)
        self.label_hint.setGeometry(QtCore.QRect(20, 282, 510, 95))
        self.label_hint.setObjectName("label_hint")
        self.label_hint.setWordWrap(True)
        self.label_hint.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.pushButton_ON = QtWidgets.QPushButton(Dialog)
        self.pushButton_ON.setGeometry(QtCore.QRect(20, 388, 130, 42))
        self.pushButton_ON.setObjectName("pushButton_ON")
        self.pushButton_OFF = QtWidgets.QPushButton(Dialog)
        self.pushButton_OFF.setGeometry(QtCore.QRect(170, 388, 130, 42))
        self.pushButton_OFF.setObjectName("pushButton_OFF")
        self.pushButton_close = QtWidgets.QPushButton(Dialog)
        self.pushButton_close.setGeometry(QtCore.QRect(330, 388, 130, 42))
        self.pushButton_close.setObjectName("pushButton_close")
        self.retranslateUi(Dialog)

    def retranslateUi(self, Dialog: QtWidgets.QDialog) -> None:
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog_Bluesight_DC_Setting", _z(0x84DD, 0x70B9, 0x76F4, 0x6D41, 0x8BBE, 0x5B9A)))
        self.label_model.setText(_translate("Dialog_Bluesight_DC_Setting", _z(0x578B, 0x53F7, 0xFF1A, 0x8BFB, 0x53D6, 0x4E2D, 0x2026)))
        self.label_mode_title.setText(
            _translate(
                "Dialog_Bluesight_DC_Setting",
                _z(
                    0x8F93,
                    0x51FA,
                    0x5DE5,
                    0x4F5C,
                    0x6A21,
                    0x5F0F,
                    0xFF08,
                    0x5BF9,
                    0x5E94,
                    0x0020,
                    0x0030,
                    0x0078,
                    0x0030,
                    0x0046,
                    0x0039,
                    0x0035,
                    0xFF1A,
                    0x539F,
                    0x8F7D,
                    0x003D,
                    0x0030,
                    0xFF0C,
                    0x0053,
                    0x0041,
                    0x0053,
                    0x003D,
                    0x0031,
                    0xFF0C,
                    0x7535,
                    0x6C60,
                    0x6A21,
                    0x62DF,
                    0x5668,
                    0x003D,
                    0x0032,
                    0xFF09,
                ),
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
        self.pushButton_ON.setText(_translate("Dialog_Bluesight_DC_Setting", _z(0x6253, 0x5F00, 0x8F93, 0x51FA)))
        self.pushButton_OFF.setText(_translate("Dialog_Bluesight_DC_Setting", _z(0x5173, 0x95ED, 0x8F93, 0x51FA)))
        self.pushButton_close.setText(_translate("Dialog_Bluesight_DC_Setting", _z(0x5173, 0x95ED, 0x7A97, 0x53E3)))
        self.label_hint.setText(
            _translate(
                "Dialog_Bluesight_DC_Setting",
                _z(
                    0x5F53,
                    0x524D,
                    0x901A,
                    0x9053,
                    0x5DF2,
                    0x8BC6,
                    0x522B,
                    0x4E3A,
                    0x84DD,
                    0x70B9,
                    0xFF08,
                    0x004D,
                    0x006F,
                    0x0064,
                    0x0062,
                    0x0075,
                    0x0073,
                    0x0020,
                    0x0054,
                    0x0043,
                    0x0050,
                    0xFF09,
                    0x3002,
                    0x81F4,
                    0x8302,
                    0x5BF9,
                    0x8BDD,
                    0x6846,
                    0x4E2D,
                    0x7684,
                    0x0020,
                    0x0056,
                    0x006D,
                    0x0070,
                    0x002F,
                    0x0049,
                    0x006D,
                    0x0070,
                    0x002F,
                    0x0056,
                    0x006F,
                    0x0063,
                    0x002F,
                    0x0049,
                    0x0073,
                    0x0063,
                    0x002F,
                    0x0050,
                    0x0046,
                    0x0020,
                    0x7B49,
                    0x4E3A,
                    0x9635,
                    0x5217,
                    0x0020,
                    0x0049,
                    0x0056,
                    0x0020,
                    0x53C2,
                    0x6570,
                    0xFF1B,
                    0x84DD,
                    0x70B9,
                    0x66F2,
                    0x7EBF,
                    0x7531,
                    0x0020,
                    0x0053,
                    0x0054,
                    0x0043,
                    0x0020,
                    0x5BC4,
                    0x5B58,
                    0x5668,
                    0x5757,
                    0x4E0E,
                    0x0020,
                    0x0042,
                    0x006C,
                    0x0075,
                    0x0065,
                    0x0073,
                    0x0069,
                    0x0067,
                    0x0068,
                    0x0074,
                    0x0054,
                    0x0072,
                    0x0061,
                    0x006E,
                    0x0073,
                    0x006C,
                    0x0061,
                    0x0074,
                    0x006F,
                    0x0072,
                    0x0020,
                    0x6620,
                    0x5C04,
                    0xFF0C,
                    0x8BF7,
                    0x52FF,
                    0x6DF7,
                    0x7528,
                    0x3002,
                )
                + "\n\n"
                + _z(
                    0x300C,
                    0x5E94,
                    0x7528,
                    0x6A21,
                    0x5F0F,
                    0x300D,
                    0xFF1A,
                    0x4EC5,
                    0x0020,
                    0x0053,
                    0x0041,
                    0x0053,
                    0x0020,
                    0x5DF2,
                    0x63A5,
                    0x5165,
                    0x5BC4,
                    0x5B58,
                    0x5668,
                    0x4E0B,
                    0x53D1,
                    0xFF1B,
                    0x539F,
                    0x8F7D,
                    0x3001,
                    0x7535,
                    0x6C60,
                    0x6A21,
                    0x62DF,
                    0x5668,
                    0x9009,
                    0x62E9,
                    0x540E,
                    0x5C06,
                    0x63D0,
                    0x793A,
                    0x6682,
                    0x672A,
                    0x5F00,
                    0x53D1,
                    0x3002,
                )
                + "\n\n"
                + _z(
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
                ),
            )
        )


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


def run_bluesight_dc_setting_dialog(
    parent: Optional[QtWidgets.QWidget],
    dc_display_number: int,
    on_open: Callable[[], None],
    on_close: Callable[[], None],
    *,
    modbus_client: Optional[Any] = None,
    device_id: int = 1,
) -> None:
    dlg = QtWidgets.QDialog(parent)
    ui = Ui_Dialog_Bluesight_DC_Setting()
    ui.setupUi(dlg)
    dlg.setWindowTitle(f"{_TITLE_BS_DC}{dc_display_number} {_SUFFIX_SETTINGS}")

    sas_applied: list[bool] = [False]

    def update_sas_curve_visibility() -> None:
        show = ui.comboBox_mode.currentIndex() == 1 and sas_applied[0]
        ui.widget_sas_curve.setVisible(show)

    def refresh_model() -> None:
        if modbus_client is None:
            ui.label_model.setText(_PREFIX_NO_MB_MODEL)
            return
        try:
            tr = BluesightTranslator(modbus_client, device_id=device_id)
            ok, text = tr.translate("*IDN?")
            if ok:
                ui.label_model.setText(_z(0x578B, 0x53F7, 0xFF1A) + text)
            else:
                ui.label_model.setText(_PREFIX_MODEL_FAIL + text)
        except Exception as ex:
            ui.label_model.setText(_PREFIX_MODEL_ERR + str(ex))

    def on_apply_mode() -> None:
        idx = ui.comboBox_mode.currentIndex()
        if idx == 0 or idx == 2:
            sas_applied[0] = False
            update_sas_curve_visibility()
            QtWidgets.QMessageBox.information(dlg, _STR_HINT_TITLE, _STR_NOT_DEV)
            return
        if modbus_client is None:
            QtWidgets.QMessageBox.warning(dlg, _STR_HINT_TITLE, _STR_NO_MB)
            return
        try:
            tr = BluesightTranslator(modbus_client, device_id=device_id)
            ok, msg = tr.translate("SYST:MODE SAS")
            sas_applied[0] = bool(ok)
            update_sas_curve_visibility()
            fn = QtWidgets.QMessageBox.information if ok else QtWidgets.QMessageBox.warning
            fn(dlg, _STR_MODE_TITLE, (msg or "")[:800])
        except Exception as ex:
            sas_applied[0] = False
            update_sas_curve_visibility()
            QtWidgets.QMessageBox.critical(dlg, _STR_ERR_TITLE, str(ex))

    def on_combo_mode_changed(_i: int = 0) -> None:
        update_sas_curve_visibility()

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

    ui.comboBox_mode.setCurrentIndex(1)
    refresh_model()
    update_sas_curve_visibility()
    ui.comboBox_mode.currentIndexChanged.connect(on_combo_mode_changed)
    ui.pushButton_apply_mode.clicked.connect(on_apply_mode)
    ui.pushButton_send_curve.clicked.connect(on_send_curve)
    ui.pushButton_ON.clicked.connect(on_open)
    ui.pushButton_OFF.clicked.connect(on_close)
    ui.pushButton_close.clicked.connect(dlg.accept)
    dlg.exec_()
