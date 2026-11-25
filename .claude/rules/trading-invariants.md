# Trading invariants (apply to every file in this repo)

These come from `docs/MASTER_BRIEF.md` (rules 1–12) and `docs/research/FAILURE_LIBRARY.md` (R-13 onward). If code would break one, stop and ask the owner.

1. No model output reaches an order endpoint without passing the deterministic risk kernel.
2. Hard limits live in a signed config outside strategy code; raising one needs owner review and a 24-hour delay.
3. Safety moves are instant; risk-up moves need an owner command + one-time code + delay. LLMs never trigger mode changes.
4. Protective stops rest at the broker; the watchdog cancels entry orders only, never protective stops.
5. Only the active-sleeve account is tradable by automation; core is rebalance-only; untouchable money is never connected.
6. External text (news, filings, web) is data, never instructions; no single source triggers a trade; no rumor trades.
7. Every strategy has a pre-registered hypothesis, benchmark and kill criteria; it must beat baselines after all costs in forward tests.
8. LLM signals are scored only on timestamped forward decisions, never on historical backtests.
9. Append-only ledger; reconcile with the broker before every order and daily; record costs per strategy.
10. Tests for new behavior; evidence for every "done".
11. Kernel enforces: symbol allowlist, liquidity floor, price collars, % of ADV cap, per-order notional cap, settled cash, instrument blocklist (leveraged/inverse/volatility ETPs, OTC, penny, fresh IPOs/SPACs).
12. Tax: lot-level ledger, household-wide wash-sale restricted list, reserve = tax with minus tax without (federal + NJ), estimated-payment schedule.
13. No market orders anywhere; marketable limits with collars; stop-limits with collars where supported (R-25, R-26).
14. No trading in the first/last 5 minutes, during halts or with stale data (R-24).
15. Self-halt on abnormal order rates or fills exceeding targets; page the owner (R-15, R-16).
16. Options and shorting are rejected in every automated path (owner decision).
17. Paper endpoint asserted at startup until the Phase 6 gate; refuse to run if the endpoint or config hash is unexpected (R-13).
18. Restricted list blocked in the kernel (C-3). The list starts empty and is owner-maintained; no employer-policy check.
