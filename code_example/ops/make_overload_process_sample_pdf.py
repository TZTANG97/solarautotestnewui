# -*- coding: utf-8 -*-
"""过载能力测试流程样板 PDF v2：设备管理（IP/SCPI）+ 试验步骤，紧凑排版."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SHOT = ROOT / "code_example" / "media" / "overload_flow_shots"
OUT = ROOT / "code_example" / "media" / "过载能力测试_软件操作流程样板.pdf"
DESKTOP = Path(r"C:\Users\13852\Desktop") / "过载能力测试_软件操作流程样板.pdf"
FN = "SimHei"
FONT = r"C:\Windows\Fonts\simhei.ttf"


def styles():
    return {
        "title": ParagraphStyle(
            "t", fontName=FN, fontSize=14, leading=20, alignment=TA_CENTER, spaceAfter=6
        ),
        "h1": ParagraphStyle(
            "h1",
            fontName=FN,
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#1d4ed8"),
            spaceBefore=6,
            spaceAfter=3,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName=FN,
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=4,
            spaceAfter=2,
        ),
        "b": ParagraphStyle("b", fontName=FN, fontSize=8.5, leading=12, spaceAfter=1),
        "n": ParagraphStyle(
            "n", fontName=FN, fontSize=8, leading=11, textColor=colors.HexColor("#64748b"), spaceAfter=2
        ),
        "cap": ParagraphStyle(
            "cap",
            fontName=FN,
            fontSize=7.5,
            leading=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#475569"),
            spaceBefore=1,
            spaceAfter=4,
        ),
        "c": ParagraphStyle("c", fontName=FN, fontSize=7.5, leading=10),
    }


def P(text, style):
    return Paragraph(str(text).replace("\n", "<br/>"), style)


def shot(name: str, max_w=16.8 * cm, max_h=6.2 * cm):
    path = SHOT / name
    if not path.exists():
        return P(f"[缺图 {name}]", styles()["n"])
    img = Image(str(path))
    scale = min(max_w / img.imageWidth, max_h / img.imageHeight, 1.0)
    img.drawWidth = img.imageWidth * scale
    img.drawHeight = img.imageHeight * scale
    return img


def bullets(items, st):
    return ListFlowable(
        [ListItem(P(x, st["b"]), leftIndent=4, value="-") for x in items],
        bulletType="bullet",
        start="•",
        leftIndent=10,
        bulletFontName=FN,
        bulletFontSize=8,
        spaceBefore=0,
        spaceAfter=2,
    )


def table(data, widths, header_bg="#dbeafe"):
    st = styles()
    rows = [[P(c, st["c"]) for c in r] for r in data]
    t = Table(rows, colWidths=widths)
    t.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#94a3b8")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return t


def hf(c, d):
    c.saveState()
    c.setFont(FN, 7.5)
    c.setFillColor(colors.grey)
    c.drawString(1.4 * cm, A4[1] - 0.85 * cm, "SolarAutoTest · 过载能力测试 · 流程样板 v2")
    c.drawRightString(A4[0] - 1.4 * cm, A4[1] - 0.85 * cm, "设备管理=各试验标准开头")
    c.drawCentredString(A4[0] / 2, 0.85 * cm, f"{d.page}")
    c.restoreState()


def block(title, tips, png, cap, st, h=6.0 * cm):
    return KeepTogether(
        [
            P(title, st["h2"]),
            bullets(tips, st),
            shot(png, max_h=h),
            P(cap, st["cap"]),
        ]
    )


def main() -> int:
    pdfmetrics.registerFont(TTFont(FN, FONT))
    st = styles()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    story = []

    # ── Cover / overview ──
    story.append(P("光伏并网自动化台架 — 试验操作流程样板", st["title"]))
    story.append(P("样板试验：过载能力测试（含设备管理标准开头）", st["title"]))
    story.append(
        P(
            "本册前半「设备管理」为每个试验通用开头；后半为过载专属步骤。"
            "确认版式后可复用前半到闪变/谐波/固定PF等。",
            st["n"],
        )
    )
    story.append(
        table(
            [
                ["项", "内容"],
                ["软件", "SolarAutoTest（主界面左侧设备页）"],
                ["标准开头", "交流源 → 直流源 → 功率分析仪(WT/德威创) → 示波器DL850(如需)"],
                ["本试验", "过载能力测试 · Dialog 四步 ①AC/DC时序 ②仪表 ③采集 ④关机"],
            ],
            [2.8 * cm, 14.0 * cm],
        )
    )
    story.append(Spacer(1, 0.15 * cm))
    story.append(P("总流程（所有试验通用骨架）", st["h1"]))
    story.append(
        bullets(
            [
                "启动软件 →【先】设备管理连接/配置电源与仪表 →【再】选试验并打开项目设置 → 追加 → 开跑",
                "未连接成功不要「测试追加」。试验对话框里的电源参数是下发命令，前提是设备页已连上。",
            ],
            st,
        )
    )

    # ── IP / SCPI guide ──
    story.append(P("一、什么时候用「串口/SCPI」，什么时候用「IP」", st["h1"]))
    story.append(
        table(
            [
                ["品牌/页面", "通信怎么选", "怎么填", "协议说明"],
                [
                    "交流 Chroma",
                    "顶栏选 Chroma；通信选「串口」",
                    "下拉选 VISA 资源：ASRL/USB/TCPIP0::…::INSTR",
                    "SCPI（VISA）",
                ],
                [
                    "交流 Chroma",
                    "顶栏选 Chroma；通信选「IP」",
                    "填设备 IP；端口可留空（自动探测）",
                    "TCP/SCPI（网口）",
                ],
                [
                    "交流 爱科(Itech)",
                    "顶栏切到「爱科(Itech)」",
                    "必须填 IP + 端口（常见 502）",
                    "Modbus TCP（不是串口 SCPI）",
                ],
                [
                    "直流 Chroma",
                    "顶栏 Chroma；串口或 IP",
                    "串口=VISA 资源；IP=填地址",
                    "多为 SCPI",
                ],
                [
                    "直流 蓝电",
                    "顶栏切「蓝电(Bluesight)」",
                    "IP+端口 → 连接 → 选工作模式并「应用模式」→ 填 SAS/原始负载参数并发送 → 开输出",
                    "Modbus TCP（不是串口 SCPI）",
                ],
                [
                    "示波器 DL850",
                    "设备页选资源后连接",
                    "USB/LAN 的 VISA 资源名",
                    "SCPI",
                ],
                [
                    "德威创 DEWETRON",
                    "设备页填 IP/端口",
                    "连接后应用配置 / 测试生效",
                    "以太网（非电源 SCPI）",
                ],
            ],
            [2.8 * cm, 4.2 * cm, 5.2 * cm, 3.6 * cm],
            header_bg="#fef3c7",
        )
    )
    story.append(
        P(
            "口诀：爱科交流/蓝电直流 → 基本只用 IP；Chroma → 看现场是串口还是网口，选「串口」或「IP」；"
            "下拉框里的 TCPIP0::x.x.x.x::INSTR 属于 SCPI 资源写法，与「通信=IP」输入框是两条路径。",
            st["n"],
        )
    )

    # ── AC shots compact ──
    story.append(PageBreak())
    story.append(P("二、设备管理 · 交流电源（标准开头①）", st["h1"]))
    story.append(
        block(
            "2.1 Chroma · 串口/SCPI",
            [
                "主界面左侧进「交流电源」→ 顶栏选 Chroma",
                "通信选「串口」→ 在资源下拉选 ASRL/USB/TCPIP0::…::INSTR → 连接设备",
                "设相位/电压/频率 → 需要时打开输出",
            ],
            "D10_ac_chroma_serial.png",
            "图 A1  Chroma 交流 · 串口/SCPI",
            st,
            h=5.8 * cm,
        )
    )
    story.append(
        block(
            "2.2 Chroma · IP/SCPI（网口）",
            [
                "同一页通信改选「IP」→ 资源下拉隐藏，出现 IP/端口框",
                "填电源 IP；端口不确定可留空 → 连接设备",
            ],
            "D11_ac_chroma_ip.png",
            "图 A2  Chroma 交流 · IP",
            st,
            h=5.8 * cm,
        )
    )

    story.append(PageBreak())
    story.append(
        block(
            "2.3 爱科(Itech) · 只用 IP/Modbus",
            [
                "顶栏切到「爱科(Itech)」（不要停在 Chroma 页填串口）",
                "填 IP + 端口（默认 502）→ 连接 → 设电压频率 → 开输出",
            ],
            "D12_ac_itech_ip.png",
            "图 A3  爱科交流 · IP/Modbus",
            st,
            h=6.2 * cm,
        )
    )

    story.append(P("三、设备管理 · 直流电源（标准开头②）", st["h1"]))
    story.append(
        block(
            "3.1 Chroma 直流",
            ["顶栏 Chroma → 串口选 VISA 资源或改 IP → 连接 → 填 Vmp/Voc/Imp/Isc → 开输出"],
            "D13_dc_chroma.png",
            "图 B1  直流 Chroma",
            st,
            h=5.6 * cm,
        )
    )
    story.append(
        block(
            "3.2 蓝电直流（完整步骤，不只填 IP）",
            [
                "顶栏切「蓝电(Bluesight)」→ 填 IP+端口(常见502) → 连接",
                "工作模式三选一：原始负载 / SAS / 电池模拟器 → 必须点「应用模式」",
                "SAS（台架光伏常用）：填 Pmpp_stc(kW)、Umpp_stc(V)、填充因子 →「发送参数到设备（曲线）」",
                "原始负载：选恒压/恒流/恒功率/恒阻 → 填对应电压/电流/功率/电阻 →「发送参数」",
                "最后「打开输出」。不要与 Chroma 页的 Vmp/Imp 串口流程混用",
            ],
            "D14_dc_bluesight_sas.png",
            "图 B2  蓝电 · SAS 模式（连接+模式+STC曲线参数）",
            st,
            h=6.2 * cm,
        )
    )
    story.append(
        block(
            "3.3 蓝电 · 原始负载模式（对照）",
            ["模式选「原始负载」后，参数区变为恒压/恒流/恒功率/恒阻及对应填写项"],
            "D14b_dc_bluesight_orig.png",
            "图 B3  蓝电 · 原始负载模式",
            st,
            h=5.6 * cm,
        )
    )

    story.append(PageBreak())
    story.append(P("四、设备管理 · 示波器 / 功率分析仪（标准开头③④）", st["h1"]))
    story.append(
        block(
            "4.1 示波器 DL850",
            [
                "左侧进 DL850 → 选 VISA/SCPI 资源 → 连接",
                "用 START/STOP 试采；每个用到示波器的试验开跑前确认已连接",
            ],
            "D15_dl850.png",
            "图 C  DL850",
            st,
            h=5.5 * cm,
        )
    )
    story.append(
        block(
            "4.2 德威创 DEWETRON（德威创台架）",
            [
                "填 IP → 连接 → 配接线/刷新率 →「应用配置」→ 需要时构造测试页",
                "开跑前必须「测试生效」",
            ],
            "D03_device_dewetron.png",
            "图 D  DEWETRON",
            st,
            h=5.8 * cm,
        )
    )
    story.append(
        block(
            "4.3 WT3000E（横河等）",
            ["连接 WT 接口；与试验对话框步骤② WT 配置保持一致"],
            "D05_device_wt3000e.png",
            "图 E  WT3000E",
            st,
            h=5.2 * cm,
        )
    )

    story.append(P("设备就绪检查（进入任一试验前）", st["h2"]))
    story.append(
        table(
            [
                ["#", "检查项", "□"],
                ["1", "交流源：品牌页正确；串口资源或 IP 已连成功", ""],
                ["2", "直流源：Chroma/蓝电/爱科选对；参数已下发", ""],
                ["3", "WT 或德威创已连；德威创已应用配置/测试生效", ""],
                ["4", "示波器（本试验需要时）已连接可采", ""],
                ["5", "主界面日志无连接失败", ""],
            ],
            [1.0 * cm, 14.5 * cm, 1.3 * cm],
            header_bg="#dcfce7",
        )
    )

    # ── Overload specific ──
    story.append(PageBreak())
    story.append(P("五、过载能力测试（设备就绪之后）", st["h1"]))
    story.append(
        bullets(
            [
                "主界面选「过载能力测试」→ 打开项目设置",
                "步骤①～④填试验参数（此处 AC/DC 是命令参数，不是再次替代设备连接）",
                "保存设定（可选）→ 测试追加 → 主界面执行",
            ],
            st,
        )
    )
    story.append(shot("00_dialog_overview.png", max_h=5.8 * cm))
    story.append(P("图 1  过载对话框总览", st["cap"]))

    story.append(
        block(
            "步骤① AC/DC + 时序",
            ["勾选通道与功率%；等待/启机时间；关机约定：先 DC 后 AC"],
            "01_step_ac_dc_timing.png",
            "图 2  步骤①",
            st,
            h=5.5 * cm,
        )
    )
    story.append(
        block(
            "步骤② 功率分析仪（须与设备管理仪表一致）",
            ["WT/德威创模式；文件名列表；德威创刷新字段并测试生效"],
            "02_step_analyzer.png",
            "图 3  步骤②",
            st,
            h=5.5 * cm,
        )
    )

    story.append(PageBreak())
    story.append(
        block(
            "步骤③ 过载采集",
            ["采集时长（如 90 分钟）；连续录/分开录"],
            "03_step_overload_params.png",
            "图 4  步骤③",
            st,
            h=5.8 * cm,
        )
    )
    story.append(
        block(
            "步骤④ 关机",
            ["确认关机顺序 → 测试追加"],
            "04_step_shutdown.png",
            "图 5  步骤④",
            st,
            h=5.5 * cm,
        )
    )

    story.append(P("开跑前总检", st["h2"]))
    story.append(
        table(
            [
                ["#", "检查项", "□"],
                ["0", "设备管理标准开头已完成（电源+仪表+示波器）", ""],
                ["1", "过载四步参数已填；录波名/时长正确", ""],
                ["2", "已测试追加；日志无报错", ""],
                ["3", "结束后录波可导入分析软件", ""],
            ],
            [1.0 * cm, 14.5 * cm, 1.3 * cm],
            header_bg="#dbeafe",
        )
    )
    story.append(Spacer(1, 0.2 * cm))
    story.append(
        P(
            "请确认：IP/SCPI 表是否好懂、截图是否够全、空白是否可接受。"
            "确认后把「第一～四章设备管理」固化为各试验 PDF 共用开头。",
            st["n"],
        )
    )

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=1.3 * cm,
        rightMargin=1.3 * cm,
        topMargin=1.3 * cm,
        bottomMargin=1.2 * cm,
        title="过载能力测试软件操作流程样板v2",
        author="SolarAutoTest",
    )
    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    try:
        DESKTOP.write_bytes(OUT.read_bytes())
        print(f"desktop -> {DESKTOP}")
    except Exception as exc:
        print(f"desktop skip: {exc}")
    print(f"OUT -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
