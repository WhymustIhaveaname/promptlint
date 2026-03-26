# promptlint

Lint and test LLM prompts — like pylint + pytest, but for prompts.

## 项目愿景

三种规则类型：

1. **硬编码规则** — 不依赖 LLM，纯本地检查（正则、行数、路径存在性等）
2. **LLM 解释型规则** — 类似 korchasa：把规则 + prompt 发给 LLM，LLM 判断是否违规（best practice 检查）
3. **LLM 响应型规则** — 类似 promptfoo：把 prompt 像生产环境那样发给 LLM，检查响应质量

设计原则：

- **配置文件**学习 promptfoo（YAML 定义规则和断言）
- **插件系统**学习 navdeep-G（Python entry_points 做规则自动发现，可扩展）
- **LLM 后端**优先用本地已登录的 claude/codex CLI（免费），也支持 API key

## Repos to investigate

| Repo | Type | Lang | ⭐ | Created | Commits (2w) | Active? | Notes |
|------|------|------|----|---------|--------------|---------|-------|
| [navdeep-G/prompt-lint](https://github.com/navdeep-G/prompt-lint) | Static lint | Python | 2 | 2025-11 | 0 | No | Rule-based, 6 built-in rules |
| [korchasa/promptlint](https://github.com/korchasa/promptlint) | LLM lint | Go | 2 | 2025-03 | 0 | No | YAML rules, calls LLM API |
| [youcommit/promptlint](https://github.com/youcommit/promptlint) | Compliance | TypeScript | 0 | 2025-11 | 0 | No | PII / sensitive data detection |
| [alexmavr/promptsage](https://github.com/alexmavr/promptsage) | Builder + lint | Python | 22 | 2024-03 | 0 | No | Sanitizer + guardrails |
| [Prompt Linter (VS Code)](https://marketplace.visualstudio.com/items?itemName=Ignire.prompt-linter) | IDE extension | — | — | — | — | — | Claude-powered analysis |
| [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | Eval / test | TypeScript | 18.5k | 2023-04 | 30+ | ✅ Yes | Red team, CI/CD, now under OpenAI |

## 试用笔记

### promptfoo (2026-03-26)

**结论：有一丢丢用，但用处不大。想钱想疯了。**

promptfoo 不是一个 prompt linter——它不内置任何 prompt 质量规则或 best practice。本质上是一个 eval 执行器：你自己写断言，它帮你跑。

| 功能 | 免费可用？ | 实际是什么 |
|------|-----------|-----------|
| 规则断言 (echo provider) | ✅ | 自己写 contains/regex/js 规则，它跑。省了写代码的功夫 |
| 模型对比 | ✅ | 同一 prompt 发多个模型，自己写断言判好坏 |
| 数据集驱动 | ✅ | 用 CSV/JSON 批量喂测试用例，还是自己写断言 |
| generate dataset | ✅ | LLM 基于现有用例生成更多变体，质量一般 |
| CI/CD 集成 | ✅ | 就是 exit code 非零，没有别的 |
| Red teaming | ❌ 要注册 | 自动生成对抗输入，锁在注册墙后面 |
| code-scans | ❌ 要注册 | 扫代码里的 LLM 安全漏洞，锁在注册墙后面 |
| scan-model | 跟 prompt 无关 | 扫模型权重文件安全性 |

免费部分唯一的价值：不用自己写测试框架代码，直接用 YAML 定义断言。但所有的"该检查什么"都得你自己知道。

### navdeep-G/prompt-lint (2026-03-26)

**结论：方向对但规则太弱，项目已停更。插件系统的设计思路值得借鉴。**

唯一一个自带内置规则的工具。纯本地运行，不调 LLM，靠正则/关键词匹配。

6 条内置规则：conflicting-length、unbounded-length、no-format-specified、vague-objective、multiple-tasks、missing-role。全都是非常初级的字符串匹配，对 skill/system prompt 这种长文档基本没用。

代码 270 行，7 个 commit，最后更新 2025-12-12，创建到停更只花了 12 天。

**值得借鉴的点：** 插件系统用 Python entry_points 做规则自动发现，我们最终也要做成这样的可扩展架构。但没必要基于它开发。

### alexmavr/promptsage (2026-03-26)

**结论：方向完全不同，对 promptlint 没有参考价值。**

不是 linter，是 prompt builder——把用户输入 + 示例 + 数据源拼成完整 prompt，附带访问控制和 prompt injection 检测（依赖外部 llm-guard 服务）。

2024 年 3 月的项目，从创建到停更只花了 9 天。思路属于 pre-agent 时代，现在的 prompt 工程已经完全变了。

### korchasa/promptlint (2026-03-26)

**结论：思路不错——把 best practice 规则交给 LLM 判断，比正则匹配灵活得多。值得借鉴。**

Go 写的 CLI 工具，编译为单二进制。内置 20 条 prompt engineering best practice 规则（YAML 格式），检查时把规则 + 待检查 prompt 一起发给 LLM，LLM 用 tool_call 返回结构化的违规列表（含原文 snippet + 修复建议）。

20 条规则涵盖：Clear Task Description、Include Examples、Provide Context、Balance Length、Be Specific and Clear、Use Step-by-Step Approach、Assign Persona、Include Edge Cases、Structure Complex Prompts 等。

实测效果：对故意写烂的 prompt 能报出 5 条具体问题且修复建议有参考价值；对已经较完整的 skill prompt 报 0 issue（可能太宽松，取决于模型）。

优点：规则质量高，LLM 判断灵活，输出实用。缺点：每次检查必须调 API，结果不稳定，规则偏通用不针对 skill/system prompt。README 自己写了 "This is a joke"。

### youcommit/promptlint (2026-03-26)

**结论：方向不同——不检查 prompt 质量，检查 prompt 里有没有敏感数据泄露。**

企业合规场景的工具。在 prompt 发给 LLM 之前扫描 PII（邮箱、电话、SSN、信用卡）、secrets（API key、AWS key、JWT）、内部主机名等。10 个内置 detector，全是正则匹配。策略用 YAML 配置（policy-as-code），支持 CI/CD 和 SARIF 输出。

实测能准确检出敏感信息（邮箱、SSN、内部 IP 等），带位置信息。但跟"prompt 写得好不好"完全无关。

2025 年 11-12 月，8 个 commit，0 star。

### Prompt Linter VS Code 插件 (2026-03-26)

**结论：思路同 korchasa——调 LLM 判断 prompt 质量，但包装成 VS Code 插件。无法 CLI/CI 集成。**

5 条规则分类：Role Clarity、Logical Conflicts、Input/Output Examples、Instruction Complexity、Emphasis Overuse。调 Claude API 做实时分析。

121 次安装，4 star，16 commit。必须有 Claude API key，只能在 VS Code 里用。服务器上无法试用。
