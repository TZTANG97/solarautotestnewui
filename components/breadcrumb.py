"""面包屑导航组件。

样式参考：首页 / 活动管理 / 活动列表
当前项加粗，非当前项常规字重，用 "/" 分隔。
"""

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget


class BreadcrumbWidget(QWidget):
    """水平面包屑导航，点击切换页面。"""

    indexChanged = pyqtSignal(int)

    _SEP_QSS = "color: #94a3b8; font-size: 13px; background: transparent; padding: 0 4px;"
    _ACTIVE_QSS = "color: #1e293b; font-size: 13px; background: transparent;"
    _INACTIVE_QSS = "color: #64748b; font-size: 13px; background: transparent;"

    def __init__(self, labels: list[str], parent=None):
        super().__init__(parent)
        self._labels = labels
        self._current = 0
        self._items: list[QLabel] = []

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 6)
        lay.setSpacing(0)

        for i, text in enumerate(labels):
            if i > 0:
                sep = QLabel("/")
                sep.setStyleSheet(self._SEP_QSS)
                sep.setAlignment(Qt.AlignCenter)
                lay.addWidget(sep)

            lbl = QLabel(text)
            lbl.setCursor(Qt.PointingHandCursor)
            lbl.setStyleSheet(self._ACTIVE_QSS)
            font = lbl.font()
            font.setBold(True)
            lbl.setFont(font)
            lbl.mousePressEvent = lambda _e, idx=i: self.setIndex(idx)
            lay.addWidget(lbl)
            self._items.append(lbl)

        lay.addStretch(1)
        self._apply_style()

    def setIndex(self, idx: int):
        if idx == self._current or idx < 0 or idx >= len(self._items):
            return
        self._current = idx
        self._apply_style()
        self.indexChanged.emit(idx)

    def index(self) -> int:
        return self._current

    def _apply_style(self):
        active_font = QFont()
        active_font.setBold(True)
        inactive_font = QFont()
        inactive_font.setBold(False)

        for i, lbl in enumerate(self._items):
            if i == self._current:
                lbl.setStyleSheet(self._ACTIVE_QSS)
                lbl.setFont(active_font)
            else:
                lbl.setStyleSheet(self._INACTIVE_QSS)
                lbl.setFont(inactive_font)
