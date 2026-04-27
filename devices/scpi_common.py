def _configure_scpi_resource(handle):
    if handle is None:
        return
    try:
        handle.timeout = 10000
    except Exception:
        pass
    try:
        handle.read_termination = '\n'
        handle.write_termination = '\n'
    except Exception:
        pass
