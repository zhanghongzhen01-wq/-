# Evolution Proposal: 处理广告数据时始终附带父级广告组名称，避免逐个点开查看

- Proposal-ID: evo-2026-07-01-ad-group-parent-name
- Status: approved
- Signature: ad-group-parent-name
- Created-At: 2026-07-01 16:05
- Last-Seen-At: 2026-07-01 16:05
- Target-File: MEMORY.md
- Trigger-Type: preference
- Confidence: medium

## Why This Matters
- 处理广告数据时始终附带父级广告组名称，避免逐个点开查看

## Evidence
- Interactive proposal card was present in the session UI.
- The original pending draft file was unavailable at approval time.
- AutoClaw reconstructed this draft from the proposal payload so the review result can still be recorded.

## Duplicate Check
- Checked: pending draft path + signature/proposal fallback
- Result: original draft file missing
- Decision: create surrogate draft from proposal payload

## Proposed Change
### MEMORY.md — 广告数据展示规范

---
summary: "Long-term memory record"
autoclaw.schema: "agent-profile/v1"
human.name: "张鸿臻"
human.call: "张鸿臻"
human.timezone: "Asia/Shanghai"
human.focus:
  - "general assistance"
agent.name: "AutoClaw"
agent.role: "AI coworker"
agent.style:
  - "sharp"
  - "resourceful"
  - "no-nonsense"
agent.emoji: "🦞"
notes.project:
  - "Current project not recorded yet"
notes.workflow:
  - "每天早上9点收集3个有趣的编程项目或开源工具并推送"
  - "处理广告数据（广告组/广告词组/广告）时，任何列表或报告都必须同时展示父级名称：广告词组要标出所属广告组，广告要标出所属广告词组+广告组。避免张鸿臻需要逐个点开查看归属关系"
notes.memory:
  - "Summarize stable facts and working patterns"
notes.tools:
  - "Record important tools, services, and local setup here"
lessons:
  - "Confirm before making risky changes"
  - "Persist important facts so they survive the session"

# MEMORY.md — Long-Term Memory

## 主人信息
- **Name**: 张鸿臻
- **Timezone**: Asia/Shanghai
- **Language**: 中文
- **First online**: 2026-06-30

## 身份
- **AutoClaw** — AI coworker 🦞
- **Creature**: sharp, resourceful, no-nonsense
- **Emoji**: 🦞

## 当前项目
- **Current project not recorded yet**
- **代码仓库**: _(待补充)_
- **主要分支**: _(待补充)_

## 系统架构
- **Gateway**: _(待补充)_
- **模型**: _(待补充)_
- **渠道**: _(待补充)_
- **浏览器**: _(待补充)_

## 工作流
- **每日开源项目推送**：每天早上9:00（北京时间）自动搜索并收集3个当天有趣的编程项目或开源工具，推送给张鸿臻。数据来源：GitHub Trending、Hacker News、Product Hunt。收集标准：新颖实用、有社区热度、覆盖不同技术领域。推送渠道：飞书。
- **广告数据展示规范**：处理广告相关数据（广告组→广告词组→广告 三级结构）时，任何列表、报告、导出都必须同时展示父级归属名称。具体：列出广告词组时附带所属广告组名称，列出广告时附带所属广告词组+广告组名称。原因是张鸿臻不想逐个点开查看归属关系，一次性看清全貌。

## 记忆系统架构
OpenClaw 三层记忆：
1. **MEMORY.md** — 精选长期记忆（核心事实/偏好）
2. **memory/YYYY-MM-DD.md** — 每日记忆日志（append-only）
3. **sessions/** — 会话历史（JSONL 格式，仅短期）

## 开发工具链
- Record important tools, services, and local setup here

## 待探索
- _(待补充)_

## 重要教训
1. Confirm before making risky changes
2. Persist important facts so they survive the session

## 技能索引
见 workspace/.agents/skills/ 目录下的 SKILL.md 文件

## Apply Plan
1. Keep this reconstructed draft as the approval artifact.
2. Record the proposal content exactly as shown in the interactive card.
3. Append an audit note after approval or rejection.

## User Approval
- Approve: 批准 evo-2026-07-01-ad-group-parent-name
- Reject: 拒绝 evo-2026-07-01-ad-group-parent-name