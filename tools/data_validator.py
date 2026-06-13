from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from config.settings import PATHS
from schemas.financial_schema import REQUIRED_CORE_ITEMS


def _value(df: pd.DataFrame, item: str, year: int) -> float | None:
    if item not in df.index or year not in df.columns:
        return None
    value = df.loc[item, year]
    if pd.isna(value):
        return None
    return float(value)


def _result_row(year: int | str, check_name: str, status: str, evidence: str, suggestion: str) -> dict[str, Any]:
    return {
        "年份": year,
        "校验项目": check_name,
        "校验结果": status,
        "校验证据": evidence,
        "处理建议": suggestion,
    }


def _balance_status(gap: float, assets: float) -> tuple[str, str]:
    denominator = max(abs(assets), 1.0)
    relative_gap = abs(gap) / denominator
    if relative_gap <= 0.01:
        return "通过", f"差异率 {relative_gap:.2%}，在 1% 容忍范围内。"
    if relative_gap <= 0.05:
        return "关注", f"差异率 {relative_gap:.2%}，超过 1% 但未超过 5%。"
    return "异常", f"差异率 {relative_gap:.2%}，超过 5%。"


def validate_financial_data(clean_df: pd.DataFrame, output_dir: str | Path | None = None) -> dict[str, Any]:
    """Validate core accounting completeness and basic statement relationships."""
    years = sorted([int(col) for col in clean_df.columns if isinstance(col, int)])
    rows: list[dict[str, Any]] = []

    missing_core_items = [item for item in REQUIRED_CORE_ITEMS if item not in clean_df.index]
    if missing_core_items:
        rows.append(
            _result_row(
                "全部",
                "核心科目完整性",
                "关注",
                "缺失核心科目：" + "、".join(missing_core_items),
                "建议补充缺失科目后重新运行分析；缺失科目对应指标会显示为数据缺失。",
            )
        )
    else:
        rows.append(
            _result_row(
                "全部",
                "核心科目完整性",
                "通过",
                "已识别收入、成本、利润、现金流、资产、负债和权益等核心科目。",
                "可继续进入指标计算和风险识别。",
            )
        )

    for year in years:
        assets = _value(clean_df, "total_assets", year)
        liabilities = _value(clean_df, "total_liabilities", year)
        equity = _value(clean_df, "total_equity", year)
        if assets is None or liabilities is None or equity is None:
            rows.append(
                _result_row(
                    year,
                    "资产负债表勾稽关系",
                    "关注",
                    "总资产、总负债或所有者权益存在缺失，无法校验：资产 = 负债 + 所有者权益。",
                    "请优先补充资产负债表三项核心数据。",
                )
            )
        else:
            gap = assets - liabilities - equity
            status, note = _balance_status(gap, assets)
            rows.append(
                _result_row(
                    year,
                    "资产负债表勾稽关系",
                    status,
                    f"总资产 {assets:,.2f}；总负债+所有者权益 {liabilities + equity:,.2f}；差异 {gap:,.2f}。{note}",
                    "若差异较大，请检查单位、合并/母公司口径和是否遗漏少数股东权益等项目。",
                )
            )

        revenue = _value(clean_df, "operating_revenue", year)
        cost = _value(clean_df, "operating_cost", year)
        profit = _value(clean_df, "net_profit", year)
        ocf = _value(clean_df, "net_operating_cash_flow", year)
        if revenue is not None and revenue <= 0:
            rows.append(
                _result_row(
                    year,
                    "利润表基础合理性",
                    "异常",
                    f"营业收入为 {revenue:,.2f}，不符合常规持续经营企业分析前提。",
                    "请核对年报抽取行是否误匹配，或补充说明特殊业务状态。",
                )
            )
        elif revenue is not None and cost is not None and cost > revenue * 1.5:
            rows.append(
                _result_row(
                    year,
                    "利润表基础合理性",
                    "关注",
                    f"营业成本 {cost:,.2f} 明显高于营业收入 {revenue:,.2f}。",
                    "建议核查收入、成本口径是否一致，并结合毛利率进一步分析。",
                )
            )
        else:
            rows.append(
                _result_row(
                    year,
                    "利润表基础合理性",
                    "通过",
                    "营业收入、营业成本和净利润未触发基础异常校验。",
                    "可继续结合盈利能力指标和趋势变化判断利润质量。",
                )
            )

        if profit is not None and profit > 0 and ocf is not None and ocf < 0:
            rows.append(
                _result_row(
                    year,
                    "利润现金流匹配性",
                    "关注",
                    f"净利润为正 {profit:,.2f}，但经营活动现金流量净额为负 {ocf:,.2f}。",
                    "建议重点核查应收账款、存货、合同资产和收入确认节奏。",
                )
            )
        elif profit is None or ocf is None:
            rows.append(
                _result_row(
                    year,
                    "利润现金流匹配性",
                    "关注",
                    "净利润或经营活动现金流量净额缺失，无法进行匹配性校验。",
                    "请补充利润表和现金流量表核心项目。",
                )
            )
        else:
            rows.append(
                _result_row(
                    year,
                    "利润现金流匹配性",
                    "通过",
                    "净利润与经营活动现金流量净额未触发基础背离校验。",
                    "仍需结合净利润现金含量和营运资金占用进一步判断。",
                )
            )

    detail_df = pd.DataFrame(rows)
    raw_counts = detail_df["校验结果"].value_counts().to_dict() if not detail_df.empty else {}
    counts = {str(key): int(value) for key, value in raw_counts.items()}
    summary = (
        f"数据校验完成：通过 {counts.get('通过', 0)} 项，"
        f"关注 {counts.get('关注', 0)} 项，异常 {counts.get('异常', 0)} 项。"
    )
    overall_status = "异常" if counts.get("异常", 0) else "关注" if counts.get("关注", 0) else "通过"

    out_dir = Path(output_dir) if output_dir else PATHS.tables_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    excel_path = out_dir / "data_validation.xlsx"
    json_path = out_dir / "data_validation.json"
    detail_df.to_excel(excel_path, index=False)
    json_path.write_text(
        json.dumps(
            {
                "overall_status": overall_status,
                "summary": summary,
                "counts": counts,
                "details": rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        "overall_status": overall_status,
        "summary": summary,
        "counts": counts,
        "details": rows,
        "detail_table": detail_df,
        "excel_path": excel_path,
        "json_path": json_path,
    }
