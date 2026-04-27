from PyQt5.QtWidgets import QMessageBox


def _show_connect_message(msg, parent=None):
    try:
        QMessageBox.information(parent, '连接提示', msg, QMessageBox.Ok, QMessageBox.Ok)
    except Exception:
        pass


def _toggle_connection_button(connected_button_name, connected):
    return connected_button_name, connected


def _safe_close_handle(handle):
    try:
        if handle is not None:
            handle.close()
    except Exception:
        pass
