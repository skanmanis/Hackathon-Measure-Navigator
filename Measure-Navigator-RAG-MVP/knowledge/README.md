# Hackathon knowledge folder

Place source files in the predefined measure folders:

```text
knowledge/
  MY2026/
    CBP/
    GSD/
    KED/
    EED/
    SPC/
```

Supported inputs:

- `.pdf` measure specifications
- `.docx` Word documents
- `.xlsx` or `.xlsm` workbooks
- `.csv` files
- `.sql` T-SQL stored procedures and shared dependency definitions
- `.txt` and `.md` supporting text

Use descriptive filenames containing `VSD`, `Value Set`, `MLD`, or `Medication` so the ingestion pipeline can assign the appropriate source type. All other non-SQL documents are treated as specification/supporting guidance for the hackathon.

Run one-time indexing after files are copied:

```powershell
python ingest.py
```

Missing shared stored-procedure or function files are reported as unresolved dependencies; the application must not invent their behavior.

