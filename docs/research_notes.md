# Research Notes

## Research question

What analytical and experimentation practices are required to turn e-commerce event logs into a trustworthy product decision rather than a collection of funnel charts?

## Dataset decision

### Selected: REES46 electronics-store events

Reasons:

- Permanent user and source-session identifiers support behavioural and repeat-use analysis.
- `view`, `cart`, and `purchase` events support a product funnel.
- The compressed archive is approximately 20 MB, making the repository reproducible for reviewers.
- REES46 publishes the data directly and describes the events as anonymised.

Observed after retrieval:

- 885,129 raw event rows.
- 407,283 users.
- 490,398 distinct source-session strings.
- Event period: 2020-09-24 through 2021-02-28.
- 793,748 views, 54,035 cart events, and 37,346 purchase-item events.

### Rejected as the primary source: GA4 obfuscated e-commerce sample

Google's official GA4 sample is credible and has a real export schema, but requires a Google Cloud project and BigQuery access. Google also warns that obfuscation creates placeholders and limited internal consistency. REES46 provides a lower-friction reproducible source for a public portfolio.

### Rejected as the main experiment source: Criteo uplift benchmark

Criteo provides a large genuine incrementality benchmark with treatment and outcomes. It is strong for uplift modelling but anonymised features and advertising context limit product-funnel interpretation. This project instead uses a transparent synthetic experiment calibrated from observed product metrics. Criteo remains a possible advanced extension, not evidence about ShopFlow.

## Initial data-quality findings

1. There are 655 exact duplicate rows.
2. There are 165 events without a source-session ID.
3. A source-session string can map to more than one user in 214 cases.
4. Source sessions can span multiple days; 14,070 user-session pairs cross a date boundary and the maximum duration exceeds 150 days.
5. Session IDs therefore cannot be used blindly. The canonical pipeline will create analytics sessions using a 30-minute inactivity rule per user while retaining the source ID for audit.
6. Category code and brand are missing for 236,219 and 212,364 raw rows respectively. Category/brand comparisons must expose an `Unknown` group instead of silently dropping these records.
7. Purchase rows appear item-grained. Without an order ID, summed purchase prices are labelled observed purchase-item value, not audited revenue.

## Product measurement research

Google's HEART paper maps product goals to signals and metrics across Happiness, Engagement, Adoption, Retention, and Task Success. This project uses the same goal-signal-metric discipline but only claims dimensions supported by behavioural logs.

Microsoft experimentation guidance separates success/OEC metrics, guardrails, feature metrics, and data-quality metrics. The project will define these before generating or analyzing experiment outcomes.

## Experiment trustworthiness research

- **Sample ratio mismatch:** Microsoft research treats unresolved SRM as a trust failure that must be investigated before interpreting treatment effects.
- **Metric interpretation:** statistical significance alone is insufficient; local metric gains can hide degradation elsewhere, and telemetry changes can bias a metric.
- **Power and MDE:** sample size will be computed before reading outcomes, using a two-sample proportion framework for the primary conversion metric.
- **Variance reduction:** CUPED will use a genuinely pre-treatment covariate from generated pre-period behaviour; post-treatment variables will never be used.
- **Novelty and primacy:** effects will be inspected by experiment day instead of assuming the pooled estimate is stable.

## Primary and authoritative references

1. REES46, Free e-commerce behaviour datasets: https://rees46.com/en/datasets
2. REES46, Direct dataset catalogue: https://data.rees46.com/
3. Google Research, *Measuring the User Experience on a Large Scale*: https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/
4. Google Analytics, GA4 BigQuery sample dataset and limitations: https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset
5. Fabijan et al., *Diagnosing Sample Ratio Mismatch in Online Controlled Experiments*: https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/
6. Dmitriev et al., *A Dirty Dozen: Twelve Common Metric Interpretation Pitfalls*: https://www.microsoft.com/en-us/research/publication/a-dirty-dozen-twelve-common-metric-interpretation-pitfalls-in-online-controlled-experiments/
7. Microsoft Research, *Patterns of Trustworthy Experimentation: Pre-Experiment Stage*: https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-pre-experiment-stage/
8. Microsoft Research, *Patterns of Trustworthy Experimentation: Post-Experiment Stage*: https://www.microsoft.com/en-us/research/?p=806938
9. Deng et al., *Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data*: https://robotics.stanford.edu/~ronnyk/2013-02CUPEDImprovingSensitivityOfControlledExperiments.pdf
10. statsmodels, two-independent-proportion power calculation: https://www.statsmodels.org/stable/stats.html
11. Kohavi et al., *Online Experimentation at Microsoft*: https://www.microsoft.com/en-us/research/publication/online-experimentation-at-microsoft/
12. Microsoft ExP, *Data Quality: Fundamental Building Blocks for Trustworthy A/B Testing Analysis*: https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/articles/data-quality-fundamental-building-blocks-for-trustworthy-a-b-testing-analysis
13. Microsoft ExP, *Patterns of Trustworthy Experimentation: During-Experiment Stage*: https://www.microsoft.com/en-us/research/?p=720145
14. Microsoft ExP, *External Validity of Online Experiments: Can We Predict the Future?*: https://www.microsoft.com/en-us/research/articles/external-validity-of-online-experiments-can-we-predict-the-future/

## Research questions still open for production

- Which checkout step and stable error code explain the largest share of post-cart exits?
- Do users interpret cart as purchase intent, comparison storage, or price monitoring?
- Which reassurance component—compatibility, delivery, returns, or payment—changes behaviour?
- Does the effect persist to fulfilled orders after cancellations and refunds?
- Can a live A/A validate assignment, trigger, and telemetry across device and geography slices?
