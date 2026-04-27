"""试验设定抽象层包。"""

from .base_setup import BaseSetup
from .main_setup import MainSetup, initialize_setup_windows


__all__ = [
    "BaseSetup",
    "MainSetup",
    "initialize_setup_windows",
]
