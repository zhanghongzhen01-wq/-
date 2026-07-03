# Evolution Proposal: 用户明确偏好输出文件使用 Excel 和 HTML 格式，拒绝 txt 纯文本。将此持久偏好记录到 MEMORY.md。

- Proposal-ID: evo-2026-07-01-output-format-preference
- Status: approved
- Signature: output-format-preference
- Created-At: 2026-07-01 15:17
- Last-Seen-At: 2026-07-01 15:17
- Target-File: MEMORY.md
- Trigger-Type: preference
- Confidence: medium

## Why This Matters
- 用户明确偏好输出文件使用 Excel 和 HTML 格式，拒绝 txt 纯文本。将此持久偏好记录到 MEMORY.md。

## Evidence
- Interactive proposal card was present in the session UI.
- The original pending draft file was unavailable at approval time.
- AutoClaw reconstructed this draft from the proposal payload so the review result can still be recorded.

## Duplicate Check
- Checked: pending draft path + signature/proposal fallback
- Result: original draft file missing
- Decision: create surrogate draft from proposal payload

## Proposed Change
### MEMORY.md — 新增输出格式偏好

---
summary: "Long-term memory record"
autoclaw.schema: "agent-profile/v1"
human.name: "张鸿臻"
human.call: "张鸿臻"
human.timezone: "Asia/Shanghai"
human.focus:
  - "marketing"
  - "广告投放"
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
  - "输出文件格式优先 Excel (.xlsx) 和网页 (.html)，不要给 txt 纯文本"
notes.memory:
  - "Summarize stable facts and working patterns"
notes.tools:
  - "Record important tools, services, and local setup here"
lessons:
  - "Confirm before making risky changes"
  - "Persist important facts so they survive the session"
---

# MEMORY.md — Long-Term Memory

## 主人信息
- **Name**: 张鸿臻
- **Timezone**: Asia/Shanghai
- **Language**: 中文
- **First online**: 2026-07-01

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
- **输出文件格式**：所有脚本/程序输出文件默认给 Excel (.xlsx) + 网页 (.html) 两种格式，不输出 txt 纯文本（太丑）。除非用户明确说只要 txt。

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
- Approve: 批准 evo-2026-07-01-output-format-preference
- Reject: 拒绝 evo-2026-07-01-output-format-preference