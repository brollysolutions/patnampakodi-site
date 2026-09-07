---
name: backend-change
description: Implement a server-side change — route, service, schema, model, migration, or background job — with authorization and data isolation intact. Use for any API, database, or job work, including as a sub-step of work-feature or systematic-debug.
---

# Backend Change

Apply only to layers that exist. This repository has no application yet; discover
and document the chosen stack before using the examples below. Contract generation
and migration commands apply only when configured; do not create a stack to satisfy
this procedure. Use the actual verification commands recorded in AGENTS.md.

1. Trace the full path before editing: route (`app/api/v1`), auth dependency (`app/core/deps.py`), service (`app/services`), schema (`app/schemas`), model (`app/models`), session/RLS context (`app/db/session.py`), migration history, and the closest API/RLS tests. Inspect the client and committed contract when the endpoint has a consumer.
2. Keep route handlers thin and async. Business rules, transactions, and retry behavior belong in services.
3. Derive authorization context from the server session. Never substitute client-supplied roles, tenant identifiers, or object IDs for server-derived context, and use the existing request-scoped database/RLS context rather than a new connection path.
4. Use explicit request/response schemas. Never return raw model objects, exception text, storage keys, or fields the caller is not entitled to.
5. New or changed tables require grants, RLS enablement and policies, indexes and constraints where appropriate, and rollback-aware migration logic. Migrations are additive and immutable after merge; preserve exactly one head.
6. Test both the positive path and the forbidden/cross-tenant path for any authorization, role, or RLS change. A passing positive test alone does not characterize an authorization change.
7. When the change alters the API surface, invoke `$contract-sync` before finishing.
8. Run targeted tests while iterating, then the backend gate from `AGENTS.md`: lint, format check, and the full suite. Confirm a single migration head.
9. Invoke `$security-review` when the change touches auth, OTP, uploads, payments, webhooks, account deletion, retention, or audit logs.
