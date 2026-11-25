# Phase 0 decisions table: paper-test values

Status: **owner decisions of 2026-11-25, paper-test values.** Every number below is a config value for paper trading. Each one is revisited at the Phase 6 live gate before any real money moves, and none is final until then. Recorded in `docs/RETRO.md` (closes debt item O3). Traces to `docs/PRD.md` v0.4.

The values become fields in the signed limits config when Phase 3 builds it (trading invariant 2). Until then this file is the record. Changing a value follows the same rule as the config: risk-down changes are instant, while risk-up changes need owner review and a 24-hour delay.

This file holds limits, rules and owner planning figures only. It holds no account balances, holdings or account numbers (Phase 1 AS-10); those go in the git-ignored `private/` folder. The $35k paper desk is a paper setting. The $150k and $1M figures are owner planning targets, not balances.

## 1. Values

| ID | Decision | Paper-test value | PRD |
|---|---|---|---|
| D-01 | Auto-trade cap ($X): Tier A notional limit per trade | **$1,000 per trade** (raised from $250 by the owner on 2026-11-25; effective 2026-11-26 after the 24-hour cooling-off for risk-up changes). Anything bigger waits for owner approval (Tier B). The 1% risk cap (D-11) still binds: a $1,000 entry with $50 at risk needs a stop within 5% | FR-15, FR-16 |
| D-02 | Paper desk total | **~$35,000.** Reset the Alpaca paper balance to match if Alpaca allows it; otherwise scale every report to $35k (see §4) | FR-1, FR-24 |
| D-03 | Active sleeve size (paper) | **$5,000**, the amount the owner would start live with | FR-1, FR-2 |
| D-04 | Core size (paper) | The rest of the desk (~$30,000). Index and long-term holdings only | FR-1 |
| D-05 | Sleeve target as a share of investable money | **5%**, a config value. It applies once the full ~$150k moves in (about a $7.5k sleeve) | FR-1, FR-2 |
| D-06 | Sleeve growth | **Manual owner approval only.** At most one step per quarter, and only after the sleeve beats its baselines after **all** costs for **2 or more quarters**. No automatic growth | FR-2, FR-12 |
| D-07 | Sleeve daily loss stop | **−2%** of sleeve equity: no new sleeve entries for the rest of the day | FR-11 |
| D-08 | Sleeve weekly loss stop | **−5%** of sleeve equity: no new sleeve entries for the rest of the week | FR-11 |
| D-09 | Sleeve drawdown alert | **−10% from peak:** alert the owner and require a review. This is the owner's "won't bother me" line and the annual loss tolerance for the sleeve | FR-11, FR-26 |
| D-10 | Sleeve off switch | **−15% from peak:** sleeve off (no new entries) until the owner reviews it. Protective stops stay at the broker (invariant 4) | FR-11, FR-12 |
| D-11 | Per-position risk | **At most 1% of the sleeve** at risk between entry and stop ($50 at a $5k sleeve) | FR-11 |
| D-12 | Open positions | **At most 5** open sleeve positions | FR-11 |
| D-13 | Stops in the sleeve | **Mandatory** on every sleeve position. A stop is risk control, not a forecast. No holding losers to get back to cost basis | FR-11, FR-19 |
| D-14 | Core on a drawdown | **Never sell core holdings because of a drawdown.** The core changes only by band rebalancing and tax-loss harvesting | FR-13 |
| D-15 | Tools and data budget (paper) | **$0–25/month** | NFR-5 |
| D-16 | Runtime LLM/API spend | **None without owner approval.** At a $5k sleeve, $25/month is already about 6% a year of hurdle ($300 ÷ $5,000), so rules-based strategies come first. Cost is reported per strategy | NFR-5, FR-26 |
| D-17 | Options | Equities and options are both wanted eventually. **Automated paths still reject options** (invariant 16). A manual paper-options learning track starts now (§2). Options automation is a future phase with its own gate (PRD Phase 8) | FR-14 |
| D-18 | Long-term picture | Year 1: a ~$30–40k desk. If it performs: ~$150k after a year. Goal: ~$1M in 5–6 years, **not super aggressive.** Risk is never tuned to chase the goal (§3) | §1 |
| D-19 | Report cadence | Daily push, a weekly report with a check-in form (Sunday), a monthly review and a quarterly sleeve-size form. Each takes the owner under 2 minutes. Answers are saved in `docs/checkins/` | FR-24, FR-26 |
| D-20 | Experiment E-1 | Pre-registered paper experiment on "take small profits, never sell below cost basis" (§2) | FR-31 |

Parameters not set by the owner yet are not filled in here. Examples are the risk mode thresholds outside the sleeve, core rebalance bands, Y% for Tier B and N minutes for approval expiry. The Phase 2 phase-plan lists them for the owner to set.

## 2. Tracks and the experiment

### Manual paper-options learning track (D-17)
- **Defined-risk only:** long calls, long puts, debit spreads, and covered calls on **sleeve** shares already held, never core shares (owner, 2026-11-25).
- **Maximum loss per trade: $50**, the same 1% sleeve cap as D-11 (owner, 2026-11-25).
- **Separate Alpaca paper account** for options learning, so manual trades never appear in the account the automation reconciles (owner, 2026-11-25). Its trades count against the sleeve limits by manual entry.
- Every trade is placed by hand. No code places or routes options.
- Each trade logs its maximum loss at entry and counts against the sleeve limits (D-07 to D-12).
- Each week there is a short "what I learned" note, saved with the weekly check-in.
- Until the Phase 3 ledger exists, the owner logs trades by hand in `docs/checkins/options/`, and the weekly report adds them up against the sleeve limits.

### E-1: "take small profits, never sell below cost basis" (pre-registered)
- **Hypothesis under test (owner's idea):** buying dips and selling only above cost basis gives a high win rate. The question is whether it beats a stop-based version and plain index buy-and-hold after costs and taxes, once capital stuck underwater is counted.
- **Arms:**
  - **A:** buy dips, sell only above cost, no stop.
  - **B:** the same entries as A, with a stop or a 10-day time stop.
  - **C:** buy-and-hold the index.
- **Universes, reported separately:**
  1. Liquid index ETFs.
  2. A small basket of single stocks.
- **Metrics:** win rate; average win vs average loss; capital stuck underwater (dollar-days and longest stretch below cost); results after all costs and estimated taxes vs C. Estimated taxes use published federal and NJ rules and are labelled "not CPA-reviewed" (PRD Phase 2).
- **Benchmark:** arm C.
- **Kill criterion:** an arm that does not beat C after costs and estimated taxes is not adopted as a strategy (invariant 7).
- **Still to freeze before any data is looked at:** the dip definition, the profit target, B's stop distance, the ETF and stock lists, the test window and the tax assumptions. The Phase 2 phase-plan proposes them for owner approval. They are frozen in writing before the Phase 4 backtest runs (R-17 pre-registration; R-18 holdout).
- **Execution (owner, 2026-11-25):** all three arms are simulated on paper market data and forward-logged, with no broker orders. Arm A therefore never sits in the sleeve without a stop (D-13), and the arms stay comparable.
- **Schedule:** a point-in-time backtest in Phase 4, then a forward simulated run alongside Phase 5 paper trading.

## 3. The $1M math

Assumptions:
- ~$150k invested at the end of year 1.
- ~$1M at the end of year 5 or 6, which leaves **4–5 years** of growth from $150k.
- Return rates are planning assumptions, not forecasts.
- Contributions are a level amount each year, added at year end. Start-of-year figures are shown in brackets.
- No taxes or fees are taken out, so real needs are somewhat higher.

| Growth from $150k | Returns alone need | $150k alone grows to (7% / 10%) | Contributions needed at 7% a year | at 10% a year |
|---|---|---|---|---|
| 5 years | **46.1% a year** | $210k / $242k | **~$137k a year** ($128k) | **~$124k a year** ($113k) |
| 4 years | **60.7% a year** | $197k / $220k | **~$181k a year** ($169k) | **~$168k a year** ($153k) |

Formulas:
- Required return = (1,000,000 ÷ 150,000)^(1/n) − 1.
- Contribution = (1,000,000 − 150,000 × (1+g)^n) ÷ [((1+g)^n − 1) ÷ g].

**The tension, stated plainly:**
- A "not super aggressive" plan and a 5–6 year $1M goal do not fit together on returns. 46–61% a year is far beyond any return a diversified portfolio can plan on.
- At 7–10% a year, almost all of the gap must come from contributions: about $124–137k a year over 5 years, or $168–181k a year over 4 years.
- The active sleeve cannot close the gap. A 5% sleeve on $150k is $7.5k, so even a 20% sleeve year adds about $1,500.
- The goal is a **savings-rate goal**, not a trading goal.
- Choosing a longer horizon (for example 8–10 years at 7–10%) is the other honest lever. Raising risk is not.

**Rule:** no limit, sleeve size, risk mode or strategy choice is ever changed to chase this goal. If the goal and the limits conflict, the goal moves.

## 4. Alpaca paper balance (D-02): verification

**Result: a $35k paper balance is unverified.** Alpaca's own page contradicts itself, and it never says whether a non-default balance can be chosen.

Source: [Alpaca docs, Paper Trading](https://docs.alpaca.markets/us/docs/paper-trading), accessed 2026-11-25. The page says:
- "We've updated the dashboard to allow you to create and delete paper accounts, rather than resetting them."
- "To create a new paper account, click the paper account number in the upper left corner of the dashboard and select "Open New Paper Account.""
- "Your initial paper trading account is created with $100k balance as a default setting."
- "You cannot change the account balance after it is created, unless you reset it."
- An older section says: "You can reset the paper trading account at any time later with arbitrary amount as you configure."
- "Don't forget to generate new API keys for any newly created account."

It gives no minimum or maximum balance and no limit on the number of accounts. Older community posts on Alpaca's forum describe a reset that asks for an amount ([forum thread](https://forum.alpaca.markets/t/how-to-set-paper-account-to-something-other-than-100k/2144)). They are not a primary source and predate the dashboard change.

**How the owner can check (no code):** in the paper dashboard, click the account number and choose "Open New Paper Account". See whether it asks for a balance.

**Timing:** do this only after Phase 1 B10 passes. A new account needs new API keys (`.env`, plus the O1 key-rotation date), and it would not hold the 1-share SPY position from O7 that B10/G-9 relies on.

**Fallback:** if $35k cannot be set, reports scale every dollar figure to a $35k desk. Position sizing uses the configured $35k and $5k, never the broker's $100k.

## 5. Points flagged for the owner

Agent findings. Points 1–5 were answered by the owner on 2026-11-25 (answers below each). Points 6–8 are still RETRO debt.

1. **E-1 arm A has no stop, but D-13 makes stops mandatory in the sleeve.**
   - Proposal: run all three E-1 arms as simulations on paper market data, forward-logged, with no broker orders. Arm A then never sits in the sleeve without a stop, and the arms stay comparable.
   - Arm A is also the disposition effect described in FAILURE_LIBRARY F-15, which is why it is worth testing rather than assuming.
   - **Owner answer: yes, simulate all arms.**
2. **Covered calls "on shares already held":**
   - Assignment sells the shares, so covered calls on core shares would break D-14. Proposal: sleeve shares only.
   - A covered call needs 100 shares. At a $5k sleeve with 1% risk ($50), that fits only low-priced stocks. The share leg's downside also counts against D-11.
   - **Owner answer: yes, sleeve shares only.**
3. **Options sizing under D-11:** counting options against the sleeve limits caps each options trade's maximum loss at $50 at a $5k sleeve. Please confirm that the learning track uses the same 1% cap, rather than a separate learning cap.
   - **Owner answer: yes, $50 maximum loss per options trade.**
4. **A separate paper account for options learning:**
   - Manual options trades in the same paper account the automation reads would break its reconciliation (invariant 9), because it would see positions it did not create.
   - Proposal: a separate Alpaca paper account, if Alpaca allows it (§4). Its trades are entered into the ledger by hand and counted against the sleeve limits.
   - **Owner answer: yes, a separate options paper account.**
5. **$250 cap vs sleeve shape:** five positions in a $5k sleeve average $1k each. Most full-size sleeve entries will therefore go to approval (Tier B), so approval is the normal path in paper, not the exception.
   - **Owner answer: raise the paper-test cap to $1,000 (D-01) and revisit it at the live gate.** Consequence: up to the full $5k sleeve (5 × $1,000) can now be deployed without an approval. It is still bounded by D-07 to D-12.
6. **Loss-limit definitions:** the exact baseline for each limit is a Phase 2 SPEC item:
   - "day" and "week": prior-close equity, and equity at the start of the week;
   - "peak": a running high-water mark, and whether it resets each year to match "annual tolerance";
   - whether realized and unrealized losses both count.
7. **Real balances in git:** paper reports in `docs/checkins/` are fine. From the Phase 6 live gate, any report with real balances goes in `private/`, and only the owner's answers stay in `docs/checkins/`.
8. **Running-cost estimate:** HANDOFF's ~$120–220/month estimate assumed LLM and hosting spend. For paper, D-15/D-16 supersede it. Phase 5 hosting must fit inside $25/month, or the owner approves the extra.
