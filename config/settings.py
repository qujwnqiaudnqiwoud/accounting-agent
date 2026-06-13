from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ProjectPaths:
    base_dir: Path = BASE_DIR
    knowledge_dir: Path = BASE_DIR / "knowledge"
    data_dir: Path = BASE_DIR / "data"
    outputs_dir: Path = BASE_DIR / "outputs"
    reports_dir: Path = BASE_DIR / "outputs" / "reports"
    charts_dir: Path = BASE_DIR / "outputs" / "charts"
    tables_dir: Path = BASE_DIR / "outputs" / "tables"
    uploads_dir: Path = BASE_DIR / "outputs" / "uploads"
    trace_path: Path = BASE_DIR / "outputs" / "agent_trace.json"

    def ensure(self) -> None:
        for path in [
            self.knowledge_dir,
            self.data_dir,
            self.outputs_dir,
            self.reports_dir,
            self.charts_dir,
            self.tables_dir,
            self.uploads_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)


@dataclass
class ModelConfig:
    provider: str = "openai_compatible"
    api_base: str = "https://api.deepseek.com"
    model_id: str = "deepseek-v4-flash"
    api_key_env: str = "DEEPSEEK_API_KEY"
    temperature: float = 0.25
    max_tokens: int = 4096
    timeout: int = 120
    reasoning_effort: str = "medium"
    enable_llm: bool = True
    api_key_override: str | None = None

    @property
    def api_key(self) -> str | None:
        if self.api_key_override:
            return self.api_key_override.strip()
        return os.getenv(self.api_key_env)

    @property
    def is_configured(self) -> bool:
        return bool(self.enable_llm and self.api_key and self.api_key_is_ascii)

    @property
    def api_key_is_ascii(self) -> bool:
        key = self.api_key
        return not key or key.isascii()

    @property
    def masked_key_status(self) -> str:
        key = self.api_key
        if not key:
            return "未配置"
        if not self.api_key_is_ascii:
            return "格式异常：请粘贴真实 API Key"
        if len(key) <= 8:
            return "已配置"
        return f"已配置（{key[:4]}...{key[-4:]}）"


def _default_config_path() -> Path:
    copied = BASE_DIR / "config" / "model_config.yaml"
    if copied.exists():
        return copied
    return BASE_DIR / "config" / "model_config.example.yaml"


def load_model_config(config_path: str | Path | None = None) -> ModelConfig:
    path = Path(config_path) if config_path else _default_config_path()
    data: dict[str, Any] = {}
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f) or {}
            if isinstance(loaded, dict):
                data = loaded

    env_overrides = {
        "provider": os.getenv("FIN_AGENT_PROVIDER"),
        "api_base": os.getenv("FIN_AGENT_API_BASE"),
        "model_id": os.getenv("FIN_AGENT_MODEL_ID"),
        "api_key_env": os.getenv("FIN_AGENT_API_KEY_ENV"),
    }
    for key, value in env_overrides.items():
        if value:
            data[key] = value

    return ModelConfig(**{k: v for k, v in data.items() if k in ModelConfig.__annotations__})


PATHS = ProjectPaths()
