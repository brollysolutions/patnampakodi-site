# MVP implementation verification — 2026-09-10

Scope is the [approved MVP](approved-mvp-plan.md), including the preserved
storefront snapshot. Implementation is isolated on `feat/pakodi-mvp`; upstream
was refreshed to `48deff1` without changing the original worktree. The three
source briefs remain unchanged. P1 and the superseded courier integration are
outside this delivery. Recommendations remain gpt-6-astra / High for planning
and Extra High for implementation/review; actual session settings were preserved.
No subagents or independent-review claims are involved.

## Verification evidence

Fresh functional output from the full PowerShell `scripts/verify.ps1 --ci` run
passed **104 workflow tests**, configuration and **22-skill parity**, **53
PostgreSQL/Redis backend tests**, **8 web unit tests**, **39 browser tests** and
technical SEO on **13 public routes**. Ruff, web lint/format/types/build,
one migration head (`0004_operations`) and generated OpenAPI/client parity passed.
There is one intentional lint warning for the private full-document redirect,
upstream test-library deprecation warnings and the SEO checker's 13 skip-link warnings.

That complete command exited 1 at Lighthouse; it is not recorded as a passed
command. Investigation found that the unsupported `--chrome-path` flag silently
selected system Chrome 152. The runner now preflights Playwright's executable and
sets the supported `CHROME_PATH` environment variable. A direct launch and process
inspection confirmed Chromium **153.0.8010.12**, and the final reports record that
browser. The application code is unchanged from the passing functional checks.

The corrected `scripts/verify_containers.py --lighthouse` run exited **0** after
building both pinned images, migrating/seeding a unique fixture database and
checking API/web, indexing/private headers, worker heartbeat, proxy HSTS/API routing
and all **18 Lighthouse observations**. Six route/device groups meet the unchanged
budgets: performance ≥90, accessibility/SEO 100, best practices ≥90, LCP ≤2.5s,
CLS ≤0.1 and TBT ≤200ms. Per the repository's Lighthouse guidance, each group uses
three sequential cold-browser runs: performance metrics/scores use medians;
accessibility, SEO and best practices must pass every observation. Regression
tests reject repeated failures, missing measurements and mixed profile groups.

| Page | Mobile median LCP | Mobile median performance | Desktop median LCP | Desktop median performance |
| --- | --- | --- | --- | --- |
| Home | 2.145s | 98 | 0.461s | 100 |
| Menu | 1.987s | 98 | 0.459s | 100 |
| Contact | 1.974s | 99 | 0.462s | 100 |

Maximum median TBT was 124ms. All observations scored 100 for accessibility,
best practices and SEO. **One individual timing observation exceeded a budget**;
maximum individual TBT was 265ms. Those observations remain in the
summary and are not reported as individual passes. JSON/HTML and Chrome traces
are retained locally under `.agent-workflow/reports/lighthouse-1789035719836/`.
These are local lab measurements, not field Core Web Vitals or certification.

The final frontend splits unrelated client code, generates responsive hero
derivatives during build, preloads its two local fonts and limits balanced
wrapping to the main headline. Mobile and desktop screenshots were reviewed.
The audit measures the standalone images through the shipping Caddy configuration
over HTTPS/HTTP/2. Its disposable localhost certificate is accepted only by the
isolated fixture clients; temporary CA volumes are removed afterwards. No host
trust store or production TLS setting changes. Earlier HTTP/1.1 LCP failures,
CPU warnings and system-Chrome blocking-time failures remain retained. They are
diagnostic records under different serving/browser conditions, not comparable
passing release evidence. Budgets and throttling were not relaxed.

The final npm installation/audit reported zero known vulnerabilities. Sharp
0.35.4 was already in Next.js's locked graph and is an explicit build dependency.
`pip-audit` reported no known vulnerabilities during this session. Image digests,
Actions pins, lockfiles and font licenses were reviewed; both bundled OFL files
match their installed source packages byte-for-byte.

Production Compose/Caddy configuration validation passed. The expanded synthetic
`scripts/verify_restore.py` check exited **0**, comparing all **19 table counts**
and the migration head after `pg_dump`/`pg_restore`. Fixture suites use only
local synthetic databases and reject secret-file overrides. Real provider,
production TLS/deployment/cutover and field-performance checks remain unverified.

## Delivery-hook verification

The first push was rejected by workflow tests because Git's hook-local environment
redirected temporary fixture operations into the calling linked worktree. The
unpublished fixture-only commit and identity changes were restored to the known
implementation state; no remote history or unrelated working files were changed.
The push hook now clears Git's repository-local variables in its verification
subshell and gives that child empty stdin, preserving the incoming references for
protected-ref checks. This follows [Git's hook guidance](https://git-scm.com/docs/githooks).

A regression using real temporary repositories and a linked worktree failed before
the fixes and passed afterwards. It verifies foreign writes, caller commit/file/
identity preservation, command-scoped config isolation, empty verifier stdin and
continued rejection of protected remote refs. The workflow-only gate exited 0
with **105 tests**, **22-skill parity** and shell checks. Security/PR self-review
found no unresolved issue in the fix. The product/provider/browser scope is unchanged.

## Review coverage

Security and PR self-review traced browser input through explicit schemas,
authorization, PostgreSQL transactions/RLS, provider adapters and durable jobs.
It covered hashed sessions/private links, TOTP/recovery replay, CSRF/Origin/proxy
trust, amount snapshots, stock concurrency, late/duplicate/obsolete captures,
refund/dispatch races, encrypted outbox/events, consent/receipts/retries,
uploads/CSV, public publication, generated contracts and container isolation.

Corrected findings include independent capture ownership, uncertain provider
POST recovery, early message receipts, CSV round trips, refund/physical delivery
separation, fixture secret-file overrides, inaccessible older admin results,
production indexing configuration and marketing asset loading. Regression cases
cover financial/security findings; current review has no unresolved actionable
finding within the implemented scope. This is a self-review, not certification.

Design review applies the pinned brand, Taste/Impeccable/Kowalski direction and
Apple accessibility/color/layout/type principles. Public and private desktop/mobile
screenshots were inspected. Browser checks cover 390px, 768px and 1440px, native
forms, keyboard navigation, reduced motion, no-JavaScript public discovery,
axe, and the customer request → staff quote → private cancellation journey.
Other browsers, assistive-technology testing and live Razorpay's hosted UI remain
outside the observed browser evidence.

Technical SEO checks cover the seven preserved entry URLs and six published
outlet detail URLs, with self canonicals, metadata, parsed structured data,
sitemap/robots and resolving internal links. Product metadata is exercised by
the synthetic browser product. Private routes are noindex and authorized;
unpublished policies/products are withheld. The skip-to-content fragment is an
intentional accessibility exception reported by the technical checker.

## Release prerequisites

Approve actual catalog/food/menu/outlet facts, final assets, five policies,
seller/tax data and invoice samples with the business/accountant. Complete the
old-site URL inventory before migration. Configure and exercise Razorpay capture,
refunds/retries and approved Meta templates/consent with the authorized accounts.
Choose the production host and verify its TLS, disk/backup protection, restore,
proxy trust and approved retention procedure. Configure GA4 only after privacy
approval and disabling Enhanced Measurement. Live provider sends/transactions,
production deployment/cutover and field performance are unverified.

The next priority is configured staging acceptance using
[commerce operations](../commerce-operations.md), followed by approved P1 work.

## Delivery record

Initial delivery `2b7acc4` was pushed to `origin/feat/pakodi-mvp`; the finish
helper exited 0 and verified open [PR #7](https://github.com/brollysolutions/patnampakodi-site/pull/7) against
`brollysolutions/patnampakodi-site:main`, matching local/remote head SHA, a clean
worktree and no unpushed commits. Hooks remained enabled. This documentation
follow-up records that observation; final delivery requires fresh remote readback
for its new head. GitHub CI results are reported separately from local checks.
