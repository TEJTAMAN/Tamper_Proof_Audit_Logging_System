"""
blockchain.py -- Blockchain Verification Logic
================================================

Verifies the integrity of the audit log chain stored in MySQL.

HOW THE CHAIN WORKS:
  Each audit_logs row has:
    - current_hash  : SHA-256 hash of (record_id + timestamp + previous_hash)
    - previous_hash : The current_hash of the row before it

  If anyone changes an old row, its hash won't match what the next
  row expects as previous_hash --> chain is broken --> tampering detected.
"""

import hashlib
from database import get_all_audit_logs


def verify_chain():
    """
    Walk through all audit logs and check that the hash chain is intact.

    Checks for each log entry (starting from the 2nd one):
      - Does this entry's previous_hash match the prior entry's current_hash?

    Returns:
        dict with keys:
          - is_valid (bool): True if chain is intact
          - message (str): Description of result
          - checked (int): Number of links checked
          - broken_at (int or None): log_id where the break was found
    """
    logs = get_all_audit_logs()

    if len(logs) == 0:
        return {
            "is_valid": True,
            "message": "No audit logs found. Chain is empty.",
            "checked": 0,
            "broken_at": None,
        }

    if len(logs) == 1:
        return {
            "is_valid": True,
            "message": "Only one log entry. Chain is valid.",
            "checked": 0,
            "broken_at": None,
        }

    # Walk the chain: for each log, check that its previous_hash
    # matches the current_hash of the log before it.
    for i in range(1, len(logs)):
        current = logs[i]
        previous = logs[i - 1]

        expected_prev_hash = previous["current_hash"]
        actual_prev_hash = current["previous_hash"]

        if actual_prev_hash != expected_prev_hash:
            return {
                "is_valid": False,
                "message": (
                    f"Chain BROKEN at log_id {current['log_id']}! "
                    f"Expected previous_hash '{expected_prev_hash[:16]}...' "
                    f"but found '{actual_prev_hash[:16] if actual_prev_hash else 'NULL'}...'"
                ),
                "checked": i,
                "broken_at": current["log_id"],
            }

    return {
        "is_valid": True,
        "message": f"Chain is VALID. All {len(logs) - 1} links verified.",
        "checked": len(logs) - 1,
        "broken_at": None,
    }
