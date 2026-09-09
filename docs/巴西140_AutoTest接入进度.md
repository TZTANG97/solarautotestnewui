# 巴西 ANEEL 140 AutoTest 接入进度

更新日期：2026-08-31

| 试验项 | 标准章节 | AutoTest 对话框 | 状态 | 备注 |
|--------|----------|-----------------|------|------|
| 电压适应性 | 5.4.21 | `Dialog_thaivoltageadaptability` | **已完成** | Chroma 61800 三相 `VOLT:AC`；StopTime 墙钟重算；可选过压/欠压分文件录；默认 list `230-253@30` + `253-230@30` |
| ROCOF 保护 | 5.4.x | `Dialog_thairocof` | **已完成** | 台架数据 `docs/ROCOF.CSV` 三相 ~230V、约 1s 连续录；离线算 df/dt 需勾 FreqU |
| 快速电压变化 | — | `Dialog_thairapidvolt` | **已完成** | 台架 `rapidvolt_change.CSV` 四段全开；Send 自动生成 `RVC_BR_*` 文件名 |
| 动态 Cos(φ) | 5.4.8.3 | `Dialog_thaidynamiccosPhi` | **已完成** | WT+Chroma 真机；P 阶梯 + ASYNC 连续录 `CosPhiP_curve` |
| 动态 QU | 5.4.8.4.2 | `Dialog_thaidynamicQU` | **已完成** | WT+Chroma 真机；ASYNC 连续录 `QU_dyn_curve` |
| 无功能力范围 | 5.4.2 | `Dialog_thaireactiveQcap` | **WT+Chroma 真机完成** | 2026-08-28；连续录 `QCap_BR` / 分开录 `QCap_P*_cos*`；交叉测试 15 passed |
| 定无功 | 5.4.24 | `Dialog_thaifixedQ` | **WT+Chroma 真机完成** | 2026-08-28；连续录 `Qset_BR` / 分开录 `Qset_P*_Q*`；交叉测试 11 passed |
| 无功注入 | 5.4.13 | `Dialog_thaireactiveQin` | **WT+Chroma 真机完成** | 2026-08-28；连续录 `Qin_BR` / 分开录 `Qin_P*_Q*`；交叉测试 8 passed |
| 无功精度 | 5.4.3.3 / VDE | `Dialog_thaireactiveQacc` | **WT+Chroma 真机完成** | 2026-08-28；连续录 `Qacc_BR` / 分开录 `Qacc_P100_Q*`；交叉测试 7 passed |
| 有功调度 | 5.4.23 | `Dialog_thaiactiveP` | **WT+Chroma 真机完成** | 2026-08-28；连续录 `Pdisp_BR` / 分开录 `Pdisp_P*`；交叉测试 7 passed |
| 动态 MPPT | EN50530 | `Dialog_thaidynamicmppt` | **可交付（SoftPanel 语义）** | 全带宽 Gmin↔Gmax；Ramp=(Gmax−Gmin)/Slope；标准斜率表；交叉测试 |
| 频率适应性 | 5.4.20 | `Dialog_thaifrequencyadaptability` | 已完成 | 连续录 1 条 |
| 过频降载 | — | `Dialog_thaiguopinjiangzai` | 已完成 | — |

## 矩阵试验录波方式（连续录 / 分开录）

以下 P×Q 或 P 阶梯矩阵试验 Step3 均提供 **录波方式** 下拉与 **填充推荐文件名**：

| 试验 | 连续录（ASYNC 单文件） | 分开录（col6 逐点） |
|------|------------------------|---------------------|
| 无功能力范围 | `QCap_BR` | `QCap_P{P}_{cos标签}` |
| 定无功 | `Qset_BR` | `Qset_P{P}_Q{Q}` |
| 无功注入 | `Qin_BR` | `Qin_P{P}_Q{Q}` |
| 无功精度 | `Qacc_BR` | `Qacc_P{P}_Q{Q}` |
| 有功调度 | `Pdisp_BR` | `Pdisp_P{P}` |

共享模块：`components/matrix_recording_ui.py`、`utils/matrix_recording_commands.py`。

## 电压适应性（5.4.21）收尾要点

- **单文件连续录**：`VoltAdapt_BR_5421`，首段 `ASYNC_START`、末段 `WAIT_END`。
- **分文件录**：功率分析仪页勾选「过压/欠压分两个文件录制」，文件名 `VoltAdapt_OV_5421,VoltAdapt_UV_5421`，`total_save_file += 2`；过压段结束 `WAIT_END` 后欠压段再 `ASYNC_START`（每段 StopTime 在 `ASYNC_START` 时按命令表重算）。
- **自测**：`code_example/test_voltage_adapt_cross.py`、`tests/test_voltage_adaptability_filename.py`、`code_example/test_chroma_61800_cmds_smoke.py`。

## AC 命令统一模块

连接交流源后，各试验 **Send 时自动** 读取 `SCPITestWave.ac_controller` 的 `*IDN?`：

- **Chroma 61800**：`CONF:COUP AC`、`VOLT:AC`、三相同压末段 `INST:EDIT ALL` 等（见 `utils/ac_scpi_commands.py`）
- **其它 SCPI 源**：爱科/通用 `INST:EDIT EACH` + `VOLT` 路径

电压适应性 / 频率适应性 / ROCOF 已接入；其余带 step1 交流启机的试验将逐步改为 `append_ac_startup_from_ui()`，无需每项单独传 `chroma_61800`。

## ROCOF 台架验收（2026-08-22）

- 数据文件：`docs/ROCOF.CSV`（579 点、约 1s、Urms 三相 ≈230V、有电流与 Sigma）。
- AutoTest 接入：**已完成**（命令走 `ac_scpi_commands`、设定 CSV 含 WT 第 3/4 行）。
- 备注：本 CSV **无频率列**；若 CEI 离线分析 ROCOF 需重录并勾选 **FreqU**。

## 快速电压变化（已完成 2026-08-22）

- 台架：`docs/rapidvolt_change.CSV` 四段全开（207/253/184/276 V）。
- Send 自动生成 `RVC_BR_230-207_230-253_230-184_230-276` 等文件名。

## 无功能力范围（WT+Chroma 真机完成 2026-08-28）

- 自测：`code_example/test_reactive_qcap_cross.py` + `tests/test_reactive_qcap_*.py`（15 passed）。
- 逻辑：功率阶梯 × 极限 cosφ；**连续录** ASYNC 单文件 `QCap_BR`，**分开录** 逐点 col6 `QCap_P{功率}_{cos标签}`。
- 默认：10~100% × cos±0.9，驻留 **1 分钟/点** → 分开录 20 个文件。

## 定无功（WT+Chroma 真机完成 2026-08-28）

- 自测：`code_example/test_fixed_q_cross.py` + `tests/test_fixed_q_*.py`（11 passed）。
- 逻辑：功率外循环 × Q 设定点（%Qmax）；软件**不改机侧 Q 指令**，驻留前人工设 Q。
- 默认：P=`50,100`；Q=`-100,-50,0,50,100`；驻留 **1 分钟/点** → 连续录 `Qset_BR`（10 点）或分开录 10 个 `Qset_P*_Q*`。
- WT：项目数 12；Element1~3；Urms/Irms/P/Q/S/PF/Sigma；50ms；3P4W；自动保存。

## 无功注入（WT+Chroma 真机完成 2026-08-28）

- 自测：`code_example/test_reactive_qin_cross.py` + `tests/test_reactive_qin_*.py`（8 passed）。
- 标准：巴西 Ordinance **5.4.13**；CEI 分析默认 **PF=0.9**、容差 ±0.025。
- 逻辑：功率外循环 × Q 注入/吸收（%Qmax）；软件**不改机侧 Q 指令**，驻留前人工设 Q。
- 默认：P=`20,50,100`；Q=`-100,-50,50,100`；驻留 **1 分钟/点** → 连续录 `Qin_BR`（12 点）或分开录 12 个 `Qin_P*_Q*`。
- WT：项目数 12；Element1~3；Urms/Irms/P/Q/S/PF/Sigma；50ms；3P4W；自动保存。

## 无功精度（WT+Chroma 真机完成 2026-08-28）

- 自测：`code_example/test_reactive_qacc_cross.py` + `tests/test_reactive_qacc_*.py`（7 passed）。
- 标准：VDE AR-N 4105 **5.4.3.3** Measurement of setting accuracy。
- 逻辑：**100%P** 下细粒度 Q 设定点；软件**不改机侧 Q 指令**，驻留前人工设 Q。
- 默认：P=`100`；Q=`-100,-75,-50,-25,0,25,50,75,100`；驻留 **1 分钟/点** → 连续录 `Qacc_BR`（9 点）或分开录 9 个 `Qacc_P100_Q*`。

## 有功调度（WT+Chroma 真机完成 2026-08-28）

- 自测：`code_example/test_active_p_cross.py` + `tests/test_active_p_*.py`（7 passed）。
- 标准：巴西 Ordinance **5.4.23** 有功功率限制/调度；CEI 分析容差 **±2.5%Pn**。
- 逻辑：P 指令阶梯（%Pn）；DC 固定 **100%** 头寸；软件**不改机侧 P 指令**，驻留前人工设 P。
- 默认：P=`100,80,60,40,20,0`；驻留 **1 分钟/点** → 连续录 `Pdisp_BR`（6 点）或分开录 6 个 `Pdisp_P*`。
- WT：项目数 12；Element1~3；Urms/Irms/P/Q/S/PF/Sigma；50ms；3P4W；自动保存。

## 动态 MPPT（可交付 / SoftPanel 语义对齐 2026-08-31）

- **界面**：Step3 与 Chroma SoftPanel 对齐——左栏 Initial Setup / Vmp / Pmpp / FF；页签 `10~50%` / `30~100%` / `Start-up`；表格 Enable / Repetitions / Slope / Ramp / Dwell / Duration；**Slope 改时自动重算 Ramp=(Gmax−Gmin)/Slope**。
- **执行（SoftPanel 语义）**：STC IV → Initial Setup → 进入 **Gmax** → 每周期 **Ramp DN→Dwell→Ramp UP→Dwell**（全带宽 Gmin↔Gmax）；仅当前页签 Enable 行。
- **默认表**：30~100% 用 SoftPanel 斜率 `10/14/20/30/50/100`、Dwell=10、Reps=10（总时长约数小时，可取消勾选）；10~50% / Start-up 同样按带宽自动算 Ramp。
- **品牌 / StopTime / 存读**：Chroma / Itech / Bluesight；StopTime=墙钟+30s（下限120s）；设定 CSV 往返。
- **自测**：`code_example/test_dynamic_mppt_cross.py`（全带宽 DN→UP、Slope 联动 Ramp、三品牌等）。
- **仍有意保留的差异**：斜坡为 1s 步进写 IV（非固件连续斜坡）；无 SoftPanel 在线 ηMPPT/Auto Run/Sandia·CGC 页；CEI 动态分析另项。

### 交付自检清单（动态 MPPT）

- [x] Append / Send / Reset / 存读按钮已接线
- [x] S1↔S3 DC 联动
- [x] SoftPanel 全带宽斜坡 + Slope→Ramp 联动
- [x] STC→IV→Initial Setup→Gmax→DN/UP
- [x] StopTime 含 Initial Setup
- [x] Chroma / Itech / Bluesight 命令冒烟
- [x] 设定 CSV 往返
- [ ] 台架真机一次（人工；建议先只开 1 行 Slope=100）
- [ ] CEI 动态效率报告（另项）

