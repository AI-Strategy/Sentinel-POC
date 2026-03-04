# Global Rule: Software Version Currency & Downgrade Ban

**Severity**: CRITICAL
**Scope**: Global

## Directive
Never downgrade software dependencies, libraries, SDKs, or models without explicit human permission.

## Requirements
1.  **Untrusted Training Data**: Acknowledge that your training data is 18 months or more out of date. It is inherently untrusted for current, modern software versions.
2.  **Version Enforcement**: If you encounter an API change or error that your training data suggests is fixed in an older version, **DO NOT DOWNGRADE**. Modern tools and SDKs (such as Next.js 16, React 19, newer LLM SDKs, etc.) intentionally deprecate older methods.
3.  **Forward Resolution**: You must resolve errors by finding the correct, modern implementation path (e.g., reading current SDK typing, running web searches, or using MCP tools) rather than retreating to deprecated patterns.
4.  **Consent**: If a downgrade truly appears to be the only viable path, you must ask the human operator for explicit permission before modifying any `package.json`, `Cargo.toml`, `requirements.txt`, or inline model identifiers.

## Enforcement
Any attempt to downgrade a package or model version without explicit human approval is a critical violation of the workspace contract and will result in immediate termination of the operation.
