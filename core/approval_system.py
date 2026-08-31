"""
Approval system.

Every action the business engine wants to take is classified into one of
three levels. LEVEL_C actions are hard-blocked in code -- not just by
convention -- so a bug elsewhere can't accidentally send an email or
spend money without the owner explicitly approving it first.
"""

from enum import Enum
import json
import os
import datetime


class ApprovalLevel(str, Enum):
    AUTONOMOUS = "AUTONOMOUS"        # Level A - do it, log it
    OWNER_REVIEW = "OWNER_REVIEW"    # Level B - show owner, proceed if no objection
    OWNER_REQUIRED = "OWNER_REQUIRED"  # Level C - hard block until explicit approval


# Action -> required level. This table is the single source of truth.
ACTION_LEVELS = {
    "research": ApprovalLevel.AUTONOMOUS,
    "score_opportunity": ApprovalLevel.AUTONOMOUS,
    "draft_audit": ApprovalLevel.AUTONOMOUS,
    "draft_outreach": ApprovalLevel.AUTONOMOUS,
    "update_memory": ApprovalLevel.AUTONOMOUS,
    "select_major_direction": ApprovalLevel.OWNER_REVIEW,
    "change_pricing": ApprovalLevel.OWNER_REVIEW,
    "launch_new_offer": ApprovalLevel.OWNER_REVIEW,
    "send_outreach": ApprovalLevel.OWNER_REQUIRED,
    "spend_money": ApprovalLevel.OWNER_REQUIRED,
    "sign_contract": ApprovalLevel.OWNER_REQUIRED,
    "accept_order": ApprovalLevel.OWNER_REQUIRED,
    "issue_refund": ApprovalLevel.OWNER_REQUIRED,
    "handle_payment": ApprovalLevel.OWNER_REQUIRED,
    "irreversible_account_change": ApprovalLevel.OWNER_REQUIRED,
}

APPROVAL_LOG = os.path.join(os.path.dirname(__file__), "..", "logs", "approvals.log")
PENDING_PATH = os.path.join(os.path.dirname(__file__), "..", "memory", "pending_approvals.json")


class ApprovalRequiredError(Exception):
    """Raised when code tries to perform a LEVEL_C action without approval on file."""
    pass


def _log(line: str):
    with open(APPROVAL_LOG, "a") as f:
        f.write(f"{datetime.datetime.utcnow().isoformat()} | {line}\n")


def request_approval(action: str, item_id: str, description: str):
    """Queue an item for owner approval. Does NOT perform the action."""
    level = ACTION_LEVELS.get(action, ApprovalLevel.OWNER_REQUIRED)  # default safe
    pending = []
    if os.path.exists(PENDING_PATH):
        with open(PENDING_PATH) as f:
            pending = json.load(f)
    pending.append({
        "action": action,
        "item_id": item_id,
        "description": description,
        "level": level.value,
        "approved": False,
        "requested_at": datetime.datetime.utcnow().isoformat(),
    })
    with open(PENDING_PATH, "w") as f:
        json.dump(pending, f, indent=2)
    _log(f"REQUESTED | {action} | {item_id} | {description}")
    return level


def approve(item_ids: list):
    """Owner calls this (via the chat, not automatically) to approve specific items."""
    if not os.path.exists(PENDING_PATH):
        return []
    with open(PENDING_PATH) as f:
        pending = json.load(f)
    approved = []
    for item in pending:
        if item["item_id"] in item_ids:
            item["approved"] = True
            approved.append(item["item_id"])
            _log(f"APPROVED | {item['action']} | {item['item_id']}")
    with open(PENDING_PATH, "w") as f:
        json.dump(pending, f, indent=2)
    return approved


def is_approved(item_id: str) -> bool:
    if not os.path.exists(PENDING_PATH):
        return False
    with open(PENDING_PATH) as f:
        pending = json.load(f)
    return any(i["item_id"] == item_id and i["approved"] for i in pending)


def perform_level_c_action(action: str, item_id: str, fn, *args, **kwargs):
    """
    Any Level C action in the whole system must be called through this
    function, never directly. If it's not approved, it refuses to run.
    """
    if ACTION_LEVELS.get(action) == ApprovalLevel.OWNER_REQUIRED and not is_approved(item_id):
        raise ApprovalRequiredError(
            f"'{action}' on '{item_id}' requires explicit owner approval "
            f"before it can run. Not approved yet."
        )
    _log(f"EXECUTED | {action} | {item_id}")
    return fn(*args, **kwargs)
