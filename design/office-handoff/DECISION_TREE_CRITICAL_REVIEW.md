# Critical review of the existing decision tree

## Overall assessment

The existing YAML decision tree is a useful deterministic prototype. It makes checks inspectable and supports unknown facts as open conditions. Under the revised constraint, it should not remain part of the target architecture because the measure team will provide SQL and stored procedures rather than maintain a second rule representation.

The current tree has 18 nodes and 20 conclusion records. It is primarily a linear CBP scenario evaluator rather than a general multi-measure decision framework.

## Strengths worth preserving

- Human-readable YAML supports measure-reviewer participation.
- Atomic check IDs improve traceability.
- Required facts come from a separate catalog.
- Value-set, date, age, setting, modifier, and threshold checks run deterministically.
- Open conditions can continue through independent checks.
- Compilation validates references before runtime.
- The age gate for frailty plus advanced illness is explicit.

## Material design gaps

### 1. Flat facts do not represent repeated clinical events

The evaluator stores facts in one flat dictionary. It cannot naturally represent multiple diagnoses, claims, readings, care settings, or competing candidate events. Two hypertension diagnoses reuse the same check but require separate event identity. Multiple same-day readings currently need a special hard-coded path outside the tree.

**Design implication:** scenario facts need typed collections with event IDs, dates, source provenance, and relationships. Deterministic aggregation operators should select or combine events before individual checks run.

### 2. Sequential routing does not scale across measures

The tree manually sequences many checks. As measures grow, shared concepts such as hospice, frailty, enrollment, age, and eligible settings will be duplicated. Annual updates will create difficult-to-review branching differences.

**Design implication:** keep the executable logic in governed SQL. Generate a reviewed English explanation with SQL lineage instead of maintaining a parallel YAML rule implementation.

### 3. The tree cannot answer broad document questions

A question such as “What does the specification say about readings from inpatient claims?” may need retrieval and citation but no full scenario traversal. Conversely, a scenario may need both retrieved evidence and deterministic evaluation.

**Design implication:** intent orchestration decides whether to use FAQ retrieval, document retrieval, deterministic evaluation, or a combination. The decision tree is one tool, not the router for every question.

### 4. Intent routing remains keyword-oriented

The current governed taxonomy still scores literal terms. It can misroute paraphrases and ambiguous questions, especially across measures with overlapping terminology.

**Design implication:** use a governed classifier with confidence and allowed routes. Low confidence asks the user to select the intended question type. Store the selected route in the trace.

### 5. Citation provenance is too coarse

Conclusions may carry citations, but every check does not retain the exact specification chunk, SQL block, package version, or value-set release supporting it.

**Design implication:** each check and aggregation result must reference evidence IDs and artifact versions. The final answer inherits citations from the actual evidence graph.

### 6. Compound rules are encoded procedurally

Frailty plus advanced illness uses manual sequencing. More complex measures will require counts, lookback windows, event pairing, temporal constraints, exclusions with exceptions, and set operations.

**Design implication:** introduce explicit rule operators such as `ALL`, `ANY`, `COUNT`, `WITHIN_WINDOW`, `BEFORE`, `AFTER`, `SELECT_LOWEST`, `SELECT_LATEST`, and `EXCEPT`. Their semantics require conformance tests.

### 7. Unknown and missing require clearer semantics

The current evaluator distinguishes missing facts from the literal sentinel `UNKNOWN`. In practice, users can express uncertainty in many ways. Some checks can return conditional results, while a numeric threshold may require values.

**Design implication:** normalize fact states as `KNOWN`, `UNKNOWN`, `NOT_APPLICABLE`, `CONFLICTING`, and `NOT_REQUESTED`. Rule definitions should declare permitted behavior for each state.

### 8. Source conflicts sit outside rule execution

The tree does not compare its result with specification evidence or SQL behavior. A conflict can be manually reported, but conformance is not intrinsic to the package lifecycle.

**Design implication:** package promotion runs shared fixtures against the reference evaluator and production SQL. Runtime comparison detects a discrepancy between retrieved authority and derived logic.

### 9. No explicit rule-version migration model

Year folders exist, but the tree lacks formal change sets, semantic rule versions, generated hashes, and backward reproducibility requirements.

**Design implication:** publish immutable package releases containing source versions, compiled hashes, prompt versions, index snapshot IDs, test results, approver, and effective date.

### 10. Hard-coded direct clarification bypasses the governed tree

The same-day reading scenario is correctly answered by a special Python function, but that creates a second rule location. Future changes could update the specification or YAML without updating this code path.

**Design implication:** represent same-day selection as a governed aggregation rule tied to the specification evidence. The LLM explains the deterministic aggregation result.

## Recommended disposition of the decision tree

Retire YAML as a required production input. Preserve the useful concepts of intermediate results, required inputs, reason codes, open conditions and visible traces through SQL instrumentation and the generated explanation document.

The replacement should provide:

- SQL object and line-level lineage
- Parsed procedure, CTE, join, filter, aggregation and reason-code units
- English explanations reviewed before indexing
- Known behavior for missing, unknown, conflicting and inapplicable inputs
- SQL hashes, repository revisions and explanation versions
- Specification comparison and conflict alerts
- Retrieval triggers for relevant explanation sections
- A complete execution trace when controlled SQL evaluation is available

The LLM should never simulate SQL execution. It explains retrieved, reviewed SQL documentation and any deterministic results returned by an approved SQL interface.
