# Solar Agent（独立进程）

出站连接 IOT。

**日常请只双击原来的 `start_SolarAutoTest.bat`（或桌面快捷方式）**：  
若存在 `config/solar_agent.json`，会**自动后台启动 Agent**，再打开桌面软件。不必再单独点 Agent。

单独调试 Agent 才用 `start_SolarAgent.bat`。

## 配置（每台工控机一次）

运行 `setup_SolarAgentConfig.bat`，或把 IOT「台架管理」生成的令牌写入 `config/solar_agent.json`（已 gitignore）。

其他电脑：各自配置自己的令牌与 `iot_base`，不要共用该文件。

## 模式

- 默认 `dry_run: true`：联调模拟进度  
- `execution_mode: handoff`：落盘给已打开的桌面 UI；参数可含 `auto_append` / `auto_start`（true 时 Append 后调「开始试验」）  
- `live`：尚未实现  

handoff 示例参数：
`{"widgets":{"textEdit_S1_AC_VOLT":"230"},"auto_append":true,"auto_start":true}`

- `auto_start=true` 时默认 `wait_finish=true`：等桌面状态变为「已结束/已中止」再写 results（Agent 才结案）
- 调试可设 `"wait_finish":false` 启动后立即回传
- 可选：`start_grace_sec`（未进入「进行中」判失败，默认 20）、`wait_finish_timeout_sec`（默认 7200）
