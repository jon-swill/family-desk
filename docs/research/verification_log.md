# Verification log (Phase 1, D1)

One row per original verify marker (11 in total: 7 in FAILURE_LIBRARY, 4 in NEWS_AND_DATA_STACK), one row per fixed or dead link, and one row per verified Alpaca/EDGAR term (G-5). Verdicts: `confirmed` (claim unchanged, citation added), `corrected` (wording fixed; any change in meaning goes through `failure_library_proposals.md` for owner approval), `unverifiable` (no primary source found; reason given). Accessed dates are ISO dates. Each section is owned by one Track A task; rows are appended at the end of their own section only.

## 1. FAILURE_LIBRARY verify markers (A1)

| # | Entry | Claim | Original text | Primary source URL | Accessed | Verdict | Change made |
|---|---|---|---|---|---|---|---|

## 2. FAILURE_LIBRARY and proposals link fixes (A1)

| # | File · location | Original link | Problem | Replacement primary source | Accessed | Verdict | Change made |
|---|---|---|---|---|---|---|---|

## 3. NEWS_AND_DATA_STACK verify markers and links (A2)

| # | Row | Claim | Original text | Primary source URL | Accessed | Verdict | Change made |
|---|---|---|---|---|---|---|---|
| 3.1 | SEC EDGAR · What it gives (link) | Free Atom feed of latest filings by form type | "free Atom feed of latest filings by form type ([dev guide](https://dev.to/nexgendata/sec-8-k-filings-api-build-a-material-events-tracker-2026-guide-2ll3))" | https://www.sec.gov/about/developer-resources (Latest Filings RSS, example `browse-edgar?action=getcurrent&type=10-k&...&count=40&output=atom`); https://www.sec.gov/about/secrss.shtml ("you can subscribe to all filings, or filter by company, CIK, or Form Type") | 2026-11-25 | confirmed (non-primary-only link replaced) | dev.to citation replaced with the two SEC pages; claim unchanged |
| 3.2 | Alpaca News API · What it gives (link) | Real-time headlines over WebSocket and history back to 2015 for stocks and crypto | "([Alpaca](https://alpaca.markets/docs/news-api))" | https://docs.alpaca.markets/us/docs/streaming-real-time-news (stream `wss://stream.data.alpaca.markets/v1beta1/news`); https://alpaca.markets/blog/introducing-news-api-for-real-time-fiancial-news/ (Alpaca, 2022-02-07: "real-time and historical news data dating back to 2015", "real-time news data via WebSocket") | 2026-11-25 | confirmed (dead link replaced: old URL 301-redirects to docs.alpaca.markets/docs/news-api, which returns 404) | Link replaced with the Alpaca docs page and Alpaca's own launch post; claim unchanged |
| 3.3 | Alpaca News API · Cost / limits (link) | At launch the news API was free with rate limits of 200 calls/min on free plans | "([Benzinga](https://benzinga.com/z/25468501))" | https://alpaca.markets/blog/introducing-news-api-for-real-time-fiancial-news/ (Alpaca, 2022-02-07: "News API is currently available for free" during a limited-time beta; "200 calls per minute for Free plans and 10,000 call per minute for Unlimited plans") | 2026-11-25 | confirmed (link fixed: Benzinga URL returns 403 and was a non-primary only source) | Citation replaced with Alpaca's own launch post; claim unchanged |
| 3.4 | Exchange trade-halt feeds (marker 1 of 4) | Nasdaq Trader halts RSS gives halts and resumptions with reason codes, free | "Halts and resumptions with reason codes · Free · [verify] in Phase 1" | https://www.nasdaqtrader.com/Trader.aspx?id=TradeHalts (page links "Trading Halt RSS Feed"; "Halt times displayed are Eastern Time"); https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts (fetched once: RSS 2.0, `ndaq:` namespace, fields listed in the row; Market values NASDAQ, NYSE, AMEX; reason codes e.g. T1, H11, T12); https://www.nasdaqtrader.com/Trader.aspx?id=CopyDisclaimMain ("personal and non-commercial use only") | 2026-11-25 | confirmed | Marker removed; feed URL, fields and site-use terms added; no published polling limit found |
| 3.5 | Company IR RSS / press-release wires (marker 2 of 4) | Company IR pages offer free RSS for earnings releases, guidance, deals | "Free RSS · [verify] per company" | https://www.apple.com/newsroom/rss-feed.rss (fetched once: Atom feed "Apple Newsroom"; includes "Apple reports fourth quarter results", 2026-11-02, category PRESS RELEASE); https://investor.apple.com/investor-relations/default.aspx (no RSS link shown); https://www.microsoft.com/en-us/investor (no RSS; "Email Alert" link); https://news.microsoft.com/source/feed/ (RSS 2.0 "Source", no earnings releases among recent items) | 2026-11-25 | corrected | "Free RSS" reworded to "free where offered, not every company publishes one", with the AAPL and MSFT findings; marker removed; per-company check at onboarding, EDGAR 8-K as fallback |
| 3.6 | FRED (marker 3 of 4) | FRED API is free and needs an API key | "Free API key · [verify]" | https://fred.stlouisfed.org/docs/api/api_key.html ("All web service requests require an API key"; key requested after logging in to a FRED account); https://fred.stlouisfed.org/legal/ ("You are free to access and use FRED at no cost"); https://fred.stlouisfed.org/docs/api/terms_of_use.html (Bank "may impose limits", no number; third-party series personal use only; required notice; invalid keys blocked) | 2026-11-25 | confirmed | Marker removed; key requirement, no-cost statement, unpublished rate limit, third-party-series and notice terms added. The often-quoted "120 requests/min" figure is not on any FRED page and was not recorded |
| 3.7 | Economic calendars BLS, BEA, Fed (marker 4 of 4) | Free official calendars for CPI, jobs, GDP and FOMC dates | "CPI, jobs, GDP, FOMC dates · Free, official · [verify]" | https://www.bls.gov/schedule/news_release/ ("Schedule of Selected Releases"; Employment Situation and CPI at 8:30 AM ET; .ics at /schedule/news_release/bls.ics); https://www.bea.gov/news/schedule (GDP, Personal Income and Outlays at 8:30 AM; ICS subscription; JSON release_dates.json); https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm (2026 and 2027 FOMC dates; 2027 tentative; RSS for news, no .ics) | 2026-11-25 | confirmed | Marker removed; official calendar URLs and machine-readable formats added |

## 4. Alpaca free-tier terms, endpoints and EDGAR terms (A2, G-5)

| # | Term | Verified value | Primary source URL | Accessed | Verdict | Change made |
|---|---|---|---|---|---|---|

## 5. STRATEGY_ENCYCLOPEDIA evidence cells and links (A3)

| # | Family · row | Claim | Original text | Primary source URL | Accessed | Verdict | Change made |
|---|---|---|---|---|---|---|---|

## 6. Broker and post-mortem sources (A4)

| # | Proposal ID | Claim | Primary source URL | Accessed | Verdict | Note |
|---|---|---|---|---|---|---|
