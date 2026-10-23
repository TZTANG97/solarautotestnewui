# 南德完整报告结案自动分析（一期扩展）

## 范围

已在 `PHASE1_AUTO_TESTS` 打通：

- **泰国 PEA 等**（`thai` / `as_nzs` / `uk_g99` / `iec61727`）→ `CEI_Nbis_NanDe`（南德 PEA TDS「总体报告.docx」）
- **意大利 CEI 0-16**（`it_cei`）→ `CEI_Nbis_BeiDe`（北德 Excel + 图喆/麦田式「总体报告.docx」，**不是**南德 TDS）

南德 PEA（`thai` 等）试验码：

| IOT testType | 分析试验码 | 正式产物 |
|---|---|---|
| harmonic | harmonic | Excel + TDS 总体 Word |
| flicker | voltage.fluctuation | Excel + TDS 总体 Word |
| dccomponent | dc.injection | Excel + TDS 总体 Word |
| fixedpf | fixed.displacement.factor | Excel + TDS 总体 Word |
| reconnect | response.to.utility.recover | Excel + TDS 总体 Word |
| ovuf | under.over.frequency | Excel + TDS 总体 Word |

北德 CEI 0-16（`it_cei`，图喆/麦田报告）试验码：

| IOT testType | 分析试验码 | 正式产物 |
|---|---|---|
| harmonic | 3.1 | Excel + 麦田式「总体报告.docx」 |
| flicker | 3.3 | Excel + 麦田式「总体报告.docx」 |
| reconnect | 5 | Excel + 麦田式「总体报告.docx」 |
| ovuf | 4 | Excel + 麦田式「总体报告.docx」 |
| reactiveqin | 6.1 | Excel + 麦田式「总体报告.docx」 |
| fixedpf | 6.7 | Excel + 麦田式「总体报告.docx」 |
| dccomponent | 8.1 | Excel + 麦田式「总体报告.docx」 |

结案成功后 `run_headless.py` 会按标准包自动：

1. 跑对应条款处理器 → 正式 **Excel**
2. `CEI_Nbis_NanDe` → 套 PEA TDS；`CEI_Nbis_BeiDe` → 套图喆 CEI 0-16 模板 → **`总体报告.docx`**

过载 + 巴西 `br_ord140` → `BRAZIL_140/5.4.2` 正式 RTQ Excel 仍保留。

## 网页开测

1. 光伏台架 → 选试验类型（如谐波）
2. **麦田 / CEI 0-16**：国家标准选 **意大利 CEI**（`it_cei`）；**泰国 PEA TDS**：选 **泰国**（`thai`）
3. 填「数据分析额定参数」Pn / Un（CEI 0-16 谐波另填 In）
4. 结案成功后 Agent 自动调 `run_headless.py` 并上传报告

## 本机冒烟

```bat
cd /d E:\solarautotestnewui
pytest tests/test_iot_data_analysis_bridge.py -q
```
