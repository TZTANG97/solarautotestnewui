# Solar Agent（独立进程）

出站连接 IOT。

**日常请只双击原来的 `start_SolarAutoTest.bat`（或桌面快捷方式）**：  
打开桌面软件后，若存在 `config/solar_agent.json`，会**在后台静默启动 Agent**，无需再点「启动 IOT Agent」。

单独调试 Agent 才用 `start_SolarAgent.bat`。首页仅显示 Agent 状态，必要时可「停止 Agent」。

## 配置（每台工控机一次）

运行 `setup_SolarAgentConfig.bat`，或把 IOT「台架管理」生成的令牌写入 `config/solar_agent.json`（已 gitignore）。

其他电脑：各自配置自己的令牌与 `iot_base`，不要共用该文件。

## 模式

- 默认 `dry_run: true`：联调模拟进度  
- `execution_mode: handoff`：落盘给已打开的桌面 UI；支持 `overload` / `antibackflow`；参数可含 `auto_append` / `auto_start`  
- `live`：尚未实现  

handoff 示例参数：
`{"widgets":{},"auto_append":true,"auto_start":true}`

- `auto_start=true` 时默认等「已结束/已中止」再写 results；等待期间写 `iot_job_inbox/progress/`，Agent 会上报云端进度
- 调试可设 `"wait_finish":false` 启动后立即回传
- 可选：`start_grace_sec`、`wait_finish_timeout_sec`
