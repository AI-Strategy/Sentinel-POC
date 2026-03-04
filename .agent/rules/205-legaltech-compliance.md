# 205: LegalTech Compliance & Precision

## 1. Defensible Reasoning & Citability
- Every legal summary, contract analysis, or statutory interpretation must quote directly from the source material where possible.
- Distinguish clearly between Law (statutes/regulations), Interpretation (case law/commentary), and Application (fact-specific analysis).
- All AI-generated legal reasoning must be "deterministic and citable"—linking every conclusion to a specific node in the GraphRAG or a verified external legal database.

## 2. Jurisdictional Awareness
- Explicitly identify the governing jurisdiction for all legal documents or advice (e.g., California, US Federal, or Canadian Law).
- If a task involves multi-jurisdictional elements (e.g., VerticGraph’s US/Canadian privacy policies), provide a comparative analysis rather than a generalized summary.

## 3. Data Sovereignty & Privilege
- Adhere to the "Digital SCIF" pattern for all client-related data. 
- Ensure that "Attorney-Client Privilege" labels are applied to relevant generated artifacts where the user (as a Clio Partner or Developer) is handling sensitive legal logic.
- Mitigate data leakage by ensuring legal work-product is stored in the "Private Knowledge" graph and never used to fine-tune or prompt-inject public-facing models.

## 4. Compliance Audit Readiness
- Write all technical and legal documentation as if it will be read aloud in court or cited in a compliance audit.
- Maintain a "Chain of Custody" for data transformations: Document exactly how raw legal data was processed, summarized, and verified by the agent.
