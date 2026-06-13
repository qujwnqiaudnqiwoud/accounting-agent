from __future__ import annotations

from typing import Any

import pandas as pd


def _get(df: pd.DataFrame, item: str, year: int) -> float | None:
    if item not in df.index or year not in df.columns or pd.isna(df.loc[item, year]):
        return None
    return float(df.loc[item, year])


def _evaluate(ratio: float | None, ocf: float | None, net_profit: float | None) -> str:
    if ratio is None:
        return "数据不足"
    if ocf is not None and ocf < 0 < (net_profit or 0):
        return "风险较高"
    if ratio >= 1.2:
        return "良好"
    if ratio >= 1.0:
        return "一般"
    if ratio >= 0.6:
        return "需要关注"
    return "风险较高"


def analyze_cashflow_quality(clean_df: pd.DataFrame) -> dict[str, Any]:
    years = sorted([int(col) for col in clean_df.columns if isinstance(col, int)])
    rows: list[dict[str, Any]] = []
    for year in years:
        net_profit = _get(clean_df, "net_profit", year)
        ocf = _get(clean_df, "net_operating_cash_flow", year)
        sales_cash = _get(clean_df, "cash_received_from_sales", year)
        revenue = _get(clean_df, "operating_revenue", year)
        ratio = None if net_profit in (None, 0) or ocf is None else ocf / net_profit
        sales_cash_ratio = None if revenue in (None, 0) or sales_cash is None else sales_cash / revenue
        rows.append(
            {
                "year": year,
                "net_profit": net_profit,
                "net_operating_cash_flow": ocf,
                "ocf_to_net_profit": ratio,
                "sales_cash_ratio": sales_cash_ratio,
                "evaluation": _evaluate(ratio, ocf, net_profit),
            }
        )

    table = pd.DataFrame(rows)
    evaluations = table["evaluation"].tolist() if not table.empty else []
    if "风险较高" in evaluations:
        overall = "风险较高"
    elif "需要关注" in evaluations:
        overall = "需要关注"
    elif "一般" in evaluations:
        overall = "一般"
    elif "良好" in evaluations:
        overall = "良好"
    else:
        overall = "数据不足"

    reasons = []
    low_count = table["ocf_to_net_profit"].dropna().lt(1).sum() if not table.empty else 0
    if low_count >= 2:
        reasons.append("净利润现金含量连续低于 100%，提示利润现金含量需要关注。")
    if not table.empty and table["net_operating_cash_flow"].dropna().is_monotonic_decreasing:
        reasons.append("经营活动现金流量净额呈下降趋势，需结合应收账款、存货和收入确认质量进一步分析。")
    if not reasons:
        reasons.append("经营活动现金流量净额与净利润整体匹配度尚可，仍需结合行业结算模式判断。")

    return {
        "cashflow_table": table,
        "cashflow_quality": overall,
        "cashflow_summary": " ".join(reasons),
    }
