# Office Codex master prompt

Copy everything below the separator into a new Codex task on the office laptop. Attach or point Codex to the approved project folder that contains the actual specifications, MLDs, VSDs, SQL, stored procedures, FAQs, and any existing application code.

---

You are helping me design and implement **Measure Navigator**, a multi-measure, multi-measurement-year HEDIS clarification assistant for a hackathon and possible office pilot.

## Start in discovery mode

Do not write or change application code immediately. First inspect the available project instructions, repository structure, approved architecture documents, and actual office artifacts. Identify missing information and conflicts. Produce a concise current-state assessment and proposed implementation plan for my approval.

Do not read or use files outside the project and authorized document locations I provide. Do not copy licensed specifications, value sets, clinical data, credentials, or internal SQL outside the approved office environment.

## Product scope

The application must support questions across multiple HEDIS measures and measurement years. Questions can concern specifications, denominator eligibility, exclusions, numerator logic, multiple readings or events, value sets, MLDs, SQL behavior, stored procedures, implementation defects, FAQs, and prior reviewed resolutions.

CBP is one available scenario, not the product boundary.

## Confirmed architecture change

Do not require or introduce YAML decision trees. Measure teams will provide SQL and stored procedures.

The target design is:

1. Ingest governed specification, MLD, VSD, SQL, stored-procedure, FAQ, and supporting documents.
2. Validate measure, measurement year, document version, approval status, access classification, and source authority.
3. Quarantine incomplete, ambiguous, or unversioned artifacts.
4. Parse SQL into procedures, CTEs, joins, filters, CASE logic, date windows, aggregations, ranking, intermediate datasets, outputs, and reason-code assignments.
5. Convert parsed SQL units into a versioned English code-explanation document.
6. Preserve exact lineage to SQL object, repository revision, file, line range, and source hash.
7. Require technical and measure-owner review before treating the English explanation as approved retrieval content.
8. Use structure-aware chunking for specifications and SQL explanations.
9. Build hybrid retrieval using mandatory metadata filters, lexical search, vector similarity, reranking, and neighboring-context expansion.
10. Retrieve approved FAQs first when a close match exists. Hide the FAQ panel when no close approved match exists.
11. Use an enterprise-hosted LLM only after evidence retrieval and any approved deterministic SQL evaluation.
12. Validate the LLM response for grounding, citations, measurement year, open conditions, and source-authority compliance.
13. Return a visible, clickable audit trace.
14. Maintain separate session, resolved-case, candidate-learning, approved-FAQ, audit, and escalation stores.

## Source authority

Use this default precedence unless the inspected office governance states otherwise:

1. Approved measure specification
2. Governed MLD and VSD
3. Original validated SQL and stored procedures
4. Reviewed SQL-to-English explanation
5. Approved FAQ
6. Prior resolved cases

The specification controls when it disagrees with SQL. Report the difference as an implementation defect, identify the SQL object and lineage, and create an escalation recommendation. Do not silently reconcile the conflict.

Clarify whether the VSD has equal authority to the specification for code-set membership.

## SQL-to-English requirements

Generate explanations by logical SQL unit, not as one narrative for an entire procedure. Preserve:

- Object and procedure names
- Tables, columns, aliases, joins, and filters
- Boolean grouping and operator direction
- Date boundaries and lookback windows
- Null behavior
- Value-set references
- Deduplication and ranking
- Multiple-event selection
- Aggregations and thresholds
- Temporary and intermediate datasets
- Final outputs and reason codes
- Known limitations or unsupported syntax

Every explanation unit must include SQL lineage and an approval state. Generated English is a derived artifact and must never outrank the original SQL or specification.

## Retrieval requirements

Apply access, measure, year, version, document type, and approval filters before similarity search. Combine lexical and vector retrieval. Exact procedure names, reason codes, value-set identifiers, medical codes, column names, and HEDIS abbreviations require strong lexical weighting.

Retrieved chunks must contain stable citation identifiers and enough neighboring context to retain qualifications and exceptions.

Do not send entire specifications or stored procedures to the LLM when a small evidence set answers the question.

## LLM and prompt requirements

Create separately versioned prompts for:

- SQL-to-English generation
- Question intent classification
- Evidence-based clarification
- Specification-versus-SQL comparison
- Answer-grounding and citation validation
- Conversation summarization

The question-answering model may explain, synthesize, compare, and ask a bounded follow-up question. It may not invent measure rules, simulate SQL execution, override deterministic results, erase open conditions, promote unreviewed learning, or cite unretrieved sources.

The model input should include only the masked question, authorized session context, measure and year, retrieved evidence, approved FAQ matches, deterministic outputs when available, source precedence, conflicts, and the requested output contract.

## Memory requirements

Keep these stores separate:

- Session memory: masked turns, selected scope, facts, and open conditions for the active conversation
- Resolved-case memory: generalized prior investigations labeled non-authoritative
- Candidate learning: explicitly confirmed worked or unresolved scenarios awaiting review
- Approved FAQ memory: reviewer-approved guidance with current citations
- Audit memory: prompt version, evidence IDs, retrieval scores, SQL results, model output, validator result, and escalation IDs

Silence remains `NO_CONFIRMATION`. A “worked” response creates a review candidate, not an automatically approved FAQ.

## Privacy behavior

Every user-facing page must display a concise caution not to enter PHI. If likely identifiers are entered, mask them, state what categories were masked, caution the user not to provide additional PHI, and continue with the minimum required facts.

Treat prototype masking as a secondary safeguard rather than the product’s headline feature. Confirm office requirements for detection, encryption, access, retention, logging, and deletion.

## User experience

Use the Coastal Teal visual direction: deep navy primary actions, teal evidence states, pale aqua supporting surfaces, consistent typography, and restrained density.

The primary workflow must include:

- Measure and measurement-year selection
- Question input
- Relevant FAQ panel shown only for close matches
- Source-grounded response
- Clickable audit trace
- Cited specification and SQL-explanation sections
- Open-condition display
- Conflict and escalation display
- FAQ library search and download
- Explicit worked or unresolved feedback

## Evaluation requirements

Design separate evaluation sets for:

- Retrieval recall, reranking, citation relevance, and year-filter violations
- SQL parser coverage and translation fidelity
- Boolean logic, null handling, dates, joins, ranking, and aggregation preservation
- Specification-versus-SQL conflict detection
- LLM unsupported claims, citation completeness, and open-condition preservation
- FAQ match precision so unrelated FAQs remain hidden
- Memory isolation and stale-context prevention
- PHI masking and retention behavior

Do not claim performance, accuracy, speed, or savings without measured evidence and a named test set.

## Initial work sequence

Perform these steps in order:

1. Read all repository instruction files completely.
2. Inventory the office artifacts without exposing their contents outside the approved environment.
3. Map each artifact to measure, measurement year, source type, version, owner, authority, and approval state.
4. Inspect representative SQL and identify dialect, stored-procedure language, reason-code behavior, intermediate outputs, dynamic SQL, and unsupported constructs.
5. Determine whether the SQL supports controlled scenario execution or only explanation and retrieval.
6. Identify approved retrieval, embedding, LLM, identity, audit, and escalation platforms available in the office environment.
7. Compare the inspected environment with the supplied architecture.
8. Produce a gap analysis, proposed physical architecture, data-flow diagram, security boundary, implementation phases, and test strategy.
9. List decisions requiring my confirmation.
10. Stop and wait for my approval before creating or changing implementation code.

After I approve the design and implementation plan, work incrementally. Preserve existing files, use branches, add tests with each capability, and never place real secrets or licensed content in commits unless the repository and users are authorized.

## First response format

Return:

1. Current-state summary
2. Artifact inventory by measure and measurement year
3. SQL capability assessment
4. Available platform assessment
5. Differences from the target architecture
6. Recommended physical architecture
7. Major risks and mitigations
8. Phased implementation plan
9. Decisions requiring my confirmation

Do not implement yet.

---

