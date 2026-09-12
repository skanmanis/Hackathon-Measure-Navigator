# Knowledge package contract

The application reads artifacts only from `knowledge_packages/<MEASURE_ID>/MY<YYYY>/` and only when the registry and package manifest agree on the measure and year.

Required production artifacts:

- `manifest.json`
- `specification.pdf` or an approved machine-readable specification extract
- `mld.json`
- `vsd.xlsx` or a governed value-set export
- `decision_tree.yaml`
- `decision_tree.generated.json`
- `check_catalog.json`
- `stored_procedures/`

The specification has the highest authority. If SQL, decision-tree logic, FAQ content, or another derived source disagrees with the specification, the application must retain the specification answer, create a conflict alert, identify the derived artifact that requires correction, and avoid promoting the scenario into the FAQ library.

Artifacts without a verifiable measurement year must not participate in an answer. The ingestion process should derive the year from governed metadata or the source itself and compare it with the folder and manifest. Ambiguous sources enter quarantine for reviewer assignment.
