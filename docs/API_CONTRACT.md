# Quantum Risk AI — API Specification & Data Contract
## RESTful Endpoints, Schemas, and Authentication Protocols

### 1. Authentication & Base Headers
All authenticated endpoints require an RFC 6750 Bearer token passed in the `Authorization` header:
```http
Authorization: Bearer <JWT_ACCESS_TOKEN>
```
Tokens are issued via `POST /api/v1/auth/login` using standard OAuth2 password credentials.

---

### 2. Core API Endpoints

#### 2.1 Authentication & RBAC
- **`POST /api/v1/auth/login`**
  - *Request Body:* `{"email": "ciso@abcbank.com", "password": "Ciso@12345"}`
  - *Response (200 OK):*
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1Ni...",
      "token_type": "bearer",
      "user": {
        "id": "usr-ciso-01",
        "email": "ciso@abcbank.com",
        "full_name": "Vikram Malhotra",
        "role": "CISO",
        "organization_id": "org-abc-bank"
      }
    }
    ```
- **`GET /api/v1/auth/me`**
  - Returns authenticated user identity and permissions.

#### 2.2 Enterprise Asset Inventory
- **`GET /api/v1/assets`**
  - *Query Params:* `asset_type`, `internet_exposed`, `min_criticality`, `search`
  - *Response (200 OK):* Array of 100 enterprise asset objects with criticality scores [0-100].
- **`GET /api/v1/assets/template-csv`**
  - *Response (200 OK):* `text/csv` header template for organizational infrastructure imports.
- **`GET /api/v1/assets/export-csv`**
  - *Response (200 OK):* `text/csv` attachment of all enterprise assets.
- **`POST /api/v1/assets/import-csv`**
  - *Request Body:* `{"csv_content": "name,asset_type,ip_address..."}`
  - *Response (200 OK):*
    ```json
    {
      "status": "SUCCESS",
      "imported_count": 2,
      "imported_names": ["Branch Gateway Router 01", "HR Employee Portal"],
      "data_origin": "ORGANIZATION-PROVIDED DATA"
    }
    ```

#### 2.3 Vulnerability Management & CISA KEV
- **`GET /api/v1/vulnerabilities`**
  - *Query Params:* `severity` (`CRITICAL`, `HIGH`, etc.), `active_exploit_only` (`true`/`false`), `limit`
  - *Response (200 OK):*
    ```json
    {
      "total": 500,
      "stats": {
        "total": 500,
        "critical": 50,
        "high": 180,
        "cisa_known_exploited": 6
      },
      "items": [...]
    }
    ```

#### 2.4 Quantitative Cyber Risk (Open FAIR)
- **`GET /api/v1/risk/enterprise`**
  - *Response (200 OK):*
    ```json
    {
      "enterprise_risk_score": 82.0,
      "expected_annual_loss": 46000000.0,
      "risk_level": "CRITICAL",
      "risk_contributors": {
        "active_exploits": 32.0,
        "crown_jewel_criticality": 27.0,
        "internet_exposure": 18.0,
        "patch_cadence_lag": 14.0,
        "threat_actor_targeting": 9.0
      }
    }
    ```
- **`GET /api/v1/financial/exposure`**
  - *Response (200 OK):* Breakout of 6 banking loss components (Downtime, IR, Recovery, Legal/DPDP, Business Interruption, Total).
- **`GET /api/v1/financial/monte-carlo`**
  - *Query Params:* `iterations=10000`
  - *Response (200 OK):* 10th, 50th, 85th, 95th percentiles and loss distribution histogram.

#### 2.5 Predictive AI & Explainability
- **`GET /api/v1/prediction/future-risk`**
  - *Response (200 OK):*
    ```json
    {
      "current_risk": 82.0,
      "predicted_30_day": 85.5,
      "predicted_60_day": 88.0,
      "predicted_90_day": 91.5,
      "trend": "INCREASING",
      "model_type": "XGBoost Regressor (Tree SHAP Enabled)",
      "top_drivers": [
        {"feature": "Unpatched Critical CVEs", "shap_value": 5.2},
        {"feature": "Patch Cadence Lag", "shap_value": 2.8}
      ]
    }
    ```

#### 2.6 Investment Optimizer (Google OR-Tools)
- **`POST /api/v1/optimization/solve`**
  - *Request Body:* `{"budget_amount": 10000000.0}`
  - *Response (200 OK):*
    ```json
    {
      "budget_amount": 10000000.0,
      "total_investment": 8500000.0,
      "current_modeled_risk": 46000000.0,
      "projected_modeled_risk": 20000000.0,
      "modeled_risk_reduction": 26000000.0,
      "efficiency_metric": 3.06,
      "selected_controls": [
        {"code": "CTRL-PATCH", "name": "Automated Critical Vulnerability Patching", "cost": 1800000.0},
        {"code": "CTRL-MFA", "name": "Privileged Identity Multi-Factor Authentication", "cost": 1200000.0},
        {"code": "CTRL-EDR", "name": "Next-Gen EDR / XDR Autonomous Response", "cost": 2500000.0},
        {"code": "CTRL-SEG", "name": "Network Micro-segmentation & Zero Trust", "cost": 2000000.0},
        {"code": "CTRL-BACKUP", "name": "Immutable WORM Air-Gapped Backup Vault", "cost": 1000000.0}
      ]
    }
    ```

#### 2.7 Blockchain Audit & Tamper Sandbox
- **`GET /api/v1/blockchain/ledger`**
  - *Response (200 OK):* Sequential immutable block list with hashes, nonces, and signatures.
- **`POST /api/v1/blockchain/verify`**
  - *Request Body:* `{"record_id": "ALL"}`
  - *Response (200 OK):* Verification status of genesis-to-latest cryptographic hash pointers.
- **`POST /api/v1/blockchain/tamper-test`**
  - Simulates database corruption and validates that the ledger catches the mismatch.
- **`POST /api/v1/blockchain/restore`**
  - Self-healing auto-restoration from the cryptographic hash tree.
