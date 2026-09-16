from __future__ import annotations

from config import settings
from service import NavigatorService


service = NavigatorService(settings)

try:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("Measure Navigator RAG")

    @mcp.tool()
    def search_measure_evidence(question: str, measure_id: str, measurement_year: int = 2026) -> dict:
        """Search MY2026 measure evidence and return citation-ready chunks."""
        service._validate_scope(measure_id, measurement_year)
        rows = service.store.search(question, measure_id, measurement_year, settings.top_k)
        return {"results": [service._evidence_dict(row) for row in rows]}

    @mcp.tool()
    def ask_measure_navigator(question: str, measure_id: str, measurement_year: int = 2026) -> dict:
        """Start a deterministic Measure Navigator clarification session."""
        return service.start(question, measure_id, measurement_year)

    @mcp.tool()
    def continue_measure_navigator(session_id: str, response: str) -> dict:
        """Continue a session with a response to the selected follow-up fact."""
        return service.respond(session_id, response)

    @mcp.tool()
    def get_index_status() -> dict:
        """Return the local hackathon index status."""
        return service.ingestion.status()

except ImportError:
    mcp = None


if __name__ == "__main__":
    if mcp is None:
        raise SystemExit("Install requirements before starting the MCP server.")
    mcp.run()

