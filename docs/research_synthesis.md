# Research Synthesis: From Event Logs to a Trustworthy Product Decision

## Why a funnel chart is not enough

An event funnel is a measurement model, not a direct recording of user intent. Its result depends on the unit of analysis, event ordering, observation window, identity stitching, session boundary, and instrumentation coverage. A credible product analysis therefore has two jobs:

1. determine whether the behavioural pattern survives defensible alternative definitions; and
2. separate evidence about **where** behaviour changes from hypotheses about **why** it changes.

ShopFlow uses real anonymised behavioural records for the first job. It refuses to infer an internal motivation—trust, compatibility anxiety, payment friction, delivery uncertainty—from clicks alone.

Google's HEART work recommends mapping product goals to observable signals and then to metrics, rather than selecting convenient metrics first. This project applies that discipline narrowly: task success is represented by an ordered purchase outcome, engagement by product/cart activity, and retention only by observed return. Happiness and adoption are not claimed because the source contains no attitudinal or acquisition data. [Google Research: HEART](https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/)

## Metric grain changes the story

A session-level funnel answers whether a session contains certain behaviours. A same-product ordered funnel asks whether the same product was viewed, carted, and purchased in timestamp order. Neither is universally correct:

- Session-level metrics align with the business question “did this shopping visit convert?” but can match unrelated products or reversed events.
- Session-product metrics preserve journey integrity but can miss valid cross-session consideration, direct-buy flows, and purchases after a session boundary.

The correct practice is to publish both and explain the decision each supports. ShopFlow uses qualified-session purchase conversion for the product-level outcome and strict session-product order for diagnosing a specific friction point.

## Observational segmentation is hypothesis generation

Segments are not treatments. A lower conversion rate for expensive products does not mean lowering price or adding reassurance will cause conversion to rise. Price is entangled with product type, brand, availability, promotion, delivery, and user selection. Conditioning on cart also selects users who have already demonstrated intent and can create collider bias.

The adjusted logistic model therefore has a deliberately limited interpretation: among already-carted session-products, price quartile remains associated with completion after controlling for broad category, calendar month, and first/returning status. It strengthens the prioritisation signal but does not identify a causal price effect.

## What trustworthy experiments require

Random assignment supports causal inference only when assignment, exposure, telemetry, and analysis units remain aligned. Microsoft describes online experiments as a way to separate the product change from environmental movement and repeatedly emphasizes that data-quality metrics must be checked before outcome metrics. [Online Experimentation at Microsoft](https://www.microsoft.com/en-us/research/publication/online-experimentation-at-microsoft/), [Data Quality for Trustworthy A/B Testing](https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/articles/data-quality-fundamental-building-blocks-for-trustworthy-a-b-testing-analysis)

The ShopFlow design therefore distinguishes:

- assignment from exposure;
- intention-to-treat from tempting post-treatment slices;
- primary outcome from diagnostic and guardrail metrics;
- statistical significance from practical thresholds;
- a valid null/result from an invalid experiment.

### Sample ratio mismatch

Sample ratio mismatch (SRM) tests whether observed allocation is compatible with the planned split. It does not identify the root cause, but unresolved SRM invalidates ordinary treatment-effect interpretation. Potential causes include assignment bugs, bot filtering, trigger asymmetry, join loss, and variant-specific telemetry loss. Microsoft's taxonomy documents why SRM should be treated as a trust failure rather than another dashboard warning. [Diagnosing Sample Ratio Mismatch](https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/)

ShopFlow includes a deliberately broken dataset where treatment rows are lost. The apparent outcome remains favourable, demonstrating that a persuasive p-value cannot repair a broken sample.

### Power and minimum detectable effect

Power planning forces the team to state what improvement is worth detecting before reading the result. At a 42.94% baseline, detecting a 5% relative improvement requires about 8,391 users per arm for 80% power and a two-sided 5% type-I error rate. Detecting a 2% relative lift would require more than 52,000 per arm. This curve communicates the cost of expecting precision for tiny product effects.

An A/A Monte Carlo calibration is also included. Across 5,000 simulated null experiments, the false-positive rate is 5.18% at nominal alpha 5%, and the p-value deciles are close to uniform. This is a test of the analysis implementation, not proof that a production assignment service works.

### Variance reduction

CUPED uses pre-treatment information correlated with the outcome to reduce variance without changing the estimand. The critical requirements are that the covariate predates assignment and is unaffected by treatment. [Deng et al., CUPED](https://robotics.stanford.edu/~ronnyk/2013-02CUPEDImprovingSensitivityOfControlledExperiments.pdf)

ShopFlow's pre-period value is weak for first-observed users, so variance reduction is small. That is a substantive measurement result: CUPED is not automatically impressive, and weak historical coverage limits its benefit. The project reports the small reduction instead of selecting a post-treatment covariate or hiding the result.

### Temporal stability and novelty

Treatment effects can change as users learn or as external conditions move. Microsoft reports that even week-long estimates can lack next-day stability and identifies novelty and primacy as important—but not exclusive—causes. [External Validity of Online Experiments](https://www.microsoft.com/en-us/research/articles/external-validity-of-online-experiments-can-we-predict-the-future/)

The readout therefore includes daily effects and a formal interaction comparing days 1–2 with days 3–14. It does not diagnose novelty merely because one day is significant and another is not; heterogeneity requires an interaction test.

### Metric multiplicity and interpretation

Experiment scorecards create many chances for a false discovery. The “Dirty Dozen” paper documents how local metrics, ratios, telemetry changes, and conditioning can mislead. ShopFlow preregisters one primary outcome, treats value as secondary, and gives latency/error metrics explicit guardrail thresholds. [A Dirty Dozen](https://www.microsoft.com/en-us/research/publication/a-dirty-dozen-twelve-common-metric-interpretation-pitfalls-in-online-controlled-experiments/)

The decision rule does not allow a significant secondary metric to rescue a failed primary, and does not treat a statistically detectable 17 ms latency increase as automatically harmful when the practical guardrail is +50 ms.

## What the evidence supports

The observational evidence supports prioritising high-price computer carts for deeper measurement and a randomized test. The synthetic experiment demonstrates how that test would be designed and read. Neither component proves a real feature will improve a real company's results.

The next real-world learning step would combine:

- checkout-step and error instrumentation;
- qualitative sessions about compatibility, delivery, returns, and payment concerns;
- a production A/A validation of the assignment/telemetry stack; and
- a user-randomised A/B test using the preregistered outcome and guardrails.
