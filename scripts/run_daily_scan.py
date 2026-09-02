"""
Runs automatically every day via GitHub Actions (see .github/workflows/daily_seo_scan.yml).

What this does WITHOUT costing any money (no LLM call needed for this part):
  1. Reads memory/prospects_queue.json — a list of website URLs waiting to be scanned.
  2. For each one: fetches the real page (GitHub Actions has normal internet access,
     unlike the sandbox this was originally built in), runs the same analyzer.py
     we already tested against Faller's Furniture, generates a report.
  3. Builds a templated outreach draft using the REAL findings (not invented) —
     rule-based personalization, not an LLM, so it's free.
  4. Writes everything to memory/outreach.json as approved=false (Level C — never
     auto-sends) and updates BUSINESS_STATUS.md.

What this deliberately does NOT do (see README for why):
  - It does not discover brand-new prospects on its own. Finding genuinely new
    businesses to target requires reasoning/search that either needs a paid LLM
    API call or a human (owner or Claude-in-chat) to add URLs to
    prospects_queue.json periodically. This is flagged, not silently skipped.
  - It never sends anything. Sending requires owner approval every time.
"""

import json
import os
import sys
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "modules", "seo_audit"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))

import requests
from analyzer import analyze_html
from report_generator import generate_report
from approval_system import request_approval

BASE = os.path.join(os.path.dirname(__file__), "..")
QUEUE_PATH = os.path.join(BASE, "memory", "prospects_queue.json")
OUTREACH_PATH = os.path.join(BASE, "memory", "outreach.json")
STATUS_PATH = os.path.join(BASE, "BUSINESS_STATUS.md")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def build_draft(company: str, result: dict) -> str:
    """Rule-based (not LLM) outreach draft, built only from real findings."""
    top_issue = result["findings"][0] if result["findings"] else None
    if not top_issue:
        return None  # nothing genuine to say — do NOT invent an issue
    return (
        f"Hi,\n\n"
        f"I came across {company}'s website while researching local businesses "
        f"and noticed something worth a quick look: {top_issue['evidence']} "
        f"({top_issue['issue']}).\n\n"
        f"{top_issue['recommended_fix']}\n\n"
        f"I do a quick $29 SEO health check covering this and a few other things — "
        f"happy to send the full report over if useful."
    )


def already_drafted(website: str, outreach: list) -> bool:
    """Prevents re-drafting the same company every single day."""
    return any(o.get("website") == website for o in outreach)


def main():
    queue = load_json(QUEUE_PATH, [])
    outreach = load_json(OUTREACH_PATH, [])
    next_id = max([o["outreach_id"] for o in outreach], default=0) + 1

    processed, skipped_no_findings, skipped_duplicate, errors = 0, 0, 0, 0
    new_entries = []

    for item in queue:
        url, company = item["url"], item["company"]

        if already_drafted(url, outreach):
            skipped_duplicate += 1
            continue

        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
        except Exception as e:
            errors += 1
            with open(os.path.join(BASE, "logs", "errors.log"), "a") as f:
                f.write(f"{datetime.datetime.utcnow().isoformat()} | FETCH_FAILED | {url} | {e}\n")
            continue

        result = analyze_html(resp.text, url)
        draft = build_draft(company, result)
        if not draft:
            skipped_no_findings += 1
            continue

        entry = {
            "outreach_id": next_id,
            "company": company,
            "website": url,
            "subject": f"Quick note about {url}",
            "body": draft,
            "personalization_basis": "FULLY_FETCHED — automated daily scan",
            "approved": False,
        }
        outreach.append(entry)
        new_entries.append(entry)
        request_approval("send_outreach", str(next_id), f"Outreach for {company}")
        next_id += 1
        processed += 1

    save_json(OUTREACH_PATH, outreach)

    with open(os.path.join(BASE, "logs", "daily.log"), "a") as f:
        f.write(
            f"{datetime.datetime.utcnow().isoformat()} | DAILY_SCAN | "
            f"processed={processed} skipped_no_findings={skipped_no_findings} "
            f"skipped_duplicate={skipped_duplicate} errors={errors}\n"
        )

    # keep BUSINESS_STATUS.md's pending-approval count honest and current
    pending = sum(1 for o in outreach if not o["approved"])
    if os.path.exists(STATUS_PATH):
        with open(STATUS_PATH) as f:
            status = f.read()
        import re
        status = re.sub(
            r"Pending owner approval: \d+ drafts",
            f"Pending owner approval: {pending} drafts",
            status,
        )
        with open(STATUS_PATH, "w") as f:
            f.write(status)

    print(f"Done. New drafts: {len(new_entries)}. Errors: {errors}. All new drafts need owner APPROVE.")


if __name__ == "__main__":
    main()
