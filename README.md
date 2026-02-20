# AXTP — Agent Experience Transfer Protocol

**An open protocol for structured experience exchange between AI agents.**

AXTP enables agents to capture, validate, and share execution experience — creating compound intelligence across agent networks. Instead of every agent starting from zero, AXTP provides a standardized layer where structured knowledge flows between agents, improving collective task execution over time.

## The Problem

Today's AI agents are stateless by default. Each execution is isolated — an agent completes a task, and the lessons learned evaporate. Current approaches fall short:

- **Stateless agents** start fresh every time, repeating mistakes indefinitely
- **Individual memory** keeps one agent's history siloed and inaccessible to others
- **Fine-tuning** bakes learning into model weights — slow, expensive, opaque, and ungovernable

There is no standardized way for agents to say: *"Here's what I did, what worked, what failed, and what I learned"* — and for other agents to benefit from that experience before they execute.

## The Solution

AXTP defines a protocol for **experiential knowledge exchange** between agents. It introduces:

- **Experience Records (XRs)** — structured representations of agent task execution, including steps taken, decisions made, outcomes, errors encountered, and resolution paths
- **Experience Pools** — shared repositories where agents deposit and retrieve XRs
- **Trust & Validation Layer** — governance controls that verify experience quality, detect poisoned or conflicting records, and maintain auditability
- **Retrieval Protocol** — a standardized interface for agents to query relevant experience before execution

## Where AXTP Fits in the Agent Stack

AXTP is **not** a replacement for existing agent protocols. It's a complementary layer:

| Protocol | Function |
|----------|----------|
| **MCP** (Anthropic) | Connects agents to tools and data sources |
| **A2A** (Google) | Enables agent-to-agent task delegation |
| **ACP** (IBM) | Structures agent communication messages |
| **AXTP** | **Captures, validates, and shares execution experience across agents** |

Agents use MCP to connect, A2A to delegate, ACP to communicate — and **AXTP to learn from each other.**

## Core Concepts

### Experience Records (XRs)

An XR is a structured artifact produced after an agent completes (or fails) a task. It includes:

```
{
  "xr_id": "uuid",
  "agent_id": "originating-agent",
  "task_type": "classification-string",
  "timestamp": "ISO-8601",
  "context": {
    "objective": "what the agent was trying to do",
    "environment": "relevant execution context",
    "constraints": "any limitations or requirements"
  },
  "execution": {
    "steps": [...],
    "decisions": [...],
    "tools_used": [...],
    "duration_ms": 0
  },
  "outcome": {
    "status": "success | partial | failure",
    "result_summary": "what happened",
    "error_details": null
  },
  "learnings": {
    "effective_patterns": [...],
    "antipatterns": [...],
    "recommendations": [...]
  },
  "trust": {
    "confidence_score": 0.0,
    "validation_status": "pending | validated | disputed",
    "validator_ids": []
  }
}
```

### Experience Pools

Experience Pools are shared repositories where XRs accumulate. They support:

- **Scoped access** — pools can be global, organizational, or task-specific
- **Temporal weighting** — recent experience is weighted more heavily
- **Conflict resolution** — when XRs disagree, the governance layer mediates
- **Retrieval by relevance** — agents query pools by task type, context similarity, or outcome patterns

### Trust & Governance Layer

This is what makes AXTP different from a simple shared database. The governance layer provides:

- **Experience validation** — are the reported outcomes accurate?
- **Poison detection** — is an agent injecting misleading experience?
- **Conflict arbitration** — when agents report contradictory learnings
- **Audit trail** — who contributed what, when, and how it influenced downstream decisions
- **Access control** — who can read from and write to which pools

## Project Status

🚧 **Early Stage — Protocol Specification in Development**

- [x] Problem definition and positioning
- [ ] Formal protocol specification (v0.1)
- [ ] XR schema definition (JSON Schema)
- [ ] Experience Pool interface specification
- [ ] Trust & Governance framework
- [ ] Reference implementation (Python)
- [ ] Example integrations (MCP, LangChain)
- [ ] Security analysis and threat model

## Repository Structure

```
axtp/
├── spec/              # Protocol specification documents
│   ├── PROTOCOL.md    # Core protocol specification
│   ├── XR_SCHEMA.md   # Experience Record schema
│   ├── GOVERNANCE.md  # Trust and governance framework
│   └── SECURITY.md    # Security model and threat analysis
├── src/               # Reference implementation
├── examples/          # Example integrations and demos
├── docs/              # Additional documentation
└── .github/           # Issue templates, CI/CD
```

## Why Open?

Agent experience compounding is too important to be proprietary. An open protocol:

- Enables interoperability across agent frameworks and vendors
- Allows public auditability of the governance model
- Attracts contributions from the broader AI safety and infrastructure community
- Prevents vendor lock-in of accumulated agent knowledge

AXTP is published under an open specification with a provisional patent filed to establish priority and prevent third-party enclosure of the core protocol concepts.

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Priority areas:
- Protocol specification review and feedback
- Security and adversarial analysis
- Reference implementation development
- Integration examples with existing agent frameworks

## Author

**Rich** — Builder of [The Abstraction Stack](https://theabstractionstack.com), exploring AI infrastructure and the future of agentic systems. Background in governance, risk, and compliance (GRC) with CISSP certification.

- 𝕏: [@Edwrdsr](https://x.com/Edwrdsr)
- Substack: [The Abstraction Stack](https://theabstractionstack.com)

## License

Protocol Specification: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
Reference Implementation: [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)

---

*AXTP is patent pending. The protocol specification is openly licensed for implementation by any party.*
