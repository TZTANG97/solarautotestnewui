# 巴西 Ordinance 140 结案自动分析（二期扩面）

在既有过载 `5.4.2` 与一期电能质量/保护条款之外，以下试验在标准选 **br_ord140** 且结案成功时，Agent 会自动跑 `run_headless.py` 并上传报告：

| IOT testType | 分析试验码 | 备注 |
|---|---|---|
| overload | 5.4.2 | 一期试点 |
| flicker | 5.4.16 | |
| harmonic | 5.10 | |
| dccomponent | 5.9 | |
| fixedpf | 5.4.11 | |
| cosphibrazil | 5.4.12 | Cos(φ)_Brazil |
| reactiveqin | 5.4.13 | |
| ovuf | 5.4.15 | 过欠频 |
| reconnect | 5.4.22 | |
| guoqianpin_immun / qianpinshengzai | 5.4.18 | 欠频有功抗扰 |
| guopinjiangzai | 5.4.19 | 过频有功控制 |
| frequencyadaptability | 5.4.20 | |
| voltageadaptability | 5.4.21 | 需 Un |
| activep | 5.4.23 | 有功调度 |
| fixedq | 5.24 | 定无功 |
| staticmppt | 5.4.26 | |

未接分析算法（仍跳过）：相角突变、动态 MPPT、LVRT、快速电压变化等。

网页开测时填「数据分析额定参数」Pn（多数条款）/ Un（谐波、直流、闪变、重连、电压适应性）。

模拟工况（`execution_mode=sim_bench`）已为上表各 testType 造专用 CSV，不再误落 `sample_overload`。

```bat
cd /d E:\solarautotestnewui
uv run python -m pytest tests/test_iot_data_analysis_bridge.py tests/test_iot_job_normalize.py tests/test_iot_sim_by_type.py -q
```
