from __future__ import annotations

from typing import Any

from config.settings import ModelConfig


SAFE_SYSTEM_PROMPT = """你是一名谨慎的会计智能体报告撰写助手。
你必须遵守：
1. 只能使用用户提供的结构化计算结果中的数字，不得新增、估算或编造任何财务数字。
2. 风险结论必须使用“提示、可能、需关注、建议进一步核查”等审慎措辞。
3. 不得使用“造假、违规、必然存在问题”等绝对化表述。
4. 报告依据为财务报表分析教材框架、指标计算结果和风险规则。
"""


def call_openai_compatible(
    config: ModelConfig,
    messages: list[dict[str, str]],
    *,
    max_tokens: int | None = None,
) -> str | None:
    if config.api_key and not config.api_key_is_ascii:
        return "LLM_API_ERROR: API Key 格式异常，请粘贴真实 API Key，不要使用中文占位文本。"
    if not config.is_configured:
        return None
    try:
        from openai import OpenAI
    except Exception:
        return None

    client = OpenAI(api_key=config.api_key, base_url=config.api_base, timeout=config.timeout)
    kwargs: dict[str, Any] = {
        "model": config.model_id,
        "messages": messages,
        "temperature": config.temperature,
        "max_tokens": max_tokens or config.max_tokens,
        "stream": False,
    }
    if "deepseek" in config.api_base:
        kwargs["reasoning_effort"] = config.reasoning_effort
    try:
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    except Exception as exc:
        return f"LLM_API_ERROR: {exc}"


def generate_agent_plan(config: ModelConfig, task_summary: str) -> str | None:
    return call_openai_compatible(
        config,
        [
            {"role": "system", "content": SAFE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "请根据以下任务生成一个简短的 Agent 工具调用计划，只列步骤，不生成财务结论。\n"
                    f"{task_summary}"
                ),
            },
        ],
        max_tokens=800,
    )


def polish_report(config: ModelConfig, draft_report: str, source_summary: str) -> str | None:
    response = call_openai_compatible(
        config,
        [
            {"role": "system", "content": SAFE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "请将下面的财务分析报告草稿润色为专业、课堂可展示的中文报告。"
                    "不要新增任何数字，不要删除免责声明，不要改变风险等级。\n\n"
                    f"结构化结果摘要：\n{source_summary}\n\n"
                    f"报告草稿：\n{draft_report}"
                ),
            },
        ],
        max_tokens=config.max_tokens,
    )
    if response and not response.startswith("LLM_API_ERROR"):
        return response
    return None
