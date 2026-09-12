# AGENTS.override.md

This file is the **context layer** for the Pi harness (the `pi` CLI, and the
`associate` non-coding harness modelled on it) when it runs inside this repo.
Pi's CONTEXT loader concatenates `AGENTS.md` or `CLAUDE.md` from its user-level
config directory (see Pi's own docs), each parent directory, and the working
directory — but an `AGENTS.override.md`
present in a directory replaces that directory's `AGENTS.md`/`CLAUDE.md` entry
outright rather than adding to it. That is why this repo ships this file
instead of an `AGENTS.md`: Pi must **not** inherit `CLAUDE.md` (the Claude Code
guidance file) — the two harnesses read the same repository very differently,
and `CLAUDE.md` assumes a coding session with full repo-write authority that
Pi's non-coding lane does not have.

The identity and behavioral bounds for that lane — who Pi is here, what it may
and may not do — live one layer up, in Pi's **system prompt** file,
[`.pi/SYSTEM.md`](.pi/SYSTEM.md). That file replaces Pi's default
coding-assistant system prompt entirely. This file is project *context* only:
what the repo is and how it is laid out, not who is reading it.

## What this project is

`xitter` is an AgentCulture mesh agent whose intended domain is a **Twitter/X
CLI for agents** — read timelines and mentions, post and reply, follow and
unfollow, manage lists and bookmarks, all from the command line.

**None of that domain surface exists yet, and that matters for your answers.**
On disk today is the scaffold this repo was cloned from
(`culture-agent-template`): the agent-first CLI skeleton (`whoami`, `learn`,
`explain`, `overview`, `doctor`, `cli overview`), a mesh identity, the vendored
skill kit, and the CI/deploy baseline. There is no X API client, no auth
handling, and no tweet/timeline code anywhere in `xitter/`. If you are asked
"how does xitter post a tweet?", the honest answer is that it doesn't yet —
report the gap rather than reading intent into the package description.

Watch for one specific trap when summarizing: several in-package strings (the
parser description, `learn`'s body, `explain`'s root entry, `overview`'s
artifact list) still describe the repo as "a clonable template for AgentCulture
mesh agents". That is leftover template prose, not a second identity. Quoting
it as the project's purpose would be repeating a known-stale string.

It is a sibling to [`guildmaster`](https://github.com/agentculture/guildmaster)
(the skills supplier), [`steward`](https://github.com/agentculture/steward)
(alignment), and [`teken`](https://github.com/agentculture/teken) (the CLI
scaffolder this package is cited from).

## Four harnesses, four files, no shared base

This repo's root carries one prompt file per harness, each read by exactly
one of them — there is deliberately no shared `AGENTS.md` base for them to
cascade from:

- **Claude Code** reads [`CLAUDE.md`](CLAUDE.md).
- **Pi / associate** reads this file (`AGENTS.override.md`) for context, plus
  [`.pi/SYSTEM.md`](.pi/SYSTEM.md) for its system prompt.
- **colleague** reads [`AGENTS.colleague.md`](AGENTS.colleague.md) (the start
  of colleague's own cascade — see that file).
- **Qwen Code** reads [`QWEN.md`](QWEN.md).

If you are reading this as a human, `CLAUDE.md` is the fullest write-up of the
repo's conventions and is the one to read first; the other three exist to keep
each non-Claude harness from silently inheriting Claude-specific instructions
it cannot act on the same way. Because nothing makes the four cascade, they
drift — if you are asked to compare them, check each file rather than assuming
they agree.

## Identity

Declared in `culture.yaml`:

```yaml
agents:
- suffix: xitter
  backend: claude
```

This agent's *mesh* resident runs on `backend: claude`, so `CLAUDE.md` is the
live resident prompt. A Pi session working in a clone of this repo is a
**local tool session**, not the mesh resident — it reads this file and
`.pi/SYSTEM.md` regardless of what `culture.yaml` declares, and running `pi`
here neither requires nor changes that declaration.

(A clone that wants `associate` as its *mesh* resident declares
`backend: colleague` with `model: associate` — see `docs/skill-sources.md`.
That is a per-clone choice; this repo does not ship it.)

## Layout (what you can read/find/summarize here)

```text
xitter/                   agent-first CLI (cited from teken's python-cli reference)
  cli/                    parser, error/output contract, _commands/ (verbs)
  explain/                markdown catalog for `explain`
tests/                    pytest CLI tests + repo-structure guard tests
scripts/                  scan-secrets.py, harness-smoke.py (both CI gates)
.claude/skills/           vendored guildmaster skill kit (cite-don't-import)
docs/skill-sources.md     skill provenance ledger
culture.yaml              mesh identity (suffix + backend)
.github/workflows/        tests + deploy (PyPI Trusted Publishing)
```

Your skills are discovered through `.pi/skills`, a relative symlink onto the
one canonical `.claude/skills` tree — the same files Claude Code, colleague and
Qwen Code load, not a Pi-specific copy.

## Conventions worth knowing before you answer a question about this repo

- The CLI has a strict output contract that shapes what any command you run
  here prints: **results on stdout, errors and diagnostics on stderr, never
  mixed**; every verb takes `--json`; exit codes are `0` success, `1` user
  error, `2` environment error. A failure surfaces as `error:` + `hint:` lines,
  never a Python traceback — so a traceback, if you ever see one, is itself the
  finding.
- Most of `tests/` guards *repo structure* (harness configs, registry
  agreement, the secret scanner) rather than the package. A failing test there
  usually means a layout or config file moved, not that the CLI broke.
- The vendored skills under `.claude/skills/` are cited **verbatim** from
  guildmaster — never propose editing their scripts; the fix belongs upstream
  (`docs/skill-sources.md` has the re-sync procedure).
- The runtime package deliberately has **zero third-party dependencies**
  (`dependencies = []`); `culture.yaml` is parsed by hand rather than with a
  YAML library to keep it that way. Note it if a question implies adding one.
- Every PR bumps the version (`version-bump` skill); CI's `version-check` job
  blocks merge otherwise.
- This file describes the repo **as it exists on disk today**. If you are
  asked to update it, keep claims grounded in checked-in reality — and per
  `.pi/SYSTEM.md`, draft the change for someone else to apply rather than
  writing it yourself.
