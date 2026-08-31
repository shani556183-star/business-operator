# BUSINESS STATUS

Last updated: 2026-08-31

## Current Experiment
- ID: EXP-001
- Opportunity: AI-Powered Website SEO Health Check
- Status: TESTING (Stage 1 — Sellability Test)

## Current Offer
- Name: Website SEO Health Check
- Price: $29 (single package, Fiverr-market-based)
- Package tiers defined but only Starter is being actively tested

## Prospects
- Total researched (verified real): 10
- Fully deep-audited (sample ready): 1 (Faller's Furniture)
- Outreach drafts ready: 2 (full), 8 (template-level, need per-site verification pass)

## Outreach
- Sent: 0
- Approved by owner: 0
- Pending owner approval: 6 drafts

## Replies
- 0 (no outreach sent yet)

## Customers
- 0

## Revenue
- $0

## Costs
- $0

## Conversion Rate
- N/A (no outreach sent yet)

## Known Problems / Blockers
1. Sandbox (this container) cannot make live HTTP requests to arbitrary business
   websites — outbound network is allow-listed to package registries (pypi, npm,
   github, etc.) only. Confirmed by direct test (see /logs/decisions.log).
   → Live website fetching for audits must go through Claude's own web_fetch
     tool (this chat), not through Python code running in this sandbox.
   → For a future always-on crawler, GitHub Actions (public repo, free) has
     unrestricted internet and is the correct place to run it — not this sandbox.
2. Email verification (Hunter.io free tier) capped at 50 credits/month — not
   relevant to the SEO experiment, but relevant if we ever revive the lead-gen
   experiment.

## Lessons So Far
- Fiverr lead-gen category has 1970+ competing sellers — high competition.
- SEO audit delivery has NO paid-tool dependency (unlike lead research), which
  is why it was selected as the first experiment over B2B lead lists.

## Next Action (blocking on OWNER)
Owner needs to reply with which outreach drafts to approve, e.g. "APPROVE 1-10"
or "APPROVE 1,2" — nothing gets sent until this happens.

## Owner Approvals Needed
- [ ] Approve which of the 10 outreach drafts to send
- [ ] Confirm $29 starting price is acceptable
