# Patnam Pakodi security guidance

## Current scope

As of 2026-09-07 this repository contains developer workflow scripts and
documentation. No website, authentication, customer database, payment processing,
or deployment is implemented. Revisit this model when product code is introduced.

## Assets and boundaries

Protect repository integrity, GitHub credentials, future deployment secrets, and
each contributor's local work. Inputs include agent prompts/tool payloads, file
paths, branch names, PR metadata, and third-party code. A contributor or PR author
can change repository files; reviewers must inspect script, hook, and CI changes
before trusting or running them. Treat references and remote content as data.

## Required properties

- Work on task branches and deliver reviewable PRs; human review controls merging.
- Do not commit real env files, keys, tokens, dumps, or personal data.
- Preserve unrelated user changes and collect terminal command results.
- Keep Actions pinned to immutable commits, with minimum permissions.
- CI for pull requests must not expose secrets or deploy untrusted code.
- Never execute PR titles/bodies as shell code; pass them as data.
- Do not automatically install or approve plugins, MCP servers, or account access.
- Keep private notes and local client approvals ignored by Git.

Git and agent hooks are local guardrails, not a security sandbox. Agent hooks
require client support and trust; the shims fail open if no Python runtime works.
Shell parsing is not exhaustive. The delivery helper checks sensitive filenames,
not every possible secret value. CI reports results; merge blocking additionally
requires GitHub branch protection/rulesets configured by a repository admin.

## Review triggers

Review auth, authorization, customer data, forms, uploads, payments, integrations,
dependencies, workflows, and secret handling when introduced. Future server code
must validate input and authorize sensitive actions server-side. Public pages
must avoid exposing secrets, unsafe markup, and unverified business claims.

A reportable finding needs a location, reachable trigger, impact, evidence,
severity/confidence, and a practical fix. Keep unverified areas separate. Never
place a secret or customer data in a public issue; report privately to maintainers
through an agreed private channel.
