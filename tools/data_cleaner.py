from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import pandas as pd

from schemas.financial_schema import REQUIRED_CORE_ITEMS, STANDARD_ITEMS


@dataclass
class CleanedFinancialData:
    data: pd.DataFrame
    missing_core_items: list[str]
    item_mapping: dict[str, str]
    warnings: list[str]
    years: list[int]


def _normalize_text(value: Any) -> str:
    text = str(value).strip()
    text = re.sub(r"\s+", "", text)
    text = text.replace("（", "(").replace("）", ")")
    return text


def _to_number(value: Any) -> float | None:
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    text = text.replace("，", "").replace("元", "").replace("万元", "")
    if text in {"", "-", "--", "—", "nan", "None"}:
        return None
    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    try:
        number = float(text)
    except ValueError:
        return None
    return -number if negative else number


def _build_alias_map() -> dict[str, str]:
    alias_map: dict[str, str] = {}
    for canonical, aliases in STANDARD_ITEMS.items():
        alias_map[_normalize_text(canonical)] = canonical
        for alias in aliases:
            alias_map[_normalize_text(alias)] = canonical
    return alias_map


def _detect_year_columns(columns: list[Any]) -> list[Any]:
    year_columns: list[Any] = []
    for col in columns:
        match = re.search(r"(20\d{2})", str(col))
        if match:
            year_columns.append(col)
    return year_columns


def _detect_project_column(columns: list[Any]) -> Any:
    preferred = ["项目", "科目", "财务项目", "报表项目", "item", "项目名称"]
    normalized = {_normalize_text(col): col for col in columns}
    for name in preferred:
        if _normalize_text(name) in normalized:
            return normalized[_normalize_text(name)]
    return columns[0]


def _is_long_format(df: pd.DataFrame) -> bool:
    normalized = {_normalize_text(col) for col in df.columns}
    has_year = bool(normalized & {"年份", "年度", "year"})
    has_item = bool(normalized & {"项目", "科目", "财务项目", "报表项目", "item"})
    has_amount = bool(normalized & {"金额", "数值", "value", "amount"})
    return has_year and has_item and has_amount


def _long_to_wide(df: pd.DataFrame) -> pd.DataFrame:
    columns = {_normalize_text(col): col for col in df.columns}
    year_col = columns.get("年份") or columns.get("年度") or columns.get("year")
    item_col = columns.get("项目") or columns.get("科目") or columns.get("财务项目") or columns.get("报表项目") or columns.get("item")
    amount_col = columns.get("金额") or columns.get("数值") or columns.get("value") or columns.get("amount")
    if year_col is None or item_col is None or amount_col is None:
        raise ValueError("长表格式需要包含 年份、项目、金额 三类字段。")

    tmp = df[[year_col, item_col, amount_col]].copy()
    tmp[year_col] = tmp[year_col].astype(str).str.extract(r"(20\d{2})").astype(float).astype("Int64")
    tmp[amount_col] = tmp[amount_col].map(_to_number)
    tmp = tmp.dropna(subset=[year_col, item_col])
    return tmp.pivot_table(index=item_col, columns=year_col, values=amount_col, aggfunc="sum").reset_index()


def clean_financial_data(raw_df: pd.DataFrame) -> CleanedFinancialData:
    warnings: list[str] = []
    alias_map = _build_alias_map()
    df = raw_df.copy()

    if _is_long_format(df):
        df = _long_to_wide(df)

    project_col = _detect_project_column(list(df.columns))
    year_cols = _detect_year_columns(list(df.columns))
    if not year_cols:
        raise ValueError("未识别到年度列。请使用类似 2022、2023、2024 的列名。")

    records: list[dict[str, Any]] = []
    item_mapping: dict[str, str] = {}
    for _, row in df.iterrows():
        raw_item = row.get(project_col)
        if pd.isna(raw_item):
            continue
        normalized_item = _normalize_text(raw_item)
        canonical = alias_map.get(normalized_item)
        if not canonical:
            continue
        item_mapping[str(raw_item)] = canonical
        record: dict[str, Any] = {"item": canonical}
        for col in year_cols:
            year = int(re.search(r"(20\d{2})", str(col)).group(1))
            record[year] = _to_number(row.get(col))
        records.append(record)

    if not records:
        raise ValueError("未能识别常见财务科目，请检查项目名称是否包含营业收入、净利润、总资产等。")

    clean_df = pd.DataFrame(records)
    year_values = sorted([col for col in clean_df.columns if isinstance(col, int)])
    clean_df = clean_df.groupby("item", as_index=True)[year_values].sum(min_count=1)
    clean_df = clean_df.sort_index()

    missing = [item for item in REQUIRED_CORE_ITEMS if item not in clean_df.index]
    if missing:
        warnings.append("关键字段缺失：" + "、".join(missing))

    return CleanedFinancialData(
        data=clean_df,
        missing_core_items=missing,
        item_mapping=item_mapping,
        warnings=warnings,
        years=year_values,
    )
