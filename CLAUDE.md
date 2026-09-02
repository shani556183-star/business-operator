# business-operator

## Workflow

- The user cannot easily upload files to GitHub manually (they previously did it via the GitHub web UI). Claude is authorized to edit files in this repo and commit + push directly to `origin main` on the user's behalf for routine updates (e.g. dashboard changes in `index.html`, data files under `memory/`, scripts) without asking for per-change confirmation.
- Still avoid force-pushes, history rewrites, or destructive git operations without asking first.
- Before pushing, run `git status`/`git diff` to sanity-check what's being committed, and skip committing anything that looks like a secret.
- `index.html` is a dashboard reading `memory/outreach.json`, `memory/prospects_queue.json`, and `memory/customers.json`. Clicking an entry shows the full message; pending approvals have a "Copy APPROVE X" button.
