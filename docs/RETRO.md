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
| 2026-11-24 | **Phase 0 signed off by the owner.** Only the O3 decisions table is carried as debt, due before the Phase 2 phase-plan. O4 advisor statements and O5 CPA booking are debt due before the Phase 6 real-money gate | See Known debt; Phase 1 may start |
| 2026-11-24 | Employer personal-trading policy check removed. Spike watchlist is final: SPY, QQQ, IWM, AAPL, MSFT | Replaces the Phase 1 O2 check |
| 2026-11-24 | Restricted-list mechanism kept (COMPLIANCE C-3, trading invariant 18): the list starts empty and is owner-maintained; no employer-policy check | C-3 and invariant 18 updated |
| 2026-11-24 | CPA review moved to before the Phase 6 real-money gate: CPA inputs for the tax-reserve model and the CPA sign-off (formerly a Phase 2 gate item). The Phase 2 tax model is built from published federal and NJ rules and labelled "not CPA-reviewed" until then | PRD v0.2 §6 Phase 2 and Phase 6 gates updated |
| 2026-11-25 | Alpaca paper key has trading scope; accepted for Phase 1 because the code has no order route and the account is paper. Revisit before Phase 3. | From the Phase 1 plan re-review (`phase_1_eval.md`, 2026-11-25) |
| 2026-11-25 | **Phase 0 decisions table recorded as paper-test values** in `docs/phases/phase_0/decisions.md` (D-01 to D-20). Every number is a config value revisited at the Phase 6 live gate. Closes debt item O3 | PRD v0.4 |
| 2026-11-25 | Paper-test values: auto-trade cap $X = $250 per trade (D-01); paper desk ~$35k, sleeve $5k, core the rest, index/long-term only; sleeve target 5% of investable money once ~$150k moves in (D-02 to D-05) | FR-1, FR-15 |
| 2026-11-25 | Paper-test values: sleeve growth by manual owner approval only, at most one step per quarter, only after beating baselines after all costs for 2+ quarters (D-06) | FR-2 |
| 2026-11-25 | Paper-test values: sleeve day stop −2%, week stop −5%, alert and review at −10% from peak (the owner's annual sleeve loss tolerance), sleeve off at −15% from peak until reviewed (D-07 to D-10) | FR-11, FR-12 |
| 2026-11-25 | Paper-test values: max 1% of the sleeve at risk per position; max 5 open positions; stops mandatory in the sleeve; the core is never sold because of a drawdown, only band rebalancing and tax-loss harvesting (D-11 to D-14) | FR-11, FR-13, FR-19 |
| 2026-11-25 | Paper-test values: tools and data budget $0–25/month; no runtime LLM/API spend without owner approval; rules-based strategies first; cost reported per strategy (D-15, D-16) | NFR-5 |
| 2026-11-25 | Options: equities and options are both wanted eventually. Automated paths still reject options (invariant 16 unchanged). A manual, defined-risk paper-options learning track starts now. Options automation becomes PRD Phase 8 with its own gate. Amends the 2026-11-24 options row (D-17) | FR-14, PRD §6 Phase 8 |
| 2026-11-25 | Long-term picture: ~$30–40k desk in year 1, ~$150k after a year if it performs, ~$1M goal in 5–6 years, not super aggressive. Risk is never tuned to chase it (D-18; math in decisions.md §3) | PRD §1 |
| 2026-11-25 | Reports: a daily one-line push; a Sunday weekly report and check-in form; a monthly review with a settings form; a quarterly sleeve-size form. Each under 2 minutes; answers saved in `docs/checkins/` (D-19) | FR-24, FR-26 |
| 2026-11-25 | Experiment E-1 ("take small profits, never sell below cost basis", arms A/B/C) is pre-registered as a paper experiment (D-20) | FR-31 |
| 2026-11-25 | Owner answers to decisions.md §5: (1) all E-1 arms are simulated, with no broker orders; (2) covered calls on sleeve shares only; (3) options maximum loss $50 per trade, and a separate options paper account | FR-14, FR-31 |
| 2026-11-25 | **Paper-test auto-trade cap raised from $250 to $1,000 per trade (D-01)**, effective 2026-11-26 after the 24-hour cooling-off for risk-up changes. Revisit at the live gate | FR-15; supersedes the $250 in the D-01 row above |

## Known debt

| Item | Owner | Notes |
|---|---|---|
| Revisit every paper-test value in `docs/phases/phase_0/decisions.md` | owner | At the Phase 6 live gate, before any real money |
| Parameters still unset: Y% and N minutes for Tier B, core rebalance bands, risk-mode thresholds outside the sleeve | owner | Listed by the Phase 2 phase-plan; set before the Phase 2 gate |
| Alpaca paper balance of $35k is unverified (the docs give a $100k default and contradict themselves on reset vs new account). Check in the dashboard; if a new account is made, do it only after B10, regenerate keys and update the O1 date. Otherwise scale reports to $35k | owner | Before Phase 5 paper trading; decisions.md §4 |
| E-1 parameters (dip definition, profit target, B's stop distance, ETF and stock lists, test window, tax assumptions) to freeze before any data is examined | agent proposes, owner approves | Phase 2 phase-plan; before any Phase 4 backtest |
| Create the separate Alpaca options paper account (keys, if any, kept out of the automation's `.env` entries) | owner | Before the first options learning trade |
| Loss-limit definitions (day/week baselines, peak high-water mark and any annual reset, realized vs unrealized) | agent | Phase 2 SPEC |
| Current holdings, cost basis, fee schedule from advisor statements (O4) | owner | Carried from Phase 0; due before the Phase 6 real-money gate |
| Book the CPA (O5) | owner | Carried from Phase 0; due before the Phase 6 real-money gate |
| CPA inputs for tax-reserve model; household wash-sale scope; CPA sign-off on the tax model | owner | Before the Phase 6 real-money gate; until then the tax model is labelled "not CPA-reviewed" |
| Strategy evidence in STRATEGY_ENCYCLOPEDIA.md is from general knowledge; re-verify with primary sources | agent | Phase 1 |
| Alpaca free-tier news terms and rate limits to re-verify | agent | Phase 1 |
| Regenerate Alpaca paper keys (previous keys were pasted into a chat) | owner | Before Phase 1 spike |
| One-time cleanup of the work Mac (zip, any local copy, .env, personal SSH key, gitconfig lines) | owner | This week |
