# RETRO: Family Trading Desk

## Project state at adoption

Greenfield (2026-11-24). Planning done in claude.ai: "Family Trading Desk — Project Plan & Prompt Pack" (architecture, risk modes, tax reserve, cost model, roadmap, prompt pack, independent review log). Research seeded in `docs/research/`.

## Closed by owner decision

| Date | Decision | Notes |
|---|---|---|
| 2026-11-24 | Paper trading on Alpaca first; live broker decided later and kept fluid | Owner also holds Schwab and Robinhood accounts; adapters keep switching cheap |
| 2026-11-24 | No X / Grok and no paid news subscriptions | Free/official sources only (see NEWS_AND_DATA_STACK.md) |
| 2026-11-24 | Options: manual only, and only after the owner understands them; automated paths reject options | FR-14 |
| 2026-11-24 | Follow all applicable laws and broker/data terms | COMPLIANCE.md |
| 2026-11-24 | Small pre-approved trades may auto-execute under $X; larger, new, long-term or riskier trades need owner approval | FR-15–17 |
| 2026-11-24 | Rules 1–12 of the master brief adopted; rules grow from the failure library and stress tests | Master brief + FAILURE_LIBRARY.md |
| 2026-11-24 | Build process: project skills in `.claude/skills/` (phase-plan → plan-review → run-phase → phase-gate → red-team → owner sign-off) | Written fresh for this repo; no HSS skills |
| 2026-11-24 | Personal Windows PC only; dedicated claude.ai project "Family Trading Desk"; no HSS devices, accounts, repos, Bedrock or skills | Remote locked to github.com/jon-swill by a pre-push hook |

## Known debt

| Item | Owner | Notes |
|---|---|---|
| Decisions table values ([X], [Y], [N], bucket sizes, hard limits, budget) | owner | Phase 0 |
| Current holdings, cost basis, fee schedule from advisor statements | owner | Phase 0 |
| CPA inputs for tax-reserve model; household wash-sale scope | owner | Before Phase 2 gate |
| Check HSS personal-trading / conflict-of-interest policy and SEP client list for a restricted list | owner | COMPLIANCE.md C-3 |
| Strategy evidence in STRATEGY_ENCYCLOPEDIA.md is from general knowledge; re-verify with primary sources | agent | Phase 1 |
| Alpaca free-tier news terms and rate limits to re-verify | agent | Phase 1 |
| Regenerate Alpaca paper keys (previous keys were pasted into a chat) | owner | Before Phase 1 spike |
| One-time cleanup of the work Mac (zip, any local copy, .env, personal SSH key, gitconfig lines) | owner | This week |
