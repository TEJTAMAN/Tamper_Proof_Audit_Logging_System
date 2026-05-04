"""
database.py -- MySQL Database Layer
=====================================

Connects to the audit_chain_db MySQL database and provides
functions to read/write data using SQL queries.

REQUIRES: pip install mysql-connector-python
"""

import mysql.connector
import hashlib
from datetime import datetime
from config import MYSQL_CONFIG


def get_connection():
    """
    Create and return a new MySQL connection.

    Each function opens its own connection and closes it when done.
    This avoids threading issues with Flask.
    """
    return mysql.connector.connect(**MYSQL_CONFIG)


# =========================================================================
# DATA RECORDS (the data being audited)
# =========================================================================

def insert_data_record(data_content):
    """
    Insert a new data record.

    The MySQL TRIGGER 'after_insert_record' will automatically:
      1. Get the previous audit log's hash
      2. Compute a new SHA-256 hash
      3. Insert an audit_logs entry

    Args:
        data_content: The data to store (string).

    Returns:
        The new record's ID.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO data_records (data_content) VALUES (%s);",
        (data_content,)
    )
    conn.commit()
    record_id = cursor.lastrowid
    print(f"[DB] Inserted record: {record_id}")
    cursor.close()
    conn.close()
    return record_id


def get_all_data_records():
    """
    SELECT * FROM data_records ORDER BY record_id ASC;
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM data_records ORDER BY record_id ASC;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    # Convert datetime objects to strings for JSON serialization
    for row in rows:
        for key, val in row.items():
            if isinstance(val, datetime):
                row[key] = val.isoformat()
    return rows


# =========================================================================
# AUDIT LOGS (the blockchain chain)
# =========================================================================

def get_all_audit_logs():
    """
    SELECT * FROM audit_logs with user and record info via JOINs.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            al.log_id,
            al.user_id,
            u.username,
            al.record_id,
            dr.data_content,
            al.action_type,
            al.action_time,
            al.current_hash,
            al.previous_hash
        FROM audit_logs al
        LEFT JOIN users u ON al.user_id = u.user_id
        LEFT JOIN data_records dr ON al.record_id = dr.record_id
        ORDER BY al.log_id ASC;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    for row in rows:
        for key, val in row.items():
            if isinstance(val, datetime):
                row[key] = val.isoformat()
    return rows


def get_audit_log_count():
    """SELECT COUNT(*) FROM audit_logs;"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM audit_logs;")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count


def search_logs_by_user(username):
    """
    SELECT audit_logs WHERE username LIKE %username%.
    SQL CONCEPT: JOIN + LIKE for flexible text search.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT al.*, u.username
        FROM audit_logs al
        LEFT JOIN users u ON al.user_id = u.user_id
        WHERE u.username LIKE %s
        ORDER BY al.log_id ASC;
    """, (f"%{username}%",))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    for row in rows:
        for key, val in row.items():
            if isinstance(val, datetime):
                row[key] = val.isoformat()
    return rows


def search_logs_by_action(action_type):
    """
    SELECT audit_logs WHERE action_type = ?.
    SQL CONCEPT: WHERE with exact match.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT al.*, u.username
        FROM audit_logs al
        LEFT JOIN users u ON al.user_id = u.user_id
        WHERE al.action_type = %s
        ORDER BY al.log_id ASC;
    """, (action_type,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    for row in rows:
        for key, val in row.items():
            if isinstance(val, datetime):
                row[key] = val.isoformat()
    return rows


def search_logs_by_date(start_date, end_date):
    """
    SELECT audit_logs WHERE action_time BETWEEN start AND end.
    SQL CONCEPT: BETWEEN for date range queries.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT al.*, u.username
        FROM audit_logs al
        LEFT JOIN users u ON al.user_id = u.user_id
        WHERE al.action_time BETWEEN %s AND %s
        ORDER BY al.log_id ASC;
    """, (start_date, end_date + " 23:59:59"))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    for row in rows:
        for key, val in row.items():
            if isinstance(val, datetime):
                row[key] = val.isoformat()
    return rows


# =========================================================================
# AGGREGATION QUERIES (GROUP BY)
# =========================================================================

def get_action_summary():
    """
    SELECT action_type, COUNT(*) FROM audit_logs GROUP BY action_type;
    SQL CONCEPT: GROUP BY with COUNT aggregate.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT action_type, COUNT(*) AS count
        FROM audit_logs
        GROUP BY action_type
        ORDER BY count DESC;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_user_summary():
    """
    SELECT username, COUNT(*) FROM audit_logs GROUP BY user_id;
    SQL CONCEPT: JOIN + GROUP BY across two tables.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.username, COUNT(*) AS count
        FROM audit_logs al
        JOIN users u ON al.user_id = u.user_id
        GROUP BY al.user_id
        ORDER BY count DESC;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


# =========================================================================
# USERS
# =========================================================================

def get_all_users():
    """SELECT users with their role names."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.user_id, u.username, r.role_name
        FROM users u
        LEFT JOIN role r ON u.role_id = r.role_id
        ORDER BY u.user_id ASC;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


# =========================================================================
# BLOCKCHAIN LOGS
# =========================================================================

def get_all_blockchain_logs():
    """SELECT * FROM blockchain_logs."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT bl.*, al.current_hash AS audit_hash
        FROM blockchain_logs bl
        LEFT JOIN audit_logs al ON bl.log_id = al.log_id
        ORDER BY bl.bc_log_id ASC;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    for row in rows:
        for key, val in row.items():
            if isinstance(val, datetime):
                row[key] = val.isoformat()
    return rows


# =========================================================================
# ALERTS
# =========================================================================

def get_all_alerts():
    """SELECT * FROM alert."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, al.action_type, u.username
        FROM alert a
        LEFT JOIN audit_logs al ON a.log_id = al.log_id
        LEFT JOIN users u ON al.user_id = u.user_id
        ORDER BY a.created_at DESC;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    for row in rows:
        for key, val in row.items():
            if isinstance(val, datetime):
                row[key] = val.isoformat()
    return rows


def insert_alert(log_id, message):
    """Insert a new alert."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO alert (log_id, alert_message) VALUES (%s, %s);",
        (log_id, message)
    )
    conn.commit()
    cursor.close()
    conn.close()
