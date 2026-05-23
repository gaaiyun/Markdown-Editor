"""AI 写作助手 —— 给 Markdown 编辑器加 5 个 LLM 能力。

5 个能力：

- proofread: 校对（改语法、拼写、标点；保留原意）
- rewrite: 改写（按指定语气重写）
- summarize: 摘要（输出 ≤ 3 句话）
- translate: 翻译（中 ↔ 英为主，可指定目标语言）
- expand: 扩写（基于大纲展开段落）

设计与 stocksight-skill / Smart-Web-Scraper 保持一致：LLMClient 适配
openai / anthropic / deepseek；缺 key 时 raise（不静默 noop，因为 AI
能力是这里的核心）。
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Literal, Optional


log = logging.getLogger(__name__)


LLMBackend = Literal["openai", "anthropic", "deepseek"]
Tone = Literal["formal", "casual", "academic", "concise", "friendly", "professional"]


class LLMNotAvailable(RuntimeError):
    pass


@dataclass(frozen=True)
class AIResult:
    action: str
    input_text: str
    output_text: str
    backend: str

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "input_chars": len(self.input_text),
            "output_chars": len(self.output_text),
            "output_text": self.output_text,
            "backend": self.backend,
        }


class LLMClient:
    def __init__(
        self,
        backend: LLMBackend = "deepseek",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.backend = backend
        self.timeout = timeout
        self.api_key = api_key or self._default_key(backend)
        self.base_url = base_url or self._default_base_url(backend)
        self.model = model or self._default_model(backend)

    @staticmethod
    def _default_key(backend: LLMBackend) -> Optional[str]:
        return {
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "deepseek": os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY"),
        }.get(backend)

    @staticmethod
    def _default_base_url(backend: LLMBackend) -> Optional[str]:
        return {"deepseek": "https://api.deepseek.com/v1"}.get(backend)

    @staticmethod
    def _default_model(backend: LLMBackend) -> str:
        return {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-5-haiku-20241022",
            "deepseek": "deepseek-chat",
        }.get(backend, "gpt-4o-mini")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, system: str, user: str, temperature: float = 0.3) -> str:
        if not self.is_available():
            raise LLMNotAvailable(
                f"{self.backend} backend 缺 API key（环境变量 "
                f"{self.backend.upper()}_API_KEY）"
            )
        if self.backend == "anthropic":
            return self._call_anthropic(system, user, temperature)
        return self._call_openai_compatible(system, user, temperature)

    def _call_openai_compatible(self, system: str, user: str, temperature: float) -> str:
        try:
            from openai import OpenAI
        except ImportError as e:
            raise LLMNotAvailable("缺 openai SDK：pip install openai") from e
        client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""

    def _call_anthropic(self, system: str, user: str, temperature: float) -> str:
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise LLMNotAvailable("缺 anthropic SDK：pip install anthropic") from e
        client = Anthropic(api_key=self.api_key, timeout=self.timeout)
        resp = client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return resp.content[0].text if resp.content else ""


# ---------------------------------------------------------------------------
# Prompt 模板
# ---------------------------------------------------------------------------


_PROMPTS = {
    "proofread": (
        "你是一名严谨的中文 / 英文文字编辑。修正用户给的 Markdown 文本中的"
        "语法错误、拼写错误、标点不当，但**严格保留原意与原 Markdown 结构**。"
        "只输出修改后的全文，不要解释、不要总结、不要添加新内容。",

        "请校对以下 Markdown 内容（保留所有 Markdown 标记）：\n\n{text}",
    ),
    "rewrite": (
        "你是一名 Markdown 改写助手。按用户指定的语气（{tone}）重写以下文本，"
        "保留 Markdown 结构。只输出改写结果，不要解释。",

        "原文：\n\n{text}",
    ),
    "summarize": (
        "你是一名摘要助手。把用户给的 Markdown 文档压缩成不超过 3 句话的中文摘要。"
        "只输出摘要文本，不要前后缀。",

        "原文：\n\n{text}",
    ),
    "translate": (
        "你是一名翻译。把用户给的 Markdown 文本翻译为 {target_lang}，"
        "**保留所有 Markdown 标记**（标题级别、链接、代码块、列表符号等）。"
        "代码块内的代码不翻译；自然语言部分翻译。只输出翻译结果。",

        "原文：\n\n{text}",
    ),
    "expand": (
        "你是一名写作助手。基于用户给的大纲或骨架，扩写为完整的 Markdown 段落。"
        "保留原大纲的 heading 层级，在每个 heading 下补充 2-4 段正文。"
        "只输出扩写后的 Markdown，不要解释。",

        "大纲：\n\n{text}",
    ),
}


# ---------------------------------------------------------------------------
# AIAssistant 主入口
# ---------------------------------------------------------------------------


class AIAssistant:
    """对一段 Markdown 文本调 LLM 做 5 类操作。"""

    def __init__(self, llm_client: Optional[LLMClient] = None,
                 backend: LLMBackend = "deepseek"):
        self.llm_client = llm_client or LLMClient(backend=backend)

    def proofread(self, text: str) -> AIResult:
        return self._run("proofread", text)

    def rewrite(self, text: str, tone: Tone = "professional") -> AIResult:
        return self._run("rewrite", text, tone=tone)

    def summarize(self, text: str) -> AIResult:
        return self._run("summarize", text)

    def translate(self, text: str, target_lang: str = "English") -> AIResult:
        return self._run("translate", text, target_lang=target_lang)

    def expand(self, text: str) -> AIResult:
        return self._run("expand", text)

    def _run(self, action: str, text: str, **kwargs) -> AIResult:
        if not text or not text.strip():
            return AIResult(action=action, input_text=text,
                            output_text="", backend=self.llm_client.backend)
        system_tpl, user_tpl = _PROMPTS[action]
        system = system_tpl.format(**kwargs)
        user = user_tpl.format(text=text, **kwargs)

        output = self.llm_client.chat(system, user)
        return AIResult(
            action=action,
            input_text=text,
            output_text=output.strip(),
            backend=self.llm_client.backend,
        )
