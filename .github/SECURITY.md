# Security Policy

This repository holds **instruction files and helper scripts** that an AI coding
agent loads and runs. That makes two classes of problems interesting here: bugs in
the scripts themselves, and skill text that could steer an agent into doing
something harmful.

## Supported versions

| Version | Supported |
|---------|-----------|
| `main` (latest commit) | Yes |
| Any older commit, tag or fork | No |

There are no releases and no deployed service. Only the tip of `main` is
maintained; the fix for a reported issue is to pull the latest commit.

## Reporting a vulnerability

**Preferred:** open a private report — go to the **Security** tab of this
repository and press **Report a vulnerability**. The report stays private between
you and the maintainers until a fix is ready.

**If that button is not available,** open a short issue that contains *no*
technical detail: say that you have a security report and name the affected skill.
A private channel will be arranged before anything technical is written down.

Please do **not** open a public issue containing a working exploit, credentials,
personal data, or a full prompt-injection payload that has not been fixed yet.

### What to include

- the skill and file path, for example `injection-scan/scripts/scan_injection.ps1`
  or `otchet/SKILL.md`
- the commit SHA you tested
- impact: what an attacker gains, and who triggers it (the user, another skill,
  a document the agent reads, a scheduled run with nobody watching)
- reproduction steps, minimal and self-contained
- whether the same problem exists in the vendored upstream project (see below)
- the affected platform (Windows / Linux / macOS) when it matters

### What to expect

- acknowledgement: within 3 business days
- initial assessment: within 10 business days
- fix or mitigation: depends on severity, coordinated with you
- credit in the fix commit or advisory if you want it

This is a personal project maintained on spare time. Those are best-effort
targets, not contractual guarantees.

## Scope

**In scope**

- scripts in this repository (PowerShell, Python, Node): command injection, path
  traversal, unsafe temporary files, secrets written to disk or to logs,
  redaction that silently fails open, data loss in batch operations
- skill instructions (`SKILL.md`, `references/`, `assets/`): text that would make
  an agent read or leak credentials, exfiltrate file contents, run destructive
  commands, or skip a confirmation step. A prompt-injection payload hidden in a
  skill counts as a vulnerability
- the adaptation layer: `tools/adapt_skill.py`, `tools/sync_upstream.py`,
  `tools/check_upstream.py`, and the workflows in `.github/workflows/`
- supply chain: a SHA pinned in `upstream.json` that does not match the code
  actually vendored, or vendored code that differs from the pinned upstream commit

**Out of scope**

- vulnerabilities in the agent or editor that runs the skills (Cline, VS Code,
  the CLI). Report those to that project; if our skill makes one of their issues
  worse, tell us as well
- model behaviour without a security impact (refusals, hallucinations, style)
- bugs that exist only in a vendored upstream skill: report upstream. Tell us too
  and we will pull the fix, but the root cause is theirs
- issues that require administrator rights, physical access, or an already
  compromised machine
- denial of service through oversized inputs, unless memory-safety or data loss
  is involved
- the sample/template documents in `assets/` being "wrong" for a specific teacher
  or university

## Upstream projects

Most skills are vendored copies of external projects, pinned in `upstream.json`:

`addyosmani/agent-skills`, `pbakaus/impeccable`, `Leonxlnx/taste-skill`,
`iart-ai/manim-skills`, `tt-a1i/archify`.

Skills from `anthropics/skills` are **not** vendored here: their license forbids
redistribution, so they are kept in a private repository. Do not report issues in
those files against this repository.

Security fixes for vendored files belong upstream; this repository only re-syncs them.
The exceptions written here are `otchet`, `injection-scan` and the `tools/` scripts.
If a vendored file inherits a serious bug, we will patch or drop it locally while
the upstream fix is pending, and say so in the commit message — the `archify`
lockfile carries exactly such a patch (`fast-uri`).

## Reporting secrets

Never paste a live token, password, cookie, session file or private key, not even
in a private report. Redact it, or quote only its prefix and length
(`sk-...`, 51 characters). If a real secret slipped into an issue or a pull
request by mistake, rotate it immediately and tell us so the content can be
removed.

## Safe harbour

If you test within this policy, in good faith, on your own machine and your own
data, we will not pursue legal action or report you. Please do not run tests
against infrastructure you do not own, do not access other people's data, and do
not use a finding to drop or alter files outside a sandbox you control.

## No bug bounty

This project has no bounty programme and no payment for reports. Reports are still
read, answered, and credited.

## Hardening you can apply yourself

The skills here are instructions, so the real boundary is the agent runtime. Before
reporting "the skill could run anything", check whether the runtime was configured
to allow it: approval prompts, per-action auto-approve, sandbox mode and file
system limits are set in the agent, not in this repository. The
`injection-scan` skill exists precisely because scanning text is a soft layer and
not a substitute for that boundary.

