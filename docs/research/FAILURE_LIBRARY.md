# Failure library

Learn from everyone who failed before us. Each entry: what happened, the root cause, and the control it becomes in this system (rule IDs R-13 onward extend the master brief's rules 1–12). Entries first written from general knowledge (F-05, F-06, F-10, F-11, F-12, F-15, F-17) were re-checked against primary sources in Phase 1; each check is recorded in `verification_log.md`. Add a row every time we find a new failure, ours or anyone's.

## A. Engineering and operations failures

### F-01 Knight Capital (1 Aug 2012): a deployment error ends a firm in 45 minutes
- **What happened:** In the first 45 minutes after the open, Knight's router sent more than 4 million orders while trying to fill 212 customer orders ([SEC press release](https://www.sec.gov/news/press-release/2013-222)). Loss of about $460 million; the firm had to be sold.
- **Root cause:** New code reused a flag that once activated a retired function ("Power Peg") still present on one of eight servers; one server was missed in deployment. The system sent 97 automated warning emails before the open that nobody acted on. The SEC cited missing controls for code deployment and testing, no second-person review of deployments, and no control to halt a system in response to its own aberrant behavior ([SEC order, Release No. 34-70694, 16 Oct 2013](https://www.sec.gov/litigation/admin/2013/34-70694.pdf), ¶¶13–15, 19, 21, 26).
- **Controls:**
  - **R-13** Every deploy: CI green, owner review of the diff, identical artifact on every host, startup self-check that reports version + config hash; the bot refuses to trade if they differ from the approved release.
  - **R-14** No dead code or repurposed flags in the trading path; feature flags are deleted when retired.
  - **R-15** Self-halt on aberrant behavior: order-rate ceiling, orders-vs-intended-quantity ratio, fills exceeding target, position exceeding target. Any breach cancels entries and pages the owner.
  - **R-16** Alerts page a human (push notification), never only email; an unacknowledged critical alert blocks the next session's trading.

### F-02 Quantopian (2016 study, fund shut 2020): backtests don't predict live results
- **What happened:** In a study of 888 strategies with at least six months of out-of-sample data, backtest metrics like the Sharpe ratio had little value in predicting out-of-sample performance (R² < 0.025) ([Quantpedia summary](https://quantpedia.com/quantopians-academic-paper-about-in-vs-out-of-sample-performance-of-trading-alg/)). The more backtest days a developer used, the larger the gap between in-sample and out-of-sample performance ([CXO Advisory](https://www.cxoadvisory.com/?p=28573)). Commentators trace Quantopian's later fund closure to this same problem ([discussion](https://discussion.fool.com/t/why-quantopian-shut-down/88667)).
- **Root cause:** Overfitting through repeated tuning; selecting the best of many trials.
- **Controls:**
  - **R-17** Pre-register every strategy (hypothesis, parameters, universe, benchmark, kill criteria) before testing; log every variant tried. Count trials and deflate the Sharpe ratio for them.
  - **R-18** Hold out the most recent data untouched until a single final check; walk-forward only after that.
  - **R-19** Prefer simple strategies with few parameters and an economic reason to work.

### F-03 Published edges decay
- **What happened:** Research on anomaly decay finds that the main predictor of out-of-sample Sharpe decay is the publication date, with more recently published factors decaying more ([arXiv 2105.01380](https://arxiv.org/pdf/2105.01380)).
- **Control:** **R-20** Expect a published strategy to be weaker than its paper; size it accordingly and monitor rolling performance against its pre-registered kill criteria.

### F-04 3Commas (2022): stolen API keys used to dump accounts into illiquid assets
- **What happened:** Attackers used users' exchange API keys to sell assets into a low-cap, low-liquidity coin; one user reported losing $200,000 ([CoinDesk via Yahoo](https://malaysia.news.yahoo.com/alameda-backed-crypto-trading-firm-131500898.html)). About 100,000 keys leaked, and the company first blamed users before confirming the leak ([Decrypt](https://decrypt.co/118094/after-repeated-denials-3commas-admits-it-was-source-for-earlier-hacks/)). Some leaked keys were more than three years old ([ForkLog/HAPI](https://forklog.com/en/api-key-leaks-and-exchange-inaction-a-hapi-analysis-of-the-3commas-incident/)).
- **Controls:** **R-21** Keys never leave our own secrets manager (no third-party bot platforms holding keys); rotate every 90 days; IP allowlist where offered. **R-22** Symbol allowlist, liquidity floor (min ADV and max spread), price collars, and % of ADV caps in the kernel, so even a stolen key path through our code cannot buy junk.

### F-05 Broker outages and restrictions at the worst moment
- **What happened:** Retail brokers have had outages on high-volume days (e.g. Robinhood, March 2020) and imposed buying restrictions on specific stocks (Jan 2021). On 2–3 March 2020, "during a time of historic market volatility", Robinhood's website and apps shut down: all customers (12.5 million accounts) were unable to enter, modify or cancel orders, and a second outage on 9 March left order entry down for 45 minutes ([FINRA AWC No. 2020066971201, June 2021](https://www.finra.org/sites/default/files/2021-06/robinhood-financial-awc-063021.pdf)). On 28 January 2021 one retail broker-dealer restricted all new customer purchases in eight stocks including GME and AMC (position closing only), then switched to position limits on more than 50 names; affected brokers said the restrictions were a reaction to NSCC margin calls and capital charges ([SEC Staff Report on Equity and Options Market Structure Conditions in Early 2021, 14 Oct 2021](https://www.sec.gov/files/staff-report-equity-options-market-struction-conditions-early-2021.pdf), §3.6).
- **Controls:** **R-23** Assume the broker can be unavailable or restrict a symbol; protection rests at the broker, the kernel treats API errors as "halt entries," and a second broker account is documented as manual fallback.

### F-06 Flash Crash (6 May 2010)
- **What happened:** Prices of many stocks and ETFs briefly collapsed, some trading at pennies, then recovered. Major indices, already down more than 4%, fell a further 5–6% in minutes and rebounded almost as quickly; between 2:40 and 3:00 p.m. more than 20,000 trades in over 300 securities, including many ETFs, executed 60% or more away from their 2:40 p.m. prices, many at a penny or less, and were later broken under clearly-erroneous rules ([CFTC and SEC staff report, 30 Sep 2010](https://www.sec.gov/news/studies/2010/marketevents-report.pdf), Executive Summary).
- **Control:** see F-07; **R-24** no trading in the first and last 5 minutes of the session by default, and none during LULD halts or market-wide circuit breakers.

### F-07 24 Aug 2015: stop orders turned into market orders and filled far below value
- **What happened:** Stop-loss orders become market orders when triggered; on 24 August retail investors' standing stop-loss orders were converted into market orders that often filled at prices markedly lower than the stop price ([BlackRock ViewPoint, archived copy](https://web.archive.org/web/20250607032623/https://www.blackrock.com/corporate/literature/whitepaper/viewpoint-us-equity-market-structure-october-2015.pdf), p. 5). BlackRock found that excessive use of market and stop-loss orders seeking liquidity at any price inflamed the selloff, with market orders running at four times a normal day ([BlackRock ViewPoint, "US Equity Market Structure: Lessons from August 24", Oct 2015, archived copy](https://web.archive.org/web/20250607032623/https://www.blackrock.com/corporate/literature/whitepaper/viewpoint-us-equity-market-structure-october-2015.pdf), pp. 2–3). Many fills were far from the ETFs' implied value and were not broken: IVV and QQQ traded at substantial discounts to their NAV in the first minutes after the open ([SEC Division of Trading and Markets staff, "Research Note: Equity Market Volatility on August 24, 2015", Dec 2015](https://www.sec.gov/marketstructure/research/equity_market_volatility.pdf), p. 5), and only a few trades were cancelled, often because the window to request a review closed before investors knew of their fills ([BlackRock ViewPoint, archived copy](https://web.archive.org/web/20250607032623/https://www.blackrock.com/corporate/literature/whitepaper/viewpoint-us-equity-market-structure-october-2015.pdf), p. 12).
- **Controls:** **R-25** No market orders anywhere in the system; marketable limit orders with a collar instead. **R-26** Protective stops are stop-limit orders with a configured collar where the broker supports them, plus a deterministic monitor that re-quotes if the limit is skipped; a gap below the limit is accepted risk that hedges, not stops, address. **R-27** ETF trades check price vs indicative value/NAV and halt on large deviation.

## B. Strategy and model failures

### F-08 LLM traders in public live tests (2025–2026)
- **What happened:** Across Alpha Arena contests, a model finished in profit only 6 of 32 times and the combined portfolio lost about a third ([Business Standard](https://www.business-standard.com/markets/news/ai-bots-auditioning-for-wall-street-trading-are-mostly-losing-money-126050701793_1.html)). Observers note the models trade too much and decide very differently from identical instructions ([ThinkAdvisor](https://www.thinkadvisor.com/amp/2026/05/06/why-ai-bots-arent-ready-to-replace-your-fund-manager/)).
- **Root causes:** Overtrading; no stable risk framework; non-deterministic decisions; narrative reasoning without an edge.
- **Controls:** **R-28** Turnover and trade-count caps per strategy and per day. **R-29** Consistency check: an LLM-originated proposal is re-asked N times (or by two models); act only when the answers agree on direction and the kernel approves. **R-30** LLMs never size positions; sizing is a deterministic function of volatility and limits.

### F-09 Parametric look-ahead bias in LLM backtests
- **What happened:** A model trained on later data "remembers" outcomes; uncorrected long-horizon LLM backtests are systematically misleading ([arXiv 2605.24564](https://arxiv.org/abs/2605.24564)).
- **Control:** **R-31** LLM signals are judged only on decisions logged with timestamps before outcomes exist (forward ledger); historical tests only for rule-based strategies with point-in-time data.

### F-10 Leverage and concentration: LTCM (1998), Archegos (2021)
- **What happened:** Highly levered, concentrated positions turned adverse moves into near-total losses and forced rescues or unwinds. LTCM ran balance-sheet leverage of more than 25-to-1 (over $125 billion of assets on 31 August 1998), some of its futures positions exceeded 5% of open interest, and its 1998 equity losses passed 50% by the end of August; 14 firms then put in about $3.6 billion of new equity because a liquidation of its positions "would have been disorderly" ([President's Working Group on Financial Markets, *Hedge Funds, Leverage, and the Lessons of Long-Term Capital Management*, April 1999](https://www.cftc.gov/sites/default/files/tm/tmhedgefundreport.htm)). Archegos used margined total return swaps to grow from $10 billion of exposure in March 2020 to $160 billion at its peak in March 2021; price declines in its most concentrated holdings triggered margin calls it could not meet, its counterparties sent default notices and unwound its positions, and they were left with billions in credit losses ([SEC press release 2022-70, 27 Apr 2022](https://www.sec.gov/newsroom/press-releases/2022-70); [SEC complaint, S.D.N.Y. No. 1:22-cv-03402](https://www.sec.gov/files/litigation/complaints/2022/comp-pr2022-70.pdf), ¶¶7, 162–166).
- **Controls:** **R-32** No margin, no shorting (unless a signed config change); single-position and sector caps; correlated-exposure cap across strategies.

### F-11 "Volmageddon" (5 Feb 2018): an inverse-volatility ETP lost almost all its value in a day
- **What happened:** On 5 February 2018 the intraday indicative value of Credit Suisse's XIV ETN (VelocityShares Daily Inverse VIX Short Term ETN) fell to 20% or less of the prior day's closing indicative value ($108.3681 on 2 February), an acceleration event; on 6 February the issuer announced it would accelerate (redeem) the notes ([Credit Suisse AG Form 6-K, exhibit 99.1, 6 Feb 2018](https://www.sec.gov/Archives/edgar/data/1053092/000095010318001572/dp86358_ex9901.htm)). The Second Circuit, reciting the investors' complaint, describes the value falling to just over $4 by 4:15 p.m., "a drop of more than 96 percent from the prior day's closing indicative value" ([*Set Capital LLC v. Credit Suisse Group AG*, No. 19-3466 (2d Cir. 27 Apr 2021)](https://www.cohenmilstein.com/wp-content/uploads/2023/07/Credit-Suisse-2d-Cir-Decision.pdf), slip op. 11–12).
- **Control:** **R-33** Instrument blocklist: leveraged/inverse ETPs, volatility ETPs, OTC/penny stocks, recent IPOs/SPACs under N days, anything with ADV below the floor.

### F-12 Momentum crashes (e.g. spring 2009)
- **What happened:** Momentum strategies suffered sharp losses when beaten-down stocks rebounded violently. From March to May 2009 the past-loser decile rose 163% while the past-winner decile gained only 8% (the market rose 26%); March and April 2009 were the 7th and 4th worst momentum months of 1927–2013. Such crashes come in "panic" states, after market declines and when volatility is high, and are driven mostly by the loser (short) side "crashing up" ([Daniel & Moskowitz, "Momentum Crashes", NBER Working Paper 20439](https://www.nber.org/papers/w20439); published in *Journal of Financial Economics* 122(2): 221–247, 2016, [DOI 10.1016/j.jfineco.2015.12.002](https://doi.org/10.1016/j.jfineco.2015.12.002)).
- **Control:** **R-34** Strategy-level drawdown kill switch and volatility scaling for momentum sleeves.

### F-13 Strategy crowding and regime shifts (ETC 2023 team lost ~$10,000 per round after a regime shift)
- **What happened:** A Jane Street ETC team's strategy lost about $10,000 per round when the market shifted mid-event ([manoflearning repo](https://github.com/manoflearning/jane-street-etc)).
- **Control:** **R-35** Each strategy declares the regime it expects; the regime monitor disables strategies whose regime is absent.

## C. Human and behavioral failures

### F-14 Day traders overwhelmingly lose
- **What happened:** Of individuals who began day trading Brazilian equity futures in 2013–2015 and persisted for at least 300 days, 97% lost money and only 0.4% earned more than a bank teller (US$54 a day) ([Chague, De-Losso & Giovannetti, "Day Trading for a Living?", SSRN 3423101](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101)); the authors find no evidence of learning by day trading ([working paper, FGV EESP TD 525, 2020](https://repositorioslatinoamericanos.uchile.cl/handle/2250/5040005)).
- **Control:** **R-36** Day trading is never the core; it lives only in the capped sleeve, must beat the index after costs in forward tests, and is off by default.

### F-15 Overtrading and the disposition effect
- **What happened:** Individual investors who trade most earn least after costs; people sell winners too early and hold losers too long. Of 66,465 households at a large discount broker in 1991–1996, those that traded most earned 11.4% a year while the market returned 17.9%; gross returns of frequent and infrequent traders barely differed, but net of spreads and commissions frequent traders earned 11.4% against 18.5% for infrequent traders ([Barber & Odean, "Trading Is Hazardous to Your Wealth", *Journal of Finance* 55(2): 773–806, 2000, DOI 10.1111/0022-1082.00226](https://doi.org/10.1111/0022-1082.00226); [author copy](https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/individual_investor_performance_final.pdf)). In trading records for 10,000 discount-brokerage accounts, investors showed "a strong preference for realizing winners rather than losers", which later returns did not justify ([Odean, "Are Investors Reluctant to Realize Their Losses?", *Journal of Finance* 53(5): 1775–1798, 1998, DOI 10.1111/0022-1082.00072](https://doi.org/10.1111/0022-1082.00072); [author copy](https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/areinvestorsreluctant.pdf)).
- **Control:** **R-37** Every trade carries its exit rules at entry; no discretionary override of a strategy mid-trade except the kill switch; monthly review of turnover vs results.

### F-16 Panic changes to rules after a bad day
- **Control:** **R-38** 24-hour cooling-off on any risk-up change (already rule 2); a written post-mortem before changing any strategy after a loss.

## D. Counterparty, tax and legal failures

### F-17 Custody failures (e.g. FTX, Nov 2022)
- **What happened:** The SEC alleges a years-long fraud (from at least May 2019) in which billions of dollars of FTX customer funds were diverted to its affiliate Alameda Research and used for venture investments and loans to executives. On 8 November 2022 FTX paused all customer withdrawals, and on 11 November 2022 FTX, Alameda and affiliates filed for Chapter 11 in Delaware (Case No. 22-11068) ([SEC press release 2022-219, 13 Dec 2022](https://www.sec.gov/newsroom/press-releases/2022-219); [SEC complaint](https://www.sec.gov/files/litigation/complaints/2022/comp-pr2022-219.pdf), ¶¶1, 79). SIPC protection (up to $500,000 including $250,000 cash) covers missing customer cash and securities at a failed member broker, not market losses and not crypto assets that are not securities ([SIPC](https://www.sipc.org/for-investors/what-sipc-protects)).
- **Control:** **R-39** Use only regulated, SIPC-member brokers for securities; no crypto custody in this phase.

### F-18 Wash-sale and tax surprises
- **Control:** R-12 in the master brief (household-wide tracking, reserve = tax with minus tax without, estimated payments).

### F-19 Trading on inside information or conflicts
- **Control:** **R-40** Restricted list is owner-maintained and starts empty; the kernel blocks every symbol on it (COMPLIANCE.md C-3).

## Open questions for Phase 1
- Find post-mortems of retail algo traders (blogs, r/algotrading) and add the top recurring causes.
- Find documented incidents at Alpaca, Schwab and Robinhood APIs (outages, order bugs) and add them.
- Verify every entry written from general knowledge against a primary source (done in Phase 1 for F-05, F-06, F-10, F-11, F-12, F-15, F-17; see `verification_log.md`).
