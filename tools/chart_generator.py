from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go

from config.settings import PATHS
from tools.ratio_calculator import get_ratio_series


COLORS = ["#1F4D3A", "#C7A76C", "#666666", "#8A3A2B", "#2E6B4F"]


def _item_series(df: pd.DataFrame, item: str) -> tuple[list[int], list[float]]:
    if item not in df.index:
        return [], []
    years = sorted([int(col) for col in df.columns if pd.notna(df.loc[item, col])])
    return years, [float(df.loc[item, year]) for year in years]


def _add_line(fig: go.Figure, x: list[int], y: list[float], name: str, color: str) -> None:
    if x and y:
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", name=name, line=dict(color=color, width=3)))


def _style(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title=title,
        template="plotly_white",
        font=dict(color="#222222"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=35, r=20, t=70, b=35),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E5E2D8")
    return fig


def generate_charts(
    clean_df: pd.DataFrame,
    ratio_df: pd.DataFrame,
    dupont_result: dict[str, Any],
    risks: list[dict[str, str]],
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    out = Path(output_dir) if output_dir else PATHS.charts_dir
    out.mkdir(parents=True, exist_ok=True)
    figures: dict[str, go.Figure] = {}
    paths: dict[str, Path] = {}

    fig = go.Figure()
    for idx, (item, label) in enumerate(
        [
            ("operating_revenue", "营业收入"),
            ("net_profit", "净利润"),
            ("net_operating_cash_flow", "经营活动现金流量净额"),
        ]
    ):
        x, y = _item_series(clean_df, item)
        _add_line(fig, x, y, label, COLORS[idx])
    figures["operating_trend"] = _style(fig, "营业收入、净利润、经营活动现金流量净额趋势")

    fig = go.Figure()
    for idx, ratio in enumerate(["毛利率", "净利率", "净资产收益率（ROE）"]):
        series = get_ratio_series(ratio_df, ratio)
        years = sorted(series)
        _add_line(fig, years, [series[y] * 100 for y in years], ratio, COLORS[idx])
    figures["profitability_trend"] = _style(fig, "毛利率、净利率、净资产收益率（ROE）趋势（%）")

    fig = go.Figure()
    for idx, ratio in enumerate(["资产负债率", "流动比率", "速动比率"]):
        series = get_ratio_series(ratio_df, ratio)
        years = sorted(series)
        multiplier = 100 if ratio == "资产负债率" else 1
        _add_line(fig, years, [series[y] * multiplier for y in years], ratio, COLORS[idx])
    figures["solvency_trend"] = _style(fig, "偿债能力指标趋势")

    dupont_table = dupont_result.get("dupont_table", pd.DataFrame())
    fig = go.Figure()
    if not dupont_table.empty:
        labels = {
            "net_margin": "净利率（%）",
            "total_asset_turnover": "总资产周转率",
            "equity_multiplier": "权益乘数",
            "roe": "净资产收益率（ROE）（%）",
        }
        for idx, col in enumerate(["net_margin", "total_asset_turnover", "equity_multiplier", "roe"]):
            values = dupont_table[col].tolist()
            if col in {"net_margin", "roe"}:
                values = [(v * 100 if pd.notna(v) else None) for v in values]
            _add_line(fig, dupont_table["year"].tolist(), values, labels[col], COLORS[idx % len(COLORS)])
    figures["dupont_trend"] = _style(fig, "杜邦分析拆解趋势")

    fig = go.Figure()
    if risks:
        risk_df = pd.DataFrame(risks)
        counts = risk_df["risk_level"].value_counts().reindex(["低", "中", "高"], fill_value=0)
        fig.add_trace(go.Bar(x=counts.index.tolist(), y=counts.values.tolist(), marker_color=["#6B8F71", "#C7A76C", "#8A3A2B"]))
    figures["risk_distribution"] = _style(fig, "风险等级分布")

    for name, figure in figures.items():
        path = out / f"{name}.html"
        figure.write_html(path, include_plotlyjs="cdn")
        paths[name] = path

    return {"figures": figures, "paths": paths}
