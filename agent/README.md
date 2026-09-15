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
- `execution_mode: handoff`：落盘给已打开的桌面 UI 追加命令  
- `live`：尚未实现  
