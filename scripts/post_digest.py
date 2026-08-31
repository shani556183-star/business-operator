"""
Posts a GitHub Issue listing every pending (unapproved) outreach draft.
This is how the owner approves things WITHOUT needing to open a chat with
Claude — GitHub's own mobile app sends a push notification for new issues,
and the owner can just comment on it from their phone.

Runs as a step in daily_seo_scan.yml, after run_daily_scan.py.
Uses the GitHub REST API via the GITHUB_TOKEN GitHub Actions provides
automatically — no extra credential setup needed for this part.
"""

import json
import os
import requests

BASE = os.path.join(os.path.dirname(__file__), "..")
OUTREACH_PATH = os.path.join(BASE, "memory", "outreach.json")

REPO = os.environ.get("GITHUB_REPOSITORY", "")  # e.g. "hassan/business-operator"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = f"https://api.github.com/repos/{REPO}/issues"


def load_pending():
    if not os.path.exists(OUTREACH_PATH):
        return []
    with open(OUTREACH_PATH) as f:
        data = json.load(f)
    return [o for o in data if not o.get("approved")]


def build_issue_body(pending):
    lines = [
        "New outreach drafts are ready for approval.",
        "",
        "**To approve:** comment below with `APPROVE` followed by the IDs, e.g. `APPROVE 1,3,7`",
        "**To skip all:** just don't comment — nothing gets sent either way until approved.",
        "",
    ]
    for item in pending:
        lines.append(f"### #{item['outreach_id']} — {item['company']}")
        lines.append(f"**To:** {item.get('contact_email', item.get('website', 'unknown'))}")
        lines.append(f"**Subject:** {item['subject']}")
        lines.append("")
        lines.append(f"> {item['body'].replace(chr(10), chr(10) + '> ')}")
        lines.append("")
    return "\n".join(lines)


def post_issue(title: str, body: str):
    if not TOKEN or not REPO:
        print("No GITHUB_TOKEN/GITHUB_REPOSITORY in environment — skipping issue post (expected outside Actions).")
        return None
    resp = requests.post(
        API,
        headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"},
        json={"title": title, "body": body, "labels": ["outreach-approval"]},
    )
    resp.raise_for_status()
    return resp.json()


def main():
    pending = load_pending()
    if not pending:
        print("No pending drafts — nothing to post.")
        return
    body = build_issue_body(pending)
    title = f"Outreach approval needed — {len(pending)} draft(s)"
    result = post_issue(title, body)
    if result:
        print(f"Posted issue #{result['number']}: {result['html_url']}")


if __name__ == "__main__":
    main()
