import pandas as pd

from tools.ratio_calculator import calculate_ratios, get_ratio_series


def _sample_clean_df():
    return pd.DataFrame(
        {
            2022: {
                "operating_revenue": 100.0,
                "operating_cost": 60.0,
                "net_profit": 10.0,
                "net_operating_cash_flow": 12.0,
                "cash_received_from_sales": 105.0,
                "total_assets": 200.0,
                "total_liabilities": 80.0,
                "total_equity": 120.0,
                "current_assets": 90.0,
                "current_liabilities": 45.0,
                "accounts_receivable": 20.0,
                "inventory": 30.0,
            },
            2023: {
                "operating_revenue": 120.0,
                "operating_cost": 72.0,
                "net_profit": 15.0,
                "net_operating_cash_flow": 10.0,
                "cash_received_from_sales": 126.0,
                "total_assets": 240.0,
                "total_liabilities": 100.0,
                "total_equity": 140.0,
                "current_assets": 100.0,
                "current_liabilities": 50.0,
                "accounts_receivable": 25.0,
                "inventory": 36.0,
            },
        }
    )


def test_core_ratio_formulas(tmp_path):
    ratios = calculate_ratios(_sample_clean_df(), tmp_path / "ratios.xlsx")
    current_ratio = get_ratio_series(ratios, "流动比率")[2023]
    gross_margin = get_ratio_series(ratios, "毛利率")[2023]
    revenue_growth = get_ratio_series(ratios, "营业收入增长率")[2023]
    assert current_ratio == 2.0
    assert round(gross_margin, 4) == 0.4
    assert round(revenue_growth, 4) == 0.2


def test_ratio_names_use_financial_terms(tmp_path):
    ratios = calculate_ratios(_sample_clean_df(), tmp_path / "ratios.xlsx")
    names = set(ratios["指标名称"])
    assert "净资产收益率（ROE）" in names
    assert "总资产报酬率（ROA）" in names
    assert "净利润现金含量" in names
    assert "销售收现比率" in names
    assert "ROE" not in names
    assert "ROA" not in names
    assert "经营现金流/净利润" not in names


def test_zero_denominator_returns_missing(tmp_path):
    df = _sample_clean_df()
    df.loc["current_liabilities", 2023] = 0
    ratios = calculate_ratios(df, tmp_path / "ratios.xlsx")
    series = get_ratio_series(ratios, "流动比率")
    assert 2023 not in series
