# Office laptop migration checklist

## Copy and verify

1. Copy the complete ZIP into an approved office location.
2. Extract it without flattening the folder structure.
3. Read `README.md`, `ARCHITECTURE_AND_SOLUTION.md`, and `knowledge_packages/PACKAGE_CONTRACT.md`.
4. Run `setup_office_laptop.ps1` from PowerShell.
5. Start the website and MCP server using the commands printed by the setup script.

## Add authorized measure content

1. Create `knowledge_packages/<MEASURE_ID>/MY<YYYY>/` for each measure year.
2. Add the specification, MLD, VSD, SQL or stored procedures, check catalog, and decision-tree YAML.
3. Update the package manifest and central registry.
4. Confirm the folder, manifest, source metadata, and selected measurement year agree.
5. Keep ambiguous or unversioned artifacts out of runtime search until a reviewer assigns the year.
6. Compile YAML to JSON. Never hand-edit generated JSON.
7. Add conformance fixtures that cover the real measure logic.
8. Run the fixtures against Python and Snowflake before approving the package.

## Configure integrations

- Keep licensed NCQA content only inside the authorized office environment.
- Use an enterprise-hosted model endpoint and approved secret storage.
- Configure the document repository, audit destination, and escalation workflow.
- Confirm identity, authorization, retention, and identifier-detection policies.

## Demo readiness

- Measure and measurement-year selection work.
- An unrelated FAQ does not appear as a match.
- A direct specification question cites the correct section.
- Unknown facts remain visible while independent checks continue.
- The audit trace shows routing, checks, sources, open conditions, and authority.
- A specification-versus-SQL conflict uses the specification and creates an alert.
- “Worked” feedback creates a review candidate rather than an automatically approved FAQ.
- No response confirmation remains `NO_CONFIRMATION`.

