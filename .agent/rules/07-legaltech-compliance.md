name
  legaltech-compliance
description
  Standards for citable legal reasoning, jurisdictional locking, and privilege tagging.
alwaysApply
  false

# LegalTech Compliance Laws (STRICT ENFORCEMENT)
1. **Direct Quotation Mandate**:
   - Paraphrasing statutory material, case law, or contract clauses is **FORBIDDEN**.
   - You MUST provide direct quotes from the source text.
   - *Format*: `"...text..." (Section 12.3)`.
2. **Jurisdictional Locking**:
   - All generated legal artifacts must include a `jurisdiction_id` metadata tag (e.g., `US-CA`, `CA-ON`).
   - Defaulting to "General Law" without explicit user instruction is a validation failure.
   - If multi-jurisdictional (e.g., US & Canada), provide a **Comparative Analysis** table.
3. **Privilege & Data Sovereignty**:
   - **Tagging**: All reasoning chains, logs, and graph nodes related to client data must be tagged `#PRIVILEGED_WORK_PRODUCT`.
   - **Storage**: These artifacts must be stored exclusively in the encrypted "Private Knowledge" tier of the Twin-Graph.
   - **Leakage**: Never use client data to prompt-tune public models.
4. **Defensible Reasoning**:
   - Every legal conclusion must be linked to a specific node in the GraphRAG or a verified external citation.
   - *Hallucination Tolerance*: **Zero**.
