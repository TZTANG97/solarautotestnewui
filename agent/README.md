# Solar Agent（独立进程）

出站连接 IOT。

**日常请只双击原来的 `start_SolarAutoTest.bat`（或桌面快捷方式）**：  
打开桌面软件后会静默处理 Agent（有令牌则启动；无令牌则先上报发现）。

单独调试 Agent 才用 `start_SolarAgent.bat`。首页仅显示 Agent 状态，必要时可「停止 Agent」。

## 配置（对齐「添加设备」：先发现，再确认添加）

1. 安装包内预置 `config/iot_bootstrap.json`（或环境变量 `SOLAR_IOT_BASE`）写好 IOT 地址，例如 `http://iot主机:端口/nss`。  
2. **打开软件**：按本机 `machineId` 向 IOT **announce 发现**，预分配 `pythonid`（此时还没有令牌）。  
3. 运维在 IOT「台架管理 → **从发现添加**」选中该 `pythonid`，填名称确认。  
4. 本机 **自动 claim 令牌**，写入 `config/solar_agent.json`，并静默启动 Agent。  

仍可用 `setup_SolarAgentConfig.bat` 手工改地址/令牌。勿把 `solar_agent.json` 拷到别的电脑。

## 模式

- 默认 `dry_run: true`：联调模拟进度  
- `execution_mode: handoff`：落盘给已打开的桌面 UI；支持 `overload` / `antibackflow`；参数可含 `auto_append` / `auto_start`  
- `live`：尚未实现  

handoff 示例参数：
`{"widgets":{},"auto_append":true,"auto_start":true}`

- `auto_start=true` 时默认等「已结束/已中止」再写 results；等待期间写 `iot_job_inbox/progress/`，Agent 会上报云端进度
- 调试可设 `"wait_finish":false` 启动后立即回传
现场怎么跑、设备更换/输出上限/急停（后做）：见 IOT 仓 `docs/IOT-Solar自动化试验线上版方案.md`。
