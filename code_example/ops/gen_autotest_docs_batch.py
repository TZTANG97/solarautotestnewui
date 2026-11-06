# -*- coding: utf-8 -*-
"""Generate operator-facing test doc pages for autotest-docs (skill format)."""
from __future__ import annotations

from pathlib import Path

OUT = Path(r"E:\utoo\utoo-pydjango\utoo-web-front\public\autotest-docs\pages")


def ac_dc_block(
    *,
    wait: str,
    wait_unit: str,
    startup: str,
    startup_unit: str,
    ac_note: str = "",
) -> str:
    note = f"<p class=\"muted\">{ac_note}</p>" if ac_note else ""
    return f"""
<h2>① AC/DC 与时序 — 怎么填</h2>
<p>通用填法详见左侧「试验条件怎么填（通用）」。下面是<strong>本试验推荐示例</strong>。</p>
{note}
<h3>交流 · 单相（示例）</h3>
<div class="table-wrap"><table>
<thead><tr><th>界面项</th><th>填写</th></tr></thead>
<tbody>
<tr><td>交流电源</td><td>开启</td></tr>
<tr><td>相位</td><td><strong>单相</strong></td></tr>
<tr><td>交流电压1</td><td><strong>230</strong> V</td></tr>
<tr><td>频率</td><td><strong>50</strong> Hz</td></tr>
</tbody></table></div>

<h3>交流 · 三相（示例）</h3>
<div class="table-wrap"><table>
<thead><tr><th>界面项</th><th>填写</th></tr></thead>
<tbody>
<tr><td>交流电源</td><td>开启</td></tr>
<tr><td>相位</td><td><strong>三相</strong></td></tr>
<tr><td>交流电压1 / 2 / 3</td><td><strong>230 / 230 / 230</strong> V</td></tr>
<tr><td>频率</td><td><strong>50</strong> Hz</td></tr>
</tbody></table></div>
<p class="muted">现场额定不是 230/50 时改成铭牌值，填法相同。</p>

<h3>直流 · 勾几个、填什么</h3>
<ul>
<li>入门 / 单路台架：只勾 <strong>直流电源1</strong>，DC2～4 取消勾选，开关选「开启」。</li>
<li>多路接线：接几路勾几路，每路填 IV。</li>
</ul>
<div class="table-wrap"><table>
<thead><tr><th>通道</th><th>勾选</th><th>开关</th><th>Vmp</th><th>Imp</th><th>Voc</th><th>Isc</th><th>功率%</th></tr></thead>
<tbody>
<tr><td>直流电源1</td><td>✔</td><td>开启</td><td>220</td><td>10</td><td>220</td><td>10</td><td>100</td></tr>
<tr><td>直流电源2～4</td><td>不勾</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
</tbody></table></div>

<h3>等待时间 / 启机时间</h3>
<div class="table-wrap"><table>
<thead><tr><th>名称</th><th>含义</th><th>本试验示例</th></tr></thead>
<tbody>
<tr><td>等待时间</td><td>交流开出后先等电网站稳</td><td><strong>{wait}</strong> {wait_unit}</td></tr>
<tr><td>启机时间</td><td>交直流开完后再等逆变器并网起来</td><td><strong>{startup}</strong> {startup_unit}</td></tr>
</tbody></table></div>
""".strip()


def analyzer_block(extra: str) -> str:
    return f"""
<h2>② 功率分析仪 — 怎么选怎么配</h2>
<ol>
<li>设备管理里先把 WT 或德威创连上。</li>
<li>试验对话框本步：型号与台架一致（如 WT3000）；有「德威创模式」的试验按台架选用。</li>
<li>填保存路径、文件名；选「一条线连续录」或「分开录」（以界面为准）。</li>
<li>德威创：刷新电力组 → 勾导出 → 点「测试生效/应用」。</li>
</ol>
{extra}
""".strip()


def footer_ops(steps: list[str]) -> str:
    lis = "\n".join(f"<li>{s}</li>" for s in steps)
    return f"""
<h2>操作顺序（照做）</h2>
<ol>
{lis}
<li>点 <strong>测试追加</strong> → 开始试验。改参数后必须重新追加。</li>
</ol>
""".strip()


PAGES = {}

PAGES["test-flicker.html"] = f"""
<h1>电压闪变 <span class="badge">已就绪</span></h1>
<p class="muted">菜单：Auto_Test → 电压闪变。先完成设备连接，再按示例录入。</p>
<div class="callout ok">前置：交流/直流/分析仪已连接。通用填法见「试验条件怎么填」。</div>

<h2>本试验步骤一览</h2>
<ol>
<li>① AC/DC 电源</li>
<li>② 闪变（WT3000闪变 或 德威创模式）</li>
<li>③ DC 开关循环</li>
<li>④ 判定结果</li>
<li>⑤ 关机设置</li>
</ol>

{ac_dc_block(wait="5", wait_unit="秒", startup="5", startup_unit="分钟",
             ac_note="本试验界面电压框若为空，请手动填 230 / 50（或现场额定）。")}

{analyzer_block('''
<div class="callout">本试验顶部可切换 <strong>WT3000闪变</strong> / <strong>德威创模式</strong>。选哪边，后面步骤②④就跟哪边配置。</div>
<h3>WT3000 闪变（示例）</h3>
<div class="table-wrap"><table>
<thead><tr><th>界面项</th><th>示例</th></tr></thead>
<tbody>
<tr><td>相位（WT）</td><td>与样机一致：单相或三相</td></tr>
<tr><td>ELEMENT</td><td>单相常用 ELEMENT1；三相按接线选</td></tr>
<tr><td>每组闪变</td><td><strong>3</strong> 次</td></tr>
<tr><td>首次闪变间隔</td><td><strong>4</strong> 分钟</td></tr>
</tbody></table></div>
<p class="muted">德威创模式：勾闪变相关项，短/长闪变时间按规程；刷新后点应用再追加。</p>
''')}

<h2>③ DC 开关循环 — 示例一套</h2>
<p>用于在测量过程中按设定时长循环开关直流，模拟工况。界面常见项：</p>
<div class="table-wrap"><table>
<thead><tr><th>界面项</th><th>示例</th><th>说明</th></tr></thead>
<tbody>
<tr><td>循环相关时长</td><td>按界面默认（如持续约 15 秒量级）</td><td>以对话框标签为准</td></tr>
<tr><td>间隔/等待类时长</td><td>界面默认约 <strong>2</strong> 分钟一档</td><td>须满足「首次间隔 + 次数×持续 + (次数-1)×间隔」不超软件上限（约 600 秒）</td></tr>
<tr><td>循环次数</td><td><strong>12</strong></td><td>冒烟可改小，如 2～3 次</td></tr>
</tbody></table></div>
<div class="callout">若追加时报时长超限，把间隔或次数改小后再追加。</div>

<h2>④ 判定结果</h2>
<p>按所选模式（WT / 德威创）勾选判定步，保持默认即可；正式试验按规程核对限值相关选项。</p>

<h2>⑤ 关机</h2>
<p>勾选关机步；习惯先关直流再关交流。</p>

<div class="callout ok">
<strong>示例一套汇总（入门）</strong>：三相 230/230/230 + 50 Hz（或单相 230/50）；只勾 DC1；等待 5 秒；启机 5 分钟；WT3000闪变、每组 3 次、首次间隔 4 分钟；循环次数可先改 2 做冒烟。
</div>

{footer_ops([
    "设备管理连接就绪。",
    "打开电压闪变 → 填 AC/DC/时序。",
    "选 WT 或德威创 → 填闪变参数。",
    "填 DC 循环（冒烟可减少次数）→ 判定 → 关机。",
])}
""".strip()

PAGES["test-harmonic.html"] = f"""
<h1>谐波电流 <span class="badge">已就绪</span></h1>
<p class="muted">菜单：Auto_Test → 谐波电流。先连设备，再按示例录入。</p>
<div class="callout ok">前置：AC/DC/分析仪就绪。通用填法见「试验条件怎么填」。</div>

<h2>本试验步骤一览</h2>
<ol>
<li>① AC/DC 电源</li>
<li>② 功率分析仪（WT3000谐波 或 德威创模式）</li>
<li>③ 谐波设置（数据采集 + 谐波 1～12 次工况卡片）</li>
<li>④ 关机设置</li>
</ol>

{ac_dc_block(wait="3", wait_unit="秒", startup="5", startup_unit="分钟")}

{analyzer_block('''
<div class="callout">顶部切换 <strong>WT3000谐波</strong> / <strong>德威创模式</strong>。德威创常用刷新率 <strong>SYNC to HARMONIC</strong>；勾谐波测量后点应用。</div>
<h3>德威创谐波（常见示例）</h3>
<div class="table-wrap"><table>
<thead><tr><th>界面项</th><th>示例</th></tr></thead>
<tbody>
<tr><td>谐波/简谐波</td><td>勾选</td></tr>
<tr><td>最大谐波次数</td><td>按规程（如 40）</td></tr>
<tr><td>THD 计算谐波次数</td><td><strong>40</strong></td></tr>
<tr><td>最大刷新率</td><td>SYNC to HARMONIC</td></tr>
<tr><td>保存路径 / 文件名</td><td>自建目录，如 harmonic_run1</td></tr>
</tbody></table></div>
''')}

<h2>③ 谐波设置 — 示例一套</h2>
<h3>数据采集</h3>
<div class="table-wrap"><table>
<thead><tr><th>界面项</th><th>示例</th></tr></thead>
<tbody>
<tr><td>数据采集时长</td><td><strong>10</strong>（单位按界面，常见分钟）</td></tr>
<tr><td>等待类间隔</td><td><strong>1</strong>（单位按界面）</td></tr>
</tbody></table></div>

<h3>谐波工况卡片（1～12 次）</h3>
<p>每一「次」是一个功率工况卡片：勾选要做的次，并勾与 step1 对应的直流通道，功率% 默认常为 <strong>100</strong>。入门建议：</p>
<ul>
<li>只勾 <strong>谐波 1次</strong>（或前 2～3 次）做冒烟；正式试验再按规程勾全。</li>
<li>每张卡上的直流勾选须与①里已勾的 DC 一致（只勾了 DC1，则卡片里也只启用 DC1）。</li>
<li>功率%：入门保持 100；规程要求多功率点时再改。</li>
</ul>

<div class="callout ok">
<strong>示例一套汇总</strong>：单相或三相 230/50；只勾 DC1；等待 3 秒；启机 5 分钟；德威创或 WT 谐波模式；采集 10；先只跑谐波 1 次 @100%Pn。
</div>

<h2>④ 关机</h2>
<p>勾选关机步后追加运行。</p>

{footer_ops([
    "连接 AC/DC/分析仪。",
    "填启机交流直流与时序。",
    "选谐波分析仪模式并应用。",
    "数据采集 + 勾要做的谐波次 → 关机 → 追加。",
])}
""".strip()

PAGES["test-fixedpf.html"] = f"""
<h1>固定 PF=1 <span class="badge">已就绪</span></h1>
<p class="muted">菜单：Auto_Test → 固定 PF=1。先连设备，再按示例录入。</p>
<div class="callout ok">前置：AC/DC/WT（或规程要求的分析仪）已连接。</div>

<h2>本试验步骤一览</h2>
<ol>
<li>① AC/DC 电源</li>
<li>② 功率分析仪</li>
<li>③ 测量步骤（数据采集 + 多个功率点）</li>
<li>④ 关机设置</li>
</ol>

{ac_dc_block(wait="3", wait_unit="秒", startup="5", startup_unit="分钟")}

{analyzer_block('''
<p>选 <strong>WT3000</strong>（或台架实际型号）。录波：五个功率点可「一条线连续录」成单文件，或「分开录」每点一个文件。文件名写在本页文件名列表。</p>
''')}

<h2>③ 测量步骤 — 示例一套</h2>
<h3>数据采集</h3>
<div class="table-wrap"><table>
<thead><tr><th>界面项</th><th>示例</th></tr></thead>
<tbody>
<tr><td>数据采集</td><td><strong>10</strong>（单位按界面，常见分钟）</td></tr>
<tr><td>间隔/等待</td><td><strong>1</strong></td></tr>
<tr><td>录波方式</td><td>一条线连续录（正式）；调试可用分开录</td></tr>
</tbody></table></div>

<h3>功率点（界面默认）</h3>
<p>每个测量步骤勾选启用，直流通道跟随①的勾选；功率% 示例：</p>
<div class="table-wrap"><table>
<thead><tr><th>测量步骤</th><th>功率%</th><th>入门建议</th></tr></thead>
<tbody>
<tr><td>步骤1</td><td><strong>100</strong></td><td>必做</td></tr>
<tr><td>步骤2</td><td><strong>75</strong></td><td>正式做；冒烟可取消勾选</td></tr>
<tr><td>步骤3</td><td><strong>50</strong></td><td>正式做；冒烟可取消</td></tr>
<tr><td>步骤4</td><td><strong>30</strong></td><td>正式做；冒烟可取消</td></tr>
<tr><td>步骤5</td><td><strong>20</strong></td><td>正式做；冒烟可取消</td></tr>
</tbody></table></div>
<div class="callout">机侧功率因数按规程设为 PF=1；软件负责扫功率点并录波，不代替机侧设定。</div>

<div class="callout ok">
<strong>示例一套汇总</strong>：三相 230×3 + 50 Hz；只勾 DC1；等待 3 秒；启机 5 分钟；WT3000 连续录；五个功率点 100/75/50/30/20（冒烟可只留 100）。
</div>

<h2>④ 关机</h2>
<p>勾选关机步 → 测试追加 → 运行。</p>

{footer_ops([
    "连接设备。",
    "填 AC/DC/时序（230/50）。",
    "配置 WT 与录波。",
    "确认功率点与采集时长 → 关机 → 追加。",
])}
""".strip()

PAGES["test-dcinj.html"] = f"""
<h1>直流分量 <span class="badge">已就绪</span></h1>
<p class="muted">菜单：Auto_Test → 直流分量。先连设备，再按示例录入。</p>
<div class="callout ok">前置：AC/DC/分析仪就绪。本试验按多个有功功率档（%Pn）分别测量。</div>

<h2>本试验步骤一览</h2>
<ol>
<li>① AC/DC 电源</li>
<li>② 功率分析仪</li>
<li>③ 100%Pn</li>
<li>④ 66%Pn</li>
<li>⑤ 33%Pn</li>
<li>⑥ 可选功率点</li>
<li>⑦ 关机设置</li>
</ol>

{ac_dc_block(wait="3", wait_unit="秒", startup="5", startup_unit="分钟",
             ac_note="本试验界面交流电压默认可能是 220；台架若统一用 230，请改成 230（或现场额定）。下面示例按手册统一写 230。")}

{analyzer_block('''
<p>选与台架一致的 WT。每个功率档会录对应段；路径与文件名事先定好，避免覆盖。</p>
''')}

<h2>③～⑥ 功率档 — 示例一套</h2>
<div class="table-wrap"><table>
<thead><tr><th>步骤</th><th>功率%</th><th>采集相关（界面常见）</th><th>入门</th></tr></thead>
<tbody>
<tr><td>100%Pn</td><td><strong>100</strong></td><td>采集约 <strong>5</strong> 分钟量级；另有短等待约 <strong>1</strong></td><td>必做</td></tr>
<tr><td>66%Pn</td><td><strong>66</strong></td><td>同系列设置</td><td>正式做</td></tr>
<tr><td>33%Pn</td><td><strong>33</strong></td><td>同系列设置</td><td>正式做</td></tr>
<tr><td>可选功率点</td><td>如 <strong>20</strong></td><td>按规程勾选</td><td>冒烟可跳过</td></tr>
</tbody></table></div>
<p>每一档勾选该步，并保证直流功率% 与该档一致；只勾 DC1 时各档也只走 DC1。</p>

<div class="callout ok">
<strong>示例一套汇总</strong>：单相或三相 230/50；只勾 DC1；等待 3 秒；启机 5 分钟；先只跑 100%Pn 档冒烟，通过后再勾 66%/33%。
</div>

<h2>⑦ 关机</h2>
<p>勾选关机 → 追加 → 运行。</p>

{footer_ops([
    "连接设备。",
    "填 AC/DC/时序。",
    "配置分析仪。",
    "按档勾选 100%→66%→33%（及可选点）→ 关机 → 追加。",
])}
""".strip()

PAGES["test-reconnect.html"] = f"""
<h1>重连 <span class="badge">已就绪</span></h1>
<p class="muted">菜单：Auto_Test → 重连。先连设备，再按示例录入。</p>
<div class="callout ok">前置：AC/DC/分析仪就绪。本试验含多段「重连测试」工况（电压/频率/采集时间）。</div>

<h2>本试验步骤一览</h2>
<ol>
<li>① AC/DC 电源</li>
<li>② 功率分析仪</li>
<li>③～⑦ 重联测试 1～5</li>
<li>⑧ 关机设置</li>
</ol>

{ac_dc_block(wait="3", wait_unit="秒", startup="5", startup_unit="分钟")}

{analyzer_block('''
<p>选 WT3000（或台架型号）。保存路径单独建，如 reconnect_run；文件名按段区分便于事后对应。</p>
''')}

<h2>③～⑦ 重联测试 — 示例一套</h2>
<p>每一段通常包含：交流电压、频率、本段采集/等待时间。界面默认接近：</p>
<div class="table-wrap"><table>
<thead><tr><th>段</th><th>交流电压</th><th>频率</th><th>本段时间</th><th>入门</th></tr></thead>
<tbody>
<tr><td>重连 1</td><td><strong>230</strong> V</td><td><strong>50</strong> Hz</td><td><strong>2.5</strong> 秒</td><td>必做</td></tr>
<tr><td>重连 2</td><td>230 V</td><td>50 Hz</td><td>2.5 秒</td><td>正式做</td></tr>
<tr><td>重连 3</td><td>230 V</td><td>50 Hz</td><td>2.5 秒</td><td>正式做</td></tr>
<tr><td>重连 4</td><td>230 V</td><td>50 Hz</td><td>2.5 秒</td><td>正式做</td></tr>
<tr><td>重连 5</td><td>230 V</td><td>50 Hz</td><td>2.5 秒</td><td>正式做</td></tr>
</tbody></table></div>
<p class="muted">规程若要求某段改电压/频率（如欠压后恢复），按规程改该段数字；冒烟可只勾重连 1。</p>

<div class="callout ok">
<strong>示例一套汇总</strong>：启机用三相 230×3 + 50 Hz（或单相 230/50）；只勾 DC1；等待 3 秒；启机 5 分钟；五段重连先保持 230/50/2.5s，或只跑第 1 段冒烟。
</div>

<h2>⑧ 关机</h2>
<p>勾选关机 → 追加 → 运行。</p>

{footer_ops([
    "连接设备。",
    "填启机 AC/DC/时序。",
    "配置分析仪。",
    "逐段勾选重连 1～5（冒烟可只留 1）→ 关机 → 追加。",
])}
""".strip()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, html in PAGES.items():
        path = OUT / name
        path.write_text(html + "\n", encoding="utf-8")
        print("wrote", path.name, "chars", len(html))


if __name__ == "__main__":
    main()
