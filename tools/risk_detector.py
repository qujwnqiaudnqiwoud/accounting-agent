from __future__ import annotations

from typing import Any

import pandas as pd

from schemas.financial_schema import RiskFinding
from tools.knowledge_loader import load_risk_rules
from tools.ratio_calculator import get_ratio_series


def _item_series(df: pd.DataFrame, item: str) -> dict[int, float]:
    if item not in df.index:
        return {}
    return {int(year): float(df.loc[item, year]) for year in df.columns if pd.notna(df.loc[item, year])}


def _growth(series: dict[int, float]) -> dict[int, float]:
    years = sorted(series)
    result: dict[int, float] = {}
    for prev, curr in zip(years, years[1:]):
        if series[prev] != 0:
            result[curr] = series[curr] / series[prev] - 1
    return result


def _latest_pair(growth_a: dict[int, float], growth_b: dict[int, float]) -> tuple[int, float, float] | None:
    years = sorted(set(growth_a) & set(growth_b))
    if not years:
        return None
    year = years[-1]
    return year, growth_a[year], growth_b[year]


def _is_decreasing(values: dict[int, float]) -> bool:
    ordered = [values[y] for y in sorted(values)]
    return len(ordered) >= 3 and all(ordered[i] < ordered[i - 1] for i in range(1, len(ordered)))


def _is_increasing(values: dict[int, float]) -> bool:
    ordered = [values[y] for y in sorted(values)]
    return len(ordered) >= 3 and all(ordered[i] > ordered[i - 1] for i in range(1, len(ordered)))


def detect_risks(
    clean_df: pd.DataFrame,
    ratio_df: pd.DataFrame,
    dupont_result: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    findings: list[RiskFinding] = []
    _ = load_risk_rules()

    revenue_g = _growth(_item_series(clean_df, "operating_revenue"))
    ar_g = _growth(_item_series(clean_df, "accounts_receivable"))
    pair = _latest_pair(ar_g, revenue_g)
    if pair and pair[1] - pair[2] > 0.2 and pair[1] > 0.1:
        year, ar, rev = pair
        findings.append(
            RiskFinding(
                "R101",
                "应收账款增长异常",
                "中",
                f"{year} 年应收账款增长率 {ar:.2%}，高于营业收入增长率 {rev:.2%}。",
                "提示赊销规模或回款压力可能上升，收入质量需结合账龄结构进一步核查。",
                "关注客户信用政策、应收账款账龄和坏账准备计提充分性。",
            )
        )

    inventory_g = _growth(_item_series(clean_df, "inventory"))
    cost_g = _growth(_item_series(clean_df, "operating_cost"))
    pair = _latest_pair(inventory_g, cost_g)
    if pair and pair[1] - pair[2] > 0.2 and pair[1] > 0.1:
        year, inv, cost = pair
        findings.append(
            RiskFinding(
                "R102",
                "存货增长较快",
                "中",
                f"{year} 年存货增长率 {inv:.2%}，高于营业成本增长率 {cost:.2%}。",
                "提示存货周转和跌价压力可能增加。",
                "进一步核查存货库龄、产品结构和跌价准备计提情况。",
            )
        )

    profit_g = _growth(_item_series(clean_df, "net_profit"))
    ocf_g = _growth(_item_series(clean_df, "net_operating_cash_flow"))
    pair = _latest_pair(profit_g, ocf_g)
    if pair and pair[1] > 0 and pair[2] < 0:
        year, profit, ocf = pair
        findings.append(
            RiskFinding(
                "R103",
                "利润增长与经营活动现金流量净额背离",
                "高",
                f"{year} 年净利润增长 {profit:.2%}，经营活动现金流量净额下降 {ocf:.2%}。",
                "提示利润现金含量可能不足，需关注收入回款和营运资金占用。",
                "结合应收账款、存货和合同负债变化进一步分析。",
            )
        )

    gross_margin = get_ratio_series(ratio_df, "毛利率")
    if _is_decreasing(gross_margin):
        findings.append(
            RiskFinding(
                "R104",
                "毛利率连续下降",
                "中",
                "毛利率近三年连续下降。",
                "提示产品竞争力或成本控制可能承压。",
                "关注售价、原材料成本、产品结构和费用转嫁能力。",
            )
        )

    debt_ratio = get_ratio_series(ratio_df, "资产负债率")
    if _is_increasing(debt_ratio):
        findings.append(
            RiskFinding(
                "R105",
                "资产负债率持续上升",
                "中",
                "资产负债率近三年持续上升。",
                "提示偿债压力和财务弹性需关注。",
                "进一步区分金融性负债与经营性负债，并关注债务期限结构。",
            )
        )

    current_ratio = get_ratio_series(ratio_df, "流动比率")
    quick_ratio = get_ratio_series(ratio_df, "速动比率")
    years = sorted(set(current_ratio) & set(quick_ratio))
    if len(years) >= 2 and current_ratio[years[-1]] < current_ratio[years[-2]] and quick_ratio[years[-1]] < quick_ratio[years[-2]]:
        findings.append(
            RiskFinding(
                "R106",
                "短期偿债能力下降",
                "中",
                f"{years[-1]} 年流动比率和速动比率较上年同时下降。",
                "提示短期偿债安全边际可能收窄。",
                "关注流动负债到期压力、受限资金和存货变现能力。",
            )
        )

    ocf_profit = get_ratio_series(ratio_df, "净利润现金含量")
    low_years = [year for year, value in ocf_profit.items() if value < 1]
    if len(low_years) >= 2:
        findings.append(
            RiskFinding(
                "R107",
                "经营活动现金流量净额长期低于净利润",
                "高",
                "净利润现金含量至少两个年度低于 100%。",
                "提示盈余质量和利润现金含量需关注。",
                "结合商业信用、应收账款回款和存货占用进一步核查。",
            )
        )

    if dupont_result and dupont_result.get("primary_driver") == "权益乘数" and dupont_result.get("dupont_risk_notes"):
        findings.append(
            RiskFinding(
                "R108",
                "净资产收益率（ROE）上升可能由杠杆驱动",
                "中",
                dupont_result["dupont_risk_notes"][0],
                "提示股东回报改善可能更多来自财务杠杆，而非经营效率或盈利能力改善。",
                "关注债务成本、偿债能力和杠杆扩张可持续性。",
            )
        )

    impairment_g = _growth(_item_series(clean_df, "asset_impairment_loss"))
    if impairment_g:
        year = sorted(impairment_g)[-1]
        if impairment_g[year] > 0.5:
            findings.append(
                RiskFinding(
                    "R109",
                    "资产减值损失大幅增加",
                    "中",
                    f"{year} 年资产减值相关项目增长 {impairment_g[year]:.2%}。",
                    "提示资产质量可能承压，需关注减值测试和相关资产可收回金额。",
                    "进一步核查应收、存货、商誉和长期资产减值明细。",
                )
            )

    nonrec = _item_series(clean_df, "non_recurring_pnl")
    profit = _item_series(clean_df, "net_profit")
    common_years = sorted(set(nonrec) & set(profit))
    if common_years and profit[common_years[-1]] != 0:
        year = common_years[-1]
        impact = abs(nonrec[year] / profit[year])
        if impact > 0.2:
            findings.append(
                RiskFinding(
                    "R110",
                    "非经常性损益影响较大",
                    "中",
                    f"{year} 年非经常性损益占净利润比例约 {impact:.2%}。",
                    "提示利润可持续性需关注。",
                    "重点比较扣非净利润和经常性业务盈利能力。",
                )
            )

    return [finding.to_dict() for finding in findings]
