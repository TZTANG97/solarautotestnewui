# SolarAutoTest（光伏自动化试验台架软件）

工控机侧桌面软件：连电源 / 分析仪 / 示波器 / 德威创，跑 Auto_Test 试验队列；可选对接 **IOT** 做云端开测、进度看板与结案回传。

相关云端仓库：`iot`（方案见其中 `docs/IOT-Solar自动化试验线上版方案.md`）。Agent 细节见 [`agent/README.md`](agent/README.md)。

---

## 分支与发版（以哪个为准）

| 分支 | 角色 | 说明 |
|------|------|------|
| **`dev`** | **当前最新开发 / 日常维护** | 追加队列、是德(Keysight)、Sandia IV / CEI 0-16、Soft Panel、IOT handoff 等均在此线。工控机发版与联调以 **`dev` tip** 为准。 |
| `V1.1` | 历史基线（`dev` 的祖先） | 侧边栏 UI、增量 OSS 打包通道等从此线分出；**不再作为最新功能分支**。 |
| `master` | 极旧主干 | 勿基于此开发或发版。 |

远程：`http://gitlab.wisecom-tech.com/solarapp/solarautotest/solarautotestnewui.git`  
发版产物：`packaging/`（OSS 通道）；近期现场包版本号示例 `20261026.1700`（以当次 `build_release` / OSS 上传记录为准）。

架构说明见 [`docs/项目架构维护指南.md`](docs/项目架构维护指南.md)（维护分支口径与上文一致）。

---

## 怎么开

- **正式/安装版**：双击桌面 **`SolarAutoTest`**（或 `start_SolarAutoTest.bat`）。会静默拉起 Agent，不必单独点「启动 Agent」。
- **开发/测试版（拉了 `dev` 的仓库）**：双击 **`启动测试版.bat`**。与桌面版一样会**自动安装缺失的 uv / Python / 依赖**到 `%LOCALAPPDATA%\SolarAutoTestDev`（国内镜像），再启动 `SCPITestWave.py`。

默认 IOT 地址在 `config/iot_bootstrap.json`（正式一般为 `https://www.laidecloud.com/nss`）。

---

## 和 IOT 怎么通（当前）

```text
IOT Web / 实验管理
    │  startexper（优先 WS，失败 MQTT）
    ▼
Agent（独立进程）── HTTPS 令牌/心跳/报告；MQTT 进度结案
    │  handoff 落盘 iot_job_inbox/
    ▼
桌面 UI 追加 → 开跑 → 写回 results/
```

| 能力 | 状态 |
|------|------|
| 发现上线 / 添加设备领令牌 / 心跳在线 | 已通 |
| Web 下发 → handoff（Auto_Test 全队列） | 已通 |
| 本机开测 → `local-run` 登记实验 | 已通 |
| 进度 / Live（`runSnapshot`：项目、进度、ETA、队列） | 已通 |
| 结案 + 报告上传 | 已通 |
| 双开测并存互斥提示（本机↔云端互挡） | 已通 |
| 开测就绪门禁（设备已连、DC 厂家识别等） | **本机与 Web 共用** |
| 仪器保护上限读回强制比对 | 骨架在，期望全 `null` 时**不拦**（日常靠面板保护 + 上述门禁） |
| `live` 无 UI 直控 / 硬线急停 | 未做 |

**日常开测入口**：Web 实验管理与本机 AutoTest **并存**；不要同台架两边同时抢。

---

## 开测前检查（原有门槛，Web 也会走）

本机点「开始试验」、以及 IOT handoff 开跑前，都会做就绪检查，例如：

- AC/DC 等按试验需要已连接  
- DC 厂家已识别，拦截品牌命令混用（如致茂 IVC 误发蓝点）  
- 关键参数 / IV 超范围等试验内校验  

请仍先在**仪器面板**设好保护档。`config/iot_output_limits.json` 仅在现场填写期望且 `enforce=true` 时才额外读回比对；默认不启用。

---

## 现场最短路径

1. 仪器上电，面板设好保护。  
2. 打开本软件 → 首页 Agent「运行中」，IOT 台架在线。  
3. 「扫描并连接设备」指定槽位并连接。  
4. **本机**：选项目 → 追加 → 开始。  
5. **或 Web**：实验管理开测（`auto_append` / `auto_start`）；桌面需已打开以 handoff。  
6. 网页看进度 / Live；结束后详情下附件。停测优先本机「结束试验」或软件急停。

异常看操作日志里的 `[IOT-handoff]` / `[IOT-Agent]`。

---

## 目录怎么分（别再全堆根目录）

完整地图见 [`docs/project_layout.md`](docs/project_layout.md)。摘要：

| 位置 | 职责 |
|------|------|
| `devices/` `utils/` `components/` `agent/` | 设备 / 纯逻辑 / 控件 / IOT Agent |
| `Dialog_*.py` | **兼容 shim**（实现在 `dialogs/`） |
| `dialogs/` | 试验/设备对话框 UI 实现 |
| `tests/` | 正式单测 |
| `code_example/patches\|audits\|smoke\|ops/` | 一次性补丁 / 审计 / 冒烟 / 运维脚本 |
| `docs/` | 说明文档 |

**禁止**：再往仓库根加 `_tmp*`、一次性 `test_*.py`；正式逻辑禁止继续堆进巨型 `SCPITestWave.py`。

## 开发与迁移约定

- 启动：`uv run python SCPITestWave.py`（或上述 bat）。  
- 增量迁移（Boy Scout）：动到的 `xxxSend`/`xxxAppend` → `sends/`；纯函数 → `utils/`；共用控件 → `components/`；一次性脚本 → `code_example/` 对应子目录。见 [`docs/incremental_migration.md`](docs/incremental_migration.md)、[`docs/project_layout.md`](docs/project_layout.md)。  
- 单测示例：`uv run python -m pytest tests/test_iot_output_limits.py tests/test_run_progress_eta.py -q`（需 `PYTHONPATH` 指向仓库根）。

---

## 配置要点

| 文件 | 作用 |
|------|------|
| `config/iot_bootstrap.json` | 默认 IOT Base URL |
| `config/solar_agent.json` | 令牌、pythonid、MQTT 等（勿整机拷贝到别的电脑） |
| `config/iot_output_limits.json` | 可选保护上限期望；全 null = 不启用强制读回 |

Agent 进程、MQTT topic、handoff 目录等见 [`agent/README.md`](agent/README.md)。
