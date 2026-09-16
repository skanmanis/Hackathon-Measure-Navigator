# Office Input Checklist

Complete this checklist when continuing the project in VS Code. Paths may point to folders or individual files.

## Application and environment

| Item | Value |
|---|---|
| Measure Navigator project root | |
| Python version available | |
| Package installation permitted? | Yes / No / Unknown |
| Local ChromaDB persistence permitted? | Yes / No / Unknown |
| Approved local port | 5002 / Other: |
| OpenAI access type | Direct OpenAI / Internal compatible endpoint / Unknown |
| Chat model or deployment name | |
| Embedding model or deployment name | |
| Credential delivery method | Environment variable / approved secret store / Other |

Do not write an API key, bearer token, password, or connection secret in this file.

## MY2026 source locations

| Source | Path | Notes |
|---|---|---|
| Measure specifications | | |
| Value Set Directory | | |
| Medication List Directory | | |
| Approved FAQs | | |
| Provider tip sheets / supporting guidance | | |
| Test scenarios | | Non-identifying only |

## Primary stored procedures

| Measure | Primary T-SQL stored procedure path | Expected procedure/object name |
|---|---|---|
| CBP | | |
| GSD | | |
| KED | | |
| EED | | |
| SPC | | |

Shared stored procedure/function folder:

```text
<enter approved path>
```

## Pre-indexing confirmation

- [ ] Every source is approved for local hackathon use.
- [ ] Measurement year is confirmed as MY2026.
- [ ] Each source is mapped to one or more measures.
- [ ] Primary stored procedures are distinguished from shared dependencies.
- [ ] Missing shared procedure/function definitions are documented.
- [ ] Password-protected or unsupported files are identified.
- [ ] No member-level PHI is included in the indexing package.
- [ ] No secrets are present in source files.
- [ ] Proprietary office documents will not be pushed to a public repository.
- [ ] ChromaDB index folders and local environment files are excluded from Git.
- [ ] Product owner approved the proposed mapping before indexing.

## Expected inventory report

The office-side assistant should report:

- file path;
- detected extension;
- proposed measure;
- proposed measurement year;
- proposed source type;
- authority level;
- primary or shared SQL classification;
- discovered SQL dependencies;
- parse/index eligibility;
- ambiguity or error notes.
