"""
app.py -- Flask REST API
=========================

Connects the MySQL database and blockchain verification
to a web API that the frontend can call.

ENDPOINTS:
  GET  /                      --> Welcome / API docs
  GET  /logs                  --> All audit logs
  GET  /logs/count            --> Total log count
  POST /data                  --> Insert a new data record (triggers audit log)
  GET  /data                  --> All data records
  GET  /verify                --> Verify blockchain integrity
  GET  /users                 --> All users
  GET  /alerts                --> All alerts
  GET  /search/user/<name>    --> Search logs by username
  GET  /search/action/<type>  --> Search logs by action type
  GET  /search/date           --> Search logs by date range
  GET  /summary               --> Aggregated stats (GROUP BY)

HOW TO RUN:
  pip install flask mysql-connector-python
  python app.py
  --> Open http://127.0.0.1:5000
"""

import os
from flask import Flask, request, jsonify, send_from_directory
import database as db
from blockchain import verify_chain

# -- Locate the frontend folder --
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

# -- Create Flask app --
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")


# =========================================================================
# CORS (allows frontend JavaScript to call this API)
# =========================================================================

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# =========================================================================
# FRONTEND
# =========================================================================

@app.route("/")
def serve_frontend():
    """Serve the frontend UI."""
    if os.path.exists(os.path.join(FRONTEND_DIR, "index.html")):
        return send_from_directory(FRONTEND_DIR, "index.html")
    return jsonify({"message": "Audit Chain API is running. Frontend not found."})


# =========================================================================
# AUDIT LOGS
# =========================================================================

@app.route("/logs", methods=["GET"])
def get_logs():
    """Return all audit logs with user and record details (uses JOINs)."""
    logs = db.get_all_audit_logs()
    return jsonify({"count": len(logs), "logs": logs})


@app.route("/logs/count", methods=["GET"])
def get_log_count():
    """Return the total number of audit log entries."""
    count = db.get_audit_log_count()
    return jsonify({"count": count})


# =========================================================================
# DATA RECORDS
# =========================================================================

@app.route("/data", methods=["POST"])
def add_data():
    """
    Insert a new data record.

    The MySQL TRIGGER automatically creates an audit log entry
    with a SHA-256 hash chained to the previous entry.

    JSON body: { "data_content": "some data here" }
    """
    body = request.get_json(silent=True)
    if not body or not body.get("data_content", "").strip():
        return jsonify({"error": "'data_content' is required."}), 400

    record_id = db.insert_data_record(body["data_content"].strip())
    return jsonify({
        "message": "Data record inserted. Audit log created automatically by trigger.",
        "record_id": record_id,
    }), 201


@app.route("/data", methods=["GET"])
def get_data():
    """Return all data records."""
    records = db.get_all_data_records()
    return jsonify({"count": len(records), "records": records})


# =========================================================================
# BLOCKCHAIN VERIFICATION
# =========================================================================

@app.route("/verify", methods=["GET"])
def verify():
    """
    Verify the integrity of the audit log chain.

    Walks through every audit_logs row and checks that each
    previous_hash matches the prior row's current_hash.
    """
    result = verify_chain()
    return jsonify(result)


# =========================================================================
# USERS
# =========================================================================

@app.route("/users", methods=["GET"])
def get_users():
    """Return all users with their roles."""
    users = db.get_all_users()
    return jsonify({"count": len(users), "users": users})


# =========================================================================
# ALERTS
# =========================================================================

@app.route("/alerts", methods=["GET"])
def get_alerts():
    """Return all alerts."""
    alerts = db.get_all_alerts()
    return jsonify({"count": len(alerts), "alerts": alerts})


# =========================================================================
# SEARCH (SQL queries)
# =========================================================================

@app.route("/search/user/<username>", methods=["GET"])
def search_user(username):
    """Search logs by username. SQL: WHERE username LIKE '%name%'."""
    results = db.search_logs_by_user(username)
    return jsonify({"query": f"user LIKE '%{username}%'", "count": len(results), "results": results})


@app.route("/search/action/<action_type>", methods=["GET"])
def search_action(action_type):
    """Search logs by action type. SQL: WHERE action_type = ?."""
    results = db.search_logs_by_action(action_type)
    return jsonify({"query": f"action_type = '{action_type}'", "count": len(results), "results": results})


@app.route("/search/date", methods=["GET"])
def search_date():
    """Search logs by date range. SQL: WHERE action_time BETWEEN ? AND ?."""
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    if not start or not end:
        return jsonify({"error": "Provide 'start' and 'end' params (YYYY-MM-DD)."}), 400
    results = db.search_logs_by_date(start, end)
    return jsonify({"query": f"BETWEEN '{start}' AND '{end}'", "count": len(results), "results": results})


# =========================================================================
# SUMMARY (GROUP BY aggregations)
# =========================================================================

@app.route("/summary", methods=["GET"])
def summary():
    """Aggregated stats using SQL GROUP BY."""
    return jsonify({
        "by_action": db.get_action_summary(),
        "by_user": db.get_user_summary(),
        "total_logs": db.get_audit_log_count(),
    })


# =========================================================================
# RUN
# =========================================================================

if __name__ == "__main__":
    print("\n  Audit Chain API starting...")
    print("  -> http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
