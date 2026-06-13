from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from config.settings import PATHS


REQUIRED_KNOWLEDGE_FILES = {
    "analysis_framework.md": "# 财务报表分析标准流程\n\n请替换为教材分析框架。\n",
    "ratio_definitions.csv": "category,ratio_name,formula,required_items,meaning,interpretation,warning_logic,notes\n",
    "risk_rules.yaml": "rules: []\n",
    "report_template.md": "# 标准化财务报表分析报告模板\n\n请替换为课程报告模板。\n",
    "agent_workflow.md": "# Agent 工作流说明\n\n请替换为工具调用流程说明。\n",
    "prompt_templates.md": "# 提示词模板\n\n请替换为报告生成提示词。\n",
}


def ensure_knowledge_files(knowledge_dir: Path | None = None) -> list[str]:
    directory = knowledge_dir or PATHS.knowledge_dir
    directory.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    for filename, content in REQUIRED_KNOWLEDGE_FILES.items():
        path = directory / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            created.append(filename)
    return created


def load_text_file(filename: str, knowledge_dir: Path | None = None) -> str:
    ensure_knowledge_files(knowledge_dir)
    path = (knowledge_dir or PATHS.knowledge_dir) / filename
    return path.read_text(encoding="utf-8")


def load_ratio_definitions(knowledge_dir: Path | None = None) -> pd.DataFrame:
    ensure_knowledge_files(knowledge_dir)
    path = (knowledge_dir or PATHS.knowledge_dir) / "ratio_definitions.csv"
    return pd.read_csv(path)


def load_risk_rules(knowledge_dir: Path | None = None) -> dict[str, Any]:
    ensure_knowledge_files(knowledge_dir)
    path = (knowledge_dir or PATHS.knowledge_dir) / "risk_rules.yaml"
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {"rules": []}


def load_knowledge_bundle(knowledge_dir: Path | None = None) -> dict[str, Any]:
    ensure_knowledge_files(knowledge_dir)
    return {
        "analysis_framework": load_text_file("analysis_framework.md", knowledge_dir),
        "report_template": load_text_file("report_template.md", knowledge_dir),
        "prompt_templates": load_text_file("prompt_templates.md", knowledge_dir),
        "agent_workflow": load_text_file("agent_workflow.md", knowledge_dir),
        "ratio_definitions": load_ratio_definitions(knowledge_dir),
        "risk_rules": load_risk_rules(knowledge_dir),
    }
