"""
Turns analyzer.py output into a client-facing Markdown report.
No fabrication: every line traces back to a finding with evidence,
or is explicitly marked NOT VERIFIED.
"""

from jinja2 import Template
import datetime

TEMPLATE = Template("""\
# Website SEO Health Check — {{ result.url }}

Prepared: {{ date }}

## Executive Summary

This report covers technical and on-page SEO factors that can be verified
directly from the website's public HTML. It does not include traffic,
rankings, or backlink data — those require a paid tool and are marked
"NOT VERIFIED" below rather than estimated.

**{{ findings|length }} issue(s) found.**

## Issues Found

{% for f in findings -%}
### {{ loop.index }}. {{ f.issue }} — Severity: {{ f.severity }}
- **Evidence:** {{ f.evidence }}
- **Recommended fix:** {{ f.recommended_fix }}
- **Confidence:** {{ f.confidence }}

{% endfor -%}

## Priority Order

{% for f in high_first -%}
{{ loop.index }}. {{ f.issue }} ({{ f.severity }})
{% endfor %}

## Metrics Not Verified in This Report

{% for m in result.unverifiable_metrics -%}
- {{ m.metric }}: {{ m.status }}
{% endfor %}

## Limitations

This audit is based on a single fetch of the homepage HTML. It does not
include: JavaScript-rendered content that isn't in the initial HTML,
internal pages beyond the homepage, real traffic/ranking data, or
competitor comparison. A full engagement would cover all of the above.
""")


def generate_report(result: dict) -> str:
    findings = result["findings"]
    high_first = sorted(findings, key=lambda f: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[f["severity"]])
    return TEMPLATE.render(
        result=result,
        findings=findings,
        high_first=high_first,
        date=datetime.date.today().isoformat(),
    )


if __name__ == "__main__":
    from analyzer import analyze_html

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
    result = analyze_html(fixture_html, "https://www.fallersfurniture.com/")
    print(generate_report(result))
