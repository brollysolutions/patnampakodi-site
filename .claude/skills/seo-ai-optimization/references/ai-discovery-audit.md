# Detailed AEO, GEO and LLMO audit

Include the content-readiness pass in a full audit. Use actual answer products
only through available, authorized free access. If no such access exists, finish
content/technical analysis and label product-answer visibility unverified.

**AEO** means answer engine optimization: make useful answers accurate and easy
to find. **GEO** means generative engine optimization: provide evidence and context
worth citing in a generated answer. **LLMO** means large language model
optimization: improve retrieval and faithful interpretation of the site's
entities, facts and relationships. These overlap and are working practices,
not three independent documented ranking algorithms.

## 1. Define the discovery tasks

Identify who searches, their market/language, task, knowledge and decision stage.
Build a small representative query/prompt set covering the intents in scope:

- Direct questions and definitions grounded in the page topic.
- How-to or troubleshooting tasks the business can answer correctly.
- Comparison/suitability questions with explicit user constraints.
- Commercial/local discovery using only real offers and locations.
- Brand/entity facts such as scope, availability, terms or prerequisites.

Derive prompts from actual queries, observed questions or supplied user needs.
Label brainstormed prompts as proposed. Avoid prompts that instruct a model to
mention the brand; those measure instruction following, not natural discovery.
Use comparable branded and unbranded tasks where relevant. No fixed word count,
prompt count or paragraph length is a visibility requirement.

## 2. AEO: answer completeness and extractability

For each material question, locate the answer and assess:

| Check | Evidence to inspect | Appropriate improvement |
| --- | --- | --- |
| Directness | Whether the page answers the question before generic scene-setting | Lead with the useful answer, then explain |
| Completeness | Necessary steps, prerequisites, constraints, units and exceptions | Keep the facts needed to use the answer safely |
| Independence | Whether an extracted passage still names its subject and comparison basis | Replace ambiguous pronouns/references where context would be lost |
| Format | Whether sequence, comparison or definition matches the task | Use lists/tables/paragraphs because the information calls for them |
| Trust | Whether sources substantiate the answer and caveats remain attached | Cite the actual basis and preserve qualifications |
| Access | Whether answer text is present and readable in inspected source/DOM | Investigate render/interaction barriers without fabricating index status |

Record **answered / partially answered / unanswered / unverified** per question,
with URL and section evidence. Do not force every heading into a question,
repeat the same answer in filler FAQs or write bot-only summaries. Featured
snippet selection cannot be guaranteed or designated through special markup.
[Google featured snippets](https://developers.google.com/search/docs/appearance/featured-snippets).

## 3. GEO: useful evidence and citation opportunities

Identify what a generated answer could legitimately cite: original data with a
method, a documented demonstration, a precise explanation, a source-backed
comparison, verified business terms or an expert account supplied by the user.
Distinguish original evidence from restating somebody else's conclusions.

For each potential citation passage record claim, supporting source, authorship/
review context where appropriate, date, limitations and stable URL/section.
Keep source attribution near the claim and uncertainty near the conclusion.
Do not hide qualifications below a CTA or require a model to follow several
links to discover that a service is only proposed.

Compare sources actually cited in observed competitor/AI answers. Explain why
their evidence serves the task and what honest contribution the user can add.
Do not assume a cited domain will be cited for every prompt, copy its tables or
fabricate original studies. Schema, backlinks, word count and brand repetition
alone do not prove citation readiness or cause an AI citation.

## 4. LLMO: entity and relationship clarity

Build a compact entity/fact map from evidence:

| Entity/fact | Check |
| --- | --- |
| Organization/brand | Consistent name, real identity and clear distinction from similarly named entities |
| Offer/product/service | What it is, who it suits, scope, prerequisites and actual availability |
| People | Supplied/verified roles and credentials; no invented reviewer or experience |
| Locations | Real locations/service areas and relevant contact information |
| Commercial terms | Price basis, units, inclusions, dates and qualifications when known |
| Relationships | Who provides what, where, to whom, with which conditions |
| Sources and versions | Which page is current, authoritative within the site and supported by linked evidence |

Audit inconsistent naming, stale duplicate pages, vague comparisons and pronouns,
unexplained abbreviations, conflicting facts and missing scope. Correct them
for readers and faithful retrieval. Use legitimate structured data only when
supported by visible facts; JSON-LD syntax is not a truth or comprehension test.

Keep important facts in readable text with meaningful headings and crawlable
internal links. Preserve context in chunks: subject, units, dates, applicability
and caveats. This is editorial judgment, not a requirement to target a model's
token/chunk size. Do not claim these edits change model weights, guarantee
training ingestion or overwrite knowledge already present in a model.

## 5. Retrieval and crawler controls

Inspect the actual robots, response directives, render output and CDN behavior
when scope supports them. Verify current provider documentation before naming
agents or recommending access changes. Separate search retrieval, training
collection and user-requested fetching; allowing one does not imply the others.

OpenAI documents OAI-SearchBot for search, GPTBot for training and ChatGPT-User
for user-initiated visits. Their purposes and controls differ; do not advise
enabling training collection as a prerequisite to search visibility.
[OpenAI crawlers](https://developers.openai.com/api/docs/bots).

Perplexity documents its search crawler and user-directed fetching separately.
Use its current guidance and verified crawler identity when reviewing logs/CDN
rules; a claimed user-agent string alone does not authenticate a crawler.
[Perplexity crawlers](https://docs.perplexity.ai/docs/resources/perplexity-crawlers).

For Google AI features, ordinary SEO foundations and snippet eligibility apply;
do not prescribe special AI schema or an AI text file. `llms.txt` is not a
documented prerequisite for those features. If the user requests an experiment,
define its scope and measurement without promising adoption or rank.
[Google AI features](https://developers.google.com/search/docs/appearance/ai-features).

Audit mode recommends changes; it does not alter robots/CDN/consent rules.
Never bypass staging protection, put instructions to rank/recommend the brand
in hidden text, cloak content for AI visitors or inject prompts into metadata.

## 6. Observe actual answers

For each authorized test capture product and visible model/version, prompt,
timestamp, market/language, logged-in or other relevant session conditions,
retrieval setting if visible, answer evidence, cited URLs and failures. Use
fresh comparable sessions where practical. Record nondeterminism and access
limits; never use paid API calls under the free-only constraint.

Evaluate independently:

- Was the relevant URL cited? A linked URL is different from an unlinked mention.
- Was the brand/entity described accurately?
- Did the answer retain material qualifications, units and availability?
- Was a recommendation suitable for the stated user constraints?
- Which factual errors or unsupported inferences appeared?

An answer generated by the auditing agent as an illustration is not evidence of
external product visibility. Ordinary web results, backlinks and fetched pages
are not observations of ChatGPT, AI Overviews or Perplexity answers. If a product
cannot be tested, record unverified rather than filling in a plausible answer.

## 7. Benchmark and report without false precision

Keep a fixed core prompt set across comparable review windows, with a separately
labeled exploratory set. Repeat when useful within available free quotas. Report
raw counts and denominator, for example “cited in 3 of 10 successfully observed
responses in this sample”; disclose failed/missing tests separately. Do not
exclude no-citation answers from the denominator or call the result market share.

Track citation accuracy, factual fidelity, relevant mentions, suitability and
attributable visits/conversions where existing data supports them. Separate
platforms and conditions. An observed lift after editing is an association unless
the study can distinguish competing causes. Do not invent separate analytics
dimensions for AI products if the provider does not expose them.

Deliver an answer-gap matrix, entity/claim issues, citation opportunities,
retrieval-control findings, observed prompt benchmark, prioritized changes and
unverified items. Use one finding ID across SEO/AEO/GEO/LLMO when a single root
cause affects several surfaces. Link concrete sections and evidence; no acronym
score should substitute for a reader-facing explanation.
