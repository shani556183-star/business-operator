# BUSINESS STATUS

Last updated: 2026-09-14

## Current Experiment
- ID: EXP-001
- Opportunity: AI-Powered Website SEO Health Check
- Status: TESTING (Stage 1 — Sellability Test)

## Current Offer
- Name: Website SEO Health Check
- Price: $29 (single package, Fiverr-market-based)
- Package tiers defined but only Starter is being actively tested

## Prospects
- Total researched (verified real): 127 (10 original + 117 from the 2026-09-14 batch scan
  across furniture, hardware, garden/pet, and bike/florist retailers)
- Fully deep-audited (real analyzer findings, not fabricated): 117
- Outreach drafts ready to send (verified email + completed audit): 63 (2 original + 61 new)
- Audited but no verified email found yet (not draft-ready): 55 — tracked in prospects.json
  for a future targeted email-discovery pass, deliberately NOT drafted as outreach

## Outreach
- Sent: 0
- Approved by owner: 2 (pre-existing, from before this batch)
- Pending owner approval: 77 drafts (63 fully ready-to-send with verified email, 16 older
  template-level drafts without a verified email)

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
