def _configure_scpi_resource(handle):
    """SCPI 会话通用配置；串口 ASRL 需波特率等与电源一致，否则 query 易 VI_ERROR_TMO。"""
    if handle is None:
        return
    try:
        rname = str(getattr(handle, 'resource_name', '') or '')
    except Exception:
        rname = ''
    is_asrl = 'ASRL' in rname.upper()
    try:
        handle.timeout = 15000 if is_asrl else 10000
    except Exception:
        pass
    try:
        handle.read_termination = '\n'
        handle.write_termination = '\n'
    except Exception:
        pass
    if is_asrl:
        vc = __import__('pyvisa').constants
        try:
            handle.baud_rate = 9600
        except Exception:
            pass
        try:
            handle.data_bits = 8
        except Exception:
            pass
        try:
            handle.parity = vc.Parity.none
        except Exception:
            pass
        try:
            handle.stop_bits = vc.StopBits.one
        except Exception:
            pass
        try:
            handle.flow_control = vc.VI_ASRL_FLOW_NONE
        except Exception:
            pass
