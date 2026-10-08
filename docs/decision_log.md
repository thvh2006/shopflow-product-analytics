# Decision Log

| Date | Decision | Evidence | Consequence |
|---|---|---|---|
| 2026-10-04 | Use REES46 electronics events as the observational backbone | Event-level user, session, product, funnel, and price fields; manageable archive | Enables reproducible funnel and retention analysis |
| 2026-10-04 | Reconstruct sessions with 30-minute inactivity | Source IDs collide across users and can span many days | Retain source ID for audit; use analytics sessions for metrics |
| 2026-10-04 | Generate experiment data transparently | Source contains no random treatment assignment | Causal results will be synthetic and separated from observational findings |
| 2026-10-04 | Do not call purchase-item value revenue | No order ID, taxes, discounts, refunds, or currency audit | Use the precise label `observed purchase-item value` |
| 2026-10-04 | Prioritise high-price computer cart completion | Computer cart completion falls from 55.24% in Q1 to 41.16% in Q4; video cards combine scale and low completion | Test purchase-confidence support after eligible add-to-cart events |
| 2026-10-04 | Randomise at user level and analyse intention-to-treat | Session assignment could expose the same user to both variants | Stable first-eligibility assignment; one analysis row per user |
| 2026-10-04 | Power for a 5% relative lift | 42.94% observed eligible baseline; 80% power and two-sided 5% alpha require about 8,391 users per arm | Record the 16,782-user requirement; do not manufacture sample size by resampling 9,742 source users |
| 2026-10-04 | Treat unresolved SRM as invalidation | Differential telemetry loss can preserve a persuasive treatment estimate | Ship a deliberately broken scenario that the analysis rejects before effect interpretation |
| 2026-10-08 | Remove synthetic launch authority | The effect is injected and the unique-user population is below the planning floor | Treat the run as pipeline validation; require a real A/A and adequately powered randomized test |
| 2026-10-04 | Publish session and funnel sensitivity instead of one canonical number | 15/30/60-minute view-to-purchase spans 4.47%–4.70%; strict product grain lowers cart completion | Use session KPI for product outcome and strict product path for diagnosis |
| 2026-10-04 | Add an adjusted association model, not a causal model | Q4 association persists after category, month, and user-status controls; pseudo-R² remains low | Use it to prioritise data collection and testing, never to claim price causality |
| 2026-10-04 | Exclude the qualifying session from all pre-period features | A deep audit found that session start precedes the qualifying cart timestamp, leaking the current session into “prior” counts | Rebuilt experiment cohort; added a regression test requiring 8,233 truly first-observed eligible users |
| 2026-10-04 | Keep weak CUPED performance | Corrected pre-period value reduces variance by only 0.26% because most users have no history | Report the limitation instead of selecting a post-treatment or stronger-but-invalid covariate |
