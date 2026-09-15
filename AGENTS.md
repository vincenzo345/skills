# Agent operating priorities

Apply these priorities in order to every task in this repository:

1. **Outcome** — Achieve the user's desired outcome. Establish a concrete completion condition and continue until it is met or a genuine blocker requires user or external action.
2. **Token economy** — Use the fewest tokens that can reliably achieve and verify the outcome. Reuse evidence, disclose detail only when its branch is active, and avoid duplicate exploration, artifacts, explanations, and reviews.
3. **Proportional execution** — Use the simplest approach that fully addresses the task's uncertainty, risk, and proof needs. Avoid both unnecessary machinery and shortcuts that leave the outcome unproven.
4. **Session closure** — Aim to complete the current outcome in one session. Treat 150,000–250,000 tokens as the planning envelope for a session on frontier models with roughly 1.05M-token context windows. Finish earlier when the outcome is achieved. If the work cannot responsibly finish in that envelope, reach a clean stopping point and persist the current state, evidence, decisions, remaining uncertainty, and exact next action so another session can resume without repeating discovery.

Higher priorities override lower ones. Token economy and session sizing never justify weakening the requested outcome, required safety, or necessary verification.
