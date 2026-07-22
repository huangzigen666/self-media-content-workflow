# Self Media Skills

[English](README.en.md)

一套通用、模块化的自媒体内容生产与经营 Skills，覆盖内容简报、账号策略、热点竞品、平台文案、短视频、数据复盘和交付归档。

它不绑定特定账号、目录、模型或第三方平台工具。总控 Skill 会根据当前环境发现可用的搜索、浏览器、图片、视频、发布和数据能力。

## 能力

- 从模糊需求生成可确认的创作简报
- 把账号定位和目标转成内容配比、栏目、选题池和内容日历
- 安全研究热点、关键词和竞品结构
- 为 X、小红书、微信公众号、视频号和抖音生成平台原生内容
- 生成口播、分镜、字幕、封面和拍摄清单
- 分析单篇、周度和月度数据，区分相关性与因果
- 按里程碑保存成品、管理版本并生成发布包
- 在方向、平台、标题、终稿和发布前保留人工确认

## 架构

```text
self-media-content-workflow
├── self-media-content-brief
├── self-media-content-strategy
├── self-media-trend-radar
├── self-media-platform-copywriting
├── self-media-short-video
├── self-media-content-analytics
└── self-media-content-delivery
```

| Skill | 作用 |
|---|---|
| `self-media-content-workflow` | 请求路由、状态管理和端到端编排 |
| `self-media-content-brief` | 澄清目标、受众、证据、角度和约束 |
| `self-media-content-strategy` | 账号定位、内容配比、栏目、选题池和日历 |
| `self-media-trend-radar` | 热点追踪、关键词研究、竞品拆解和原创选题 |
| `self-media-platform-copywriting` | X、小红书、公众号和短视频平台原生文案 |
| `self-media-short-video` | 钩子、口播、分镜、字幕和拍摄方案 |
| `self-media-content-analytics` | 数据质量、基线比较、归因、决策和实验 |
| `self-media-content-delivery` | 里程碑保存、版本、路径核验和完整发布包 |

## 安装

### 安装到 Codex 用户目录

```bash
git clone https://github.com/yanhua1010/self-media-content-workflow.git
cd self-media-content-workflow
python3 scripts/install.py
```

默认安装到 `${CODEX_HOME:-~/.codex}/skills`。

### 安装到单个项目

```bash
python3 scripts/install.py --target /path/to/project/.agents/skills
```

目标目录已有同名 Skill 时，安装器会停止。确认需要覆盖后使用 `--force`。

## 使用

从总控开始：

```text
使用 $self-media-content-workflow，把这段产品失败经历做成小红书和公众号内容。
```

也可以直接调用模块：

```text
使用 $self-media-content-strategy，为一个新账号建立选题池和一个月内容日历。

使用 $self-media-trend-radar，研究最近一个月 AI 编程内容的高频问题。

使用 $self-media-content-analytics，分析这 10 篇内容并找出下一轮唯一实验。
```

## 工作流

```text
需求澄清
→ 方向确认
→ 研究与证据
→ 平台确认
→ 发布预检
→ 平台原生初稿
→ 标题确认
→ 视觉或视频素材
→ 质量审校
→ 终稿确认
→ 草稿或发布包
→ 数据复盘
```

终稿确认不等于发布授权。Skill 默认只创建草稿或手动发布包，不直接群发。

## 安全边界

- 不使用主账号登录态自动采集竞品
- 不自动点赞、评论、关注、私信或发布
- 不在任务卡、日志或仓库保存 Cookie、Token 和 Secret
- 验证码、限流和平台风控出现时立即停止
- 近期产品、价格、版本和平台规则优先核验官方来源
- 不编造数据、体验、收益、用户评价和测试结果

## 校验

```bash
python3 scripts/validate.py
```

校验器检查 Skill frontmatter、目录名称、核心文件行数、UI 元数据、相对链接和未处理的 TODO，无需安装第三方依赖。

## 仓库结构

```text
skills/                 # 8 个可独立安装的 Skill
scripts/install.py      # 安装到用户或项目 Skill 目录
scripts/validate.py     # 仓库校验
.github/workflows/      # 持续集成
```

## 设计取舍

- 采用一个总控加七个模块的结构
- 采集和发布作为运行时适配层，不绑定厂商实现
- 多平台共享事实与证据，但分别重写标题、开头、结构和行动
- 平台限制可能变化，需要精确值时以官方说明或发布界面为准
- 商单和自然内容分开分析，样本不足时不调整长期策略

## 贡献

提交修改前阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，并运行 `python3 scripts/validate.py`。

## 许可证

[MIT](LICENSE)
