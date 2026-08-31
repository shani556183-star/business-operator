"""
Opportunity data model.

Every business opportunity the system discovers or evaluates must be
represented as an Opportunity record with this exact shape. This keeps
the system general-purpose: SEO audit is just one row in opportunities.json,
not something hard-coded into the core engine.

Confidence levels are explicit so we never present a guess as a fact.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
import json
import os


class Confidence(str, Enum):
    VERIFIED_FACT = "VERIFIED_FACT"      # confirmed via direct source (fetch, search, doc)
    ESTIMATE = "ESTIMATE"                # reasoned from real data but not directly measured
    ASSUMPTION = "ASSUMPTION"            # working assumption, not yet checked
    UNKNOWN = "UNKNOWN"                  # genuinely don't know


class OpportunityStatus(str, Enum):
    IDEA = "IDEA"
    RESEARCH = "RESEARCH"
    VALIDATING = "VALIDATING"
    TESTING = "TESTING"
    VALIDATED = "VALIDATED"
    WINNER = "WINNER"
    SCALING = "SCALING"
    FAILED = "FAILED"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"


@dataclass
class Opportunity:
    id: str
    name: str
    category: str
    problem: str
    target_buyer: str
    evidence: list          # list of {claim, source, confidence}
    competitors: list
    pricing_evidence: list  # list of {source, price_range, confidence}
    acquisition_channels: list
    estimated_cost_usd: float
    automation_potential_pct: int   # 0-100, must be justified in evidence
    human_involvement: str          # short description of what stays manual and why
    legal_platform_risk: str        # short description of known ToS/legal risk
    scalability: str
    first_customer_difficulty: str  # LOW / MEDIUM / HIGH + why
    confidence: Confidence
    status: OpportunityStatus
    next_action: str
    score: Optional[int] = None     # 0-100, filled in by scoring.py

    def to_dict(self):
        d = asdict(self)
        d["confidence"] = self.confidence.value
        d["status"] = self.status.value
        return d


MEMORY_PATH = os.path.join(os.path.dirname(__file__), "..", "memory", "opportunities.json")


def load_opportunities() -> list:
    if not os.path.exists(MEMORY_PATH):
        return []
    with open(MEMORY_PATH, "r") as f:
        return json.load(f)


def save_opportunity(opp: Opportunity):
    data = load_opportunities()
    data = [o for o in data if o["id"] != opp.id]  # replace if exists
    data.append(opp.to_dict())
    with open(MEMORY_PATH, "w") as f:
        json.dump(data, f, indent=2)
