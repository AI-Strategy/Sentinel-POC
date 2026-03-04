name
  infrastructure-and-resilience
description
  Rules for Ports, CORS, and System Stability.
alwaysApply
  true

# Infrastructure Laws
1. **Port Discipline (No New Ports)**: 
   - NEVER open a new port (e.g., 3001) because the default (3000) is "blocked."
   - **Action**: Identify and kill the zombie process occupying the port.
2. **The Monster of CORS**:
   - **Dev**: Use **Vite Proxy** (`server.proxy`) to tunnel requests. Do not hack headers.
   - **Prod**: Handle CORS at the **GCP Load Balancer** level or via strict Middleware (no wildcard `*`).
3. **Self-Healing**: 
   - All automation scripts must "Fail Closed" and log to `.audit/`.
   - Never leave a system in an undefined state.
