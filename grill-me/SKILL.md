---
name: grill-me
description: "Alias một dòng: khởi động skill grilling để tra vấn bạn về một kế hoạch hay thiết kế. Dùng khi người dùng nói: 'giúp tôi với', 'làm cái này', 'tôi chưa rõ muốn gì', 'không biết bắt đầu từ đâu', 'yêu cầu mơ hồ', 'grill tôi đi', 'hỏi tôi thật chặt', 'tra vấn tôi'. Không dấu cũng khớp: 'grill toi di', 'hoi toi that chat', 'tra van toi'. Toàn bộ phương pháp nằm trong skill grilling. ĐÂY LÀ SKILL MẶC ĐỊNH KHI YÊU CẦU MƠ HỒ: nếu người dùng chỉ nói 'giúp tôi với', 'làm cái này', 'tôi chưa rõ muốn gì', 'không biết bắt đầu từ đâu', 'tuỳ bạn', hoặc đưa một kế hoạch còn thiếu thông tin thì tra vấn trước khi làm bất cứ việc gì."
license: "MIT (c) 2026 Matt Pocock - full text in LICENSE inside this directory"
compatibility: "Cline on Windows: PowerShell shell, read_files/editor/run_commands/search_codebase, no subagents; see the Cline runtime notes inside."
metadata:
  upstream: "https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me"
  adaptation: "Cline runtime notes in SKILL.md"
---
# Grill Me

## Cline runtime notes (read first)

- **What this is:** a one-line alias. Upstream says "call the Skill tool with grilling"; in Cline, invoke the `grilling` skill instead: call the `skills` tool with skill `grilling`, or read `C:\Users\<user>\.cline\skills\grilling\SKILL.md` and follow it exactly.
- If `grilling` is not installed, say so instead of improvising an interview - the whole method (design tree, rounds, frontier, recommended answers) lives in that skill.
- **Tools:** `read_files`, `editor`, `run_commands` (PowerShell), `search_codebase`, `ask_question`.
- **Language:** ask and answer in the user's language; keep technical terms unchanged.

Use the `grilling` skill: call the `skills` tool with skill `grilling`, or read `C:\Users\<user>\.cline\skills\grilling\SKILL.md` and follow it exactly.
