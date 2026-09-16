from __future__ import annotations

import csv
import io
import os

from flask import Flask, Response, jsonify, render_template, request

from config import settings
from service import NavigatorService


app = Flask(__name__)
service = NavigatorService(settings)


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/faqs")
def faq_library():
    return render_template("faqs.html", faqs=service.store.list_faqs())


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", **service.ingestion.status()})


@app.get("/api/packages")
def packages():
    return jsonify({"packages": service.packages()})


@app.get("/api/index/status")
def index_status():
    return jsonify(service.ingestion.status())


@app.post("/api/index/build")
def build_index():
    return jsonify(service.ingestion.build())


@app.get("/api/faqs")
def faqs():
    return jsonify({"faqs": service.store.list_faqs(request.args.get("measure_id"))})


@app.get("/api/faqs/download")
def download_faqs():
    rows = service.store.list_faqs()
    output = io.StringIO()
    if request.args.get("format", "csv") == "md":
        output.write("# Measure Navigator FAQs\n\n")
        for row in rows:
            output.write(f"## {row.get('question', '')}\n\n{row.get('answer', '')}\n\nSources: {row.get('source_refs', '')}\n\n")
        return Response(output.getvalue(), mimetype="text/markdown", headers={"Content-Disposition": "attachment; filename=measure-navigator-faq.md"})
    fields = ["measure_id", "measurement_year", "question", "answer", "source_refs"]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows({field: row.get(field, "") for field in fields} for row in rows)
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=measure-navigator-faq.csv"})


@app.post("/api/chat")
def chat():
    body = request.get_json(silent=True) or {}
    try:
        return jsonify(service.start(
            body.get("question", ""), body.get("measure_id", "CBP"), int(body.get("measurement_year", 2026))
        ))
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/sessions/<session_id>/respond")
def respond(session_id: str):
    try:
        return jsonify(service.respond(session_id, (request.get_json(silent=True) or {}).get("response", "")))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/sessions/<session_id>/action")
def session_action(session_id: str):
    try:
        return jsonify(service.action(session_id, (request.get_json(silent=True) or {}).get("action", "")))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5002")), debug=False)
