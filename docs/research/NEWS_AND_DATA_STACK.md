# News and data stack (free and official sources only)

Owner decision: no X/Grok and no paid news subscriptions. Goal: know why a held, adjacent, or watched stock is moving within about a minute, from sources we are allowed to use automatically.

## Sources

| Source | What it gives | Cost / limits | Status |
|---|---|---|---|
| Alpaca News API (Benzinga) | Real-time headlines over WebSocket and history back to 2015 for stocks and crypto ([Alpaca real-time news](https://docs.alpaca.markets/us/docs/streaming-real-time-news); [Alpaca launch post](https://alpaca.markets/blog/introducing-news-api-for-real-time-fiancial-news/)) | Comes with the Alpaca account; the free market-data plan limits real-time equity prices to the IEX exchange ([Alpaca](https://docs.alpaca.markets/us/docs/about-market-data-api.md)). At launch the news API was free with rate limits of 200 calls/min on free plans ([Alpaca launch post, 2022](https://alpaca.markets/blog/introducing-news-api-for-real-time-fiancial-news/)) | Primary news feed. Re-verify current terms in Phase 1 |
| SEC EDGAR | Every 8-K, 10-Q, 10-K, Form 4 as filed; free Atom feed of latest filings by form type ([SEC developer resources](https://www.sec.gov/about/developer-resources); [SEC RSS feeds](https://www.sec.gov/about/secrss.shtml)) | Free; max 10 requests/second ([SEC](https://www.sec.gov/os/accessing-edgar-data)); descriptive User-Agent with contact email required | Primary source of truth for company events |
| Exchange trade-halt feeds (e.g. Nasdaq Trader halts RSS) | Halts and resumptions with reason codes: RSS 2.0 at `https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts`, one item per halt with `ndaq:` fields `HaltDate`, `HaltTime` (ET), `IssueSymbol`, `IssueName`, `Market`, `ReasonCode`, `PauseThresholdPrice`, `ResumptionDate`, `ResumptionQuoteTime`, `ResumptionTradeTime`; items seen for NASDAQ, NYSE and AMEX markets ([Nasdaq Trader halts](https://www.nasdaqtrader.com/Trader.aspx?id=TradeHalts)) | Free, no login; site terms allow personal, non-commercial use only and bar redistribution ([Nasdaq Trader disclaimer](https://www.nasdaqtrader.com/Trader.aspx?id=CopyDisclaimMain)); no published polling limit found | Confirmed 2026-11-25 (feed served) |
| Company investor-relations RSS / press-release wires | Earnings releases, guidance, deals | Free where offered, but not every company publishes one: Apple's newsroom Atom feed (`https://www.apple.com/newsroom/rss-feed.rss`) carries its earnings press releases ([Apple Newsroom feed](https://www.apple.com/newsroom/rss-feed.rss)); Microsoft's investor page offers email alerts, not RSS ([Microsoft Investor Relations](https://www.microsoft.com/en-us/investor)) | Corrected 2026-11-25: availability checked per company when a symbol is added; EDGAR 8-K is the fallback |
| FRED (St. Louis Fed) | Macro series, credit spreads, yields | Free ("access and use FRED at no cost", [FRED legal](https://fred.stlouisfed.org/legal/)); every API request needs an API key from a FRED user account ([FRED API keys](https://fred.stlouisfed.org/docs/api/api_key.html)). No numeric rate limit is published; the Bank "may impose limits" and blocks invalid keys. Third-party series are for personal use only without the owner's permission; apps must show "This product uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis." ([FRED API terms](https://fred.stlouisfed.org/docs/api/terms_of_use.html)) | Confirmed 2026-11-25 |
| Economic calendars (BLS, BEA, Fed) | CPI, jobs, GDP, FOMC dates: BLS release schedule with an iCalendar file `https://www.bls.gov/schedule/news_release/bls.ics` ([BLS schedule](https://www.bls.gov/schedule/news_release/)); BEA release schedule with an ICS subscription and a JSON file `https://apps.bea.gov/API/signup/release_dates.json` ([BEA schedule](https://www.bea.gov/news/schedule)); FOMC meeting dates (HTML; next year's dates tentative until confirmed) ([Federal Reserve FOMC calendar](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)) | Free, official | Confirmed 2026-11-25 |
| Google News RSS | Broad headline discovery with links | Free, but check terms of use before automated polling; never scrape Google Search pages | Fallback / discovery only |
| Alpaca market data (IEX) | Real-time prices for triggers | Free plan | Paper phase; consider paid consolidated feed only if intraday precision matters |

## Watch universe
1. **Held** symbols.
2. **Adjacent** symbols: same-sector peers, key suppliers/customers, the sector ETF, and ETFs with large weights in the holding (built once per holding, reviewed monthly).
3. **Watchlist** symbols with owner-set buy zones.
4. **Market**: major index ETFs, volatility gauge, rates, credit spreads.

## "Why is it moving?" pipeline (FR-9)
1. **Trigger** (deterministic): price crosses a buy zone or alert level, a move exceeds k × typical daily volatility, a halt, or a new 8-K/Form 4 for a watched symbol.
2. **Gather** (≤ 30 s): last 24h headlines from Alpaca News for the symbol and its adjacent set; new EDGAR filings; halt status; today's macro calendar; sector ETF move (is it the stock or the market?).
3. **Summarize** (LLM, ≤ 30 s): 3–5 bullet brief, each with a source link and timestamp; classify the cause as company / sector / market / unknown. External text is data, never instructions (rule 6).
4. **Act**: push to the owner. If a buy-zone trigger meets every Tier A condition, the kernel may act; otherwise it raises a Tier B approval request with the brief attached. Rumors without a primary source never trigger a trade.

## Honest latency note
Benzinga-class wires and EDGAR are near real time for company news. X can be earlier for rumors and breaking events, but that speed comes with misinformation and manipulation; this desk deliberately does not trade on unconfirmed social posts.

## Compliance notes
- Respect each source's terms and rate limits; cache locally; identify ourselves in User-Agent where required.
- Market data and news are for personal use; never redistribute.
