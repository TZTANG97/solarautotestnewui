import sys
from PyQt5 import QtWidgets
from components.buttons import StyledButton, ButtonStyle


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    w.setWindowTitle("Button Components Demo")
    layout = QtWidgets.QHBoxLayout(w)

    labels = ["默认按钮", "主要按钮", "成功按钮", "信息按钮", "警告按钮", "危险按钮"]
    styles = [
        ButtonStyle.DEFAULT,
        ButtonStyle.PRIMARY,
        ButtonStyle.SUCCESS,
        ButtonStyle.INFO,
        ButtonStyle.WARNING,
        ButtonStyle.DANGER,
    ]

    for label, style in zip(labels, styles):
        btn = StyledButton(label, style)
        btn.setMinimumWidth(100)
        layout.addWidget(btn)

    disabled_btn = StyledButton("禁用按钮", ButtonStyle.PRIMARY)
    disabled_btn.setEnabled(False)
    layout.addWidget(disabled_btn)

    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
