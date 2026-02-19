# AXTP Protocol Specification v0.1 (DRAFT)

## Abstract

The Agent Experience Transfer Protocol (AXTP) defines a standardized mechanism for AI agents to capture structured execution experience, deposit it into shared experience pools, and retrieve relevant prior experience before task execution. The protocol enables compound intelligence across agent networks by transforming isolated task completions into collective organizational knowledge.

## 1. Introduction

### 1.1 Motivation

Modern AI agent architectures treat each task execution as an independent event. An agent that successfully navigates a complex API integration, resolves an ambiguous customer request, or recovers from an unexpected error generates valuable experiential knowledge — knowledge that is discarded the moment the session ends.

This is analogous to an organization where every employee starts their first day, every day. No institutional knowledge. No onboarding. No lessons learned from past projects.

AXTP addresses this by defining:

1. A **structured format** for encoding execution experience
2. A **deposit protocol** for submitting experience to shared pools
3. A **retrieval protocol** for querying relevant experience before execution
4. A **governance framework** for validating, weighting, and auditing shared experience

### 1.2 Design Principles

- **Agent-agnostic**: AXTP works with any agent framework, LLM provider, or execution environment
- **Transport-agnostic**: The protocol defines data structures and interfaces, not transport mechanisms
- **Governance-first**: Trust, validation, and auditability are core to the protocol, not bolt-on features
- **Incremental adoption**: Agents can begin producing XRs without consuming them, and vice versa
- **Privacy-aware**: Experience can be scoped, anonymized, and access-controlled

### 1.3 Relationship to Existing Protocols

AXTP operates at a distinct layer in the emerging agent protocol stack:

```
┌─────────────────────────────────────────────┐
│           Application / Orchestration        │
├─────────────────────────────────────────────┤
│  AXTP (Experience Transfer & Compounding)    │  ← This protocol
├─────────────────────────────────────────────┤
│  A2A (Agent-to-Agent Delegation)             │
├─────────────────────────────────────────────┤
│  MCP (Tool & Context Connection)             │
├─────────────────────────────────────────────┤
│  ACP (Structured Agent Communication)        │
├─────────────────────────────────────────────┤
│           Transport (HTTP, gRPC, WS)         │
└─────────────────────────────────────────────┘
```

AXTP is complementary to — not competitive with — MCP, A2A, and ACP. It can consume events from these protocols to generate Experience Records, and it can feed retrieved experience into agents operating over these protocols.

## 2. Core Data Structures

### 2.1 Experience Record (XR)

An Experience Record is the atomic unit of the protocol. It captures a single agent's experience executing a task or subtask.

#### 2.1.1 Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `xr_id` | string (UUID v4) | Unique identifier for this record |
| `xr_version` | string | Protocol version (e.g., "0.1.0") |
| `agent_id` | string | Identifier of the producing agent |
| `task_type` | string | Hierarchical classification (e.g., "api.integration.rest") |
| `timestamp` | string (ISO 8601) | When execution completed |
| `outcome_status` | enum | One of: `success`, `partial_success`, `failure`, `aborted` |

#### 2.1.2 Context Object

```json
{
  "context": {
    "objective": "string — what the agent was tasked with",
    "environment": {
      "framework": "string — agent framework (e.g., langchain, autogen)",
      "model": "string — underlying LLM if applicable",
      "tools_available": ["array of tool identifiers"],
      "constraints": ["array of constraint descriptions"]
    },
    "trigger": "string — what initiated this task (user, scheduler, another agent)",
    "parent_xr_id": "string | null — if this is a subtask, reference to parent"
  }
}
```

#### 2.1.3 Execution Trace

```json
{
  "execution": {
    "steps": [
      {
        "step_index": 0,
        "action": "string — what the agent did",
        "reasoning": "string — why it chose this action",
        "tool_used": "string | null",
        "input_summary": "string — summarized input (no raw data)",
        "output_summary": "string — summarized output",
        "duration_ms": 0,
        "success": true
      }
    ],
    "total_duration_ms": 0,
    "total_steps": 0,
    "retries": 0,
    "pivots": [
      {
        "from_step": 0,
        "to_step": 0,
        "reason": "string — why the agent changed approach"
      }
    ]
  }
}
```

#### 2.1.4 Outcome Object

```json
{
  "outcome": {
    "status": "success | partial_success | failure | aborted",
    "result_summary": "string — what was achieved",
    "error_details": {
      "error_type": "string",
      "error_message": "string",
      "recovery_attempted": true,
      "recovery_successful": false,
      "recovery_method": "string"
    },
    "quality_self_assessment": 0.0
  }
}
```

#### 2.1.5 Learnings Object

This is the highest-value component of an XR — it encodes transferable knowledge.

```json
{
  "learnings": {
    "effective_patterns": [
      {
        "pattern_id": "string",
        "description": "string — what worked and why",
        "applicability": "string — when this pattern is relevant",
        "confidence": 0.0
      }
    ],
    "antipatterns": [
      {
        "pattern_id": "string",
        "description": "string — what didn't work and why",
        "trigger_conditions": "string — when you might mistakenly try this",
        "alternative": "string — what to do instead"
      }
    ],
    "environmental_notes": [
      "string — context-specific observations (e.g., 'API rate limits are 100/min not 1000/min as documented')"
    ],
    "recommendations": [
      "string — advice for future agents attempting similar tasks"
    ]
  }
}
```

### 2.2 Experience Pool

An Experience Pool is a managed collection of XRs with defined scope, access controls, and governance policies.

```json
{
  "pool_id": "string (UUID)",
  "pool_name": "string",
  "scope": "global | organization | team | task_type",
  "access_policy": {
    "read": ["agent_ids or role patterns"],
    "write": ["agent_ids or role patterns"],
    "admin": ["agent_ids or role patterns"]
  },
  "governance": {
    "validation_required": true,
    "min_confidence_threshold": 0.5,
    "conflict_resolution": "latest_wins | consensus | admin_review",
    "retention_policy": {
      "max_age_days": 90,
      "max_records": 10000,
      "archival_strategy": "compress | summarize | delete"
    }
  },
  "statistics": {
    "total_xrs": 0,
    "contributing_agents": 0,
    "avg_confidence": 0.0,
    "last_updated": "ISO 8601"
  }
}
```

## 3. Protocol Operations

### 3.1 Deposit

An agent deposits an XR into one or more Experience Pools after task execution.

```
DEPOSIT(pool_id, experience_record) → deposit_receipt
```

The deposit operation:
1. Validates the XR against the schema
2. Checks agent authorization for the target pool
3. Runs governance checks (if configured)
4. Assigns an initial trust score
5. Returns a receipt with the XR's pool-specific ID and status

### 3.2 Retrieve

An agent retrieves relevant XRs from a pool before executing a task.

```
RETRIEVE(pool_id, query) → ranked_experience_set
```

Query parameters:
- `task_type` — hierarchical match (exact or prefix)
- `context_similarity` — semantic similarity to current context
- `min_confidence` — minimum trust score threshold
- `max_results` — limit on returned XRs
- `recency_weight` — how much to favor recent experience (0.0 to 1.0)
- `outcome_filter` — filter by outcome status

The retrieval operation returns XRs ranked by a composite relevance score incorporating task type match, context similarity, confidence, and recency.

### 3.3 Validate

A validator (agent or human) updates the trust metadata on an existing XR.

```
VALIDATE(pool_id, xr_id, validation) → updated_trust
```

Validation includes:
- `validator_id` — who is validating
- `validation_type` — `confirm`, `dispute`, `amend`
- `evidence` — supporting reasoning or data
- `adjusted_confidence` — proposed confidence adjustment

### 3.4 Query Pool Metadata

Agents or administrators can inspect pool health and statistics.

```
INSPECT(pool_id) → pool_metadata
```

## 4. Governance Framework

### 4.1 Trust Model

Every XR carries a trust score that evolves over time based on:

- **Source reputation** — agents that consistently produce accurate XRs earn higher base trust
- **Validation signals** — confirmation or disputes from other agents/validators
- **Outcome correlation** — if agents that consume an XR subsequently perform better, the XR's trust increases
- **Age decay** — trust naturally decreases over time unless reinforced

### 4.2 Poison Detection

The governance layer must detect and mitigate:

- **Deliberate poisoning** — malicious agents injecting false experience
- **Drift poisoning** — initially valid experience that becomes incorrect as environments change
- **Amplification attacks** — agents citing each other's bad experience to inflate trust scores

Detection mechanisms include:
- Statistical outlier detection on XR content
- Cross-validation against independent agent experiences
- Anomaly detection on trust score trajectories
- Human-in-the-loop review triggers for high-impact XRs

### 4.3 Audit Trail

Every operation (deposit, retrieve, validate) is logged with:
- Timestamp
- Actor (agent or human)
- Operation type
- Affected XR IDs
- Outcome

The audit trail is append-only and tamper-evident.

## 5. Security Considerations

### 5.1 Data Sensitivity

XRs may contain sensitive information derived from task execution. The protocol requires:
- **No raw data** in XRs — only summarized inputs/outputs
- **Configurable redaction** — organizations define what fields require sanitization
- **Encryption at rest** — XRs stored in pools must be encrypted
- **Encryption in transit** — all protocol operations over TLS minimum

### 5.2 Access Control

- Agent identity verification before deposit or retrieval
- Role-based access control on pools
- Rate limiting on retrieval to prevent data exfiltration
- Scope isolation between organizational pools

### 5.3 Threat Model

See [SECURITY.md](SECURITY.md) for the full threat model analysis.

## 6. Implementation Guidelines

### 6.1 Minimum Viable Implementation

An AXTP-compliant implementation must support:
1. XR creation conforming to the schema in §2.1
2. At least the DEPOSIT and RETRIEVE operations
3. Basic confidence scoring
4. Schema validation on deposit

### 6.2 Full Implementation

A full implementation additionally provides:
1. Complete governance framework (§4)
2. Audit trail (§4.3)
3. Poison detection (§4.2)
4. Pool management and administration
5. Integration adapters for major agent frameworks

---

## Appendix A: Full XR JSON Schema

*To be published as a formal JSON Schema document in `/spec/schemas/xr.schema.json`*

## Appendix B: Example XRs

*See `/examples/` directory for annotated example Experience Records across common task types.*

---

**Document Status**: DRAFT v0.1
**Last Updated**: 2026-02-19
**Author**: Rich
**License**: CC BY 4.0
