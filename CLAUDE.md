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
- **`DewetronController`** — DEWETRON OXYGEN 功率分析仪. TCP SCPI (port 10001, ASCII, CR+LF terminator). 只允许 1 个客户端连接。配置通过 XML 上传。
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

## 常见问题与解决方案

### PyVISA / SCPI 通信
- **`write_raw` 超时**: PyVISA 的 `write_raw()` 发送二进制数据时可能超时。改用 `write()` 发送字符串格式（将二进制 header 嵌入字符串）。
- **GBK Unicode 错误**: Windows 控制台默认 GBK 编码，`✓` 等 Unicode 字符无法输出。用 `[OK]` / `[FAIL]` 替代。
- **`read_termination` 警告**: `read string doesn't end with termination characters` — DEWETRON 返回的数据可能不含终止符，可忽略。

### Python 日志 / print 递归
- `print()` → `Tee` → `StdoutToLogger` → logging error → `handleError` → `print()` → 无限递归
- 修复: `StdoutToLogger.write()` 中加 `_in_write` flag 防止重入

### XML 处理
- 去掉 XML 声明: `re.sub(r'<\?xml[^?]*\?>', '', xml)`
- 字符串替换时用 `re.sub` + 命名组比直接切片更安全
- 大 XML (200K+) 用 IEEE 488.2 格式传输，不要用引号包裹的字符串格式

## DEWETRON OXYGEN 特殊注意事项

### SCPI 连接
- 端口 10001，编码 ASCII，终止符 CR+LF (`\r\n`)
- **只允许 1 个客户端连接** — 远程桌面或 raw socket 测试会阻断 VISA 连接
- VISA 资源字符串格式: `TCPIP0::<IP>::10001::SOCKET`

### `:SETUP:APPLY` 命令格式
- **必须使用 IEEE 488.2 定长块格式**，不是字符串格式
- 正确格式: `:SETUP:APPLY #<NUM_INT><NUM_CHAR><XML_DATA>`
- 示例: XML 236387 字节 → `:SETUP:APPLY #6236387<xml...>`
- `<NUM_INT>` = `<NUM_CHAR>` 的位数（1-9），`<NUM_CHAR>` = XML 字节数
- 错误格式会返回 `-102 "Syntax error"` 或 `-200 "Execution error"`

### `:SETUP:READ?` 返回值
- 返回的 XML 前面有 SCPI 响应前缀，如 `:SET:READ #6236385`
- 必须找到 `<?xml` 位置并截取后面的 XML 内容
- XML 可能含中文，需用 UTF-8 编码读取

### Channel ID 映射
- DEWETRON XML 中电流通道用大写 `I`（如 `AI 1/I1`），UI 中用小写 `l`（如 `AI 1/l1`）
- **ChannelID 是动态分配的**，每次设备加载配置/创建电力组时都会重新生成，不能硬编码
- **必须每次从设备读取**：通过 `read_channel_id_map()` 获取当前 ChannelID，不能用本地模板文件
- `modify_xml()` 接受 `channel_id_map` 参数，动态查找 ShortId -> ChannelID
- 未映射的通道 ChannelID = `18446744073709551615` (0xFFFFFFFFFFFFFFFF)

### 配置保存流程（SaveDEWETRONConfig）
- **不要用本地 XML 模板文件** — ChannelID 每次都变，模板会过期导致映射丢失
- 正确流程：
  1. `read_channel_id_map()` → 从设备读取当前 XML 和 ChannelID 映射
  2. `read_input_channels(xml)` → 从同一个 XML 解析 InputChannels
  3. `modify_xml()` → 修改 WiringType、Used/Neon/Active、InputChannels
  4. `send_apply_config()` → 发送到设备

### InputChannels 映射
- `modify_xml()` 根据 UI 选择的通道（channel_map）+ 当前设备 ChannelID 构建 InputChannels
- UI 选择 `U1 <- AI 1/U2` → `InputChannels/U1` 的 ChannelID 设为 AI 1/U2 的当前 ChannelID
- 未在 UI 中选择的槽位设为 UNUSED
- 设备接受 SCPI 写入的 InputChannels 更改

### `modify_xml` 位置偏移修复
- 不能在 `re.finditer` 遍历时直接修改 xml 字符串（位置会偏移）
- 正确做法：先收集所有替换 `(start, end, new_val)`，按位置降序排列后从后往前替换

### 错误检查
- `:SYSTEM:ERROR:ALL?` 返回格式: `0, "No error"` (注意逗号后有空格)
- 检查方式: `'0,' in err_str and 'No error' in err_str`

## Cursor Rules

- Every function in `devices/dc_controller.py` must include a short docstring describing its purpose.
- Keep functions small and focused; extract shared logic into reusable helpers.
