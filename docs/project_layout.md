# SolarAutoTest 目录地图

仓库约定：**不做一次性大搬家**。动到的代码再迁；根目录禁止再堆 `_tmp*` / 一次性 `test_*.py`。  
本页是「该放哪」的分类；历史债按 Boy Scout 逐步收。

---

## 一眼结构

| 目录 / 入口 | 放什么 | 不要放什么 |
|-------------|--------|------------|
| `SCPITestWave.py` + `start_SolarAutoTest.bat` | 主程序入口（薄；业务继续外迁） | 新增大段试验逻辑 |
| `Dialog_*.py`（根） | **兼容 re-export**；实现已在 `dialogs/` | 勿再往根目录写新 Dialog 实现 |
| `dialogs/` | 试验/设备对话框 UI 实现 | — |
| `devices/` | 仪器连接与读写（AC/DC/WT/德威创…） | UI、试验编排 |
| `components/` | 共用 UI 控件 | 单试验专用大 Dialog |
| `utils/` | 纯函数、IOT handoff/门禁/ETA 等 | Qt 大界面 |
| `agent/` | 独立 Agent 进程（HTTPS/WS/MQTT） | 桌面 UI |
| `sends/`（碰到再迁） | `xxxSend` / `xxxAppend` | — |
| `config/` | 正式配置模板 | 含令牌的本机 `solar_agent.json`（已 gitignore） |
| `tests/` | 正式 pytest | 一次性台架脚本 |
| `docs/` | 说明、方案摘录 | 原始 CSV 录音垃圾（应 gitignore） |
| `code_example/` | 一次性补丁 / 审计 / 冒烟（见下） | 正式运行时依赖 |
| `scripts/scratch/` | 更短命的本地折腾 | 要进版本库的正式工具 |
| `packaging/` / `setup/` | 打包安装 | — |
| `iot_job_inbox/` | 运行时 handoff（gitignore） | 勿提交 |

根目录 `Dialog_*.py` 现为 **一行兼容导入**；实现在 `dialogs/`。新增对话框请直接写在 `dialogs/`，并在根目录补同名 shim（或改调用方 `from dialogs.xxx import`）。

---

## `code_example/` 内部分类

| 子目录 | 用途 | 文件名习惯 |
|--------|------|------------|
| `patches/` | 一次性接线/对齐/生成补丁（跑完可留档） | `_patch_*` `_align_*` `_gen_*` |
| `audits/` | 只读审计、peek、dump 文本 | `_audit_*` `_peek_*` `_scan_*` `*_dump.txt` |
| `smoke/` | 本地冒烟 | `_smoke_*` `_test_*`（非正式 `tests/`） |
| `ops/` | 周报/安装路径/同步类脚本 | `_fill_*` `_sync_*` `*.ps1` |
| `media/` | 样例 CSV/图（大文件少提交） | — |
| `update_e2e/` | E2E 更新联调 | — |

新增一次性脚本：**先放对应子目录**，不要再丢根目录。

---

## 与 IOT 的边界

- 本仓 = 台架软件 + Agent  
- 云端 API / 台架 Live / 实验管理 = `iot` 仓  
- 连通说明见根 [`README.md`](../README.md) 与 IOT `docs/IOT-Solar自动化试验线上版方案.md`
