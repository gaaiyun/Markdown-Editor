"""Markdown-Editor CLI —— 5 个 AI 写作命令 + 导出。

子命令：
    proofread <file>          校对（修正语法/拼写/标点，保留 Markdown 结构）
    rewrite <file> --tone X   按指定语气改写
    summarize <file>          ≤ 3 句话摘要
    translate <file> --to en  翻译到指定语言（默认 English）
    expand <file>             基于大纲扩写
    export <file>             调原 exporter 导 HTML/PDF/Word
    list-backends             列 LLM backend

示例：

    python __main__.py proofread draft.md -o cleaned.md
    python __main__.py rewrite draft.md --tone academic -o academic.md
    python __main__.py translate cn_post.md --to English -o en_post.md
    python __main__.py summarize long_article.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ai_assistant import AIAssistant, LLMClient, LLMNotAvailable  # noqa: E402


def _read_input(path: str) -> str:
    p = Path(path)
    if not p.exists():
        sys.stderr.write(f"[error] 找不到文件 {p}\n")
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def _write_output(text: str, output: str | None) -> None:
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text, encoding="utf-8")
        sys.stderr.write(f"[ok] {len(text)} 字符已写入 {output}\n")
    else:
        sys.stdout.write(text)


def _run_ai_op(args, op_name: str, **op_kwargs) -> int:
    assistant = AIAssistant(LLMClient(backend=args.backend))
    text = _read_input(args.file)
    try:
        result = getattr(assistant, op_name)(text, **op_kwargs) if op_kwargs \
                 else getattr(assistant, op_name)(text)
    except LLMNotAvailable as e:
        sys.stderr.write(f"[error] {e}\n")
        return 2
    except Exception as e:
        sys.stderr.write(f"[error] {type(e).__name__}: {e}\n")
        return 3
    _write_output(result.output_text, args.output)
    return 0


def cmd_proofread(args) -> int:
    return _run_ai_op(args, "proofread")


def cmd_rewrite(args) -> int:
    return _run_ai_op(args, "rewrite", tone=args.tone)


def cmd_summarize(args) -> int:
    return _run_ai_op(args, "summarize")


def cmd_translate(args) -> int:
    return _run_ai_op(args, "translate", target_lang=args.to)


def cmd_expand(args) -> int:
    return _run_ai_op(args, "expand")


def cmd_export(args) -> int:
    from exporter import MarkdownExporter
    text = _read_input(args.file)
    exporter = MarkdownExporter()
    fmt = args.format
    out = args.output or args.file.replace(".md", f".{fmt}")
    if fmt == "html":
        exporter.export_html(text, out)
    elif fmt == "pdf":
        exporter.export_pdf(text, out)
    elif fmt == "docx":
        exporter.export_docx(text, out)
    else:
        sys.stderr.write(f"[error] 不支持的格式 {fmt}\n")
        return 1
    print(f"[ok] exported to {out}")
    return 0


def cmd_list_backends(args) -> int:
    import os as _os
    rows = [
        ("openai",    "gpt-4o-mini",                "OPENAI_API_KEY"),
        ("anthropic", "claude-3-5-haiku-20241022",  "ANTHROPIC_API_KEY"),
        ("deepseek",  "deepseek-chat",              "DEEPSEEK_API_KEY"),
    ]
    print(f"{'backend':<12} {'default model':<32} {'env var'}")
    print("-" * 70)
    for b, m, e in rows:
        cfg = "yes" if _os.getenv(e) else "no"
        print(f"{b:<12} {m:<32} {e}  (configured: {cfg})")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="md_editor", description="Markdown 编辑器 CLI")
    sub = p.add_subparsers(dest="cmd", required=True)
    common_backends = ["openai", "anthropic", "deepseek"]
    tones = ["formal", "casual", "academic", "concise", "friendly", "professional"]

    sp = sub.add_parser("proofread", help="校对：修语法/拼写/标点，保 Markdown 结构")
    sp.add_argument("file")
    sp.add_argument("--backend", default="deepseek", choices=common_backends)
    sp.add_argument("-o", "--output")
    sp.set_defaults(func=cmd_proofread)

    sp = sub.add_parser("rewrite", help="按语气改写")
    sp.add_argument("file")
    sp.add_argument("--tone", default="professional", choices=tones)
    sp.add_argument("--backend", default="deepseek", choices=common_backends)
    sp.add_argument("-o", "--output")
    sp.set_defaults(func=cmd_rewrite)

    sp = sub.add_parser("summarize", help="≤ 3 句话摘要")
    sp.add_argument("file")
    sp.add_argument("--backend", default="deepseek", choices=common_backends)
    sp.add_argument("-o", "--output")
    sp.set_defaults(func=cmd_summarize)

    sp = sub.add_parser("translate", help="翻译")
    sp.add_argument("file")
    sp.add_argument("--to", default="English", help="目标语言，如 English / 中文 / 日本語")
    sp.add_argument("--backend", default="deepseek", choices=common_backends)
    sp.add_argument("-o", "--output")
    sp.set_defaults(func=cmd_translate)

    sp = sub.add_parser("expand", help="基于大纲扩写")
    sp.add_argument("file")
    sp.add_argument("--backend", default="deepseek", choices=common_backends)
    sp.add_argument("-o", "--output")
    sp.set_defaults(func=cmd_expand)

    sp = sub.add_parser("export", help="导出 HTML / PDF / DOCX")
    sp.add_argument("file")
    sp.add_argument("--format", choices=["html", "pdf", "docx"], required=True)
    sp.add_argument("-o", "--output")
    sp.set_defaults(func=cmd_export)

    sp = sub.add_parser("list-backends")
    sp.set_defaults(func=cmd_list_backends)

    return p


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
