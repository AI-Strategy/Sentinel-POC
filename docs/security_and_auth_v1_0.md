# 🛡️ Sentinel Security & Authentication Protocol v1.0

## 1. Overview
Sentinel v2.0 implements a "Defense in Depth" strategy for enterprise data liquidity. This protocol codifies the mandatory transport security and authentication layers required for forensic auditing.

## 2. Transport Layer Security (HTTPS)
To prevent man-in-the-middle attacks and interception of sensitive financial data, all components are served over HTTPS.

### A. Frontend (Vite/React)
- **Plugin**: `@vitejs/plugin-basic-ssl`
- **Port**: 5173 (Secure)
- **Configuration**: `server.https: true`
- **Substrate**: Served via `https://localhost:5173`

### B. Backend (FastAPI/Uvicorn)
- **Implementation**: Uvicorn with SSL keys.
- **Artifacts**: `backend/cert.pem` and `backend/key.pem` (2048-bit RSA).
- **Endpoint**: `https://localhost:8000`
- **Requirement**: Browsers must trust the backend certificate (Proceed past safety warning) to allow AJAX/Fetch calls from the frontend.

## 3. Authentication & Authorization (JWT)
Sentinel uses a stateless, token-based authentication system.

### A. The Login Flow
1. **Identity Proof**: User provides credentials via the modern glassmorphism Login Page.
2. **Substrate Verification**: Backend verifies credentials against the secure identity core.
3. **Token Issuance**: A secure JWT is generated using common `HS256` HMAC algorithms.
4. **Session Persistence**: The token is stored in the browser's `localStorage` and attached to all subsequent `Authorization: Bearer <TOKEN>` headers.

### B. Default Access (POC Credentials)
| Resource | Identity | Access Key |
| :--- | :--- | :--- |
| **Forensic Portal** | `admin` | `sentinel2026` |

## 4. Substrate Protection
- **API Lockdown**: All critical endpoints (`/reconcile`, `/dashboard/metrics`, `/query`) are protected by the `verify_api_key` (JWT-based) dependency.
- **CORS Policy**: Configured to allow cross-origin requests from the secure frontend port.

## 5. Deployment Instructions
To refresh the security substrate:
1. Generate new keys: `python tmp/gen_certs.py`
2. Restart the orchestrator: `docker-compose up -d --build`
3. Launch frontend: `npm run dev`

---
*Created on March 4, 2026*
*Security Clearance: Executive Auditor*
