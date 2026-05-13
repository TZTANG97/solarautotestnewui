"""统一释放仪器句柄（VISA/Modbus 包装等）。

后台线程或错误恢复路径在 ``open_resource`` 打开同地址新会话之前，**必须先**释放旧句柄，
否则 USBTMC 上易出现 ``VI_ERROR_SYSTEM_ERROR`` / 重连看似成功仍不可用；与 UI 上先断开再连接的行为对齐。
"""


def release_resource_handle(handle):
    """关闭设备句柄：PyVISA 资源用 ``close()``；带 ``disconnect`` 的包装（如 ModbusVISA）用 ``disconnect``。

    逻辑与 ``SCPITestWave._safe_close_handle`` 历史实现一致，供控制器与主程序共用。
    """
    try:
        if handle is None:
            return
        close_fn = getattr(handle, "close", None)
        if callable(close_fn):
            close_fn()
            print("关闭设备成功")
            return
        disconnect_fn = getattr(handle, "disconnect", None)
        if callable(disconnect_fn):
            try:
                disconnect_fn(quiet=True)
            except TypeError:
                disconnect_fn()
            print("断开设备成功")
            return
    except Exception as e:
        print(f"关闭设备失败: {e}")
