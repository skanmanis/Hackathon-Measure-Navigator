# Decision Log

## Recorded product-owner decisions

| ID | Decision | Status | Consequence |
|---|---|---|---|
| D-001 | Use MY2026 | Confirmed | All retrieval must filter to MY2026 for the hackathon package |
| D-002 | Support CBP, GSD, KED, EED, and SPC | Confirmed | Source and test coverage must include all five measures |
| D-003 | Stored procedures are T-SQL | Confirmed | Parser assessment and SQL-English logic target T-SQL |
| D-004 | No database connection or SQL execution | Confirmed | The product explains retrieved logic and user-supplied scenarios only |
| D-005 | Sources are specifications, stored procedures, VSD, and MLD | Confirmed | These define the one-time ingestion scope |
| D-006 | No formal English-review workflow for the hackathon | Confirmed | Product owner inspects representative translations during testing |
| D-007 | Use OpenAI | Confirmed in principle | Exact model, endpoint type, and credentials remain to be selected |
| D-008 | Use ChromaDB | Confirmed | Local persisted vector retrieval is the hackathon target |
| D-009 | MCP is preferred if feasible | Confirmed priority | Implement after the web flow unless made mandatory |
| D-010 | Build a new UI | Confirmed | New project should not depend on the old application at runtime |
| D-011 | Use one-time indexing | Confirmed | Incremental and production refresh are deferred |
| D-012 | Reproduce the current UI style in a new application | Confirmed | Preserve Coastal Teal layout and chat behavior without runtime coupling |
| D-013 | Accept PDF, Word, Excel, CSV, and T-SQL sources | Confirmed | Ingestion design must cover these formats |
| D-014 | One primary measure SP may call shared SPs/functions | Confirmed | Build dependency discovery; do not infer missing dependency logic |
| D-015 | Office endpoint may be internal OpenAI | Partially confirmed | Use configurable OpenAI-compatible provider settings |
| D-016 | Reuse the generated hackathon FAQ set | Confirmed | Seed FAQ retrieval below authoritative sources |
| D-017 | Load from a predefined folder | Confirmed | No upload UI on the MVP critical path |
| D-018 | Use a lightweight extensible trace | Confirmed | Show citations, facts, and open condition now; defer scores and diagnostics |
| D-019 | MCP may be deferred | Confirmed | Treat MCP as stretch work |
| D-020 | Delivery target is tomorrow | Confirmed | Enforce the one-day MVP cut |

## Open decisions

The remaining endpoint details can be resolved through configuration during implementation. Implementation remains unauthorized until the product owner explicitly approves the revised WBS.
