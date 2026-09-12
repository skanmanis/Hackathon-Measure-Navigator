$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.12 or later must be installed and available as 'python'."
}

python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements-office.txt
& .\.venv\Scripts\python.exe yaml_to_json.py
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v

Write-Host "Setup complete. Start the website with: .\.venv\Scripts\python.exe app.py"
Write-Host "Start the MCP server with: .\.venv\Scripts\python.exe mcp_server.py"

