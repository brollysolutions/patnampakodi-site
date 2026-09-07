---
name: contract-sync
description: Regenerate the API contract and its typed client after a server schema or route change, then reconcile every consumer. Use whenever an endpoint, request/response schema, enum, or auth requirement changes.
---

# Contract Sync

Apply only to layers that exist. This repository has no application yet; discover
and document the chosen stack before using the examples below. Contract generation
and migration commands apply only when configured; do not create a stack to satisfy
this procedure. Use the actual verification commands recorded in AGENTS.md.

1. Change the server schemas and routes first. Generated artifacts are outputs, never inputs; never hand-edit the OpenAPI document or the generated client types.
2. Regenerate from the repository root in order: `./scripts/generate-openapi.sh`, then `./scripts/generate-client.sh`.
3. Review the regenerated diff for compatibility before adapting consumers. Removals, nullability changes, enum changes, auth requirement changes, and response-shape changes are potentially breaking; say so explicitly rather than absorbing them silently.
4. Adapt every consumer the diff affects. Search for callers instead of assuming the type-error surface is complete.
5. Commit the server change, the contract document, the generated client, the consumer adaptation, and the tests together as one compatibility change.
6. Finish by re-running generation in the same environment used for verification and confirming a clean `git diff --exit-code` on the generated directories. Drift there means the committed contract does not match the code.
