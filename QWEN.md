# QWEN.md

This file provides guidance to Qwen Code when working with code in this
repository. Qwen Code's context loader reads exactly `QWEN.md` and `AGENTS.md`
in a directory; this repo deliberately ships only `QWEN.md` — there is no
`AGENTS.md` here (each harness gets its own file; see "Prompt files by
harness" below), so this file is the sole source of project guidance for a
Qwen Code session.

## What this project is

`xitter` is an AgentCulture mesh agent whose intended domain is a **Twitter/X
CLI for agents** — read timelines and mentions, post and reply, follow and
unfollow, manage lists and bookmarks, all from the command line.

**None of that domain surface exists yet.** On disk today is the scaffold this
repo was cloned from (`culture-agent-template`): the agent-first CLI skeleton,
a mesh identity, the vendored skill kit, and the CI/deploy baseline. There is
no X API client, no auth handling, and no tweet/timeline code in `xitter/`.
Some in-package strings (the parser description, `learn`'s body, `explain`'s
root entry, `overview`'s artifact list) still describe the repo as "a clonable
template for AgentCulture mesh agents" — leftover template prose, to be
rewritten as the domain verbs land.

It is a sibling to [`guildmaster`](https://github.com/agentculture/guildmaster)
(the **skills supplier**), [`steward`](https://github.com/agentculture/steward)
(**alignment** — `steward doctor`, the sibling-pattern baseline), and
[`teken`](https://github.com/agentculture/teken) (the **afi-cli** "Agent First
Interface" scaffolder this CLI is cited from) within the Organic Development
framework.

## Prompt files by harness

This repo's root carries one prompt file per agent harness, each read by
exactly one of them — there is no shared base file for them to inherit from:

- **Claude Code** → [`CLAUDE.md`](CLAUDE.md) (the fullest write-up; read it
  first if you are new to the repo).
- **Pi / associate** → [`AGENTS.override.md`](AGENTS.override.md) for context,
  plus [`.pi/SYSTEM.md`](.pi/SYSTEM.md) for its system prompt.
- **colleague** → [`AGENTS.colleague.md`](AGENTS.colleague.md).
- **Qwen Code** → this file.

Change a repo convention and all four files need the update in the same PR;
nothing makes them cascade, so they drift silently.

## Identity

Declared in `culture.yaml`:

```yaml
agents:
- suffix: xitter
  backend: claude
```

`backend: claude` fixes the *mesh resident* prompt file to `CLAUDE.md` — the
mesh runtime reads that file, not this one. A Qwen Code session working in a
clone of this repo is a separate, local tool session; it reads `QWEN.md`
regardless of what `culture.yaml` declares, and running Qwen Code here neither
requires nor changes that declaration. The declaration and the resident prompt
together satisfy the two invariants `steward doctor` verifies:
**prompt-file-present** and **backend-consistency** (`claude` ↔ `CLAUDE.md`).

Your project skills are discovered through `.qwen/skills`, a **relative**
symlink onto the one canonical `.claude/skills` tree. Do not replace it with a
real directory or an absolute link — `scripts/harness-smoke.py` fails the build
if you do, because a forked skill tree is how four harnesses silently stop
sharing one kit.

## The CLI

The CLI is cited (cite-don't-import) from teken's `python-cli` reference
(`teken cli cite`), so the runtime package has **no third-party dependencies**;
`teken` (a.k.a. `afi-cli`) is a dev dependency only. Adding an HTTP client for
the X API would break that property — treat it as a deliberate decision, not an
incidental one. Agent-first verbs:

- `xitter whoami` — identity from `culture.yaml`.
- `xitter learn` — structured self-teaching prompt.
- `xitter explain <path>` — markdown docs for any noun/verb.
- `xitter overview` — descriptive snapshot of the agent.
- `xitter doctor` — check the agent-identity invariants.
- `xitter cli overview` — describe the CLI surface itself.

Conventions: every command supports `--json`; results go to stdout, errors and
diagnostics to stderr (never mixed); exit codes are `0` success, `1` user
error, `2` environment error, `3+` reserved. Failures raise `CliError` and are
formatted centrally — no Python traceback ever reaches stderr. The agent-first
rubric is enforced in CI by `teken cli doctor . --strict`.

The planned Twitter/X verbs land as noun groups under that same contract; each
registers in `xitter/cli/_commands/`, is wired into `_build_parser()`, and
needs a matching entry in `xitter/explain/catalog.py`.

## Skills

`.claude/skills/` vendors the **canonical guildmaster skill kit**
(cite-don't-import). Provenance and the re-sync procedure live in
`docs/skill-sources.md`. Do not reformat or edit vendored scripts — re-sync
from guildmaster instead.

## Conventions

- **Every PR bumps the version** — even docs/config/CI. Use the
  `version-bump` skill; the `version-check` CI job blocks merge otherwise.
- **Tests**: `uv run pytest -n auto`. Most of the suite guards *repo
  structure* (harness configs, registry agreement, the secret scanner) rather
  than the package — breaking the layout breaks tests, by design.
- **Lint**: black, isort, flake8 (line length 100), bandit, markdownlint, plus
  `python3 scripts/scan-secrets.py`, which rejects credential-shaped strings
  and non-localhost endpoints in JSON config. X API credentials belong in the
  environment, never in a tracked file.
- **Deploy**: pushing to `main` publishes to PyPI via Trusted Publishing
  (`.github/workflows/publish.yml`); PRs do a TestPyPI dry-run.

## Layout

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

This file describes the repository **as it exists on disk today**. When you
edit, keep claims grounded in checked-in reality; if a section drifts ahead of
reality, mark it `(planned)` or move it under a `## Roadmap` heading. For the
full set of workflow conventions (the CLI dispatch contract, `doctor`'s two
registries, memory discipline, `ask-colleague` usage), see
[`CLAUDE.md`](CLAUDE.md) — those conventions apply to work in this repo
regardless of which harness is doing it.
