# -*- coding: utf-8 -*-
"""IOT 仪器勾选项写到桌面德威创面板。"""

from utils.dewetron_widget_apply import apply_dewetron_panel_widgets


class _FakeCheck:
    def __init__(self):
        self._v = False

    def isChecked(self):
        return self._v

    def setChecked(self, v):
        self._v = bool(v)


class _FakeEdit:
    def __init__(self):
        self._t = ""

    def text(self):
        return self._t

    def setText(self, t):
        self._t = str(t)


class _FakePanel:
    def __init__(self):
        self.checkBox_DEW_RealtimeWaveform = _FakeCheck()
        self.checkBox_DEW_ExportAbsTime = _FakeCheck()
        self.checkBox_DEW_KeepOxygenDmd = _FakeCheck()
        self.lineEdit_DEW_SaveDir = _FakeEdit()


def test_apply_abs_time_keep_dmd_save_dir_to_panel_widgets():
    panel = _FakePanel()
    done = apply_dewetron_panel_widgets(
        panel,
        {
            "checkBox_DEW_RealtimeWaveform": False,
            "checkBox_DEW_ExportAbsTime": True,
            "checkBox_DEW_KeepOxygenDmd": True,
            "lineEdit_DEW_SaveDir": r"%LOCALAPPDATA%\SolarAutoTest\dewetron_save",
        },
    )
    assert done["abs_time"] is True
    assert done["keep_dmd"] is True
    assert done["save_dir"] is True
    assert panel.checkBox_DEW_ExportAbsTime.isChecked() is True
    assert panel.checkBox_DEW_KeepOxygenDmd.isChecked() is True
    assert panel.checkBox_DEW_RealtimeWaveform.isChecked() is False
    assert "dewetron_save" in panel.lineEdit_DEW_SaveDir.text()
