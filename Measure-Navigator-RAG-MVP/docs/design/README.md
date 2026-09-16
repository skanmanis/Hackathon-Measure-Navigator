# Measure Navigator Lite RAG — Design Package

## Status

**Design and work-breakdown only. Implementation is not authorized.**

This folder defines a lightweight hackathon design for Measure Navigator. It preserves the existing Coastal Teal UI and chat experience while replacing the YAML-driven runtime with a deterministic conversation controller, SQL-to-English knowledge preparation, document chunking, retrieval, and bounded LLM reasoning.

No application source code, database schema, prompt implementation, ingestion pipeline, infrastructure, or deployment configuration is included in this folder.

## Documents

- `TARGET_SOLUTION_DESIGN.md` — proposed logical design, boundaries, runtime behavior, and design principles
- `WORK_BREAKDOWN_STRUCTURE.md` — build plan, deliverables, dependencies, acceptance gates, and approval checkpoints
- `CLARIFYING_QUESTIONS.md` — decisions required before implementation begins
- `DECISION_LOG.md` — confirmed product decisions and their design consequences

## Approval rule

Implementation may begin only after the product owner approves:

1. Target scope and hackathon success criteria
2. Source hierarchy and supported document types
3. SQL-to-English review expectations
4. Conversation-controller behavior
5. LLM and embedding platform
6. Work-breakdown scope and sequence

## Current planning scope

- Measurement year: MY2026
- Measures: CBP, GSD, KED, EED, and SPC
- SQL dialect: T-SQL stored procedures
- Available sources: measure specifications, stored procedures, Value Set Directory, and Medication List Directory
- Runtime SQL execution: unavailable; the application explains logic but does not query a database
- LLM provider: OpenAI
- Local vector store: ChromaDB
- Indexing: one-time hackathon indexing; production refresh is deferred
- Experience: a new standalone application using the same Coastal Teal UI and chat interaction pattern
- MCP: preferred if it does not put the core demonstration at risk
- SQL-English review: no formal workflow; the product owner will inspect representative output during testing
- Source formats: PDF, Word, Excel, CSV, and T-SQL files
- Source loading: predefined hackathon folder
- FAQ seed: reuse the previously generated hackathon FAQ set
- Delivery target: tomorrow; core web flow takes priority over stretch capabilities
