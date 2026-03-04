# Issue: Node.js 20 Undici IPv6 Timeout (Next.js 15)

## Date: 2026-02-23
**Status:** Resolved
**Component:** Frontend API Routes (`app/api/copilot/route.ts`), Google GenAI SDK (`@google/genai`)
**Impact:** `fetch failed` (500 Internal Server Error) on initial model generation causing an alternating "Network Failure" in the UI.

### Context
When integrating the unified `@google/genai` SDK within Next.js 15 App Router API routes on Node 20+, a severe network hang occurred resulting in a 10,000ms delay followed by an `UND_ERR_CONNECT_TIMEOUT`. This issue often manifested as alternating successes and failures (e.g., "it works, then it does not work on the first post") due to Round Robin DNS load balancing hitting unresponsive IPv6 addresses.

### Root Cause
Node 20 utilizes `undici` for its native global `fetch` API. Due to a known issue in Windows/Docker environments, `undici` prefers IPv6 resolution (`generativelanguage.googleapis.com`). If the local network cannot successfully route IPv6 traffic, `undici` hangs until the 10-second DNS resolution timeout expires. 

This issue is exacerbated by Turbopack in Next.js, which spawns worker threads that do NOT robustly inherit the parent CLI thread's process execution flags (`--dns-result-order=ipv4first`). Finally, `@google/genai` drops the `fetch` override from its configuration, preventing an easy native bypass.

### Resolution
The resolution enforces IPv4 DNS resolution by completely replacing the broken `undici` global fetch specifically within the API route, forcing the SDK to use `node-fetch`, which correctly respects `node:dns` behaviors.

**Implementation (in the API Route):**
```typescript
import nodeFetch from 'node-fetch';
import dns from 'node:dns';

// Fix Node 20 / node-fetch IPv6 timeout bug natively
dns.setDefaultResultOrder('ipv4first');

// Intercept global fetch so @google/genai is forced to use node-fetch (which respects dns.setDefaultResultOrder)
// overriding the broken Next.js Turbopack Undici implementation.
const originalFetch = globalThis.fetch;
globalThis.fetch = nodeFetch as unknown as typeof globalThis.fetch;

const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY as string });
```
