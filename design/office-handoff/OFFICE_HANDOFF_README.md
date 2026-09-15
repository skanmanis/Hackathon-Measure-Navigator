# Office-laptop design and coding handoff

## Start here

1. Copy this design-only handoff package to an approved office location.
2. Place it beside, not inside, repositories that contain licensed specifications or proprietary SQL unless local policy permits otherwise.
3. Open `OFFICE_CODEX_MASTER_PROMPT.md`.
4. Copy the prompt into a new Codex task on the office laptop.
5. Point Codex to the approved project and document locations.
6. Complete `OFFICE_ARTIFACT_INVENTORY_TEMPLATE.md` during discovery.
7. Review the proposed architecture and decisions with Codex.
8. Confirm the design before authorizing implementation.

## Supporting design documents

- `SOLUTION_ARCHITECTURE.md`
- `SQL_TO_ENGLISH_RAG_DESIGN.md`
- `DECISION_TREE_CRITICAL_REVIEW.md`
- `SOLUTION_COMPARISON.md`
- `DESIGN_DECISIONS_TO_CONFIRM.md`
- `OFFICE_IMPLEMENTATION_GATES.md`

## Important constraints

- Do not introduce YAML decision trees.
- Keep governed SQL as the executable implementation.
- Treat generated English SQL explanations as reviewed derived artifacts.
- Apply measure and measurement-year filters before retrieval.
- Keep licensed material and proprietary SQL inside the office environment.
- Do not include PHI in prompts, source control, test fixtures, or demonstration screenshots.
- Do not commit credentials or local audit databases.

## Recommended Git workflow

Use an approved office repository if one becomes available. Create a design branch first, commit reviewed architecture changes separately, and implement each approved phase on a dedicated branch with its tests.

