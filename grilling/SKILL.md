---
name: grilling
description: "Phỏng vấn dồn dập để stress-test một kế hoạch hoặc quyết định, theo cây quyết định, từng vòng câu hỏi, mỗi câu kèm đáp án gợi ý. Dùng khi người dùng nói: 'yêu cầu mơ hồ', 'chưa rõ phạm vi', 'không biết bắt đầu từ đâu', 'tra vấn tôi', 'hỏi dồn dập', 'stress test kế hoạch', 'phản biện kế hoạch', 'làm rõ yêu cầu'. Không dấu cũng khớp: 'tra van toi', 'hoi don dap', 'stress test ke hoach', 'phan bien ke hoach', 'lam ro yeu cau'. Dừng khi frontier rỗng: mọi nhánh của cây quyết định đã được hỏi. Cũng dùng khi yêu cầu mơ hồ hoặc thiếu thông tin, trước khi giao việc cho skill khác. Kết hợp: tra vấn xong mới chuyển sang archify, otchet hoặc skill-creator."
license: "MIT (c) 2026 Matt Pocock - full text in LICENSE inside this directory"
compatibility: "Cline on Windows: PowerShell shell, read_files/editor/run_commands/search_codebase, no subagents; see the Cline runtime notes inside."
metadata:
  upstream: "https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling"
  adaptation: "Cline runtime notes in SKILL.md"
---
# Grilling

## Cline runtime notes (read first)

- **Skill directory:** the folder holding this `SKILL.md`, written `<skill>` below. Installed: `C:\Users\<user>\.cline\skills\grilling\`; source repo: `E:\Private\Projects\Cline-Skills\grilling\`.
- **Tools:** `Read` -> `read_files`; `Write`/`Edit` -> `editor`; shell -> `run_commands` (PowerShell); search -> `search_codebase`; asking the user -> `ask_question` when a single choice is needed, otherwise numbered questions in the reply.
- **One round = one message.** Ask the whole frontier in a single reply, numbered, each with your recommended answer, then stop and wait. Do not drip one question per message, and never start the next round before the user answers this one.
- **No subagents.** Where the upstream text says to dispatch a sub-agent with a fresh context to find a fact, do that lookup yourself with `read_files`, `search_codebase` or `run_commands`, state the fact you found, and ask only the questions downstream of it. Do not ask the user for anything you can read from disk.
- **Facts are yours, decisions are the user's.** Lookups are yours to do; every decision goes to the user and waits.
- **Language:** ask in the user's language; keep technical terms, file paths and identifiers unchanged.
- **Stop condition:** the frontier is empty. Then list the settled decisions in one block, and act only after the user confirms that you understood each other.

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Word each question so "yes" accepts your recommended answer.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent with a fresh context window to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.
