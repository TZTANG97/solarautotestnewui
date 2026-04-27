import sys
import traceback


def install_exception_hook(logger, original_stderr):
    def _handle_exception(exc_type, exc_value, exc_tb):
        logger.error('Uncaught exception', exc_info=(exc_type, exc_value, exc_tb))
        if original_stderr is not None:
            traceback.print_exception(exc_type, exc_value, exc_tb, file=original_stderr)

    sys.excepthook = _handle_exception
    return _handle_exception
