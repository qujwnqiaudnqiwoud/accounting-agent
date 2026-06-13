from pathlib import Path

from agents.main_agent import run_financial_analysis
from config.settings import ModelConfig


def test_trace_callback_receives_live_updates():
    events = []

    def callback(event, rows):
        events.append((event["event"], event["trace"]["tool_name"], event["trace"]["status"], len(rows)))

    result = run_financial_analysis(
        Path("data/sample_financial_data.xlsx"),
        enable_pdf=False,
        generate_word=False,
        model_config_override=ModelConfig(enable_llm=False),
        trace_callback=callback,
    )

    statuses = {status for _, _, status, _ in events}
    assert "运行中" in statuses
    assert "完成" in statuses
    assert any(event == "skip" and tool == "pdf_parser" for event, tool, _, _ in events)
    assert any(tool == "data_validator" for _, tool, _, _ in events)
    assert len(result["trace"]) == 13
