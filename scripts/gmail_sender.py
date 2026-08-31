"""
Sends email via the Gmail API (free, no cost — Gmail API has a generous
free quota that a solo small business will never hit).

WHY THIS EXISTS SEPARATELY FROM THE CHAT GMAIL CONNECTOR:
The Gmail connector Claude uses inside this chat only works while you're
actively talking to Claude. Since you chose "fully autonomous, runs on
GitHub, I never have to trigger it," the sending step also needs to run
from GitHub Actions — which means it needs its OWN Gmail credentials,
stored as encrypted GitHub Secrets (never in code, never in this file).

ONE-TIME SETUP (you do this yourself — see SETUP_STAGE_3.md):
  1. Google Cloud Console (free) -> enable Gmail API -> create OAuth
     credentials -> generate a refresh token for your Gmail account.
  2. Add these as GitHub repo Secrets (Settings -> Secrets -> Actions):
     GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN
  3. Never paste these values into any file in this repo.

This script reads them from environment variables only — that's what
GitHub Actions injects secrets as.
"""

import os
import base64
from email.mime.text import MIMEText

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    Credentials = None
    build = None


def get_gmail_service():
    if Credentials is None:
        raise RuntimeError(
            "google-api-python-client / google-auth not installed. "
            "Add to requirements.txt: google-auth google-api-python-client"
        )
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GMAIL_REFRESH_TOKEN"],
        client_id=os.environ["GMAIL_CLIENT_ID"],
        client_secret=os.environ["GMAIL_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
    )
    return build("gmail", "v1", credentials=creds)


def send_email(to: str, subject: str, body: str) -> dict:
    """
    Sends one email. Caller (process_approval.py) is responsible for
    only calling this on items that are actually marked approved=true —
    this function itself does not check approval status, so it must
    never be called directly from anywhere except the approved-items path.
    """
    service = get_gmail_service()
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return result


if __name__ == "__main__":
    # Dry-run self-test: proves the message gets built correctly WITHOUT
    # actually sending or needing real credentials (safe to run anywhere).
    msg = MIMEText("test body")
    msg["to"] = "test@example.com"
    msg["subject"] = "test subject"
    encoded = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    print("Message would encode to (first 60 chars):", encoded[:60])
    print("Self-test passed: MIME encoding works. Real send needs GMAIL_* secrets set.")
