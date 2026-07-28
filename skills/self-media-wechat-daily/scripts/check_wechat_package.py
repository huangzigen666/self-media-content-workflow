#!/usr/bin/env python3
"""Validate a WeChat article package before it enters the draft box."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
RELATIVE_DATE_RE = re.compile(r"(今天|明天|昨日|昨天|刚刚|本月|下月)")
ABSOLUTE_DATE_RE = re.compile(r"\b20\d{2}[-年/.]\d{1,2}(?:[-月/.]\d{1,2}日?)?")

REQUIRED_FIELDS = (
    "title",
    "platform",
    "content_type",
    "topic_key",
    "publish_priority",
    "source_checked_at",
    "evidence_level",
    "core_judgment",
    "information_gain_1",
    "information_gain_2",
    "original_contribution",
    "reader_action",
    "duplicate_check",
    "ai_assistance",
    "rights_status",
    "status",
)
PENDING_VALUES = {"", "pending", "todo", "待确认", "待检查", "未知", "未核验"}
BLOCKING_DUPLICATE = {"重复", "高度重复", "未通过", "fail", "failed"}
BLOCKING_AI = {"直接生成", "原样使用", "批量生成", "未核验", "direct", "raw"}
WEAK_CONTRIBUTIONS = {"ai润色", "ai改写", "改写", "润色", "整理", "换标题", "换封面"}


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


def normalized(value: str | None) -> str:
    return (value or "").strip().lower().replace(" ", "")


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    values = parse_frontmatter(text)
    errors: list[str] = []

    if not values:
        return ["缺少 YAML front matter"]

    for field in REQUIRED_FIELDS:
        if field not in values:
            errors.append(f"缺少字段：{field}")
        elif normalized(values[field]) in PENDING_VALUES:
            errors.append(f"字段尚未完成：{field}")

    title = values.get("title", "").strip()
    frontmatter_match = FRONTMATTER_RE.match(text)
    assert frontmatter_match is not None
    h1_match = H1_RE.search(text[frontmatter_match.end() :])
    if h1_match and title and h1_match.group(1).strip() != title:
        errors.append("front matter 标题与 H1 标题不一致")

    platform = normalized(values.get("platform"))
    if platform and platform not in {"微信公众号", "wechat", "微信公众平台"}:
        errors.append(f"平台字段不是微信公众号：{values.get('platform')}")

    if normalized(values.get("duplicate_check")) in BLOCKING_DUPLICATE:
        errors.append("近 7 天同题检查未通过")

    if normalized(values.get("ai_assistance")) in BLOCKING_AI:
        errors.append("AI 辅助状态属于直接生成、批量生成或未核验")

    if normalized(values.get("original_contribution")) in WEAK_CONTRIBUTIONS:
        errors.append("原创贡献只有改写、润色或整理，不构成信息增量")

    body = text[frontmatter_match.end() :]
    if RELATIVE_DATE_RE.search(body) and not ABSOLUTE_DATE_RE.search(body):
        errors.append("正文含相对日期，但没有可识别的绝对日期")

    if len(re.sub(r"\s+", "", body)) < 300:
        errors.append("正文少于内部最低信息量 300 个非空白字符")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
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
        errors = validate(path)
        if errors:
            failed = True
            for error in errors:
                print(f"FAIL: {path}: {error}", file=sys.stderr)
        else:
            print(f"PASS: {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
