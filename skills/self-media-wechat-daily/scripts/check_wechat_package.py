#!/usr/bin/env python3
"""Validate a WeChat article package before it enters the draft box."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
RELATIVE_DATE_RE = re.compile(r"(今天|明天|昨日|昨天|刚刚|本月|下月)")
ABSOLUTE_DATE_RE = re.compile(r"\b20\d{2}[-年/.]\d{1,2}(?:[-月/.]\d{1,2}日?)?")
FIRST_PERSON_CLAIM_RE = re.compile(
    r"(我亲历|我亲眼|我家孩子|我的孩子|我的客户|真实客户|客户真实案例)"
)

REQUIRED_FIELDS = (
    "title",
    "platform",
    "content_type",
    "content_role",
    "topic_key",
    "source_asset_id",
    "publish_priority",
    "signal_type",
    "signal_source",
    "source_checked_at",
    "evidence_level",
    "platform_claim_evidence",
    "core_judgment",
    "information_gain_1",
    "information_gain_2",
    "original_contribution",
    "reader_action",
    "duplicate_check",
    "ai_mode",
    "ai_assistance",
    "human_decisions",
    "human_revisions",
    "fact_check_status",
    "approval_status",
    "approver",
    "approved_at",
    "case_provenance",
    "publish_mode",
    "rights_status",
    "status",
)
PENDING_VALUES = {"", "pending", "todo", "待确认", "待检查", "未知", "未核验"}
BLOCKING_DUPLICATE = {"重复", "高度重复", "未通过", "fail", "failed"}
BLOCKING_AI = {"直接生成", "原样使用", "批量生成", "未核验", "direct", "raw"}
WEAK_CONTRIBUTIONS = {"ai润色", "ai改写", "改写", "润色", "整理", "换标题", "换封面"}
CONTENT_ROLES = {"discovery", "trust", "conversion"}
SIGNAL_TYPES = {"official_update", "search", "comment", "consultation", "reader_question"}
QUESTION_SIGNAL_TYPES = {"search", "comment", "consultation", "reader_question"}
AI_MODES = {"none", "assist"}
PUBLISH_MODES = {"manual_package", "single_draft_with_human_gate"}
BLOCKING_PUBLISH_MODES = {
    "bulk_publish",
    "unattended_autopublish",
    "批量发布",
    "无人值守",
}
PLATFORM_EVIDENCE = {
    "none",
    "official",
    "backstage",
    "own-data",
    "third-party-hypothesis",
}
EMPTY_CASE_PROVENANCE = {"none", "无", "不适用"}
NO_PUBLISH_STATUS = {"no_publish", "不发布"}
FINAL_ONLY_FIELDS = {"fact_check_status", "approval_status", "approver", "approved_at"}
INVALID_APPROVERS = {"无", "none", "不适用", "系统", "ai", "待定", "稍后"}
APPROVED_AT_FORMATS = ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S")


def validate_no_publish(values: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for field in ("signal_type", "signal_source", "source_checked_at", "rejection_reason"):
        if normalized(values.get(field)) in PENDING_VALUES:
            errors.append(f"NO_PUBLISH 缺少字段：{field}")
    signal_type = normalized(values.get("signal_type"))
    if signal_type and signal_type not in SIGNAL_TYPES:
        errors.append(f"未知 signal_type：{values.get('signal_type')}")
    return errors


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


def parse_approved_at(value: str) -> datetime | None:
    for date_format in APPROVED_AT_FORMATS:
        try:
            return datetime.strptime(value.strip(), date_format)
        except ValueError:
            continue
    return None


def validate(path: Path, stage: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    values = parse_frontmatter(text)
    errors: list[str] = []

    if not values:
        return ["缺少 YAML front matter"]

    if normalized(values.get("status")) in NO_PUBLISH_STATUS:
        return validate_no_publish(values)

    for field in REQUIRED_FIELDS:
        if field not in values:
            errors.append(f"缺少字段：{field}")
        elif (
            normalized(values[field]) in PENDING_VALUES
            and field not in FINAL_ONLY_FIELDS
        ):
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

    content_role = normalized(values.get("content_role"))
    if content_role and content_role not in CONTENT_ROLES:
        errors.append(
            "content_role 必须是 DISCOVERY、TRUST 或 CONVERSION"
        )

    signal_type = normalized(values.get("signal_type"))
    if signal_type and signal_type not in SIGNAL_TYPES:
        errors.append(f"未知 signal_type：{values.get('signal_type')}")
    if signal_type in QUESTION_SIGNAL_TYPES:
        for field in ("reader_question_quote", "question_source", "audience_stage"):
            if normalized(values.get(field)) in PENDING_VALUES:
                errors.append(f"问题型信号缺少字段：{field}")

    ai_mode = normalized(values.get("ai_mode"))
    if ai_mode and ai_mode not in AI_MODES:
        errors.append("ai_mode 只能是 none 或 assist")

    platform_evidence = normalized(values.get("platform_claim_evidence"))
    if platform_evidence and platform_evidence not in PLATFORM_EVIDENCE:
        errors.append(
            "platform_claim_evidence 必须是 none、official、backstage、"
            "own-data 或 third-party-hypothesis"
        )

    if normalized(values.get("duplicate_check")) in BLOCKING_DUPLICATE:
        errors.append("近 7 天同题检查未通过")

    ai_assistance = normalized(values.get("ai_assistance"))
    if any(term in ai_assistance for term in BLOCKING_AI):
        errors.append("AI 辅助状态属于直接生成、批量生成或未核验")

    original_contribution = normalized(values.get("original_contribution"))
    if any(
        term in original_contribution for term in WEAK_CONTRIBUTIONS
    ) and not any(
        term in original_contribution
        for term in ("核验", "计算", "案例", "实测", "独立分析", "对照")
    ):
        errors.append("原创贡献只有改写、润色或整理，不构成信息增量")

    if stage == "final":
        if normalized(values.get("fact_check_status")) != "verified":
            errors.append("最终阶段 fact_check_status 必须是 verified")
        if normalized(values.get("approval_status")) != "approved":
            errors.append("最终阶段 approval_status 必须是 approved")
        approver = normalized(values.get("approver"))
        if approver in PENDING_VALUES or approver in INVALID_APPROVERS:
            errors.append("最终审批人无效：approver")
        approved_at = parse_approved_at(values.get("approved_at", ""))
        if approved_at is None:
            errors.append("approved_at 必须是 YYYY-MM-DD HH:MM[:SS]")
        elif approved_at > datetime.now() + timedelta(minutes=10):
            errors.append("approved_at 晚于当前时间超过 10 分钟")

    publish_mode = normalized(values.get("publish_mode"))
    if publish_mode in BLOCKING_PUBLISH_MODES or (
        publish_mode and publish_mode not in PUBLISH_MODES
    ):
        errors.append(
            "publish_mode 只能是 manual_package 或 single_draft_with_human_gate"
        )

    body = text[frontmatter_match.end() :]
    if RELATIVE_DATE_RE.search(body) and not ABSOLUTE_DATE_RE.search(body):
        errors.append("正文含相对日期，但没有可识别的绝对日期")

    if (
        FIRST_PERSON_CLAIM_RE.search(body)
        and normalized(values.get("case_provenance")) in EMPTY_CASE_PROVENANCE
    ):
        errors.append("正文含第一人称或真实客户主张，但 case_provenance 未记录")

    if len(re.sub(r"\s+", "", body)) < 300:
        errors.append("正文少于内部最低信息量 300 个非空白字符")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage", choices=("preflight", "final"), default="final"
    )
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
        errors = validate(path, args.stage)
        if errors:
            failed = True
            for error in errors:
                print(f"FAIL: {path}: {error}", file=sys.stderr)
        else:
            print(f"PASS: {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
