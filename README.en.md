# Self Media Skills

[中文](README.md)

A modular, tool-agnostic skill suite for social media content planning, research, platform-native writing, short-form video, analytics, and delivery.

## Modules

| Skill | Responsibility |
|---|---|
| `self-media-content-workflow` | Routing, state, approvals, and end-to-end orchestration |
| `self-media-content-brief` | Audience, goal, evidence, angle, tone, and constraints |
| `self-media-content-strategy` | Positioning, content mix, series, topic pool, and calendar |
| `self-media-trend-radar` | Trend research, competitor analysis, and original topic discovery |
| `self-media-platform-copywriting` | Native copy for X, Xiaohongshu, WeChat, and short video platforms |
| `self-media-short-video` | Hooks, spoken script, storyboard, captions, and shoot plan |
| `self-media-content-analytics` | Data quality, comparable baselines, attribution, decisions, and tests |
| `self-media-content-delivery` | Milestone files, versions, path verification, and publishing packages |

## Install

```bash
git clone https://github.com/yanhua1010/self-media-content-workflow.git
cd self-media-content-workflow
python3 scripts/install.py
```

The default target is `${CODEX_HOME:-~/.codex}/skills`. For a project-local installation:

```bash
python3 scripts/install.py --target /path/to/project/.agents/skills
```

## Use

```text
Use $self-media-content-workflow to turn this product failure story into an X thread and a Xiaohongshu carousel.
```

Individual modules can also be invoked directly.

## Principles

- Share facts and evidence across platforms, not one shared body draft.
- Require explicit approval for direction, platform choice, title, final copy, and publishing actions.
- Create drafts or publishing packages by default. Never broadcast automatically.
- Keep competitor research read-only and separate from a creator's primary account session.
- Treat platform limits as time-sensitive and verify exact values against official sources.
- Never invent results, product experience, audience feedback, or attribution.

## Validate

```bash
python3 scripts/validate.py
```

The validator has no third-party dependencies.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and run the validator before opening a pull request.

## License

[MIT](LICENSE)
