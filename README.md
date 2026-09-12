# xitter

Twitter/X CLI for agents: read timelines and mentions, post and reply, follow
and unfollow, and manage lists and bookmarks from the command line.

## Status

**Scaffold.** The domain surface described above is not implemented yet —
there is no X API client, no auth handling, and no timeline/post code in the
package today. What ships right now is the agent-first CLI skeleton and the
mesh-agent baseline this repo was scaffolded with:

- **An agent-first CLI** cited from [teken](https://github.com/agentculture/teken)
  (`afi-cli`) — the runtime package has no third-party dependencies.
- **A mesh identity** — `culture.yaml` (`suffix` + `backend`) plus the matching
  resident prompt file (`CLAUDE.md`, since `culture.yaml` declares
  `backend: claude`).
- **Four harness prompt files**, one per agent harness, each read by exactly
  one of them (see [Prompt files by harness](#prompt-files-by-harness)). All
  four harnesses are usable interactively regardless of which one
  `culture.yaml` names as the mesh resident.
- **The canonical guildmaster skill kit** under `.claude/skills/`, vendored
  cite-don't-import. See [`docs/skill-sources.md`](docs/skill-sources.md).
- **A build + deploy baseline** — pytest, lint, the agent-first rubric gate, a
  committed-secret scan, a per-harness config smoke check, and PyPI Trusted
  Publishing wired into GitHub Actions.

## Quickstart

```bash
uv sync
uv run pytest -n auto                 # run the test suite
uv run xitter whoami                  # identity from culture.yaml
uv run xitter learn                   # self-teaching prompt (add --json)
uv run teken cli doctor . --strict    # the agent-first rubric gate CI runs
```

## CLI

| Verb | What it does |
|------|--------------|
| `whoami` | Report this agent's nick, version, backend, and model from `culture.yaml`. |
| `learn` | Print a structured self-teaching prompt. |
| `explain <path>` | Markdown docs for any noun/verb path. |
| `overview` | Read-only descriptive snapshot of the agent. |
| `doctor` | Check the agent-identity invariants (prompt-file-present, backend-consistency). |
| `cli overview` | Describe the CLI surface itself. |

Every command supports `--json`. Results go to stdout, errors/diagnostics to
stderr (never mixed). Exit codes: `0` success, `1` user error, `2` environment
error, `3+` reserved.

The Twitter/X verbs (timeline, mentions, post, reply, follow, lists,
bookmarks) are **planned** and land as noun groups under the same contract —
see [`CLAUDE.md`](CLAUDE.md) for how a noun group registers.

## Prompt files by harness

Four harnesses, four root files, no shared base — each file is read by
exactly one harness:

| Harness | File(s) |
|---------|---------|
| Claude Code | [`CLAUDE.md`](CLAUDE.md) |
| Pi / associate | [`AGENTS.override.md`](AGENTS.override.md) + [`.pi/SYSTEM.md`](.pi/SYSTEM.md) |
| colleague | [`AGENTS.colleague.md`](AGENTS.colleague.md) |
| Qwen Code | [`QWEN.md`](QWEN.md) |

**Claude Code** — `CLAUDE.md` is the fullest write-up of the repo's
conventions; read it first.

**Pi / associate** — `AGENTS.override.md` replaces this directory's
`AGENTS.md`/`CLAUDE.md` in Pi's context layer, so Pi does not inherit
`CLAUDE.md`. `.pi/SYSTEM.md` replaces Pi's default system prompt with the
non-coding `associate` identity (read/find/summarize only).

**colleague** — colleague's prompt cascade is `AGENTS.md` →
`AGENTS.colleague.md` → `AGENTS.colleague.<model>.md`. This repo ships only
the middle layer: there is no `AGENTS.md` (a shared base across harnesses was
considered and rejected) and no per-model override file.

**Qwen Code** — Qwen Code reads `QWEN.md` and `AGENTS.md`; since there is no
`AGENTS.md`, `QWEN.md` is its sole source of guidance.

There is intentionally **no `AGENTS.md`** at the root — each harness gets an
unrelated file rather than cascading from a shared base. Change a repo
convention and all four files need the update in the same PR; nothing makes
them cascade.

## Two selections, not one

It is tempting to read "switch harness" as one decision. It is actually two,
and keeping them separate matters:

1. **The interactive harness** — which binary you run (`claude`, `pi`,
   `colleague`, `qwen`). `cd` into the clone and run any of them; all four
   are live simultaneously, and none of them requires editing a file or
   flipping a switch. A harness can be force-selected for one invocation
   (e.g. a CI smoke check) without ever touching `culture.yaml` — see
   [`docs/automation-contract.md`](docs/automation-contract.md).
2. **The mesh resident** — the single `backend` `culture.yaml` declares,
   which is what the Culture daemon starts and what `steward doctor`
   checks. `guild harness use <name>` changes only this.

`culture.yaml`'s `backend` affects (2) only. It never affects which harness
you can invoke interactively in (1). See
[`docs/harness-selection.md`](docs/harness-selection.md) for the full writeup.

## Development

```bash
uv run pytest -n auto --cov=xitter --cov-report=term   # coverage floor: 60%
uv run black xitter tests && uv run isort xitter tests # line length 100
uv run flake8 xitter tests
uv run bandit -c pyproject.toml -r xitter
python3 scripts/scan-secrets.py                        # committed-secret gate
uv run python scripts/harness-smoke.py --stage all --require config
```

Every PR bumps the version in `pyproject.toml` and adds a `CHANGELOG.md`
entry — even docs-only PRs. The `version-check` CI job blocks merge on the
version bump only (it compares `project.version` against `main`); the
changelog entry is convention, not an enforced gate. Pushing to `main`
publishes to PyPI via Trusted Publishing.

`markdownlint-cli2` is a Node tool and is not installed by `uv sync` —
`npm install -g markdownlint-cli2@0.21.0` (the version CI pins) if you want
to run the markdown lint locally.

See [`CLAUDE.md`](CLAUDE.md) for the full conventions and architecture.

## License

Apache 2.0 — see [`LICENSE`](LICENSE).
