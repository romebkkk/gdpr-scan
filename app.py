#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDPR Scan — Web UI (Flask).
Sirve una interfaz web premium en http://localhost:8000 que ejecuta el
mismo motor de escaneo (gdpr_scan.scan + evaluate).
"""
import os
import sys

from flask import Flask, request, jsonify, send_file

from gdpr_scan import scan, evaluate, VERSION, BRAND, BRAND_URL

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "web"), static_url_path="/static")


@app.get("/")
def index():
    return send_file(os.path.join(BASE_DIR, "web", "index.html"))


@app.get("/api/meta")
def meta():
    return jsonify({"version": VERSION, "brand": BRAND, "brand_url": BRAND_URL})


@app.get("/api/scan")
def api_scan():
    url = (request.args.get("url") or "").strip()
    if not url:
        return jsonify({"error": "Introduce una URL para analizar."}), 400
    try:
        result = scan(url, timeout_ms=45000)
    except Exception as e:
        return jsonify({"error": f"No se pudo analizar la web: {e}"}), 502
    checks, score, grade = evaluate(result)
    return jsonify({"scan": result, "checks": checks, "score": score, "grade": grade})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print("=" * 60)
    print(f"  🛡️  GDPR Scan Web v{VERSION} — {BRAND}")
    print(f"  ▶  http://localhost:{port}")
    print("=" * 60)
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
