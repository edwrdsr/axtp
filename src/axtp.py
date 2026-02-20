"""
AXTP - Agent Experience Transfer Protocol
Reference Implementation v0.1

A minimal but functional implementation of the AXTP protocol,
demonstrating Experience Record creation, Experience Pool management,
and the core deposit/retrieve/validate operations.
"""

import uuid
import json
import math
import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum


# ============================================================
# Enums
# ============================================================

class OutcomeStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    ABORTED = "aborted"


class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    DISPUTED = "disputed"


class ValidationType(str, Enum):
    CONFIRM = "confirm"
    DISPUTE = "dispute"
    AMEND = "amend"


class ConflictResolution(str, Enum):
    LATEST_WINS = "latest_wins"
    CONSENSUS = "consensus"
    ADMIN_REVIEW = "admin_review"


# ============================================================
# Data Structures
# ============================================================

@dataclass
class Step:
    """A single step in an agent's execution trace."""
    step_index: int
    action: str
    reasoning: str
    tool_used: Optional[str] = None
    input_summary: str = ""
    output_summary: str = ""
    duration_ms: int = 0
    success: bool = True


@dataclass
class Pivot:
    """Records when an agent changed its approach."""
    from_step: int
    to_step: int
    reason: str


@dataclass
class Pattern:
    """An effective pattern or antipattern learned during execution."""
    pattern_id: str
    description: str
    applicability: str = ""
    confidence: float = 0.0
    # Antipattern-specific fields
    trigger_conditions: str = ""
    alternative: str = ""


@dataclass
class ExperienceRecord:
    """
    The atomic unit of AXTP — captures a single agent's
    experience executing a task.
    """
    # Required fields
    agent_id: str
    task_type: str
    outcome_status: OutcomeStatus

    # Auto-generated
    xr_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    xr_version: str = "0.1.0"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Context
    objective: str = ""
    environment: dict = field(default_factory=dict)
    trigger: str = "user_request"
    parent_xr_id: Optional[str] = None

    # Execution trace
    steps: list[Step] = field(default_factory=list)
    pivots: list[Pivot] = field(default_factory=list)
    total_duration_ms: int = 0
    retries: int = 0

    # Outcome
    result_summary: str = ""
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    quality_self_assessment: float = 0.0

    # Learnings
    effective_patterns: list[Pattern] = field(default_factory=list)
    antipatterns: list[Pattern] = field(default_factory=list)
    environmental_notes: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Trust
    confidence_score: float = 0.5
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validator_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize to AXTP-compliant dictionary."""
        return {
            "xr_id": self.xr_id,
            "xr_version": self.xr_version,
            "agent_id": self.agent_id,
            "task_type": self.task_type,
            "timestamp": self.timestamp,
            "context": {
                "objective": self.objective,
                "environment": self.environment,
                "trigger": self.trigger,
                "parent_xr_id": self.parent_xr_id
            },
            "execution": {
                "steps": [asdict(s) for s in self.steps],
                "pivots": [asdict(p) for p in self.pivots],
                "total_duration_ms": self.total_duration_ms,
                "total_steps": len(self.steps),
                "retries": self.retries
            },
            "outcome": {
                "status": self.outcome_status.value,
                "result_summary": self.result_summary,
                "error_details": {
                    "error_type": self.error_type,
                    "error_message": self.error_message,
                    "recovery_attempted": self.recovery_attempted,
                    "recovery_successful": self.recovery_successful
                } if self.error_type else None,
                "quality_self_assessment": self.quality_self_assessment
            },
            "learnings": {
                "effective_patterns": [asdict(p) for p in self.effective_patterns],
                "antipatterns": [asdict(p) for p in self.antipatterns],
                "environmental_notes": self.environmental_notes,
                "recommendations": self.recommendations
            },
            "trust": {
                "confidence_score": self.confidence_score,
                "validation_status": self.validation_status.value,
                "validator_ids": self.validator_ids
            }
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# ============================================================
# Trust Engine
# ============================================================

class TrustEngine:
    """
    Computes and maintains trust scores for Experience Records.

    Trust = weighted combination of:
    - Source reputation (0.30)
    - Validation signals (0.25)
    - Outcome correlation (0.25)
    - Recency (0.10)
    - Consistency (0.10)
    """

    def __init__(
        self,
        weight_reputation: float = 0.30,
        weight_validation: float = 0.25,
        weight_outcome: float = 0.25,
        weight_recency: float = 0.10,
        weight_consistency: float = 0.10,
        decay_rate: float = 0.01  # lambda for exponential decay
    ):
        self.weights = {
            "reputation": weight_reputation,
            "validation": weight_validation,
            "outcome": weight_outcome,
            "recency": weight_recency,
            "consistency": weight_consistency
        }
        self.decay_rate = decay_rate
        self.agent_reputations: dict[str, float] = {}  # agent_id -> reputation
        self.outcome_feedback: dict[str, list[bool]] = {}  # xr_id -> [helpful, not helpful, ...]

    def get_agent_reputation(self, agent_id: str) -> float:
        """Get an agent's reputation score, defaulting to 0.5 for unknown agents."""
        return self.agent_reputations.get(agent_id, 0.5)

    def update_agent_reputation(self, agent_id: str, delta: float):
        """Adjust an agent's reputation score."""
        current = self.get_agent_reputation(agent_id)
        self.agent_reputations[agent_id] = max(0.0, min(1.0, current + delta))

    def compute_recency_factor(self, timestamp: str) -> float:
        """Apply exponential decay based on age of experience."""
        try:
            xr_time = datetime.fromisoformat(timestamp)
            now = datetime.now(timezone.utc)
            age_days = (now - xr_time).total_seconds() / 86400
            return math.exp(-self.decay_rate * age_days)
        except (ValueError, TypeError):
            return 0.5

    def compute_validation_score(self, xr: ExperienceRecord) -> float:
        """Score based on validation status and number of validators."""
        if xr.validation_status == ValidationStatus.VALIDATED:
            return min(1.0, 0.7 + 0.1 * len(xr.validator_ids))
        elif xr.validation_status == ValidationStatus.DISPUTED:
            return max(0.0, 0.3 - 0.1 * len(xr.validator_ids))
        return 0.5  # Pending

    def compute_outcome_score(self, xr_id: str) -> float:
        """Score based on downstream feedback from consuming agents."""
        feedback = self.outcome_feedback.get(xr_id, [])
        if not feedback:
            return 0.5
        return sum(1 for f in feedback if f) / len(feedback)

    def compute_trust_score(self, xr: ExperienceRecord, pool_xrs: list[ExperienceRecord] = None) -> float:
        """Compute composite trust score for an Experience Record."""
        reputation = self.get_agent_reputation(xr.agent_id)
        validation = self.compute_validation_score(xr)
        outcome = self.compute_outcome_score(xr.xr_id)
        recency = self.compute_recency_factor(xr.timestamp)

        # Consistency: how well does this XR align with others of the same task type?
        consistency = 0.5
        if pool_xrs:
            same_type = [x for x in pool_xrs if x.task_type == xr.task_type and x.xr_id != xr.xr_id]
            if same_type:
                same_outcome = sum(1 for x in same_type if x.outcome_status == xr.outcome_status)
                consistency = same_outcome / len(same_type)

        score = (
            self.weights["reputation"] * reputation +
            self.weights["validation"] * validation +
            self.weights["outcome"] * outcome +
            self.weights["recency"] * recency +
            self.weights["consistency"] * consistency
        )
        return round(max(0.0, min(1.0, score)), 4)

    def record_feedback(self, xr_id: str, was_helpful: bool):
        """Record downstream outcome feedback for an XR."""
        if xr_id not in self.outcome_feedback:
            self.outcome_feedback[xr_id] = []
        self.outcome_feedback[xr_id].append(was_helpful)


# ============================================================
# Experience Pool
# ============================================================

class ExperiencePool:
    """
    A managed collection of Experience Records with governance controls.
    """

    def __init__(
        self,
        pool_name: str,
        scope: str = "global",
        validation_required: bool = True,
        min_confidence_threshold: float = 0.3,
        conflict_resolution: ConflictResolution = ConflictResolution.LATEST_WINS,
        max_records: int = 10000
    ):
        self.pool_id = str(uuid.uuid4())
        self.pool_name = pool_name
        self.scope = scope
        self.validation_required = validation_required
        self.min_confidence_threshold = min_confidence_threshold
        self.conflict_resolution = conflict_resolution
        self.max_records = max_records

        self._records: dict[str, ExperienceRecord] = {}
        self._audit_log: list[dict] = []
        self.trust_engine = TrustEngine()

    # --- Core Operations ---

    def deposit(self, xr: ExperienceRecord) -> dict:
        """
        DEPOSIT: Submit an Experience Record to the pool.

        Returns a deposit receipt with status.
        """
        # Schema validation
        if not xr.agent_id or not xr.task_type:
            return {"status": "rejected", "reason": "Missing required fields (agent_id, task_type)"}

        # Capacity check
        if len(self._records) >= self.max_records:
            self._evict_oldest()

        # Compute initial trust score
        xr.confidence_score = self.trust_engine.compute_trust_score(xr, list(self._records.values()))

        # Store
        self._records[xr.xr_id] = xr

        # Audit
        self._log("deposit", xr.agent_id, [xr.xr_id], "accepted")

        return {
            "status": "accepted",
            "xr_id": xr.xr_id,
            "pool_id": self.pool_id,
            "confidence_score": xr.confidence_score,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def retrieve(
        self,
        task_type: str = None,
        min_confidence: float = None,
        max_results: int = 10,
        recency_weight: float = 0.5,
        outcome_filter: OutcomeStatus = None,
        agent_id: str = "anonymous"
    ) -> list[dict]:
        """
        RETRIEVE: Query the pool for relevant Experience Records.

        Returns ranked XRs based on composite relevance scoring.
        """
        if min_confidence is None:
            min_confidence = self.min_confidence_threshold

        candidates = list(self._records.values())

        # Filter by task type (supports prefix matching)
        if task_type:
            candidates = [
                xr for xr in candidates
                if xr.task_type == task_type or xr.task_type.startswith(task_type + ".")
            ]

        # Filter by outcome
        if outcome_filter:
            candidates = [xr for xr in candidates if xr.outcome_status == outcome_filter]

        # Recompute trust scores with current pool state
        for xr in candidates:
            xr.confidence_score = self.trust_engine.compute_trust_score(xr, list(self._records.values()))

        # Filter by confidence
        candidates = [xr for xr in candidates if xr.confidence_score >= min_confidence]

        # Score and rank
        scored = []
        for xr in candidates:
            # Composite relevance = trust score weighted by recency preference
            recency = self.trust_engine.compute_recency_factor(xr.timestamp)
            relevance = (1 - recency_weight) * xr.confidence_score + recency_weight * recency
            scored.append((relevance, xr))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = [
            {
                "xr_id": xr.xr_id,
                "relevance_score": round(rel, 4),
                "confidence_score": xr.confidence_score,
                "task_type": xr.task_type,
                "outcome_status": xr.outcome_status.value,
                "result_summary": xr.result_summary,
                "learnings": {
                    "effective_patterns": [asdict(p) for p in xr.effective_patterns],
                    "antipatterns": [asdict(p) for p in xr.antipatterns],
                    "recommendations": xr.recommendations
                }
            }
            for rel, xr in scored[:max_results]
        ]

        # Audit
        self._log("retrieve", agent_id, [r["xr_id"] for r in results], f"returned {len(results)} results")

        return results

    def validate(
        self,
        xr_id: str,
        validator_id: str,
        validation_type: ValidationType,
        evidence: str = ""
    ) -> dict:
        """
        VALIDATE: Confirm, dispute, or amend an Experience Record.
        """
        if xr_id not in self._records:
            return {"status": "error", "reason": "XR not found"}

        xr = self._records[xr_id]

        # Prevent self-validation
        if validator_id == xr.agent_id:
            return {"status": "rejected", "reason": "Self-validation not permitted"}

        # Apply validation
        if validation_type == ValidationType.CONFIRM:
            xr.validator_ids.append(validator_id)
            if len(xr.validator_ids) >= 2:
                xr.validation_status = ValidationStatus.VALIDATED
            self.trust_engine.update_agent_reputation(xr.agent_id, 0.05)

        elif validation_type == ValidationType.DISPUTE:
            xr.validator_ids.append(validator_id)
            xr.validation_status = ValidationStatus.DISPUTED
            self.trust_engine.update_agent_reputation(xr.agent_id, -0.05)

        elif validation_type == ValidationType.AMEND:
            xr.validator_ids.append(validator_id)
            # Amendments don't change status but add to the record

        # Recompute trust
        xr.confidence_score = self.trust_engine.compute_trust_score(xr, list(self._records.values()))

        # Audit
        self._log("validate", validator_id, [xr_id], f"{validation_type.value}: {evidence[:100]}")

        return {
            "status": "accepted",
            "xr_id": xr_id,
            "new_confidence": xr.confidence_score,
            "validation_status": xr.validation_status.value
        }

    def inspect(self) -> dict:
        """INSPECT: Get pool metadata and health statistics."""
        records = list(self._records.values())
        return {
            "pool_id": self.pool_id,
            "pool_name": self.pool_name,
            "scope": self.scope,
            "total_xrs": len(records),
            "contributing_agents": len(set(xr.agent_id for xr in records)),
            "avg_confidence": round(
                sum(xr.confidence_score for xr in records) / len(records), 4
            ) if records else 0.0,
            "task_types": list(set(xr.task_type for xr in records)),
            "outcome_distribution": {
                status.value: sum(1 for xr in records if xr.outcome_status == status)
                for status in OutcomeStatus
            },
            "validation_distribution": {
                status.value: sum(1 for xr in records if xr.validation_status == status)
                for status in ValidationStatus
            },
            "audit_entries": len(self._audit_log),
            "last_updated": records[-1].timestamp if records else None
        }

    # --- Internal ---

    def _evict_oldest(self):
        """Remove the oldest, lowest-trust record to make room."""
        if not self._records:
            return
        worst = min(self._records.values(), key=lambda xr: (xr.confidence_score, xr.timestamp))
        del self._records[worst.xr_id]
        self._log("evict", "system", [worst.xr_id], "capacity limit reached")

    def _log(self, operation: str, actor: str, xr_ids: list[str], outcome: str):
        self._audit_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "actor": actor,
            "xr_ids": xr_ids,
            "outcome": outcome
        })


# ============================================================
# Demo: Full Protocol Walkthrough
# ============================================================

def demo():
    """
    Demonstrates the complete AXTP lifecycle:
    1. Create an Experience Pool
    2. Agent Alpha executes a task and deposits experience
    3. Agent Beta retrieves experience before executing a similar task
    4. Agent Beta validates Agent Alpha's experience
    5. Inspect pool health
    """

    print("=" * 60)
    print("AXTP Reference Implementation — Demo")
    print("=" * 60)

    # 1. Create pool
    pool = ExperiencePool(
        pool_name="API Integrations",
        scope="organization",
        min_confidence_threshold=0.3
    )
    print(f"\n✓ Created Experience Pool: '{pool.pool_name}' ({pool.pool_id[:8]}...)")

    # 2. Agent Alpha deposits experience
    print("\n--- Agent Alpha: Executing Stripe integration task ---")

    xr_alpha = ExperienceRecord(
        agent_id="agent-alpha",
        task_type="api.integration.stripe.subscriptions",
        outcome_status=OutcomeStatus.SUCCESS,
        objective="Integrate Stripe API for subscription billing",
        environment={
            "framework": "langchain",
            "model": "claude-sonnet-4-5-20250929",
            "tools_available": ["http_client", "code_executor"]
        },
        steps=[
            Step(0, "Retrieved Stripe API docs", "Need current API surface", "http_client",
                 "GET Stripe docs", "Endpoint specs retrieved", 1200, True),
            Step(1, "Created customer with idempotency", "Prevent duplicates", "code_executor",
                 "Customer creation code", "Function with error handling", 3400, True),
            Step(2, "Attempted inline price_data subscription", "Simpler approach",
                 "code_executor", "Subscription with price_data", "Error: price_data not supported", 2100, False),
            Step(3, "Used explicit Product→Price→Subscription chain", "More reliable approach",
                 "code_executor", "Three-step creation", "Subscription created successfully", 4200, True),
        ],
        pivots=[
            Pivot(2, 3, "Inline price_data failed for recurring subscriptions. Explicit object chain required.")
        ],
        total_duration_ms=10900,
        result_summary="Complete Stripe subscription integration with customer creation and webhook handling",
        quality_self_assessment=0.85,
        effective_patterns=[
            Pattern("stripe-product-first", "Always create Product→Price→Subscription explicitly",
                    "Any Stripe subscription integration", 0.95),
            Pattern("stripe-idempotency", "Use idempotency keys on all mutating calls",
                    "Any Stripe API integration", 0.90)
        ],
        antipatterns=[
            Pattern("stripe-inline-price", "Inline price_data fails for recurring subscriptions",
                    trigger_conditions="Reading Stripe Checkout docs and assuming same pattern works for Subscription API",
                    alternative="Create Product → Create Price → Create Subscription with price reference")
        ],
        environmental_notes=[
            "Stripe API version 2025-12-01. Behavior may differ on older versions.",
            "Webhook signature verification requires raw request body — JSON parsing middleware breaks it."
        ],
        recommendations=[
            "Start with Product→Price→Subscription chain even for simple cases.",
            "Test webhook handlers with Stripe CLI before deploying."
        ]
    )

    receipt = pool.deposit(xr_alpha)
    print(f"✓ Agent Alpha deposited XR: {receipt['xr_id'][:8]}... (confidence: {receipt['confidence_score']})")

    # 3. Agent Beta retrieves experience
    print("\n--- Agent Beta: Preparing for Stripe task, querying pool ---")

    results = pool.retrieve(
        task_type="api.integration.stripe",
        max_results=5,
        agent_id="agent-beta"
    )

    print(f"✓ Retrieved {len(results)} relevant experience records")
    for r in results:
        print(f"  └ [{r['relevance_score']}] {r['task_type']} → {r['outcome_status']}")
        if r['learnings']['antipatterns']:
            for ap in r['learnings']['antipatterns']:
                print(f"    ⚠ Antipattern: {ap['description'][:80]}...")
        if r['learnings']['recommendations']:
            for rec in r['learnings']['recommendations']:
                print(f"    → {rec}")

    # 4. Agent Beta validates after executing
    print("\n--- Agent Beta: Completed task, validating Alpha's experience ---")

    validation = pool.validate(
        xr_id=xr_alpha.xr_id,
        validator_id="agent-beta",
        validation_type=ValidationType.CONFIRM,
        evidence="Confirmed: Product→Price→Subscription chain worked correctly. Inline price_data does fail."
    )
    print(f"✓ Validation accepted. New confidence: {validation['new_confidence']}")
    print(f"  Status: {validation['validation_status']}")

    # Deposit Beta's own experience
    xr_beta = ExperienceRecord(
        agent_id="agent-beta",
        task_type="api.integration.stripe.subscriptions",
        outcome_status=OutcomeStatus.SUCCESS,
        objective="Implement Stripe subscription with trial period",
        steps=[
            Step(0, "Retrieved Alpha's experience from pool", "Check for prior knowledge", None,
                 "Query: api.integration.stripe", "Found 1 relevant XR with antipattern warning", 50, True),
            Step(1, "Created Product→Price→Subscription with trial", "Following Alpha's recommended pattern",
                 "code_executor", "Three-step creation with trial_period_days", "Subscription with 14-day trial", 3800, True),
        ],
        total_duration_ms=3850,
        result_summary="Stripe subscription with trial period, using proven pattern from pool",
        quality_self_assessment=0.90,
        effective_patterns=[
            Pattern("stripe-trial-on-subscription", "Set trial_period_days on Subscription, not Price",
                    "Stripe subscriptions with trial periods", 0.85)
        ],
        recommendations=[
            "Trial periods go on the Subscription object, not the Price. Easy to get wrong."
        ]
    )

    receipt2 = pool.deposit(xr_beta)
    print(f"\n✓ Agent Beta deposited XR: {receipt2['xr_id'][:8]}... (confidence: {receipt2['confidence_score']})")
    print(f"  Note: Beta completed in {xr_beta.total_duration_ms}ms vs Alpha's {xr_alpha.total_duration_ms}ms")
    print(f"  → {round((1 - xr_beta.total_duration_ms / xr_alpha.total_duration_ms) * 100)}% faster with prior experience")

    # 5. Inspect pool
    print("\n--- Pool Health ---")
    stats = pool.inspect()
    print(f"  Pool: {stats['pool_name']}")
    print(f"  Total XRs: {stats['total_xrs']}")
    print(f"  Contributing agents: {stats['contributing_agents']}")
    print(f"  Avg confidence: {stats['avg_confidence']}")
    print(f"  Outcomes: {stats['outcome_distribution']}")
    print(f"  Validation: {stats['validation_distribution']}")
    print(f"  Audit entries: {stats['audit_entries']}")

    # Show the compounding effect
    print("\n" + "=" * 60)
    print("COMPOUNDING EFFECT DEMONSTRATED")
    print("=" * 60)
    print(f"• Agent Alpha: Discovered antipattern through trial and error ({xr_alpha.total_duration_ms}ms)")
    print(f"• Agent Beta:  Avoided antipattern using Alpha's experience ({xr_beta.total_duration_ms}ms)")
    print(f"• Agent Beta:  Added NEW knowledge (trial periods) to the pool")
    print(f"• Next agent:  Will benefit from BOTH agents' experience")
    print(f"• Pool grows stronger with every task execution")

    return pool


if __name__ == "__main__":
    demo()
