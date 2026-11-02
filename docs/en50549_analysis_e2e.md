# EN 50549 结案自动分析

国家标准选 **欧洲 EN 50549**（`en50549` / 别名 `cn_gb`）时，结案成功后 Agent 走 `CEI_Nbis_BeiDe_50549` 包（**不是** CEI 0-16 北德包）。

| IOT testType | 分析试验码 | 额定参数 |
|---|---|---|
| voltageadaptability | 5.2 | — |
| phasejump | 5.3.2 | 需工况图 PNG（CSV 仅占位） |
| lvrt | 5.3.3 | Pn / Un |
| frequencyadaptability | 5.4.3 | Pn |
| guopinjiangzai | 5.4.3.2 | Pn |
| qianpinshengzai / guoqianpin_immun | 5.4.3.3 | Pn |
| reactiveqcap | 5.5.1.3 | SeMax / Qmax / Qmin |
| reactiveqacc / fixedq | 5.5.2.3.2 | SeMax / Qmax / Qmin |
| flicker | 5.7.2.3.3 | — |
| dccomponent | 5.7.2.4 | Pn / Un |
| ovuf | 5.8.3.2 | — |
| voltprotect10min | 5.8.3.3 | Un |
| rocof / rocofprotect | 5.8.3.4.1 | Pn / Un |
| rocofreset | 5.8.3.4.2 | Pn / Un |
| reconnect | 5.9 | Pn / Un |
| activep | 5.10.3.2 | Pn / Srated(Pmax) |

说明：

- IOT「ROCOF保护」对应 **5.8.3.4.1**（设定值精度与动作时间），不是抗扰度 **5.3.1**（暂无独立 testType）。
- **5.7.2** 三相不平衡、**5.10.3.3** 有功调度动态、**5.5.2.4.2** Q(U) 稳态：分析侧已有或待交付处理器，但 IOT 尚无对应开测类型，暂未挂映射。
- 未挂处理器的试验（如 `harmonic`、`overload`、`fixedpf`）在 `en50549` 下**跳过分析**，不会误落到南德默认码。

德系 `de_vde` 仍走 `CEI_Nbis_BeiDe`（0-21 / A.x）。

```bat
cd /d E:\solarautotestnewui
uv run python -m pytest tests/test_iot_data_analysis_bridge.py tests/test_iot_sim_by_type.py -q
```
