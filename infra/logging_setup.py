import logging
import os
import sys
import traceback
from datetime import datetime


class DailyFileHandler(logging.Handler):
    """按天写入日志文件：data_logs/auto_test_YYYY-MM-DD.log"""

    def __init__(self, log_dir):
        super().__init__()
        self.log_dir = log_dir
        self._current_date = None
        self._stream = None
        self._rotate()

    def _rotate(self):
        if self._stream:
            self._stream.close()
        today = datetime.now().strftime('%Y-%m-%d')
        self._current_date = today
        os.makedirs(self.log_dir, exist_ok=True)
        filepath = os.path.join(self.log_dir, f'auto_test_{today}.log')
        self._stream = open(filepath, 'a', encoding='utf-8')

    def emit(self, record):
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            if today != self._current_date:
                self._rotate()
            msg = self.format(record)
            self._stream.write(msg + '\n')
            self._stream.flush()
        except Exception:
            self.handleError(record)

    def close(self):
        if self._stream:
            self._stream.close()
        super().close()


def setup_logging(base_dir):
    logger = logging.getLogger('auto_test')
    logger.setLevel(logging.INFO)

    log_dir = os.path.join(base_dir, 'data_logs')
    file_handler = DailyFileHandler(log_dir)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s %(filename)s [%(lineno)d] %(threadName)s :%(message)s')
    )
    logger.addHandler(file_handler)

    return logger


class StdoutToLogger:
    def __init__(self, logger, level):
        self._logger = logger
        self._level = level
        self._buffer = ''
        self._in_write = False  # 防止递归

    def write(self, msg):
        if msg is None or self._in_write:
            return
        self._in_write = True
        try:
            self._buffer += msg
            while '\n' in self._buffer:
                line, self._buffer = self._buffer.split('\n', 1)
                line = line.rstrip()
                if line:
                    self._logger.log(self._level, line)
        except Exception:
            pass
        finally:
            self._in_write = False

    def flush(self):
        if self._in_write:
            return
        self._in_write = True
        try:
            if self._buffer.strip():
                self._logger.log(self._level, self._buffer.strip())
                self._buffer = ''
        except Exception:
            pass
        finally:
            self._in_write = False


class Tee:
    def __init__(self, *streams):
        self._streams = streams

    def write(self, msg):
        for stream in self._streams:
            stream.write(msg)

    def flush(self):
        for stream in self._streams:
            stream.flush()


def install_stream_logging(logger):
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = Tee(original_stdout, StdoutToLogger(logger, logging.INFO))
    sys.stderr = Tee(original_stderr, StdoutToLogger(logger, logging.ERROR))
    return original_stdout, original_stderr


class UILogHandler(logging.Handler):
    """将日志消息写入 Qt QTextEdit 控件。"""

    def __init__(self, text_edit):
        super().__init__()
        self._text_edit = text_edit

    def emit(self, record):
        try:
            msg = self.format(record)
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(0, lambda m=msg: self._append(m))
        except Exception:
            self.handleError(record)

    def _append(self, msg):
        try:
            self._text_edit.append(msg)
            sb = self._text_edit.verticalScrollBar()
            if sb is not None:
                sb.setValue(sb.maximum())
        except Exception:
            pass


def install_exception_hook(logger, original_stderr):
    def _handle_exception(exc_type, exc_value, exc_tb):
        logger.error('Uncaught exception', exc_info=(exc_type, exc_value, exc_tb))
        if original_stderr is not None:
            traceback.print_exception(exc_type, exc_value, exc_tb, file=original_stderr)

    sys.excepthook = _handle_exception
    return _handle_exception
