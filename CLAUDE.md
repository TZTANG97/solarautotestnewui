# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Photovoltaic (solar) inverter automated test system. A PyQt5 desktop application that controls AC/DC power supplies, power analyzers (WT3000/WT1800/WT1806E/WT5000), and oscilloscopes (DL850) via SCPI/Modbus TCP to run standardized compliance tests. The UI is primarily in Chinese.

## Running the Application

**必须使用 Conda 虚拟环境 `SolarAutoTestEnv`。** 本项目中所有测试、运行、代码审查都必须在此环境下执行。

```bash
conda activate SolarAutoTestEnv
python SCPITestWave.py
```

No build step. Python 3.10+ required. Install dependencies:

```bash
conda activate SolarAutoTestEnv
pip install -r requirements.txt
```

Key dependencies: PyQt5, pyvisa, pymodbus, pyautogui, pywin32, numpy, xlwt.

## Architecture

### Entry Point

`SCPITestWave.py` (~27,500 lines) is the monolithic main file. It contains the main window class, all test flow logic, device connection handlers, and the `if __name__ == "__main__"` block. This file is being incrementally refactored — see `app/`, `devices/`, `setup/`, `config/` for extracted modules.

### Device Layer (`devices/`)

Each instrument type has a controller class that encapsulates connect/disconnect/query logic:

- **`ACController`** —交流电源 (AC source). Supports both VISA/SCPI and Modbus TCP paths. Uses `ItechTranslator` for 爱科 (Itech) Modbus register translation.
- **`DCController`** — 直流电源 (DC source, up to 4 channels: DC1–DC4). Supports SCPI and Modbus TCP (蓝点/Bluesight). Register `0x0BB8` controls output on/off.
- **`WT3000Controller`** — Yokogawa power analyzer. Tries multiple VISA resource string formats on connect.
- **`DL850Controller`** — Yokogawa oscilloscope. Simple SCPI START/STOP/SAVE.
- **`handle_release.py`** — Unified handle cleanup (`release_resource_handle`). Must be called before reconnecting to avoid USBTMC errors.
- **`scpi_common.py`** — Shared SCPI resource configuration (timeout, termination, serial params).

### Modbus/SCPI Translation (`scpi_to_modbustcp.py`)

- **`ItechTranslator`** — Translates SCPI commands to Itech AC source Modbus registers.
- **`BluesightTranslator`** — Translates SCPI commands to Bluesight DC source Modbus registers.

### Modbus Transport (`modbus_visa.py`)

`ModbusVISA` class wraps both PyVISA TCPIP SOCKET and raw Python `socket` for Modbus TCP. Handles idle reconnection, frame parsing (MBAP), and automatic retry on `CONN_LOST`. The `use_plain_socket=True` path bypasses PyVISA for devices with半连接 issues.

### Application Context (`app/`)

- **`context.py`** — `AppContext` dataclass holds all shared runtime state (controllers, dialogs, connection flags). Access via `get_app_context()` singleton.
- **`bootstrap.py`** — Startup assembly: wires UI, logger, and VISA ResourceManager into `AppContext`.

### Setup Layer (`setup/`)

- **`base_setup.py`** — Abstract `BaseSetup` class defining the contract for test setup modules.
- **`main_setup.py`** — `MainSetup` creates all test setting dialogs (QDialog instances) and registers them in `AppContext`.

### UI Files

- `ui_files/` — `.ui` files for Qt Designer. Generated Python UI classes live at the repo root as `Dialog_*.py` files (e.g., `Dialog_thaiWT3000E.py`).
- Regenerate with: `pyuic5 ui_files/Foo.ui -o Dialog_Foo.py`
- **Never edit generated `Dialog_*.py` files directly** — changes will be overwritten.

### Test Configurations

Each test type has:
- A `Dialog_thai*.py` UI dialog (generated from `.ui`)
- An `Open_Save_Thai*.py` utility for loading/saving test parameters
- Some tests have config managers in `config_manager/`

### Recordings & Macro Playback (`RecPlayer/`)

`MacroManager` plays back recorded mouse/keyboard macros (JSON files in `recordings/`) to interact with WTViewerEfree software. Coordinate enums in `enums/wt_auto_enums.py` define click positions relative to the WT viewer window.

### Configuration

- `config_files/config.ini` — Paths to external executables (WTViewerEfree, Chroma MPPT tool).
- `config/app_config.py` — Reads the INI file via `configparser`.
- `config/path_config.py` — Derives recording paths from the repo root (`recordings/WT3000/`, etc.).

## Key Patterns

- **Dual protocol paths**: Many controllers support both SCPI (VISA) and Modbus TCP. Check `self.client is not None` to determine which path is active.
- **Handle lifecycle**: Always use `release_resource_handle()` before reconnecting. Never close a handle without releasing it first.
- **Thread safety**: `ModbusVISA` uses `threading.RLock` (not `Lock`) because `send()` can recursively reconnect.
- **Coordinate-based automation**: WT viewer interaction uses absolute screen coordinates derived from window-relative offsets in `enums/wt_auto_enums.py`.

## Cursor Rules

- Every function in `devices/dc_controller.py` must include a short docstring describing its purpose.
- Keep functions small and focused; extract shared logic into reusable helpers.
