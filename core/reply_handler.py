"""
Reply handling — Level A (classify + draft) is automatic and free.
Sending the response is still Level C: owner reads, approves, sends.

This does NOT connect to a live inbox by itself (that needs the Gmail
connector, which the owner authorizes separately). What this module does:
given the text of a reply someone sent, it classifies it and drafts a
response — the same free, rule-based approach as outreach drafting, no LLM
API cost required for the common cases below. Genuinely ambiguous replies
fall through to "UNCLEAR" and get queued for the owner (or Claude-in-chat)
to handle personally rather than guessing.
"""

from enum import Enum
import re


class ReplyType(str, Enum):
    INTERESTED = "INTERESTED"
    QUESTION = "QUESTION"
    PRICE_OBJECTION = "PRICE_OBJECTION"
    NOT_INTERESTED = "NOT_INTERESTED"
    REQUEST_SAMPLE = "REQUEST_SAMPLE"
    REQUEST_CALL = "REQUEST_CALL"
    SPAM = "SPAM"
    UNCLEAR = "UNCLEAR"


# Simple, transparent keyword rules -- not an LLM, so it's free, but it
# also means anything it can't confidently match falls through to UNCLEAR
# rather than guessing.
PATTERNS = {
    ReplyType.NOT_INTERESTED: [r"\bnot interested\b", r"\bno thanks?\b", r"\bunsubscribe\b", r"\bremove me\b"],
    ReplyType.PRICE_OBJECTION: [r"\btoo expensive\b", r"\bcheaper\b", r"\bdiscount\b", r"\bbudget\b"],
    ReplyType.REQUEST_SAMPLE: [r"\bsample\b", r"\bexample\b", r"\bsee (a|an) report\b"],
    ReplyType.REQUEST_CALL: [r"\bcall\b", r"\bphone\b", r"\bschedule a (meeting|time)\b", r"\bzoom\b"],
    ReplyType.INTERESTED: [r"\byes\b", r"\bsounds good\b", r"\binterested\b", r"\bsend it over\b", r"\bgo ahead\b"],
    ReplyType.QUESTION: [r"\?"],
}

RESPONSE_TEMPLATES = {
    ReplyType.INTERESTED: (
        "Great, thanks! I'll get the full SEO health check over to you within "
        "[X business days]. Just to confirm — is {website} the best site to run it on?"
    ),
    ReplyType.REQUEST_SAMPLE: (
        "Of course — here's a sample report so you can see the format: [attach/link sample]. "
        "Happy to run the same thing on your site for $29 if it looks useful."
    ),
    ReplyType.PRICE_OBJECTION: (
        "Totally understand. The $29 covers a full technical + on-page pass with a "
        "prioritized action plan — happy to start with just the top 3 fixes at a lower "
        "price if that's a better fit, just let me know."
    ),
    ReplyType.REQUEST_CALL: (
        "Happy to hop on a quick call. [OWNER: insert your actual availability / booking link here]"
    ),
    ReplyType.NOT_INTERESTED: (
        "No problem at all, thanks for the reply — won't follow up further. Wishing you well!"
    ),
    ReplyType.QUESTION: None,  # genuinely needs a human/Claude-in-chat to read and answer
    ReplyType.SPAM: None,
    ReplyType.UNCLEAR: None,
}


def classify_reply(text: str) -> ReplyType:
    text_lower = text.lower()
    for reply_type, patterns in PATTERNS.items():
        for p in patterns:
            if re.search(p, text_lower):
                return reply_type
    return ReplyType.UNCLEAR


def draft_response(reply_text: str, website: str = "") -> dict:
    reply_type = classify_reply(reply_text)
    template = RESPONSE_TEMPLATES.get(reply_type)
    draft = template.format(website=website) if template else None
    return {
        "classification": reply_type.value,
        "draft_response": draft,
        "needs_human_judgment": draft is None,
        "approved": False,  # always false — owner must approve before sending, no exceptions
    }


if __name__ == "__main__":
    tests = [
        "Yes this sounds good, send it over please",
        "This seems too expensive for us right now",
        "Can we do a quick call about this?",
        "Not interested, please remove me",
        "What exactly is included in the $29 report?",
    ]
    for t in tests:
        print(t, "->", draft_response(t, "example.com"))
