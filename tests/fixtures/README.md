# Test fixtures

Synthetic payloads shaped like the provider documentation (Alpaca Trading/Market Data API
reference, SEC EDGAR Atom). No real account data, keys or personal values. Real recorded
payloads, where used, say so in a header comment with source URL and access date.

`alpaca_account_no_pdt.json` follows the current Account schema for `GET /v2/account`
(https://docs.alpaca.markets/reference/getaccount-1, read 2026-11-25), which has no
`pattern_day_trader` field. It reproduces the shape that crashed the B10 live run on
2026-11-25. Values are synthetic.
