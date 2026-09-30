# Quantum Risk AI — System Limitations, Assumptions & Future Roadmap
## Known Boundary Conditions, Assumptions, and Enterprise Production Path

### 1. Current System Assumptions
1. **Asset Scoping:** Current default database models 100 enterprise assets representing ABC Bank's core banking network. While the architecture scales horizontally to 10,000+ assets, full-graph traversal on dense networks requires indexed edge matrices.
2. **Financial Loss Models:** Parametric downtime rates (₹3,00,000/hr) and DPDP Act base legal costs are calibrated for Indian Scheduled Commercial Banks; multinational organizations require multi-currency and regional regulatory penalty profiles (e.g. GDPR, CCPA).
3. **Telemetry Connectors:** Wazuh and OpenVAS connectors are designed for on-premise deployments. In the absence of live on-premise credentials, they operate in fallback diagnostic mode.

---

### 2. Known Constraints & Boundary Conditions
- **NIST NVD Public API Rate Limiting:** Unauthenticated calls to NIST NVD 2.0 API are capped at 5 requests per 30-second rolling window. For high-volume enterprise deployments, an official NVD API key should be placed in `NVD_API_KEY`.
- **Single-Node Cryptographic Ledger:** For hackathon portability, the blockchain audit layer operates a local SHA-256 Merkle chain alongside the Hyperledger Fabric v2.5 channel client. A full production multi-peer Raft consensus deployment requires Docker Swarm or Kubernetes orchestration.
- **Continuous Learning Retraining Cadence:** Retraining the XGBoost pipeline on incoming telemetry executes synchronously in the current version; enterprise deployments should offload retraining to an asynchronous Celery/Redis worker queue.

---

### 3. Future Production Roadmap
1. **Agentic Remediation Dispatch:** Integrate with Ansible Tower and ServiceNow ITSM to automatically open change requests and dispatch playbooks upon CISO approval.
2. **Dynamic Cyber Insurance Underwriting:** Connect the FAIR Monte Carlo tail-risk engine (95th percentile Cyber VaR) to cyber insurance carrier APIs to quote dynamic policy premiums based on real-time posture.
3. **Zero-Knowledge Proofs (ZKP):** Implement ZK-SNARKs on the blockchain audit layer, allowing banks to prove regulatory compliance to RBI without exposing sensitive internal network topology or asset vulnerabilities.
