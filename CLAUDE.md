# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`xitter` is an AgentCulture mesh agent whose intended domain is a
**Twitter/X CLI for agents** — read timelines and mentions, post and reply,
follow and unfollow, manage lists and bookmarks, all from the command line.

**None of that domain surface exists yet.** What is on disk today is the
scaffold cloned from `culture-agent-template`: the agent-first CLI skeleton
(`whoami`, `learn`, `explain`, `overview`, `doctor`, `cli overview`), the mesh
identity, the vendored skill kit, and the CI/deploy baseline. There is no X API
client, no auth handling, and no tweet/timeline code anywhere in `xitter/`.
Several strings in the package (the parser description, `learn`'s body,
`explain`'s root entry, `overview`'s artifact list) still describe the repo as
"a clonable template for AgentCulture mesh agents" — that is leftover template
prose, and it should be rewritten to describe the X CLI as the domain verbs
land. Keep claims in docs grounded in what is actually checked in; mark
anything ahead of reality as `(planned)`.

Siblings in the Organic Development framework:
[`guildmaster`](https://github.com/agentculture/guildmaster) (skills supplier),
[`steward`](https://github.com/agentculture/steward) (alignment,
`steward doctor`), [`teken`](https://github.com/agentculture/teken) (the
`afi-cli` scaffolder this CLI is cited from).

## Commands

```bash
uv sync                                   # install (dev group included)

uv run pytest -n auto                     # full suite, parallel (what CI runs)
uv run pytest tests/test_cli.py -v        # one file
uv run pytest tests/test_cli.py::test_whoami_json -v   # one test
uv run pytest -n auto --cov=xitter --cov-report=term   # with coverage (fail_under = 60)

uv run black --check xitter tests         # CI lint gate, in order
uv run isort --check-only xitter tests
uv run flake8 xitter tests                # line length 100
uv run bandit -c pyproject.toml -r xitter
markdownlint-cli2 "**/*.md" "#node_modules" "#.local" "#.claude/skills"
python3 scripts/scan-secrets.py           # committed-credential / endpoint gate
uv run teken cli doctor . --strict        # agent-first rubric gate
uv run python scripts/harness-smoke.py --stage all --require config

uv run xitter whoami                      # the CLI itself (every verb takes --json)
```

`black`/`isort`/`flake8` all agree on line length 100; run `black xitter tests`
and `isort xitter tests` to fix rather than hand-wrapping.

## Architecture

### CLI dispatch and the output contract

`xitter/cli/__init__.py` is the whole control flow, and three invariants there
are load-bearing for every command you add:

- **Errors never escape as tracebacks.** Handlers raise
  `CliError(code, message, remediation)` from `xitter/cli/_errors.py`;
  `_dispatch()` catches it, and wraps any other exception into a `CliError`
  rather than letting it surface. Exit codes: `0` success, `1` user error,
  `2` environment error, `3+` reserved.
- **Argparse errors route through the same contract.** `_CliArgumentParser`
  overrides `.error()`, and subparsers are built with
  `parser_class=_CliArgumentParser` so the override propagates. Because
  parse-time failures happen before `args.json` exists, `main()` pre-scans raw
  argv for `--json` into the class-level `_json_hint`. A new noun group that
  calls `add_subparsers()` must pass `parser_class=type(p)` (see
  `_commands/cli.py`) or its parse errors bypass the contract.
- **stdout and stderr never mix.** `_output.py`: results to stdout
  (`emit_result`), errors and diagnostics to stderr (`emit_error`,
  `emit_diagnostic`). Text-mode errors render `error:` + `hint:` lines; the
  `hint:` prefix is required by the agent-first rubric.

### Adding a verb or noun group

1. Add `xitter/cli/_commands/<name>.py` exposing `register(sub)` that adds a
   parser, a `--json` flag, and `set_defaults(func=...)`.
2. Register it in `_build_parser()` (there's a marked spot for noun groups).
3. Add a catalog entry in `xitter/explain/catalog.py` — `ENTRIES` is keyed by
   command-path tuples, and `tests/test_cli.py::test_every_catalog_path_resolves`
   walks them all. Every registered path should have one.
4. Any noun that gains action verbs must also expose `<noun> overview` — the
   rubric's `overview_cli_noun_exists` check, enforced by
   `teken cli doctor . --strict` in CI.
5. Descriptive verbs must not hard-fail on a bad target path (see
   `overview`'s ignored optional `target`).

### Identity and `doctor`

`whoami` finds `culture.yaml` by walking up from `__file__` — deliberately *not*
the CWD, so the identity reported is the agent's own — and parses it with a
hand-rolled line reader so the **runtime package keeps zero third-party
dependencies** (`dependencies = []` in `pyproject.toml`; `teken`, `pyyaml` etc.
are dev-only). Adding an HTTP client for the X API breaks that property; treat
it as a deliberate decision, not an incidental one.

`doctor` (`_commands/doctor.py`) carries **two tables that must not be
conflated**:

- `_PROMPT_FILE` — every prompt file *recognized* under a backend name (several
  interactive harnesses ride one backend).
- `_RESIDENT_PROMPT` — the *one* file the Culture daemon reads for a resident on
  that backend. This is what the health check requires; harness files are never
  accepted as substitutes.

`_PROMPT_FILE` mirrors `backends[*].prompt` in
`.claude/skills/agent-config/data/backend-fingerprints.yaml`, and
`tests/test_harness_registries.py` + `tests/test_doctor_resident_prompt.py`
assert the two never drift apart. Change one, change the other.

### Four harnesses over one clone

Two independent selections, and conflating them is the classic mistake:

1. **Interactive harness** — whichever binary you run (`claude`, `pi`,
   `colleague`, `qwen`). All four are live against the same working tree at all
   times; force-selection is invocation-level only (flags to that one process),
   never a rewrite of a tracked file. See `docs/automation-contract.md` and its
   machine-readable source `docs/harness-invocations.yaml`.
2. **Mesh resident** — the single `backend` in `culture.yaml` (`claude` here),
   which is what the Culture daemon starts and what `steward doctor` checks.

One root file per harness, no shared base and deliberately **no `AGENTS.md`**
(its absence is what stops Pi inheriting `CLAUDE.md`):

| Harness | File(s) |
|---------|---------|
| Claude Code | `CLAUDE.md` |
| Pi / associate | `AGENTS.override.md` + `.pi/SYSTEM.md` |
| colleague | `AGENTS.colleague.md` |
| Qwen Code | `QWEN.md` |

When you change repo conventions here, update the other three files in the same
PR — nothing makes them cascade, so they drift silently. `.qwen/skills`,
`.colleague/skills` and `.pi/skills` are **relative** symlinks onto
`.claude/skills` (one tree, four loaders); `scripts/harness-smoke.py` fails if
any becomes a real directory, an absolute symlink, or points elsewhere.

### Vendored skills

`.claude/skills/` is cited verbatim from guildmaster (cite-don't-import).
**Never edit a vendored script or `SKILL.md`** — the fix belongs upstream;
`docs/skill-sources.md` is the provenance ledger and re-sync procedure. These
paths are excluded from markdownlint and from Sonar analysis for that reason.
Every vendored `SKILL.md` must carry `type: command` — `core.skill_loader`
silently skips ones that don't.

### Test suite shape

`tests/test_cli.py` and `test_cli_introspection.py` cover the CLI; the rest are
*guard* tests over repo structure rather than the package —
`test_harness_registries.py` (registries agree), `test_doctor_resident_prompt.py`
(resident vs. recognized), `test_harness_smoke.py` (breaks each harness config
in a temp clone and asserts the smoke check fails), `test_pi_settings.py`,
`test_qwen_skills_symlink.py`, `test_scan_secrets.py` (plants secrets and
asserts they're caught). Breaking repo layout breaks tests here, by design.

## Conventions

- **Every PR bumps the version** — even docs/config/CI-only PRs. Use the
  `version-bump` skill (updates `pyproject.toml` + `CHANGELOG.md`); the
  `version-check` CI job comments on and blocks the PR otherwise.
- **PR lane**: the `cicd` skill (create/read/reply/status/await, SonarCloud
  quality gate + unresolved-thread tally). It signs replies automatically as
  `- xitter (Claude)` via `culture.yaml`; don't sign those bodies by hand. Sign
  manually authored posts (`gh pr create --body …`, issues) as
  `- xitter (Claude)`.
- **Secrets**: `scripts/scan-secrets.py` runs in CI and rejects
  credential-shaped strings anywhere, plus non-localhost `url`/`endpoint`/`host`
  values in files that parse as JSON. X API credentials belong in the
  environment, never in a tracked config.
- **Deploy**: push to `main` publishes to PyPI via Trusted Publishing
  (`.github/workflows/publish.yml`); PRs from this repo do a TestPyPI dry-run
  with a `.devN` suffix. Use the `pypi-maintainer` skill to switch an install
  between PyPI, TestPyPI, and a local editable checkout.
- **SonarCloud**: project key `agentculture_xitter`; the gate blocks CI when a
  `SONAR_TOKEN` is configured (skipped on fork PRs). Coverage must stay at or
  above `fail_under = 60`, and `relative_files = true` is required for Sonar to
  map coverage at all.
- **Renaming**: the `xitter` name is hard-coded in ~100 places
  (`pyproject.toml`, the package, `tests/`, `sonar-project.properties`, the four
  harness files, the workflows). Enumerate with `git grep -nF xitter` before
  touching any of it.
