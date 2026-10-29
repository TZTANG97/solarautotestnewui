# Solar Agent（独立进程）

出站连接 IOT（HTTPS 任务 + WebSocket 上线 + **MQTT 进度上行**）。

**日常请只双击 `start_SolarAutoTest.bat`（或桌面快捷方式）**。

## 新电脑 / 升级后（正式地址已打进安装包）

1. 安装包内 `config/iot_bootstrap.json` 默认为 `https://www.laidecloud.com/nss`（升级会覆盖）。  
2. 打开软件：本机 announce + **WebSocket `on`**，pythonid 出现在 IOT「**设备管理 → 添加设备 → 选择 Python 端 ID**」。  
3. 运维验证连通 → 选取「光伏自动化台架」→ 保存。  
4. 本机自动 claim 令牌并启动任务 Agent。  

勿把 `solar_agent.json` 拷到别的电脑。

## 模式

- `execution_mode: handoff`：落盘给已打开的桌面 UI；支持过载 / 防逆流 / 直流分量等  
- 开测下发：优先 **WebSocket `startexper`**，失败则 MQTT `/EquCommand/{pythonid}`  
- 进度/结案状态：**MQTT** `SolarEquipment_*`（对齐温箱，不与 TH/TS 串道）  
- HTTPS 仅保留：领令牌、报告文件上传、以及 WS+MQTT 全断时的 claim/done 兜底  
- 现场方案见 IOT 仓 `docs/IOT-Solar自动化试验线上版方案.md`

## MQTT 配置（`solar_agent.json` → `mqtt`）

```json
"mqtt": {
  "enable": true,
  "host": "www.laidecloud.com",
  "port": 11883,
  "username": "mqtt_ops",
  "password": "",
  "topic_prefix": "/EquMessage",
  "qos": 1,
  "use_ssl": false
}
```

与温箱/箱子共用公网 EMQX（`www.laidecloud.com:11883`，明文 MQTT，**不需要 EasyTier**）。  
仅 IOT 云主机已入组网时才用内网 `10.144.144.3:1883`。  
`enable=false` 或未装 `paho-mqtt` 时进度改走 HTTP；`iot_base` 用 `https://` 是因为公网站点本身是 HTTPS，与 MQTT 无关。
