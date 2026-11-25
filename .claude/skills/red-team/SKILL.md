---
name: red-team
description: Independent adversarial review of a family-desk plan, spec or phase result, run in a fresh session. Use when the owner asks for a red-team, independent review, or stress test.
---

# Red team

Act as a reviewer who did not write this work. Find what would lose the family money, break the law, or fail silently. Do not soften findings.

Check, citing file and line where possible:
1. Any path from an LLM, a bug or external text to an order that skips the risk kernel.
2. Any hard limit or mode that can be raised quickly.
3. Behavior when the server, broker API, data feed or internet fails mid-order.
4. Crash response: failing to de-risk, and de-risking into whipsaw.
5. Tax-reserve correctness: losses, wash sales across the household, NJ, estimated payments.
6. Results that rely on overfit or look-ahead-contaminated backtests (FAILURE_LIBRARY F-02, F-09).
7. Costs vs sleeve size.
8. Security: key exposure, command spoofing, dependency or dev-pipeline tampering, secrets in logs or git history.
9. Operations: partial fills, halts, corporate actions, extended hours, provider outages, clock/timezone and holiday bugs.
10. Every row of `docs/COMPLIANCE.md`.
11. Every entry in `docs/research/FAILURE_LIBRARY.md`: is its control present and tested?
12. Fact-check claims about brokers, rules, taxes and prices against live primary sources.

Output `docs/phases/phase_{N}/phase_{N}_redteam.md`: ranked findings (severity, scenario, evidence, fix), proposed new FAILURE_LIBRARY entries, and a go / no-go with conditions.
