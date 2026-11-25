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

## 4. Alpaca free-tier terms, endpoints and EDGAR terms (A2, G-5)

| # | Term | Verified value | Primary source URL | Accessed | Verdict | Change made |
|---|---|---|---|---|---|---|

## 5. STRATEGY_ENCYCLOPEDIA evidence cells and links (A3)

| # | Family · row | Claim | Original text | Primary source URL | Accessed | Verdict | Change made |
|---|---|---|---|---|---|---|---|

## 6. Broker and post-mortem sources (A4)

| # | Proposal ID | Claim | Primary source URL | Accessed | Verdict | Note |
|---|---|---|---|---|---|---|
