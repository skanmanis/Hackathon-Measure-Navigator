# Measure Navigator RAG MVP

A standalone MY2026 hackathon application for CBP, GSD, KED, EED, and SPC. It preserves the Coastal Teal conversation experience while using one-time document ingestion, SQL-to-English explanations, ChromaDB retrieval, deterministic follow-up control, and OpenAI-compatible grounded answers.

## What it does

- Parses PDF, DOCX, XLSX/XLSM, CSV, text, Markdown, and T-SQL files
- Splits documents by structure and T-SQL by logical blocks
- Creates English explanations that retain T-SQL filename and line lineage
- Discovers called procedures/functions without inventing missing dependency behavior
- Stores embeddings in local persisted ChromaDB
- Combines semantic similarity, exact term overlap, metadata filters, and source authority
- Filters every query to the selected measure and MY2026
- Shows seeded FAQs only above a dedicated relevance threshold
- Uses deterministic Python state to choose the next missing fact
- Lets the LLM phrase that selected question and compose a cited answer
- Never executes stored procedures or queries member data
- Provides a lightweight answer trace and optional MCP tools

## Knowledge layout

Copy the office-approved source documents into:

```text
knowledge/MY2026/CBP/
knowledge/MY2026/GSD/
knowledge/MY2026/KED/
knowledge/MY2026/EED/
knowledge/MY2026/SPC/
```

The repository includes one clearly labelled synthetic CBP demonstration document so the UI can be exercised before office documents are added. Remove or replace it before the office-source validation run.

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Configure the office OpenAI-compatible endpoint in `.env`. For direct OpenAI, set `OPENAI_API_KEY`. For an internal compatible endpoint, also set `OPENAI_BASE_URL` and the organization-provided model names.

The application has a deterministic local fallback for development, but OpenAI configuration is expected for the judged conversational experience.

## One-time indexing

```powershell
python ingest.py
```

The output reports files, chunks, parsing errors, retrieval backend, and LLM mode. Re-running indexing replaces the previous hackathon index.

## Run the web application

```powershell
python app.py
```

Open `http://127.0.0.1:5002/`. Port 5002 intentionally avoids changing the existing application on port 5001.

Convenience scripts are included:

```powershell
.\setup.ps1
.\reindex.ps1
.\start.ps1
```

## Optional MCP server

```powershell
python mcp_server.py
```

MCP tools include evidence search, session start/continue, and index status.

## Important limitation

Answers are document-grounded explanations based on user-supplied non-identifying facts. They are not official determinations, do not execute SQL, and do not query member records.
