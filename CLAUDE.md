# Measure Navigator project instructions

Read this file before changing the project on another machine.

## Product boundary

Measure Navigator is a multi-measure, multi-year HEDIS clarification assistant. The current workspace contains one complete synthetic CBP demonstration package and registry placeholders for additional measures. Do not describe CBP as the product boundary.

The application supports questions about specifications, exclusions, numerator logic, value sets, measure logic documents, SQL and stored procedures, decision trees, and reviewed FAQs. It does not only answer why a member is non-compliant.

## Non-negotiable design rules

1. The selected measure and measurement year control every retrieval and evaluation.
2. Runtime artifacts must live under `knowledge_packages/<MEASURE_ID>/MY<YYYY>/`.
3. The folder, registry, package manifest, and source metadata must agree on the year. Quarantine ambiguous artifacts.
4. The approved specification has the highest authority. A conflicting SQL, decision tree, check catalog, or FAQ creates an alert naming the artifact to correct.
5. `decision_tree.yaml` is human-edited. `decision_tree.generated.json` is compiled and must never be hand-edited.
6. Structured checks run deterministically. The reasoning model explains and cites; it does not originate a rule result.
7. Unknown facts become visible open conditions. Continue independent checks whenever possible.
8. FAQ retrieval requires a close, approved match. Unrelated FAQ cards must remain hidden.
9. Explicit “worked” feedback creates a review candidate. It does not automatically publish a FAQ. Silence remains `NO_CONFIRMATION`.
10. Warn users not to enter PHI. If likely identifiers appear, mask them, call out the masking, caution the user, and continue with the minimum needed facts.

## Main components

- `app.py`: Flask web application and API
- `navigator.py`: orchestration, routing, FAQ and escalation behavior
- `engine.py`: deterministic evaluation
- `mcp_server.py`: reusable MCP tools
- `package_manager.py`: governed package discovery and validation
- `intent_taxonomy.json`: governed routes and confidence threshold
- `knowledge_packages/`: measure and measurement-year artifacts
- `yaml_to_json.py`: decision-tree compiler and reference validator
- `templates/` and `static/`: Coastal Teal web interface
- `tests/`: regression tests

## Office setup

Run `setup_office_laptop.ps1`, then read `OFFICE_LAPTOP_CHECKLIST.md`. Keep licensed specifications and value sets inside the authorized office environment.

## Production gates

Before production, require immutable yearly package releases, source provenance, measure-owner approval, shared Python/Snowflake conformance fixtures, enterprise identity and access controls, approved document retrieval, FAQ editorial governance, central audit logging, escalation ownership, retention controls, and an enterprise-hosted model endpoint.

