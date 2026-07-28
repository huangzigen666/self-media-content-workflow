#!/usr/bin/env python3
"""Validate a Toutiao Markdown package before publishing."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
RELATIVE_DATE_RE = re.compile(r"(今天|明天|昨日|昨天|刚刚|本月|下月)")
ABSOLUTE_DATE_RE = re.compile(r"\b20\d{2}[-年/.]\d{1,2}(?:[-月/.]\d{1,2}日?)?")

FIELD_ALIASES = {
    "title": ("title", "标题"),
    "platform": ("platform", "平台"),
    "content_type": ("content_type", "类型"),
    "topic_key": ("topic_key", "选题键"),
    "publish_priority": ("publish_priority", "发布优先级"),
    "source_checked_at": ("source_checked_at", "来源核验时间"),
    "evidence_level": ("evidence_level",),
    "core_judgment": ("core_judgment",),
    "originality_mode": ("originality_mode", "原创声明"),
    "ai_disclosure": ("ai_disclosure", "AI声明"),
    "duplicate_check": ("duplicate_check", "同题去重"),
    "status": ("status", "状态"),
}

PENDING_VALUES = {"", "pending", "todo", "待确认", "待检查"}


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    values: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def get_field(values: dict[str, str], canonical: str) -> str | None:
    for alias in FIELD_ALIASES[canonical]:
        if alias in values:
            return values[alias].strip()
    return None


def validate(path: Path, max_title_chars: int) -> list[str]:
    text = path.read_text(encoding="utf-8")
    values = parse_frontmatter(text)
    errors: list[str] = []

    if not values:
        return ["缺少 YAML front matter"]

    for canonical in FIELD_ALIASES:
        if get_field(values, canonical) is None:
            errors.append(f"缺少字段：{canonical}")

    title = get_field(values, "title") or ""
    if len(title) > max_title_chars:
        errors.append(
            f"标题 {len(title)} 字符，超过内部上限 {max_title_chars}：{title}"
        )

    frontmatter_match = FRONTMATTER_RE.match(text)
    assert frontmatter_match is not None
    h1_match = H1_RE.search(text[frontmatter_match.end() :])
    if h1_match and title and h1_match.group(1).strip() != title:
        errors.append("front matter 标题与 H1 标题不一致")

    platform = get_field(values, "platform")
    if platform and platform not in {"今日头条", "toutiao", "Toutiao"}:
        errors.append(f"平台字段不是今日头条：{platform}")

    for field in ("source_checked_at", "core_judgment", "duplicate_check"):
        value = (get_field(values, field) or "").lower()
        if value in PENDING_VALUES:
            errors.append(f"字段尚未完成：{field}")

    ai_disclosure = (get_field(values, "ai_disclosure") or "").lower()
    if ai_disclosure in PENDING_VALUES:
        errors.append("AI 声明尚未确认")

    originality = (get_field(values, "originality_mode") or "").lower()
    if originality in PENDING_VALUES:
        errors.append("原创声明尚未确认")

    body = text[frontmatter_match.end() :]
    if RELATIVE_DATE_RE.search(body) and not ABSOLUTE_DATE_RE.search(body):
        errors.append("正文含相对日期，但没有可识别的绝对日期")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--max-title-chars", type=int, default=30)
    args = parser.parse_args()

    files: list[Path] = []
    for path in args.paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
        elif path.suffix.lower() == ".md":
            files.append(path)

    if not files:
        print("FAIL: 未找到 Markdown 文件", file=sys.stderr)
        return 2

    failed = False
    for path in files:
        errors = validate(path, args.max_title_chars)
        if errors:
            failed = True
            for error in errors:
                print(f"FAIL: {path}: {error}", file=sys.stderr)
        else:
            print(f"PASS: {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

