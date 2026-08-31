"""
Triggered when the owner comments on the approval issue (see
.github/workflows/process_approval.yml). Parses "APPROVE 1,3,7" (any
spacing/casing) from the comment, marks exactly those outreach IDs as
approved, and sends ONLY those — nothing else, ever, regardless of what
else is pending.

This is the one file in the whole system that is allowed to call
gmail_sender.send_email(). Nothing else does, on purpose — one clear
choke point makes it easy to verify nothing sends without approval.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))

from gmail_sender import send_email
from approval_system import approve as mark_approved_in_log

BASE = os.path.join(os.path.dirname(__file__), "..")
OUTREACH_PATH = os.path.join(BASE, "memory", "outreach.json")


def parse_approved_ids(comment_text: str) -> list:
    """Supports both 'APPROVE 1,3,7' and 'APPROVE 1-10' (range) formats."""
    match = re.search(r"approve\s+([\d,\-\s]+)", comment_text, re.IGNORECASE)
    if not match:
        return []
    ids = []
    for part in match.group(1).split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            if start.strip().isdigit() and end.strip().isdigit():
                ids.extend(range(int(start.strip()), int(end.strip()) + 1))
        elif part.isdigit():
            ids.append(int(part))
    return sorted(set(ids))


def main():
    comment_text = os.environ.get("APPROVAL_COMMENT", "")
    approved_ids = parse_approved_ids(comment_text)

    if not approved_ids:
        print("No valid 'APPROVE n,n,n' pattern found in comment — nothing sent.")
        return

    with open(OUTREACH_PATH) as f:
        outreach = json.load(f)

    sent, failed = [], []
    for item in outreach:
        if item["outreach_id"] not in approved_ids:
            continue
        if item.get("approved") and item.get("sent_at"):
            print(f"#{item['outreach_id']} already sent previously — skipping (no duplicate sends).")
            continue
        item["approved"] = True
        to_addr = item.get("contact_email")
        if not to_addr:
            print(f"#{item['outreach_id']} has no contact_email on file — cannot send, flagging for manual send.")
            failed.append(item["outreach_id"])
            continue
        try:
            send_email(to_addr, item["subject"], item["body"])
            item["sent_at"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
            sent.append(item["outreach_id"])
        except Exception as e:
            failed.append(item["outreach_id"])
            with open(os.path.join(BASE, "logs", "errors.log"), "a") as ef:
                ef.write(f"SEND_FAILED | outreach_id={item['outreach_id']} | {e}\n")

    with open(OUTREACH_PATH, "w") as f:
        json.dump(outreach, f, indent=2)

    mark_approved_in_log([str(i) for i in approved_ids])

    with open(os.path.join(BASE, "logs", "daily.log"), "a") as f:
        f.write(f"APPROVAL_PROCESSED | requested={approved_ids} | sent={sent} | failed={failed}\n")

    print(f"Sent: {sent}. Failed/needs manual: {failed}.")


if __name__ == "__main__":
    main()
