# -*- coding: utf-8 -*-
"""交流电压输入解析：绝对 V 或相对 Un 的百分比。"""


def resolve_ac_volt_input(raw, base_un):
    """将用户输入解析为绝对电压（V）。

    支持：
    - 绝对值：``230`` / ``257.6`` / ``257.6V``
    - 百分比：``112%`` / ``112 ％``（相对 ``base_un``，即通常为 step1 交流电压）

    无 ``%`` 后缀时一律按伏特处理，保持旧配置兼容。

    Returns:
        float: 解析后的电压（保留 2 位小数）

    Raises:
        ValueError: 空串、非数字、或百分比缺少有效 Un
    """
    text = (raw or "").strip().replace("％", "%")
    if not text:
        raise ValueError("电压输入为空")

    is_pct = text.endswith("%")
    num_part = text[:-1].strip() if is_pct else text
    num_part = num_part.rstrip("VvＶｖ").strip()
    if not num_part:
        raise ValueError(f"无法解析电压: {raw!r}")

    try:
        value = float(num_part)
    except ValueError as exc:
        raise ValueError(f"无法解析电压: {raw!r}") from exc

    if is_pct:
        try:
            un = float(base_un)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"百分比电压需要有效 Un，当前 Un={base_un!r}") from exc
        if un <= 0:
            raise ValueError(f"Un 必须为正数，当前 Un={un}")
        return round(un * value / 100.0, 2)

    return round(value, 2)


def format_volt_for_scpi(volts):
    """格式化为 SCPI VOLT 参数字符串。"""
    v = float(volts)
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.2f}".rstrip("0").rstrip(".")
