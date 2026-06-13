import pandas as pd

from tools.data_validator import validate_financial_data


def _valid_df():
    return pd.DataFrame(
        {
            2023: {
                "operating_revenue": 120.0,
                "operating_cost": 72.0,
                "net_profit": 15.0,
                "net_operating_cash_flow": 18.0,
                "total_assets": 240.0,
                "total_liabilities": 100.0,
                "total_equity": 140.0,
                "current_assets": 100.0,
                "current_liabilities": 50.0,
            }
        }
    )


def test_validate_balance_sheet_identity_passes(tmp_path):
    result = validate_financial_data(_valid_df(), tmp_path)
    statuses = {row["校验结果"] for row in result["details"]}
    assert result["overall_status"] == "通过"
    assert statuses == {"通过"}
    assert (tmp_path / "data_validation.xlsx").exists()
    assert (tmp_path / "data_validation.json").exists()


def test_validate_balance_sheet_identity_flags_large_gap(tmp_path):
    df = _valid_df()
    df.loc["total_equity", 2023] = 100.0
    result = validate_financial_data(df, tmp_path)
    abnormal = [row for row in result["details"] if row["校验结果"] == "异常"]
    assert result["overall_status"] == "异常"
    assert any(row["校验项目"] == "资产负债表勾稽关系" for row in abnormal)


def test_validate_profit_cashflow_mismatch_warns(tmp_path):
    df = _valid_df()
    df.loc["net_operating_cash_flow", 2023] = -2.0
    result = validate_financial_data(df, tmp_path)
    assert result["overall_status"] == "关注"
    assert any(row["校验项目"] == "利润现金流匹配性" and row["校验结果"] == "关注" for row in result["details"])
