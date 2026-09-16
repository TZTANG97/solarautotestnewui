# -*- coding: utf-8 -*-
from agent.main_loop import main

if __name__ == "__main__":
    # 独立进程：若被挂到可见控制台，先断开，避免闪黑窗
    try:
        import os

        if os.name == "nt":
            import ctypes

            ctypes.windll.kernel32.FreeConsole()
    except Exception:
        pass
    raise SystemExit(main())
