from PyQt5.QtWidgets import QMessageBox


def _remote_connect_silent() -> bool:
    try:
        from utils.iot_remote_ui import remote_connect_silent

        return bool(remote_connect_silent())
    except Exception:
        return False


def _show_connect_message(msg, parent=None):
    # 云端下发的连接在后台执行：弹模态框会把整个自动化软件卡住（人在网页上看不到这个框）
    if _remote_connect_silent():
        print(f'[连接提示] {msg}')
        return
    try:
        QMessageBox.information(None, '连接提示', msg, QMessageBox.Ok, QMessageBox.Ok)
    except Exception:
        print(f'[连接提示] {msg}')


def _toggle_connection_button(connected_button_name, connected):
    return connected_button_name, connected


def _safe_close_handle(handle):
    """释放 VISA/Modbus 句柄；与 ``devices.handle_release`` 对齐（勿仅 ``close()``，否则 Modbus 包装无法断开）。"""
    try:
        from devices.handle_release import release_resource_handle

        release_resource_handle(handle)
    except Exception:
        pass
