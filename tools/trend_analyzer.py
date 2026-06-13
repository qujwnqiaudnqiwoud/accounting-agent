from __future__ import annotations

from typing import Any

import pandas as pd

from tools.ratio_calculator import get_ratio_series


CORE_ITEM_LABELS = {
    "operating_revenue": "营业收入",
    "net_profit": "净利润",
    "net_operating_cash_flow": "经营活动现金流量净额",
    "total_assets": "总资产",
    "total_liabilities": "总负债",
    "total_equity": "所有者权益",
    "accounts_receivable": "应收账款",
    "inventory": "存货",
}


def _classify(values: list[float | None]) -> str:
    valid = [v for v in values if v is not None and pd.notna(v)]
    if len(valid) < 2:
        return "数据不足"
    avg_abs = sum(abs(v) for v in valid) / len(valid) or 1
    if max(valid) - min(valid) <= avg_abs * 0.05:
        return "基本稳定"
    if all(valid[i] >= valid[i - 1] for i in range(1, len(valid))):
        return "上升"
    if all(valid[i] <= valid[i - 1] for i in range(1, len(valid))):
        return "下降"
    return "波动"


def _basis(years: list[int], values: list[float | None]) -> str:
    pairs = [(y, v) for y, v in zip(years, values) if v is not None and pd.notna(v)]
    if len(pairs) < 2:
        return "可用年度数据不足，暂不判断。"
    first_y, first_v = pairs[0]
    last_y, last_v = pairs[-1]
    if first_v == 0:
        return f"{first_y} 年为 0，无法计算整体变动幅度。"
    change = last_v / first_v - 1
    return f"{first_y} 年至 {last_y} 年累计变动 {change:.2%}。"


def analyze_trends(clean_df: pd.DataFrame, ratio_df: pd.DataFrame) -> pd.DataFrame:
    years = sorted([int(col) for col in clean_df.columns if isinstance(col, int)])
    rows: list[dict[str, Any]] = []

    for item, label in CORE_ITEM_LABELS.items():
        if item not in clean_df.index:
            continue
        values = [clean_df.loc[item, year] if year in clean_df.columns else None for year in years]
        trend = _classify(values)
        rows.append(
            {
                "分析对象": label,
                "趋势判断": trend,
                "主要依据": _basis(years, values),
                "初步解释": _explain(label, trend),
            }
        )

    for ratio_name in ["毛利率", "净利率", "净资产收益率（ROE）", "资产负债率", "流动比率", "净利润现金含量"]:
        series = get_ratio_series(ratio_df, ratio_name)
        values = [series.get(year) for year in years]
        trend = _classify(values)
        rows.append(
            {
                "分析对象": ratio_name,
                "趋势判断": trend,
                "主要依据": _basis(years, values),
                "初步解释": _explain(ratio_name, trend),
            }
        )

    return pd.DataFrame(rows)


def _explain(label: str, trend: str) -> str:
    if trend == "上升":
        return f"{label}呈上升态势，需结合质量、现金流和战略背景判断其可持续性。"
    if trend == "下降":
        return f"{label}呈下降态势，提示相关能力或规模可能承压。"
    if trend == "波动":
        return f"{label}波动较明显，建议关注业务稳定性和一次性因素。"
    if trend == "基本稳定":
        return f"{label}整体较稳定，可作为后续横向比较基础。"
    return f"{label}数据不足，暂不形成趋势结论。"
