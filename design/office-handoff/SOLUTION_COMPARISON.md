# Comparison of the two solutions

## Solution A: current deterministic prototype

The current prototype uses SQLite FAQs, token-overlap FAQ matching, keyword-based intent routing, a compiled YAML decision tree, a Python check evaluator, simple local document keyword search, and fixed Python answer templates.

## Solution B: proposed governed hybrid solution

The proposed solution replaces YAML authoring with governed SQL ingestion. It generates a reviewed English code-explanation document from SQL, chunks and indexes that document alongside specifications, and adds hybrid retrieval, reranking, evidence-bound LLM reasoning, citation validation, governed memory, and production package governance.

## Comparison

| Dimension | Solution A: current prototype | Solution B: proposed architecture |
|---|---|---|
| Primary strength | Simple, inspectable deterministic demonstration | Complete clarification platform across structured and unstructured evidence |
| FAQ retrieval | Token overlap in SQLite | Metadata-filtered hybrid retrieval with semantic similarity and lexical matching |
| Document retrieval | Reads a few local files and ranks shared words | Parsed and chunked repository with vector index, lexical index, reranking and citations |
| Measurement-year safety | Package folder and manifest checks | Same controls plus indexed metadata filtering, immutable index snapshots and quarantine |
| Decision logic | Linear YAML tree and flat facts | Production SQL remains executable; reviewed SQL explanations support retrieval and reasoning |
| Multiple readings or events | Requires special-case code | First-class event collections and governed selection rules |
| LLM | Not connected | Bounded explanation and synthesis after retrieval and deterministic checks |
| Prompts | UI fact questions only | Versioned system, task, context and output-contract prompts |
| Citations | Static conclusion references | Chunk-level citations inherited from evidence and check provenance |
| Conversation memory | Stored session and interactions, not supplied to a model | Bounded session summary with measure/year and fact state |
| Learning memory | Confirmed outcomes can enter an FAQ review state | Separate case, candidate-learning and approved-FAQ stores with semantic retrieval |
| Conflict handling | Manual or keyword-triggered alert | Automated authority comparison, grounded response and routed remediation |
| Evaluation | Unit tests for prototype behavior | Retrieval, rule, LLM-grounding, workflow and privacy evaluation suites |
| Operational complexity | Low | Moderate to high |
| Infrastructure cost | Low | Higher due to indexing, embeddings, model use and governance |
| Best use | Hackathon proof of deterministic behavior | Office pilot and production path after governance approval |

## Trade-offs

### Reasons to retain Solution A elements

- Deterministic checks remain essential for calculable outcomes.
- Atomic checks and visible traces demonstrate the value of inspectable intermediate results.
- A small FAQ database provides fast responses and downloadable guidance.
- The current trace concepts provide a useful foundation.

### Reasons Solution A alone is insufficient

- It cannot reliably retrieve semantically similar specification content.
- It cannot synthesize evidence across several documents.
- Its decision tree duplicates logic already implemented in SQL and cannot naturally model repeated events and aggregation.
- It has no real LLM reasoning or prompt governance.
- Its stored questions do not become usable, governed memory without additional retrieval and review design.

### Risks introduced by Solution B

- Retrieval can return an incorrect year or authority unless metadata filtering is mandatory.
- Embeddings can obscure exact-code matches unless hybrid retrieval is used.
- The LLM can overstate evidence unless output validation and citation checks run.
- Conversation memory can create privacy and stale-context risks.
- A second evaluator can drift from Snowflake without shared conformance fixtures.
- Operational ownership becomes more complex.

## Recommendation

Proceed with Solution B as a layered extension rather than a replacement:

```text
Governed executable SQL
        +
Reviewed SQL-to-English explanations and hybrid retrieval
        +
Evidence-bound LLM explanation
        +
Separated and reviewed memory
        +
Package, evaluation and escalation governance
```

This preserves the strongest property of the existing prototype: the LLM does not decide measure logic. It adds the missing capabilities needed to search documents, reason across evidence, preserve useful context, and support multiple measures at production scale.
