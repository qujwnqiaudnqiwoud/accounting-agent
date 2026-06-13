from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
import sys
from typing import Any

import pandas as pd
import streamlit as st

import agents.main_agent as main_agent_module
from config.settings import ModelConfig, PATHS, load_model_config
from schemas.financial_schema import REQUIRED_CORE_ITEMS
from tools.data_cleaner import clean_financial_data
from tools.file_loader import load_financial_table, save_uploaded_file
from tools.financial_statement_extractor import extract_financial_data_from_report


st.set_page_config(
    page_title="财报智析 Agent",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)


THEME_CSS = """
<style>
    .stApp { background: #F7F7F3; color: #222222; }
    section[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E5E2D8; }
    h1, h2, h3 { color: #1F4D3A; letter-spacing: 0; }
    .hero {
        background: #FFFFFF;
        border: 1px solid #E5E2D8;
        border-left: 6px solid #1F4D3A;
        border-radius: 8px;
        padding: 24px 28px;
        margin-bottom: 18px;
    }
    .hero-title { font-size: 34px; font-weight: 760; color: #1F4D3A; margin: 0 0 6px 0; }
    .hero-subtitle { color: #222222; font-size: 18px; margin-bottom: 10px; }
    .hero-desc { color: #666666; line-height: 1.7; max-width: 1050px; }
    .tag {
        display: inline-block;
        padding: 5px 10px;
        margin: 10px 8px 0 0;
        border: 1px solid #C7A76C;
        border-radius: 999px;
        color: #1F4D3A;
        background: #FAFAF7;
        font-size: 13px;
    }
    .card {
        background: #FFFFFF;
        border: 1px solid #E5E2D8;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
    }
    .flow {
        display: flex;
        gap: 10px;
        align-items: center;
        flex-wrap: wrap;
        color: #1F4D3A;
        font-weight: 650;
    }
    .flow-step {
        background: #FAFAF7;
        border: 1px solid #E5E2D8;
        border-radius: 6px;
        padding: 10px 12px;
    }
    .risk-card {
        background: #FFFFFF;
        border: 1px solid #E5E2D8;
        border-left: 5px solid #C7A76C;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
    }
    .risk-high { border-left-color: #8A3A2B; }
    .risk-mid { border-left-color: #C7A76C; }
    .risk-low { border-left-color: #6B8F71; }
    div.stButton > button {
        background-color: #1F4D3A;
        color: white;
        border: 1px solid #1F4D3A;
        border-radius: 6px;
        width: 100%;
        font-weight: 700;
    }
    div.stButton > button:hover {
        background-color: #2E6B4F;
        color: white;
        border-color: #2E6B4F;
    }
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E5E2D8;
        border-radius: 8px;
        padding: 14px 16px;
    }
</style>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">财报智析 Agent</div>
            <div class="hero-subtitle">基于财务报表分析教材框架的上市公司财务报表智能分析系统</div>
            <div class="hero-desc">
                支持直接上传年度报告 PDF/Word 抽取财务报表数据，也支持上传标准 Excel/CSV。
                系统先生成可预览的标准 CSV，确认后再由 Agent 调用指标计算、趋势分析、
                杜邦分析、现金流量质量分析和风险识别工具，生成标准化财务分析报告。
            </div>
            <span class="tag">smolagents</span>
            <span class="tag">财务报表分析</span>
            <span class="tag">教材框架</span>
            <span class="tag">风险识别</span>
            <span class="tag">自动报告生成</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def workflow_template() -> pd.DataFrame:
    return pd.DataFrame(
        [
            [1, "llm_model", "加载大模型 API", "待执行", ""],
            [2, "main_agent", "模型驱动工具调度", "待执行", ""],
            [3, "file_loader", "读取标准财务数据 CSV/Excel", "待执行", ""],
            [4, "pdf_parser", "解析年度报告 PDF", "待执行/可跳过", ""],
            [5, "data_cleaner", "标准化财务报表项目", "待执行", ""],
            [6, "data_validator", "校验数据完整性与勾稽关系", "待执行", ""],
            [7, "ratio_calculator", "计算财务指标", "待执行", ""],
            [8, "trend_analyzer", "分析多年度趋势", "待执行", ""],
            [9, "dupont_analyzer", "执行杜邦分析", "待执行", ""],
            [10, "cashflow_analyzer", "分析现金流量质量", "待执行", ""],
            [11, "risk_detector", "识别异常风险", "待执行", ""],
            [12, "chart_generator", "生成可视化图表", "待执行", ""],
            [13, "report_generator", "生成标准化报告", "待执行", ""],
        ],
        columns=["步骤", "工具模块", "执行动作", "状态", "输出摘要"],
    )


def default_page() -> None:
    st.markdown('<div class="card"><h3>系统工作逻辑</h3>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="flow">
            <div class="flow-step">年报/标准数据输入</div><span>→</span>
            <div class="flow-step">读取并生成标准 CSV</div><span>→</span>
            <div class="flow-step">用户确认数据</div><span>→</span>
            <div class="flow-step">Agent 分析</div><span>→</span>
            <div class="flow-step">指标计算</div><span>→</span>
            <div class="flow-step">风险识别</div><span>→</span>
            <div class="flow-step">报告生成</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.05, 1])
    with col1:
        st.markdown('<div class="card"><h3>标准 CSV/Excel 输入格式</h3>', unsafe_allow_html=True)
        sample = pd.DataFrame(
            {
                "项目": ["营业收入", "营业成本", "净利润", "经营活动现金流量净额", "总资产", "总负债", "所有者权益"],
                "2022": ["", "", "", "", "", "", ""],
                "2023": ["", "", "", "", "", "", ""],
                "2024": ["", "", "", "", "", "", ""],
            }
        )
        st.table(sample)
        st.caption("如果只上传 PDF/Word 年报，系统会尽量从其中的财务报表表格抽取并生成同格式标准 CSV。")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><h3>Agent 工作流执行状态</h3>', unsafe_allow_html=True)
        st.dataframe(workflow_template(), hide_index=True, width="stretch")
        st.caption("以上流程由主控 Agent 根据用户输入自动调度执行。")
        st.markdown("</div>", unsafe_allow_html=True)


def render_trace(trace: list[dict]) -> None:
    table = trace_dataframe(trace)
    if table.empty:
        st.info("暂无 Agent 调用记录。")
        return
    st.dataframe(table, hide_index=True, width="stretch")


def trace_dataframe(trace: list[dict]) -> pd.DataFrame:
    table = pd.DataFrame(trace)
    if table.empty:
        return table
    rename = {
        "order": "调用顺序",
        "tool_name": "工具名称",
        "action": "执行动作",
        "input_summary": "输入摘要",
        "output_summary": "输出摘要",
        "status": "状态",
        "elapsed_seconds": "耗时",
        "error": "错误",
    }
    renamed = table.rename(columns=rename)
    columns = [label for label in rename.values() if label in renamed.columns]
    return renamed[columns]


def completed_trace_count(trace: list[dict]) -> int:
    return sum(1 for row in trace if row.get("status") in {"完成", "跳过", "失败"})


def get_financial_analysis_runner():
    # Streamlit reruns app.py but can keep imported project modules in memory.
    # Reload the Agent module before analysis so UI and backend signatures stay in sync.
    global main_agent_module
    main_agent_module = importlib.reload(main_agent_module)
    return main_agent_module.run_financial_analysis


def upload_signature(*files: Any) -> str:
    parts = []
    for file in files:
        if file is not None:
            parts.append(f"{file.name}:{getattr(file, 'size', 0)}")
    return "|".join(parts)


def prepared_data_ready(signature: str) -> bool:
    info = st.session_state.get("prepared_data_info")
    if not info or not signature:
        return False
    csv_path_value = info.get("csv_path", "")
    if not csv_path_value:
        return False
    csv_path = Path(csv_path_value)
    return info.get("input_signature") == signature and csv_path.exists()


def _standard_data_payload(
    *,
    dataframe: pd.DataFrame,
    source_type: str,
    source_path: Path,
    report_path: Path | None,
    warnings: list[str],
    input_signature: str,
) -> dict[str, Any]:
    PATHS.tables_dir.mkdir(parents=True, exist_ok=True)
    csv_path = PATHS.tables_dir / "prepared_financial_data.csv"
    xlsx_path = PATHS.tables_dir / "prepared_financial_data.xlsx"
    dataframe.to_csv(csv_path, index=False, encoding="utf-8-sig")
    dataframe.to_excel(xlsx_path, index=False)

    cleaned = clean_financial_data(dataframe)
    years = [int(year) for year in cleaned.years]
    final_warnings = [*warnings, *cleaned.warnings]

    return {
        "source_type": source_type,
        "source_path": str(source_path),
        "report_path": str(report_path) if report_path else "",
        "csv_path": str(csv_path),
        "xlsx_path": str(xlsx_path),
        "dataframe": dataframe,
        "items_extracted": len(cleaned.data.index),
        "years": years,
        "warnings": final_warnings,
        "coverage_ratio": round(len(set(cleaned.data.index) & set(REQUIRED_CORE_ITEMS)) / len(REQUIRED_CORE_ITEMS), 4),
        "missing_core_items": cleaned.missing_core_items,
        "input_signature": input_signature,
    }


def prepare_financial_data(structured_file: Any, report_file: Any, input_signature: str) -> dict[str, Any]:
    if not structured_file and not report_file:
        raise ValueError("请先上传标准 Excel/CSV，或上传年度报告 PDF/Word。")

    report_path = None
    if report_file is not None:
        report_path = save_uploaded_file(report_file, PATHS.uploads_dir / report_file.name)

    if structured_file is not None:
        source_path = save_uploaded_file(structured_file, PATHS.uploads_dir / structured_file.name)
        dataframe = load_financial_table(source_path)
        return _standard_data_payload(
            dataframe=dataframe,
            source_type="用户上传的标准财务数据",
            source_path=source_path,
            report_path=report_path,
            warnings=[],
            input_signature=input_signature,
        )

    if report_path is None:
        raise ValueError("未找到可读取的年报文件。")

    extracted = extract_financial_data_from_report(report_path, PATHS.tables_dir)
    return {
        "source_type": "从年度报告自动抽取",
        "source_path": str(extracted["source_path"]),
        "report_path": str(extracted["source_path"]),
        "csv_path": str(extracted["csv_path"]),
        "xlsx_path": str(extracted["xlsx_path"]),
        "audit_path": str(extracted.get("audit_path", "")),
        "dataframe": extracted["dataframe"],
        "items_extracted": int(extracted["items_extracted"]),
        "years": extracted["years"],
        "warnings": extracted["warnings"],
        "rows_scanned": int(extracted["rows_scanned"]),
        "pages_total": extracted.get("pages_total"),
        "pages_scanned": extracted.get("pages_scanned"),
        "tables_found": extracted.get("tables_found"),
        "table_rows": extracted.get("table_rows"),
        "text_lines": extracted.get("text_lines"),
        "coverage_ratio": extracted.get("coverage_ratio"),
        "missing_core_items": extracted.get("missing_core_items", []),
        "evidence": extracted.get("evidence", {}),
        "report_year": extracted.get("report_year"),
        "input_signature": input_signature,
    }


def render_prepared_data(info: dict[str, Any] | None) -> None:
    if not info:
        return

    st.markdown('<div class="card"><h3>数据读取结果</h3>', unsafe_allow_html=True)
    cols = st.columns(5)
    cols[0].metric("数据来源", info.get("source_type", ""))
    cols[1].metric("识别科目", f"{info.get('items_extracted', 0)} 个")
    cols[2].metric("识别年度", "、".join(str(year) for year in info.get("years", [])) or "未识别")
    coverage = info.get("coverage_ratio")
    cols[3].metric("核心科目覆盖率", f"{float(coverage):.0%}" if coverage is not None else "已校验")
    pages_scanned = info.get("pages_scanned")
    cols[4].metric("扫描页数", str(pages_scanned) if pages_scanned else "结构化输入")

    source_path_value = info.get("source_path", "")
    source_name = Path(source_path_value).name if source_path_value else "未识别来源"
    st.caption(f"当前标准数据来源：{source_name}。请先核对下方数据，再点击左侧“开始分析”。")
    warnings = [warning for warning in info.get("warnings", []) if warning]
    if warnings:
        st.warning("；".join(dict.fromkeys(warnings)))

    detail_items = []
    for label, key in [
        ("识别报告年度", "report_year"),
        ("PDF 总页数", "pages_total"),
        ("已扫描页数", "pages_scanned"),
        ("识别表格数", "tables_found"),
        ("表格行数", "table_rows"),
        ("文本行数", "text_lines"),
        ("候选行数", "rows_scanned"),
    ]:
        value = info.get(key)
        if value is not None:
            detail_items.append(f"**{label}**：{value}")
    missing_core_items = info.get("missing_core_items") or []
    if missing_core_items:
        detail_items.append(f"**缺失核心科目**：{'、'.join(str(item) for item in missing_core_items)}")
    if detail_items or info.get("evidence"):
        with st.expander("查看读取质量与证据", expanded=False):
            if detail_items:
                st.markdown("\n\n".join(detail_items))
            evidence = info.get("evidence") or {}
            if evidence:
                evidence_rows = []
                for item_name, years in evidence.items():
                    for year, detail in years.items():
                        evidence_rows.append(
                            {
                                "项目": item_name,
                                "年份": year,
                                "页码": detail.get("page"),
                                "来源": detail.get("source"),
                                "置信分": detail.get("score"),
                                "原始行": detail.get("row_text"),
                            }
                        )
                if evidence_rows:
                    st.dataframe(pd.DataFrame(evidence_rows), hide_index=True, width="stretch")

    dataframe = info.get("dataframe")
    if isinstance(dataframe, pd.DataFrame):
        st.dataframe(dataframe, hide_index=True, width="stretch")

    download_cols = st.columns(2)
    for col, label, key, mime in [
        (download_cols[0], "下载标准 CSV", "csv_path", "text/csv"),
        (
            download_cols[1],
            "下载标准 Excel",
            "xlsx_path",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
    ]:
        path_value = info.get(key, "")
        path = Path(path_value) if path_value else None
        if path and path.exists():
            with path.open("rb") as f:
                col.download_button(label, f, file_name=path.name, mime=mime, width="stretch")
    audit_path_value = info.get("audit_path", "")
    audit_path = Path(audit_path_value) if audit_path_value else None
    if audit_path and audit_path.exists():
        with audit_path.open("rb") as f:
            st.download_button("下载读取证据 JSON", f, file_name=audit_path.name, mime="application/json", width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)


def display_dupont_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    renamed = df.rename(
        columns={
            "year": "年份",
            "net_margin": "净利率",
            "total_asset_turnover": "总资产周转率",
            "equity_multiplier": "权益乘数",
            "roe": "净资产收益率（ROE）",
        }
    ).copy()
    for col in ["净利率", "净资产收益率（ROE）"]:
        if col in renamed.columns:
            renamed[col] = renamed[col].map(lambda x: "" if pd.isna(x) else f"{x:.2%}")
    for col in ["总资产周转率", "权益乘数"]:
        if col in renamed.columns:
            renamed[col] = renamed[col].map(lambda x: "" if pd.isna(x) else f"{x:.2f}")
    return renamed


def display_cashflow_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    renamed = df.rename(
        columns={
            "year": "年份",
            "net_profit": "净利润",
            "net_operating_cash_flow": "经营活动现金流量净额",
            "ocf_to_net_profit": "净利润现金含量",
            "sales_cash_ratio": "销售收现比率",
            "evaluation": "现金流量质量评价",
        }
    ).copy()
    for col in ["净利润", "经营活动现金流量净额"]:
        if col in renamed.columns:
            renamed[col] = renamed[col].map(lambda x: "" if pd.isna(x) else f"{x:,.2f}")
    for col in ["净利润现金含量", "销售收现比率"]:
        if col in renamed.columns:
            renamed[col] = renamed[col].map(lambda x: "" if pd.isna(x) else f"{x:.2%}")
    return renamed


def render_risks(risks: list[dict[str, str]]) -> None:
    if not risks:
        st.success("未触发内置风险规则。")
        return
    for risk in risks:
        level = risk.get("risk_level", "")
        css = "risk-high" if level == "高" else "risk-mid" if level == "中" else "risk-low"
        display_level = {"高": "高风险", "中": "中风险", "低": "低风险"}.get(level, level)
        st.markdown(
            f"""
            <div class="risk-card {css}">
                <b>风险名称：</b>{risk.get("risk_name", "")}<br>
                <b>风险等级：</b>{display_level}<br>
                <b>触发依据：</b>{risk.get("evidence", "")}<br>
                <b>会计解释：</b>{risk.get("explanation", "")}<br>
                <b>改进建议：</b>{risk.get("suggestion", "")}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_downloads(result: dict) -> None:
    st.sidebar.markdown("### 四、下载结果")
    report = result.get("report", {})
    downloads = [
        ("下载 Markdown 报告", report.get("markdown_path"), "text/markdown"),
        ("下载 Word 报告", report.get("word_path"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        ("下载指标 Excel", PATHS.tables_dir / "ratio_results.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("下载数据校验表", PATHS.tables_dir / "data_validation.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("下载 Agent 调用记录", result.get("trace_path"), "application/json"),
    ]
    for label, path, mime in downloads:
        if path and Path(path).exists():
            with Path(path).open("rb") as f:
                st.sidebar.download_button(label, f, file_name=Path(path).name, mime=mime, width="stretch")


def render_results(result: dict) -> None:
    st.markdown('<div class="card"><h3>Agent 工作流执行状态</h3>', unsafe_allow_html=True)
    render_trace(result["trace"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("核心财务指标概览")
    metrics = result["core_metrics"]
    cols = st.columns(6)
    for col, (name, value) in zip(cols, metrics.items()):
        col.metric(name, value)

    st.subheader("财务趋势可视化")
    charts = result["charts"]["figures"]
    chart_tabs = st.tabs(["经营成果趋势", "盈利能力趋势", "偿债能力趋势", "杜邦分析", "风险分布"])
    for tab, key in zip(chart_tabs, ["operating_trend", "profitability_trend", "solvency_trend", "dupont_trend", "risk_distribution"]):
        with tab:
            st.plotly_chart(charts[key], width="stretch")

    tabs = st.tabs(["数据校验", "财务指标表", "趋势分析", "杜邦分析", "现金流量质量", "风险识别", "生成报告", "Agent 调用记录"])
    with tabs[0]:
        validation = result.get("validation", {})
        st.caption("本表用于核查核心科目完整性、资产负债表勾稽关系和利润现金流匹配性。")
        st.info(validation.get("summary", "暂无数据校验摘要。"))
        detail_table = validation.get("detail_table")
        if isinstance(detail_table, pd.DataFrame):
            st.dataframe(detail_table, hide_index=True, width="stretch")
        else:
            st.dataframe(pd.DataFrame(validation.get("details", [])), hide_index=True, width="stretch")
    with tabs[1]:
        st.caption("本表基于已确认的标准财务数据自动计算，公式来源于财务报表分析教材框架。")
        st.dataframe(result["ratio_pivot"], hide_index=True, width="stretch")
    with tabs[2]:
        st.dataframe(result["trend_summary"], hide_index=True, width="stretch")
    with tabs[3]:
        st.markdown("**净资产收益率（ROE） = 净利率 × 总资产周转率 × 权益乘数**")
        st.dataframe(display_dupont_table(result["dupont"]["dupont_table"]), hide_index=True, width="stretch")
        st.info(result["dupont"].get("dupont_summary", "暂无杜邦分析结论。"))
    with tabs[4]:
        st.dataframe(display_cashflow_table(result["cashflow"]["cashflow_table"]), hide_index=True, width="stretch")
        st.info(f"现金流量质量评价：{result['cashflow'].get('cashflow_quality')}。{result['cashflow'].get('cashflow_summary')}")
    with tabs[5]:
        render_risks(result["risks"])
    with tabs[6]:
        st.markdown(result["report"]["markdown"])
    with tabs[7]:
        render_trace(result["trace"])


def sidebar_model_config() -> ModelConfig:
    base_config = load_model_config()
    st.sidebar.markdown("### 模型 API 配置")
    enable_llm = st.sidebar.checkbox("启用大模型 API", value=base_config.enable_llm)
    api_base = st.sidebar.text_input("API Base URL", value=base_config.api_base)
    model_id = st.sidebar.text_input("模型名称", value=base_config.model_id)
    api_key_env = st.sidebar.text_input("环境变量名", value=base_config.api_key_env)
    api_key_input = st.sidebar.text_input(
        "API Key",
        value="",
        type="password",
        placeholder="可直接粘贴 API Key；留空则读取环境变量",
    )

    with st.sidebar.expander("高级参数", expanded=False):
        temperature = st.slider("temperature", 0.0, 1.0, float(base_config.temperature), 0.05)
        max_tokens = st.number_input("max_tokens", min_value=512, max_value=32000, value=int(base_config.max_tokens), step=512)
        timeout = st.number_input("timeout 秒", min_value=10, max_value=600, value=int(base_config.timeout), step=10)
        reasoning_effort = st.selectbox(
            "reasoning_effort",
            ["low", "medium", "high"],
            index=["low", "medium", "high"].index(base_config.reasoning_effort)
            if base_config.reasoning_effort in {"low", "medium", "high"}
            else 1,
        )

    model_config = ModelConfig(
        provider=base_config.provider,
        api_base=api_base.strip() or base_config.api_base,
        model_id=model_id.strip() or base_config.model_id,
        api_key_env=api_key_env.strip() or base_config.api_key_env,
        temperature=float(temperature),
        max_tokens=int(max_tokens),
        timeout=int(timeout),
        reasoning_effort=reasoning_effort,
        enable_llm=enable_llm,
        api_key_override=api_key_input.strip() or None,
    )

    st.sidebar.caption("页面输入的 API Key 仅本次会话使用，不会写入本地文件。")
    st.sidebar.write(f"当前模型：`{model_config.model_id}`")
    st.sidebar.write(f"API Key：{model_config.masked_key_status}")
    smolagents_available = importlib.util.find_spec("smolagents") is not None
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if smolagents_available:
        st.sidebar.write("smolagents：已安装")
    else:
        st.sidebar.write(f"smolagents：未安装（当前 Python {py_version}）")
    if not enable_llm:
        st.sidebar.info("已关闭大模型 API，将使用 Python fallback pipeline 完成演示。")
    elif model_config.api_key and not model_config.api_key_is_ascii:
        st.sidebar.error("API Key 不能包含中文或空格占位文本，请粘贴平台提供的真实 key。")
    elif not model_config.is_configured:
        st.sidebar.warning(f"未填写 API Key，也未读取到环境变量 `{model_config.api_key_env}`。")
    elif not smolagents_available:
        st.sidebar.warning("API 已配置；当前仅缺少本地 smolagents 包，报告生成仍会调用大模型。")
    else:
        st.sidebar.success("大模型 API 已配置。")
    return model_config


def sidebar_controls() -> tuple:
    st.sidebar.title("财报智析 Agent")
    model_config = sidebar_model_config()

    st.sidebar.markdown("### 一、读取数据")
    structured_file = st.sidebar.file_uploader("上传标准财务数据 Excel/CSV（可选）", type=["xlsx", "xls", "csv"])
    report_file = st.sidebar.file_uploader("上传年度报告 PDF/Word", type=["pdf", "docx"])
    current_signature = upload_signature(structured_file, report_file)
    has_input = bool(current_signature)
    data_ready = prepared_data_ready(current_signature)
    prepare = st.sidebar.button("读取数据并生成标准 CSV", width="stretch", disabled=not has_input)
    if data_ready:
        st.sidebar.success("标准 CSV 已生成，可开始分析。")
    elif has_input:
        st.sidebar.info("请先点击“读取数据并生成标准 CSV”，核对数据后再分析。")
    else:
        st.sidebar.caption("可直接上传 PDF/docx 年报抽取财务数据；也可上传已整理好的 Excel/CSV。单个上传文件上限为 1GB。")

    st.sidebar.markdown("### 二、选择分析模块")
    modules = []
    groups = {
        "报表分析": ["资产负债表分析", "利润表分析", "现金流量表分析"],
        "指标分析": ["偿债能力分析", "营运能力分析", "盈利能力分析", "成长能力分析"],
        "综合分析": ["杜邦分析", "现金流量质量分析", "异常风险识别"],
    }
    for group, names in groups.items():
        st.sidebar.markdown(f"**{group}**")
        for name in names:
            if st.sidebar.checkbox(name, value=True):
                modules.append(name)

    st.sidebar.markdown("### 三、报告设置")
    report_level = st.sidebar.radio("报告详细程度", ["简版", "标准版", "详细版"], index=1)
    enable_pdf = st.sidebar.checkbox("启用 PDF 文本分析", value=True)
    generate_word = st.sidebar.checkbox("生成 Word 报告", value=True)
    show_trace = st.sidebar.checkbox("展示 Agent 调用过程", value=True)
    start = st.sidebar.button("开始分析", width="stretch", disabled=not data_ready)
    st.sidebar.caption("请先完成数据读取。分析过程包括指标计算、趋势分析、风险识别和报告生成，可能需要数十秒。")
    return (
        structured_file,
        report_file,
        modules,
        report_level,
        enable_pdf,
        generate_word,
        show_trace,
        prepare,
        start,
        model_config,
        current_signature,
    )


def main() -> None:
    PATHS.ensure()
    render_hero()
    (
        structured_file,
        report_file,
        modules,
        report_level,
        enable_pdf,
        generate_word,
        show_trace,
        prepare,
        start,
        model_config,
        current_signature,
    ) = sidebar_controls()

    if prepare:
        try:
            with st.status("正在读取年报/结构化数据，并生成标准 CSV……", expanded=True) as status:
                st.write("当前步骤：保存上传文件")
                st.write("当前步骤：识别财务报表表格与标准科目")
                prepared_info = prepare_financial_data(structured_file, report_file, current_signature)
                st.session_state["prepared_data_info"] = prepared_info
                st.session_state.pop("analysis_result", None)
                status.update(label="数据读取完成，已生成标准 CSV", state="complete", expanded=False)
            st.rerun()
        except Exception as exc:
            st.error(f"数据读取失败：{exc}")
            default_page()
            return

    if "analysis_result" in st.session_state:
        render_downloads(st.session_state["analysis_result"])

    prepared_info = st.session_state.get("prepared_data_info")
    if prepared_info and prepared_info.get("input_signature") == current_signature:
        render_prepared_data(prepared_info)

    if not start:
        if "analysis_result" in st.session_state:
            render_results(st.session_state["analysis_result"])
        else:
            default_page()
        return

    if not prepared_data_ready(current_signature):
        st.error("请先点击“读取数据并生成标准 CSV”，核对数据后再开始分析。")
        default_page()
        return

    prepared_info = st.session_state["prepared_data_info"]
    excel_path = Path(prepared_info["csv_path"])
    report_path_text = prepared_info.get("report_path") or ""
    report_path = Path(report_path_text) if report_path_text else None
    pdf_path = report_path if report_path and report_path.suffix.lower() == ".pdf" else None

    with st.status("Agent 正在执行财务分析工具链……", expanded=True) as status:
        st.write("当前步骤：读取已确认的标准 CSV")
        live_title = st.empty()
        live_detail = st.empty()
        live_progress = st.progress(0, text="准备调用 Agent 工具链")
        live_table = st.empty()

        def update_live_trace(event: dict, rows: list[dict]) -> None:
            trace = event.get("trace", {})
            done = completed_trace_count(rows)
            total = 13
            progress_value = min(done / total, 1.0)
            tool_name = trace.get("tool_name", "")
            action = trace.get("action", "")
            state = trace.get("status", "")
            live_title.markdown(f"**当前 Agent 步骤：{trace.get('order', '-')}/{total} · {tool_name} · {state}**")
            live_detail.info(
                f"正在执行：{action}\n\n"
                f"输入摘要：{trace.get('input_summary') or '无'}\n\n"
                f"输出摘要：{trace.get('output_summary') or '处理中...'}"
            )
            live_progress.progress(progress_value, text=f"Agent 工具链进度：{done}/{total}")
            live_table.dataframe(trace_dataframe(rows), hide_index=True, width="stretch")
            if state == "失败":
                status.update(label=f"Agent 执行失败：{tool_name}", state="error", expanded=True)
            else:
                status.update(label=f"Agent 正在执行：{tool_name}", state="running", expanded=True)

        st.write("当前步骤：调用主控 Agent")
        run_financial_analysis = get_financial_analysis_runner()
        result = run_financial_analysis(
            excel_path=excel_path,
            pdf_path=pdf_path,
            modules=modules,
            report_level=report_level,
            enable_pdf=enable_pdf,
            generate_word=generate_word,
            model_config_override=model_config,
            trace_callback=update_live_trace,
        )
        st.session_state["analysis_result"] = result
        live_progress.progress(1.0, text="Agent 工具链进度：13/13")
        live_title.markdown("**当前 Agent 步骤：全部完成**")
        live_detail.success("指标计算、风险识别、图表生成和报告导出已完成。")
        live_table.dataframe(trace_dataframe(result["trace"]), hide_index=True, width="stretch")
        status.update(label="分析完成", state="complete", expanded=False)

    render_downloads(result)
    render_results(result)


if __name__ == "__main__":
    main()
