from PyQt5.QtWidgets import QMessageBox


def _show_connect_message(msg, parent=None):
    try:
        QMessageBox.information(parent, '连接提示', msg, QMessageBox.Ok, QMessageBox.Ok)
    except Exception:
        pass


def _toggle_connection_button(connected_button_name, connected):
    return connected_button_name, connected


def _safe_close_handle(handle):
    """释放 VISA/Modbus 句柄；与 ``devices.handle_release`` 对齐（勿仅 ``close()``，否则 Modbus 包装无法断开）。"""
    try:
        from devices.handle_release import release_resource_handle

        release_resource_handle(handle)
    except Exception:
        pass
