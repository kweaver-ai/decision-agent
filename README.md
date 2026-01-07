# Decision Agent

[中文](README.zh.md) | English

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE.txt)

**AISHU For a smarter future.**

KWeaver is an open-source ecosystem for building, deploying, and running decision intelligence AI applications. This ecosystem adopts ontology as the core methodology for business knowledge networks, with DIP as the core platform, aiming to provide elastic, agile, and reliable enterprise-grade decision intelligence to further unleash everyone's productivity.

The DIP platform includes key subsystems such as ADP, Decision Agent, DIP Studio, and AI Store.

## 📚 Quick Links

- 🤝 [Contributing](CONTRIBUTING.md) - Guidelines for contributing to the project
- 📄 [License](LICENSE.txt) - Apache License 2.0
- 🐛 [Report Bug](https://github.com/kweaver-ai/decision-agent) - Report a bug or issue
- 💡 [Request Feature](https://github.com/kweaver-ai/decision-agent) - Suggest a new feature

## Data Agent Definition

Data Agent is a specialized agent that loads business knowledge networks to form high-quality context, and then implements multi-agent collaboration through the Agent framework for planning, reasoning, execution, and security control.

Data Agent is a specialized intelligent agent based on business knowledge networks as a unified business semantic foundation, integrating enterprise multi-source heterogeneous data, business systems, and automated processes. Through ContextLoader, it dynamically and precisely constructs high-quality context, and is driven by the Dolphin dynamic orchestration engine to enable multi-agent completion of planning, reasoning, action, and tool invocation closed loops. Under the guarantee of full-link observability, evaluability, and auditability mechanisms, it leverages large language models to implement Data+AI for enterprise core business scenarios.

## Key Requirements for Data Agent

- **Reducing Agent Development Complexity: Tightly Coupled Business Logic, Difficult to Reuse**
  - Business semantics/metric calibers are fragmented. Agent configurers need to embed semantic logic into prompts and control chains, resulting in poor adaptability of Agent configurations to business scenarios, with Data Agent tightly coupled to business logic.
  - Multi-system tool integration is fragmented (inconsistent interfaces, parameters, error handling), amplifying integration and orchestration costs.

- **Difficult Maintenance and Optimization: Unobservable After Go-live, Optimization Relies on Manual Effort**
  - Business rules, data calibers, and model versions fluctuate with changes, but lacking standard evaluation and regression sets, problems can only be "firefighted" in production.
  - Lack of runtime trajectory and failure reason accumulation (what data/tools were called, where errors occurred), making it difficult to locate issues and form an iterative closed loop.

- **Difficulty Forming High-Quality Context: Context Struggles to Be "Trustworthy, Complete, and Controllable"**
  - Multi-source heterogeneous data caliber conflicts and inconsistent timeliness. Agents lacking evidence priority and constraints are prone to reasoning drift.
  - Context assembly based on permissions and dynamic states by person/role is difficult: either insufficient information leads to wrong answers, or access violations create risks.

- **Difficult Multi-Agent Collaboration: Inconsistent Collaboration Protocols Lead to Friction and Distortion**
  - Inconsistent input/output standards between Agents. Information gets compressed and loses key constraints during multi-round transmission, with results deviating from goals.
  - Lack of global scheduling/arbitration/conflict governance mechanisms. Multiple Agents easily enter loops, disputes, or duplicate efforts, skyrocketing costs.

- **Incomplete Security Control Risk Chain: Untrusted Core Chain Makes Core Production Pipelines Difficult**
  - Reasoning and execution chains are not traceable (what data was used, what tools were called, why it was done this way), making error accountability and review difficult.
  - Prompt injection and unauthorized calls are prominent risks. Without complete tool permissions, data masking, and approval trails, entry into core production pipelines is impossible.

## Technical Goals of Data Agent

### 1. Reducing Agent Development Complexity: Semantic Modeling Decoupling and Low-Code Assembly

Through business knowledge networks, achieve decoupling of business semantic modeling, complete unified semantic alignment of structured/unstructured data and metric caliber standardization, eliminating dependence on hardcoded complex semantic logic. Through no-code/low-code model definitions (Agent roles, Dolphin instructions, and skill configurations), achieve Agent componentization reuse, support rapid migration to new business scenarios, and reduce development barriers and customization costs.

- **Business Knowledge Network Unified Semantic Modeling**: Uniformly abstract concepts, objects, relationships, logic, and actions from the real world in business knowledge networks, unifying all metrics and business semantics for global reuse across all Agents without separately defining business semantics in each Agent.
- **Agent Node Embedding**: Allow different Agents (such as data governance Agent, intelligence analysis Agent) to be embedded as "nodes" in processes, achieving cross-Agent collaboration.
- **Process Reuse**: Through templatized processes (such as "data cleaning-analysis-reporting"), reduce enterprise custom Agent development costs, achieving completely no-code configuration.

### 2. Improving Maintenance and Optimization Efficiency: Agent Full Lifecycle Automation Closed Loop

Based on runtime trajectory data (context, reasoning, tools, permission stages), quickly locate problem root causes. Drive automatic optimization (prompts, tool parameters, business knowledge network definitions) through Benchmark and effectiveness evaluation, combined with manual review of core configurations, achieving "configuration-evaluation-runtime-observability-optimization" automation closed loop, improving Agent stability and iteration efficiency.

- **Observation**: Through Dolphin Runtime's observability module, collect Agent runtime data (such as performance metrics, error logs).
- **Optimization**: Based on observation data, automatically adjust Agent parameters (such as Plan strategies, model weights, recall strategies, etc.).

### 3. High-Quality Context: Precise Assembly and On-Demand Loading

Leveraging business knowledge networks and ContextLoader to achieve precise cross-system, cross-session context loading (replacing coarse vector retrieval), combined with permission policies and Memory (dynamic assembly by person/role/task and Agent state), reducing context noise and access violation risks, improving Agent task execution accuracy.

- **Concept Recall**: Based on knowledge graphs or semantic understanding, extract core concepts from context.
- **Object Recall**: Based on identified concepts, precisely recall entity data from context through semantic transformation.
- **Pre-Ranking/Re-Ranking**: Based on configuring different recall strategies and automatically associating appropriate sorting algorithms, filter context most relevant to tasks.

### 4. Multi-Agent Collaboration: Unified Semantics and Dynamic Scheduling

Based on unified semantic protocols and Dolphin scheduling engine, achieve dynamic task division and automatic orchestration between Agents. Through shared Memory (multi-Agent task state transfer, business knowledge network semantics), reduce collaboration distortion and siloing effects, improving multi-Agent collaboration efficiency.

- **Context Compression**: May employ self-developed algorithms (such as dynamic context pruning, semantic compression), reducing memory usage during inference.
- **Coroutine Scheduling**: Through lightweight coroutine management, optimize multi-task concurrency (such as simultaneous data queries, tool calls).
- **State Machine Management**: Abstract Agent decision processes (Plan-Reason-Act) into state machines, ensuring process controllability and traceability.
- **Observability**: Built-in monitoring metrics (such as inference latency, error rate, resource usage), providing data support for "observation-optimization" phases.

### 5. Security Control: Full-Link Auditable Defense Guardrails

Through security policy layers (permission verification, sensitive information filtering, prompt injection protection) and tool call whitelists/minimum permissions, combined with Human-in-the-loop approval (critical actions), achieve full-link trackability and auditability, meeting enterprise compliance, risk control, and accountability requirements.

- **Role and Access Policies**: Role-Based Access Control (RBAC) for access control, restricting different users' permissions to Agents.
- **Log Auditing**: Record all Agent operations (such as Plan decisions, Act executions), meeting compliance requirements like classified protection and GDPR.
- **Data Security Services**: Support data encryption, data masking, sensitive data detection and filtering, prompt injection protection, and other security capabilities.

## Business Value of Data Agent

- **Decision Efficiency: From "Information Production" to "Decision Driving"**
  - Transform "labor costs" of data collection, caliber alignment, and analysis writing into reusable decision assets, making management actions faster and more consistent. For example, in business review/weekly-monthly report scenarios, automatically align calibers for issues like declining sales, profit fluctuations, and TopN anomalies, outputting meeting-ready conclusions, attributions, key evidence, and action recommendations.

- **Trustworthy Knowledge: From "Word of Mouth" to "Documented Evidence"**
  - Unify internal enterprise calibers for answers to the same question, with traceable and reviewable answers, reducing communication costs and misjudgment risks. In business Q&A scenarios, DataAgent uniformly recalls multi-source information based on ContextLoader and cites business knowledge network sources, outputting "conclusions + evidence chains."

- **Process Automation: From "Manual Chaining" to "Closed-Loop Delivery"**
  - Transform cross-department tasks into executable, trackable, and approvable standard processes, significantly reducing collaboration friction and rework. For example, in specialized report materials/operations follow-up scenarios, chain "query-analysis-writing-verification-approval-implementation" into AutoFlow; different nodes are completed by different Agents, with humans only doing key confirmations/approvals, tasks automatically progressing to delivery.

- **Usable Data Assets: From "After-the-Fact Firefighting" to "Continuously Stable Availability"**
  - Continuously reduce the business impact of metric caliber conflicts and data quality issues, accumulating long-term capabilities for "the same set of data." When metric anomalies, caliber conflicts, or data source changes occur, DataAgent automatically locates impact scope and differences, generates governance recommendations, and links to tickets/processes for closed-loop processing.

- **Controllable Risk: From "Unusable Black Box" to "Auditable Production Capability"**
  - Without sacrificing efficiency, ensure data and behavior are compliant and controllable, allowing AI to enter core business pipelines. In sensitive scenarios like finance/legal/HR/customer data, introduce permission boundaries, approval trails, and full-link tracing for sensitive data access and critical operations; outputs are reviewable and replayable, meeting audit and internal control requirements.

## Product Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              Data Agent Applications                                 │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐        │
│  │ Data Governance│ │ Intelligence   │ │ Quality        │ │ Ops Analysis   │        │
│  │ Agent          │ │ Analysis Agent │ │ Detection Agent│ │ Agent          │ ...    │
│  └────────────────┘ └────────────────┘ └────────────────┘ └────────────────┘        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                         Data Agent Lifecycle Management                              │
│              Configure → Test → Publish → Run → Observe → Optimize                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                  Core Components                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  Autoflow: Agent Node Embedding → Node → Node → Node (Orchestrable Reuse)     │
│  ├─────────────────────────────────────────────────────────────────────────────┤   │
│  │  ISF (Security Fabric): Unified Auth | Role & Access Policies | Audit Logs    │
│  ├─────────────────────────────────────────────────────────────────────────────┤   │
│  │  Model Factory: General Models | Industry Models                              │
│  ├─────────────────────────────────────────────────────────────────────────────┤   │
│  │  Business Knowledge Network:                                                   │
│  │    Data (Unstructured/Structured/Machine) → Find Data                         │
│  │    Logic (Methods/Domain Models) → Find Operators                             │
│  │    Actions (API/MPC) → Find Actions                                           │
│  ├─────────────────────────────────────────────────────────────────────────────┤   │
│  │  ContextLoader: Concept Recall | Object Recall | Pre-Ranking | Re-Ranking     │
│  ├─────────────────────────────────────────────────────────────────────────────┤   │
│  │  Dolphin Runtime:                                                              │
│  │    Plan → Act → Reason (Loop) | Coroutine Scheduling | Context Compression    │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                            Interaction & Flow                                        │
│  Master Agent ─┬→ Data Recall Agent → Data Recall → Return Data                     │
│                ├→ Tool Call Agent → Tool Call → Return Data                         │
│                └→ Result Generation Agent → Generate Result → Return Result         │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Platform Architecture

```text
┌─────────────────────────────────────────────┐
│              DIP Platform                   │
│  ┌───────────────────────────────────────┐  │
│  │             AI Store                  │  │
│  ├───────────────────────────────────────┤  │
│  │            DIP Studio                 │  │
│  ├───────────────────────────────────────┤  │
│  │          Decision Agent               │  │
│  ├───────────────────────────────────────┤  │
│  │               ADP                     │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### Core Subsystems

| Sub-project | Description | Repository |
| --- | --- | --- |
| **DIP** | Decision Intelligence Platform (DIP) | [kweaver-ai/dip](https://github.com/kweaver-ai/dip) |
| **AI Store** | AI application and component marketplace | *Coming soon* |
| **Studio** | DIP Studio - Visual development and management interface | [kweaver-ai/studio](https://github.com/kweaver-ai/studio) |
| **Decision Agent** | Intelligent decision agent | [kweaver-ai/decision-agent](https://github.com/kweaver-ai/decision-agent) |
| **ADP** | AI Data Platform - Core development framework, including Ontology Engine, ContextLoader, and VEGA data virtualization engine | [kweaver-ai/adp](https://github.com/kweaver-ai/adp) |
| **Operator Hub** | Operator management and orchestration platform | [kweaver-ai/operator-hub](https://github.com/kweaver-ai/operator-hub) |
| **Sandbox** | Sandbox runtime environment | [kweaver-ai/sandbox](https://github.com/kweaver-ai/sandbox) |

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to contribute to this project.

Quick start:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE.txt) file for details.

## Support & Contact

- **Contributing**: [Contributing Guide](CONTRIBUTING.md)
- **Issues**: [GitHub Issues](https://github.com/kweaver-ai/decision-agent)
- **License**: [Apache License 2.0](LICENSE.txt)

---

More components will be open-sourced in the future. Stay tuned!
