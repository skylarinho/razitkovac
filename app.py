"""Razitkovac - local web tool for placing an APPROVED stamp into a PDF."""

import re
import threading
import uuid
import webbrowser
from io import BytesIO
from pathlib import Path

from flask import Flask, Response, abort, jsonify, render_template, request, send_file

import config
import pdf_ops
import stamp

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_MB * 1024 * 1024

# In-memory store of uploaded documents: id -> {"name": str, "data": bytes, "pages": int}
DOCS: dict[str, dict] = {}

MAX_NAME_LENGTH = 60


def get_doc(doc_id: str) -> dict:
    doc = DOCS.get(doc_id)
    if doc is None:
        abort(404)
    return doc


def error(code: str, status: int, **extra):
    """JSON error; the frontend turns `code` into a Czech message."""
    return jsonify(code=code, **extra), status


def clean_name(raw) -> str:
    """Normalise the stamper name: collapse whitespace/control characters, cap the length."""
    return re.sub(r"[\s\x00-\x1f\x7f]+", " ", str(raw or "")).strip()[:MAX_NAME_LENGTH]


@app.errorhandler(413)
def too_large(_):
    return error("too_large", 413, limit=config.MAX_UPLOAD_MB)


@app.errorhandler(404)
def not_found(_):
    if request.path.startswith("/api/"):
        return error("doc_gone", 404)
    return "Not found", 404


@app.errorhandler(500)
def server_error(_):
    if request.path.startswith("/api/"):
        return error("server", 500)
    return "Server error", 500


@app.get("/")
def index():
    return render_template("index.html", version=config.VERSION)


@app.post("/api/upload")
def upload():
    file = request.files.get("file")
    if file is None:
        return error("no_file", 400)
    data = file.read()
    try:
        pdf_ops.validate_pdf(data)
        pages = pdf_ops.page_sizes(data)
    except pdf_ops.PdfError as e:
        return error(e.code, 400)
    # Only one document is worked on at a time; drop anything older.
    DOCS.clear()
    doc_id = uuid.uuid4().hex
    DOCS[doc_id] = {"name": file.filename or "document.pdf", "data": data, "pages": len(pages)}
    return jsonify(id=doc_id, pages=pages, stampAspect=stamp.ASPECT)


@app.get("/api/page/<doc_id>/<int:index>.png")
def page_png(doc_id: str, index: int):
    doc = get_doc(doc_id)
    if not 0 <= index < doc["pages"]:
        abort(404)
    png = pdf_ops.render_page(doc["data"], index, config.PREVIEW_ZOOM)
    return Response(png, mimetype="image/png", headers={"Cache-Control": "no-store"})


@app.get("/api/stamp-preview.png")
def stamp_preview():
    name = clean_name(request.args.get("name"))
    if not name:
        return error("name_required", 400)
    return Response(stamp.render_stamp(name, 800), mimetype="image/png", headers={"Cache-Control": "no-store"})


@app.post("/api/stamp")
def stamp_document():
    body = request.get_json(silent=True) or {}
    doc = get_doc(str(body.get("id", "")))
    name = clean_name(body.get("name"))
    if not name:
        return error("name_required", 400)
    try:
        index = int(body["page"])
        x_rel = min(max(float(body["x"]), 0.0), 1.0)
        y_rel = min(max(float(body["y"]), 0.0), 1.0)
    except (KeyError, TypeError, ValueError):
        return error("bad_position", 400)
    if not 0 <= index < doc["pages"]:
        return error("bad_page", 400)

    png = stamp.render_stamp(name)
    result = pdf_ops.stamp_pdf(doc["data"], index, x_rel, y_rel, png, stamp.ASPECT)
    DOCS.pop(body["id"], None)
    name = f"{Path(doc['name']).stem}_approved.pdf"
    return send_file(BytesIO(result), mimetype="application/pdf", as_attachment=True, download_name=name)


if __name__ == "__main__":
    url = f"http://{config.HOST}:{config.PORT}"
    threading.Timer(1.0, webbrowser.open, args=[url]).start()
    app.run(host=config.HOST, port=config.PORT, debug=False)
