import os
import csv
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file

from navigator import NavigatorService

ROOT=Path(__file__).resolve().parent
load_dotenv(ROOT/".env")
app=Flask(__name__)
service=NavigatorService(ROOT)

@app.get("/")
def home(): return render_template("index.html")

@app.get("/faqs")
def faq_library(): return render_template("faqs.html",faqs=service.list_faqs())

@app.get("/style-lab")
def style_lab(): return render_template("style_lab.html")

@app.get("/prototype/<theme>")
def prototype(theme):
    themes={
        "clinical":{"name":"Clinical clarity","description":"Direct healthcare-service styling with strong blue actions and restrained sage guidance."},
        "enterprise":{"name":"Enterprise evidence","description":"Compact, structured styling for analysts who spend most of the session reviewing evidence."},
        "calm":{"name":"Calm navigator","description":"A more spacious and approachable interface with prominent sage surfaces and softer blue controls."},
        "coastal":{"name":"Coastal teal","description":"Deep navy with clear teal accents and pale aqua surfaces. Crisp without feeling clinical."},
        "indigo":{"name":"Indigo cloud","description":"Indigo actions with soft lavender-gray surfaces. Modern and polished without strong green."},
        "sand":{"name":"Warm neutral","description":"Ink blue, warm sand, and muted terracotta accents. Less institutional and more editorial."},
        "slate":{"name":"Slate and cyan","description":"Charcoal slate with bright cyan signals and cool gray surfaces. Technical and high contrast."},
        "navy":{"name":"Navy and mint","description":"Deep navy structure with fresh mint highlights. Formal, calm, and presentation-ready."}
    }
    if theme not in themes: return "Prototype not found",404
    return render_template("prototype.html",theme=theme,meta=themes[theme])

@app.get("/api/health")
def health(): return jsonify({"status":"ok","packages":len(service.packages.list_packages()),"source_authority":"SPECIFICATION"})

@app.get("/api/packages")
def packages(): return jsonify({"packages":service.packages.list_packages()})

@app.get("/api/escalations")
def escalations(): return jsonify({"escalations":service.list_escalations()})

@app.post("/api/escalations")
def create_escalation():
    body=request.get_json(silent=True) or {}
    try: return jsonify(service.report_conflict(body.get("session_id"),body.get("conflicting_source","DERIVED_LOGIC"),body.get("detail","Source conflict requires measure-owner review.")))
    except ValueError as exc: return jsonify({"error":str(exc)}),400

@app.get("/api/faqs")
def faqs(): return jsonify({"faqs":service.list_faqs(request.args.get("measure_id"),request.args.get("measurement_year",type=int))})

@app.get("/api/faqs/download")
def download_faqs():
    rows=service.list_faqs()
    if request.args.get("format", "md").lower()=="csv":
        target=ROOT/"data"/"measure-navigator-faq.csv"
        fields=["measure_id","measurement_year","question","answer","source_refs"]
        with target.open("w",encoding="utf-8-sig",newline="") as handle:
            writer=csv.DictWriter(handle,fieldnames=fields)
            writer.writeheader()
            writer.writerows({key:row[key] for key in fields} for row in rows)
        return send_file(target,as_attachment=True,download_name="measure-navigator-faq.csv",mimetype="text/csv")
    lines=["# Measure Navigator FAQ - SYN-CBP MY2026",""]
    for row in rows: lines.extend([f"## {row['question']}",row["answer"],f"Sources: {row['source_refs']}",""])
    target=ROOT/"data"/"measure-navigator-faq.md"; target.write_text("\n".join(lines),encoding="utf-8")
    return send_file(target,as_attachment=True,download_name="measure-navigator-faq.md")

@app.post("/api/chat")
def chat():
    body=request.get_json(silent=True) or {}
    try: return jsonify(service.start(body.get("question",""),bool(body.get("deepen",False)),body.get("measure_id","SYN-CBP"),int(body.get("measurement_year",2026))))
    except (ValueError,TypeError) as exc: return jsonify({"error":str(exc)}),400

@app.post("/api/sessions/<session_id>/decision-tree")
def begin_tree(session_id):
    try: return jsonify(service.begin_tree(session_id))
    except ValueError as exc: return jsonify({"error":str(exc)}),404

@app.post("/api/sessions/<session_id>/facts")
def facts(session_id):
    try: return jsonify(service.continue_tree(session_id,(request.get_json(silent=True) or {}).get("facts",{})))
    except ValueError as exc: return jsonify({"error":str(exc)}),400

@app.post("/api/sessions/<session_id>/feedback")
def feedback(session_id):
    body=request.get_json(silent=True) or {}
    try: return jsonify(service.feedback(session_id,body.get("state",""),body.get("faq_id")))
    except ValueError as exc: return jsonify({"error":str(exc)}),400

if __name__=="__main__": app.run(host="127.0.0.1",port=int(os.getenv("PORT","5001")),debug=False)
