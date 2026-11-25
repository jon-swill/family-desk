# Phase 1 hand-off (run-phase session, 2026-11-25)

Nothing was pushed. Everything below is local commits on `main`. Gates at hand-off: `ruff check`, `ruff format --check`, `mypy --strict src` green; `pytest -q` 229 passed, 1 skipped (the real AAPL fixture test, see step 2).

## Done (agent)
B1, B2, B3, B4, B5, B6, B7, B9, B12, A1, A2, A3, A4, A5, A6, A7. B8 is done except its real fixture (step 2). Proof for each is in `phase_1_tasks.md`.

## Waits on the owner, in order

1. **O1: keys.** Confirm the paper keys were regenerated and `.env` has the 4 variables. Then run `git check-ignore .env` (it must print `.env`) and tell the agent the regeneration date (needed for A11's 90-day rotation row). Paste no values.

2. **B8 fixture (reads `.env` for the SEC User-Agent, makes one SEC request).** From the repo root with the venv active:
   ```powershell
   python -m family_desk_spike.tools.fetch_edgar_fixture
   python -m pytest -q tests/test_edgar.py
   ```
   The skipped test should now pass. Tell the agent, which reviews the fixture for personal values and commits it.

3. **O7: one manual paper order.** During market hours, in Alpaca's **paper** web dashboard, by hand: buy 1 SPY, **limit**, day order, limit at or just above the ask. Never market. No code is involved. Tell the agent "filled" or "not filled".

4. **B10: live spike run.** Valid windows: start at or after 10:00 ET, and end by `next_close` − 30 min. Thu 26 Nov is Thanksgiving, so the market is closed. Fri 27 Nov is a half-day closing at 13:00 ET, so a 35-minute run must start between 10:00 and 11:55 ET. From Mon 30 Nov, a run can start between 10:00 and 14:55 ET. The runner refuses outside these windows; there is no override.
   ```powershell
   # a) Refusal demo (wrong host; refused before any network call)
   (Get-Content config\spike.toml -Raw).Replace('https://paper-api.alpaca.markets','https://wrong-host.invalid') | Set-Content -NoNewline config\spike.toml
   python -m family_desk_spike --duration-min 35      # expect: startup REFUSED codes=host,config_hash,dirty_tree
   git checkout -- config
   git status --porcelain -- src config               # must print nothing
   # b) Real run (about 35 minutes; Ctrl+C is safe and still writes the summary)
   python -m family_desk_spike --duration-min 35
   python -m family_desk_spike.verify_log logs\spike\<YYYY-MM-DD>.jsonl
   ```
   Save both outputs (they hold counts and hashes, no secrets), or paste them to the agent for B11. **Rerun rule (G-9):** if `news_rest_watchlist=0`, or `pre_filter_min` and `pre_filter_max` are both 0, the run fails. Do a new run on another day; the criterion is never relaxed.

5. **O6: failure proposals.** Approve or reject P-07 to P-18 in `docs/research/failure_library_proposals.md`, from A4. A9 then merges the approved ones.

6. **O3** (Phase 0 decisions table): done 2026-11-25. Paper-test values are in `docs/phases/phase_0/decisions.md`. Its §5 lists the points the agent flagged for the owner. Do not make a new $35k Alpaca paper account until B10 has passed (see §4 of that file).

## Decisions the agents raised (owner's call)
- **A5 matrix method:** (a) the data table is split into price feeds and company-event sources, ranked separately; (b) a knock-out (KO) rule was added: a 0 on a KO criterion excludes the candidate; (c) G-1's HOLD rule is read as applying to the engine recommendation only, while a broker or data rank flip is published as "not robust". Confirm or override.
- **A3 evidence contradictions** (Evidence cells corrected; "Why it might work" columns left alone): turn-of-month "fund flows" is rejected by McConnell & Xu 2008; volatility targeting has no systematic out-of-sample edge (Cederburg et al. 2020); SMA crossover is not significant out-of-sample (Sullivan et al. 1999); time-series momentum is weak asset by asset (Huang et al. 2020); opening-range breakout results rely on 3x ETFs, which are on our blocklist.
- **A1:** the F-14 figure changed from "1.1% earned more than minimum wage" (not found in any readable source) to "0.4% earned more than a bank teller", from the abstract. F-10 got a wording fix. Neither changes a rule.
- **A2:** (a) free-plan news may be delayed 15 minutes; the spike's real timestamps will show it; (b) news now also comes from `fiscal.ai`, not only Benzinga; (c) AS-16 is false, as the two Atom formats differ (the parser handles both); (d) whether the free plan can use the delayed-SIP stream is unverified.

- **A6 engines:** both packaged engines (NautilusTrader, LEAN) have built-in exit paths that send market orders (`close_all_positions`, `liquidate`, margin-call liquidation) and no documented way to put our kernel in front of them. Under the robustness check that is a knock-out (E-1), so A8 may end with no engine pick, unless you move the choice to the Phase 2 install-check. LEAN local/on-prem live trading appears to need a paid tier. NautilusTrader v2 needs Python 3.13 or later (the repo pins 3.12).
- **A7 brokers:** Schwab's developer portal and interactivebrokers.com refused automated reads, so 9 Schwab and 2 IBKR cells are `unverified`. You can close them by reading those pages in a browser; the robustness check sets them to the worst score, and Schwab's B-1 and B-2 then knock it out. Read-only keys: Alpaca none, Robinhood none, IBKR only as a local TWS setting, Schwab unknown. Robinhood's customer agreement §29.1 needs written consent for "Licensee Products", and it is unclear whether a deterministic order client counts.

## Next agent tasks once the above is done
B8 fixture commit → B11 (evidence, `pytest -rA` capture, secret scan) → A10 (data scores with spike measurements) → A8 (totals, robustness, sensitivity, dissent) → A9 (after O6) → A11 (after O1 and O7) → G1 phase-gate.
