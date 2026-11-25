# Strategy encyclopedia

Every common family of retail-accessible strategy and system, with how it works, why it might work, what usually kills it, and whether it fits this desk. Written from general knowledge on 2026-11-24; **every "Evidence" cell must be re-verified against primary sources in Phase 1** before a strategy enters Phase 4 testing.

Fit key: **Core** = can sit in the long-term bucket · **Sleeve** = active sleeve candidate · **Watch** = study only · **No** = not viable for this desk (latency, cost, legal, or options-manual rule).

## 1. Trend following

| Strategy | Typical rules | Why it might work | Evidence and decay | Main failure mode | Fit |
|---|---|---|---|---|---|
| SMA crossover (e.g. 50/200 "golden/death cross") | Long when fast SMA > slow SMA; flat or defensive otherwise | Slow-moving capital and behavioral underreaction create persistent trends | [Brock, Lakonishok & LeBaron (1992)](https://doi.org/10.1111/j.1540-6261.1992.tb04681.x): moving-average and trading-range-break rules on the Dow 1897–1986 gave higher, less volatile returns after buy signals. Out-of-sample: [Sullivan, Timmermann & White (1999)](https://doi.org/10.1111/0022-1082.00163) found the best rule "not even statistically significant" in 1987–1996 and no rule beat the benchmark on S&P 500 futures. Drawdown-reduction claim unverified | Whipsaw in sideways markets; late exits and entries | Core overlay / Sleeve |
| Price vs long moving average (e.g. 10-month / 200-day filter) | Hold asset when price above its MA, else T-bills | Same; avoids the worst of bear markets historically | [Faber (2007)](https://doi.org/10.3905/jwm.2007.674809) (originator, J. Wealth Mgmt): 10-month SMA timing tested in-sample on US equities and out-of-sample on 20+ markets; abstract reports "equity-like returns with bond-like volatility and drawdown" since 1972. Post-publication results and the "lower return in bull markets" claim unverified (author's later SSRN update not reachable) | Whipsaw; tax drag from realized gains | Core overlay |
| Time-series momentum (12-month return sign) | Long assets with positive trailing return, scaled by volatility | Trend persistence across asset classes | [Moskowitz, Ooi & Pedersen (2012)](https://doi.org/10.1016/j.jfineco.2011.11.003): 1–12 month persistence in all 58 futures studied, best in extreme markets. Challenge: [Huang, Li, Wang & Zhou (2020)](https://doi.org/10.1016/j.jfineco.2019.08.004) find "little evidence of TSM" asset by asset, in- and out-of-sample, with profits matching a no-predictability sample-mean strategy. [Hurst, Ooi & Pedersen (2017)](https://doi.org/10.3905/jpm.2017.44.1.015) extend the test to 1880 and discuss higher cross-market correlations since the credit crisis. "Weaker 2010s" not quantified in the sources read | Sharp reversals; crowding | Sleeve (ETF-based) |
| Dual momentum | Pick the stronger of US vs international equity; go to bonds if both trail T-bills | Combines relative and absolute momentum | unverified (originator paper [Antonacci (2012)](https://doi.org/10.2139/ssrn.2042750) exists but SSRN blocks automated access, so its abstract was not read; no independent out-of-sample study read) | Few signals, long flat periods, concentration | Sleeve |
| Donchian / turtle channel breakout | Buy new N-day high, exit on M-day low | Captures large trends; famous turtle rules | [Szakmary, Shen & Sharma (2010)](https://doi.org/10.1016/j.jbankfin.2009.08.004): dual-MA and channel rules on 28 commodity futures over 48 years earned positive mean excess returns net of costs in at least 22 of 28 markets, robust to data-mining adjustments. Survey [Park & Irwin (2007)](https://doi.org/10.1111/j.1467-6419.2007.00519.x): early studies found profits in FX and futures "but not in stock markets"; modern studies profitable "at least until the early 1990s". Turtle rules themselves: no primary study | Many false breakouts; long losing streaks | Sleeve (ETFs) |
| Trend pullback | In an uptrend (price > 200-day), buy a dip to the 20/50-day MA or an RSI dip; exit on new high or trend break | Buy weakness within strength | unverified (practitioner setup; no primary study found) | Pullback becomes a trend reversal | Sleeve |
| ADX-filtered trend | Trade trend signals only when ADX shows a strong trend | Avoid choppy regimes | unverified (originator is Wilder's 1978 book, not online; no peer-reviewed test of ADX filtering found) | Lag; over-filtering | Watch |
| MACD signal-line cross | Long when MACD crosses above signal | Momentum change detection | [Chong & Ng (2008)](https://doi.org/10.1080/13504850600993598): MACD and RSI rules beat buy-and-hold "in most cases" on 60 years of the FT30; follow-up [Chong, Ng & Liew (2014)](https://doi.org/10.3390/jrfm7010001) found MACD(12,26,0) significant only in Milan and the TSX among five other OECD indices. Neither abstract addresses costs or data snooping; the "weak after costs" claim is not confirmed by these sources | Noise, whipsaw | Watch (as a feature) |
| Parabolic SAR / Supertrend / chandelier exits | Trailing-stop-based trend systems | Lock in trend gains | unverified (practitioner trailing-stop tools; Wilder's 1978 book originates Parabolic SAR, not online; no peer-reviewed test found) | Stopped out by normal volatility | Exit tool |

## 2. Momentum (cross-sectional) and rotation

| Strategy | Typical rules | Why it might work | Evidence and decay | Main failure mode | Fit |
|---|---|---|---|---|---|
| 12-1 stock momentum | Buy top decile by 12-month return excluding last month; rebalance monthly | Underreaction, herding | [Jegadeesh & Titman (1993)](https://doi.org/10.1111/j.1540-6261.1993.tb04702.x): winners-minus-losers earn significant returns over 3–12 month holds, partly reversing in years 2–3. Out-of-sample: [Jegadeesh & Titman (2001)](https://doi.org/10.1111/0022-1082.00342) found profits "continued in the 1990s". Crashes: [Daniel & Moskowitz (2016)](https://doi.org/10.1016/j.jfineco.2015.12.002) show crashes occur in panic states and coincide with market rebounds. General decay: [McLean & Pontiff (2016)](https://doi.org/10.1111/jofi.12365) find published predictors' returns 58% lower post-publication. "Weaker recently" for momentum specifically not quantified in the sources read | Momentum crashes at market rebounds; turnover | Sleeve (via ETF or small basket) |
| Sector / industry rotation | Hold the top 2–3 sector ETFs by 3–12 month momentum | Industry momentum | [Moskowitz & Grinblatt (1999)](https://doi.org/10.1111/0022-1082.00146): industry momentum "appear[s] highly profitable" and explains much of stock momentum, after controls for size, book-to-market and microstructure. The "modest after costs" claim is not addressed in the abstract (unverified); post-publication decay not measured in the sources read | Rotation lag; concentration | Sleeve |
| Asset-class rotation (GTAA) | Rotate among stocks, bonds, gold, REITs, cash by momentum/trend | Diversified trend capture | [Faber (2007)](https://doi.org/10.3905/jwm.2007.674809) (originator, J. Wealth Mgmt): trend timing applied to an S&P 500 / EAFE / GSCI / REIT / 10-year Treasury mix since 1972 gave "equity-like returns with bond-like volatility and drawdown". No independent post-publication study read; "variable returns" unverified | Long underperformance vs equities in bull runs | Core overlay / Sleeve |
| 52-week-high proximity | Buy stocks near 52-week highs | Anchoring bias | [George & Hwang (2004)](https://doi.org/10.1111/j.1540-6261.2004.00695.x): nearness to the 52-week high explains a large portion of momentum profits, dominates past returns as a forecaster, and does not reverse long-run. No post-publication study read; subject to the general decay in [McLean & Pontiff (2016)](https://doi.org/10.1111/jofi.12365) | Same crash risk as momentum | Watch |
| Earnings momentum / revisions | Buy stocks with rising analyst estimates | Slow information diffusion | [Chan, Jegadeesh & Lakonishok (1996)](https://doi.org/10.1111/j.1540-6261.1996.tb05222.x): past earnings surprises predict drifts independently of price momentum, and analysts' forecasts "respond sluggishly" to past news. No post-publication study read; data-cost claim not checked | Data access; crowding | Watch |

## 3. Mean reversion

| Strategy | Typical rules | Why it might work | Evidence and decay | Main failure mode | Fit |
|---|---|---|---|---|---|
| RSI(2) reversion on index ETFs | In an uptrend, buy when 2-day RSI < 10; sell when RSI > 70 or close > 5-day MA | Short-term overreaction in liquid indices | unverified (originator is Connors & Alvarez's 2008 book, not online; no peer-reviewed test found; decay claim unsourced) | Buying into a crash; small edge eaten by costs | Sleeve |
| RSI dip (14-period < 30) | Buy oversold, sell on recovery | Overreaction | [Chong, Ng & Liew (2014)](https://doi.org/10.3390/jrfm7010001): RSI(14, 30/70) was profitable on the Dow Jones Industrials and RSI(21,50) in Milan and the TSX (index-level tests; abstract silent on costs). The single-stock and trend-filter claims are unverified | "Oversold" keeps falling | Sleeve (with trend filter) |
| Bollinger Band reversion | Buy at lower band, sell at middle/upper | Volatility-scaled overreaction | [Lento, Gradojević & Wright (2007)](https://doi.org/10.1080/17446540701206576): after transaction costs Bollinger Bands were "consistently unable" to beat buy-and-hold; a contrarian version improved profitability. "Works in ranges, fails in trends" unverified | Band walks in strong trends | Sleeve |
| Internal bar strength / close-near-low | Buy index ETF closing near day's low | Short-term reversal | [Pandey & Joshi (2023)](https://arxiv.org/abs/2306.12434) (non-peer-reviewed arXiv report): IBS mean-reversion on a basket of country ETFs over 10 years was "a useful technical indicator". No peer-reviewed or out-of-sample study found | Same as above | Watch |
| Short-term reversal (1-week/1-month losers) | Buy last week's/month's losers | Liquidity provision | [Jegadeesh (1990)](https://doi.org/10.1111/j.1540-6261.1990.tb05110.x) (monthly) and [Lehmann (1990)](https://doi.org/10.2307/2937816) (weekly) document reversals; Lehmann reports profits persisting after bid-ask and plausible costs. Later: [Avramov, Chordia & Goyal (2006)](https://doi.org/10.1111/j.1540-6261.2006.01060.x) find reversal profits concentrated in illiquid stocks and "smaller than the likely transactions costs". "Captured by fast players" unverified | Costs, news-driven drops that don't revert | Watch |
| Gap fade | Fade overnight gaps that are not news-driven | Opening overreaction | unverified (no primary study found) | Gaps with real news keep going | No (open-auction risk, R-24) |
| VWAP reversion intraday | Trade back toward VWAP | Intraday overextension | [Berkowitz, Logue & Noser (1988)](https://doi.org/10.1111/j.1540-6261.1988.tb02591.x) introduced the day's VWAP as a measure of execution cost on NYSE trades, which supports its role as an execution benchmark. No primary study of VWAP reversion as an alpha source found (unverified) | HFT competition | No |

## 4. Breakout and volatility expansion

| Strategy | Typical rules | Why it might work | Evidence and decay | Main failure mode | Fit |
|---|---|---|---|---|---|
| Range breakout (N-day high) | Buy close above recent range high with volume | New information, trend start | Mixed; most breakouts fail | False breakouts | Sleeve (with filters) |
| Opening range breakout | Trade break of first 15–30 min range | Intraday momentum | Some practitioner evidence; sensitive to costs | Chop; slippage | Watch (day trading, R-36) |
| Volatility contraction (squeeze) | Enter when Bollinger width / ATR hits multi-month low and then expands | Calm before moves | Practitioner | Direction ambiguity | Watch |
| Cup-and-handle / chart patterns | Pattern recognition | Behavioral | Weak, subjective evidence | Pattern ambiguity, overfitting | No (unless rules are fully mechanical) |

## 5. Volatility, risk-based and allocation systems

| Strategy | Typical rules | Why it might work | Evidence and decay | Main failure mode | Fit |
|---|---|---|---|---|---|
| Strategic index allocation + band rebalancing | Fixed weights; rebalance when drift exceeds bands | Low cost, diversification, disciplined buy-low/sell-high | Strongest long-run evidence of anything here | Behavior (abandoning it) | Core (the fee replacement) |
| Volatility targeting | Scale exposure inversely to recent volatility | Volatility clusters; risk-adjusted returns improve | Moreira-Muir and follow-ups | De-risking just before rebounds | Core overlay / Sleeve |
| Risk parity | Weight assets by inverse volatility/risk contribution | Balanced risk | Institutional; often uses leverage | Rate shocks hit bonds and stocks together (2022) | Watch (no leverage) |
| Minimum variance / low volatility | Hold lowest-volatility stocks/ETF | Low-vol anomaly | Documented; available as ETFs | Rate sensitivity, crowding | Core tilt |
| CPPI / drawdown control | Exposure = multiple × (value − floor) | Guarantees a floor in theory | Practitioner | Gap risk; locks into cash after a drop | Watch |
| Kelly / fractional Kelly sizing | Size by edge/variance | Growth-optimal | Theory; full Kelly too aggressive with estimation error | Overbetting on bad estimates | Sizing tool (fractional only) |

## 6. Factor and fundamental

| Strategy | Typical rules | Why it might work | Evidence and decay | Main failure mode | Fit |
|---|---|---|---|---|---|
| Value (cheap on P/B, P/E, EV/EBIT) | Buy cheapest quintile | Risk premium / behavioral | Long history; very weak 2007–2020 | Value traps; long droughts | Core tilt via ETF |
| Quality / profitability | Buy high ROE, stable margins, low leverage | Underpriced quality | Novy-Marx and others | Expensive in some regimes | Core tilt via ETF |
| Multi-factor (value + momentum + quality) | Composite score | Diversified factor premia | Strong academic base; decays with crowding | Factor drawdowns | Core tilt / Sleeve |
| Shareholder yield / dividend growth | Buy high payout + buybacks | Capital discipline | Practitioner | Sector concentration | Core tilt |
| Small-cap premium | Overweight small caps | Size premium | Weakened since discovery | Long droughts | Watch |

## 7. Event-driven

| Strategy | Typical rules | Why it might work | Evidence and decay | Main failure mode | Fit |
|---|---|---|---|---|---|
| Post-earnings announcement drift | Buy positive surprises, hold weeks | Slow information diffusion | Bernard-Thomas; much weaker now | Quick reversal; crowding | Sleeve (LLM can read releases) |
| Earnings-call / filing NLP signals | Score tone/changes in 8-K, 10-Q, calls | Information in text | Research literature; LLMs now widespread | Look-ahead in tests; crowding | Sleeve, forward-test only (R-31) |
| Index additions/deletions | Trade around index rebalances | Forced buying/selling | Mostly arbitraged away | Front-running is crowded | Watch |
| Insider buying (Form 4) | Follow clusters of open-market insider buys | Insiders know more | Documented modest effect; free data from EDGAR | Small, slow edge | Sleeve |
| Buyback announcements | Buy on new authorizations | Signaling | Documented, decayed | Announcements not executed | Watch |
| Merger arbitrage | Buy target after announced deal | Deal-completion premium | Institutional; tail risk if deal breaks | Deal breaks | Watch |
| 13F / "guru" following | Copy large funds' holdings | Skill transfer | 45-day lag erodes value | Stale data | Watch |
| Analyst upgrades / news sentiment | Trade on rating changes or headlines | Information flow | Fast players act first | Latency | Watch (alerts only) |

## 8. Relative value and statistical arbitrage

| Strategy | Typical rules | Why it might work | Evidence and decay | Main failure mode | Fit |
|---|---|---|---|---|---|
| Pairs trading (distance / cointegration) | Long the laggard, short the leader when spread widens | Mean reversion of related assets | Gatev et al.; returns fell after 2000s | Pairs break; needs shorting (off) | Watch (needs shorting) |
| ETF vs basket / ADR arbitrage | Trade price vs fair value of components | Arbitrage | Done by APs and HFTs in microseconds | Latency, conversion access | No |
| Closed-end fund discount reversion | Buy funds at unusually wide discounts | Discount mean reversion | Documented niche | Discounts can widen for years | Watch |
| Market making / pennying (the ETC winner) | Quote both sides near fair value | Capture spread | Real only with co-location and rebates | Adverse selection by faster players | No |

## 9. Seasonality and calendar

| Strategy | Typical rules | Why it might work | Evidence and decay | Main failure mode | Fit |
|---|---|---|---|---|---|
| Turn-of-month | Hold index from last trading day to 3rd of next month | Fund flows | Documented, weaker | Small edge | Watch |
| Pre-holiday / pre-FOMC drift | Hold index into holidays or FOMC days | Flows / risk premium | Documented then decayed | Small, noisy | Watch |
| "Sell in May" / Halloween | Hold equities Nov–Apr | Seasonality | Mixed; data-mined risk | Missing summer rallies | Watch |
| Tax-loss selling / January effect | Buy December losers | Tax-motivated selling | Mostly faded | Small | Watch |

## 10. Income and options-based (manual only by owner decision)

| Strategy | Typical rules | Why it might work | Evidence and decay | Main failure mode | Fit |
|---|---|---|---|---|---|
| Covered calls | Sell calls against held stock | Volatility risk premium | Documented; caps upside | Big rallies called away; full downside | No (manual future phase) |
| Cash-secured puts / wheel | Sell puts, take assignment, then sell calls | Same | Same | Assignment in crashes | No (manual future phase) |
| Protective puts / collars | Buy puts; finance with calls | Insurance | Cost drag | Expensive when needed most | No (manual future phase) |
| Iron condors, spreads, 0DTE | Sell premium in ranges | Premium harvesting | Many retail losses | Tail events | No |

## 11. Exits and risk management (apply to every strategy)

| Tool | How it works | Notes for this desk |
|---|---|---|
| Fixed stop-loss | Exit at X% below entry | Use stop-limit with collar, never stop-market (R-25, R-26) |
| ATR / volatility stop | Exit at k × ATR below entry or high | Adapts to volatility; preferred default |
| Trailing stop | Stop follows price up | Locks gains; can be whipsawed |
| Time stop | Exit after N days if thesis not playing out | Reduces dead money; easy to test |
| Thesis invalidation | Exit when the proposal's stated invalidation level or event occurs | Required field in every proposal (FR-4) |
| Take-profit target | Exit at R multiple | Pair with trailing logic |
| Portfolio stop / drawdown breaker | Cut exposure at portfolio drawdown thresholds | Risk-mode state machine (FR-12) |
| Volatility-scaled sizing | Size so each position risks a fixed % of capital | Deterministic sizing (R-30) |

## 12. What the Phase 4 test plan needs for every candidate

1. Pre-registration (R-17): hypothesis, economic rationale, universe, parameters, benchmark, kill criteria.
2. Point-in-time data, survivorship-free universe, realistic costs and slippage.
3. Walk-forward test, then one untouched holdout check (R-18).
4. Trial count and deflated Sharpe.
5. Regime breakdown (bull, bear, sideways, high-vol) and worst drawdown.
6. Capacity and turnover; after-tax result vs the core benchmark.
7. Forward-logged paper results before any live money.

## Suggested first candidates for Phase 4 (owner decides)

1. Core: strategic allocation with band rebalancing + tax-loss harvesting.
2. Core overlay: 200-day / 10-month trend filter and volatility targeting.
3. Sleeve A: sector or asset-class rotation (monthly, ETF-based).
4. Sleeve B: trend-pullback / RSI(2) reversion on index ETFs, uptrend only.
5. Experimental: LLM-read earnings/filing signals, forward-logged only.
