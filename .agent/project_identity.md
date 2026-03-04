# Project Identity & Domain Context

## 1. The Architect
* **User**: Crispin Courtenay
* **Role**: AI Foundational Architect & Fractional CTO
* **Firm**: AI Strategy / VerticGraph
* **Core Philosophy**: "Precision, Security, and Autonomy."

## 2. The Ecosystem: "Talos" Architecture
*The foundational architecture powering all projects.*
* **Core Mission**: Solve for LLM Memory Drift, enforce strict security guardrails, and provide citable, deterministic reasoning.
* **Key Mechanic**: **Twin-Graph Architecture**.
    * **Shared Graph (Public)**: Documentation, Libraries, Syntax.
    * **Private Graph (User)**: Business Logic, PII, Secrets. *Strictly encrypted and segregated.*
* **Security Standard**: **OpenClaw Exoshell**. All agents operate within a security-hardened shell using brokered authentication and client-held keys.

## 3. Active Initiatives (The "What")

### **A. Protocol Zero**
* **Definition**: AI Pair-Programming SaaS & "Second Brain" architecture.
* **Key Differentiator**: "Twin-Graph" memory separation. Users own their private knowledge graph keys.
* **Target Stack**: Python/Rust (Backend), React/Vite (Frontend), Neo4j (Memory).

### **B. VerticGraph**
* **Definition**: LegalTech Intelligence Platform.
* **Constraint**: **High-Compliance**. Requires "LegalTech Rule" (07) enforcement.
* **Focus**: Transforming raw legal data into queryable knowledge graphs.
* **Relation to Talos**: VerticGraph is the *application layer* built on the Talos *reasoning engine*.

### **C. Project Hlidskjalf**
* **Definition**: Super-premium, on-demand opposition research service.
* **Constraint**: **Digital SCIF**. Absolute data isolation. No data leaves the Private VPC.

### **D. Mimisbrunr**
* **Definition**: The "Wisdom Engine."
* **Function**: Scores and ranks strategic decisions based on process quality and outcomes.

## 4. Operational Mandates
1.  **"Don't Be Stupid" (DBS)**: If a high-risk action is detected (deletion, financial), **PAUSE** and reflect.
2.  **100-Day Goal**: All systems must be designed for **Autonomy**. The goal is to minimize human maintenance to allow for a "100-day ski season" lifestyle.
3.  **Antigravity Mode**: Automation is preferred over manual intervention. If a task is repeated 3 times, write a skill for it.

## 5. Technical North Star
* **Language**: Python (Architectural) / Rust (Performance).
* **Frontend**: React + Tailwind (Strict Types).
* **Data**: Neo4j (Graph/Vector) + Postgres (Relational) + Redis (Ephemeral).
* **Infra**: GCP (Zero Trust/OIDC).
