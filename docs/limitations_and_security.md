# Security Requirements & Operational Limitations

## 1. Security Architecture & Threat Model

- **Untrusted Input Handling**: All uploaded CSV datasets, extracted IOC values, and external API responses are treated as untrusted data and strictly validated against Pydantic schemas.
- **Resource Exhaustion Controls**:
  - File upload limits enforced (100 MB default).
  - Maximum row batch limits on synchronous prediction endpoints (capped at 100 flows per batch request).
- **Safe Authentication**:
  - Passwords hashed using PBKDF2 with SHA-256 and unique 16-byte cryptographically secure salts.
  - Role-based authorization for administrative operations (admin, analyst, observer).
- **Secret Separation**: API keys for external services (VirusTotal, AbuseIPDB, LLM providers) are exclusively loaded from environment variables and never logged or serialized into client responses.
- **Defensive Safeguards**: The platform operates as a passive detection, enrichment, and analysis system. It does not perform autonomous blocking, modification of production firewall rules, or destructive endpoint remediation without explicit human analyst authorization.

## 2. Operational Assumptions & Limitations

- **Simulated vs Live Telemetry**: Live packet capture (PCAP) requires raw socket privileges and network TAP/SPAN configuration. The platform currently supports NetFlow CSV ingestion and streaming replay. Live capture interfaces are structured as pluggable future ingestion adapters.
- **Federated Learning Simulation**: The federated learning module executes an authentic local simulation of the FedAvg coordinator and client nodes. Production multi-tenant federated deployment across separate untrusted enterprises would additionally require secure enclave aggregation (e.g. differential privacy, homomorphic encryption, or secure multi-party computation) to protect against model inversion attacks.
- **Explainability Constraints**: Feature-level sensitivity attributions indicate statistical correlation with model decisions; they do not constitute mathematical proof of causality or real-world adversary intent.
- **Threat Intelligence Verification**: An IP address observed in an anomalous flow is classified as an observed indicator, not a verified malicious threat actor, until confirmed by threat intelligence enrichment or human investigation.
