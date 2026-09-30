# Quantum Risk AI — Security Architecture & Access Control
## Authentication, RBAC Matrix, Cryptographic Standards, and Hardening

### 1. Authentication & Session Security
- **OAuth2 Bearer Tokens:** State-of-the-art JSON Web Tokens (JWT) signed using HMAC-SHA256 (`HS256`) with a cryptographically randomized 256-bit secret key.
- **Password Hashing:** Passlib with **Bcrypt** adaptive key derivation (`rounds=12`), resistant to rainbow table lookups and GPU brute-force attacks.
- **Token Expiration:** Access tokens expire after 480 minutes (8 hours), with token refresh capability.
- **Security Headers:** CORS middleware configured with explicit allowed origins, restricting unauthorized cross-domain access.

---

### 2. Granular 6-Role RBAC Matrix

Quantum Risk AI enforces strict separation of duties across all 6 enterprise personas:

| Action / Capability | CISO | Security Analyst | Risk Analyst | Executive / CFO | Compliance Auditor | System Admin |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **View Executive Dashboard** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Inspect Asset Inventory** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Import / Export Asset CSV** | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Trigger Vuln Feed Sync** | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Recalculate FAIR Risk Engine** | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Tune Financial Assumptions** | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Retrain XGBoost ML Pipeline** | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Run Investment Optimizer** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Authorize CISO Approval** | **✅** | ❌ *(403)* | ❌ *(403)* | ❌ *(403)* | ❌ *(403)* | ❌ *(403)* |
| **Verify Blockchain Ledger** | ✅ | ✅ | ✅ | ✅ | **✅** | ✅ |
| **Launch Tamper Sandbox** | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Platform System Settings** | ✅ | ❌ | ❌ | ❌ | ❌ | **✅** |

---

### 3. Data Protection & Defense-in-Depth
- **SQL Injection Prevention:** 100% of database queries utilize SQLAlchemy parameterized statements and ORM queries; no dynamic string concatenation is permitted.
- **Input Validation:** Every API request is strictly typed and sanitized using Pydantic schemas with type coercion and value range bounds.
- **Rate Limiting & Denial of Service Defense:** API routes validate request payload sizes (CSV imports bounded at 5MB).
- **Audit Logging:** Every critical state transition (login, risk recalculation, budget solve, CISO approval) writes an immutable entry into both the relational `AuditLog` table and the cryptographic blockchain ledger.
