# Solar Agent（独立进程）

出站连接 IOT（HTTPS 任务 + WebSocket 上线）。

**日常请只双击 `start_SolarAutoTest.bat`（或桌面快捷方式）**。

## 新电脑 / 升级后（正式地址已打进安装包）

1. 安装包内 `config/iot_bootstrap.json` 默认为 `https://www.laidecloud.com/nss`（升级会覆盖）。  
2. 打开软件：本机 announce + **WebSocket `on`**，pythonid 出现在 IOT「**设备管理 → 添加设备 → 选择 Python 端 ID**」。  
3. 运维验证连通 → 选取「光伏自动化台架」→ 保存。  
4. 本机自动 claim 令牌并启动任务 Agent。  

勿把 `solar_agent.json` 拷到别的电脑。

## 模式

- `execution_mode: handoff`：落盘给已打开的桌面 UI；支持 `overload` / `antibackflow`  
- 现场方案见 IOT 仓 `docs/IOT-Solar自动化试验线上版方案.md`
