# Technology stack

## Tested portable baseline

| Layer | Technology | Tested version | Role |
|---|---|---:|---|
| Runtime | Python | 3.12.14 | Application, MCP server, package compiler and tests |
| Web API | Flask | 3.1.3 | UI routes and JSON endpoints |
| MCP | MCP Python SDK | 1.30.0 | Reusable Measure Navigator tools over stdio |
| Configuration | python-dotenv | 1.2.3 | Local environment configuration |
| YAML compiler | PyYAML | 6.0.3 | English-like decision-tree authoring and validated JSON generation |
| Model client | OpenAI Python SDK | 2.54.0 | Optional enterprise model integration point |
| Local persistence | SQLite | Python standard library | FAQ, session, feedback and escalation records |
| Browser client | HTML5, CSS3, JavaScript | Browser-native | Coastal Teal user interface |
| Rule platform | Snowflake SQL and JavaScript procedures | Account-managed | Production deterministic evaluation target |
| Tests | unittest | Python standard library | Routing, masking, open-condition, trace and package tests |

`requirements-office.txt` pins the tested Python package versions. `requirements.txt` retains compatible version ranges for continued development.

## MCP tools

- `ask_hedis_question`
- `lookup_value_set`
- `get_exclusion_rules`
- `get_required_facts`
- `evaluate_check`
- `search_spec_docs`
- `list_approved_faqs`
- `record_resolution`
- `list_measure_packages`
- `report_source_conflict`

## Production additions

- Enterprise identity and role-based authorization
- Approved document repository connector
- Managed secret storage
- Central audit logging and observability
- CI pipeline for YAML compilation and Python/Snowflake conformance
- Editorial review workflow for FAQ promotion
- Issue or workflow integration for source conflicts
- Policy-approved identifier detection and data-retention controls

