# Keyword research and URL strategy

Produce decisions about which reader needs each URL serves. A large keyword
list is not a strategy. Use research setup first and retain metric provenance.

## 1. Define the market and baseline

Extract actual products/services/topics, audience vocabulary, purchase or task
constraints, language and geography. Separate brand/nonbrand, existing/new
customers, informational/commercial/transactional/navigational and local intent.
Mixed intent is possible; verify page types before forcing a single label.

Read available Search Console query/page exports, route inventories, content
lists and aggregated conversion reports. Preserve date windows and filters.
Do not silently join page-only totals to query rows as query-level conversions.
Keep raw URLs until redirects/canonicals establish equivalence; query strings,
case and trailing slashes can represent distinct resources.

## 2. Build and expand seeds

Start from the audience's tasks and the confirmed offer. Consider:

- Category/entity terms and natural synonyms.
- Problems, prerequisites, methods, troubleshooting and practical questions.
- Costs, inclusions, delivery, suitability and alternatives when relevant.
- Comparisons, use cases, specifications or compatibility when facts support them.
- Location/language modifiers for real service areas or distinct localized needs.

Expand using observed queries/results, questions, relevant competitor sections
and authorized keyword data. Mark brainstormed queries **proposed**, not measured.
Keep negative/excluded intents so irrelevant jobs, freebies, unsupported locations
or different products do not return disguised as high-volume opportunities.

## 3. Inspect search intent

For representative queries in each candidate cluster, inspect the actual result
mix and relevant pages. Log query, sources, market, date and tool limitations.
Note dominant page type, task, audience knowledge, freshness requirements,
SERP features and whether an answer might satisfy the query without a click.
Do not claim a zero-click rate without data.

Group variants when the same page can satisfy their purpose well. Shared words
alone do not establish shared intent. Substantial SERP overlap supports a cluster
but no fixed percentage is a ranking rule; mixed/unstable results need judgment.
Queries in different languages need independent intent checks, not literal
translation and inherited volume.

## 4. Evaluate demand without false precision

For any volume, CPC, difficulty, traffic or trend value, preserve provider,
retrieval date, market, language, device where available, time window and units.
Retain ranges and provider caveats, including grouped variants. Do not add
overlapping keyword volumes to imply distinct people or guaranteed traffic.

Search Console impressions measure the site's observed exposure, not total
market demand. Average position is aggregated; an expanded query mix can change
it without existing rankings deteriorating. Sum clicks and impressions before
calculating aggregate CTR; do not average row CTRs. Never average average-position
rows blindly across incompatible dimensions. Trends compares normalized interest
within its selected context. Ads competition/CPC do not establish organic difficulty.
[Search Console](https://support.google.com/webmasters/answer/7576553),
[Google Trends](https://support.google.com/trends/answer/4365533).

If numeric data is unavailable, label it unknown and use supported qualitative
signals: repeated relevant result coverage, existing impressions, direct customer
needs supplied by the user and fit to the business. Never invent a numeric
opportunity score to fill a table.

## 5. Map clusters to URLs and find conflicts

Assign each intent cluster an owner URL and one of: improve existing, create,
consolidate proposal, retain, or defer. Include primary query, supporting queries,
page type, business role and the specific unique value to publish.

Check existing URLs first. Two pages appearing for a query are not automatically
cannibalization. Look for the same intent, overlapping value and evidence of
confusing URL selection or performance harm. Different funnel stages, useful
local pages and legitimate multiple result appearances can coexist.

For a proposed consolidation, retain the original URL and performance evidence,
choose a destination that actually satisfies the old intent, identify content
to preserve and list redirect/internal-link/sitemap changes as a separate scoped
implementation. Do not change slugs just to insert keywords.

## 6. Prioritize and hand off

Evaluate business fit, intent fit, observed demand, evidence the business can
provide, competitor quality, current URL traction and work required. A small
high-intent cluster can outrank an unrelated high-volume term in the work plan.

Use **now / next / later / reject** with an explicit rationale and confidence.
Separate research confidence from estimated implementation effort. Do not predict
rankings, traffic or revenue from keyword volume alone. If a scenario is requested,
label CTR/conversion inputs as assumptions and show a range with dependencies.

For each approved writing target, hand off the content brief template: reader
task, intent, owner URL, questions, evidence gap, original contribution, relevant
internal links, CTA and acceptance criteria. A content calendar follows evidence
availability and owner capacity; do not invent a publishing quota.

## Keyword map fields

`cluster_id, primary_query, supporting_queries, intent, audience, market,
language, page_type, owner_url, action, business_fit, evidence_ids,
demand_value_or_unknown, demand_unit, provider, window, retrieved_at,
competition_observations, unique_value, priority, rationale, confidence`

Use readable tables for small sets; CSV plus a written rationale for large sets
when file output is authorized. Keep proposed and observed queries distinguishable.
