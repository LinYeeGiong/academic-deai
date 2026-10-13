# academic-deai

中英文学术写作**去AI化**与**去防御性表述** skill。适用于 Claude Code、Codex、pi、Cursor、Gemini CLI、OpenCode、Goose 等支持 [Agent Skills](https://agentskills.io) 标准的 agent。

An [Agent Skill](https://agentskills.io) that strips AI tells and defensive hedging from academic prose in **Chinese and English**, without touching numbers, formulas, citations, or terminology. [English summary below](#english).

---

## 它做什么

| 处理对象 | 例子 |
|---|---|
| **AI 腔** | 「值得注意的是」「随着……的快速发展」「起到了关键作用」「为……提供了新思路」、四字格堆砌、“不是……而是……”、*delve / underscore / pivotal*、em-dash、句长过于均匀 |
| **防御性表述** | 「可能在一定程度上」「需要说明的是，本文并非……」「当然这一结论仍需进一步验证」「尽管存在一定局限性，但……」、*We do not claim that…*、*may potentially* |

**必须保留的谨慎表述不会被删**：因果与相关的区分、真实的机制推测、置信区间与 p 值、局限性章节本身。把「结果提示 X 可能参与调控」改成「证明 X 参与调控」是制造过度论断，本 skill 明确禁止这种改法。

**硬约束**：不改数值、公式、引用键（`\cite`/`\ref`/`\label`）、术语和 LaTeX 结构；不新增事实；不删减论证内容。原文没有数值支撑的「显著提升」不会被编一个数字填上，而是列入「需作者确认」。

### 改写示例

> **改前**：随着深度学习的快速发展，医学图像分割受到了广泛关注。值得注意的是，本文方法显著提升了分割精度，这一结果可能在一定程度上表明该策略是有效的。综上所述，本文为该领域提供了新思路。
>
> **改后**：医学图像分割的标注依赖专科医生，单张三维 CT 的人工标注通常需要数小时。本文方法的 Dice 系数比最强基线高 2.4 个百分点（表 2）。

> **Before**: *In recent years, graph learning has attracted increasing attention. It is worth noting that our method significantly outperforms baselines, which may potentially suggest that it could, to some extent, improve robustness.*
>
> **After**: *Graph neural networks degrade on heterophilous graphs. On four benchmarks, our method exceeds the strongest baseline by 1.8–3.5 F1 points (Table 2).*

（示例中的数值仅作演示；实际改写只使用原文已有的数值。）

---

## 安装

### Claude Code（插件市场，推荐）

```bash
claude plugin marketplace add LinYeeGiong/academic-deai
claude plugin install academic-deai@academic-deai
```

或在 Claude Code 会话内：

```
/plugin marketplace add LinYeeGiong/academic-deai
/plugin install academic-deai@academic-deai
```

更新：`claude plugin marketplace update academic-deai`。

### 任意 agent（一条命令自动探测）

```bash
git clone https://github.com/LinYeeGiong/academic-deai.git
cd academic-deai
sh install.sh            # macOS / Linux / Git Bash / WSL
```

```powershell
git clone https://github.com/LinYeeGiong/academic-deai.git
cd academic-deai
.\install.ps1            # Windows PowerShell
```

脚本总会装到跨 agent 通用位置 `~/.agents/skills/`，并为本机已有配置目录的 agent 各装一份。常用选项：

| 选项 | 作用 |
|---|---|
| `--list` / `-List` | 只显示将安装的位置，不做改动 |
| `--link` / `-Link` | 软链接（Windows 为 junction），`git pull` 后自动生效 |
| `--agents` / `-Agents` | 只装通用位置 `~/.agents/skills/` |
| `--claude` / `-Claude` | 只装 Claude Code |
| `--project` / `-Project` | 装到当前目录的 `.agents/skills/`，可提交给团队共享 |

### 手动安装

把 `skills/academic-deai/` 整个目录复制到对应位置即可：

| Agent | 用户级目录 | 项目级目录 | 调用方式 |
|---|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` | `/academic-deai` |
| Codex | `~/.agents/skills/` | `.agents/skills/` | `$academic-deai` 或 `/skills` |
| pi | `~/.agents/skills/` | `.agents/skills/` | `/skill:academic-deai` |
| Cursor \* | `~/.cursor/skills/` | `.cursor/skills/` | 直接描述需求 |
| Gemini CLI \* | `~/.gemini/skills/` | `.gemini/skills/` | 直接描述需求 |
| OpenCode \* | `~/.config/opencode/skills/` | `.opencode/skills/` | 直接描述需求 |
| Goose \* | `~/.config/goose/skills/` | `.goose/skills/` | 直接描述需求 |

\* 这几个 agent 的目录按其公开约定填写，未在本仓库逐一实测。不确定时优先用 `~/.agents/skills/`，这是 Agent Skills 标准的跨 agent 位置；多数 agent 也会读取它。各 agent 的目录约定可能随版本变化，以其官方文档为准。

---

## 使用

直接描述需求即可，agent 会根据 skill 描述自动加载：

```
帮我把 paper/main.tex 第 120–260 行去AI化，去掉防御性表述
```

```
De-AI the abstract in draft.md and remove defensive hedging
```

三种模式：

| 模式 | 行为 |
|---|---|
| `audit` | 只列问题清单 |
| `rewrite`（默认） | 输出改写稿 + 修改记录 + 保留未改说明 + 需作者确认清单，不动源文件 |
| `apply` | 改写后写回源文件（需明确要求） |

### 扫描脚本（可选）

skill 自带一个零依赖的扫描器，用来给出带行号的候选问题。没有 Python 时 agent 会直接按规则库人工审计。

```bash
python skills/academic-deai/scripts/scan.py draft.tex --format md
python skills/academic-deai/scripts/scan.py draft.tex --lines 120-260 --format text
```

- 需要 Python 3.9+，只用标准库。
- 中英文规则同时运行，句长统计按语言分别计算。
- `.tex` 文件自动跳过注释、数学环境、`\cite`/`\ref`/`\label` 键，以及 `equation`/`table`/`figure`/`algorithm` 等环境。
- 命中项是**候选**，需结合上下文判断：带统计检验的「显著」、表达真实不确定性的「可能」都应保留。

自测：

```bash
python skills/academic-deai/scripts/scan.py skills/academic-deai/scripts/_selftest.tex --format text
```

---

## 仓库结构

```
academic-deai/
├── .claude-plugin/
│   ├── marketplace.json        # Claude Code 插件市场清单
│   └── plugin.json             # 插件清单
├── skills/academic-deai/       # ← skill 本体，所有 agent 共用
│   ├── SKILL.md
│   ├── references/
│   │   ├── zh_patterns.md          # 中文 AI 腔模式库
│   │   ├── en_patterns.md          # English AI-tell catalog
│   │   └── defensive_hedging.md    # 防御性表述 + 必须保留的谨慎表述
│   └── scripts/
│       ├── scan.py                 # 中英双语扫描器
│       └── _selftest.tex           # 自测样例
├── install.sh                  # macOS / Linux / Git Bash 安装脚本
├── install.ps1                 # Windows PowerShell 安装脚本
└── LICENSE
```

---

## 声明

本 skill 用于提升学术文本的可读性和表达质量，**不用于规避**期刊、学校或资助机构对 AI 使用的披露要求。请遵守所在机构与投稿目标的政策。

---

## English

**academic-deai** is a portable [Agent Skill](https://agentskills.io) for editing academic prose in Chinese and English. It removes two classes of problems:

- **AI tells**: formulaic openers and closers, boilerplate emphasis (*It is worth noting that*), significance hype (*paves the way*), AI vocabulary (*delve, underscore, pivotal*), light verbs, negative parallelism, superficial *-ing* tails, em-dashes, uniform sentence rhythm.
- **Defensive hedging**: stacked hedges (*may potentially*), pre-emptive self-defence (*We do not claim that…*), generic disclaimer suffixes (*further research is needed*), concessive boilerplate, excessive modesty.

It **keeps** calibrated hedging that matches the evidence (correlation vs. causation, genuine mechanistic speculation, confidence intervals, the limitations section) and **never** changes numbers, formulas, citation keys, or terminology, and never invents data.

**Install**: Claude Code users run `claude plugin marketplace add LinYeeGiong/academic-deai` then `claude plugin install academic-deai@academic-deai`. For any other agent, clone the repo and run `sh install.sh` (or `.\install.ps1` on Windows), which installs to the cross-agent location `~/.agents/skills/` plus every detected agent. Or copy `skills/academic-deai/` into your agent's skills directory manually (see the table above).

This skill improves clarity. It is not a tool for evading AI-use disclosure requirements.

## License

[MIT](LICENSE)
