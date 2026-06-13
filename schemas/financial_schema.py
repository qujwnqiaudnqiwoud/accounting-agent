from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AnalysisOptions:
    modules: list[str] = field(default_factory=list)
    report_level: str = "标准版"
    enable_pdf: bool = False
    generate_word: bool = True
    show_agent_trace: bool = True
    use_llm: bool = True


@dataclass
class ToolTrace:
    order: int
    tool_name: str
    action: str
    input_summary: str = ""
    output_summary: str = ""
    status: str = "pending"
    elapsed_seconds: float = 0.0
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RiskFinding:
    risk_id: str
    risk_name: str
    risk_level: str
    evidence: str
    explanation: str
    suggestion: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class AnalysisArtifacts:
    ratio_excel: Path | None = None
    markdown_report: Path | None = None
    word_report: Path | None = None
    trace_json: Path | None = None
    chart_paths: dict[str, Path] = field(default_factory=dict)


STANDARD_ITEMS: dict[str, list[str]] = {
    "operating_revenue": ["营业收入", "主营业务收入", "营业总收入", "收入合计"],
    "operating_cost": ["营业成本", "主营业务成本", "营业总成本"],
    "net_profit": ["净利润", "归母净利润", "归属于母公司股东的净利润"],
    "net_operating_cash_flow": ["经营活动现金流量净额", "经营活动产生的现金流量净额", "经营现金流量净额"],
    "cash_received_from_sales": ["销售商品、提供劳务收到的现金", "销售商品提供劳务收到的现金", "销售收现"],
    "total_assets": ["总资产", "资产总计", "资产合计"],
    "total_liabilities": ["总负债", "负债合计", "负债总计"],
    "total_equity": ["所有者权益", "股东权益合计", "所有者权益合计", "归属于母公司所有者权益合计"],
    "current_assets": ["流动资产合计", "流动资产"],
    "current_liabilities": ["流动负债合计", "流动负债"],
    "accounts_receivable": ["应收账款", "应收账款净额"],
    "inventory": ["存货", "存货净额"],
    "cash": ["货币资金", "现金及现金等价物", "现金及银行存款"],
    "asset_impairment_loss": ["资产减值损失", "信用减值损失及资产减值损失"],
    "non_recurring_pnl": ["非经常性损益", "非经常性损益净额"],
}


REQUIRED_CORE_ITEMS = [
    "operating_revenue",
    "operating_cost",
    "net_profit",
    "net_operating_cash_flow",
    "total_assets",
    "total_liabilities",
    "total_equity",
    "current_assets",
    "current_liabilities",
]
