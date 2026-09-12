from __future__ import annotations

import json
import math
import re
import sqlite3
import uuid
from pathlib import Path

from engine import CheckEvaluator, DecisionTreeEngine
from package_manager import KnowledgePackageManager, PackageError


class PHIRedactor:
    PATTERNS = (
        ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
        ("EMAIL", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
        ("PHONE", re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)")),
        ("MEMBER_ID", re.compile(r"\b(?:member|patient)\s*(?:id|number|#)\s*[:#-]?\s*[A-Z0-9-]{3,}\b", re.I)),
        ("MRN", re.compile(r"\bMRN\s*[:#-]?\s*[A-Z0-9-]{3,}\b", re.I)),
        ("DOB", re.compile(r"\b(?:DOB|date of birth)\s*[:#-]?\s*[^,;.\n]+", re.I)),
        ("NAME", re.compile(r"\b(?:member|patient)\s+name\s*[:#-]?\s*[A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+){1,2}", re.I)),
    )

    def redact(self, text: str) -> tuple[str, list[str]]:
        safe, found = text, []
        for label, pattern in self.PATTERNS:
            safe, count = pattern.subn(f"[{label}_REDACTED]", safe)
            if count:
                found.append(label)
        return safe, found


class Store:
    def __init__(self, root: Path):
        self.path = root / "data" / "navigator.db"
        self.path.parent.mkdir(exist_ok=True)
        with self.connect() as db:
            db.executescript((root / "app_storage.sql").read_text(encoding="utf-8"))
            columns={row[1] for row in db.execute("PRAGMA table_info(sessions)")}
            if "measure_id" not in columns: db.execute("ALTER TABLE sessions ADD COLUMN measure_id TEXT NOT NULL DEFAULT 'SYN-CBP'")
            if "measurement_year" not in columns: db.execute("ALTER TABLE sessions ADD COLUMN measurement_year INTEGER NOT NULL DEFAULT 2026")
            if "intent_json" not in columns: db.execute("ALTER TABLE sessions ADD COLUMN intent_json TEXT NOT NULL DEFAULT '{}'")
            if not db.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]:
                db.executemany("INSERT INTO faqs(measure_id,measurement_year,question,answer,keywords,source_refs) VALUES(?,?,?,?,?,?)", [
                    ("SYN-CBP",2026,"Can an inpatient or emergency department BP reading count for CBP?","A reading taken during an acute inpatient stay or emergency department visit is excluded from numerator evidence in this synthetic prototype. Verify the place of service with CHK-READING-SETTING.","CBP inpatient ED emergency reading permitted setting",'["CHK-READING-SETTING","SYN.CBP.VS.015"]'),
                    ("SYN-CBP",2026,"Why might a CBP result be numerator non-compliant?","Check the representative reading date, care setting, CPT II modifier, and both BP values. The decision tree evaluates each fact and carries unknown conditions forward.","CBP non compliant numerator blood pressure",'["CHK-READING-DATE-VALID","CHK-READING-SETTING","CHK-READING-MODIFIER","CHK-BP-CONTROLLED"]'),
                    ("SYN-CBP",2026,"Why might a member be excluded from CBP?","The prototype evaluates ESRD diagnosis or procedures, pregnancy, hospice, non-acute inpatient care, and the combined frailty plus advanced illness path.","CBP excluded exclusion ESRD pregnancy hospice frailty",'["route_exclusions"]'),
                    ("SYN-CBP",2026,"What happens when a fact is unknown?","The engine records an OPEN_CONDITION, states both possible outcomes, and continues through other relevant checks. The BP threshold requires both numeric values.","unknown missing fact open condition",'["OPEN_CONDITION","CHK-BP-CONTROLLED"]'),
                ])

    def connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db


class NavigatorService:
    def __init__(self, root: Path):
        self.root, self.store = root, Store(root)
        self.redactor = PHIRedactor()
        self.packages = KnowledgePackageManager(root)
        self.engines = {}

    def engine_for(self, measure_id: str, measurement_year: int) -> DecisionTreeEngine:
        key=(measure_id,int(measurement_year))
        if key not in self.engines:
            package=self.packages.resolve(*key)
            self.engines[key]=DecisionTreeEngine(package,self.root/"intent_taxonomy.json")
        return self.engines[key]

    @property
    def engine(self):
        return self.engine_for("SYN-CBP",2026)

    @staticmethod
    def tokens(text: str) -> set[str]:
        stop={"a","an","the","is","are","can","does","do","why","what","for","to","of","this","member"}
        return {x for x in re.findall(r"[a-z0-9]+",text.lower()) if len(x)>1 and x not in stop}

    def search_faqs(self, query: str, measure_id: str="SYN-CBP", measurement_year: int=2026, limit: int = 3) -> list[dict]:
        qt=self.tokens(query)
        with self.store.connect() as db:
            rows=db.execute("SELECT * FROM faqs WHERE status='approved' AND measure_id=? AND measurement_year=?",(measure_id,measurement_year)).fetchall()
        ranked=[]
        minimum=max(2,math.ceil(len(qt)*0.45))
        for row in rows:
            score=len(qt & self.tokens(f"{row['question']} {row['answer']} {row['keywords']}"))
            if score>=minimum: ranked.append((score+min(row["helpful_count"],5)/10,dict(row)))
        return [item for _,item in sorted(ranked,key=lambda x:x[0],reverse=True)[:limit]]

    @staticmethod
    def _same_day_readings(question: str) -> list[tuple[int,int]]:
        q=question.lower()
        if not (("same day" in q or "same date" in q or "in a day" in q) and ("reading" in q or "bp" in q)):
            return []
        return [(int(s),int(d)) for s,d in re.findall(r"\b(\d{2,3})\s*/\s*(\d{2,3})\b",question)]

    def _specification_clarification(self, question: str, measure_id: str, measurement_year: int) -> dict|None:
        readings=self._same_day_readings(question)
        q=question.lower()
        scenario=("same day" in q or "same date" in q or "in a day" in q) and ("two" in q or "multiple" in q or len(readings)>=2) and ("reading" in q or "bp" in q)
        if not scenario or measure_id!="SYN-CBP": return None
        citation="specification.synthetic.json#SYN-CBP-NUM-MULTIPLE-READINGS"
        if len(readings)>=2:
            low_sys=min(value[0] for value in readings); low_dia=min(value[1] for value in readings)
            controlled=low_sys<140 and low_dia<90
            message=(f"Yes. For multiple readings on the same date, use the lowest systolic value ({low_sys}) and the lowest diastolic value ({low_dia}). "
                     f"Those selected values {'meet' if controlled else 'do not meet'} the synthetic MY{measurement_year} threshold of <140/<90, so this scenario is {'numerator compliant' if controlled else 'not numerator compliant'}.")
            check={"check_id":"CHK-MULTIPLE-READINGS-SAME-DAY","status":"MET" if controlled else "NOT_MET","inputs":readings,"selected":{"systolic":low_sys,"diastolic":low_dia},"explanation":"Lowest systolic and lowest diastolic were selected independently from the same date."}
        else:
            message="Yes. When multiple readings occur on the same date, use the lowest systolic and the lowest diastolic from that date. The two selected values may come from different readings. Compliance then depends on whether the selected values meet the measure-year threshold."
            check={"check_id":"CHK-MULTIPLE-READINGS-SAME-DAY","status":"SPECIFICATION_CLARIFIED","explanation":"No numeric readings were supplied, so the selection rule was clarified without calculating compliance."}
        return {"stage":"DOCUMENT_CLARIFICATION","status":"COMPLETE","message":message,"faqs":[],"conclusion":{"result":"NUMERATOR_COMPLIANT" if readings and check["status"]=="MET" else "SPECIFICATION_CLARIFICATION","cites":[citation]},"trace":[check],"open_conditions":[]}

    def start(self, question: str, deepen: bool = False, measure_id: str="SYN-CBP", measurement_year: int=2026) -> dict:
        if not isinstance(question,str) or not question.strip(): raise ValueError("Enter a question.")
        if len(question)>2000: raise ValueError("Question must be 2,000 characters or fewer.")
        safe, phi = self.redactor.redact(question.strip())
        engine=self.engine_for(measure_id,measurement_year)
        session_id=str(uuid.uuid4()); interaction_id=str(uuid.uuid4()); faqs=self.search_faqs(safe,measure_id,measurement_year)
        intent=engine.classify_intent(safe); route=engine.choose_route(safe); node=route
        direct=self._specification_clarification(safe,measure_id,measurement_year)
        if direct:
            result=direct
        elif faqs and not deepen:
            result={"stage":"FAQ","message":"I found approved quick-reference guidance. Review it below, or continue to the deterministic decision tree.","faqs":faqs}
        else:
            if route in {"ESCALATE","FAQ"} or intent["status"]=="CHOOSE_INTENT":
                result={"stage":"ROUTING","status":intent["status"],"message":"I need a reviewed route selection before applying measure logic."}
            else:
                result=engine.advance(node,{},[]); result["stage"]="DECISION_TREE"; result["message"]=self._message(result)
        result["answer_trace"]={"package":f"{measure_id}/MY{measurement_year}","intent":intent,"faq_matches":[f["id"] for f in faqs],"checks":result.get("trace",[]),"open_conditions":result.get("open_conditions",[]),"citations":result.get("conclusion",{}).get("cites",[]),"source_precedence":["SPECIFICATION","MLD","VSD","SQL","DECISION_TREE","FAQ"]}
        result.update({"session_id":session_id,"interaction_id":interaction_id,"masked_question":safe,"phi_masked":bool(phi),"phi_types":phi,
                       "privacy_notice":"Please do not enter PHI. Detected details were masked; do not enter further PHI." if phi else "Please do not enter PHI or member identifiers."})
        with self.store.connect() as db:
            db.execute("INSERT INTO sessions(id,masked_question,route,current_node,measure_id,measurement_year,intent_json) VALUES(?,?,?,?,?,?,?)",(session_id,safe,route,result.get("node_id",node),measure_id,measurement_year,json.dumps(intent)))
            if route=="ESCALATE":
                db.execute("INSERT INTO escalations(id,session_id,severity,reason,conflicting_source) VALUES(?,?,?,?,?)",(str(uuid.uuid4()),session_id,"HIGH","Potential specification and implementation conflict requires review.","SQL_OR_DERIVED_LOGIC"))
            db.execute("INSERT INTO interactions(id,session_id,masked_input,stage,response_json) VALUES(?,?,?,?,?)",(interaction_id,session_id,safe,result["stage"],json.dumps(result)))
            db.execute("INSERT INTO learning_records(session_id,state) VALUES(?,'NO_CONFIRMATION')",(session_id,))
        return result

    def continue_tree(self, session_id: str, facts: dict) -> dict:
        with self.store.connect() as db:
            row=db.execute("SELECT * FROM sessions WHERE id=?",(session_id,)).fetchone()
            if not row: raise ValueError("Session not found.")
            current=json.loads(row["facts_json"]); safe_facts={}
            phi=[]
            for key,value in (facts or {}).items():
                safe,found=self.redactor.redact(str(value)); safe_facts[key]=safe; phi.extend(found)
            current.update(safe_facts); opened=json.loads(row["open_conditions_json"])
            engine=self.engine_for(row["measure_id"],row["measurement_year"])
            result=engine.advance(row["current_node"],current,opened); result["stage"]="DECISION_TREE"; result["message"]=self._message(result)
            intent=json.loads(row["intent_json"])
            result["answer_trace"]={"package":f"{row['measure_id']}/MY{row['measurement_year']}","intent":intent,"faq_matches":[],"checks":result.get("trace",[]),"open_conditions":result.get("open_conditions",[]),"citations":result.get("conclusion",{}).get("cites",[]),"source_precedence":["SPECIFICATION","MLD","VSD","SQL","DECISION_TREE","FAQ"]}
            db.execute("UPDATE sessions SET current_node=?,facts_json=?,open_conditions_json=?,final_answer=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(result.get("node_id",row["current_node"]),json.dumps(current),json.dumps(result.get("open_conditions",opened)),result["message"] if result["status"]=="COMPLETE" else None,session_id))
            db.execute("INSERT INTO interactions(id,session_id,masked_input,stage,response_json) VALUES(?,?,?,?,?)",(str(uuid.uuid4()),session_id,json.dumps(safe_facts),"DECISION_TREE",json.dumps(result)))
        result.update({"session_id":session_id,"phi_masked":bool(phi),"phi_types":sorted(set(phi)),"privacy_notice":"Please do not enter PHI. Detected details were masked; do not enter further PHI." if phi else "Please do not enter PHI or member identifiers."})
        return result

    def begin_tree(self, session_id: str) -> dict:
        return self.continue_tree(session_id,{})

    @staticmethod
    def _message(result: dict) -> str:
        if result["status"]=="NEEDS_MORE_INFO": return result["question"]
        if result["status"]=="COMPLETE":
            text=result["conclusion"]["explanation"]
            if result.get("open_conditions"): text += " Open conditions remain; the result is conditional on those facts."
            return text
        return "Choose the area you want to evaluate."

    def feedback(self, session_id: str, state: str, faq_id: int | None = None) -> dict:
        allowed={"CONFIRMED_WORKED","CONFIRMED_UNRESOLVED"}
        if state not in allowed: raise ValueError("Unsupported feedback state.")
        with self.store.connect() as db:
            row=db.execute("SELECT * FROM sessions WHERE id=?",(session_id,)).fetchone()
            if not row: raise ValueError("Session not found.")
            db.execute("UPDATE sessions SET outcome_state=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(state,session_id))
            db.execute("UPDATE learning_records SET state=?,generalized_question=?,generalized_answer=? WHERE session_id=? AND state='NO_CONFIRMATION'",(state,row["masked_question"],row["final_answer"],session_id))
            if state=="CONFIRMED_WORKED" and faq_id:
                db.execute("UPDATE faqs SET helpful_count=helpful_count+1,updated_at=CURRENT_TIMESTAMP WHERE id=?",(faq_id,))
            elif state=="CONFIRMED_WORKED" and row["final_answer"]:
                db.execute("INSERT INTO faqs(measure_id,measurement_year,question,answer,keywords,source_refs,status) VALUES('SYN-CBP',2026,?,?,?,?, 'needs_review')",(row["masked_question"],row["final_answer"],"learned scenario","[]"))
        return {"status":state,"message":"Outcome recorded. Confirmed learning is available for review."}

    def list_faqs(self, measure_id: str|None=None, measurement_year: int|None=None):
        sql="SELECT id,measure_id,measurement_year,question,answer,source_refs,helpful_count FROM faqs WHERE status='approved'"
        params=[]
        if measure_id: sql+=" AND measure_id=?"; params.append(measure_id)
        if measurement_year: sql+=" AND measurement_year=?"; params.append(measurement_year)
        sql+=" ORDER BY helpful_count DESC,id"
        with self.store.connect() as db: return [dict(x) for x in db.execute(sql,params)]

    def list_escalations(self):
        with self.store.connect() as db: return [dict(x) for x in db.execute("SELECT * FROM escalations ORDER BY created_at DESC")]

    def report_conflict(self, session_id: str|None, conflicting_source: str, detail: str) -> dict:
        source=conflicting_source.upper()
        if source=="SPECIFICATION": raise ValueError("The specification is authoritative and cannot be registered as the derived conflicting source.")
        alert_id=str(uuid.uuid4())
        with self.store.connect() as db:
            db.execute("INSERT INTO escalations(id,session_id,severity,reason,authoritative_source,conflicting_source) VALUES(?,?,?,?,?,?)",(alert_id,session_id,"HIGH",detail,"SPECIFICATION",source))
        return {"alert_id":alert_id,"status":"OPEN","authoritative_source":"SPECIFICATION","action":f"Correct {source} and rerun conformance tests."}

    def search_docs(self, query: str, limit: int=5):
        candidates=[self.root/"check_catalog.json",self.root/"decision_tree.generated.json",self.root/"evaluate_check.sql",self.root/"CLAUDE.md"]
        qt=self.tokens(query); results=[]
        for path in candidates:
            text=path.read_text(encoding="utf-8"); score=len(qt & self.tokens(text))
            if score: results.append({"source":path.name,"score":score,"excerpt":text[:1200]})
        return sorted(results,key=lambda x:x["score"],reverse=True)[:limit]
