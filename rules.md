# promptlint 规则清单

## 硬编码规则（不依赖 LLM，共 5 条）

### H1. max-lines — 文件行数上限

SKILL.md 推荐 40-100 行，超出后重要指令容易被淹没。

- 默认阈值：100 行（SKILL.md）
- 可配置

**来源：**
- [Claude Code Skills 文档](https://code.claude.com/docs/en/skills) — SKILL.md 推荐 40-100 行，加载后 <5K tokens
- [SKILL.md 架构指南 (MindStudio)](https://www.mindstudio.ai/blog/claude-code-skills-architecture-skill-md-reference-files)
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) — "如果 CLAUDE.md 太长，Claude 会忽略一半内容"
- ["Same Task, More Tokens" (ACL 2024)](https://arxiv.org/abs/2402.14848) — 推理能力在 ~3,000 tokens 时开始下降

### H2. max-filesize — 文件大小上限

Prompt 文件过大会导致 token 预算浪费，模型容易忽略关键指令。

- 默认阈值：10 KB
- 可配置（`max_bytes`）
- 按 UTF-8 编码计算字节数（中文字符占 3 字节）

**来源：**
- [Claude Code Skills 文档](https://code.claude.com/docs/en/skills) — SKILL.md 加载后 <5K tokens
- ["Same Task, More Tokens" (ACL 2024)](https://arxiv.org/abs/2402.14848) — 推理能力在 ~3,000 tokens 时开始下降

### H3. path-exists — 引用的绝对路径必须存在

检测 prompt 中引用的绝对路径（如 `/home/user/tool.py`），验证是否真实存在。

- 自动跳过 URL 中的路径
- 已实现

**来源：** 自研规则，无外部来源。

### H4. unclosed-xml-tags — XML 标签未闭合

Anthropic 和 OpenAI 都推荐用 XML 标签组织 prompt。未闭合的标签会导致模型解析混乱。

```
❌ <instructions>
     Do something.
   （忘记 </instructions>）

✅ <instructions>
     Do something.
   </instructions>
```

**来源：**
- [Anthropic Claude 4 Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) — "Use XML tags to structure complex prompts"
- [OpenAI GPT-4.1 Prompting Guide](https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide) — "Use Markdown or XML as delimiters"

### H5. excessive-caps — ALL-CAPS 强调词密度过高

少量 CAPS 可以提高遵循度，但过度使用会适得其反——模型对所有指令同等"紧张"，反而抓不住重点。

```
❌ "CRITICAL: You MUST ALWAYS use this tool. NEVER skip this step.
    IMPORTANT: You MUST follow these rules EXACTLY."

✅ "Use this tool when processing user queries.
    IMPORTANT: Never skip validation for financial transactions."
```

- 检测方式：统计 ALL-CAPS 词（MUST, ALWAYS, NEVER, CRITICAL, IMPORTANT 等）占总词数的比例
- 阈值待定

**来源：**
- [Anthropic Claude 4 Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) — "Claude 4.5/4.6 对 system prompt 更敏感，避免过度强调性语言"
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) — "可以用 IMPORTANT 提高遵循度，但不要过度使用"

---

## LLM 解释型规则（需要 LLM 判断，共 7 条）

### L1. suggestive-language — 建议性语言用于需要行动的场景

在需要模型执行操作的 prompt 中，使用 "Can you suggest..."、"Maybe you could..." 等语言会导致模型犹豫不决。正则能抓到明显模式，但在示例、引用中出现时不该报——需要 LLM 理解上下文。

```
❌ "Can you suggest some changes to improve this function?"
❌ "Maybe you could refactor the login module?"
❌ "Would it be possible to add error handling?"

✅ "Refactor the login module to use async/await."
✅ "Add error handling for network timeouts in this function."
```

**来源：**
- [Anthropic Claude 4 Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) — "Use explicit action directives, not suggestive language"

### L2. hollow-instructions — 空洞指令

删掉也不会改变模型行为的指令——因为模型本来就会尽力做到。它们浪费 token 预算但不提供引导。空洞短语列表永远列不全，需要 LLM 判断一条指令是否真正提供了有用的约束。

> 判断标准：对 prompt 的每一行问自己：**"删掉它会导致模型犯错吗？"** 如果不会，就是噪音，应该删掉。
>
> — [Anthropic Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)

```
❌ "Be helpful and accurate"
❌ "Write clean, maintainable code"
❌ "Think carefully before responding"
❌ "Provide high-quality answers"
❌ "Be concise and clear"

✅（有信息量的替代）
   "Use snake_case for variables, camelCase for functions"
   "Keep functions under 20 lines"
   "Respond in Chinese"
```

**来源：**
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) — "对每行问：删掉它会导致 Claude 犯错吗？"

### L3. vague-instructions — 指令不够具体清晰

模糊指令让模型靠猜测行事。Anthropic 的黄金法则：把 prompt 给一个不了解任务的同事看，如果他会困惑，模型也会困惑。

```
❌ "处理一下用户数据"
❌ "优化这段代码"
❌ "写个好一点的版本"

✅ "将 users 表中 created_at 早于 2024-01-01 的记录标记为 inactive"
✅ "将这个 O(n²) 的嵌套循环改为使用 hash map，降低到 O(n)"
```

**来源：**
- [Anthropic Claude 4 Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) — "Golden rule: show your prompt to a colleague unfamiliar with the task"
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering) — "Include details in your query to get more relevant answers"

### L4. contradictory-instructions — 指令之间矛盾

矛盾的指令迫使模型消耗推理能力去调和冲突，降低实际任务的输出质量。

```
❌ "Always respond in JSON format.
    ...
    Write your answer as a natural paragraph."

❌ "Keep responses under 100 words.
    ...
    Provide comprehensive, detailed explanations."

❌ "Never use external tools.
    ...
    Search the web when you don't know the answer."
```

**来源：**
- [OpenAI GPT-5 Prompting Guide](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide) — "矛盾指令会消耗 reasoning tokens 去调和，降低性能"
- [Anthropic Claude 4 Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)

### L5. negative-only-instructions — 只有否定没有正向替代

告诉模型"别做 X"但不说该做什么，模型缺少正面目标，容易产生不符合预期的替代行为。

```
❌ "Do not use markdown formatting"
✅ "Write your response as smoothly flowing prose paragraphs"

❌ "Don't make up information"
✅ "Only answer based on the provided documents. If the answer isn't there, say 'I don't have that information'"

❌ "Never use bullet points"
✅ "Present information in complete sentences within paragraphs"
```

**来源：**
- [Anthropic Claude 4 Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) — "Tell Claude what to do, not just what not to do"

### L6. style-mismatch — prompt 风格与期望输出不一致

prompt 本身的写作风格会影响模型的输出风格。如果 prompt 满是 markdown，输出也会充满 markdown——即使你希望输出纯文本。

```
❌ prompt 用 markdown 写，但期望输出纯文本对话
❌ prompt 用正式学术语气，但期望输出是轻松的聊天风格
❌ prompt 用英文写，但期望输出中文

✅ prompt 风格与期望输出一致
```

**来源：**
- [Anthropic Claude 4 Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) — "Your prompt's formatting style influences Claude's output style"

### L7. over-engineering — 过度工程化

prompt 中塞满了"以防万一"的防御性指令，分散模型注意力，导致过度谨慎、产出臃肿。

```
❌ "Before making any changes, always create a backup.
    Add comprehensive error handling for all edge cases.
    Add type annotations to all functions.
    Add docstrings to all functions.
    Consider backwards compatibility.
    Create abstractions for reusable patterns.
    Add feature flags for new functionality."

✅ "Fix the bug in the login function."
```

判断标准：指令是否与当前任务直接相关？如果是"通用好习惯"但跟任务无关，就是过度工程化。

**来源：**
- [Anthropic Claude 4 Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) — "Don't add features, refactor code, or make 'improvements' beyond what was asked"
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)
