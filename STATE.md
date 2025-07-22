# MISO Factory - Project State & Manifest

## 1. Definitive Master Project Manifest (v2.1)
This is the final specification for the MISO Factory.

### I. Core Operating & Diagnostic Protocols
* **Never Say Die / Never Terminate Protocol**: The prime directive.
* **Process Optimization Protocol**: Continuously improve our own methodology.
* **State Verification First**: Verify state before acting.
* **Phased Evolution**: Implement capabilities in logical, risk-mitigating phases (Epochs).
* **The Living Document Protocol**: The final action of any Epoch must be to update this document.
* **"Golden Image" Mandate**: Produce a complete `definitive_genesis.sh` script for each major, stable version.

### II. Final System Architecture
* **Fractal Agent Hierarchy**: A recursive hierarchy of AI agents (Kingdom...Species).
* **Engram Memory Architecture**: Content-addressable storage with a Semantic Index.
* **Core Infrastructure & Patterns**:
    * **Strict API Contract (Modularity)**: Using gRPC/Protobuf.
    * **Asynchronous Message Bus (Scalability)**: Using a message queue.
    * **Standard Agent Template (Simplicity)**: A reusable "agent chassis."
    * **Circuit Breaker Pattern (Robustness)**: To prevent cascading failures.
* **Universal Governing Protocols**:
    * **The Goal Kernel (Digital DNA)**: Ensures goal alignment.
    * **The Resource Broker (Metabolism)**: Manages resource budgets.
    * **The Telemetry Protocol (Collective Consciousness)**: Provides an auditable "chain of thought."

### III. The Prime Directive of Self-Evolution
* **The Inquisitor Protocol**: An agent's drive to self-analyze and experiment.
* **The Promotional Pathway**: A system for successful "mutations" to evolve the entire system.
* **The Council of Elders**: A top-level supervisory function for high-risk missions.

### IV. User Interface, Security & Commercialization
* **Administrator & End-User Portals**.
* **Role-Based Access Control (RBAC)**.
* **Agent Store & Monetization**.

### V. The Evolutionary Roadmap (Epochs)
* **Epoch I: The Foundation (COMPLETE)**: Established a stable, multi-service application with a UI, RBAC, and a working semi-automated CI/CD pipeline.
* **Epoch II: The Library of MISO (NEXT)**: Implement the Engram Memory Architecture.
* **Epochs III-V**: Division of Labor, The Constitution, and The Cambrian Explosion.

## 2. Implementation Status & Critical Knowledge
* **Current State**: We have a stable, multi-service application deployed. The CI/CD pipeline automatically builds images from a GitHub push, but the final deployment to the VM is a manual step run by the user.
* **Current Goal**: We are about to begin Sprint 10, the first sprint of Epoch II, to implement the `memory-service`.
* **Critical Environmental Constraints Discovered**:
    * The VM's OS (COS) has a read-only filesystem and a `noexec` flag on the home directory. Workaround: run scripts with `bash` and use specific writable directories.
    * The VM's Docker daemon has unreliable internal DNS. Workaround: use direct IP address lookups via the Docker socket.
    * The user's account (`kyle@stemcultivation.com`) is subject to Organizational Policies that can block services (e.g., Cloud Source Repositories) and actions (e.g., creating service account keys).
    * The user's local network/ISP is blocking connections, requiring workarounds like using standard ports.

## 3. Current Operational Platform
* **Project ID**: `miso-final-1234`
* **VM Name**: `miso-vm`
* **Source Repository**: `https://github.com/made-it-so/miso-factory-repo`

## 4. Established User Protocols
* **Full Remediation Protocol**: Upon any user-reported error, the AI must: 1. Diagnose the root cause. 2. Provide the specific corrective command(s). 3. Restate ALL subsequent steps required to complete the original goal.
* **`nano` Editor Workflow**: All multi-line scripts intended for the user must be delivered via the `nano` editor protocol.
