import pandas as pd
import pytest

from tools.data_cleaner import clean_financial_data


def test_clean_wide_format_maps_common_items():
    raw = pd.DataFrame(
        {
            "项目": ["营业收入", "营业成本", "净利润", "总资产", "总负债", "所有者权益", "流动资产合计", "流动负债合计"],
            "2022": [100, 60, 12, 300, 120, 180, 150, 80],
            "2023": [120, 70, 15, 330, 140, 190, 170, 85],
        }
    )
    cleaned = clean_financial_data(raw)
    assert "operating_revenue" in cleaned.data.index
    assert cleaned.data.loc["operating_revenue", 2023] == 120
    assert cleaned.years == [2022, 2023]


def test_clean_long_format():
    raw = pd.DataFrame(
        {
            "年份": [2022, 2023, 2022, 2023],
            "项目": ["营业收入", "营业收入", "净利润", "净利润"],
            "金额": [100, 130, 10, 18],
        }
    )
    cleaned = clean_financial_data(raw)
    assert cleaned.data.loc["operating_revenue", 2023] == 130
    assert cleaned.data.loc["net_profit", 2022] == 10


def test_missing_year_columns_raises_clear_error():
    raw = pd.DataFrame({"项目": ["营业收入"], "金额": [100]})
    with pytest.raises(ValueError, match="未识别到年度列"):
        clean_financial_data(raw)
