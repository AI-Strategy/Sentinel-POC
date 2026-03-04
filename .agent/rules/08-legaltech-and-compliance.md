# LegalTech Compliance & Defensibility (STRICT ENFORCEMENT)

1. **Direct Quotation Mandate**: Any analysis of statutory material or contract clauses MUST include direct quotes. Paraphrasing legal text without a direct reference is a critical failure.
2. **Jurisdictional Locking**: All generated legal artifacts must include a `jurisdiction_id` in the metadata. Defaulting to a general jurisdiction without explicit user instruction triggers a validation error.
3. **Work-Product Privilege**: All logs and generated reasoning files related to client data must be tagged `privileged_work_product`. These files must be stored in the encrypted "Private Knowledge" tier of the Twin-Graph.
4. **Audit Trail Generation**: Every data transformation involving LegalTech logic must append an entry to the `.audit/` log, detailing the raw source, the transformation logic used, and the verification timestamp.
