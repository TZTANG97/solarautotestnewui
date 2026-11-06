# -*- coding: utf-8 -*-
"""Batch-2 operator docs: remaining Auto_Test items."""
from __future__ import annotations

from pathlib import Path

OUT = Path(r"E:\utoo\utoo-pydjango\utoo-web-front\public\autotest-docs\pages")


def ac_dc(wait: str, wait_u: str, start: str, start_u: str, note: str = "") -> str:
    n = f'<p class="muted">{note}</p>' if note else ""
    return f"""
<h2>① AC/DC 与时序 — 怎么填</h2>
<p>通章见「试验条件怎么填」。本试验推荐示例如下。</p>
{n}
<h3>交流 · 单相</h3>
<div class="table-wrap"><table><thead><tr><th>项</th><th>填写</th></tr></thead><tbody>
<tr><td>交流电源</td><td>开启</td></tr>
<tr><td>相位</td><td><strong>单相</strong></td></tr>
<tr><td>交流电压1</td><td><strong>230</strong> V</td></tr>
<tr><td>频率</td><td><strong>50</strong> Hz</td></tr>
</tbody></table></div>
<h3>交流 · 三相</h3>
<div class="table-wrap"><table><thead><tr><th>项</th><th>填写</th></tr></thead><tbody>
<tr><td>相位</td><td><strong>三相</strong></td></tr>
<tr><td>电压1/2/3</td><td><strong>230 / 230 / 230</strong> V</td></tr>
<tr><td>频率</td><td><strong>50</strong> Hz</td></tr>
</tbody></table></div>
<h3>直流</h3>
<ul><li>入门只勾 <strong>直流电源1</strong>，开启；IV 示例 Vmp220 Imp10 Voc220 Isc10 功率100%。</li>
<li>多路机按接线勾 DC2～4。</li></ul>
<h3>等待 / 启机</h3>
<div class="table-wrap"><table><thead><tr><th>名称</th><th>含义</th><th>示例</th></tr></thead><tbody>
<tr><td>等待时间</td><td>交流开出后站稳</td><td><strong>{wait}</strong> {wait_u}</td></tr>
<tr><td>启机时间</td><td>交直流开完后等并网</td><td><strong>{start}</strong> {start_u}</td></tr>
</tbody></table></div>
""".strip()


def analyzer(extra: str = "") -> str:
    return f"""
<h2>② 功率分析仪 — 怎么选怎么配</h2>
<ol>
<li>设备管理先连好 WT / 德威创。</li>
<li>本步选与台架一致的型号；有德威创模式的试验按台架选。</li>
<li>设路径、文件名、连续录/分开录；德威创须刷新并「测试生效」。</li>
</ol>
{extra}
""".strip()


def ops(*items: str) -> str:
    lis = "\n".join(f"<li>{x}</li>" for x in items)
    return f"""
<h2>操作顺序（照做）</h2>
<ol>
{lis}
<li>点 <strong>测试追加</strong> → 开始。改参数后重新追加。</li>
</ol>
""".strip()


def page(title: str, menu: str, steps: list[str], body: str, wait="3", wait_u="秒", start="5", start_u="分钟", note="", ana="") -> str:
    sl = "\n".join(f"<li>{s}</li>" for s in steps)
    return f"""
<h1>{title} <span class="badge">已就绪</span></h1>
<p class="muted">菜单：Auto_Test → {menu}。先完成设备连接。</p>
<div class="callout ok">前置：交流/直流/分析仪就绪。通用填法见「试验条件怎么填」。</div>
<h2>本试验步骤一览</h2>
<ol>
{sl}
</ol>
{ac_dc(wait, wait_u, start, start_u, note)}
{analyzer(ana)}
{body}
""".strip()


PAGES: dict[str, str] = {}

PAGES["test-ovuf.html"] = page(
    "过欠压 / 过欠频",
    "过欠压_过欠频",
    ["① AC/DC 电源", "② 功率分析仪", "③～⑥ 过欠压 1～4", "⑦ 过欠频", "⑧ 关机"],
    """
<h2>③～⑥ 过欠压段 — 示例一套</h2>
<p>每一段通常含「交流电压变动区间」「频率变动区间」及本段采集/驻留。入门建议：</p>
<ul>
<li>启机电网用 230 V / 50 Hz（单相或三相按样机）。</li>
<li>正式试验按规程填各段过压/欠压目标与恢复；冒烟可只勾 <strong>过欠压1</strong>。</li>
<li>电压变动不要超过台架与规程允许范围。</li>
</ul>
<div class="callout">四段过欠压 + 过欠频都勾选时总时长较长；第一次先只跑一段确认录波正常。</div>
<h2>⑦ 过欠频</h2>
<p>按规程填频率变动区间；单位与启机频率一致（例 50 Hz 基准）。</p>
<h2>⑧ 关机</h2>
<p>勾选关机步。</p>
<div class="callout ok"><strong>示例汇总</strong>：三相 230×3+50；只勾 DC1；等待 3 秒；启机 5 分钟；先只勾过欠压1 冒烟。</div>
"""
    + ops("连设备", "填启机 AC/DC/时序", "配分析仪", "勾过欠压/过欠频段 → 关机"),
    wait="3",
)

PAGES["test-static-cos.html"] = page(
    "静态 Cos(φ)",
    "静态Cos(φ)",
    ["① AC/DC 电源", "② 功率分析仪", "③ cosPhi 设置", "④ 关机"],
    """
<h2>③ cosPhi 设置 — 示例一套</h2>
<div class="table-wrap"><table><thead><tr><th>项</th><th>示例</th></tr></thead><tbody>
<tr><td>功率档(%)</td><td>逗号分隔，如 <strong>100,90,80,70</strong>（空则用各卡功率%）</td></tr>
<tr><td>每点驻留</td><td><strong>30</strong> 秒（勿误用很长「分钟」导致空录过久）</td></tr>
<tr><td>cosφ 勾选</td><td>按规程勾要测的 cosφ 点；机侧曲线事先设好</td></tr>
<tr><td>录波</td><td>连续录单文件（如 CosPhi_BR）；分开录则每点一文件</td></tr>
</tbody></table></div>
<div class="callout">软件扫功率×cosφ 并录波；机侧位移因数由试验员预先设定。</div>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待/启机 5 秒与 5 分钟；功率档 100,90,80；驻留 30 秒；连续录。</div>
"""
    + ops("连设备", "填启机", "配 WT", "功率档+cosφ+驻留 → 关机"),
    wait="5",
    start="5",
)

PAGES["test-static-qu.html"] = page(
    "静态 QU",
    "静态QU",
    ["① AC/DC", "② 功率分析仪", "③ 电压阶梯", "④～⑥ QU测试2～4", "⑦ 判定", "⑧ 关机"],
    """
<h2>③ 电压阶梯 — 示例一套</h2>
<div class="table-wrap"><table><thead><tr><th>项</th><th>示例</th></tr></thead><tbody>
<tr><td>Un（基准电压）</td><td><strong>230</strong> V</td></tr>
<tr><td>电压 list</td><td>按规程填 U 序列（逗号分隔）；连续录 1 条 QU_curve</td></tr>
<tr><td>每点驻留</td><td>按界面默认或规程（常见数十秒级）</td></tr>
</tbody></table></div>
<p>后续 QU测试2～4、判定：按规程勾选；冒烟可只做电压阶梯段。</p>
<div class="callout ok"><strong>示例汇总</strong>：启机 230/50；DC1；等待/启机 5 秒与 5 分钟；Un=230；电压 list 按规程；连续录。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "电压 list →（可选后续段）→ 关机"),
    wait="5",
    start="5",
)

PAGES["test-active-p.html"] = page(
    "有功调度",
    "有功调度",
    ["① AC/DC", "② 功率分析仪", "③ P 调度", "④ 关机"],
    """
<h2>③ P 调度 — 示例一套</h2>
<div class="table-wrap"><table><thead><tr><th>项</th><th>示例</th></tr></thead><tbody>
<tr><td>启用有功调度工况</td><td>勾选</td></tr>
<tr><td>P指令(%Pn)</td><td><strong>100,80,60,40,20,0</strong></td></tr>
<tr><td>DC功率头寸(%)</td><td><strong>100</strong>（通常满功率，保证机侧限功率有头寸）</td></tr>
<tr><td>每点驻留</td><td><strong>1</strong> 分钟（界面默认；可按规程改）</td></tr>
<tr><td>录波</td><td>连续录或分开录按需要</td></tr>
</tbody></table></div>
<div class="callout">软件发功率指令阶梯并录波；机侧调度功能需事先投入。</div>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待/启机 5 秒与 5 分钟；P list 如上；头寸 100%；驻留 1 分钟。</div>
"""
    + ops("连设备", "填启机", "配 WT", "填 P list → 关机"),
    wait="5",
    start="5",
)

PAGES["test-overfreq.html"] = page(
    "过频降载",
    "过频降载",
    ["① AC/DC", "② 功率分析仪", "③ 过频设置", "④ 关机"],
    """
<h2>③ 过频频率 list — 示例一套</h2>
<div class="table-wrap"><table><thead><tr><th>项</th><th>示例</th></tr></thead><tbody>
<tr><td>启用频率台阶</td><td>勾选</td></tr>
<tr><td>台阶电压</td><td><strong>230</strong> V</td></tr>
<tr><td>频率Hz(list)</td><td><strong>50,50.25,50.7,51.15,50.7,50.25,50</strong></td></tr>
<tr><td>每点驻留</td><td><strong>60</strong> 秒</td></tr>
<tr><td>录波</td><td>连续录 1 条</td></tr>
</tbody></table></div>
<div class="callout ok"><strong>示例汇总</strong>：启机 230/50；DC1；等待 3 秒；启机 5 分钟；过频 list 用界面默认往返扫频。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "填频率 list → 关机"),
)

PAGES["test-underfreq.html"] = page(
    "欠频升载",
    "欠频升载",
    ["① AC/DC", "② 功率分析仪", "③ 欠频设置", "④ 关机"],
    """
<h2>③ 欠频频率 list — 示例一套</h2>
<div class="table-wrap"><table><thead><tr><th>项</th><th>示例</th></tr></thead><tbody>
<tr><td>启用频率台阶</td><td>勾选</td></tr>
<tr><td>台阶电压</td><td><strong>230</strong> V</td></tr>
<tr><td>频率Hz(list)</td><td><strong>50,49.75,49.5,49.25,49.0,49.25,49.5,49.75,50</strong></td></tr>
<tr><td>每点驻留</td><td><strong>60</strong> 秒</td></tr>
</tbody></table></div>
<div class="callout ok"><strong>示例汇总</strong>：启机 230/50；DC1；等待 3 秒；启机 5 分钟；欠频 list 用界面默认。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "填频率 list → 关机"),
)

PAGES["test-fixed-q.html"] = page(
    "固定无功 Q",
    "固定Q",
    ["① AC/DC", "② 功率分析仪", "③ Q 设定", "④ 关机"],
    """
<h2>③ Q 设定 — 示例一套</h2>
<ul>
<li>按规程勾选 Q 工况点 / 列表（界面为 Q 设定页）。</li>
<li>每点驻留常见默认约 <strong>1</strong> 分钟量级；连续录时 StopTime 为上限。</li>
<li>机侧无功设定由试验员预先投入；软件负责工况与录波。</li>
</ul>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待/启机 5 秒与 5 分钟；只勾少量 Q 点冒烟。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "勾 Q 点 → 关机"),
    wait="5",
    start="5",
)

PAGES["test-qin.html"] = page(
    "无功注入",
    "无功注入",
    ["① AC/DC", "② 功率分析仪", "③ Q 设定", "④ 关机"],
    """
<h2>③ Q 设定 — 示例一套</h2>
<p>与固定 Q 类似：勾选注入工况，填驻留（常见约 1 分钟），连续录。机侧无功模式事先设好。</p>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待/启机 5 秒与 5 分钟；先 1～2 个 Q 点冒烟。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "Q 工况 → 关机"),
    wait="5",
    start="5",
)

PAGES["test-qacc.html"] = page(
    "无功精度",
    "无功精度",
    ["① AC/DC", "② 功率分析仪", "③ Q 设定", "④ 关机"],
    """
<h2>③ Q 设定 — 示例一套</h2>
<p>按精度试验规程勾选目标 Q 点；每点驻留常见约 1 分钟；连续录。软件不发机侧 P/Q 设定值，只录响应。</p>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待/启机 5 秒与 5 分钟；少点冒烟后全开。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "Q 点 → 关机"),
    wait="5",
    start="5",
)

PAGES["test-qcap.html"] = page(
    "无功能力",
    "无功能力",
    ["① AC/DC", "② 功率分析仪", "③ 能力工况", "④ 关机"],
    """
<h2>③ 能力工况 — 示例一套</h2>
<p>勾选规程要求的 Q 能力工况组合；驻留约 1 分钟量级；注意机侧已处相应无功能力模式。</p>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待/启机 5 秒与 5 分钟；先 1 个工况冒烟。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "能力工况 → 关机"),
    wait="5",
    start="5",
)

PAGES["test-dyn-cos.html"] = page(
    "动态 Cos(φ)",
    "动态Cos(φ)",
    ["① AC/DC", "② 功率分析仪", "③ 功率阶梯", "④ 关机"],
    """
<h2>③ 功率阶梯 — 示例一套</h2>
<ul>
<li>按规程填功率阶梯 list（%Pn）。</li>
<li>每点驻留界面常见默认约 <strong>5</strong> 分钟量级（可按规程改短冒烟）。</li>
<li>连续录 1 条曲线跟踪 cosφ(P)；机侧动态曲线事先设好。</li>
</ul>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待/启机 5 秒与 5 分钟；功率阶梯按规程；连续录。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "功率阶梯 → 关机"),
    wait="5",
    start="5",
)

PAGES["test-dyn-qu.html"] = page(
    "动态 QU",
    "动态QU",
    ["① AC/DC", "② 功率分析仪", "③ 电压阶梯", "④ 关机"],
    """
<h2>③ 电压阶梯 — 示例一套</h2>
<p>填动态 Q(U) 的电压阶梯 list 与驻留；连续录跟踪。机侧动态 QU 曲线事先设好。</p>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待/启机 5 秒与 5 分钟；电压 list 按规程。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "电压阶梯 → 关机"),
    wait="5",
    start="5",
)

PAGES["test-pu.html"] = page(
    "Test_PU",
    "Test_PU",
    ["① AC/DC", "② 功率分析仪+PU", "③ PU 测试", "④ 关机"],
    """
<h2>③ PU 测试 — 示例一套</h2>
<p>按规程填电压 list / PU 曲线相关设定；连续录 PU_curve。基准电压常用 230 V。</p>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待/启机 5 秒与 5 分钟；电压 list 按规程；连续录。</div>
"""
    + ops("连设备", "填启机", "配分析仪+PU", "PU 段 → 关机"),
    wait="5",
    start="5",
)

PAGES["test-rocof.html"] = page(
    "RoCoF",
    "RoCoF",
    ["① AC/DC", "② 功率分析仪", "③ ROCOF设置", "④ 关机"],
    """
<h2>③ ROCOF 设置 — 示例一套</h2>
<p>按欧洲/对应规程填频率变化率相关台阶或 list（勿与巴西频率适应性混用）。驻留与限值以对话框与规程为准。</p>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待 3 秒；启机 5 分钟；ROCOF 参数按规程；少段冒烟。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "ROCOF 参数 → 关机"),
)

PAGES["test-freq-adapt.html"] = page(
    "频率适应性",
    "频率适应性",
    ["① AC/DC", "② 功率分析仪", "③ 频率适应性", "④ 频率扫描", "⑤ 关机"],
    """
<h2>③～④ 频率适应性 / 扫描 — 示例一套</h2>
<ul>
<li>③：适应性相关设定按规程勾选。</li>
<li>④：频率扫描 list（过频/欠频方向以规程为准），每点驻留按界面。</li>
<li>须用连续录，保证扫频与录波同时进行。</li>
</ul>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待 3 秒；启机 5 分钟；扫描 list 先缩短点数冒烟。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "适应性+扫描 → 关机"),
)

PAGES["test-volt-adapt.html"] = page(
    "电压适应性",
    "电压适应性",
    ["① AC/DC", "② 功率分析仪", "③ 电压适应性", "④ 电压扫描", "⑤ 关机"],
    """
<h2>③～④ 电压适应性 / 扫描 — 示例一套</h2>
<p>与频率适应性类似：先适应性设定，再电压 list 扫描；基准常用 230 V；连续录。</p>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待 3 秒；启机 5 分钟；扫描点数冒烟可减少。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "适应性+电压扫描 → 关机"),
)

PAGES["test-rapid-volt.html"] = page(
    "快速电压变化",
    "快速电压变化",
    ["① AC/DC", "② 功率分析仪", "③ 快速电压变化", "④ 关机"],
    """
<h2>③ 快速电压变化 — 示例一套</h2>
<p>按规程填快速电压台阶/序列与驻留；分析仪可用 WT 或德威创（有模式切换时按台架）。</p>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待 3 秒；启机 5 分钟；少台阶冒烟。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "快速电压参数 → 关机"),
)

PAGES["test-volt10min.html"] = page(
    "10min 过压保护",
    "10min过压保护",
    ["① AC/DC", "② 功率分析仪", "③ 过压保护", "④ 保护后恢复", "⑤ 关机"],
    """
<h2>③～④ 过压与恢复 — 示例一套</h2>
<div class="table-wrap"><table><thead><tr><th>项</th><th>示例</th></tr></thead><tbody>
<tr><td>过压保护相关时长</td><td>界面常见约 <strong>10</strong> 分钟量级（以标签为准）</td></tr>
<tr><td>保护后恢复</td><td>按规程填恢复电压/等待</td></tr>
</tbody></table></div>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待 3 秒；启机 5 分钟；保护时长按规程；冒烟可缩短（若规程允许）。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "过压→恢复→关机"),
)

PAGES["test-immun.html"] = page(
    "过欠频免疫",
    "过欠频免疫",
    ["① AC/DC", "② 功率分析仪", "③ 频率扫描", "④ 关机"],
    """
<h2>③ 频率扫描 — 示例一套</h2>
<ul>
<li>勾选「更新率」时，常见默认约 <strong>200</strong> ms 量级（以界面为准）。</li>
<li>频率扫描 list / 段按规程；连续录与扫频同步。</li>
</ul>
<div class="callout ok"><strong>示例汇总</strong>：230/50；DC1；等待 3 秒；启机 5 分钟；更新率按默认；扫描段先缩短冒烟。</div>
"""
    + ops("连设备", "填启机", "配分析仪", "频率扫描 → 关机"),
)

PAGES["test-static-mppt.html"] = page(
    "静态 MPPT",
    "静态MPPT",
    ["① AC/DC", "② 功率分析仪", "③ 测试功率段", "④ MPPT设置", "⑤ 关机"],
    """
<h2>③～④ 功率段 / MPPT — 示例一套</h2>
<div class="table-wrap"><table><thead><tr><th>项</th><th>示例</th></tr></thead><tbody>
<tr><td>直流路径</td><td>国产台架常选 <strong>蓝电</strong>：设备管理先连 IP，SAS 模式+参数已下发</td></tr>
<tr><td>总测试时长</td><td>约 <strong>0 时 30 分</strong></td></tr>
<tr><td>单次/每段</td><td>约 <strong>0 时 5 分</strong></td></tr>
<tr><td>功率段</td><td>按界面勾选（如含 100% 等）；冒烟少勾</td></tr>
<tr><td>录波文件</td><td>如 StaticMPPT_BR 连续录</td></tr>
</tbody></table></div>
<div class="callout">IV 为各点曲线参数；功率段% 会缩放 Imp/Isc。现场曲线以组件/蓝电设定为准。</div>
<div class="callout ok"><strong>示例汇总</strong>：230/50；只勾 DC1+蓝电已 SAS；总 30 分/单次 5 分；少功率段冒烟。</div>
"""
    + ops("连 AC + 蓝电并应用模式", "填启机", "配 WT", "功率段+MPPT → 关机"),
)

for name, html in PAGES.items():
    path = OUT / name
    path.write_text(html + "\n", encoding="utf-8")
    print("wrote", name, len(html))
print("DONE", len(PAGES))
