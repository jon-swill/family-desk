# PRD: Family Trading Desk

Owner: Jonathan Swill · Status: Draft v0.3 (2026-11-25; v0.3 adds proposed Phase 2 requirements FR-27–FR-30; v0.2 moved CPA review of the tax model to the Phase 6 gate) · Source: "Family Trading Desk — Project Plan & Prompt Pack" (claude.ai doc) and owner decisions in `docs/RETRO.md`.

Requirement IDs are stable. Phase plans must trace every deliverable to an ID here.

## 1. Purpose and scope

Replace a 1%-per-year advisory relationship with an owner-controlled, automated, rules-first investing system for one household. The system:

- holds a long-term, low-cost **core** and rebalances it on bands;
- runs a small, capped **active sleeve** of systematic strategies that must earn their place in forward tests;
- enforces hard risk limits that no model, strategy, or single message can override;
- reserves taxes on realized gains automatically and produces an estimated-payment schedule;
- shows the owner, every day, what is held, why, and how close each limit is;
- executes small, pre-approved trades on its own and routes larger, new, or riskier trades to the owner for approval.

Success in year one: zero operational incidents that lose money, every limit held, taxes fully reserved, and each active strategy either beating its benchmark after all costs over 6+ months of forward testing or switched off.

## 2. Users and access

| User | Access |
|---|---|
| Owner (Jonathan) | Full: approvals, mode changes, config changes (with cooling-off), kill switch |
| Spouse (Tali) | Read-only dashboard, kill switch, runbook |
| CPA | Read-only tax exports |
| Automated agents (Claude) | Research and proposals only; never order placement; never production secrets |

Household only. The system never manages money for anyone outside the household or for compensation (see `docs/COMPLIANCE.md` C-9).

## 3. Functional requirements

### Accounts and buckets
- **FR-1** Model five buckets: untouchable (never connected), core, active sleeve, tax reserve, ops budget. Sizes come from config.
- **FR-2** The active sleeve is capped by config; the cap can only be raised by a signed config change plus a 24-hour cooling-off.
- **FR-3** Broker adapters behind one interface. Paper: Alpaca. Live: decided later (candidates: Alpaca, Schwab, Robinhood Agentic, IBKR). Switching broker is a config change.

### Research and signals
- **FR-4** A research layer (LLMs + rules) produces typed proposals: symbol, side, size, strategy ID, thesis, invalidation level, evidence links, confidence, timestamp.
- **FR-5** Every proposal and its outcome is logged before the outcome is known (forward-test ledger).
- **FR-6** Strategy library implements only strategies listed in `docs/research/STRATEGY_ENCYCLOPEDIA.md` after they pass Phase 4 gates; each strategy has a pre-registered hypothesis, parameters, benchmark, and kill criteria.
- **FR-7** Watchlist with owner-set buy zones and alert levels.

### News and monitoring (free sources only; no X/Grok)
- **FR-8** Ingest news for held symbols, adjacent symbols (sector peers, suppliers, ETFs holding them), and watchlist symbols from free/official sources (`docs/research/NEWS_AND_DATA_STACK.md`).
- **FR-9** When a held or watched symbol crosses a configured move or level, assemble a "why is it moving" brief (news, filings, halts, macro calendar) with source links within 60 seconds of the trigger and push it to the owner.
- **FR-10** Monitor market-wide state: index moves, volatility, breadth, credit spreads, halts, data staleness.

### Risk kernel (deterministic, no LLM)
- **FR-11** Validate every proposal against hard limits: position size, sector/asset exposure, daily loss, drawdown, trades per day, turnover, liquidity floor, price collars, % of ADV, per-order notional, symbol allowlist, settled cash, instrument blocklist.
- **FR-12** Risk modes PRESERVE / DEFENSIVE / NORMAL / AGGRESSIVE with an explicit state machine. Toward safety: instant. Toward risk: owner command + one-time code + delay.
- **FR-13** Automatic de-risking only from deterministic multi-signal breakers, rate-limited, using price-collared limit orders, never auto-selling the core.
- **FR-14** Options orders are rejected in all automated paths (owner decision). Manual options support is a separate future phase.

### Trade routing and execution
- **FR-15** Tier A (automatic): under $X notional, approved strategy, allowlisted symbol, within limits, not options, not a core change.
- **FR-16** Tier B (approval): above $X, new symbol or strategy, core rebalance above threshold, above Y% of portfolio, any risk-up move. Push request with thesis, size, max loss, tax impact; expires after N minutes; silence = no.
- **FR-17** Tier C (never): outside limits, blocklisted instruments, halts, stale data.
- **FR-18** Idempotent orders (client order IDs), reconciliation with the broker before every order and daily, partial-fill handling, corporate-action handling.
- **FR-19** Protective stops/brackets rest at the broker; stop policy per `docs/research/FAILURE_LIBRARY.md` F-07 (no stop-market at the open or during halts; collared stop-limits where supported).
- **FR-20** Kill switch (command, phone button) and dead-man watchdog that cancels entry orders but never protective stops.

### Tax
- **FR-21** Lot-level ledger; short/long-term classification; household-wide wash-sale tracking (all household accounts, IRAs included) via a restricted list.
- **FR-22** Reserve target = estimated tax with portfolio activity minus without, federal and NJ separately, floored at zero; daily sweep to a money market/T-bill bucket the bot cannot trade.
- **FR-23** Estimated-payment schedule with reminders; year-end CPA export.

### Owner interface
- **FR-24** Daily dashboard: holdings by bucket/asset/sector, P&L vs benchmark, risk mode and limit headroom, pending approvals, tax reserve vs target, costs vs budget, fees saved vs 1%.
- **FR-25** Command channel with fixed grammar (no LLM parsing), allowlisted user IDs, TOTP for risk-up.
- **FR-26** Daily journal and weekly scorecard (strategy vs baselines after costs, limit breaches, rejections, incidents).

### Proposed for Phase 2 (owner, 2026-11-25)

**Status: proposed.** These are not yet accepted requirements. The Phase 2 phase-plan and plan-review decide their scope, and the owner accepts or rejects each one. Their IDs stay fixed either way.

- **FR-27 (proposed)** Modular, versioned interfaces for the data, strategy, kernel, broker and LLM layers, so each can be swapped without changing the others. Extends FR-3. Swapping the kernel stays under the owner-diff-review hard stop and trading invariant 2.
- **FR-28 (proposed)** An UPGRADE risk mode that halts the short-term (active) sleeve, holds the core, and leaves protective stops resting at the broker (invariant 4). Entering it is instant, like any move toward safety. Leaving it is a risk-up move and follows FR-12 like any other: an owner command, a one-time code and the standard delay (FR-25, invariant 3).
- **FR-29 (proposed)** Regime-anomaly detection that may only move the risk mode in the defensive direction. It never raises risk or leaves a defensive mode. It is subject to FR-13 and invariant 3, so LLMs never trigger mode changes.
- **FR-30 (proposed)** An improvement loop in which agents propose changes only as pull requests. Each change goes through pre-registration (FR-6, invariant 7), a paper forward test (FR-5) and owner approval before merge. Nothing self-modifies in live. *Owner note (2026-11-25, proposed):* RD-Agent and gs-quant as design references only, and Kronos as a Phase 4 candidate signal, forward-logged only (invariant 8).

## 4. Non-functional requirements

- **NFR-1 Safety:** no path from an LLM, external text, or a single message to an order without the risk kernel. Proven by tests.
- **NFR-2 Determinism:** risk kernel, execution, and ledger are pure, deterministic, fully tested code (functional core, imperative shell).
- **NFR-3 Security:** secrets in a secrets manager; no prod secrets on dev machines; signed limits config; pinned dependencies; paper-vs-live endpoint asserted at startup; least-privilege broker keys; IP allowlist where offered.
- **NFR-4 Reliability:** survives server loss (broker-side protection), broker/API outage (halt new entries, alert), data staleness (halt), provider outage (degrade to rules-only).
- **NFR-5 Cost:** total running cost under the monthly budget in config; hard caps in code and provider consoles; cost reported per strategy.
- **NFR-6 Auditability:** append-only ledger of proposals, decisions, orders, fills, fees, tax movements; reproducible from logs.
- **NFR-7 Compliance:** every requirement in `docs/COMPLIANCE.md`.
- **NFR-8 Latency:** risk breakers act within seconds of a trigger; LLM work is never in the hot path.

## 5. Architecture constraints

- Python. Functional core, imperative shell. Parse at the boundary. Fakes over mocks (per `coding-standards`).
- Execution/backtest engine chosen in Phase 1 (candidates: NautilusTrader, LEAN, custom on vectorbt for research).
- LLM roles: judgment = Opus/Fable class; execution and routine = Sonnet; mechanical = Haiku. Model IDs pinned.
- Dev local; production on a locked-down small EC2/Lightsail host (no inbound ports, SSM only).
- Broker access only through official APIs. No scraping of broker or data websites.

## 6. Phase plan

| Phase | Goal | Gate (summary) |
|---|---|---|
| 0 | Charter and decisions | Decisions table complete; current holdings and fees captured |
| 1 | Landscape + strategy + failure research; engine/broker/data choice | Decision matrix reviewed (plan-evaluation + independent review) and owner sign-off |
| 2 | SPEC.md, FMEA, interface contracts | samd-design-review style graded review; owner sign-off. The tax model is built from published federal and NJ rules and labelled "not CPA-reviewed" until the CPA signs off before the Phase 6 gate |
| 3 | Safety spine: ledger, kernel, execution adapter, watchdog, tax reserve, dashboard, news alerts | Fault-injection suite green |
| 4 | Strategy research: baselines, point-in-time backtests, forward logging | Pre-registered hypotheses survive out-of-sample after costs |
| 5 | Paper trading 60–90 days (30 minimum) | Zero limit breaches; clean reconciliation; honest scorecard |
| 6 | Live pilot (realistically month 5–6) | Live tracks paper; CPA sign-off on the tax model (CPA inputs incorporated, "not CPA-reviewed" label removed) before any real money; owner sign-off on allocation |
| 7 | Scale and operate | Monthly reviews; quarterly re-certification |

## 7. Out of scope

- Automated options trading (manual-only future phase after owner education).
- Crypto (future separate module).
- X / Grok or any paid news subscription.
- Margin and short selling (off unless the owner changes it in a signed config).
- High-frequency or market-making strategies.
- Managing money for anyone outside the household.
