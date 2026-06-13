from __future__ import annotations

from typing import Any

import pandas as pd

from tools.ratio_calculator import get_ratio_series


def analyze_dupont(ratio_df: pd.DataFrame) -> dict[str, Any]:
    net_margin = get_ratio_series(ratio_df, "净利率")
    asset_turnover = get_ratio_series(ratio_df, "总资产周转率")
    equity_multiplier = get_ratio_series(ratio_df, "权益乘数")
    roe = get_ratio_series(ratio_df, "净资产收益率（ROE）")
    years = sorted(set(net_margin) | set(asset_turnover) | set(equity_multiplier) | set(roe))

    rows = []
    for year in years:
        rows.append(
            {
                "year": year,
                "net_margin": net_margin.get(year),
                "total_asset_turnover": asset_turnover.get(year),
                "equity_multiplier": equity_multiplier.get(year),
                "roe": roe.get(year),
            }
        )
    table = pd.DataFrame(rows)

    summary = "杜邦分析数据不足，暂不能判断净资产收益率（ROE）变化驱动因素。"
    risk_notes: list[str] = []
    driver = ""
    if len(table.dropna(subset=["roe"])) >= 2:
        valid = table.dropna(subset=["roe"]).sort_values("year")
        prev = valid.iloc[-2]
        curr = valid.iloc[-1]
        changes = {
            "净利率": abs((curr.get("net_margin") or 0) - (prev.get("net_margin") or 0)),
            "总资产周转率": abs((curr.get("total_asset_turnover") or 0) - (prev.get("total_asset_turnover") or 0)),
            "权益乘数": abs((curr.get("equity_multiplier") or 0) - (prev.get("equity_multiplier") or 0)),
        }
        driver = max(changes, key=changes.get)
        direction = "上升" if curr["roe"] > prev["roe"] else "下降"
        summary = f"{int(prev['year'])} 年至 {int(curr['year'])} 年净资产收益率（ROE）{direction}，变化主要受{driver}影响。"
        if curr["roe"] > prev["roe"] and driver == "权益乘数":
            risk_notes.append("净资产收益率（ROE）上升主要由权益乘数推动，提示需关注财务杠杆驱动而非经营改善。")

    return {
        "dupont_table": table,
        "dupont_summary": summary,
        "dupont_risk_notes": risk_notes,
        "primary_driver": driver,
    }
