# CLAUDE.md: family-desk

Personal, household-only investing system for Jonathan Swill. **Not an HSS project**: never reference HSS repositories, organizations, AWS accounts, Bedrock credentials or HSS skills. Remote must be `github.com/jon-swill/family-desk`. Development happens only on the owner's personal Windows PC.

## Read first, every session
1. `docs/MASTER_BRIEF.md`: principles and owner decisions (non-negotiable).
2. `docs/PRD.md`: requirements with stable IDs (FR-*, NFR-*). Every plan and change traces to an ID.
3. `docs/RETRO.md`: owner decisions (closed: don't reopen) and known debt (open).
4. `.claude/rules/trading-invariants.md`: hard rules for any code in this repo.
5. Current phase folder `docs/phases/phase_{N}/` if it exists.

## Workflow (project skills in `.claude/skills/`)
`phase-plan` → `plan-review` → `run-phase` → `phase-gate` → `red-team` (fresh session) → owner sign-off. `failure-check` runs inside plan-review and phase-gate. One phase at a time; never start the next phase without a recorded owner sign-off in RETRO.

## Hard stops (ask the owner first)
- Any code that imports or calls an order-placing endpoint, before the Phase 3 safety spine passes its gate.
- Anything using live (non-paper) keys or endpoints. Ever, until the Phase 6 gate.
- Pushing, creating remotes, changing GitHub settings, cloud resources, paid services or spending money.
- Changing hard limits, risk modes or the kernel without the owner reviewing the diff.
- Reading or printing secrets. Secrets live in `.env` (git-ignored) and are read only by code, never echoed.

## Engineering stance
Python. Functional core, imperative shell: risk kernel, sizing, ledger and tax logic are pure functions with tests; I/O lives at the edges. Parse external data at the boundary into typed models. Fakes over mocks. Tests for new behavior; prove it works with real evidence (command output, logs), never "looks done". Pin dependencies. No market orders anywhere. Keep diffs small and in scope.

## Windows notes
Shell is PowerShell (or Git Bash if installed). Use `py`/`python` from the project's virtual environment in `.venv`. Paths with backslashes; never write outside the repo.

## Quality gates
To be defined in Phase 1 (lint, type check, tests). Until then: `python -m pytest -q` must pass before any commit.
