# Making This Actually Run By Itself (Stage 3 setup)

## What becomes fully automatic after this setup

Once this is on GitHub, `.github/workflows/daily_seo_scan.yml` runs
`scripts/run_daily_scan.py` **every day at 8am UTC, forever, for $0** —
no one needs to open a chat or click anything for this part:

- Fetches every URL in `memory/prospects_queue.json` (real internet — GitHub
  Actions is not restricted like the sandbox this was built in, confirmed by
  the test above: sandbox = 403, this is designed to run where fetch succeeds)
- Runs the same tested `analyzer.py` against each real site
- Builds a rule-based outreach draft from the REAL findings only (no LLM,
  so no cost, and it flatly refuses to draft anything if there's no genuine
  finding — see `build_draft()`, returns `None` rather than inventing an issue)
- Adds it to `memory/outreach.json` as `approved: false` and logs a pending
  approval in `core/approval_system.py` — nothing sends itself, ever
- Commits the results back to the repo automatically

## What you need to do ONCE (I can't do these for you — account creation
and credential entry are things only you should do)

1. Create a free GitHub account (if you don't have one) and a new **public**
   repo — public is what keeps Actions free and unlimited.
2. Push everything in this `business-operator/` folder to that repo.
3. **For fully autonomous sending (no chat needed):**
   a. Go to Google Cloud Console (console.cloud.google.com) — free.
   b. Create a project, enable the "Gmail API".
   c. Create OAuth 2.0 credentials (Desktop app type), download client ID + secret.
   d. Use Google's OAuth Playground (developers.google.com/oauthplayground) with
      your own client ID/secret to authorize `gmail.send` scope for your
      Gmail account and generate a refresh token.
   e. In your GitHub repo: Settings -> Secrets and variables -> Actions ->
      New repository secret. Add three secrets:
      `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`.
      **Never put these values in any file that gets committed to the repo.**
4. That's it. From here on:
   - Every day at 8am UTC: site scan runs, drafts get created, and a GitHub
     Issue is posted listing them.
   - GitHub's mobile app (free) can push-notify you when that issue is posted.
   - You comment `APPROVE 1,3` (or `APPROVE 1-10` for a range) on that issue,
     from your phone, from anywhere.
   - `process_approval.yml` triggers automatically on your comment, sends
     ONLY those emails via the Gmail API, and logs everything.
   - **Safety check already built in:** the workflow only acts on comments
     from the repo owner's own GitHub account — a random person can't
     trigger a send even though the repo is public.

## The ONE thing that genuinely costs money (flagged per the zero-budget rule)

```
TOOL: Claude API (or similar LLM)
COST: Roughly a few cents to a few dollars per month, depending on volume
WHY NEEDED: Finding genuinely NEW prospects (businesses we haven't already
  queued) requires reasoning + web search — the daily script above can only
  process a queue that's already been filled in. It can't discover new
  companies on its own for free; that's what I (Claude, in this chat) do
  when you ask me to research more prospects.
FREE ALTERNATIVE: Keep discovery manual — every so often, ask me in chat to
  research N more prospects (like I did for the first 10), and I'll add
  them to prospects_queue.json. The daily scan then handles the rest
  (fetch, analyze, draft) for free, automatically, every night.
EXPECTED BENEFIT: True 24/7 discovery without you asking. Only worth paying
  for once there's real revenue to justify it — not before.
```

**My recommendation:** don't pay for this yet. Keep discovery as a periodic
chat request (free) until the SEO experiment has an actual paying customer.
Then it's a real business decision, not a guess.

## Honest automation percentage for THIS specific workflow

| Step | Automated? |
|---|---|
| Fetch + analyze + draft for queued prospects | 100% automatic, $0, runs daily |
| Discover brand-new prospects to add to the queue | Manual (chat request) or costs money |
| Approve which drafts get sent | Always you |
| Actually sending | Always you (or Gmail connector with per-send approval) |
| Accepting orders / payment | Always you |
