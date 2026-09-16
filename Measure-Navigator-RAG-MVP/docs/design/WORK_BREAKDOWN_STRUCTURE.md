# Work Breakdown Structure

## Status and authorization boundary

This is a proposed work breakdown. It does not authorize implementation.

No code, schema, prompt, ingestion pipeline, vector database, package installation, infrastructure, or changes to the current Measure Navigator application should be created until the product owner approves this WBS and resolves the blocking questions.

## Planning assumptions

- A new UI will be built using the current Measure Navigator chat experience as a product reference.
- The build is intended for a hackathon demonstration on an office laptop.
- YAML will not be used.
- Synthetic or approved non-production artifacts will be used during development.
- The system supports more than one measure and requires explicit measurement-year context.
- The specification is authoritative.
- SQL-to-English content is derived material and retains exact source lineage.
- The LLM provides language understanding and explanation; deterministic services own workflow state.
- The hackathon scope is MY2026 for CBP, GSD, KED, EED, and SPC.
- SQL inputs are T-SQL stored procedures and will not be executed because no database connection is available.
- Source documents include measure specifications, Value Set Directory, and Medication List Directory.
- OpenAI is the selected LLM provider and ChromaDB is the selected local vector store.
- Indexing is a one-time hackathon preparation process.
- The source package may contain PDF, Word, Excel, CSV, and T-SQL files in a predefined folder.
- Each measure has one primary logic procedure and may reference shared stored procedures or functions.
- The previously generated FAQ set will seed FAQ retrieval.
- The delivery target is tomorrow, so MCP and expanded diagnostics are stretch work.

## WBS overview

| ID | Workstream | Outcome | Approval gate |
|---|---|---|---|
| 0 | Product and architecture approval | Agreed scope, sources, flows, and success criteria | Gate A |
| 1 | Experience baseline | Approved reuse map for the current UI | Gate B |
| 2 | Knowledge contract | Agreed source, chunk, and metadata rules | Gate C |
| 3 | SQL-to-English design | Validated translation and lineage approach | Gate D |
| 4 | Retrieval design | Approved hybrid retrieval behavior and thresholds | Gate E |
| 5 | Conversation control | Approved deterministic state and follow-up policy | Gate F |
| 6 | LLM contracts | Approved bounded LLM responsibilities and evaluations | Gate G |
| 7 | Integrated MVP | Working end-to-end hackathon solution | Gate H |
| 8 | Evaluation and demo | Evidence that the solution meets hackathon objectives | Gate I |
| 9 | Packaging and handoff | Portable package for the office laptop | Gate J |

## 0. Product definition and architecture approval

### 0.1 Confirm hackathon use cases

Define a small acceptance set covering:

- direct specification clarification;
- multiple-reading selection;
- eligibility or exclusion investigation;
- data-source permissibility;
- SQL implementation explanation;
- specification-versus-SQL difference;
- no relevant FAQ;
- insufficient information requiring a follow-up.

### 0.2 Confirm scope boundaries

- Measurement year is MY2026.
- Measures are CBP, GSD, KED, EED, and SPC.
- SQL dialect is T-SQL stored procedures.
- The demo explains scenarios from user-supplied facts and retrieved logic; it does not execute SQL or query member data.
- Included sources are measure specifications, stored procedures, Value Set Directory, and Medication List Directory.
- MCP is preferred when feasible but is not on the critical path to the web demonstration.

### 0.3 Define measurable success criteria

Proposed minimum criteria:

- no irrelevant FAQ shown for the agreed negative test cases;
- correct measure/year filtering;
- direct questions answered without unnecessary follow-ups;
- missing material facts trigger one relevant follow-up at a time;
- every substantive answer cites retrieved evidence;
- SQL explanations retain source lineage;
- specification wins in an intentional conflict test;
- current UI remains visually consistent.

### Deliverables

- approved product scope;
- approved architecture;
- prioritized use-case list;
- acceptance-test outline;
- resolved decision log.

### Gate A — Product-owner approval

No implementation work begins before Gate A.

## 1. New experience design

### 1.1 Inventory the current UI as a product reference

- chat page and message states;
- measure/year selectors;
- right-side FAQ/source panel;
- clickable audit trace;
- FAQ library and downloads;
- warnings and masking notices;
- responsive behavior and styling assets.

### 1.2 Create reuse and change map

- interaction patterns to retain;
- components and styling that may be adapted without coupling the new application to the old project;
- APIs required by the new application;
- new states for retrieval, follow-up, source evidence, and conflict;
- behavior when no FAQ is relevant;
- loading, empty, error, and insufficient-evidence states.

### 1.3 Approve interaction prototypes

Document conversation examples for each primary use case before backend integration.

The approved visual direction is the same Coastal Teal UI and chat experience, implemented as a new standalone application.

### Deliverables

- UI reuse inventory;
- behavior/state matrix;
- approved conversation mockups;
- regression checklist for existing pages.

### Gate B — Experience approval

## 2. Knowledge-source and chunking contract

### 2.1 Source inventory

- identify sample specifications, SQL, stored procedures, MLD/VSD artifacts, FAQs, and supporting documents;
- capture measure, year, format, version, and authority;
- identify documents that cannot be included in the portable package.
- load the hackathon sources from a predefined folder rather than building an upload interface.

### 2.2 Parsing rules

- define structure boundaries for each file type;
- determine table and heading handling;
- define parsing failure and unsupported-format behavior;
- specify adjacent-context rules.
- cover PDF, DOCX, XLSX, CSV, and T-SQL inputs for the MVP.

### 2.3 Metadata contract

Define required conceptual metadata for:

- measure and measurement year;
- source type and authority;
- filename, version, page/section or SQL line range;
- SQL object, revision/hash, and logic category;
- review status;
- chunk relationships and neighboring context.

### 2.4 Year and package validation

- define how year is obtained from filenames, folders, and content;
- specify behavior for missing or conflicting year information;
- define quarantine behavior for ambiguous sources.

### Deliverables

- source catalog template;
- chunking specification;
- metadata dictionary;
- example chunks for each source type;
- ingestion acceptance cases.

### Gate C — Knowledge-contract approval

## 3. SQL-to-English capability

### 3.1 SQL dialect assessment

- collect representative T-SQL stored procedures for all five measures;
- identify supported syntax, temporary objects, dynamic SQL, proprietary functions, and procedural constructs;
- assess parser coverage and fallback behavior.
- distinguish the primary measure procedure from referenced shared procedures and functions.
- catalog missing dependency definitions without inventing their behavior.

### 3.2 Logical-block segmentation

Define segmentation for:

- CTEs and subqueries;
- joins and filters;
- CASE expressions;
- eligibility, exclusion, numerator, and reading selection;
- dates and measurement periods;
- ranking, deduplication, and aggregation;
- upstream object dependencies.

### 3.3 Translation contract

Define the English explanation fields and require separation of:

- directly implemented behavior;
- inherited behavior;
- specification context;
- inference or uncertainty.

### 3.4 Fidelity validation

- compare each explanation with its SQL block;
- reject unsupported details;
- retain SQL line and object citations;
- test whether the explanation preserves null, date, ranking, and aggregation semantics.
- conduct a one-time product-owner inspection of representative English explanations during hackathon flow testing.

### Deliverables

- SQL support matrix;
- logical-block rules;
- translation-quality rubric;
- reviewed example translations;
- unsupported-SQL handling policy.

### Gate D — SQL-to-English approval

## 4. Retrieval and indexing

### 4.1 Select local retrieval components

- use local persisted ChromaDB;
- select an OpenAI embedding model during the approved implementation phase;
- confirm keyword-search implementation;
- confirm persistence location and portability constraints.

### 4.2 Define indexing workflow

- catalog and validate sources;
- parse and chunk;
- generate SQL explanations where applicable;
- attach metadata;
- embed and index;
- record failures and counts.

### 4.3 Define query workflow

- mandatory measure/year filtering;
- optional source-type filtering;
- vector and keyword search;
- deterministic score combination or reranking;
- neighboring-context expansion;
- duplicate removal.

### 4.4 Define FAQ relevance policy

- FAQ-specific minimum score;
- exact measure/year matching requirements;
- maximum displayed FAQs;
- empty-panel behavior;
- approved-content requirement.
- reuse the previously generated hackathon FAQ set as the initial seed.

### 4.5 Retrieval evaluation

Create a labelled set of questions and expected source chunks. Measure retrieval recall, irrelevant retrieval, year leakage, and citation usability.

### Deliverables

- component decision;
- retrieval design;
- threshold policy;
- evaluation set;
- retrieval acceptance results.

### Gate E — Retrieval approval

## 5. Deterministic conversation controller

### 5.1 Intent taxonomy

- finalize supported intents;
- define confidence thresholds;
- define ambiguity and unsupported-intent handling;
- map each intent to relevant source types.

### 5.2 Fact model

- define facts required by supported use cases;
- distinguish required, optional, derived, and unknown facts;
- define validation and normalization rules;
- record fact provenance from user turns or deterministic results.

### 5.3 State transitions

Define permitted stages such as:

- scope collection;
- retrieval;
- follow-up required;
- answer ready;
- insufficient evidence;
- conflict detected;
- resolved or ended.

### 5.4 Next-question selection

- retrieve before asking unnecessary questions;
- select only from allowed missing facts;
- prioritize facts that materially change the answer;
- ask one question at a time;
- prevent repeated questions;
- define maximum follow-up depth and stopping behavior.

### 5.5 Conflict behavior

- compare specification and implementation evidence;
- distinguish conflict from incomplete evidence or year mismatch;
- follow specification authority;
- expose a hackathon-visible alert.

### Deliverables

- intent catalog;
- conceptual fact catalog;
- state-transition specification;
- follow-up prioritization rules;
- conflict behavior matrix;
- conversation test scenarios.

### Gate F — Conversation-control approval

## 6. Bounded LLM behavior

### 6.1 Provider and model decision

- select the specific OpenAI chat/reasoning and embedding models during the approved implementation phase;
- confirm office connectivity and credentials;
- define offline or unavailable-model behavior;
- estimate expected request volume and cost.
- support an internal OpenAI-compatible endpoint through external configuration because the final office endpoint is not yet known.

### 6.2 Structured understanding contract

Define validated outputs for:

- intent classification;
- fact extraction;
- ambiguity reporting;
- query expansion where permitted.

### 6.3 Follow-up phrasing contract

The input identifies the controller-selected missing fact. The LLM returns one concise question without changing the requested fact or adding a new rule.

### 6.4 Answer-generation contract

The answer uses only the evidence bundle and must preserve uncertainty, conditions, source priority, and citations.

### 6.5 Output validation and fallback

- validate structured responses;
- confirm cited sources are in the evidence bundle;
- reject unsupported claims where feasible;
- use deterministic fallback wording if generation fails.

### 6.6 LLM evaluation

Test extraction accuracy, unnecessary-question rate, groundedness, citation completeness, conflict handling, and repeatability at the selected generation settings.

### Deliverables

- provider decision;
- LLM responsibility contract;
- output-validation rules;
- evaluation cases and pass criteria;
- cost and failure-mode estimate.

### Gate G — LLM-contract approval

## 7. Integrated hackathon MVP

Implementation begins only after Gates A–G are approved.

### 7.1 Build ingestion slice

- ingest the agreed sources;
- produce reviewed SQL-English chunks;
- create the local index;
- expose ingestion status.

### 7.2 Build retrieval slice

- implement metadata filtering;
- implement hybrid search;
- enforce FAQ thresholds;
- return citation-ready evidence.

### 7.3 Build conversation slice

- implement session state;
- integrate structured understanding;
- implement deterministic next-action selection;
- integrate follow-up phrasing and grounded answers.

### 7.4 Integrate the existing UI

- reproduce the current Coastal Teal styling and chat layout in the new standalone application;
- connect new conversation behavior;
- update right-side source and FAQ states;
- retain the FAQ page and download behavior;
- expose a clickable trace.

### 7.5 Preferred MCP surface

If schedule and environment permit, expose stable retrieval and conversation operations as MCP tools after the end-to-end web flow is stable. MCP must not delay the core judged demonstration.

### Deliverables

- integrated local application;
- indexed hackathon knowledge package;
- repeatable local startup;
- demonstration trace.

### Gate H — MVP acceptance

## 8. Evaluation and demonstration readiness

### 8.1 Functional evaluation

- direct-answer scenarios;
- follow-up scenarios;
- no-relevant-FAQ scenarios;
- insufficient-evidence scenarios;
- intentional conflict scenarios;
- multi-measure and multi-year separation.

### 8.2 SQL fidelity evaluation

- compare explanations with SQL source;
- verify line/object lineage;
- test ranking, null, date, and aggregation examples;
- document unsupported constructs.

### 8.3 Retrieval evaluation

- expected chunks in top results;
- no measurement-year leakage;
- FAQ precision;
- useful adjacent context.

### 8.4 Conversation evaluation

- one relevant follow-up at a time;
- no repeated questions;
- no unnecessary question when evidence is sufficient;
- conclusion updates correctly after each user response.

### 8.5 UI regression and demo rehearsal

- desktop layout;
- FAQ page consistency;
- empty and error states;
- startup on the agreed fixed port;
- scripted end-to-end demonstration.

### Deliverables

- test report;
- known-limitations register;
- demo script;
- judge-facing architecture summary.

### Gate I — Demo readiness

## 9. Portable packaging and office handoff

### 9.1 Package composition

- source application;
- approved synthetic or office-permitted sample content;
- dependency manifest;
- configuration template without credentials;
- index rebuild instructions;
- startup and troubleshooting guide;
- architecture and known limitations.

### 9.2 Portability validation

- test in a clean environment;
- verify no absolute personal paths;
- verify no secrets or restricted content;
- verify deterministic package rebuild;
- confirm office-compatible dependency installation.

### 9.3 Repository handoff

- commit approved artifacts;
- provide branch/tag convention;
- document how office-only documents are added and indexed;
- avoid placing proprietary documents in public repositories.

### Deliverables

- portable package;
- office-laptop continuation prompt;
- installation checklist;
- clean repository history.

### Gate J — Handoff approval

## Dependencies and critical path

```text
Scope approval
   → source/chunk contract
   → SQL translation contract
   → retrieval design
   → conversation state design
   → LLM contracts
   → integrated MVP
   → evaluation
   → packaging
```

UI analysis may proceed alongside source-contract work after Gate A. Retrieval implementation depends on the metadata and chunk contract. Conversation integration depends on stable retrieval outputs and the approved fact/state model.

## One-day MVP delivery cut

Because the target is tomorrow, the first release is restricted to:

1. predefined-folder ingestion;
2. the five MY2026 measures;
3. primary procedure logic with dependency discovery;
4. one-time ChromaDB indexing;
5. seeded FAQ search with a strict threshold;
6. deterministic conversation state and one follow-up at a time;
7. OpenAI-compatible understanding, phrasing, and grounded answers;
8. the new standalone Coastal Teal UI;
9. citations plus a lightweight trace;
10. a small acceptance set covering direct answer, follow-up, no-FAQ, and conflict behavior.

Deferred from the one-day critical path:

- MCP implementation;
- full semantic analysis of every shared dependency;
- UI-based document upload;
- incremental indexing;
- retrieval-score visualization;
- production governance and security.

## Principal risks

| Risk | Impact | Planned mitigation |
|---|---|---|
| SQL parser cannot handle office stored procedures | Incorrect or incomplete explanations | Dialect assessment, fallback chunking, explicit unsupported status |
| LLM adds domain rules absent from SQL | Misleading explanation | Lineage, evidence labels, fidelity review and tests |
| Semantic search returns vaguely related FAQs | Poor user trust | Dedicated FAQ threshold and empty-state behavior |
| Follow-up questions become free-form | Non-repeatable workflow | Controller selects the fact; LLM only phrases it |
| Measure-year sources are mixed | Incorrect answer | Mandatory metadata filters and leakage tests |
| Hackathon scope becomes production program | Missed delivery | Enforce deferred list and approval gates |
| Office model access differs from personal laptop | Integration failure | Provider adapter decision and early connectivity test |

## Proposed definition of done for the hackathon

The solution is done when the agreed MY2026 cases for CBP, GSD, KED, EED, and SPC run through the new UI, retrieve the correct evidence, ask only necessary follow-up questions, produce grounded cited explanations without implying database execution, show no irrelevant FAQs, expose an understandable trace, and can be installed and started on the office laptop using documented steps.
