"""ai_assistant.py 测试（mock LLM，不打网络）。"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_assistant import AIAssistant, AIResult, LLMClient, LLMNotAvailable


def test_llm_client_defaults():
    c = LLMClient()
    assert c.backend == "deepseek"
    assert c.model == "deepseek-chat"


def test_llm_client_chat_raises_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(LLMNotAvailable):
        LLMClient(backend="openai").chat("sys", "user")


def _make_assistant_with_fake_llm(return_value: str) -> AIAssistant:
    fake = MagicMock(spec=LLMClient)
    fake.is_available.return_value = True
    fake.backend = "deepseek"
    fake.chat.return_value = return_value
    return AIAssistant(llm_client=fake)


def test_proofread_calls_llm_and_returns_result():
    a = _make_assistant_with_fake_llm("修正后的文本")
    r = a.proofread("原文 有些 错误的 地方")
    assert isinstance(r, AIResult)
    assert r.action == "proofread"
    assert r.output_text == "修正后的文本"
    assert r.backend == "deepseek"


def test_rewrite_with_tone_in_prompt():
    fake = MagicMock(spec=LLMClient)
    fake.is_available.return_value = True
    fake.backend = "deepseek"
    fake.chat.return_value = "更正式版本"
    a = AIAssistant(llm_client=fake)
    a.rewrite("原文", tone="academic")

    # 检查 system prompt 含 academic 语气标记
    system_arg = fake.chat.call_args[0][0]
    assert "academic" in system_arg.lower()


def test_summarize():
    a = _make_assistant_with_fake_llm("一句话摘要。")
    r = a.summarize("一段很长的文章内容..." * 10)
    assert r.action == "summarize"
    assert r.output_text == "一句话摘要。"


def test_translate_target_lang_in_prompt():
    fake = MagicMock(spec=LLMClient)
    fake.is_available.return_value = True
    fake.backend = "deepseek"
    fake.chat.return_value = "Translated"
    a = AIAssistant(llm_client=fake)
    a.translate("中文原文", target_lang="日本語")

    system_arg = fake.chat.call_args[0][0]
    assert "日本語" in system_arg


def test_expand_returns_expanded_text():
    a = _make_assistant_with_fake_llm("# Title\n\n扩写后的段落...\n")
    r = a.expand("# Title\n- point 1\n- point 2")
    assert r.output_text.startswith("# Title")


def test_empty_text_returns_empty_result_without_calling_llm():
    fake = MagicMock(spec=LLMClient)
    fake.is_available.return_value = True
    fake.backend = "deepseek"
    a = AIAssistant(llm_client=fake)
    r = a.proofread("")
    assert r.output_text == ""
    fake.chat.assert_not_called()    # 空输入不该调 LLM


def test_ai_result_to_dict():
    r = AIResult(action="proofread", input_text="abc",
                 output_text="ABC", backend="deepseek")
    d = r.to_dict()
    assert d["action"] == "proofread"
    assert d["input_chars"] == 3
    assert d["output_chars"] == 3
    assert d["backend"] == "deepseek"


def test_llm_unavailable_when_no_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    a = AIAssistant()
    with pytest.raises(LLMNotAvailable):
        a.proofread("text")


def test_proofread_includes_text_in_user_prompt():
    fake = MagicMock(spec=LLMClient)
    fake.is_available.return_value = True
    fake.backend = "deepseek"
    fake.chat.return_value = "ok"
    AIAssistant(llm_client=fake).proofread("特殊文本标记 XYZ123")

    user_prompt = fake.chat.call_args[0][1]
    assert "XYZ123" in user_prompt
