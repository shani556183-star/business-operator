"""
SEO Audit analyzer.

IMPORTANT ARCHITECTURE NOTE:
This sandbox's outbound network is allow-listed to package registries only
(pypi, npm, github, etc.) -- confirmed by a direct test that returned 403 for
a plain external domain. So this module does NOT fetch live websites itself.

Real flow right now (Stage 1, manual):
  1. Claude (in chat) uses its own web_fetch tool to pull the real page HTML.
  2. That HTML is saved to a file or passed as a string into analyze_html().
  3. This module does the actual parsing/analysis -- no fabrication, no
     guessing at things it can't see.

Future flow (Stage 2/3, automated):
  A GitHub Actions workflow (which DOES have normal internet access, unlike
  this sandbox) would run a fetch step + call this same analyzer.

Every finding includes its own evidence and a confidence label so nothing
gets silently presented as a fact when it's actually an inference.
"""

from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Finding:
    issue: str
    severity: str          # LOW / MEDIUM / HIGH
    evidence: str           # what was actually observed
    recommended_fix: str
    confidence: str          # VERIFIED_FACT / ESTIMATE / NOT_VERIFIED


NOT_VERIFIED = "NOT VERIFIED — requires external tool/data source"


def analyze_html(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    findings = []

    # --- Title tag ---
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None
    if not title:
        findings.append(Finding(
            "Missing <title> tag", "HIGH",
            "No <title> element found in <head>.",
            "Add a unique, descriptive title (50-60 chars) including primary keyword + location if local business.",
            "VERIFIED_FACT",
        ))
    elif len(title) > 60:
        findings.append(Finding(
            "Title tag too long", "LOW",
            f"Title is {len(title)} characters: \"{title}\"",
            "Shorten to under 60 characters so it doesn't get truncated in search results.",
            "VERIFIED_FACT",
        ))

    # --- Meta description ---
    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc_content = meta_desc.get("content", "").strip() if meta_desc else None
    if not desc_content:
        findings.append(Finding(
            "Missing meta description", "HIGH",
            "No <meta name=\"description\"> tag found.",
            "Add a 140-160 character description summarizing the page and including a call to action.",
            "VERIFIED_FACT",
        ))
    else:
        if title and desc_content:
            # crude consistency check: does description mention what title mentions?
            title_words = set(w.lower().strip(",.-") for w in title.split() if len(w) > 3)
            desc_words = set(w.lower().strip(",.-") for w in desc_content.split() if len(w) > 3)
            overlap = title_words & desc_words
            if len(overlap) < max(1, len(title_words) // 4):
                findings.append(Finding(
                    "Title/meta description may be inconsistent", "MEDIUM",
                    f"Title: \"{title}\" | Description: \"{desc_content}\" -- low keyword overlap.",
                    "Align the description with everything promised in the title (e.g. all locations/services named in the title).",
                    "ESTIMATE",
                ))
        if len(desc_content) > 160:
            findings.append(Finding(
                "Meta description too long", "LOW",
                f"{len(desc_content)} characters.",
                "Trim to under 160 characters.",
                "VERIFIED_FACT",
            ))

    # --- Legacy meta keywords tag ---
    meta_kw = soup.find("meta", attrs={"name": "keywords"})
    if meta_kw and meta_kw.get("content"):
        findings.append(Finding(
            "Legacy <meta name=\"keywords\"> tag present", "LOW",
            "Google has not used this tag as a ranking signal since 2009.",
            "Safe to remove; not harmful, but signals the site hasn't had an SEO pass recently.",
            "VERIFIED_FACT",
        ))

    # --- Heading structure ---
    h1s = soup.find_all("h1")
    if len(h1s) == 0:
        findings.append(Finding(
            "No H1 heading found", "HIGH",
            "Zero <h1> tags on the page.",
            "Add exactly one H1 that includes the primary keyword.",
            "VERIFIED_FACT",
        ))
    elif len(h1s) > 1:
        findings.append(Finding(
            "Multiple H1 headings", "MEDIUM",
            f"{len(h1s)} <h1> tags found: {[h.get_text(strip=True)[:40] for h in h1s]}",
            "Keep a single H1 per page; demote the rest to H2.",
            "VERIFIED_FACT",
        ))
    else:
        h1_text = h1s[0].get_text(strip=True)
        if title and h1_text.lower() not in title.lower() and not any(
            w.lower() in h1_text.lower() for w in title.split() if len(w) > 4
        ):
            findings.append(Finding(
                "H1 doesn't reinforce the title's target keyword", "MEDIUM",
                f"H1: \"{h1_text}\" | Title: \"{title}\"",
                "Rework the H1 to include the same core keyword as the title tag.",
                "ESTIMATE",
            ))

    # --- Images missing alt text ---
    imgs = soup.find_all("img")
    missing_alt = [img for img in imgs if not img.get("alt", "").strip()]
    if imgs and missing_alt:
        findings.append(Finding(
            "Images missing alt text", "MEDIUM",
            f"{len(missing_alt)} of {len(imgs)} <img> tags have no (or empty) alt attribute.",
            "Add descriptive alt text to every product/content image for accessibility and image search.",
            "VERIFIED_FACT",
        ))

    # --- Structured data ---
    ld_json = soup.find_all("script", attrs={"type": "application/ld+json"})
    if not ld_json:
        findings.append(Finding(
            "No structured data (schema.org) detected", "MEDIUM",
            "No <script type=\"application/ld+json\"> blocks found in fetched HTML.",
            "Add LocalBusiness/Organization schema so search engines can build rich results (hours, address, reviews).",
            "ESTIMATE",  # HTML fetch may not always capture JS-injected schema, hence not VERIFIED_FACT
        ))

    # --- Word count (thin content check) ---
    body = soup.find("body")
    text = body.get_text(separator=" ", strip=True) if body else ""
    word_count = len(text.split())
    if word_count < 300:
        findings.append(Finding(
            "Thin content on page", "MEDIUM",
            f"Approximately {word_count} visible words detected on this page.",
            "Expand with genuinely useful content (buying guides, FAQs) -- thin pages rank poorly.",
            "ESTIMATE",
        ))

    # Always-flag unverifiable metrics so nobody downstream invents them
    unverifiable = [
        {"metric": "Organic traffic", "status": NOT_VERIFIED},
        {"metric": "Keyword rankings", "status": NOT_VERIFIED},
        {"metric": "Backlink count / Domain Authority", "status": NOT_VERIFIED},
        {"metric": "Core Web Vitals / page speed score", "status": NOT_VERIFIED},
        {"metric": "Search volume for target keywords", "status": NOT_VERIFIED},
    ]

    return {
        "url": url,
        "title": title,
        "meta_description": desc_content,
        "word_count": word_count,
        "findings": [asdict(f) for f in findings],
        "unverifiable_metrics": unverifiable,
    }


if __name__ == "__main__":
    # Self-test using a fixture built from REAL observed data
    # (Faller's Furniture, fallersfurniture.com -- fetched live via Claude's
    # web_fetch tool in chat on 2026-08-31; this is a minimal reconstruction
    # of the relevant <head> elements for testing this parser, not a claim
    # that this is the full page source).
    fixture_html = """
    <html><head>
      <title>Furniture, Mattresses in Clarion, Shippenville and Knox PA | Faller's Furniture</title>
      <meta name="description" content="Faller's Furniture is a family owned Furniture, Mattresses store located in Clarion, PA. We offer the best in home Furniture, Mattresses at discount prices.">
      <meta name="keywords" content="Faller's Furniture, Clarion, home, furniture, chests, chairs">
    </head><body>
      <h1>Your home. your way. Since 1847</h1>
      <img src="logo.png">
      <p>Faller's Furniture is family owned and has proudly served our area for five generations.</p>
    </body></html>
    """
    import json
    result = analyze_html(fixture_html, "https://www.fallersfurniture.com/")
    print(json.dumps(result, indent=2))
