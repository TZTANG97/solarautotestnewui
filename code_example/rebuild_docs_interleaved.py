# -*- coding: utf-8 -*-
"""Rebuild autotest-docs test pages: each step = screenshot then text under it."""
from __future__ import annotations

from pathlib import Path

OUT = Path(r"E:\utoo\utoo-pydjango\utoo-web-front\public\autotest-docs\pages")
MEDIA = Path(r"E:\utoo\utoo-pydjango\utoo-web-front\public\autotest-docs\media")


def fig(slug: str, n: int, caption: str) -> str:
    """n: 0=overview, 1..=step. Prefer NN_step; fall back to 00_overview for n=0."""
    if n == 0:
        name = f"T_{slug}_00_overview.png"
        if not (MEDIA / name).exists():
            name = f"T_{slug}_01_step.png"
    else:
        name = f"T_{slug}_{n:02d}_step.png"
        if not (MEDIA / name).exists():
            return f'<p class="muted">（步骤截图待补：{name}）</p>'
    return (
        f'<figure>\n  <img src="media/{name}" alt="{caption}" />\n'
        f"  <figcaption>{caption}</figcaption>\n</figure>"
    )


def ac_body(wait: str, wait_u: str, start: str, start_u: str, note: str = "") -> str:
    n = f"<p class=\"muted\">{note}</p>" if note else ""
    return f"""
{n}
<p>本步填交流、直流和时序。通章说明见左侧「试验条件怎么填」。</p>
<h3>交流 · 单相（示例）</h3>
<div class="table-wrap"><table><thead><tr><th>项</th><th>填写</th></tr></thead><tbody>
<tr><td>交流电源</td><td>开启</td></tr>
<tr><td>相位</td><td><strong>单相</strong></td></tr>
<tr><td>交流电压1</td><td><strong>230</strong> V</td></tr>
<tr><td>频率</td><td><strong>50</strong> Hz</td></tr>
</tbody></table></div>
<h3>交流 · 三相（示例）</h3>
<div class="table-wrap"><table><thead><tr><th>项</th><th>填写</th></tr></thead><tbody>
<tr><td>相位</td><td><strong>三相</strong></td></tr>
<tr><td>电压1/2/3</td><td><strong>230 / 230 / 230</strong> V</td></tr>
<tr><td>频率</td><td><strong>50</strong> Hz</td></tr>
</tbody></table></div>
<h3>直流 · 勾几个</h3>
<ul>
<li>入门只勾 <strong>直流电源1</strong>，开关「开启」；IV 示例 Vmp220 Imp10 Voc220 Isc10 功率100%。</li>
<li>接几路勾几路；空接不要勾。</li>
</ul>
<h3>等待时间 / 启机时间</h3>
<div class="table-wrap"><table><thead><tr><th>名称</th><th>含义</th><th>本试验示例</th></tr></thead><tbody>
<tr><td>等待时间</td><td>交流开出后先站稳</td><td><strong>{wait}</strong> {wait_u}</td></tr>
<tr><td>启机时间</td><td>交直流开完后再等并网</td><td><strong>{start}</strong> {start_u}</td></tr>
</tbody></table></div>
""".strip()


def ana_body(extra: str = "") -> str:
    """Legacy short body; prefer analyzer_step()."""
    return analyzer_text(extra)


def analyzer_text(extra: str = "") -> str:
    return f"""
<p>本步顶部有两档（多数试验一样）：</p>
<ul>
<li><strong>功率分析仪 (WT)</strong>：台架用横河 WT 时选这项，再选 WT3000/WT1800 等型号并配置。</li>
<li><strong>DEWETRON</strong>（德威创）：台架用德威创时<strong>必须点选这一项</strong>，下方会换成德威创配置页（不要只停在 WT 页）。</li>
</ul>
<div class="callout">选哪边，必须与「设备管理」里已经连上的仪器一致。连的是德威创却留在 WT，试验录不到德威创数据。</div>
<h3>选 WT 时怎么配</h3>
<ol>
<li>点选「功率分析仪 (WT)」。</li>
<li>再选具体型号（如 WT3000）。</li>
<li>填保存路径、文件名；选「一条线连续录 / 分开录」。</li>
</ol>
<h3>选德威创（DEWETRON）时怎么配</h3>
<ol>
<li>设备管理里德威创已 IP 连接，且接线/通道已保存（见左侧德威创连接页）。</li>
<li>本步点选 <strong>DEWETRON</strong>。</li>
<li>点 <strong>刷新</strong> 电力组/导出字段。</li>
<li>勾选本试验需要导出的量。</li>
<li>点 <strong>测试生效 / 应用</strong>（名称以界面按钮为准）。</li>
<li>录波方式（连续录/分开录）按试验需要选。</li>
</ol>
{extra}
""".strip()


def shutdown_body() -> str:
    return "<p>勾选关机步。习惯：先关直流，稍等，再关交流。填完后点<strong>测试追加</strong>再运行；改参数须重新追加。</p>"


def step_block(slug: str, step_n: int, title: str, body: str) -> str:
    return f"""
<h2>{title}</h2>
{fig(slug, step_n, title)}
{body}
""".strip()


def analyzer_step(slug: str, title: str = "② 功率分析仪", extra: str = "") -> str:
    """WT screenshot + DEWETRON screenshot, each with guidance underneath the pair."""
    dew_name = f"T_{slug}_02b_dewetron.png"
    dew_fig = ""
    if (MEDIA / dew_name).exists():
        dew_fig = (
            f'<figure>\n  <img src="media/{dew_name}" alt="{title} · 已选 DEWETRON" />\n'
            f"  <figcaption>{title} · 点选 DEWETRON（德威创）后的界面</figcaption>\n</figure>"
        )
    else:
        dew_fig = '<p class="muted">（德威创模式截图待补：切换「DEWETRON」后应出现德威创配置页）</p>'
    return f"""
<h2>{title}</h2>
{fig(slug, 2, f"{title} · 功率分析仪 (WT)")}
{dew_fig}
{analyzer_text(extra)}
""".strip()


def page(
    title: str,
    menu: str,
    slug: str,
    steps: list[tuple[int, str, str]],
    summary: str,
) -> str:
    """steps: (shot_index, heading, body). For ② analyzer heading, body = extra tips only
    (WT/DEWETRON selection text is injected automatically)."""
    overview = "\n".join(f"<li>{h}</li>" for _, h, _ in steps)
    blocks = []
    for n, h, b in steps:
        is_ana = h.startswith("②") or ("功率分析仪" in h and "①" not in h)
        if is_ana:
            blocks.append(analyzer_step(slug, h, b.strip()))
        else:
            blocks.append(step_block(slug, n, h, b))
    return f"""
<h1>{title} <span class="badge">已就绪</span></h1>
<p class="muted">菜单：Auto_Test → {menu}。先完成设备连接，再按下列「截图 + 说明」逐步填写。</p>
<div class="callout ok">前置：交流/直流/分析仪已连接。功率仪步骤请按台架选择 <strong>功率分析仪 (WT)</strong> 或 <strong>DEWETRON（德威创）</strong>。通用填法见「试验条件怎么填」。</div>

<h2>步骤一览</h2>
<ol>
{overview}
</ol>

{"\n\n".join(blocks)}

<div class="callout ok"><strong>示例一套汇总</strong>：{summary}</div>
""".strip() + "\n"


# ---------- build all pages ----------

def build_all() -> dict[str, str]:
    P: dict[str, str] = {}

    def S(wait="3", wait_u="秒", start="5", start_u="分钟", note="", ana_extra=""):
        return ac_body(wait, wait_u, start, start_u, note), ana_body(ana_extra)

    # overload: 4 steps
    ac, an = S(wait="3", start="5", start_u="分钟")
    P["test-overload.html"] = page(
        "过载能力测试", "过载能力", "overload",
        [
            (1, "① AC/DC 电源 + 时序", ac),
            (2, "② 功率分析仪", "<p>正式过载常用「一条线连续录」；文件名可点填充推荐。</p>"),
            (3, "③ 过载测试（采集 / 录波）", """
<div class="table-wrap"><table><thead><tr><th>项</th><th>示例</th></tr></thead><tbody>
<tr><td>数据采集时长</td><td><strong>90</strong> 分钟（冒烟可改 2～5 分钟）</td></tr>
<tr><td>录波方式</td><td>一条线连续录</td></tr>
</tbody></table></div>
""".strip()),
            (4, "④ 关机设置", shutdown_body()),
        ],
        "单相或三相 230/50；只勾 DC1；等待 3 秒；启机 5 分钟；WT 连续录；采集 90 分钟（冒烟可缩短）。",
    )

    ac, an = S(wait="5", start="5", start_u="分钟", note="电压框若为空请填 230/50。",
               ana_extra="<p>顶部可选 <strong>WT3000闪变</strong> / <strong>德威创模式</strong>。</p>")
    P["test-flicker.html"] = page(
        "电压闪变", "电压闪变", "flicker",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 闪变测量设置", an + """
<div class="table-wrap"><table><thead><tr><th>项</th><th>示例</th></tr></thead><tbody>
<tr><td>WT 相位</td><td>与样机一致（单相/三相）</td></tr>
<tr><td>每组闪变</td><td><strong>3</strong> 次</td></tr>
<tr><td>首次闪变间隔</td><td><strong>4</strong> 分钟</td></tr>
</tbody></table></div>
""".strip()),
            (3, "③ DC 开关循环", """
<p>按界面填循环时长、间隔、次数。默认循环次数常见 <strong>12</strong>；冒烟可改 2～3。</p>
<div class="callout">注意总时长上限（约 600 秒），超限则减小间隔或次数。</div>
""".strip()),
            (4, "④ 判定结果", "<p>按所选 WT/德威创模式勾选判定步，正式试验核对规程限值相关项。</p>"),
            (5, "⑤ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待 5 秒；启机 5 分钟；每组闪变 3 次；循环次数冒烟可改小。",
    )

    ac, an = S(ana_extra="<p>可选 <strong>WT3000谐波</strong> / <strong>德威创</strong>；德威创刷新率常用 SYNC to HARMONIC。</p>")
    P["test-harmonic.html"] = page(
        "谐波电流", "谐波电流", "harmonic",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ 谐波设置", """
<p><strong>数据采集</strong>：时长常见默认约 10；间隔约 1（单位看界面）。</p>
<p><strong>谐波 1～12 次卡片</strong>：入门只勾谐波 1 次 @100%；正式再按规程勾全。卡片上直流勾选须与①一致。</p>
""".strip()),
            (4, "④ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待 3 秒；启机 5 分钟；先只跑谐波 1 次。",
    )

    ac, an = S()
    P["test-fixedpf.html"] = page(
        "固定 PF=1", "固定 PF=1", "fixedpf",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", "<p>五个功率点可连续录成单文件或分开录。</p>"),
            (3, "③ 测量步骤", """
<p>数据采集约 <strong>10</strong>；功率点默认：<strong>100 / 75 / 50 / 30 / 20</strong>%。冒烟可只留 100%。机侧 PF=1 事先设好。</p>
""".strip()),
            (4, "④ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待 3 秒；启机 5 分钟；功率点 100→20。",
    )

    ac, an = S(note="界面电压默认可能是 220；台架统一用 230 时请改成 230。")
    P["test-dcinj.html"] = page(
        "直流分量", "直流分量", "dcinj",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ 100%Pn", "<p>功率% = <strong>100</strong>；采集约 5 分钟量级。入门必做。</p>"),
            (4, "④ 66%Pn", "<p>功率% = <strong>66</strong>。正式试验勾选。</p>"),
            (5, "⑤ 33%Pn", "<p>功率% = <strong>33</strong>。正式试验勾选。</p>"),
            (6, "⑥ 可选功率点", "<p>如 20%；按规程勾选，冒烟可跳过。</p>"),
            (7, "⑦ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待 3 秒；启机 5 分钟；先跑 100%Pn。",
    )

    ac, an = S()
    P["test-reconnect.html"] = page(
        "重连", "重连", "reconnect",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ 重连测试1", "<p>电压 <strong>230</strong>、频率 <strong>50</strong>、本段时间 <strong>2.5</strong> 秒。入门必做。</p>"),
            (4, "④ 重连测试2", "<p>默认同 230 / 50 / 2.5s；按规程可改。</p>"),
            (5, "⑤ 重连测试3", "<p>默认同 230 / 50 / 2.5s。</p>"),
            (6, "⑥ 重连测试4", "<p>默认同 230 / 50 / 2.5s。</p>"),
            (7, "⑦ 重连测试5", "<p>默认同 230 / 50 / 2.5s。</p>"),
            (8, "⑧ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待 3 秒；启机 5 分钟；冒烟可只勾重连1。",
    )

    ac, an = S()
    P["test-ovuf.html"] = page(
        "过欠压 / 过欠频", "过欠压_过欠频", "ovuf",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ 过欠压1", "<p>填本段电压/频率变动区间。冒烟可只做本段。</p>"),
            (4, "④ 过欠压2", "<p>按规程填变动区间。</p>"),
            (5, "⑤ 过欠压3", "<p>按规程填变动区间。</p>"),
            (6, "⑥ 过欠压4", "<p>按规程填变动区间。</p>"),
            (7, "⑦ 过欠频", "<p>填频率变动区间（相对 50 Hz 基准）。</p>"),
            (8, "⑧ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待 3 秒；启机 5 分钟；先只勾过欠压1 冒烟。",
    )

    ac, an = S(wait="5", start="5", start_u="分钟")
    P["test-static-cos.html"] = page(
        "静态 Cos(φ)", "静态Cos(φ)", "static-cos",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ cosPhi 设置", """
<div class="table-wrap"><table><thead><tr><th>项</th><th>示例</th></tr></thead><tbody>
<tr><td>功率档(%)</td><td>如 <strong>100,90,80,70</strong></td></tr>
<tr><td>每点驻留</td><td><strong>30</strong> 秒</td></tr>
<tr><td>cosφ</td><td>按规程勾选；机侧曲线事先设好</td></tr>
</tbody></table></div>
""".strip()),
            (4, "④ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待/启机 5 秒与 5 分钟；驻留 30 秒；连续录。",
    )

    ac, an = S(wait="5", start="5", start_u="分钟")
    P["test-static-qu.html"] = page(
        "静态 QU", "静态QU", "static-qu",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ 电压阶梯", "<p>Un=<strong>230</strong>；电压 list 按规程；连续录 QU_curve。</p>"),
            (4, "④ QU测试2", "<p>按规程勾选。</p>"),
            (5, "⑤ QU测试3", "<p>按规程勾选。</p>"),
            (6, "⑥ QU测试4", "<p>按规程勾选。</p>"),
            (7, "⑦ 判定结果", "<p>核对判定相关项。</p>"),
            (8, "⑧ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待/启机 5 秒与 5 分钟；Un=230；电压 list 按规程。",
    )

    ac, an = S(wait="5", start="5", start_u="分钟")
    P["test-active-p.html"] = page(
        "有功调度", "有功调度", "active-p",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ P 调度", """
<div class="table-wrap"><table><thead><tr><th>项</th><th>示例</th></tr></thead><tbody>
<tr><td>P指令(%Pn)</td><td><strong>100,80,60,40,20,0</strong></td></tr>
<tr><td>DC功率头寸(%)</td><td><strong>100</strong></td></tr>
<tr><td>每点驻留</td><td><strong>1</strong> 分钟</td></tr>
</tbody></table></div>
""".strip()),
            (4, "④ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待/启机 5 秒与 5 分钟；P list 如上。",
    )

    ac, an = S()
    P["test-overfreq.html"] = page(
        "过频降载", "过频降载", "overfreq",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ 过频设置", """
<div class="table-wrap"><table><thead><tr><th>项</th><th>示例</th></tr></thead><tbody>
<tr><td>台阶电压</td><td><strong>230</strong> V</td></tr>
<tr><td>频率Hz(list)</td><td><strong>50,50.25,50.7,51.15,50.7,50.25,50</strong></td></tr>
<tr><td>每点驻留</td><td><strong>60</strong> 秒</td></tr>
</tbody></table></div>
""".strip()),
            (4, "④ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待 3 秒；启机 5 分钟；用界面默认过频 list。",
    )

    ac, an = S()
    P["test-underfreq.html"] = page(
        "欠频升载", "欠频升载", "underfreq",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ 欠频设置", """
<div class="table-wrap"><table><thead><tr><th>项</th><th>示例</th></tr></thead><tbody>
<tr><td>台阶电压</td><td><strong>230</strong> V</td></tr>
<tr><td>频率Hz(list)</td><td><strong>50,49.75,49.5,49.25,49.0,49.25,49.5,49.75,50</strong></td></tr>
<tr><td>每点驻留</td><td><strong>60</strong> 秒</td></tr>
</tbody></table></div>
""".strip()),
            (4, "④ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待 3 秒；启机 5 分钟；用界面默认欠频 list。",
    )

    for fn, title, menu, slug, mid_title, mid_body in [
        ("test-fixed-q.html", "固定无功 Q", "固定Q", "fixed-q", "③ Q 设定",
         "<p>按规程勾选 Q 点；驻留约 1 分钟量级。机侧无功事先投入。冒烟少勾几点。</p>"),
        ("test-qin.html", "无功注入", "无功注入", "qin", "③ Q 设定",
         "<p>勾选注入工况与驻留；机侧无功模式事先设好。</p>"),
        ("test-qacc.html", "无功精度", "无功精度", "qacc", "③ Q 设定",
         "<p>按精度规程勾目标 Q 点；软件主要录响应。</p>"),
        ("test-qcap.html", "无功能力", "无功能力", "qcap", "③ 能力工况",
         "<p>勾选能力工况组合；机侧处相应无功能力模式。</p>"),
    ]:
        ac, an = S(wait="5", start="5", start_u="分钟")
        P[fn] = page(title, menu, slug, [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, mid_title, mid_body),
            (4, "④ 关机设置", shutdown_body()),
        ], "230/50；DC1；等待/启机 5 秒与 5 分钟；少点冒烟。")

    ac, an = S(wait="5", start="5", start_u="分钟")
    P["test-dyn-cos.html"] = page(
        "动态 Cos(φ)", "动态Cos(φ)", "dyn-cos",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ 功率阶梯", "<p>填功率阶梯 list；驻留常见约 5 分钟量级（冒烟可缩短）。机侧动态曲线事先设好；连续录。</p>"),
            (4, "④ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待/启机 5 秒与 5 分钟；功率阶梯按规程。",
    )

    ac, an = S(wait="5", start="5", start_u="分钟")
    P["test-dyn-qu.html"] = page(
        "动态 QU", "动态QU", "dyn-qu",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ 电压阶梯", "<p>填动态 Q(U) 电压 list 与驻留；连续录。机侧动态 QU 事先设好。</p>"),
            (4, "④ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待/启机 5 秒与 5 分钟；电压 list 按规程。",
    )

    ac, an = S(wait="5", start="5", start_u="分钟")
    P["test-pu.html"] = page(
        "Test_PU", "Test_PU", "pu",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪 + PU", ""),
            (3, "③ PU 测试", "<p>填电压 list / PU 相关设定；基准常用 230 V；连续录 PU_curve。</p>"),
            (4, "④ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待/启机 5 秒与 5 分钟；电压 list 按规程。",
    )

    ac, an = S()
    P["test-rocof.html"] = page(
        "RoCoF", "RoCoF", "rocof",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ ROCOF 设置", "<p>按规程填频率变化率相关台阶/list（勿与巴西频率适应性混用）。</p>"),
            (4, "④ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待 3 秒；启机 5 分钟；少段冒烟。",
    )

    ac, an = S()
    P["test-freq-adapt.html"] = page(
        "频率适应性", "频率适应性", "freq-adapt",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ 频率适应性", "<p>按规程勾选适应性相关设定。</p>"),
            (4, "④ 频率扫描", "<p>填频率扫描 list；须连续录，保证扫频与录波同时。冒烟可缩短点数。</p>"),
            (5, "⑤ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待 3 秒；启机 5 分钟；扫描点数先缩短。",
    )

    ac, an = S()
    P["test-volt-adapt.html"] = page(
        "电压适应性", "电压适应性", "volt-adapt",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ 电压适应性", "<p>按规程勾选适应性设定。</p>"),
            (4, "④ 电压扫描", "<p>填电压 list；基准常用 230 V；连续录。冒烟可减少点数。</p>"),
            (5, "⑤ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待 3 秒；启机 5 分钟；扫描点数先缩短。",
    )

    ac, an = S()
    P["test-rapid-volt.html"] = page(
        "快速电压变化", "快速电压变化", "rapid-volt",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ 快速电压变化", "<p>填快速电压台阶/序列与驻留；少台阶冒烟。</p>"),
            (4, "④ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待 3 秒；启机 5 分钟；少台阶冒烟。",
    )

    ac, an = S()
    P["test-volt10min.html"] = page(
        "10min 过压保护", "10min过压保护", "volt10min",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ 过压保护", "<p>保护相关时长常见约 <strong>10</strong> 分钟量级（以界面为准）。</p>"),
            (4, "④ 保护后恢复", "<p>按规程填恢复电压/等待。</p>"),
            (5, "⑤ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待 3 秒；启机 5 分钟；保护时长按规程。",
    )

    ac, an = S()
    P["test-immun.html"] = page(
        "过欠频免疫", "过欠频免疫", "immun",
        [
            (1, "① AC/DC 电源", ac),
            (2, "② 功率分析仪", ""),
            (3, "③ 频率扫描", "<p>可勾「更新率」（常见约 200 ms）；频率扫描 list 按规程；连续录。冒烟缩短扫描段。</p>"),
            (4, "④ 关机设置", shutdown_body()),
        ],
        "230/50；DC1；等待 3 秒；启机 5 分钟；扫描段先缩短。",
    )

    ac, an = S()
    P["test-static-mppt.html"] = page(
        "静态 MPPT", "静态MPPT", "static-mppt",
        [
            (1, "① AC/DC 电源", ac + "<p>国产台架常用蓝电：设备管理先连 IP，SAS 模式与参数已下发。</p>"),
            (2, "② 功率分析仪", ""),
            (3, "③ 测试功率段", """
<div class="table-wrap"><table><thead><tr><th>项</th><th>示例</th></tr></thead><tbody>
<tr><td>总时长</td><td>约 <strong>0 时 30 分</strong></td></tr>
<tr><td>单次/每段</td><td>约 <strong>0 时 5 分</strong></td></tr>
<tr><td>功率段</td><td>按界面勾选；冒烟少勾</td></tr>
</tbody></table></div>
""".strip()),
            (4, "④ MPPT 设置", "<p>IV 为各点曲线；功率段% 会缩放 Imp/Isc。以现场蓝电/组件为准。</p>"),
            (5, "⑤ 关机设置", shutdown_body()),
        ],
        "230/50；DC1+蓝电 SAS；总 30 分/单次 5 分；少功率段冒烟。",
    )

    return P


def main() -> None:
    pages = build_all()
    OUT.mkdir(parents=True, exist_ok=True)
    for name, html in pages.items():
        (OUT / name).write_text(html, encoding="utf-8")
        print("wrote", name)
    print("DONE", len(pages))


if __name__ == "__main__":
    main()
