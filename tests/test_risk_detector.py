import pandas as pd

from tools.dupont_analyzer import analyze_dupont
from tools.ratio_calculator import calculate_ratios
from tools.risk_detector import detect_risks


def test_detects_cashflow_profit_divergence(tmp_path):
    df = pd.DataFrame(
        {
            2022: {
                "operating_revenue": 100,
                "operating_cost": 60,
                "net_profit": 10,
                "net_operating_cash_flow": 12,
                "total_assets": 200,
                "total_liabilities": 80,
                "total_equity": 120,
                "current_assets": 90,
                "current_liabilities": 45,
                "accounts_receivable": 20,
                "inventory": 30,
            },
            2023: {
                "operating_revenue": 130,
                "operating_cost": 80,
                "net_profit": 20,
                "net_operating_cash_flow": 8,
                "total_assets": 260,
                "total_liabilities": 130,
                "total_equity": 130,
                "current_assets": 95,
                "current_liabilities": 60,
                "accounts_receivable": 50,
                "inventory": 60,
            },
            2024: {
                "operating_revenue": 140,
                "operating_cost": 95,
                "net_profit": 22,
                "net_operating_cash_flow": 7,
                "total_assets": 300,
                "total_liabilities": 170,
                "total_equity": 130,
                "current_assets": 96,
                "current_liabilities": 70,
                "accounts_receivable": 75,
                "inventory": 90,
            },
        }
    )
    ratios = calculate_ratios(df, tmp_path / "ratios.xlsx")
    risks = detect_risks(df, ratios, analyze_dupont(ratios))
    risk_ids = {risk["risk_id"] for risk in risks}
    assert "R103" in risk_ids
    assert "R107" in risk_ids
