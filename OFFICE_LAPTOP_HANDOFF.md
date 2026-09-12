# Office laptop handoff

## Copy

Copy and extract `Measure-Navigator-Office-Laptop-Package-v3.zip`. The bundle excludes local environments and private build folders. Run `setup_office_laptop.ps1` to recreate the tested Python environment, compile the YAML, and execute the regression tests.

Review `ARCHITECTURE_AND_SOLUTION.md`, `TECHNOLOGY_STACK.md`, and `OFFICE_LAPTOP_CHECKLIST.md` before adding office-only content.

## Add governed measure content

Place every artifact under:

`knowledge_packages/<MEASURE_ID>/MY<YYYY>/`

Update `knowledge_packages/registry.json` and the package `manifest.json`. The folder, registry, manifest, and document metadata must agree on the measurement year. The application rejects incomplete packages.

Recommended contents:

- `specification.pdf`
- `mld.json`
- `vsd.xlsx`
- `decision_tree.yaml`
- `decision_tree.generated.json`
- `check_catalog.json`
- `stored_procedures/`
- `manifest.json`

## Source authority

The specification wins. If SQL, the decision tree, FAQ content, or another derived artifact disagrees, keep the specification-based answer and create an escalation. Correct the derived artifact and rerun conformance tests before closing the alert.

## Validate

1. Run `python yaml_to_json.py` within the applicable package build workflow.
2. Run `python -m unittest discover -s tests -v`.
3. Add shared conformance fixtures for each real measure and execute them against Python and Snowflake.
4. Start the app with `python app.py` and open the printed localhost URL.
5. Confirm measure and year selection, FAQ matching, answer traces, open conditions, citations, and conflict alerts.

## Licensed content

Keep licensed NCQA specifications and value sets inside the authorized office environment. Do not copy them back into this synthetic workspace.
