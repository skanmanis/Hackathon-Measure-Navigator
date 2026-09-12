from pathlib import Path
from mcp.server.fastmcp import FastMCP
from navigator import NavigatorService

service=NavigatorService(Path(__file__).resolve().parent)
mcp=FastMCP("measure-navigator")

@mcp.tool()
def ask_hedis_question(question:str,deepen:bool=False,measure_id:str="SYN-CBP",measurement_year:int=2026)->dict:
    """Start a synthetic HEDIS clarification. FAQ is searched before the decision tree."""
    return service.start(question,deepen,measure_id,measurement_year)

@mcp.tool()
def lookup_value_set(value_set_oid:str,code_system:str,code:str)->dict:
    """Deterministically test a code against the synthetic value-set reconstruction."""
    return {"value_set_oid":value_set_oid,"code_system":code_system,"code":code,"member":service.engine.evaluator.lookup_value_set(value_set_oid,code_system,code)}

@mcp.tool()
def get_exclusion_rules()->list[dict]:
    """List CBP exclusion checks in the atomic check catalog."""
    return [x for x in service.engine.evaluator.catalog_data["checks"] if "EXCL" in x.get("supports_rule","")]

@mcp.tool()
def get_required_facts(check_id:str)->list[dict]:
    """Return only the scenario facts required for one deterministic check."""
    return service.engine.evaluator.required_facts(check_id)

@mcp.tool()
def evaluate_check(check_id:str,facts:dict)->dict:
    """Evaluate one atomic check without using a reasoning model."""
    return service.engine.evaluator.evaluate(check_id,facts)

@mcp.tool()
def search_spec_docs(query:str)->list[dict]:
    """Search the local synthetic specification, decision tree, catalog, and SQL corpus."""
    return service.search_docs(query)

@mcp.tool()
def list_approved_faqs()->list[dict]: return service.list_faqs()

@mcp.tool()
def record_resolution(session_id:str,state:str,faq_id:int|None=None)->dict:
    """Record CONFIRMED_WORKED or CONFIRMED_UNRESOLVED; silence remains NO_CONFIRMATION."""
    return service.feedback(session_id,state,faq_id)

@mcp.tool()
def list_measure_packages()->list[dict]:
    """List governed measure and measurement-year packages and readiness states."""
    return service.packages.list_packages()

@mcp.tool()
def report_source_conflict(session_id:str|None,conflicting_source:str,detail:str)->dict:
    """Create a measure-review alert. The specification remains authoritative."""
    return service.report_conflict(session_id,conflicting_source,detail)

if __name__=="__main__": mcp.run(transport="stdio")
