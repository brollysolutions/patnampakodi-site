# Reports, prioritization and measurement

Use the audit report template as a starting point. Adapt scope while retaining
the evidence, coverage, decisions and verification that make the work reviewable.

## Evidence and findings

Source register fields: evidence ID, URL/file/artifact, access date, query or
tool/command, market/device/window, observed excerpt or result, and limitations.
Use short excerpts and direct source links. Protect private data in screenshots,
URLs and exports. Preserve failed tool results as failures, not negative findings
about the website.

Finding fields: ID, URL/file/component/section, category, observed behavior,
evidence IDs, affected reader task, causal mechanism, severity, confidence,
recommendation, scope/owner when known, effort estimate, dependency and acceptance
check. Example: “At 390 px the sticky enquiry bar covers the submit button;
reproduce with keyboard focus after form validation; reserve space or change
positioning; pass when the focused button and error message remain visible.”

Avoid “optimize UX”, “improve authority” and “add more keywords” without a specific
trigger, evidence and fix. Distinguish source-only candidates from live findings.
Deduplicate one template defect across pages; list scope without inflating counts.

## Severity, confidence and sequencing

| Priority | Meaning | Typical action |
| --- | --- | --- |
| P0 | Verified severe live access failure or materially harmful information/action | Restore essential behavior or correct the harmful fact within authorized scope |
| P1 | Strong evidence of a major search/task barrier on important pages | Address before expanding content or cosmetic work |
| P2 | Useful content, discoverability or usability improvement | Schedule by business value, evidence and effort |
| P3 | Lower-impact polish or explicitly labeled experiment | Do after stronger opportunities; define what would justify it |

Priority is a local work-order convention, not a search-engine scale. Confidence
is high for direct reproducible evidence, medium for strong but incomplete
support, low for a hypothesis. Unknowns belong in a verification queue. Do not
assign a missing metric a critical severity to make a report look comprehensive.

Order fixes by verified access blockers, wrong/missing material facts, intent
and decision barriers, useful differentiation/internal links, then polish. Real
harm or business impact may change that order. Distinguish a one-template change
from many independent edits; record effort as an estimate, not a commitment.

## Measurement plan

Define the baseline before recommending targets:

- Target query/URL set, brand versus nonbrand, market, language, device, search
  type, date range and data source.
- Organic clicks, impressions and CTR with their aggregation rules; query/page
  position trends interpreted with changing query mix.
- Qualified conversions using an existing definition and measurement method;
  raw form counts are not automatically qualified leads.
- Technical tests, crawl/index evidence, lab performance, field performance and
  usability journeys, each with an artifact and observation date.
- AI answer/citation samples separately using the search-surfaces procedure.

Use comparable windows and sufficient observations, noting seasonality, reporting
lag, release changes and other plausible causes. “Review after recrawl and a
comparable reporting window” is a monitoring plan, not a deadline for rankings.
Specify a reasonable check cadence for the site's scale without creating a
scheduled job or changing account settings without authorization.

For Lighthouse, compare the same version, environment, profile and run count.
Report individual results and a median when repeated runs were taken; preserve
variation. Missing field data cannot become a passed CWV result. See the
installed toolchain procedure for actual local commands and their limits.

## Deliverables by mode

Full audit: verdict, scope/coverage, baseline, prioritized findings, keyword map,
competitor matrix, existing-content dispositions, technical and UX evidence,
applicable AI/local/international checks, action plan and unverified items.

Writing: brief, claim ledger, final copy/metadata, internal-link plan, short
before/after explanation and separate missing facts. An audit-only report includes
illustrative fixes but does not silently expand into full rewriting.

Conclude with exact verification states: **passed**, **failed**, **skipped with
reason**, **unverified**. Distinguish installed, configured and runtime-tested
tools. Link the detailed artifacts and lead the user-facing message with the
most consequential findings and next actions.
