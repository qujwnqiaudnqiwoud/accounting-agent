from config.settings import ModelConfig


def test_ui_api_key_override_takes_priority(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "env-key")
    config = ModelConfig(api_key_override="ui-key")
    assert config.api_key == "ui-key"
    assert config.is_configured


def test_rejects_chinese_placeholder_api_key():
    config = ModelConfig(api_key_override="你的key")
    assert not config.api_key_is_ascii
    assert not config.is_configured
    assert "格式异常" in config.masked_key_status
