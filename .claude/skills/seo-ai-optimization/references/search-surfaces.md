# Search, answers, citations and decisions

These are working definitions for this workflow. AIO, LLMO, LMO, LLM SEO and DEO do
not have one universally agreed specification. Use the user's definitions when
provided; otherwise explain the practical outcome instead of implying a
documented ranking mechanism.

| Surface | What to improve | What to measure |
| --- | --- | --- |
| SEO: search engine optimization | Query intent, crawl/index eligibility, page quality and useful links | Organic clicks, impressions, CTR, query/page position trends and qualified conversions |
| AEO: answer engine optimization | Accurate direct answers, clear questions, definitions, procedures and appropriate comparisons | Observed answer/snippet appearances for a recorded query set; answer accuracy and any attributable visits |
| GEO: generative engine optimization | Evidence a generative answer can cite, entity clarity, original useful material and source traceability | Actual cited URLs, accurate brand mentions and observed recommendations for a fixed prompt set |
| AIO: AI optimization | Clear accessible content and accurate machine interpretation across AI discovery surfaces | Retrieval/access checks and whether observed answers preserve the facts and limitations |
| LLMO: large language model optimization / LMO / LLM SEO | Consistent entities, coherent passages, explicit relationships and understandable context | Observed retrieval and faithful citation/paraphrase; no claim of changing model training or weights |
| DEO: decision engine optimization | Fit, alternatives, criteria, tradeoffs, verified commercial facts and appropriate next actions | Qualified enquiries/conversions, factual accuracy of comparisons and recommendation suitability |

For the detailed AEO/GEO/LLMO procedure, entity audit, retrieval controls and
prompt benchmark, read [AI discovery audit](ai-discovery-audit.md). Use one
evidence ledger across these surfaces rather than duplicating findings by acronym.

## Answers that remain correct outside their paragraph

Give a concise answer immediately after a relevant question/heading, then add
the evidence, caveats and useful detail. Name the subject and units. Replace
ambiguous references such as "this is cheaper" with an explicit comparison
when the facts support one. Do not force every heading into a question or
truncate necessary qualifications to meet an arbitrary answer-length target.

Lists are for real sets or sequences; tables are for comparable dimensions.
Use decision rows such as prerequisites, included support, total cost basis,
time commitment and limitations only when the underlying facts exist. State
"ask for the current fee" when appropriate; never fabricate a price or imply
that an unspecified option is free. Competitor statements need their own sources.

For education/service pages, useful decision evidence can include actual
curriculum, intended learner, sample work, instructor credentials, delivery
mode, assessment, refund terms and scope of assistance. These are candidate
facts to verify, not defaults to invent for every provider.

## Visibility claims and crawler access

Google states that ordinary SEO foundations apply to AI Overviews and AI Mode;
supporting pages need to be indexed and snippet-eligible. It does not require
special AI files or schema. Treat `llms.txt` as an optional experiment only if
requested or justified, not a ranking requirement. [Google AI features](https://developers.google.com/search/docs/appearance/ai-features)

Google selects featured snippets algorithmically; page markup cannot designate
a page as the featured answer. [Featured snippets](https://developers.google.com/search/docs/appearance/featured-snippets)

For other AI products, verify the provider's current primary documentation
before making crawler-specific recommendations. Search retrieval, training
collection and user-directed browsing can use different agents and controls.
Do not conflate them or silently alter robots/CDN access policies. A supplied
file cannot establish what a production crawler received.

## Measurement without false precision

- Define the target query set, country/city, language, device and page. Separate
  branded from nonbranded queries and conventional organic results from ads,
  local packs, snippets and AI modules. Positions 1-3 are an aspiration, not a
  forecast. A general web-search result order is not verified local Google rank.
- Compare like date windows with the same filters, noting seasonality,
  algorithm changes, data lag and sample size. Search Console average position
  is an aggregate, not a promise that everyone sees the same rank. A move to a
  lower average position can coexist with broader impressions.
- Record the AI product/model if visible, prompt, locale, date, whether web
  retrieval was enabled, cited URLs, factual errors and available evidence.
  Repeat the same small prompt set at defined review points. One generated
  response is an observation; it does not establish market-wide AI visibility.
- Only claim an AI citation after observing an actual answer or provider
  report. Ordinary web results, backlinks and the agent's own hypothetical
  answer are not evidence of ChatGPT/Copilot/Perplexity citations.
- Google reports AI-feature traffic within Search Console's Web performance;
  do not invent a separate AI Overview CTR or query dimension when unavailable.
  [Google measurement guidance](https://developers.google.com/search/docs/appearance/ai-features#measuring-the-performance-of-your-site)
- Use a provider's AI-performance report only when the user's authorized account
  actually exposes it and its current official definitions have been checked;
  preserve product coverage, date range and metric definitions rather than
  relabeling a limited report all-LLM reach.
- Suggest existing analytics/enquiry measurements. Adding trackers, cookies,
  new events or ongoing scheduled monitoring requires the relevant authorization.
