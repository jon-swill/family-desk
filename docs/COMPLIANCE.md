# Compliance requirements

Owner decision: follow all applicable laws and every broker and data provider's terms. This is a working checklist, not legal advice; confirm anything uncertain with a securities attorney or the CPA. Each item becomes a test or a kernel rule where it can.

| ID | Requirement | How the system enforces it |
|---|---|---|
| C-1 | No market manipulation: no spoofing or layering (orders placed with intent to cancel), no wash trades (buying and selling the same security without a real change in ownership, including across the household's own accounts), no marking the close, no pump-and-dump behavior | Kernel blocks opposite-side orders in the same symbol across household accounts within a window; no order is placed without intent to fill; no trading in the final minutes by default (R-24); order-to-fill ratio monitored |
| C-2 | Pattern-day-trader / intraday margin rules | Built in so the owner does not have to track them: margin is off, so accounts are cash accounts; PDT never applied to cash accounts, and FINRA replaced PDT with an intraday margin standard effective 4 June 2026 with phase-in allowed to 20 Oct 2027 ([FINRA RN 26-10](https://www.finra.org/rules-guidance/notices/26-10)). Broker-specific rules live in the broker adapter config |
| C-3 | No trading on material non-public information; conflicts of interest | Restricted list in config; kernel blocks every symbol on it. The list starts empty and is owner-maintained: the owner adds a symbol whenever they know of a conflict. No employer-policy check (owner decision 2026-11-24, RETRO) |
| C-4 | Cash-account settlement rules (Reg T: no good-faith violations or free-riding; T+1 settlement) | Kernel checks settled cash before every buy |
| C-5 | Taxes: report every sale; wash-sale rule across all household accounts; estimated payments | Ledger, restricted list, reserve and payment schedule (FR-21–23) |
| C-6 | Broker terms of service | Official APIs only (Alpaca Trading API, Schwab developer API, Robinhood Agentic Trading); never automate a broker's website or app by scraping or screen control |
| C-7 | Data and news terms | Official APIs/RSS only; respect rate limits (e.g. SEC 10 req/s); personal use, no redistribution; no scraping sites that prohibit it |
| C-8 | Short-sale rules (Reg SHO) | Shorting is off |
| C-9 | Investment-adviser registration | The system manages only the household's own money and never anyone else's, for pay or not, without legal advice first |
| C-10 | Recordkeeping for tax and disputes | Append-only ledger retained at least 7 years; broker statements archived monthly |
| C-11 | Options (when the manual phase arrives): broker options approval levels, assignment and exercise rules | Out of scope until then; automated paths reject options (FR-14) |
| C-12 | Crypto (future): tax rules, possible wash-sale extension | Out of scope; ledger can shadow-compute crypto wash sales |
