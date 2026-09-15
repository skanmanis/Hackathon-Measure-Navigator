# Design decisions requiring confirmation

No implementation should begin until these decisions are reviewed.

## 1. Retrieval platform

Select the office-approved target:

- Snowflake Cortex Search
- Azure AI Search
- PostgreSQL with pgvector
- Qdrant
- Another approved service

The choice affects ingestion, hybrid ranking, authentication, deployment and cost.

## 2. Model and embedding endpoints

Confirm the enterprise-hosted reasoning model and embedding model. Confirm whether reranking uses a dedicated model, the retrieval platform, or a deterministic scoring blend.

## 3. Document systems

Identify the authorized repositories for specifications, MLDs, VSDs, SQL, stored procedures, provider guidance and FAQs. Confirm supported formats and access-control requirements.

## 4. Source authority

Confirm the proposed order:

1. Approved specification
2. Governed MLD and VSD
3. Validated SQL
4. Reviewed SQL-to-English explanation
5. Reviewed FAQ
6. Prior resolved cases

Clarify whether the VSD carries equal authority to the specification for code membership.

## 5. Memory retention

Confirm retention for session turns, scenario facts, prompts, model responses, audit traces, unresolved cases and candidate learning. Confirm whether users may resume a prior session.

## 6. FAQ publication workflow

Identify who can review, approve, revise, retire and republish FAQs. Confirm whether approval belongs to a measure owner, clinical reviewer, coding reviewer, or a combination based on question type.

## 7. SQL-to-English generation and approval

YAML will not be required. Confirm the SQL repositories and supported dialects, the required reviewers for generated English explanations, and whether the application will support explanation-only mode, controlled scenario evaluation through SQL, or both.

## 8. Conflict escalation destination

Select the office workflow for alerts, such as ServiceNow, Jira, Azure DevOps, email queue, or an internal review dashboard. Define ownership and severity rules.

## 9. User and access model

Identify user roles and document-level permissions. Confirm whether the system serves analysts only or also measure owners, developers, auditors and operations teams.

## 10. Deployment boundary

Confirm where the web application, MCP server, indexes, operational database, model endpoint and audit logs will run. Confirm whether any component may leave the corporate network.

## Proposed approval sequence

1. Approve logical architecture and source authority
2. Select retrieval, model and data platforms
3. Approve memory and privacy boundaries
4. Approve the revised decision-definition model
5. Approve evaluation and release gates
6. Authorize implementation planning
