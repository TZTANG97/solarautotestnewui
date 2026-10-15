# 试点全链路：过载 + 巴西 Ordinance 140 → 数据分析报告

## 目标

把一条试验从开测到报告跑通：

```text
IOT 选 overload + br_ord140 + 填 Pn
  → 台架自动化跑过载
  → 结案 success
  → 本机 SolarTestDataAnalysisApp 无头 5.4.2
  → 上传 processed_5.4.2.csv / Word 报告到 IOT
```

## 前置

1. 台架已装/可访问 `E:\MyProject\SolarTestDataAnalysisApp`  
   （或设环境变量 `SOLAR_DATA_ANALYSIS_ROOT`）
2. 分析项目 `.venv` 可用：`CEI\..\.venv\Scripts\python.exe`
3. SolarAutoTest `dev` 含结案钩子（`iot_data_analysis_bridge`）
4. IOT 开测页过载试验能看到「数据分析额定参数」填 `Pn`

## 开测填写

| 项 | 值 |
|----|----|
| 试验 | 过载能力 / overload |
| 国家标准 | 巴西 Ordinance 140 (`br_ord140`) |
| Pn | 例 `10000`（W）或 `10`（kW，分析侧会换算） |
| SeMax | 可空，默认=Pn |
| 自动追加 / 自动开始 / 等待结束 | 建议都勾选 |

## 本机无仪器冒烟（不接真机）

已可搭「假结案」链路：样例 CSV 当台架产出 → 调分析 → 可选模拟 upload。

```bat
cd /d E:\solarautotestnewui

rem 单元冒烟（pytest）
uv run python -m pytest tests/test_iot_overload_brazil_analysis_e2e.py -q --tb=short

rem 一键模拟结案（推荐看日志）
uv run python code_example/sim_overload_brazil_analysis_chain.py --upload-mock --keep
```

样例 CSV：`tests/fixtures/brazil_overload_542/sample_overload.csv`

模拟脚本会：
1. 在临时目录写入假 `command_data/*.csv`
2. 假 job：`overload` + `br_ord140` + Pn
3. 调 `run_analysis_after_job` → `analysis_reports/job_*`
4. `--upload-mock` 写出将调用的 `upload_report` 清单（不连 IOT）

不覆盖：IOT 开测页 UI、仪器 SCPI、真实 MQTT 结案。那些仍需真机/联调。

## 模拟工况机（接 IOT、不接仪器）

Agent 新模式 `execution_mode=sim`：领取云端任务 → 落样例 CSV → `success` 结案 → 调你已有的 `BRAZIL_140/5.4.2` 模板分析 → `upload_report`。

```bat
cd /d E:\solarautotestnewui
copy config\solar_agent.sim.example.json config\solar_agent.sim.json
rem 编辑 solar_agent.sim.json：iot_base / agent_token / pythonid

uv run python code_example/run_sim_bench_agent.py
```

然后 IOT 开测（绑该 PythonID 台架）：过载 → 巴西 Ordinance 140 → 填 Pn → 开始。

本地校验 runner（不连 IOT）：

```bat
uv run python -m pytest tests/test_sim_bench_runner.py -q --tb=short
```

## 真机走通检查点

1. 试验结束后 `result_summary.data_analysis.success == true`
2. 本机出现 `command_save_files/analysis_reports/job_*/`
3. IOT 实验报告列表能下到分析产出（csv/docx）
4. 若 skip：看 `data_analysis.reason`（常见：缺 Pn、无 CSV、分析根目录找不到）

## 手工无头复现

```bat
cd /d E:\MyProject\SolarTestDataAnalysisApp\CEI
..\.venv\Scripts\python.exe run_headless.py --standard BRAZIL_140 --test 5.4.2 --input <csv目录> --output <out> --params-json "{\"Pn\":10000,\"SeMax\":10000}"
```
