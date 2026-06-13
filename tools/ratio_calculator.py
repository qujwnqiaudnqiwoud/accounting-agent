from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from config.settings import PATHS


def _value(df: pd.DataFrame, item: str, year: int) -> float | None:
    if item not in df.index or year not in df.columns:
        return None
    value = df.loc[item, year]
    if pd.isna(value):
        return None
    return float(value)


def _avg(df: pd.DataFrame, item: str, year: int, years: list[int]) -> float | None:
    current = _value(df, item, year)
    prev_years = [y for y in years if y < year]
    previous = _value(df, item, prev_years[-1],) if prev_years else None
    values = [v for v in [current, previous] if v is not None]
    if not values:
        return None
    return sum(values) / len(values)


def _safe_div(num: float | None, den: float | None) -> float | None:
    if num is None or den is None or den == 0:
        return None
    return num / den


def _growth(df: pd.DataFrame, item: str, year: int, years: list[int]) -> float | None:
    prev_years = [y for y in years if y < year]
    if not prev_years:
        return None
    current = _value(df, item, year)
    previous = _value(df, item, prev_years[-1])
    if current is None or previous in (None, 0):
        return None
    return current / previous - 1


def _ratio_specs() -> list[dict[str, Any]]:
    return [
        {
            "category": "偿债能力",
            "name": "流动比率",
            "formula": "流动资产 / 流动负债",
            "required": ["current_assets", "current_liabilities"],
            "meaning": "衡量企业短期偿债能力。",
            "calc": lambda df, y, ys: _safe_div(_value(df, "current_assets", y), _value(df, "current_liabilities", y)),
        },
        {
            "category": "偿债能力",
            "name": "速动比率",
            "formula": "(流动资产 - 存货) / 流动负债",
            "required": ["current_assets", "inventory", "current_liabilities"],
            "meaning": "剔除存货后衡量即时短期偿债能力。",
            "calc": lambda df, y, ys: _safe_div(
                None
                if _value(df, "current_assets", y) is None or _value(df, "inventory", y) is None
                else _value(df, "current_assets", y) - _value(df, "inventory", y),
                _value(df, "current_liabilities", y),
            ),
        },
        {
            "category": "偿债能力",
            "name": "资产负债率",
            "formula": "总负债 / 总资产",
            "required": ["total_liabilities", "total_assets"],
            "meaning": "衡量企业财务杠杆水平。",
            "calc": lambda df, y, ys: _safe_div(_value(df, "total_liabilities", y), _value(df, "total_assets", y)),
            "percent": True,
        },
        {
            "category": "偿债能力",
            "name": "权益乘数",
            "formula": "总资产 / 所有者权益",
            "required": ["total_assets", "total_equity"],
            "meaning": "衡量权益资本撬动资产规模的杠杆倍数。",
            "calc": lambda df, y, ys: _safe_div(_value(df, "total_assets", y), _value(df, "total_equity", y)),
        },
        {
            "category": "营运能力",
            "name": "应收账款周转率",
            "formula": "营业收入 / 平均应收账款",
            "required": ["operating_revenue", "accounts_receivable"],
            "meaning": "衡量商业债权回收效率。",
            "calc": lambda df, y, ys: _safe_div(_value(df, "operating_revenue", y), _avg(df, "accounts_receivable", y, ys)),
        },
        {
            "category": "营运能力",
            "name": "存货周转率",
            "formula": "营业成本 / 平均存货",
            "required": ["operating_cost", "inventory"],
            "meaning": "衡量存货周转和管理效率。",
            "calc": lambda df, y, ys: _safe_div(_value(df, "operating_cost", y), _avg(df, "inventory", y, ys)),
        },
        {
            "category": "营运能力",
            "name": "总资产周转率",
            "formula": "营业收入 / 平均总资产",
            "required": ["operating_revenue", "total_assets"],
            "meaning": "衡量资产整体运营效率。",
            "calc": lambda df, y, ys: _safe_div(_value(df, "operating_revenue", y), _avg(df, "total_assets", y, ys)),
        },
        {
            "category": "盈利能力",
            "name": "毛利率",
            "formula": "(营业收入 - 营业成本) / 营业收入",
            "required": ["operating_revenue", "operating_cost"],
            "meaning": "衡量产品或服务的基本盈利空间。",
            "calc": lambda df, y, ys: _safe_div(
                None
                if _value(df, "operating_revenue", y) is None or _value(df, "operating_cost", y) is None
                else _value(df, "operating_revenue", y) - _value(df, "operating_cost", y),
                _value(df, "operating_revenue", y),
            ),
            "percent": True,
        },
        {
            "category": "盈利能力",
            "name": "净利率",
            "formula": "净利润 / 营业收入",
            "required": ["net_profit", "operating_revenue"],
            "meaning": "衡量收入转化为最终利润的能力。",
            "calc": lambda df, y, ys: _safe_div(_value(df, "net_profit", y), _value(df, "operating_revenue", y)),
            "percent": True,
        },
        {
            "category": "盈利能力",
            "name": "总资产报酬率（ROA）",
            "formula": "净利润 / 平均总资产",
            "required": ["net_profit", "total_assets"],
            "meaning": "衡量总资产报酬水平。",
            "calc": lambda df, y, ys: _safe_div(_value(df, "net_profit", y), _avg(df, "total_assets", y, ys)),
            "percent": True,
        },
        {
            "category": "盈利能力",
            "name": "净资产收益率（ROE）",
            "formula": "净利润 / 平均所有者权益",
            "required": ["net_profit", "total_equity"],
            "meaning": "衡量股东投入资本形成净利润的能力。",
            "calc": lambda df, y, ys: _safe_div(_value(df, "net_profit", y), _avg(df, "total_equity", y, ys)),
            "percent": True,
        },
        {
            "category": "成长能力",
            "name": "营业收入增长率",
            "formula": "(本年营业收入 - 上年营业收入) / 上年营业收入",
            "required": ["operating_revenue"],
            "meaning": "衡量收入规模成长速度。",
            "calc": lambda df, y, ys: _growth(df, "operating_revenue", y, ys),
            "percent": True,
        },
        {
            "category": "成长能力",
            "name": "净利润增长率",
            "formula": "(本年净利润 - 上年净利润) / 上年净利润",
            "required": ["net_profit"],
            "meaning": "衡量利润成长速度。",
            "calc": lambda df, y, ys: _growth(df, "net_profit", y, ys),
            "percent": True,
        },
        {
            "category": "成长能力",
            "name": "总资产增长率",
            "formula": "(本年总资产 - 上年总资产) / 上年总资产",
            "required": ["total_assets"],
            "meaning": "衡量资产规模扩张速度。",
            "calc": lambda df, y, ys: _growth(df, "total_assets", y, ys),
            "percent": True,
        },
        {
            "category": "成长能力",
            "name": "所有者权益增长率",
            "formula": "(本年所有者权益 - 上年所有者权益) / 上年所有者权益",
            "required": ["total_equity"],
            "meaning": "衡量权益资本积累速度。",
            "calc": lambda df, y, ys: _growth(df, "total_equity", y, ys),
            "percent": True,
        },
        {
            "category": "现金流量质量",
            "name": "净利润现金含量",
            "formula": "经营活动现金流量净额 / 净利润",
            "required": ["net_operating_cash_flow", "net_profit"],
            "meaning": "衡量净利润由经营活动现金流量净额支撑的程度。",
            "calc": lambda df, y, ys: _safe_div(_value(df, "net_operating_cash_flow", y), _value(df, "net_profit", y)),
            "percent": True,
        },
        {
            "category": "现金流量质量",
            "name": "销售收现比率",
            "formula": "销售商品、提供劳务收到的现金 / 营业收入",
            "required": ["cash_received_from_sales", "operating_revenue"],
            "meaning": "衡量收入回款质量。",
            "calc": lambda df, y, ys: _safe_div(_value(df, "cash_received_from_sales", y), _value(df, "operating_revenue", y)),
            "percent": True,
        },
        {
            "category": "现金流量质量",
            "name": "经营现金流量收入比率",
            "formula": "经营活动现金流量净额 / 营业收入",
            "required": ["net_operating_cash_flow", "operating_revenue"],
            "meaning": "衡量营业收入转化为经营活动现金流量净额的能力。",
            "calc": lambda df, y, ys: _safe_div(_value(df, "net_operating_cash_flow", y), _value(df, "operating_revenue", y)),
            "percent": True,
        },
    ]


def calculate_ratios(clean_df: pd.DataFrame, output_path: str | Path | None = None) -> pd.DataFrame:
    years = sorted([int(col) for col in clean_df.columns if isinstance(col, int)])
    rows: list[dict[str, Any]] = []
    for spec in _ratio_specs():
        missing = [item for item in spec["required"] if item not in clean_df.index]
        for year in years:
            value = None if missing else spec["calc"](clean_df, year, years)
            rows.append(
                {
                    "指标类别": spec["category"],
                    "指标名称": spec["name"],
                    "年份": year,
                    "指标值": value,
                    "是否百分比": bool(spec.get("percent", False)),
                    "计算公式": spec["formula"],
                    "所需字段": "、".join(spec["required"]),
                    "指标含义": spec["meaning"],
                    "分析提示": "需结合行业特征、企业战略和项目质量综合判断。",
                    "异常说明": "数据缺失，未计算。" if missing else "",
                }
            )

    result = pd.DataFrame(rows)
    path = Path(output_path) if output_path else PATHS.tables_dir / "ratio_results.xlsx"
    path.parent.mkdir(parents=True, exist_ok=True)
    result.to_excel(path, index=False)
    return result


def pivot_ratio_table(ratio_df: pd.DataFrame) -> pd.DataFrame:
    display_df = ratio_df.copy()
    display_df["指标值展示"] = display_df.apply(
        lambda row: ""
        if pd.isna(row["指标值"])
        else f"{float(row['指标值']):.2%}"
        if bool(row["是否百分比"])
        else f"{float(row['指标值']):.2f}",
        axis=1,
    )
    pivot = display_df.pivot_table(
        index=["指标类别", "指标名称", "计算公式", "指标含义"],
        columns="年份",
        values="指标值展示",
        aggfunc="first",
    ).reset_index()
    pivot.columns = [str(col) for col in pivot.columns]
    return pivot


def get_ratio_series(ratio_df: pd.DataFrame, name: str) -> dict[int, float]:
    part = ratio_df[ratio_df["指标名称"] == name]
    return {
        int(row["年份"]): float(row["指标值"])
        for _, row in part.iterrows()
        if pd.notna(row["指标值"])
    }
