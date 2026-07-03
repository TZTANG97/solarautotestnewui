# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Photovoltaic (solar) inverter automated test system. A PyQt5 desktop application that controls AC/DC power supplies, power analyzers (WT3000/WT1800/WT1806E/WT5000), and oscilloscopes (DL850) via SCPI/Modbus TCP to run standardized compliance tests. The UI is primarily in Chinese.

## Running the Application

**必须使用项目根目录的 `.venv` 虚拟环境（由 uv 管理）。** 本项目中所有测试、运行、代码审查都必须在此环境下执行。Conda 环境 `SolarAutoTestEnv` 已弃用。

```bash
.venv/Scripts/python.exe SCPITestWave.py
# 或激活 venv 后直接运行
.venv/Scripts/activate
python SCPITestWave.py
```

No build step. Python 3.10+ required. Install dependencies:

```bash
uv sync
# 或
.venv/Scripts/pip install -r requirements.txt
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

- `ui_files/SCPI_Test.py` — **V1.1 主 UI**（手写，非 pyuic5 生成）。侧边栏 + QStackedWidget 布局，1600x900 固定分辨率。类 `Ui_Dialog`，`setupUi(self, Dialog)` 接收 `QMainWindow`。
- `ui_files/` 下其他 `.ui` 文件供 Qt Designer 使用，生成的 Python UI 类在根目录 `Dialog_*.py`。
- Regenerate with: `pyuic5 ui_files/Foo.ui -o Dialog_Foo.py`
- **Never edit generated `Dialog_*.py` files directly** — changes will be overwritten.

### V1.1 UI 架构

主 UI `ui_files/SCPI_Test.py` 采用侧边栏 + QStackedWidget 布局：

- **侧边栏**：可折叠两级菜单（首页/设备管理/Auto_Test/其他），包裹在 QScrollArea 中，底部固定刷新按钮
- **QStackedWidget**：11 页（首页=0, 设备1-8=1-8, 项目配置=9, 命令文件=10）
- **首页**：2x4 设备状态卡片网格（写死 8 设备）+ 当前测试项目卡片
- **status.json**（根目录）：设备连接状态和项目信息的单一数据源，首页通过 `_load_home_status()` 读取显示
- **Auto_Test 动态菜单**：`ui.add_auto_test_item(text, page_index)` 供 SCPITestWave.py 调用

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

### DEWETRON 相关文件

- `devices/dewetron_controller.py` — DewetronController 类，connect/disconnect/modify_xml
- `Dialog_DEWETRON_Setting.py` — DEWETRON 设置 UI（单页左布局，含接线图+设备参数）
- `DewetronTestPage.py` — 测试界面构造模块（MeasurementScreens 注入）
- `DialogFileManager.py` — 文件管理对话框（含自动化命令+DEWETRON配置两个 Tab）

### status.json

根目录 `status.json` 是设备连接状态和项目信息的单一数据源。首页通过 `_load_home_status()` 读取并显示：

- `devices[]`：每个设备的 name、resource、connected、page、last_connected
- `project`：当前测试项目的 name、status、progress、estimated_time

设备连接/断开时应更新此文件，首页自动反映变化。

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
  3. `modify_xml()` → 修改 WiringType、Used/Neon/Active、InputChannels、MaxUpdateRate、DataSubsampling、FrequencyChannel
  4. `send_apply_config()` → 发送到设备
  5. APPLY 成功后，将 XML 保存为本地文件（`command_save_files/dewetron_data/`）

### InputChannels 映射
- `modify_xml()` 根据 UI 选择的通道（channel_map）+ 当前设备 ChannelID 构建 InputChannels
- UI 选择 `U1 <- AI 1/U2` → `InputChannels/U1` 的 ChannelID 设为 AI 1/U2 的当前 ChannelID
- 未在 UI 中选择的槽位设为 UNUSED
- 设备接受 SCPI 写入的 InputChannels 更改

### DEWETRON XML Key 映射（modify_xml 处理）
- `POWER/FrequencyChannel` — ChannelID 格式，频率测量通道，默认为组 1 的 U 通道
- `POWER/MaxUpdateRate` — StringValue，最大刷新率（单位 ms）
- `POWER/DataSubsampling` — StringValue，通道二次采样（"Auto"/"Off"/"2"~"5"）
- `POWER/FlickerType` — EnumValue，加权类型（TYPE_230V50HZ / TYPE_230V60HZ / TYPE_120V50HZ / TYPE_120V60HZ / AUTO）
- `POWER/Flicker/NominalVoltage` — ScalarValue，标称电压（单位 V）
- `POWER/Flicker/PstAggregationTime` — ScalarValue，短时闪变计算时间（单位 min）
- `POWER/Flicker/PltAggregationTime` — ScalarValue，长时闪变计算时间（单位 min）
- `POWER/Flicker/ShortCircuitPower` — ScalarValue，短路视在功率（单位 MVA）
- `POWER/Features/Flicker` — BooleanValue，IEC 标准开关
- `POWER/Features/Rolling` — BooleanValue，滚动计算开关
- **不要用的 Key：** `AcquisitionRate`（Hz，每通道）、`TRION/Oversampling`（每通道）、`POWER/LineToLineVoltageInput`（设备不允许 SCPI 更改）

### DEWETRON 导出设置（Export Settings）

**导出设置 ≠ 电力组，是两个独立的菜单项。**

- **电力组** → 数据通道菜单 → `Neon/Stored` 控制录制
- **导出设置** → 菜单栏"导出设置" → `<ExportChannels>` 控制 CSV/报告导出

XML 结构：
```xml
<ExportSetup>
  <ExportSettings format="CSV">
    <ExportChannels>
      <ExportChannel channel_id="..."/>  ← 通道勾选
    </ExportChannels>
    <ExportProperties>
      EXPORT_VALUE_PRECISION  ← 小数位数 (UnsignedInt64)
      WAVEFORM               ← 实时波形 (BooleanValue)
    </ExportProperties>
  </ExportSettings>
</ExportSetup>
```

**修改方式：** `modify_xml()` 的 `export_fields` 替换 `<ExportChannels>`，`decimal_places` 和 `realtime_waveform` 修改 `<ExportProperties>`。

**APPLY 后 ChannelID 会重新分配**，每次提交前必须重新 `read_channel_id_map()`。连续提交需重试读取（设备重载需要时间），最多 3 次间隔 2 秒。

**SCPI 限制：** `:CHANNELLIST:ITEM<id>:ATTR` 只读，`Used`/`Neon/Active` 由设备自动管理不可修改。

### DEWETRON 配置文件命名
- 标准格式：`dewetron_YYYYMMDD_HH.xml`
- 校验格式：`dewetron_verify_YYYYMMDD_HH.xml`
- 文件必须以 `dewetron_` 开头才能被加载列表和文件管理器识别
- 另存为时自动加上 `dewetron_YYYYMMDD_HH_` 前缀
- 存储目录：`command_save_files/dewetron_data/`（已加入 .gitignore）

### `modify_xml` 位置偏移修复
- 不能在 `re.finditer` 遍历时直接修改 xml 字符串（位置会偏移）
- 正确做法：先收集所有替换 `(start, end, new_val)`，按位置降序排列后从后往前替换

### `modify_xml` XML 格式与 regex 规则（重要！）

**XML 值格式分两类：**
- **StringValue 属性**（MaxUpdateRate、DataSubsampling）：值有引号包裹 → `<StringValue>"500"</StringValue>`
- **EnumValue/ScalarValue/BooleanValue 属性**：值无引号 → `<Value>230</Value>`

**StringValue regex 模式（group 1 不含引号，`"?` 匹配但不捕获引号）：**
```python
r'(<Property name="POWER/MaxUpdateRate">\s*<StringValue>)"?([^"<]+)"?(</StringValue>)'
# 替换值必须是裸值，不带引号：
replacements.append((m.start(2), m.end(2), acquisition_rate, label))  # 正确 → "200"
replacements.append((m.start(2), m.end(2), f'"{acquisition_rate}"', label))  # 错误！→ ""200""
```

**EnumValue/ScalarValue/BooleanValue regex 模式（group 1 含完整开标签）：**
```python
r'(<Property name="POWER/FlickerType">\s*<EnumValue enum="FlickerType">)([^<]+)(</EnumValue>)'
# 替换值直接是裸值：
replacements.append((m.start(2), m.end(2), flicker_type, label))
```

**Why:** 2026-07-02 调试发现 `f'"{acquisition_rate}"'` 导致 `""200""` 双重引号，设备报 `-102 Syntax error`。引号由 XML 格式本身提供，regex 的 `"` 保留原引号。

### 错误检查
- `:SYSTEM:ERROR:ALL?` 返回格式: `0, "No error"` (注意逗号后有空格)
- 检查方式: `'0,' in err_str and 'No error' in err_str`

## Cursor Rules

- Every function in `devices/dc_controller.py` must include a short docstring describing its purpose.
- Keep functions small and focused; extract shared logic into reusable helpers.

## 目录结构规则

- `devices/` 是**设备控制专用目录**，只放设备控制器代码（如 `dewetron_controller.py`、`ac_controller.py`）
- **不要**在 `devices/` 中放入配置、UI、工具类等非设备控制代码
- UI 对话框 → 根目录 `Dialog_*.py`（如 `DialogFileManager.py`、`Dialog_DEWETRON_Setting.py`）
- 独立工具模块 → 根目录（如 `DewetronTestPage.py`）
- **通用 UI 组件** → `components/`（如 `buttons.py`）

## 通用组件库（components/）

`components/` 目录存放可复用的 UI 组件。**遇到样式/组件需求时，优先查找此目录，已有则复用，没有再新建。**

当前组件：
- **`StyledButton`** — 通用样式按钮，6 种预设风格（DEFAULT/PRIMARY/SUCCESS/INFO/WARNING/DANGER），支持自定义 width、height、min_width、font_size、padding
- **`apply_button_style(btn, style)`** — 将预设样式应用到已有 QPushButton 上（不替换控件，保留信号连接）

```python
from components import StyledButton, ButtonStyle, apply_button_style

# 创建新按钮
btn = StyledButton("确定", ButtonStyle.SUCCESS, width=120, height=36)

# 给已有按钮换样式（保留信号连接）
apply_button_style(existing_btn, ButtonStyle.DANGER)
```

## AutoTest 按钮调试规则

- **闪变测试（fluctuation）是标准参考，只读参考，不允许修改**
- AutoTest 各测试项目逐个调试，以闪变为模板接入按钮逻辑
- 每个项目的「测试追加」「读取」「保存」「操作日志」按钮逻辑与闪变一致
- 每个项目中的「测试追加」和「项目设置 count + 重置」逻辑与闪变一致
- **UI 不再变动**，仅调整按钮附带的现有逻辑
- 原功能逻辑不变，每次只处理一个测试项目
- 操作日志统一输出到主 UI 的 `ui.textEdit_ReturnMessage`

### 新项目按钮接入速查（以谐波电流为模板）

每个测试项目需要改动 **5 处**（全在 `SCPITestWave.py`）：

**1. 新增 Append 函数**（在对应 `xxxSend()` 函数定义之后）
```python
def xxxAppend():
    global strAddTestFlag, xxx_append_count
    if 'xxx_append_count' not in globals():
        xxx_append_count = 0
    strAddTestFlag = "0" if xxx_append_count == 0 else "1"
    mode = "覆盖" if xxx_append_count == 0 else "追加"
    ui.textEdit_ReturnMessage.append(f"[项目名] 第{xxx_append_count + 1}次{mode}模式，开始生成命令...")
    xxxSend()
```

**2. 在 `xxxSend()` 末尾（`dialog_windowXxx.close()` 之前）加计数递增**
```python
if 'xxx_append_count' not in globals():
    xxx_append_count = 0
xxx_append_count += 1
uiXxx.label_append_count.setText(str(xxx_append_count))
_sync_start_end_buttons()
ui.textEdit_ReturnMessage.append(f"[项目名] 追加完成，当前计数: {xxx_append_count}")
```
注意：不要直接 `setEnabled(True/False)`，统一走 `_sync_start_end_buttons()`。

**3. 信号连接区域（`_safe_click` 批量连接处）加 TestAppend + ResetCount**
```python
_safe_click(uiXxx, "pushButton_TestAppend", xxxAppend)

def reset_xxx_count():
    global xxx_append_count
    xxx_append_count = 0
    uiXxx.label_append_count.setText("0")
    _sync_start_end_buttons()
    ui.textEdit_ReturnMessage.append("[项目名] 计数器已重置为0")
_safe_click(uiXxx, "pushButton_ResetCount", reset_xxx_count)
```

**4. 在 `_sync_start_end_buttons()` 中添加该项目的计数器判断**
```python
def _sync_start_end_buttons():
    current = ui.comboBox_PS.currentText()
    count = 0
    if current == '电压闪变':
        count = flicker_append_count
    elif current == '谐波电流':
        count = harmonic_append_count
    elif current == '新项目':
        count = xxx_append_count
    # ...更多项目
    ui.pushButton_StartTest.setEnabled(count >= 1)
    ui.pushButton_EndTest.setEnabled(count >= 1)
```

**5. `chooseDetailDialog()` / `addtestDialog()` — 对应 elif 分支**
```python
elif currentSecond == '项目名':
    uiXxx.label_append_count.setText(str(xxx_append_count))
    _sync_start_end_buttons()
    dialog_windowXxx.show()
```
同时在函数顶部 global 声明中加 `xxx_append_count`，并在函数体中初始化 `xxx_append_count = 0`。

**变量命名约定：**
- 全局计数变量：`{项目英文名}_append_count`（如 `harmonic_append_count`）
- UI 对象：`uiXxx`（如 `uiThaiXieBoDianLiu`）
- 对话框：`dialog_windowXxx`（如 `dialog_windowxiebodianliu`）
- Append 函数：`xxxAppend()`（如 `thaixiebodianliuAppend`）
- Send 函数：已有 `xxxSend()`（如 `thaixiebodianliuSend`）
- Reset 闭包：`reset_xxx_count()`

### 试验生命周期标准（所有项目必须遵循）

每个测试项目的试验流程必须符合以下标准：

**1. 追加测试 → 计数器+1 → 启用开始按钮**
```python
def xxxAppend():
    global xxx_append_count
    xxx_append_count += 1
    uiXxx.label_append_count.setText(str(xxx_append_count))
    _sync_start_end_buttons()
```

**2. 测试完成 → 计数器归0 → 禁用开始按钮**
在 `RunProject()` 的"实验完成"复位处调用：
```python
_reset_current_project_count()
_sync_start_end_buttons()
```

**3. 结束试验按钮 → 二次确认弹窗 → 归零 → 禁用开始按钮**
```python
def EndProjectPush():
    global strTestStatusFlag
    try:
        if strTestStatusFlag == "运行":
            reply = QMessageBox.question(None, "确认结束", "确定要结束当前试验吗？",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                strTestStatusFlag = "结束"
                # ... 结束逻辑 ...
                _reset_current_project_count()
                _sync_start_end_buttons()
        else:
            QMessageBox.warning(None, "提示", "项目未运行，无法结束试验")
    except NameError:
        QMessageBox.warning(None, "提示", "项目未运行，无法结束试验")
```

**4. `_reset_current_project_count()` 函数**
重置当前项目的计数器并更新 label：
```python
def _reset_current_project_count():
    global flicker_append_count, harmonic_append_count
    current = ui.comboBox_PS.currentText()
    if current == '电压闪变':
        flicker_append_count = 0
        uiThaiDianYaShanBian.label_append_count.setText("0")
    elif current == '谐波电流':
        harmonic_append_count = 0
        uiThaiXieBoDianLiu.label_append_count.setText("0")
    # ...更多项目
```

**5. `Upper_WT_Config` 异常处理**
`RunProject()` 中 `wt_is_check()` 必须用 try/except 包裹，防止线程崩溃导致定时器循环停止：
```python
if first_test == '':
    try:
        wt_is_check()
    except Exception as e:
        _append_debug_log(f"[Upper_WT_Config][error] wt_is_check failed: {e}")
    first_test = '1'
```

**6. 设备连接校验**
`RunProjectPush()` 中点击"开始试验"时，根据 `strArrayTest` 中实际用到的设备，一次性检查所有连接：
```python
def _check_device_connections():
    device_map = {
        "AC": ("交流电源", ac_controller),
        "DC1": ("DC电源1", dc1_controller),
        "DC2": ("DC电源2", dc2_controller),
        "DC3": ("DC电源3", dc3_controller),
        "DC4": ("DC电源4", dc4_controller),
        "Upper_WT_Config": ("功率分析仪", wt3000_controller),
        "DL850": ("示波器(DL850)", dl850_controller),
    }
    used_devices = set()
    for cmd in strArrayTest:
        if len(cmd) > 0 and cmd[0] in device_map:
            used_devices.add(cmd[0])
    disconnected = []
    for device_key in sorted(used_devices):
        name, controller = device_map[device_key]
        if controller is None or not controller.connected:
            disconnected.append(name)
    return "、".join(disconnected) if disconnected else ""
```
调用处（`RunProjectPush` 中 `strSettingTestFlag == "1"` 分支开头）：
```python
disconnected = _check_device_connections()
if disconnected:
    QMessageBox.warning(None, "连接错误",
        f"以下设备未连接，已终止本次试验启动：\n\n{disconnected}")
    return
```

**改动生效范围：**
- **全局生效（所有项目自动受益）：**
  - `EndProjectPush` 二次确认弹窗 — 所有点"结束试验"都会弹确认框
  - `EndProjectPush` 未运行时警告弹窗 — 所有项目
  - `wt_is_check()` try/except — 所有使用 WT 的项目不会因 WTViewerEfree 缺失而崩溃线程
  - `_check_device_connections()` — 根据 `strArrayTest` 自动判断用了哪些设备，一次性校验连接
- **需要逐项目补充（接入新项目时必须添加）：**
  - `_reset_current_project_count()` — 添加 `elif current == '项目名':` 分支，重置计数器 + 更新 label
  - `_sync_start_end_buttons()` — 添加 `elif current == '项目名':` 分支，读取对应计数器

### 已踩坑点（必须避免）

**坑1：LazyDialog 不能作为 QMessageBox/QFileDialog 的 parent**
- `dialog_windowXxx` 是 `LazyDialog` 实例，不是 `QWidget`
- `QMessageBox.warning/dialog_windowXxx` 和 `QFileDialog.getSaveFileName(dialog_windowXxx, ...)` 会报 `TypeError`
- **修复**：所有 Open/Save 工具函数中 `QMessageBox` 和 `QFileDialog` 的 parent 传 `None`
- 涉及文件：`utils/Open_Save_Thai*.py` 中所有 `dialog_window` 参数

**坑2：`_make_checkbox` 不传 parent 不会存储到 self**
- `Dialog_thaixiebodianliu.py` 的 `_make_checkbox(name, text)` 不传 `parent` 时，只创建 widget 但不 `setattr(self, name, cb)`
- 导致 `uiThaiXieBoDianLiu.checkBox_S2_WT3000` 等属性不存在
- **修复**：创建 checkbox 时传 `parent=self`，如 `self._make_checkbox(cb_name, cb_text, parent=self)`

**坑3：reset 函数不能直接操作全局 Start/End 按钮**
- 之前 `reset_flicker_count()` 直接 `ui.pushButton_StartTest.setEnabled(False)` 会影响所有项目
- **修复**：reset 函数只重置计数器和 label，按钮状态由 `_sync_start_end_buttons()` 统一管理

**坑4：按钮状态必须在启动时初始化 + 切换项目时同步**
- 程序启动时计数器为 0 但按钮默认启用
- **修复**：信号连接处调用 `_sync_start_end_buttons()` 初始化，并连接 `ui.comboBox_PS.currentTextChanged` 信号自动同步

**坑5：调试后必须检查未定义属性**
- 每个项目调试完毕后，必须检查代码中引用的所有 UI 属性是否都已定义
- 典型报错：`AttributeError: 'Ui_Dialog_thaixiebodianliu' object has no attribute 'checkBox_S3'`
- **原因**：`_make_checkbox`、`_make_combo`、`_make_input` 等方法仅在传 `parent` 参数时才存储到 `self`，否则只创建 widget 但不绑定属性
- **检查方法**：
  1. 在 `Dialog_thaiXxx.py` 中搜索所有 `self.uiXxx.属性名` 引用
  2. 验证这些属性名在对应的 `Dialog_thaiXxx.py` 中都有对应的 `self.xxx = ...` 定义
  3. 特别注意 `_make_checkbox`、`_make_combo`、`_make_input` 创建的控件是否传了 `parent=self`
- **修复**：确保创建控件时传 `parent=self`，如 `self._make_checkbox(cb_name, cb_text, parent=self)`

**坑6：DC 验证错误标志会被覆盖（多 DC 通道时）**
- `strShowErrorMessageBoxFlag` 在每个 DC 通道检查时会被覆盖，导致只显示最后一个错误
- 典型场景：DC1 有错误（flag="1"），DC2 也有错误（flag="3"），DC1 的错误被覆盖
- **修复**：使用 `dc_error_messages` 列表收集所有错误，最后一次性显示
- **代码模式**：
  ```python
  dc_error_messages = []
  if dc1_checked:
      if error:
          dc_error_messages.append("DC电源1赋值错误")
  if dc2_checked:
      if error:
          dc_error_messages.append("DC电源2赋值错误")
  # 最后显示所有错误
  if dc_error_messages:
      all_errors = "\n".join([f"{i+1}. {msg}" for i, msg in enumerate(dc_error_messages)])
      QMessageBox.information(None, "错误提示信息", all_errors, ...)
  ```
- **涉及函数**：`thaidianyashanbianSend()`、`thaixiebodianliuSend()` 等所有包含 DC 验证的函数

**坑7：DC 变量未初始化会导致 UnboundLocalError**
- 如果未勾选 step1 DC 通道（如 `checkBox_S1_DC2`），变量（如 `S1DC2Vmp`）未定义
- 在谐波步骤中使用这些变量时会触发 `UnboundLocalError`
- **修复**：在函数开头初始化所有 DC 变量为空字符串
- **代码模式**：
  ```python
  S1DC1Vmp = S1DC1Imp = S1DC1Voc = S1DC1Isc = ""
  S1DC2Vmp = S1DC2Imp = S1DC2Voc = S1DC2Isc = ""
  S1DC3Vmp = S1DC3Imp = S1DC3Voc = S1DC3Isc = ""
  S1DC4Vmp = S1DC4Imp = S1DC4Voc = S1DC4Isc = ""
  ```
- **涉及函数**：所有包含谐波步骤的 Send 函数

**坑8：所有 QMessageBox 和 QFileDialog 调用都需要检查 parent**
- 不仅是 `utils/Open_Save_Thai*.py`，`SCPITestWave.py` 中的调用也需要检查
- 典型报错：`TypeError: information(parent: Optional[QWidget]...): argument 1 has unexpected type 'LazyDialog'`
- **修复**：所有 `QMessageBox.warning/information/critical` 和 `QFileDialog.getSaveFileName/getOpenFileName` 的 parent 参数传 `None`
- **涉及文件**：
  - `SCPITestWave.py`：所有 `Send()` 函数中的错误提示框
  - `utils/Open_Save_Thai*.py`：保存/读取完成提示框、文件选择对话框
- **检查方法**：
  1. 搜索 `QMessageBox\.(warning|information|critical)\(dialog_window` 确保所有调用都使用 `None`
  2. 搜索 `QFileDialog\.(getSaveFileName|getOpenFileName)\(dialog_window` 确保所有调用都使用 `None`

**坑9：计数器变量未初始化会导致 UnboundLocalError**
- `harmonic_append_count`、`flicker_append_count`、`overloads_append_count` 等计数器变量在 Send 函数开头未声明 global 且未初始化
- 典型报错：`UnboundLocalError: local variable 'overloads_append_count' referenced before assignment`
- **修复**：在 Send 函数开头**同时**做两件事：
  1. `global` 声明中**加入**计数器变量（如 `global ..., overloads_append_count`）
  2. 紧接着加初始化检查：`if 'overloads_append_count' not in globals(): overloads_append_count = 0`
- **代码模式**：
  ```python
  def xxxSend():
      global uiXxx, strArrayTest, ...
      global xxx_append_count  # 必须声明！
      if 'xxx_append_count' not in globals():
          xxx_append_count = 0
      # ... 其他代码
  ```
- **涉及函数**：`thaidianyashanbianSend()`、`thaixiebodianliuSend()`、`thaioverloadsSend()` 等所有包含计数器的 Send 函数
- **检查方法**：搜索每个 Send 函数中的 `+= 1`，确认对应的计数器变量在该函数的 `global` 声明中且有初始化检查
- **新项目接入时必须检查**：接入新项目的 Append/Send 逻辑时，第一步就是确认 Send 函数的 global 声明包含计数器变量

**坑10：步骤启用复选框必须联动子控件**
- 取消勾选步骤启用复选框（如 `checkBox_S3`）后，下方的 DC 通道复选框和功率输入框仍可操作，导致用户困惑
- **修复**：步骤复选框的 `toggled` 信号连接到子控件的 `setEnabled`
- **代码模式**：
  ```python
  # 收集子控件
  dc_cbs = [cb1, cb2, cb3, cb4]
  pf_widget = self._make_input(...)

  # 联动逻辑
  def _on_step_toggled(checked):
      for dc_cb in dc_cbs:
          dc_cb.setEnabled(checked)
      pf_widget.setEnabled(checked)

  step_widget.toggled.connect(_on_step_toggled)
  _on_step_toggled(step_widget.isChecked())  # 初始化状态
  ```
- **涉及文件**：所有 `Dialog_thaiXxx.py` 的步骤构建方法
- **适用范围**：闪变、谐波电流及后续所有测试项目
- **扩展：step1 DC 联动 step3+ DC 复选框**：step1 中未勾选某个 DC 通道（如 `checkBox_S1_DC1`）时，所有谐波步骤中对应的 DC 复选框（如 `checkBox_S1_DC1_2`/`_3`/`_4`/`_5`）应被禁用且取消勾选。DC 复选框的启用条件为：`步骤已启用 AND step1 DC 已勾选`。**当 step1 DC 勾选时，step3+ 对应 DC 复选框应自动勾选**，避免用户逐个手动点击。
- **代码模式（含自动勾选）**：
  ```python
  step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
               self.checkBox_S1_DC3, self.checkBox_S1_DC4]

  def _update_dc_enabled():
      step_on = step_widget.isChecked()
      for i, dc_cb in enumerate(dc_cbs):
          should_enable = step_on and step1_dcs[i].isChecked()
          dc_cb.setEnabled(should_enable)
          dc_cb.setChecked(should_enable)  # 自动勾选/取消勾选

  step_widget.toggled.connect(_update_dc_enabled)
  for s1dc in step1_dcs:
      s1dc.toggled.connect(_update_dc_enabled)
  _update_dc_enabled()  # 初始化
  ```
- **适用范围**：闪变（step3 DC 开关循环 + step5 关机 DC）、谐波电流（12 个谐波卡片 + step4 关机 DC）、过载（step4 关机 DC）及后续所有有多步 DC 测量的项目
- **关机步骤也必须联动**：每个项目的关机设置（通常为最后一个步骤）中的 DC 复选框（`checkBox_S5_DCx` 或 `checkBox_S7_DCx`）也必须联动 step1 DC，逻辑与 step3 相同。已修复项目：
  - 闪变：step5 关机 DC（`checkBox_S5_DCx`）
  - 谐波电流：step4 关机 DC（`checkBox_S5_DCx`）
  - 过载：step4 关机 DC（`checkBox_S5_DCx`）
  - 直流分量：step7 关机 DC（`checkBox_S7_DCx`）— 待修复
  - 静态CosPhi：step5 关机 DC（`checkBox_S5_DCx`）— 待修复
  - 固定PF：step5 关机 DC（`checkBox_S5_DCx`）— 待修复

**坑11：所有 step3/step4/step5/step7 的 DC 命令必须联动 step1 DC 复选框**
- step3/step4/step5/step7 中的 DC 块生成命令时，如果只检查该步骤的复选框，而 step1 的 `checkBox_S1_DCx` 未勾选，DC 命令仍会被添加到 `strArrayTest`
- **后果1**：`S1DC1Vmp` 等变量未定义 → `UnboundLocalError`
- **后果2**：`strArrayTest` 中包含 DC 命令 → `_check_device_connections()` 误判 DC 设备需要连接，提示"设备未连接，终止启动"
- **修复**：所有 DC 块必须同时检查 step1 DC 复选框
- **代码模式**：
  ```python
  # 错误：只检查 step3/step5 复选框
  if uiXxx.checkBox_S3_DC1.isChecked():
      ...
  if uiXxx.checkBox_S5_DC1.isChecked():
      ...

  # 正确：同时检查 step1 复选框
  if uiXxx.checkBox_S1_DC1.isChecked() and uiXxx.checkBox_S3_DC1.isChecked():
      ...
  if uiXxx.checkBox_S1_DC1.isChecked() and uiXxx.checkBox_S5_DC1.isChecked():
      ...
  ```
- **涉及文件**：`SCPITestWave.py` 中所有包含 DC 块的 Send 函数
- **适用项目**（2026-06-12 已全部修复）：
  - 闪变 `thaidianyashanbianSend()`：step3（24 块）+ step5 关机（4 块）
  - 谐波电流 `thaixiebodianliuSend()`：step3（16 块）+ step4 关机（4 块）
  - 过载 `thaioverloadsSend()`：step4 关机（4 块）
  - 直流分量 `thaizhiliufenliangSend()`：step3（4 块）+ step5（4 块）+ step7 关机（4 块）
  - 静态CosPhi `thaistaticcosPhiSend()`：step3（4 块）+ step5（4 块）+ step5 关机（4 块）
  - 巴西CosPhi `thaicosPhiBrazilSend()`：step3（4 块）+ step5（4 块）+ step5 关机（4 块）
- **新项目接入时必须检查**：接入新项目的 Send 函数时，搜索所有 `checkBox_S*_DC`（包括 step3、step4、step5、step7），确保每个都有对应的 `checkBox_S1_DC` 联动

### 功率分析仪配置内嵌规则

当测试项目的 step2 是功率分析仪配置时，采用以下模式：

1. 使用 `QRadioButton`（单选框），默认 WT3000
2. 配置内容直接嵌入 step2，不再弹窗
3. `QStackedWidget` 承载 4 个设备配置页面（WT3000/WT1800/WT1806E/WT5000）
4. Radio 切换联动 `stackedWidget.setCurrentIndex()`
5. 去掉弹窗中的 TestAppend/ReadSetting/SaveSetting 按钮
6. 所有 widget objectName 保持不变（SCPITestWave.py 和 Open_Save 按名称访问）
7. 步骤启用复选框 `checkBox_S2` 联动禁用所有子控件（Radio + Stacked 内容）

**涉及文件模式：**
- `Dialog_thaiXxx.py` — `_build_step2()` 使用 radio + stackedWidget
- `SCPITestWave.py` — 移除 `pushButton_S2_WT_xxx_CONFIG.clicked.connect(xxx_show)`
- `components/wt_config_content.py` — 共享的 WT 配置内容构建函数

**实现参考：** 谐波电流 `Dialog_thaixiebodianliu.py` 的 `_build_step2()` 方法

### 谐波电流 WT 配置内嵌改动记录（2026-06-12，已验收通过）

**改动范围：**
- `Dialog_thaixiebodianliu.py` — `_build_step2()` 改为 radio + QStackedWidget
- `components/wt_config_content.py` — 新增 `build_wt3000_content` / `build_wt1800_content` / `build_wt1806e_content` / `build_wt5000_content`
- `utils/Open_Save_ThaiXieBoDianLiu.py` — 保存/读取改用 `_PageWidgetFinder` 代理
- `SCPITestWave.py` — `thaixiebodianliuSend()` 中 WT config 读取改用 `_PageWidgetFinder`

**已解决的 Bug：**

1. **Radio 信号不触发**：`QButtonGroup` 作为局部变量被垃圾回收，信号断裂
   - **解决**：`self._radio_group = radio_group` 保持引用

2. **`self.sender()` 报错**：`Ui_Dialog_thaixiebodianliu` 不是 QObject，无 `sender()` 方法
   - **解决**：改用 `buttonToggled` 信号，回调参数 `(btn, checked)` 直接获取 button 对象

3. **`setCurrentIndex` 类型错误**：`buttonToggled` 传递 button 对象而非 int ID
   - **解决**：用 `radio_group.id(btn)` 获取整数 ID

4. **QStackedWidget 页面 visible=False**：`isVisible()` 返回 False 因为主 stackedWidget 未显示 step2
   - **解决**：加载完成后调用 `_switch_step(1)` 切换到 step2

5. **保存的 WT 配置值全为 0**：4 个 `build_wt*_content(self)` 共享同一个 `self`，`_make_combo` 用 `setattr(parent, name, combo)` 导致同名属性被最后一个 build 函数覆盖
   - **解决**：`Open_Save_ThaiXieBoDianLiu.py` 新增 `_PageWidgetFinder` 代理类，通过 `findChild(objectName)` 在正确的 stacked page 中查找 widget

6. **CSV 读写 UnicodeDecodeError**：Windows 默认 GBK 编码，保存的 CSV 含中文时读取报错
   - **原因**：`open(file, 'w+')` 和 `open(file, 'r')` 未指定 encoding，Windows 默认 GBK，但含中文的 CSV 需要 UTF-8
   - **解决**：所有 `Open_Save_Thai*.py` 统一修复——写入加 `encoding='utf-8-sig'`（兼容 Excel/记事本），读取先尝试 `utf-8-sig` 再回退 `gbk`
   - **涉及文件**：全部 15 个 `utils/Open_Save_Thai*.py`

7. **追加测试时 WT 配置全为空/0**：`thaixiebodianliuSend()` 中 `WT3000E_params_config(uiThiaWT3000E)` 读取旧弹窗对象（默认值），未从 stacked widget 页面读取
   - **原因**：WT 配置从弹窗改为内嵌 stacked widget 后，`SCPITestWave.py` 中的 `WT*_params_config()` 仍传入旧弹窗 UI 对象
   - **解决**：改为 `_PageWidgetFinder(_wtStacked.widget(N))` 传入正确的 stacked page，通过 `findChild` 按 objectName 查找 widget
   - **涉及文件**：`SCPITestWave.py` — `thaixiebodianliuSend()` + `from utils.Open_Save_ThaiXieBoDianLiu import _PageWidgetFinder`

## 已知问题与技术债务

### 谐波电流 DC4 通道命名不一致
- **文件**：`Dialog_thaixiebodianliu.py` 行 152-170
- **问题**：部分 DC4 通道的 checkbox 命名使用了 `checkBox_S1_DC3_xx` 而非 `checkBox_S1_DC4_xx`
- **示例**：
  - 正确：`dc4_cb="checkBox_S1_DC4_2"`（行 115）
  - 错误：`dc4_cb="checkBox_S1_DC3_15"`（行 152）
- **影响**：不影响运行（所有引用处命名一致），但命名不直观，易造成混淆
- **修改范围**：需同时修改 `Dialog_thaixiebodianliu.py` 通道映射字典 + `SCPITestWave.py` 中 `thaixiebodianliuSend()` 函数
- **建议**：功能正常可暂不改，下次调试谐波电流时统一修正

## PyQt5 布局注意事项

- `QVBoxLayout` 没有 `setMaximumWidth` 方法，需要在外层包 `QWidget` 再设宽度
- 辅助方法（如 `_rotate_tips`）必须在类末尾定义，**不能放在 `setupUi` 内部**，否则会把后续代码吞入方法体
- `setupUi` 的最后几行应该是布局组装代码（`layout.addWidget(...)`），不是新方法定义
