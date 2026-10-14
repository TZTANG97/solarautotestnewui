# 南德完整报告结案自动分析（一期扩展）

## 范围

已在 `PHASE1_AUTO_TESTS` 打通（标准选 **thai / it_cei / as_nzs / uk_g99 / iec61727** → `CEI_Nbis_NanDe`）：

| IOT testType | 分析试验码 | 正式产物 |
|---|---|---|
| harmonic | harmonic | Excel 模板报告 |
| flicker | voltage.fluctuation | Excel 模板报告 |
| dccomponent | dc.injection | Excel 模板报告 |
| fixedpf | fixed.displacement.factor | Excel 模板报告 |
| reconnect | response.to.utility.recover | Excel 模板报告 |
| ovuf | under.over.frequency | Excel 模板报告 |

多条款 Excel 齐备后，可用分析仓 `CEI_Nbis_NanDe/services/generate_report.py` 套 TDS 模板生成 **总体报告.docx**（完整 Word）。

过载 + 巴西 `br_ord140` → `BRAZIL_140/5.4.2` 正式 RTQ Excel 仍保留。

## 网页开测

1. 光伏台架 → 选试验类型（如谐波）
2. 国家标准选 **意大利 CEI**（`it_cei`）或 **泰国**（`thai`）
3. 填「数据分析额定参数」Pn / Un
4. 结案成功后 Agent 自动调 `run_headless.py` 并上传报告

## 本机冒烟

```bat
cd /d E:\solarautotestnewui
pytest tests/test_iot_data_analysis_bridge.py -q
```
