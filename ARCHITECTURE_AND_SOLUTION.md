# Measure Navigator reference architecture and solution flow

## Purpose

Measure Navigator clarifies HEDIS measure requirements across multiple measures and measurement years. Questions may cover eligibility, exclusions, numerator evidence, calculation rules, value sets, SQL behavior, or implementation differences. The application checks approved FAQs first, uses governed deterministic logic for scenario evaluation, retrieves source evidence, and uses a reasoning model only to explain results already grounded in the package.

CBP is the most complete synthetic demonstration package. The architecture supports additional measures through the same package contract.

## Runtime architecture

```mermaid
flowchart LR
    U[User] --> UI[Web UI]
    UI --> API[Flask orchestration API]
    MCP[MCP clients] --> TOOLS[MCP tool server]
    TOOLS --> API
    API --> SAFE[Identifier detection and masking]
    SAFE --> PKG[Measure and year package resolver]
    PKG --> ROUTE[Governed intent taxonomy and confidence gate]
    ROUTE --> FAQ[(Approved FAQ database)]
    ROUTE --> TREE[Compiled decision tree]
    TREE --> CHECK[Deterministic check evaluator]
    CHECK --> VSD[Governed value sets]
    CHECK --> SQL[Snowflake procedures in production]
    ROUTE --> DOCS[Specification, MLD, VSD, SQL and supporting document retrieval]
    FAQ --> ANSWER[Evidence composer]
    CHECK --> ANSWER
    DOCS --> ANSWER
    ANSWER --> LLM[Optional reasoning model for explanation]
    LLM --> TRACE[Answer, citations and visible trace]
    TRACE --> UI
    TRACE --> LEARN[(Feedback and review queue)]
    TRACE --> ALERT[(Conflict and escalation queue)]
```

## User solution flow

```mermaid
flowchart TD
    A[Select measure and measurement year] --> B[Enter clarification question]
    B --> C[Detect and mask likely identifiers]
    C --> D[Classify intent and calculate confidence]
    D --> E{Close approved FAQ match?}
    E -- Yes --> F[Show relevant FAQ and its governed sources]
    E -- No --> G[Retrieve applicable source sections]
    F --> H{User needs scenario evaluation?}
    H -- No --> N[Present answer and trace]
    H -- Yes --> I[Ask only for facts required by the active check]
    G --> I
    I --> J[Run deterministic decision tree and value set checks]
    J --> K{Unknown facts?}
    K -- Yes --> L[Continue independent checks and retain open conditions]
    K -- No --> M[Assemble computed outcome]
    L --> M
    M --> O{Specification conflicts with derived artifact?}
    O -- Yes --> P[Use specification answer and create correction alert]
    O -- No --> Q[Compose cited explanation]
    P --> Q
    Q --> N
    N --> R{Explicit user feedback?}
    R -- Worked --> S[Store redacted review candidate]
    R -- Unresolved --> T[Escalate with evidence trace]
    R -- No confirmation --> V[Retain NO_CONFIRMATION and do not promote]
```

## Annual package lifecycle

```mermaid
flowchart LR
    SRC[Approved MY source artifacts] --> FOLDER[knowledge_packages / measure / MY year]
    FOLDER --> VALIDATE[Validate year, provenance and manifest]
    VALIDATE -->|Ambiguous| QUAR[Quarantine for reviewer]
    VALIDATE -->|Valid| YAML[Reviewer edits decision_tree.yaml]
    YAML --> BUILD[YAML to JSON compiler]
    BUILD --> TEST[Schema, route and shared conformance tests]
    TEST -->|Fail| FIX[Correct derived artifact]
    FIX --> YAML
    TEST -->|Pass| APPROVE[Measure owner approval]
    APPROVE --> RELEASE[Immutable versioned package]
    RELEASE --> RUNTIME[Runtime registry]
```

## Source authority

1. Approved measure specification
2. Governed MLD and value-set sources
3. Validated SQL implementation
4. Compiled decision tree and check catalog
5. Reviewed FAQ content

When a derived source disagrees with the specification, the application keeps the specification-grounded answer, marks the response with a conflict, and creates an alert naming the artifact that needs correction. FAQ content never overrides measure logic.

## Visible answer trace

Every resolved response should expose a compact trace containing the selected measure and year, detected intent and confidence, FAQ match decision, package version, checks executed, facts used, open conditions, cited source sections, source authority, and any escalation ID. The interface keeps this information behind the clickable **View audit trace** control so it remains available without cluttering the conversation.

## Implemented prototype and production target

| Capability | Portable prototype | Production target |
|---|---|---|
| Web interface | Flask, HTML, CSS and JavaScript | Enterprise web hosting and identity integration |
| Measure packages | Synthetic JSON, YAML and SQL assets | Licensed, immutable, approved yearly packages |
| FAQ store | Local SQLite | Governed relational store with editorial workflow |
| Rule evaluation | Python evaluator | Snowflake evaluator with shared conformance suite |
| Document retrieval | Local synthetic corpus | Authorized repository and vector or hybrid search |
| Explanation model | Optional integration point | Enterprise-hosted endpoint with audit controls |
| Identifier handling | Warning plus prototype masking | Policy-approved detection, encryption, retention and access controls |
| Escalation | Local conflict records | Workflow integration with ownership and service levels |

