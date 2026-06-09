import logging
import os
import re
import sys
import traceback
from logging.handlers import TimedRotatingFileHandler


def setup_logging(base_dir):
    logger = logging.getLogger('auto_test')
    logger.setLevel(logging.INFO)

    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(base_dir, 'command_save_files', 'auto_test.log'),
        when='H',
        interval=24,
    )
    file_handler.suffix = r'%Y-%m-%d_%H-%M-%S.log'
    file_handler.extMatch = re.compile(r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}.log$')
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s %(filename)s [%(lineno)d] %(threadName)s :%(message)s')
    )
    logger.addHandler(file_handler)

    log_txt_path = os.path.join(base_dir, 'log.txt')
    log_txt_handler = logging.FileHandler(log_txt_path, encoding='utf-8')
    log_txt_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(log_txt_handler)

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


def install_exception_hook(logger, original_stderr):
    def _handle_exception(exc_type, exc_value, exc_tb):
        logger.error('Uncaught exception', exc_info=(exc_type, exc_value, exc_tb))
        if original_stderr is not None:
            traceback.print_exception(exc_type, exc_value, exc_tb, file=original_stderr)

    sys.excepthook = _handle_exception
    return _handle_exception
