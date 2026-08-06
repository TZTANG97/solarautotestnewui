# -*- coding: utf-8 -*-
"""
小红书评论采集数据分类工具

按笔记主题、IP归属、是否与求职相关等维度标注，并导出多 Sheet Excel。
用法:
  python classify_comments.py                  # 弹窗选文件
  python classify_comments.py 采集数据.xlsx    # 指定文件
  或把 Excel 拖到「运行分类.bat」上
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def ensure_deps() -> None:
    """缺失依赖时自动 pip 安装。"""
    missing = []
    for pkg, mod in (("pandas", "pandas"), ("openpyxl", "openpyxl")):
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    if not missing:
        return
    import subprocess

    print(f"[依赖] 正在安装: {', '.join(missing)} ...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", *missing, "-q"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    print("[依赖] 安装完成")


def pick_file() -> Path | None:
    """无参数时弹出文件选择框。"""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(
            title="选择采集数据 Excel",
            filetypes=[("Excel 文件", "*.xlsx *.xls"), ("所有文件", "*.*")],
        )
        root.destroy()
        return Path(path) if path else None
    except Exception as e:
        print(f"[错误] 无法打开文件选择框: {e}")
        return None


def classify_note(title) -> str:
    import pandas as pd

    if pd.isna(title) or str(title).strip() == "":
        return "无标题或其他讨论"
    t = str(title)
    if "司法文书" in t or "造谣" in t:
        return "维权司法文书(赛格案)"
    if "威海" in t:
        return "旅游攻略(威海)"
    if "济州岛" in t or "黑礁石" in t:
        return "旅拍身材展示"
    if "拳头" in t or "静音" in t or "救回" in t:
        return "正能量见义勇为"
    if "劳务费" in t or "评标" in t:
        return "劳务费评标咨询"
    if any(k in t for k in ("兼职", "招人", "临时工", "便利店", "招聘")):
        return "招聘兼职"
    if any(k in t for k in ("租", "转租", "求租", "出租", "公寓", "一室", "两居")):
        return "租房转租"
    return "其他"


JOB_SEEK_KW = ("缺人", "招人", "招聘", "兼职", "找工作", "求职", "面试", "应聘", "招工")
LABOR_RIGHTS_KW = ("劳动仲裁", "劳动局", "劳动关系", "工牌", "工伤", "削掉", "临时工")
FEE_KW = ("劳务费", "评标")
JOB_KEYWORDS = JOB_SEEK_KW + LABOR_RIGHTS_KW + FEE_KW + ("打工", "工资", "用工", "岗位", "简历")

REGION_MAP = {
    "北京": "华北",
    "天津": "华北",
    "河北": "华北",
    "山西": "华北",
    "内蒙古": "华北",
    "辽宁": "东北",
    "吉林": "东北",
    "黑龙江": "东北",
    "上海": "华东",
    "江苏": "华东",
    "浙江": "华东",
    "安徽": "华东",
    "福建": "华东",
    "江西": "华东",
    "山东": "华东",
    "河南": "华中",
    "湖北": "华中",
    "湖南": "华中",
    "广东": "华南",
    "广西": "华南",
    "海南": "华南",
    "重庆": "西南",
    "四川": "西南",
    "贵州": "西南",
    "云南": "西南",
    "西藏": "西南",
    "陕西": "西北",
    "甘肃": "西北",
    "青海": "西北",
    "宁夏": "西北",
    "新疆": "西北",
    "中国香港": "港澳台",
    "中国澳门": "港澳台",
    "中国台湾": "港澳台",
    "未知": "未知",
}
ABROAD = {"德国", "泰国", "新西兰", "澳大利亚", "美国", "日本", "韩国", "新加坡", "英国", "法国", "加拿大"}


def classify_job_relation(row) -> tuple[str, str]:
    import pandas as pd

    content = str(row["评论内容"]) if pd.notna(row["评论内容"]) else ""
    title = str(row["笔记标题"]) if pd.notna(row["笔记标题"]) else ""
    text = content + " " + title
    note_cat = row["笔记主题分类"]

    if any(k in text for k in JOB_SEEK_KW) or note_cat == "招聘兼职":
        return "明确求职招工意向", "高"
    if any(k in text for k in FEE_KW) or note_cat == "劳务费评标咨询":
        return "劳务报酬相关(评标劳务费)", "中"
    # 赔偿单独判断：仅当同时出现劳动相关语境时才算维权
    labor_hit = any(k in content for k in LABOR_RIGHTS_KW)
    if labor_hit or ("赔偿" in content and any(k in content for k in ("劳动", "工伤", "临时工", "仲裁"))):
        return "劳动维权工伤讨论(非直接求职)", "中低"
    if note_cat == "租房转租":
        return "无关(租房)", "无"
    mapping = {
        "维权司法文书(赛格案)": "无关(维权司法文书)",
        "旅游攻略(威海)": "无关(旅游攻略)",
        "旅拍身材展示": "无关(旅拍身材)",
        "正能量见义勇为": "无关(正能量)",
    }
    if note_cat in mapping:
        return mapping[note_cat], "无"
    if any(k in content for k in JOB_KEYWORDS):
        return "弱相关(含工作关键词)", "低"
    return "无关", "无"


def ip_region(ip) -> str:
    import pandas as pd

    if pd.isna(ip):
        return "未知"
    ip = str(ip).strip()
    if ip in ABROAD:
        return "海外"
    return REGION_MAP.get(ip, "其他或海外")


def intent(row) -> str:
    import pandas as pd

    c = str(row["评论内容"]) if pd.notna(row["评论内容"]) else ""
    cat = row["笔记主题分类"]
    if row["求职相关强度"] == "高":
        return "询问是否缺人求职"
    if cat == "劳务费评标咨询":
        return "询问或分享劳务费到账"
    if cat == "租房转租":
        if any(k in c for k in ("多少钱", "价格", "问价")):
            return "询价"
        if any(k in c for k in ("还在吗", "位置", "看房", "短租", "几个月")):
            return "询问房源状态位置"
        return "租房咨询"
    if cat == "维权司法文书(赛格案)":
        if any(k in c for k in ("加油", "支持", "顶", "up", "🆙", "坚", "正义", "扫黑")):
            return "声援顶热度"
        if any(k in c for k in ("赛格", "黑", "保护", "伞", "审判", "程")):
            return "案情讨论"
        return "其他互动"
    if cat == "旅游攻略(威海)":
        return "旅游经验避雷分享"
    if cat == "旅拍身材展示":
        return "外貌身材评价"
    if cat == "正能量见义勇为":
        return "赞美英雄"
    if any(k in c for k in ("劳动仲裁", "劳动关系", "劳动局")):
        return "劳动维权建议"
    if any(k in c for k in ("游客", "凶手", "景区", "拘留")):
        return "事故追责讨论"
    return "其他"


def safe_sheet(name: str) -> str:
    return re.sub(r"[\\/*?:\[\]]", "-", str(name))[:28]


REQUIRED_COLS = ("评论内容", "评论者IP地址", "笔记标题")


def classify(input_path: Path, output_path: Path | None = None) -> Path:
    import pandas as pd

    print(f"[读取] {input_path}")
    df = pd.read_excel(input_path)

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            f"缺少必要列: {missing}\n当前列: {list(df.columns)}\n"
            "请确认是「采集数据」类 Excel（含评论内容/评论者IP地址/笔记标题）。"
        )

    df.insert(0, "原行号", range(1, len(df) + 1))
    df["笔记主题分类"] = df["笔记标题"].apply(classify_note)

    rels = df.apply(classify_job_relation, axis=1, result_type="expand")
    df["求职相关分类"] = rels[0]
    df["求职相关强度"] = rels[1]
    df["IP大区"] = df["评论者IP地址"].apply(ip_region)
    df["评论意图"] = df.apply(intent, axis=1)

    cols = [
        "原行号",
        "评论者昵称",
        "评论者账号",
        "评论内容",
        "评论者IP地址",
        "IP大区",
        "笔记标题",
        "笔记主题分类",
        "求职相关分类",
        "求职相关强度",
        "评论意图",
        "评论点赞数",
        "评论回复数",
        "评论时间",
        "采集时间",
    ]
    # 原表没有的列跳过
    cols = [c for c in cols if c in df.columns]

    if output_path is None:
        output_path = input_path.with_name(f"{input_path.stem}_分类结果.xlsx")

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df[cols].to_excel(writer, sheet_name="全量标注", index=False)

        summary_rows: list[list] = []
        summary_rows.append(["一、数据概况", "", ""])
        summary_rows.append(["总评论数", len(df), ""])
        summary_rows.append(["涉及笔记数", int(df["笔记标题"].nunique(dropna=True)), ""])
        summary_rows.append(["IP省份数", int(df["评论者IP地址"].nunique()), ""])
        summary_rows.append(["", "", ""])

        summary_rows.append(["二、按笔记主题分类", "条数", "占比"])
        for k, v in df["笔记主题分类"].value_counts().items():
            summary_rows.append([k, int(v), f"{v / len(df) * 100:.1f}%"])
        summary_rows.append(["", "", ""])

        summary_rows.append(["三、按求职相关分类", "条数", "原行号列表"])
        for k, g in df.groupby("求职相关分类", sort=False):
            rows = ",".join(map(str, g["原行号"].tolist()))
            summary_rows.append([k, len(g), rows])
        summary_rows.append(["", "", ""])

        summary_rows.append(["四、按IP归属(省份)", "条数", "占比"])
        for k, v in df["评论者IP地址"].value_counts().items():
            summary_rows.append([k, int(v), f"{v / len(df) * 100:.1f}%"])
        summary_rows.append(["", "", ""])

        summary_rows.append(["五、按IP大区", "条数", "占比"])
        for k, v in df["IP大区"].value_counts().items():
            summary_rows.append([k, int(v), f"{v / len(df) * 100:.1f}%"])
        summary_rows.append(["", "", ""])

        summary_rows.append(["六、按评论意图", "条数", "占比"])
        for k, v in df["评论意图"].value_counts().items():
            summary_rows.append([k, int(v), f"{v / len(df) * 100:.1f}%"])

        pd.DataFrame(summary_rows, columns=["项目", "数值", "备注"]).to_excel(
            writer, sheet_name="分类汇总", index=False
        )

        job_df = df[df["求职相关强度"].isin(["高", "中", "中低", "低"])][cols]
        job_df.to_excel(writer, sheet_name="求职相关明细", index=False)

        for cat in df["笔记主题分类"].value_counts().index.tolist():
            sub = df[df["笔记主题分类"] == cat][cols]
            if len(sub) == 0:
                continue
            sub.to_excel(writer, sheet_name=safe_sheet(cat), index=False)

        cross = pd.crosstab(df["评论者IP地址"], df["笔记主题分类"])
        cross["合计"] = cross.sum(axis=1)
        cross = cross.sort_values("合计", ascending=False)
        cross.to_excel(writer, sheet_name="IP与主题交叉")

    # 控制台摘要
    print()
    print("=" * 50)
    print(f"总评论: {len(df)}")
    print("--- 求职相关 ---")
    for k, g in df.groupby("求职相关分类"):
        strength = g["求职相关强度"].iloc[0]
        if strength == "无":
            print(f"  [{strength}] {k}: {len(g)} 条")
        else:
            print(f"  [{strength}] {k}: {len(g)} 条 -> 行号 {g['原行号'].tolist()}")
    print("--- 主题 TOP ---")
    for k, v in df["笔记主题分类"].value_counts().head(8).items():
        print(f"  {k}: {v}")
    print("--- IP TOP ---")
    for k, v in df["评论者IP地址"].value_counts().head(8).items():
        print(f"  {k}: {v}")
    print("=" * 50)
    print(f"[完成] 结果已保存:\n  {output_path}")
    return output_path


def main() -> int:
    # Windows 控制台尽量用 UTF-8，避免中文乱码
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print("评论采集数据分类工具")
    print("-" * 40)
    ensure_deps()

    if len(sys.argv) >= 2:
        input_path = Path(sys.argv[1].strip().strip('"'))
    else:
        print("未指定文件，请在弹窗中选择 Excel ...")
        input_path = pick_file()
        if input_path is None:
            print("已取消。")
            return 1

    if not input_path.exists():
        print(f"[错误] 文件不存在: {input_path}")
        return 1
    if input_path.suffix.lower() not in (".xlsx", ".xls"):
        print(f"[错误] 请选择 Excel 文件 (.xlsx/.xls): {input_path}")
        return 1

    out_arg = Path(sys.argv[2]) if len(sys.argv) >= 3 else None
    try:
        classify(input_path, out_arg)
    except Exception as e:
        print(f"[错误] 分类失败: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
