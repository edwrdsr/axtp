# AXTP — Agent Experience Transfer Protocol

🌐 **[axtp.dev](https://axtp.dev)** · 📄 **[White Paper](https://github.com/edwrdsr/axtp/blob/main/docs/axtp-whitepaper.pdf)** · 📰 **[The Abstraction Stack](https://theabstractionstack.substack.com/)**

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
| **A2A** (Google) | Enables agent-to-agent delegation and structured communication |
| **AXTP** | **Captures, validates, and shares execution experience across agents** |

Agents use MCP to connect, A2A to delegate — and **AXTP to learn from each other.**

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

- [x] Protocol specification (v0.1)
- [x] Experience Record schema definition
- [x] Experience Pool interface specification
- [x] Trust & Governance framework
- [x] Reference implementation (Python)
- [x] Security analysis and threat model (white paper §5)
- [x] Example XRs
- [ ] MCP server integration (in progress)
- [ ] Benchmark suite with live agents
- [ ] Additional framework integrations (LangChain, CrewAI)

## Repository Structure

```
axtp/
├── spec/              # Protocol specification documents
│   ├── PROTOCOL.md    # Core protocol specification
│   ├── GOVERNANCE.md  # Trust and governance framework
│   └── SECURITY.md    # Security model and threat analysis
├── src/               # Reference implementation
│   └── axtp.py        # Python reference implementation with demo
├── examples/          # Example Experience Records
│   └── xr-stripe-integration.json
├── docs/              # Documentation and white paper
│   └── axtp-whitepaper.pdf
├── CONTRIBUTING.md
└── LICENSE
```

## Quick Start

Run the reference implementation demo:

```bash
python3 src/axtp.py
```

This simulates two agents executing similar tasks — Agent Alpha without prior experience, Agent Beta with access to Alpha's pooled experience. Beta completes the task 65% faster by retrieving and applying Alpha's learnings.

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

**Richard Edwards**

- 𝕏: [@edwrdsr](https://x.com/edwrdsr)
- Substack: [The Abstraction Stack](https://theabstractionstack.substack.com/)

## License

Protocol Specification: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
Reference Implementation: [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)

---

*AXTP is patent pending. The protocol specification is openly licensed for implementation by any party.*
