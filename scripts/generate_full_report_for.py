"""
On-demand full SEO audit PDF generator.

Run this once a client replies "yes, I want the audit" -- it produces the
complete, real, PDF report ready to attach to an email.

Usage:
    python scripts/generate_full_report_for.py <url> [company_name]

What it does:
  1. Fetches the client's real, live page (same requests pattern as
     scripts/run_daily_scan.py).
  2. Runs it through modules/seo_audit/analyzer.py's analyze_html() -- the
     same real, non-fabricated on-page findings the rest of this project
     already uses (every finding carries its own evidence and a confidence
     label; anything that can't be verified from the HTML -- traffic,
     rankings, backlinks, page speed -- is listed as NOT VERIFIED, never
     estimated or invented).
  3. Turns the findings into the full Markdown report via
     modules/seo_audit/report_generator.py (Executive Summary, every issue
     with evidence/fix/confidence, Priority Order, unverified metrics,
     Limitations).
  4. Converts that Markdown into a PDF, saved under reports/.
  5. Prints where the PDF landed and appends a line to logs/reports.log.

What it deliberately does NOT do: send anything anywhere. Emailing the
PDF to the client is the owner's own manual step (send_outreach is an
OWNER_REQUIRED / Level C action per core/approval_system.py -- this script
doesn't touch that system at all, it only ever produces a local file).
"""

import argparse
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "modules", "seo_audit"))

import requests
import markdown as md_lib
from xhtml2pdf import pisa

from analyzer import analyze_html
from report_generator import generate_report

BASE = os.path.join(os.path.dirname(__file__), "..")
REPORTS_DIR = os.path.join(BASE, "reports")
LOG_PATH = os.path.join(BASE, "logs", "reports.log")

# Minimal print styling -- report_generator.py's template is plain
# Markdown (#/##/### headers, "- **Label:** value" bullets, a numbered
# Priority Order list), so a light CSS pass is enough to make the PDF
# readable without pulling in a heavier templating step.
PDF_CSS = """
<style>
  body { font-family: Helvetica, Arial, sans-serif; font-size: 11pt; color: #1a1a1a; line-height: 1.5; }
  h1 { font-size: 20pt; margin-bottom: 4px; }
  h2 { font-size: 15pt; margin-top: 22px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }
  h3 { font-size: 12.5pt; margin-top: 16px; margin-bottom: 4px; }
  ul, ol { margin-top: 4px; }
  strong { color: #111; }
</style>
"""


def slugify(url: str) -> str:
    host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
    return re.sub(r"[^a-z0-9]+", "-", host.lower()).strip("-")


def log(line: str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{datetime.datetime.now(datetime.timezone.utc).isoformat()} | {line}\n")


def generate_pdf_for(url: str, company: str | None = None) -> tuple[str, int]:
    resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    result = analyze_html(resp.text, url)
    report_md = generate_report(result)

    html_body = md_lib.markdown(report_md, extensions=["sane_lists"])
    full_html = f"<html><head>{PDF_CSS}</head><body>{html_body}</body></html>"

    os.makedirs(REPORTS_DIR, exist_ok=True)
    slug = slugify(url)
    date_str = datetime.date.today().isoformat()
    pdf_path = os.path.join(REPORTS_DIR, f"{slug}-{date_str}.pdf")

    with open(pdf_path, "wb") as f:
        pisa_status = pisa.CreatePDF(full_html, dest=f)
    if pisa_status.err:
        raise RuntimeError(f"PDF generation failed for {url} ({pisa_status.err} error(s))")

    finding_count = len(result["findings"])
    log(f"REPORT_GENERATED | {url} | {company or ''} | {finding_count} findings | {pdf_path}")
    return pdf_path, finding_count


def main():
    parser = argparse.ArgumentParser(
        description="Generate a full SEO audit PDF for one client, ready to attach to an email. Does not send anything."
    )
    parser.add_argument("url", help="The client's website URL")
    parser.add_argument("company", nargs="?", default=None, help="Company name (optional, for the log only)")
    args = parser.parse_args()

    try:
        pdf_path, finding_count = generate_pdf_for(args.url, args.company)
    except Exception as e:
        print(f"FAILED to generate report for {args.url}: {e}")
        log(f"REPORT_FAILED | {args.url} | {args.company or ''} | {e}")
        sys.exit(1)

    print(f"\nPDF ready: {pdf_path}")
    print(f"{finding_count} issue(s) found on {args.url}.")
    print("Nothing was sent -- attach this file to an email yourself when ready.")


if __name__ == "__main__":
    main()
