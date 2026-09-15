# Office implementation gates

These gates keep the office implementation aligned with the approved design.

## Gate 1: architecture approval

Required decisions:

- Retrieval platform
- Embedding and reasoning-model endpoints
- Document repositories
- Source-authority policy
- SQL execution mode
- Memory and retention policy
- Identity and access model
- Escalation destination

No production-oriented implementation begins before this gate.

## Gate 2: representative artifact assessment

Required evidence:

- At least one representative specification
- At least one MLD and VSD
- Representative SQL or stored procedure for each major SQL pattern
- Existing FAQ sample
- Confirmed measurement-year metadata
- SQL parser coverage report

Exit decision: approve the SQL-to-English document format and chunk metadata.

## Gate 3: retrieval proof

Required evidence:

- Approved source ingestion
- Structure-aware chunks with stable citations
- Mandatory measure and year filtering
- Lexical and vector retrieval
- Reranking
- Retrieval evaluation set
- Demonstrated rejection of wrong-year and unrelated FAQ results

Exit decision: approve retrieval quality before adding LLM-generated answers.

## Gate 4: LLM explanation proof

Required evidence:

- Versioned prompt templates
- Evidence-only model context
- Citation validator
- Specification authority enforcement
- Open-condition preservation
- Unsupported-claim evaluation
- Conflict response and escalation behavior

Exit decision: approve the model for a controlled hackathon demonstration.

## Gate 5: memory and learning proof

Required evidence:

- Session isolation
- Bounded conversation summaries
- Non-authoritative resolved-case retrieval
- Candidate-learning review queue
- Approved FAQ publication workflow
- `NO_CONFIRMATION` behavior
- Retention and deletion tests

## Gate 6: office pilot readiness

Required evidence:

- Identity and role enforcement
- Authorized document access during retrieval
- Secret management
- Central audit logging
- Operational monitoring
- Incident and escalation ownership
- Package and index versioning
- Rollback procedure
- Measure-owner and security approval

