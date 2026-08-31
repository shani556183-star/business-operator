# Business Operator — Foundation (Stage 1)

Minimal, general-purpose business system. SEO Audit is the first experiment,
not the whole system — see `memory/opportunities.json` for other tracked
opportunities (e.g. lead research, currently PAUSED).

## What's real vs what's next

**Actually built and tested (you can run these yourself):**
- `core/opportunity_model.py` — data schema every opportunity must follow
- `core/approval_system.py` — Level A/B/C gate; Level C actions (send outreach,
  accept orders, handle payment) are hard-blocked in code until approved
- `modules/seo_audit/analyzer.py` — real BeautifulSoup analysis, tested against
  a reconstruction of the real fallersfurniture.com HTML (see bottom of file)
- `modules/seo_audit/report_generator.py` — turns analyzer output into the
  client-facing report at `memory/sample_report_fallers_furniture.md`
- `memory/*.json` — real opportunity, experiment, prospect, and outreach data
  from this session (10 real prospects, not fabricated)

**Known limitation (see `logs/decisions.log`):**
This sandbox cannot reach arbitrary websites over the network (tested: 403 on
example.com). It's allow-listed to package registries only. So right now,
Claude fetches each prospect's site via its own `web_fetch` tool in chat, and
this code analyzes the HTML that gets passed in — the crawler is not a live,
self-running bot yet. A future GitHub Actions workflow (free, normal internet
access) is the correct place to make it fully autonomous — that's Stage 3.

## How to run it yourself

```bash
cd modules/seo_audit
python3 analyzer.py           # runs self-test against Faller's fixture
python3 report_generator.py   # produces the full markdown report
```

## Approving outreach

Owner says "APPROVE 1" or "APPROVE 1,8" etc. in chat. That updates
`memory/outreach.json` and `logs/approvals.log` — nothing is sent
automatically; sending is still a manual Gmail action per the Level C rule.

## Next milestone

First real reply from a prospect. See `BUSINESS_STATUS.md` for current state.
