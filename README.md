# Measure Navigator

Measure Navigator is a synthetic-data HEDIS clarification application designed for multiple measures and measurement years. The included CBP package demonstrates the contract; the registry also reserves packages for additional hackathon measures.

The portable handoff includes `ARCHITECTURE_AND_SOLUTION.md`, `TECHNOLOGY_STACK.md`, `OFFICE_LAPTOP_CHECKLIST.md`, and a Coastal Teal architecture deck under `output/`.

The application checks approved FAQs first, then runs a deterministic decision tree against only the scenario facts supplied by the user. A reasoning model may explain and cite computed results, but it does not originate rule outcomes.

The specification is authoritative. Conflicts in SQL, decision trees, or FAQ content create escalation alerts and identify the derived artifact that requires correction.

## Knowledge package

Production artifacts belong under `knowledge_packages/<MEASURE_ID>/MY<YYYY>/`. See `knowledge_packages/PACKAGE_CONTRACT.md` and `OFFICE_LAPTOP_HANDOFF.md`.

- `decision_tree.yaml`: human-edited routing source of truth
- `yaml_to_json.py`: validates routes and check references, then compiles JSON
- `decision_tree.generated.json`: runtime artifact; never edit directly
- `check_catalog.json`: atomic checks, required facts, prompts, and unknown guidance
- `value_sets.synthetic.json`: small synthetic value-set reconstruction for local demonstration
- `evaluate_check.sql`: Snowflake production-target evaluator

For an annual update, copy the measure package to the new measurement year, edit the YAML and knowledge sources, compile, then run regression tests. Do not overwrite a prior measurement year in place.

## Run locally

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python yaml_to_json.py
python app.py
```

Open `http://127.0.0.1:5001`.

Always open the application through that URL after starting Flask. Do not open `templates/index.html` directly: it is a server-side template, so its styles, scripts, APIs, and FAQ downloads require the running application.

The Navigator includes a live relevant-FAQ panel. The `/faqs` page provides a searchable approved FAQ library with Markdown and CSV downloads.

## MCP server

```powershell
.\.venv\Scripts\python.exe mcp_server.py
```

Tools include FAQ search, required-fact discovery, value-set lookup, atomic check evaluation, specification search, and outcome recording.

## Learning states

- `CONFIRMED_WORKED`: increase approved FAQ usefulness, or create a review candidate for a new resolved scenario
- `CONFIRMED_UNRESOLVED`: retain for document or reviewer follow-up
- `NO_CONFIRMATION`: default state; silence never counts as success
- `REVIEWED`: reserved for reviewer-approved learning

## Important limits

This prototype uses synthetic measure logic and value-set groupings. It provides educational clarification, not an official HEDIS determination. Every page cautions against entering PHI. When likely identifiers are entered, the application masks and calls them out before continuing.
