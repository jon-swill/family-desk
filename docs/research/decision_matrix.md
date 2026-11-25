# Decision matrix: engine, broker and data sources (Phase 1, D6)

## 1. Header

**Purpose.** Compare the execution/backtest engine candidates (PRD §5), the broker candidates (FR-3) and the data-source options (Phase 1 plan D6) on criteria fixed in advance, so the Phase 1 recommendation rests on cited evidence and not on the plan's wording or on familiarity. Traces to PRD §5, §6, FR-3 and Phase 1 gate G-1.

**Status: criteria and weights frozen 2026-11-25 before any scoring (A5).** No candidate has been scored. Sections 6 to 9 are empty.

**Freeze rule.** Weights may not change after scoring starts without an owner-approved, dated row in the amendment table below. The same applies to criteria, level anchors, worst plausible scores, knock-out flags and the method in section 5. Scoring starts with the first score cell committed by A6, A7 or A10. When an amendment lands after scoring has started, A8 reports totals under both the original and the amended version, and the dissent says whether the change moved the result.

**Outcomes this matrix may and may not produce.**
- Engine: a recommendation labelled **provisional, install-check in Phase 2**. Engine packages bundle live order adapters, so installing one is a CLAUDE.md hard stop before the Phase 3 gate. Evidence this phase is from documentation only, and the Phase 2 install-check needs explicit owner approval.
- Broker: a ranking only. It does not choose the live broker; that choice stays open by owner decision (RETRO 2026-11-24).
- Data: a ranking only. It buys nothing (Phase 1 non-goals; RETRO 2026-11-24: no paid news).

### Amendment table

| Date | Section and item | Change (old → new) | Reason | Owner approval (where recorded) |
|---|---|---|---|---|
| | | | | |

## 2. Scoring scale and citation rule

### Scale (0 to 5, integers only)

| Score | Anchor |
|---|---|
| 5 | Fully meets the criterion as documented, with no workaround |
| 4 | Meets it with minor limits or ordinary configuration |
| 3 | Partly meets it; a documented workaround exists that we would own and can test |
| 2 | Weak; the workaround is significant, or the burden or cost recurs |
| 1 | Barely; the workaround is fragile or unsupported, or the option conflicts with a principle unless our own code compensates |
| 0 | Absent or blocked, or it breaks an invariant or a hard stop with no workaround |

Each criterion below also says what a 5 and a 0 look like where the general anchor is not enough.

### Citation rule

Every score cell carries exactly one of these:
1. **A primary source**: the vendor's own documentation, terms, status page or filing, or a regulator's record, as a link plus the date it was accessed (ISO date).
2. **For data sources only, a D18 spike measurement**: a reference to the field in `docs/phases/phase_1/spike_evidence.md`, with the spike commit hash.
3. **`unverified (reason)`**: for example `unverified (login required)` (plan risk R4: no accounts are created), `unverified (no primary source found)`, `unverified (secondary only: <link>)` or `unverified (dead link)`.

Rules for cells:
- A secondary source (forum post, blog, third-party wrapper documentation) may support a primary source. A score that rests on a secondary source alone is marked `unverified (secondary only: <link>)`.
- An `unverified` cell still carries the scorer's best-estimate score, which counts in the base total. The robustness check (section 5.3) replaces it with the criterion's worst plausible score.
- Engine evidence is from documentation only. Nothing is installed or imported this phase.
- A broker or data cell cited to a failure-library entry or a proposal (F-*, P-*) also cites that entry's primary source.
- The scorer records the evidence in one line next to the score. The line quotes or paraphrases the source; it is not an opinion.

### Score-table layout (for A6, A7, A10)

One row per candidate per criterion:

| Criterion ID | Candidate | Score (0–5) | Evidence (one line) | Source (link + accessed date, D18 field, or `unverified (reason)`) | Status (`cited` / `measured` / `unverified`) |
|---|---|---|---|---|---|

## 3. Criteria and weights

Weights reflect the master brief's order of concern: safety and compliance weigh more than convenience. Each table's weights sum to 100.

**Worst plausible score**: the score an `unverified` cell takes in the robustness check. It is normally 0 or 1, and the column gives the reason.

**KO (knock-out).** A criterion marked KO protects an invariant, a hard stop or an owner decision. A candidate that scores 0 on a KO criterion is excluded from the recommendation or the top of the ranking, whatever its total. It stays in the table, marked `excluded (KO <ID>)`.

### 3.1 Engines

Candidates: **NautilusTrader**, **LEAN**, **custom on vectorbt**. For scoring, "custom on vectorbt" means the open-source vectorbt edition for vectorised research backtests, plus our own Python event loop, broker adapters and execution layer. (The paid vectorbt PRO would be a paid service, which is a CLAUDE.md hard stop, so it is not the candidate.) Where we would write a capability ourselves, the score reflects the work and risk that we would own.

| ID | Criterion | What is measured / evidence wanted | Weight | Worst plausible (reason) | Protects |
|---|---|---|---|---|---|
| E-1 (KO) | Own deterministic risk kernel in front of every order | Documentation shows that every order path, including engine-internal ones (liquidation, risk-engine actions, "close all"), can be routed through our own pure-function kernel, and that the engine has no path that bypasses it. 5 = a documented single choke point we control. 0 = some order path cannot be intercepted | 15 | 0 (if we can't show interception, an order can bypass the kernel, which breaks invariant 1) | inv. 1, NFR-1, FR-11, MASTER_BRIEF principle 1 |
| E-2 | Paper↔live parity | The same strategy and kernel code runs in backtest, paper and live with only configuration changing; documented differences between simulated and live fills | 12 | 1 (an unknown parity gap means forward tests may not predict live; 0 is kept for a documented split code path) | inv. 7, F-02, P-14 (proposed), Phase 5 gate |
| E-3 | Point-in-time and look-ahead safety | Documented point-in-time data handling, event-time ordering, handling of corporate actions and survivorship, and guards against using future bars | 12 | 1 (we can still add our own point-in-time checks, but unverified support must be assumed weak) | inv. 8, F-02, F-09, R-18, R-31 |
| E-4 | Control of order types | Market orders can be refused or never emitted by the engine; marketable limits with collars and broker-side stop-limit orders can be expressed; no hidden market-order fallback (for example on liquidation or expiry) | 8 | 0 (a hidden market-order path would break invariant 13) | inv. 13, R-25, R-26, FR-19 |
| E-5 | Install footprint | Whether live order adapters install by default or only as opt-in extras; dependency count; compiled or native components; whether a backtest-only install with no order-capable code is documented | 8 | 0 (an unknown footprint must be assumed to include order adapters, which is the CLAUDE.md hard stop) | CLAUDE.md hard stop, R-14, NFR-3 (pinned dependencies) |
| E-6 | Event-driven vs vectorised fit for both backtest and live | One model that serves research backtests and live event handling; deterministic replay of a recorded event stream | 9 | 1 (we could still run two separate stacks, at the cost of parity) | NFR-2, NFR-6, NFR-8 |
| E-7 | Adapters for the candidate brokers | Documented, maintained adapters for Alpaca, Schwab Trader API, Robinhood Agentic Trading and IBKR, behind one interface; how much adapter code we would own | 8 | 0 (assume we write and maintain every adapter ourselves) | FR-3, FR-27 (proposed) |
| E-8 | Windows support (documentation only) | Native Windows support stated in the official docs for the versions we would use; otherwise documented WSL2 or container use. Dev is on the owner's Windows PC; production is Linux (PRD §5) | 7 | 1 (Linux-only tools can usually run under WSL2 on Windows 11, so 0 is kept for "not runnable on the dev PC") | CLAUDE.md (Windows dev), PRD §5, plan risk R6 |
| E-9 | Python fit | Strategy, kernel and adapter code written in Python; typed APIs that work with `mypy --strict`; no second language needed for our code | 8 | 1 (a second language is a burden, not a block) | PRD §5 (Python; functional core), NFR-2 |
| E-10 | Maintenance activity and community health | Release cadence over the last 12 months, open-issue handling, number of active maintainers, documented deprecation policy | 7 | 1 (an abandoned engine can be forked or pinned, but at high cost) | P-16 (proposed), R-14, NFR-3 |
| E-11 | Licence and cost | The licence permits private household use and changes to the code; any paid tier or cloud dependence; licence terms that bind our own code | 6 | 0 (an unknown licence may forbid our use; paid parts are a CLAUDE.md hard stop) | NFR-5, CLAUDE.md hard stop (paid services) |
| | **Total** | | **100** | | |

Weight rationale (one line each):
- E-1 (15): principle 1 and invariant 1 are the system's first rule; an engine that cannot keep the kernel in front of orders is disqualified.
- E-2 (12): every promotion decision (rule 7, Phase 5) relies on paper predicting live.
- E-3 (12): look-ahead bias silently invalidates every backtest (rule 8, F-09), and this is the main thing a backtest engine offers.
- E-4 (8): no market orders is a hard rule; the kernel can refuse them too, so the engine's part is defence in depth.
- E-5 (8): installing order-capable code before Phase 3 is a hard stop, so the footprint decides whether the Phase 2 install-check can happen at all.
- E-6 (9): one deterministic event model serves both NFR-2 and auditability.
- E-7 (8): FR-3 keeps broker switching cheap, but adapters are code we can write.
- E-8 (7): needed for daily development on the owner's PC; production runs on Linux, so it weighs less than safety.
- E-9 (8): the whole codebase and its quality gates are Python.
- E-10 (7): an unmaintained engine becomes our maintenance burden and a supply-chain risk.
- E-11 (6): household use and low cost matter, but most of the cost is in time, which E-7 and E-9 already count.

### 3.2 Brokers

Candidates: **Alpaca**, **Schwab Trader API**, **Robinhood Agentic Trading**, **IBKR**. Score the documented automated-API offering, not the retail app.

| ID | Criterion | What is measured / evidence wanted | Weight | Worst plausible (reason) | Protects |
|---|---|---|---|---|---|
| B-1 (KO) | Broker-side protective orders | Stop-limit, bracket and OCO orders that rest at the broker through the API for the instruments we trade; collar or limit-offset support; extended-hours behaviour; whether accepted stops can be read back by ID. 0 = protective stops cannot rest at the broker | 14 | 0 (if stops can't be shown to rest at the broker, invariant 4 can't hold) | inv. 4, inv. 13, R-25, R-26, FR-19, P-09 (proposed) |
| B-2 (KO) | API terms permit our automation | The official API terms allow automated trading by an individual for their own account, with no scraping or screen control | 9 | 0 (without written permission we can't comply with C-6) | C-6, NFR-7, P-16 (proposed) |
| B-3 (KO) | Regulation and SIPC | A registered US broker-dealer, FINRA member and SIPC member for the account type we would use; the carrying or clearing firm is named | 8 | 0 (R-39 permits only regulated, SIPC-member brokers) | R-39, F-17 |
| B-4 | Key controls and least privilege | Read-only keys; keys scoped to a single account (so automation reaches only the active sleeve); trading without withdrawal rights; IP allowlist; key rotation and revocation | 10 | 0 (assume a full-access key with no allowlist, so only our code limits it) | P-04, R-21, NFR-3, inv. 5 |
| B-5 | Authentication burden for unattended operation | Token and session lifetimes, forced re-login or MFA cadence, scheduled restarts, and whether a person must act during market hours | 8 | 1 (assume frequent interactive re-login; 0 is kept for "cannot run unattended at all") | P-17 (proposed), NFR-4 |
| B-6 | Paper availability and parity | A paper or sandbox environment through the same API, with the same order types; documented differences in its fill model | 9 | 0 (no paper environment means no Phase 5 on that broker) | inv. 7, P-14 (proposed), Phase 5 gate |
| B-7 | Incident history (from A4) | Outages, wrong balances or fills, API retirements, regulator findings, with dates and the broker's response (`failure_library_proposals.md`, A4 ranked causes) | 9 | 1 (no record found is not evidence of reliability; 0 is kept for an unresolved regulator finding of systemic failure) | F-05, R-23, P-07, P-11, P-12, P-15, P-16 (proposed) |
| B-8 | Options, shorting and margin can be switched off at the account | An account-level setting or account type that blocks options, shorting and margin, readable through the API so it can be asserted at startup | 7 | 1 (the kernel still rejects options and shorting under invariant 16, so a missing broker switch removes defence in depth, not the control) | inv. 16, R-32, C-2, C-8, P-11 (proposed) |
| B-9 | Cost-basis and lot export | Lot-level cost basis, realised gain or loss, and wash-sale adjustments, available through the API or as a documented export; year-end tax forms | 7 | 1 (broker 1099-B basis reporting exists for covered securities; worst case is no machine-readable lot export) | inv. 12, FR-21, FR-23, C-5, C-10 |
| B-10 | Rate limits | Documented request limits per endpoint and account, rate-limit headers, and a separate allowance or priority for cancels | 5 | 1 (assume a low, undocumented limit that we must stay well under) | P-13 (proposed), R-15 |
| B-11 | Idempotency and reconciliation support | Client order IDs, order lookup by client order ID, fills or activities with execution IDs, streaming order updates, positions and cash endpoints | 6 | 0 (without client order IDs, a timed-out order can't be resolved safely) | inv. 9, FR-18, P-07, P-15 (proposed) |
| B-12 | Fractional shares | Fractional or notional orders through the API, and which order types allow them | 3 | 0 (whole shares only is a plausible case and still workable) | FR-15 (small trades), FR-11 (sizing) |
| B-13 | Cost | Commissions, API or data fees, account minimums, regulatory fee pass-through | 5 | 1 (assume paid API or data access; 0 is kept for a cost above the NFR-5 budget) | NFR-5, rule 7 (all costs) |
| | **Total** | | **100** | | |

Weight rationale (one line each):
- B-1 (14): broker-side protection is what keeps a crashed or cut-off bot safe (invariant 4); it is the broker's most safety-relevant feature.
- B-2 (9): breaking a broker's terms is a compliance failure and can close the account.
- B-3 (8): custody failure is the one loss our code cannot limit (F-17); a knock-out matters more than the weight.
- B-4 (10): key theft is a top real-world failure (F-04); least privilege is the only control outside our own code.
- B-5 (8): forced re-login stops an unattended bot from managing its orders.
- B-6 (9): Phase 5 forward tests need paper trading through the same API.
- B-7 (9): A4 ranked broker unavailability and wrong broker data among the most common causes of failure.
- B-8 (7): important defence in depth, but the kernel already enforces the rule.
- B-9 (7): tax correctness is a principle (rule 12), but our own lot-level ledger is the system of record.
- B-10 (5): a client-side budget (P-13) can work within most limits.
- B-11 (6): idempotent orders and reconciliation are rule 9; much of that work sits in our own ledger, but a broker without client order IDs leaves P-07 uncontrolled.
- B-12 (3): a convenience for small trades and precise sizing.
- B-13 (5): costs count in rule 7, but at household volumes they matter less than safety.

### 3.3 Data sources

The data options fall into two groups that cannot be compared on the same criteria: price feeds and company-event sources. Each group therefore has its own table, weights sum to 100 in each, and each group is ranked on its own.

#### 3.3a Price and reference-price feeds

Candidates: **Alpaca free IEX**, **Alpaca delayed SIP on the free plan**, **Alpaca paid SIP (ranked only, not bought)**. iNAV or indicative-value availability for R-27 is criterion DP-7. A10 also records, as a finding outside the ranking, which source (if any) carries indicative values for SPY, QQQ and IWM.

The spike measures only the free IEX feed (paper accounts receive IEX only). Measured criteria for the other two candidates are therefore scored from primary documentation or marked `unverified`. The dissent must say whether this asymmetry favoured or penalised IEX.

| ID | Criterion | What is measured / evidence wanted | Weight | Worst plausible (reason) | Protects |
|---|---|---|---|---|---|
| DP-1 (KO) | Terms permit our use | Personal, non-commercial use for automated decisions; storage in a private local log; no redistribution; the plan the account is actually entitled to | 12 | 0 (use outside the terms breaks C-7) | C-7, NFR-7 |
| DP-2 | Share of consolidated volume | The feed's share of consolidated US equity volume, and whether it is NBBO or a single venue (primary docs) | 14 | 1 (assume a single-venue feed; 0 is kept for a feed with no usable price at all) | inv. 11 (collars, liquidity floor), R-22, R-27 |
| DP-3 | Quote update rate on the watchlist | Quotes per minute per symbol for SPY, QQQ, IWM, AAPL and MSFT during the session (D18 for IEX; docs or `unverified` for the others) | 10 | 1 (assume sparse updates) | inv. 14 (stale data), R-24, P-12 (proposed) |
| DP-4 | Quoted spread on the watchlist | Median and tail quoted spread per symbol (D18 for IEX), and whether it reflects the NBBO | 10 | 1 (assume spreads wider than the NBBO, which distorts collars and the max-spread floor) | inv. 11, R-22, R-26 |
| DP-5 | Latency and timeliness | Real-time vs delayed (for example 15 minutes), exchange timestamps on each message, end-to-end delay | 14 | 0 (a delayed price used for an order decision is stale data under invariant 14) | inv. 14, R-24, NFR-8, P-12 (proposed) |
| DP-6 | Reliability and detectable staleness | Incident history (vendor status page), exchange timestamps that allow age checks, reconnect rules, connection limits | 12 | 1 (assume silent stalls happen, as A4 found; 0 is kept for "staleness cannot be detected") | P-02, P-12 (proposed), NFR-4 |
| DP-7 | iNAV or indicative-value availability | Indicative value for the watchlist ETFs (SPY, QQQ, IWM) from this feed, its update rate and documentation | 8 | 0 (absence is the plausible default for a price feed) | R-27, FR-19 |
| DP-8 | Cost | Monthly price and what the price includes; fits the NFR-5 budget (ranked only, nothing is bought) | 10 | 1 (assume a recurring fee; 0 is kept for a cost above the NFR-5 budget) | NFR-5, rule 7, CLAUDE.md hard stop (spending) |
| DP-9 | Same feed in paper and live | The same feed and entitlement in paper and live, so forward tests use the prices live would | 6 | 1 (assume paper and live differ) | inv. 7, P-14 (proposed) |
| DP-10 | Limits and history | Symbol and connection limits, REST call budget, history depth and timestamps for Phase 4 point-in-time research | 4 | 1 (assume tight limits) | P-13 (proposed), inv. 8 |
| | **Total** | | **100** | | |

Weight rationale (one line each):
- DP-1 (12): the owner decided to follow every provider's terms; this criterion is a knock-out.
- DP-2 (14): collars, the liquidity floor and the R-27 check are only as good as the reference price.
- DP-3 (10): sparse quotes leave staleness checks halting often or trading on old prices.
- DP-4 (10): a misleading spread breaks collars and the max-spread liquidity floor.
- DP-5 (14): trading on stale data is a hard rule (invariant 14); a delayed feed is safe only for reference.
- DP-6 (12): silent data stalls were a top A4 cause; we must at least be able to detect them.
- DP-7 (8): R-27 needs an indicative value, but it can come from a separate source.
- DP-8 (10): spend is a P&L line with hard caps (rule 9); the ranking buys nothing.
- DP-9 (6): paper results must predict live (rule 7).
- DP-10 (4): limits matter for Phase 4 research, but the watchlist is small.

#### 3.3b Company-event sources

Candidates: **Alpaca/Benzinga news**, **EDGAR only**, **issuer IR RSS**. IR RSS ingestion is not built this phase (non-goal); it is scored from documentation only.

| ID | Criterion | What is measured / evidence wanted | Weight | Worst plausible (reason) | Protects |
|---|---|---|---|---|---|
| DE-1 (KO) | Terms permit automated access | Official API or feed (no scraping); automated polling or streaming allowed at our cadence; private local storage; no redistribution | 14 | 0 (use outside the terms breaks C-6 and C-7) | C-6, C-7, NFR-7 |
| DE-2 | Primary-source status and provenance | Whether the item is the primary source (issuer filing, issuer release) or a report about it; the original source named on each item | 16 | 1 (assume secondary reporting; 0 is kept for unattributed items) | inv. 6, MASTER_BRIEF principle 6 (no rumor trades) |
| DE-3 | Coverage of watchlist and held-symbol events | Share of material events for AAPL and MSFT and the fund trusts SPY, QQQ, IWM that the source carries; correct handling of identifiers shared across funds | 12 | 1 (assume partial coverage) | FR-8, FR-9, P-05 |
| DE-4 | Timeliness | Delay from event publication to receipt; streaming or polling cadence allowed | 12 | 1 (assume minutes of delay, which misses FR-9's 60 seconds) | FR-9, NFR-8 |
| DE-5 | Reliability and provable liveness | Status page or incident history; a way to prove the path is alive on a known positive (ack, unfiltered sample, REST cross-check) | 12 | 1 (assume silent failure is possible) | P-02, P-12 (proposed), NFR-4 |
| DE-6 | Machine-readability and attribution | Structured fields: symbol or CIK tags, form type, timestamps with time zone; parseable without free-text interpretation | 10 | 1 (assume symbol tagging must be inferred from text) | P-05, P-18 (proposed), inv. 6 (data, never instructions) |
| DE-7 | Rate limits and access rules | Documented limits (for example SEC 10 requests per second), User-Agent rules, connection limits | 6 | 1 (assume a low, undocumented limit) | C-7, P-13 (proposed) |
| DE-8 (KO) | Cost within the free-sources decision | Free under the account we already hold, or free and official; 0 = needs a paid news subscription | 8 | 0 (a paid requirement breaks the owner decision of 2026-11-24) | RETRO 2026-11-24 (no paid news), NFR-5 |
| DE-9 | Point-in-time history | Trustworthy, unrevised publication timestamps and history depth, so forward-logged decisions and Phase 4 research can be timed correctly | 10 | 1 (assume timestamps can be revised or are missing) | inv. 8, R-31, FR-5, F-09 |
| | **Total** | | **100** | | |

Weight rationale (one line each):
- DE-1 (14): following provider terms is an owner decision; this criterion is a knock-out.
- DE-2 (16): "no single source, no rumor" trading rests on knowing which items are primary.
- DE-3 (12): an event the source never carries cannot be checked.
- DE-4 (12): FR-9 sets a 60-second target for the "why is it moving" brief.
- DE-5 (12): silence must be provably healthy (P-02, approved).
- DE-6 (10): structured tags avoid misattribution (P-05) and keep text as data.
- DE-7 (6): limits shape cadence but rarely decide the choice.
- DE-8 (8): the free-only owner decision is enforced by the knock-out; the weight scores how freely the source can be used.
- DE-9 (10): forward-test integrity (rule 8) needs trustworthy timestamps.

## 4. Who scores what

| Task | Scores | Depends on |
|---|---|---|
| A6 | Section 3.1 (engines), documentation only, no installs | A5 |
| A7 | Section 3.2 (brokers); B-7 uses A4's incidents | A5, A2, A4 |
| A10 | Sections 3.3a and 3.3b; DP-3 and DP-4 for IEX from D18; terms from A2 | A5, A2, B11 |
| A8 | Section 5 method applied to all tables | A6, A7, A10 |

Scorers record each cell as they find the evidence and do not look at the other candidates' totals while scoring.

## 5. Method for A8 (written now, applied after scoring)

### 5.1 Totals

For each candidate in each table: **total = Σ (weight × score)** over the table's criteria. The maximum is 500. A8 reports the raw total and the total as a percentage of 500. A candidate with a 0 on a KO criterion is marked `excluded (KO <ID>)` and cannot be the recommendation or rank first, whatever its total. A lead of less than 5 percentage points is reported as a near-tie, and the dissent discusses it.

### 5.2 Unverified share

For each candidate, A8 reports:
- **By weight**: Σ weights of the candidate's `unverified` cells (out of 100).
- **By count**: the number of `unverified` cells out of the number of criteria in the table.

Both appear in one table per candidate group. A candidate with an unverified share by weight above 50 must be discussed in the dissent.

### 5.3 Robustness check

Set every `unverified` cell to its criterion's worst plausible score (section 3), keep every cited and measured cell, re-apply the KO rule and recompute the totals. A8 shows the base and robustness totals side by side.
- **Engines:** if the winner changes, no recommendation is made. G-1 fails (phase-gate HOLD) unless the owner records at G3 that the engine choice moves to the Phase 2 install-check.
- **Brokers and data:** if rank 1 changes, the ranking is published as "not robust", with both orders shown and no leading candidate named. These rankings decide nothing (RETRO 2026-11-24; Phase 1 non-goals). Reading G-1's HOLD rule as applying to the engine recommendation only is this document's interpretation; phase-gate confirms or overrides it.

### 5.4 Sensitivity check

For each criterion in turn, multiply its weight by 1.5, then by 0.5. Rescale the other weights in that table proportionally so the table still sums to 100: each other weight w_j becomes w_j × (100 − w_i′) / (100 − w_i), where w_i′ is the moved weight. Recompute the base totals each time. A8 reports a table of every single-weight move that changes the winner (engines) or rank 1 (brokers, each data group). Any flip is reported in the dissent, and the recommendation or ranking stays provisional. A sensitivity flip alone does not fail G-1.

### 5.5 Recommendation and rankings

- Engine: name the winner, labelled **provisional, install-check in Phase 2**. Nothing is installed or imported in Phase 1.
- Brokers: a ranking with totals. It does not choose the live broker (RETRO 2026-11-24). Alpaca stays the paper broker by owner decision, whatever its rank.
- Data: a ranking per group (3.3a, 3.3b) with totals. Nothing is bought; any paid option is ranked only.

### 5.6 Skeptic's dissent (required)

A8 writes a dissent from a skeptic's framing (MASTER_BRIEF working rules). At a minimum it covers:
- the strongest case for the runner-up in each table;
- the cells the result leans on most, and which of them are `unverified`;
- every robustness change and every sensitivity flip;
- anchoring: Alpaca is the paper broker and the spike runs on Alpaca, so its documentation was read most closely. Did that familiarity raise Alpaca's or the IEX feed's scores?
- the limits of documentation-only engine evidence (plan risk R6), and what the Phase 2 install-check must confirm.

## 6. A6 Engine scores

Scored 2026-11-25 by A6 against the frozen section 3.1 criteria and the section 2 scale. Evidence is from documentation, official repositories (README, licence, packaging metadata), the GitHub REST API for repository metadata, and PyPI release feeds only. No engine package was installed, downloaded or imported. Every source was accessed 2026-11-25. Statements that are the vendor's own claims about its product (for example parity claims) are marked "vendor claim". No totals and no recommendation (A8).

| Criterion ID | Candidate | Score (0–5) | Evidence (one line) | Source (link + accessed date, D18 field, or `unverified (reason)`) | Status (`cited` / `measured` / `unverified`) |
|---|---|---|---|---|---|
| E-1 | NautilusTrader | 3 | Docs: new orders reach the ExecutionEngine only via the built-in RiskEngine, which "sits on the submit and modify path" (cancels bypass it); `RiskEngineConfig.bypass` exists; docs do not say the RiskEngine can be replaced or extended with our kernel, so the choke point would be a strategy-side wrapper we own; `close_position`, `close_all_positions`, `market_exit` and `manage_stop` submit orders internally | `unverified (docs show one engine-owned choke point but do not document that our own kernel can sit in it or that a wrapper catches engine-internal submits)`: https://nautilustrader.io/docs/latest/concepts/execution and https://nautilustrader.io/docs/latest/concepts/strategies (accessed 2026-11-25) | unverified |
| E-1 | LEAN | 2 | Docs: a custom Python `DefaultBrokerageModel` subclass can override `can_submit_order`/`can_update_order`, but docs say LEAN uses "some of the brokerage model rules"; the engine generates its own orders (margin-call liquidations, which can be disabled with `MarginCallModel.NULL`; automatic liquidation of delisted securities, with no documented off switch); docs do not say these pass the brokerage-model hook | `unverified (docs do not say whether engine-generated margin-call and delisting liquidations pass can_submit_order)`: https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/brokerages/key-concepts, https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/margin-calls, https://www.quantconnect.com/docs/v2/writing-algorithms/securities/asset-classes/us-equity/corporate-actions (accessed 2026-11-25) | unverified |
| E-1 | Custom on vectorbt | 4 | vectorbt docs: scheduling "does not fetch data, persist state, retry failures, or place orders by itself"; Alpaca integration is data-only; no order path exists in the library, so the only order path is our own event loop, whose single kernel choke point we would write and test (work and risk ours) | https://vectorbt.dev/getting-started/features/ (accessed 2026-11-25) | cited |
| E-2 | NautilusTrader | 4 | Vendor claim: "The same strategy and execution-algorithm code can run across backtest and live"; docs list six live-only differences (venue, transport, timing, persistence, external activity, reconciliation) and say a simulation "may not reproduce" them | https://nautilustrader.io/docs/latest/concepts/live/ and https://github.com/nautechsystems/nautilus_trader (accessed 2026-11-25) | cited |
| E-2 | LEAN | 4 | Vendor claim: "Algorithms should generally work seamlessly shifting from backtesting to live trading with no changes required"; documented differences: event timing, daily data delayed 4–8 hours live, no automatic state management live; fill-model behaviour live vs backtest not stated | https://www.quantconnect.com/docs/v2/writing-algorithms/live-trading/key-concepts and https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/key-concepts (accessed 2026-11-25) | cited |
| E-2 | Custom on vectorbt | 1 | vectorbt `from_signals`/`from_orders` are array-based simulations and the library has no live mode; parity would need our own event loop to replay history too, so the vectorised research path is a separate code path from live | https://vectorbt.dev/api/portfolio/base/ and https://vectorbt.dev/getting-started/features/ (accessed 2026-11-25) | cited |
| E-3 | NautilusTrader | 3 | Docs: backtest data "ordered by `ts_init` using a stable sort", giving deterministic replay; `time_bars_timestamp_on_close` defaults to True (bar stamped at close); corporate actions, splits, dividends, survivorship, point-in-time universe and look-ahead are not covered on the data or backtesting pages, so we would own them | https://nautilustrader.io/docs/latest/concepts/data and https://nautilustrader.io/docs/latest/concepts/backtesting (accessed 2026-11-25) | cited |
| E-3 | LEAN | 4 | Docs: algorithm time equals the Time Frontier and "you can only access data from before this Time Frontier" to avoid look-ahead; splits, dividends, delistings and symbol changes are delivered as events with normalization modes; locally these rely on the US Equity Security Master, a paid subscription ($600/yr and up), or factor data we would produce ourselves | https://www.quantconnect.com/docs/v2/writing-algorithms/key-concepts/time-modeling/timeslices, https://www.quantconnect.com/docs/v2/writing-algorithms/securities/asset-classes/us-equity/corporate-actions, https://www.quantconnect.com/docs/v2/lean-cli/datasets/quantconnect/us-equity (accessed 2026-11-25) | cited |
| E-3 | Custom on vectorbt | 2 | Docs put look-ahead on the user: signals must be shifted one bar "so a close observed today cannot trigger a fill at that same close"; `from_order_func` has "less risk" of look-ahead; no corporate-action, survivorship or point-in-time handling documented, so all guards are ours | https://vectorbt.dev/getting-started/features/ and https://vectorbt.dev/api/portfolio/base/ (accessed 2026-11-25) | cited |
| E-4 | NautilusTrader | 3 | Docs: `close_position`/`close_all_positions` "submit closing market orders"; `market_exit` closes with "market orders tagged `MARKET_EXIT`"; `manage_stop=True` makes `stop()` run a market exit; all are strategy-invoked and off by default, so our wrapper must forbid them; IB adapter supports limit and stop-limit and bracket order lists | https://nautilustrader.io/docs/latest/concepts/strategies and https://nautilustrader.io/docs/latest/integrations/interactive_brokers/ (accessed 2026-11-25) | cited |
| E-4 | LEAN | 2 | Docs: `liquidate()` "creates market orders"; market-closed liquidations are converted to market-on-open; the engine auto-liquidates delisted positions and margin calls generate liquidation orders (order type not stated); limit and stop-limit exist (Alpaca plugin lists StopLimit for equities) | https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/liquidating-positions, https://www.quantconnect.com/docs/v2/writing-algorithms/securities/asset-classes/us-equity/corporate-actions, https://github.com/QuantConnect/Lean.Brokerages.Alpaca (accessed 2026-11-25) | cited |
| E-4 | Custom on vectorbt | 4 | vectorbt places no orders ("does not ... place orders by itself"), so every order type is built by our own code; no hidden fallback exists, but the order layer and its tests are work we own | https://vectorbt.dev/getting-started/features/ (accessed 2026-11-25) | cited |
| E-5 | NautilusTrader | 1 | IB docs: "The Python package includes the adapter"; v2 `pyproject.toml` has `dependencies = []` and one extra (`visualization`), i.e. a single compiled Rust/PyO3 wheel; all live adapters ship in the base install and no backtest-only install is documented | https://nautilustrader.io/docs/latest/integrations/interactive_brokers/ and https://raw.githubusercontent.com/nautechsystems/nautilus_trader/develop/python/pyproject.toml (accessed 2026-11-25) | cited |
| E-5 | LEAN | 3 | Main repo `Brokerages/` holds only shared code plus `Paper`, `Backtesting` and `CrossZero`; live brokerages are separate plugin repos (e.g. `Lean.Brokerages.Alpaca`), which suggests a source build without live plugins, but no backtest-only install is documented; the CLI path uses the `quantconnect/lean` Docker image (13.1 GB, contents not listed) and needs the .NET 10 SDK to build from source | `unverified (backtest-only footprint inferred from repo layout; no doc states it, and the Docker image's contents are not listed)`: https://github.com/QuantConnect/Lean/tree/master/Brokerages, https://hub.docker.com/r/quantconnect/lean, https://github.com/QuantConnect/Lean (accessed 2026-11-25) | unverified |
| E-5 | Custom on vectorbt | 4 | `pyproject.toml`: base install has 18 dependencies (numpy, pandas, scipy, numba with LLVM, plotly, ipywidgets, requests, schedule …) and no broker SDK; the `full` extra adds order-capable SDKs (`alpaca-py`, `python-binance`, `ccxt`), so only the base install is backtest-only; optional `rust` extra is compiled | https://raw.githubusercontent.com/polakowo/vectorbt/master/pyproject.toml (accessed 2026-11-25) | cited |
| E-6 | NautilusTrader | 5 | Event-driven core used for both backtest and live (vendor claim); backtests give "deterministic replay" via stable sort on `ts_init`; a Deterministic Simulation Testing page exists | https://nautilustrader.io/docs/latest/concepts/data, https://nautilustrader.io/docs/latest/concepts/live/, https://nautilustrader.io/docs/latest/concepts/ (accessed 2026-11-25) | cited |
| E-6 | LEAN | 4 | One event-driven algorithm model for backtest and live; backtest events are "triggered as fast as possible" and live in realtime (vendor claim); deterministic replay of a recorded live stream is not documented on the pages read | https://www.quantconnect.com/docs/v2/writing-algorithms/live-trading/key-concepts (accessed 2026-11-25) | cited |
| E-6 | Custom on vectorbt | 2 | vectorbt is vectorised (`from_signals`, `from_orders`); `from_order_func` is event-driven callbacks inside the simulator only; live event handling and replay would be our own second stack | https://vectorbt.dev/api/portfolio/base/ (accessed 2026-11-25) | cited |
| E-7 | NautilusTrader | 2 | Integrations list: Interactive Brokers "Stable" (needs TWS or IB Gateway); no Alpaca, Schwab or Robinhood brokerage adapter ("Lighter on Robinhood" is a crypto DEX venue); we would write 3 of 4 adapters (Python custom adapters are documented) | https://nautilustrader.io/docs/latest/integrations/, https://nautilustrader.io/docs/latest/integrations/interactive_brokers/, https://nautilustrader.io/docs/latest/concepts/python/ (accessed 2026-11-25) | cited |
| E-7 | LEAN | 3 | Brokerage list includes Alpaca, Charles Schwab and Interactive Brokers, not Robinhood; local deployment of these goes through the LEAN CLI, which needs a paid-tier organization; Schwab "only supports authenticating one account at a time per user"; IB plugin requires IBKR Pro; a Robinhood adapter would be C# we write | https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/brokerages, https://www.quantconnect.com/docs/v2/lean-cli/live-trading/brokerages/charles-schwab, https://github.com/QuantConnect/Lean.Brokerages.InteractiveBrokers (accessed 2026-11-25) | cited |
| E-7 | Custom on vectorbt | 0 | vectorbt has no broker connections (Alpaca is a data source only); we would write and maintain all four adapters, which is this criterion's worst case | https://vectorbt.dev/getting-started/features/ and https://github.com/polakowo/vectorbt (accessed 2026-11-25) | cited |
| E-8 | NautilusTrader | 4 | Installation docs: officially supported and CI-tested on "Windows Server 2022+ on x86_64" with PyPI wheels; Windows 11 desktop is not named; source-build setup steps are documented for Linux and macOS only | https://nautilustrader.io/docs/latest/getting_started/installation (accessed 2026-11-25) | cited |
| E-8 | LEAN | 4 | README documents a Windows build (open `QuantConnect.Lean.sln` in Visual Studio); Python setup on Windows documented (python.org 3.11.11 MSI, `PYTHONNET_PYDLL`) with a caveat that the stubs package "can sometimes have issues" on Windows; CLI runs via Docker (WSL 2 backend noted) | https://github.com/QuantConnect/Lean, https://github.com/QuantConnect/Lean/tree/master/Algorithm.Python, https://www.quantconnect.com/docs/v2/lean-cli/key-concepts/getting-started (accessed 2026-11-25) | cited |
| E-8 | Custom on vectorbt | 4 | Only Windows evidence is the packaging classifier "Operating System :: OS Independent"; the installation page names no OS (it offers pip or Docker); our own loop and adapters would be plain Python | https://raw.githubusercontent.com/polakowo/vectorbt/master/pyproject.toml and https://vectorbt.dev/getting-started/installation/ (accessed 2026-11-25) | cited |
| E-9 | NautilusTrader | 3 | Python components subclass PyO3 base classes; generated `.pyi` stubs exist, but mypy is not addressed and `py.typed` is not mentioned; official adapters are Rust; requires Python 3.13–3.15 (PyPI wheels 3.13–3.14), while this repo pins 3.12 | https://nautilustrader.io/docs/latest/concepts/python/ and https://nautilustrader.io/docs/latest/getting_started/installation (accessed 2026-11-25) | cited |
| E-9 | LEAN | 2 | Engine is C# (GitHub language C#); Python algorithms run through QuantConnect's own pythonnet fork; Python 3.11.11 is the documented version (repo pins 3.12); brokerage plugins are C#, so any adapter we write or fix is C# | https://github.com/QuantConnect/Lean/tree/master/Algorithm.Python and https://api.github.com/repos/QuantConnect/Lean (accessed 2026-11-25) | cited |
| E-9 | Custom on vectorbt | 4 | Pure Python with Numba; supports Python 3.11–3.14 (includes our 3.12); no `py.typed` marker, so `mypy --strict` needs an override or our own stubs at the vectorbt boundary | https://raw.githubusercontent.com/polakowo/vectorbt/master/pyproject.toml (accessed 2026-11-25) | cited |
| E-10 | NautilusTrader | 4 | 17 PyPI releases in the last 12 months (1.222.0 on 2026-01-02 to 1.231.0 on 2026-08-02, then 2.0.0rc3–rc9, last 2026-11-10); last stable 1.231.0 on 2026-08-02, and `--pre` is required until 2.0.0; README: "breaking changes can occur between releases", bi-weekly target; repo pushed 2026-11-25, 130 open issues; no deprecation policy found | https://pypi.org/rss/project/nautilus_trader/releases.xml, https://github.com/nautechsystems/nautilus_trader, https://api.github.com/repos/nautechsystems/nautilus_trader (accessed 2026-11-25) | cited |
| E-10 | LEAN | 4 | Engine has no GitHub releases, only build-number tags; LEAN CLI had 11 PyPI releases in the last 12 months (last 1.0.234 on 2026-11-18); repo pushed 2026-11-24, 335 open issues; recent visible commits mostly from one maintainer plus a bot; company-backed; no deprecation policy found | https://pypi.org/rss/project/lean/releases.xml and https://api.github.com/repos/QuantConnect/Lean (accessed 2026-11-25) | cited |
| E-10 | Custom on vectorbt | 3 | 9 PyPI releases in the last 12 months (0.28.2 on 2025-12-12 to 1.2.1 on 2026-11-11); repo under the author's personal account, pushed 2026-11-11, 133 open issues; README calls it "the open-source community edition of VectorBT PRO" (the paid product); no deprecation policy found | https://pypi.org/rss/project/vectorbt/releases.xml, https://api.github.com/repos/polakowo/vectorbt, https://github.com/polakowo/vectorbt (accessed 2026-11-25) | cited |
| E-11 | NautilusTrader | 5 | LGPL-3.0-only (`license = "LGPL-3.0-only"`); no paid tier is needed to backtest or trade; LGPL obligations attach to distributing the library, which we do not do | https://github.com/nautechsystems/nautilus_trader and https://raw.githubusercontent.com/nautechsystems/nautilus_trader/develop/python/pyproject.toml (accessed 2026-11-25) | cited |
| E-11 | LEAN | 2 | Engine and plugins are Apache-2.0, but "To use the CLI, you must be a member in an organization on a paid tier" (the README's recommended path); pricing page shows live trading as cloud-only on Researcher/Team/Trading Firm and on-premises only on Institution; local corporate-action data is paid; self-hosted live trading from a source build is not documented | https://github.com/QuantConnect/Lean, https://www.quantconnect.com/docs/v2/lean-cli/key-concepts/getting-started, https://www.quantconnect.com/pricing/ (accessed 2026-11-25) | cited |
| E-11 | Custom on vectorbt | 4 | "Apache 2.0 with Commons Clause" (fair-code, not an OSI licence); the clause withholds only the right to "Sell" the software to third parties, so private household use and changes are allowed; README warns optional dependencies may carry more restrictive licences; vectorbt PRO (paid) is excluded from the candidate | https://github.com/polakowo/vectorbt/blob/master/LICENSE.md and https://github.com/polakowo/vectorbt (accessed 2026-11-25) | cited |

### Notes for A8 (facts, not a recommendation)

1. **E-1 interception is undocumented for both packaged engines.** NautilusTrader and LEAN each have engine-side order paths that emit market orders (Nautilus: `close_position`, `close_all_positions`, `market_exit`, `manage_stop`; LEAN: `liquidate`, margin-call orders, automatic delisting liquidation). Neither documents a way to put our own kernel in front of every one of them. Both E-1 cells are therefore `unverified`. The robustness check sets them to 0, which is a KO.
2. **Python version mismatch.** NautilusTrader v2 needs Python 3.13–3.15 (PyPI wheels 3.13–3.14). LEAN documents Python 3.11.11 through its own pythonnet fork. vectorbt supports 3.11–3.14. This repo pins `>=3.12,<3.13`.
3. **NautilusTrader is mid-rewrite.** The last stable release is 1.231.0 (2026-08-02). Since then there have only been 2.0.0 release candidates (rc9 on 2026-11-10), which need `--pre`. The README warns about breaking changes and says development wheels should not control real capital. A Phase 2 install-check would be testing a moving target.
4. **LEAN's local path costs money.** The CLI needs a paid-tier organization. The pricing page lists on-premises live trading only for Institution. Corporate-action data (Security Master) is paid. The CLI and plugin READMEs do describe `lean live deploy` locally, so QuantConnect's own pages are inconsistent here. A self-hosted live setup built from source is not documented.
5. **Footprint.** NautilusTrader ships every live adapter in its base wheel. vectorbt's `full` extra pulls in `alpaca-py`, `python-binance` and `ccxt`, so only its base install is free of order-capable code.
6. **Adapter coverage.** None of the three has a Robinhood brokerage adapter. NautilusTrader covers IBKR only. LEAN covers Alpaca, Schwab and IBKR, all through the paid CLI. Schwab via LEAN allows one authenticated account at a time.
7. **Vendor claims.** Every parity statement (E-2, E-6) is the vendor's own. Nautilus's Windows support is stated for Windows Server 2022+; Windows 11 is not named. vectorbt's only Windows evidence is an "OS Independent" classifier.

## 7. A7 Broker scores

Not started.

## 8. A10 Data-source scores

Not started.

## 9. A8 Totals, unverified share, robustness, sensitivity, recommendation and dissent

Not started.
