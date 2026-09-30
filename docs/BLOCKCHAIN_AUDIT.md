# Quantum Risk AI — Cryptographic Audit & Blockchain Integrity
## Hyperledger Fabric v2.5, SHA-256 Merkle Chaining, and Tamper-Detection Sandbox

### 1. The Need for Tamper-Evident Audit Trails
In enterprise cyber risk governance and regulatory compliance (e.g. RBI Master Directions, SEBI CSCRF, SOX 404, ISO 27001):
- Regulators require proof that risk evaluations and CISO decisions were not altered retroactively.
- Traditional database audit logs are vulnerable to privileged insider tampering (`UPDATE audit_logs SET status = 'APPROVED'`).
- A cryptographically linked ledger ensures that any unauthorized modification immediately breaks hash pointer continuity, triggering alerts and auto-healing.

Quantum Risk AI implements a **dual-architecture audit layer**:
1. **Hyperledger Fabric v2.5** enterprise decentralized channel.
2. **Canonical Local SHA-256 Merkle Chain** for environments without multi-node Fabric deployments.

---

### 2. Cryptographic Block Structure & Hash Formula

Each block committed to the ledger contains:
- `index`: Sequential integer block height ($0, 1, 2, \dots$).
- `timestamp`: ISO-8601 UTC timestamp of block commit.
- `record_type`: Event type (`GENESIS`, `RISK_ASSESSMENT`, `OPTIMIZATION_PLAN`, `CISO_APPROVAL`, `CONTROL_DEPLOYMENT`).
- `record_id`: UUID of the evaluated business object.
- `data_payload`: Canonical JSON representation of the decision state.
- `previous_hash`: SHA-256 hex digest of block $i-1$.
- `current_hash`: Cryptographic proof hash of block $i$.
- `ciso_digital_signature`: Simulated RSA-2048 / ECDSA signature verifying executive consent.

#### Canonical Block Hash Formula:
$$H_i = \text{SHA-256}\Big(\text{index} \parallel \text{timestamp} \parallel \text{previous\_hash} \parallel \text{record\_type} \parallel \text{CanonicalJSON}(\text{payload})\Big)$$

---

### 3. Verification & Tamper Detection Sandbox

The platform features an interactive **Tamper Detection Sandbox** designed to prove cryptographic defenses to SIH judges:
1. **Normal Verification:** The system iterates from Genesis ($H_0$) to Block #$N$, verifying that:
   $$H_i = \text{SHA-256}(\text{Block}_i) \quad \text{and} \quad \text{Block}_i.\text{previous\_hash} == \text{Block}_{i-1}.\text{current\_hash}$$
2. **Simulated Malicious Modification:** An evaluator clicks *"Launch Tamper Test"*, which maliciously updates an off-chain database record (e.g. altering an unapproved risk assessment to "APPROVED").
3. **Detection Alert:** The verification engine immediately flags **Block Hash Mismatch**:
   - `Expected Hash:` `59d06615bb26...`
   - `Calculated Hash:` `551f70c3e977...`
   - `Status:` **`TAMPERING_DETECTED`**
4. **Self-Healing Auto-Restoration:** The CISO can trigger *"Restore Ledger"*, which pulls the authentic signed block from the cryptographic hash tree and overwrites the corrupted database record, returning the system to 100% verified status.
