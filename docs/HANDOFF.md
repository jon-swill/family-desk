# Handoff: Family Trading Desk (as of 2026-11-24)

> **Note (2026-11-24):** `docs/RETRO.md` decisions of 2026-11-24 supersede the Phase 1 owner rows below: the employer personal-trading policy check is removed, and the CPA (booking, inputs, tax-model sign-off) and advisor statements move to before the Phase 6 real-money gate.

Start here in any new chat or Claude Code session. Planning began in claude.ai on 24 Nov 2026 and moves to a dedicated claude.ai project and the owner's personal Windows PC.

## Who and what
Jonathan Swill (owner) is building a personal, household-only investing system to replace a 1%-per-year advisor: low-cost long-term core, small capped active sleeve, hard risk limits in deterministic code, automatic tax reserve, daily visibility. Small pre-approved trades run automatically under $X; larger, new, long-term or riskier trades wait for his approval. Tali (spouse) gets read-only access and the kill switch.

## Where things live
| Item | Location |
|---|---|
| Plan doc (architecture diagram, risk modes, cost model, roadmap, strategy catalog, trade routing, gated workflow, independent review log) | claude.ai doc "Family Trading Desk — Project Plan & Prompt Pack": https://claude.ai/artifact/7ngaotGWsWf54ebjaDYTeC |
| Repo | github.com/jon-swill/family-desk (private), local `C:\Users\<you>\code\family-desk` |
| Requirements | `docs/PRD.md` (FR-*, NFR-* IDs) |
| Decisions and debt | `docs/RETRO.md` |
| Principles (Prompt 0) | `docs/MASTER_BRIEF.md` |
| Failures and rules R-13 to R-40 | `docs/research/FAILURE_LIBRARY.md` |
| ~60 strategies, 12 families | `docs/research/STRATEGY_ENCYCLOPEDIA.md` |
| Free news and data | `docs/research/NEWS_AND_DATA_STACK.md` |
| Laws and terms | `docs/COMPLIANCE.md` |
| Workflow skills | `.claude/skills/` (phase-plan, plan-review, run-phase, phase-gate, red-team, failure-check) |

## Owner decisions so far (closed)
- Personal Windows PC only; no HSS devices, accounts, repos, Bedrock or HSS skills. Dedicated claude.ai project for this work.
- Paper trading on Alpaca; live broker stays fluid (owner also holds Schwab and Robinhood).
- No X/Grok, no paid news; free/official sources only.
- Options manual only, later; automation covers stocks and ETFs only. No margin, no shorting.
- Follow all laws and provider terms; household money only.
- Rules 1–12 adopted; failure-derived rules grow with every failure found.
- Process: phase-plan → plan-review → run-phase → phase-gate → red-team (fresh session, ideally a different model) → owner sign-off.

## Key findings to carry forward
- Building the system is feasible; beating an index after costs and taxes is unproven. Public LLM trading contests mostly lost money (6 of 32 runs profitable in Alpha Arena), and LLM historical backtests suffer look-ahead bias, so LLM signals are scored only on forward-logged decisions.
- Most reliable win: replacing the 1% fee (about 18% more ending wealth over 20 years) with an index core + band rebalancing + tax-loss harvesting.
- Jane Street ETC bots (repos the owner shared) won with simulator-only market making; only their engineering habits transfer.
- Running cost estimate with free news: ~$120–220/month; LLM spend is judged against the active sleeve only.
- Independent review fixes already folded in: watchdog never cancels protective stops; LLM never auto-triggers de-risking; tax reserve = tax with minus tax without (federal + NJ) with household wash-sale tracking and estimated payments; key/command/dev-pipeline compromise controls; realistic timeline (live in month 5–6).

## Phase 1 definition (what to plan next)
Two tracks, no orders anywhere.
- **A. Research:** verify every [verify] item in `docs/research/*.md` against primary sources; extend FAILURE_LIBRARY with retail-algo post-mortems and broker-API incidents (Alpaca, Schwab, Robinhood); re-verify STRATEGY_ENCYCLOPEDIA evidence; compare engines (NautilusTrader, LEAN, custom on vectorbt) and live-broker candidates (Alpaca, Schwab Trader API, Robinhood Agentic Trading, IBKR) in `docs/research/decision_matrix.md`; confirm Alpaca free-tier news terms.
- **B. Read-only data spike (Windows, Python):** assert the paper endpoint at startup; read account and positions; stream IEX quotes and Alpaca News for a 5-symbol watchlist; poll the SEC EDGAR 8-K Atom feed at ≤1 request/second with the owner's User-Agent; write everything to an append-only local log; tests with fakes. No order endpoints imported.
- **Owner rows:** Phase 0 decisions table (bucket sizes, hard limits, $X/Y%/N minutes, budget), advisor statements (holdings, cost basis, account types, fees), CPA booking, HSS personal-trading policy check for a restricted list.
- **Gate:** decision matrix and spike pass plan-review/phase-gate, red-team in a fresh session, owner sign-off in RETRO.

## Open owner tasks
- Regenerate the Alpaca paper keys (old ones were pasted into a chat) and keep them only in `.env` and a password manager.
- Work Mac cleanup (one time): delete the starter zip, any `~/personal/family-desk` folder and `.env` there, any personal SSH key created there (and remove it from GitHub → Settings → SSH keys), and any `includeIf` lines added to `~/.gitconfig`.
- Phase 0 homework (above).
