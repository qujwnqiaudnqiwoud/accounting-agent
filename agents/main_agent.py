from __future__ import annotations

import importlib.util
import json
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from config.settings import PATHS, ModelConfig, load_model_config
from schemas.financial_schema import AnalysisOptions, ToolTrace
from tools.cashflow_analyzer import analyze_cashflow_quality
from tools.chart_generator import generate_charts
from tools.data_cleaner import clean_financial_data
from tools.data_validator import validate_financial_data
from tools.dupont_analyzer import analyze_dupont
from tools.file_loader import load_financial_table
from tools.knowledge_loader import ensure_knowledge_files
from tools.llm_client import generate_agent_plan
from tools.pdf_parser import parse_annual_report
from tools.ratio_calculator import calculate_ratios, pivot_ratio_table
from tools.report_generator import generate_report
from tools.risk_detector import detect_risks
from tools.trend_analyzer import analyze_trends


TraceCallback = Callable[[dict[str, Any], list[dict[str, Any]]], None]


class TraceRecorder:
    def __init__(self, callback: TraceCallback | None = None) -> None:
        self.records: list[ToolTrace] = []
        self._order = 0
        self.callback = callback

    def _emit(self, event_name: str, trace: ToolTrace, rows: list[dict[str, Any]] | None = None) -> None:
        if not self.callback:
            return
        event = {"event": event_name, "trace": trace.to_dict()}
        try:
            self.callback(event, rows if rows is not None else self.to_dicts())
        except Exception:
            pass

    @contextmanager
    def step(self, tool_name: str, action: str, input_summary: str = ""):
        self._order += 1
        trace = ToolTrace(order=self._order, tool_name=tool_name, action=action, input_summary=input_summary, status="运行中")
        start = time.perf_counter()
        self._emit("start", trace, self.to_dicts() + [trace.to_dict()])
        try:
            yield trace
            trace.status = "完成"
        except Exception as exc:
            trace.status = "失败"
            trace.error = str(exc)
            raise
        finally:
            trace.elapsed_seconds = round(time.perf_counter() - start, 3)
            self.records.append(trace)
            self._emit("finish", trace, self.to_dicts())

    def add_skip(self, tool_name: str, action: str, reason: str) -> None:
        self._order += 1
        trace = ToolTrace(self._order, tool_name, action, output_summary=reason, status="跳过")
        self.records.append(trace)
        self._emit("skip", trace, self.to_dicts())

    def to_dicts(self) -> list[dict[str, Any]]:
        return [record.to_dict() for record in self.records]

    def save(self, path: Path | None = None) -> Path:
        out = path or PATHS.trace_path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(self.to_dicts(), ensure_ascii=False, indent=2), encoding="utf-8")
        return out


def _try_create_smolagents_model(model_config: ModelConfig) -> tuple[bool, str]:
    if not model_config.is_configured:
        if model_config.api_key and not model_config.api_key_is_ascii:
            return False, "API Key 格式异常：请粘贴真实 API Key，不要使用“你的key”等中文占位文本。"
        return False, f"未配置 {model_config.api_key_env}，将使用 Python fallback pipeline。"
    if importlib.util.find_spec("smolagents") is None:
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        return (
            False,
            "API Key 已配置；但当前 Python 环境未安装 smolagents，"
            f"正在使用 OpenAI-compatible API 生成计划/报告，并用 fallback pipeline 执行工具调度。当前 Python：{py_version}。"
            "如需启用 smolagents 主控 Agent，请使用 Python 3.10+ 重建虚拟环境后重新安装依赖。",
        )
    try:
        from smolagents import OpenAIModel

        _ = OpenAIModel(
            model_id=model_config.model_id,
            api_base=model_config.api_base,
            api_key=model_config.api_key,
            temperature=model_config.temperature,
            max_tokens=model_config.max_tokens,
        )
        return True, f"已初始化 smolagents OpenAIModel：{model_config.model_id}"
    except Exception as exc:
        return False, f"smolagents 模型初始化失败，将使用 fallback pipeline：{exc}"


def _run_smolagents_planner(model_config: ModelConfig) -> str | None:
    if not model_config.is_configured or importlib.util.find_spec("smolagents") is None:
        return None
    try:
        from smolagents import OpenAIModel, ToolCallingAgent, tool

        @tool
        def list_financial_analysis_tools() -> str:
            """List deterministic accounting analysis tools available to the agent."""
            return (
                "file_loader -> data_cleaner -> data_validator -> ratio_calculator -> "
                "trend_analyzer -> dupont_analyzer -> cashflow_analyzer -> risk_detector -> "
                "chart_generator -> report_generator"
            )

        @tool
        def approve_financial_workflow(task: str) -> str:
            """Approve the controlled workflow for this financial analysis task.

            Args:
                task: A short description of the user's financial analysis task.
            """
            return (
                f"已批准任务：{task}。财务数字由确定性 Python 工具计算；"
                "模型只负责规划、解释和报告组织，不新增未计算数字。"
            )

        model = OpenAIModel(
            model_id=model_config.model_id,
            api_base=model_config.api_base,
            api_key=model_config.api_key,
            temperature=model_config.temperature,
            max_tokens=min(model_config.max_tokens, 1200),
        )
        agent = ToolCallingAgent(
            tools=[list_financial_analysis_tools, approve_financial_workflow],
            model=model,
            max_steps=3,
            verbosity_level=0,
        )
        result = agent.run(
            "请调用工具确认本次财报分析的工具链顺序。只输出简短中文计划，不生成财务结论。"
        )
        return str(result)
    except Exception as exc:
        return f"SMOLAGENTS_AGENT_ERROR: {exc}"


def _core_metric_cards(ratio_df: pd.DataFrame, risks: list[dict[str, str]]) -> dict[str, str]:
    def latest(name: str, percent: bool | None = None) -> str:
        part = ratio_df[(ratio_df["指标名称"] == name) & ratio_df["指标值"].notna()].sort_values("年份")
        if part.empty:
            return "数据缺失"
        row = part.iloc[-1]
        is_percent = bool(row["是否百分比"]) if percent is None else percent
        value = float(row["指标值"])
        return f"{value:.2%}" if is_percent else f"{value:.2f}"

    return {
        "营业收入增长率": latest("营业收入增长率"),
        "净利润增长率": latest("净利润增长率"),
        "资产负债率": latest("资产负债率"),
        "净资产收益率（ROE）": latest("净资产收益率（ROE）"),
        "净利润现金含量": latest("净利润现金含量"),
        "风险提示数量": str(len(risks)),
    }


def run_financial_analysis(
    excel_path: str | Path,
    pdf_path: str | Path | None = None,
    modules: list[str] | None = None,
    report_level: str = "标准版",
    enable_pdf: bool = False,
    generate_word: bool = True,
    model_config_path: str | Path | None = None,
    model_config_override: ModelConfig | None = None,
    trace_callback: TraceCallback | None = None,
) -> dict[str, Any]:
    PATHS.ensure()
    options = AnalysisOptions(modules=modules or [], report_level=report_level, enable_pdf=enable_pdf, generate_word=generate_word)
    model_config = model_config_override or load_model_config(model_config_path)
    ensure_knowledge_files()
    trace = TraceRecorder(trace_callback)

    with trace.step("llm_model", "加载大模型 API 配置", f"{model_config.provider}/{model_config.model_id}") as item:
        smol_ready, message = _try_create_smolagents_model(model_config)
        item.output_summary = message

    with trace.step("main_agent", "smolagents 主控 Agent 规划工具调度", "标准财务数据 + 可选 PDF") as item:
        if model_config.is_configured:
            plan = _run_smolagents_planner(model_config)
            if not plan or plan.startswith("SMOLAGENTS_AGENT_ERROR"):
                fallback_plan = generate_agent_plan(model_config, "读取标准财务数据，解析 PDF，计算指标，识别风险，生成财务分析报告。")
                item.output_summary = (fallback_plan or plan or "模型计划生成失败，使用受控工具链。")[:500]
            else:
                item.output_summary = plan[:500]
        elif model_config.api_key and not model_config.api_key_is_ascii:
            item.output_summary = "API Key 格式异常，已跳过模型计划生成，使用固定工具链完成分析。"
        else:
            item.output_summary = "未配置 API Key，使用固定工具链完成分析。"

    with trace.step("file_loader", "读取标准财务数据 CSV/Excel", str(excel_path)) as item:
        raw_df = load_financial_table(excel_path)
        item.output_summary = f"读取 {raw_df.shape[0]} 行、{raw_df.shape[1]} 列。"

    if enable_pdf and pdf_path:
        with trace.step("pdf_parser", "解析年度报告 PDF", str(pdf_path)) as item:
            pdf_info = parse_annual_report(pdf_path)
            item.output_summary = pdf_info.get("message") or pdf_info.get("company_name", "PDF 解析完成")
    else:
        pdf_info = parse_annual_report(None)
        trace.add_skip("pdf_parser", "解析年度报告 PDF", "未启用或未上传 PDF。")

    with trace.step("data_cleaner", "标准化财务报表项目", "识别宽表/长表和中文科目") as item:
        cleaned = clean_financial_data(raw_df)
        item.output_summary = f"识别 {len(cleaned.data.index)} 个标准科目、{len(cleaned.years)} 个年度。"

    with trace.step("data_validator", "校验数据完整性与勾稽关系", "核心科目 + 资产负债表等式 + 利润现金流匹配") as item:
        validation_result = validate_financial_data(cleaned.data)
        item.output_summary = validation_result["summary"]

    with trace.step("ratio_calculator", "计算财务指标", "偿债、营运、盈利、成长、现金流量质量") as item:
        ratio_df = calculate_ratios(cleaned.data, PATHS.tables_dir / "ratio_results.xlsx")
        item.output_summary = f"生成 {len(ratio_df)} 条指标记录。"

    with trace.step("trend_analyzer", "分析多年度趋势", "财务项目和核心指标") as item:
        trend_df = analyze_trends(cleaned.data, ratio_df)
        item.output_summary = f"生成 {len(trend_df)} 条趋势判断。"

    with trace.step("dupont_analyzer", "执行杜邦分析", "净资产收益率（ROE）= 净利率 × 总资产周转率 × 权益乘数") as item:
        dupont_result = analyze_dupont(ratio_df)
        item.output_summary = dupont_result.get("dupont_summary", "")

    with trace.step("cashflow_analyzer", "分析现金流量质量", "经营活动现金流量净额与净利润匹配") as item:
        cashflow_result = analyze_cashflow_quality(cleaned.data)
        item.output_summary = f"现金流量质量评价：{cashflow_result.get('cashflow_quality')}"

    with trace.step("risk_detector", "识别异常风险", "教材规则库 + 内置规则") as item:
        risks = detect_risks(cleaned.data, ratio_df, dupont_result)
        item.output_summary = f"触发 {len(risks)} 条风险提示。"

    with trace.step("chart_generator", "生成可视化图表", "趋势图、杜邦图、风险分布图") as item:
        chart_result = generate_charts(cleaned.data, ratio_df, dupont_result, risks)
        item.output_summary = f"保存 {len(chart_result['paths'])} 个图表 HTML。"

    trace_snapshot = trace.to_dicts()
    with trace.step("report_generator", "生成标准化报告", "Markdown + Word") as item:
        report_result = generate_report(
            cleaned.data,
            ratio_df,
            trend_df,
            dupont_result,
            cashflow_result,
            risks,
            validation_result,
            trace_snapshot,
            pdf_info,
            model_config,
            report_level,
            generate_word,
        )
        item.output_summary = f"报告生成完成；LLM 润色：{'是' if report_result.get('used_llm') else '否'}。"

    trace_path = trace.save(PATHS.trace_path)

    return {
        "options": options,
        "model_config": model_config,
        "raw_data": raw_df,
        "cleaned_data": cleaned.data,
        "missing_core_items": cleaned.missing_core_items,
        "warnings": cleaned.warnings,
        "validation": validation_result,
        "ratio_results": ratio_df,
        "ratio_pivot": pivot_ratio_table(ratio_df),
        "trend_summary": trend_df,
        "dupont": dupont_result,
        "cashflow": cashflow_result,
        "risks": risks,
        "charts": chart_result,
        "report": report_result,
        "pdf_info": pdf_info,
        "trace": trace.to_dicts(),
        "trace_path": trace_path,
        "core_metrics": _core_metric_cards(ratio_df, risks),
    }
