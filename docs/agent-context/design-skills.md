# Design skills: selection and sources

Reviewed 2026-09-08 after the user requested Taste, Apple Design, and research
into established additions. Counts below are repository stars observed through
the GitHub API on that date, not per-skill usage or a measure of design quality.

| Candidate | Repository stars | Decision and fit |
| --- | ---: | --- |
| [Taste](https://github.com/Leonxlnx/taste-skill) | 85,223 | Installed as `design-taste-frontend`; primary reference for public marketing pages and redesigns. |
| [Apple Design](https://github.com/dickwu/apple-design-skill) | 339 | Requested installation completed locally as `apple-design`; HIG review reference. Native app conventions need adaptation for the web. |
| [Anthropic Frontend Design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | 175,084 | Added as `frontend-design`; concise alternative for interfaces outside Taste's landing-page scope. Apache-2.0 license bundled. |
| [Vercel Web Design Guidelines](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) | 30,950 | Best next candidate for an objective web review pass. Deferred: its current entrypoint fetches mutable rules on every review, contrary to our pinned-reference policy. Evaluate a licensed, pinned guideline snapshot before integrating. |
| [Impeccable](https://github.com/pbakaus/impeccable) | 66,393 | Strong design/refinement toolkit. Deferred because its broad command set overlaps our design-create/review chain; assess when an actual site needs a repeated refinement workflow. |
| [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 125,890 | Broad style and design-system exploration. Deferred until stack and product scope are known; its larger data/script footprint adds little to today's scaffolding. |

These decisions are project-fit judgments based on the upstream instructions and
READMEs. They are not comparative output-quality benchmarks. No website exists
yet, so browser-based design evaluations have not been run.

## How to use the installed skills

Keep `design-reference` or `design-create` as the entry workflow. Select **one**
supplementary visual reference: Taste for a marketing page, or Anthropic for a
different interface. Do not load both complete aesthetic rule sets automatically.
Run `design-review`, the relevant `apple-design` chapters when available, then
`seo-review`, `review-pr`, and `ship` for an implementation task.

The user's brief and approved project design always win. Skills cannot pick the
website stack, invent business facts, require dark mode or animation, install
packages, replace brand assets, or waive performance/accessibility/SEO gates.
Apple HIG is a second opinion; native app chrome, gestures, and platform target
sizes are not automatically web requirements. Existing approval in the session
does not need to be requested again.

## Pinned installations

| Skill | Revision and source path | Location and license handling |
| --- | --- | --- |
| Taste | [`ccbc15639c97057cbfcf32ecebc38ef716e4bb37`](https://github.com/Leonxlnx/taste-skill/tree/ccbc15639c97057cbfcf32ecebc38ef716e4bb37/skills/taste-skill) | `.agents/skills/design-taste-frontend` and identical `.claude/skills` copy. MIT license retained. The upstream entrypoint is preserved as `references/upstream.md`; a small project entrypoint selects relevant sections. |
| Anthropic Frontend Design | [`41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f`](https://github.com/anthropics/skills/tree/41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f/skills/frontend-design) | `.agents/skills/frontend-design` and identical `.claude/skills` copy. Upstream entrypoint and Apache-2.0 license preserved. |
| Apple Design | [`d0bac1e765a27a696839e62962e36330ce72f0b7`](https://github.com/dickwu/apple-design-skill/tree/d0bac1e765a27a696839e62962e36330ce72f0b7) | User-local `~/.codex/skills/apple-design` and `~/.claude/skills/apple-design`. Entry point and bundled references copied; local `SOURCE.json` records revision and file hashes. No license file was present in this revision, so its text is not redistributed in this repository. |

The built-in skill installer downloaded pinned snapshots for inspection. Only
Markdown references and licenses were installed; no upstream shell scripts,
package installers, hooks, MCP servers, plugins, telemetry, or account settings
were executed or enabled. Taste's additional style variants were not installed.

Other contributors receive the two shared skills when pulling this PR after
merge. They may ask their agent to install Apple Design at the pinned revision
locally. Setup does not download optional skills automatically. Newly installed
Codex skills are available on the next turn; client hook changes still require
the client's normal reload/trust process.

For updates, inspect the exact new revision, references, executable files and
license; preserve attribution, reconcile project constraints, update both shared
trees and this record, then run skill validation and the workflow gate. Do not
follow a mutable upstream branch during an ordinary design review.
