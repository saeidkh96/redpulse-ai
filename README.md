<div align="center">

<img src="docs/images/redpulse-logo.png" alt="RedPulse AI" width="520"/>

# RedPulse AI

### Behavioral Intelligence & Predictive Maintenance Platform

**Behavior. Insight. Uptime.**

</div>

[![Version](https://img.shields.io/badge/version-v2.0.0-e11d2e)](https://github.com/saeidkh96/redpulse-ai/releases/tag/v2.0.0)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![TimescaleDB](https://img.shields.io/badge/TimescaleDB-Telemetry-FDB515)](https://www.timescale.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

---

## What is RedPulse AI?

**RedPulse AI** is a production-oriented behavioral intelligence and predictive-maintenance platform designed to learn how individual industrial machines normally behave, detect when that behavior changes, estimate failure risk, recommend maintenance, verify intervention outcomes, and compare possible maintenance decisions.

Instead of treating every machine as identical, RedPulse builds a **machine-specific behavioral fingerprint — Machine DNA** — from multivariate telemetry. That baseline captures sensor statistics, trends, and relationships between signals so future behavior can be compared against what is normal for that specific machine.

RedPulse has evolved beyond threshold monitoring into an end-to-end predictive-maintenance intelligence pipeline:

- machine-specific behavioral baselines;
- multivariate behavioral deviation detection;
- slow-drift analysis;
- persistent behavioral memory;
- historical failure fingerprint storage;
- failure-trajectory matching;
- machine health scoring;
- predictive failure intelligence;
- explainable failure evidence and root-cause hints;
- maintenance decision intelligence;
- post-maintenance verification;
- maintenance intervention history;
- maintenance outcome learning;
- counterfactual maintenance analysis.

> **Current milestone — v2.0.0:** RedPulse now combines machine-, fleet-, and plant-level predictive-maintenance intelligence with streaming and large-scale analytics, production-oriented MLOps, Hugging Face model integration, Industrial Intelligence, enterprise automation, multi-tenant controls, and a production-platform layer for approvals, jobs, predictive-AI operations, data quality, governance, security, observability, persistence contracts, and readiness validation.

---

## Why Machine DNA?

Traditional monitoring often asks:

> "Did a sensor cross a fixed threshold?"

RedPulse is built to ask a richer question:

> **"Is this machine behaving differently from its own learned normal behavior?"**

Two machines of the same model may operate under different loads, environments, ages, maintenance histories, and sensor characteristics. A single global threshold can miss that context.

Machine DNA provides a per-machine baseline containing:

- sensor distributions and operating ranges;
- mean, median, standard deviation, minimum, and maximum;
- temporal trend/slope information;
- multivariate sensor correlations;
- baseline observation window and sample count;
- persistent, automatically versioned baseline history.

Machine DNA is the foundation for later reasoning: deviation, drift, failure matching, health scoring, prediction, maintenance verification, and counterfactual analysis all depend on understanding what is normal for the machine itself.

---

## Current Intelligence Architecture

```mermaid
flowchart TD
    SIM[CNC Machine Simulator] --> API[FastAPI API]

    API --> TS[(TimescaleDB)]
    API --> PG[(PostgreSQL)]
    API -. infrastructure .-> REDIS[(Redis)]

    TS --> FE[Feature Engine]
    FE --> STAT[Sensor Statistics]
    FE --> TREND[Trend / Slope]
    FE --> CORR[Correlation Engine]

    STAT --> DNA[Machine DNA]
    TREND --> DNA
    CORR --> DNA
    DNA --> BASE[(Versioned Machine Baselines)]

    TS --> DEV[Behavioral Deviation]
    BASE --> DEV
    DEV --> DRIFT[Slow Drift Detection]

    DEV --> MEM[Behavioral Memory]
    DRIFT --> MEM
    MEM --> EVENTS[(Behavior Events)]

    EVENTS --> FPLIB[Failure Fingerprint Library]
    FPLIB --> MATCH[Failure Trajectory Matching]

    MATCH --> HEALTH[Machine Health Scoring]
    DEV --> HEALTH
    DRIFT --> HEALTH

    HEALTH --> PRED[Predictive Failure Intelligence]
    PRED --> EXPLAIN[Explainable Failure Intelligence]

    EXPLAIN --> DECIDE[Maintenance Decision Intelligence]
    DECIDE --> INTERVENTION[Maintenance Intervention]

    INTERVENTION --> VERIFY[Post-Maintenance Verification]
    VERIFY --> HISTORY[(Maintenance History)]

    HISTORY --> OUTCOME[Maintenance Outcome Learning]
    OUTCOME --> CF[Counterfactual Maintenance Intelligence]
    HEALTH --> CF

    CF --> RECOMMEND[Evidence-Adjusted Intervention Recommendation]

    HISTORY --> CROSS[Cross-Machine Learning]
    CROSS --> FLEET[Fleet Intelligence]
    FLEET --> PLANT[Plant Intelligence]
    PLANT --> STREAM[Streaming Intelligence]
    STREAM --> DATA[Data Platform / Spark Analytics]
    DATA --> MLOPS[Production MLOps Platform]
    MLOPS --> HF[Hugging Face Model Platform]
    HF --> AILAYER[Industrial AI / Copilot Layer]
    AILAYER --> AUTO[Enterprise Automation Runtime]
    AUTO --> TENANT[Multi-Tenant Platform]
    TENANT --> PROD[Production Platform]
    PROD --> GOV[Governance / Security]
    PROD --> OBS[Observability / Readiness]
    PROD --> PAI[Production Predictive AI]
    PROD --> PDATA[Production Data Controls]
```

---

## Current Capabilities — v2.0.0

| Area | Capability | Status |
|---|---|:---:|
| Platform | FastAPI backend foundation | ✅ |
| Infrastructure | PostgreSQL / TimescaleDB | ✅ |
| Infrastructure | Redis service | ✅ |
| Data Model | Machine registry | ✅ |
| Telemetry | Single and batch measurement ingestion | ✅ |
| Telemetry | Machine / sensor / time-window queries | ✅ |
| Telemetry | TimescaleDB hypertable | ✅ |
| Simulation | Reproducible CNC telemetry generator | ✅ |
| Simulation | RPM, load, temperature, current, vibration | ✅ |
| Simulation | Normal, moderate, and severe degradation profiles | ✅ |
| Features | Statistical sensor features | ✅ |
| Features | Trend / slope extraction | ✅ |
| Features | Cross-sensor correlation fingerprint | ✅ |
| Machine DNA | Baseline generation and persistence | ✅ |
| Machine DNA | Automatic baseline versioning | ✅ |
| Behavioral Intelligence | Behavioral deviation scoring | ✅ |
| Behavioral Intelligence | Per-sensor deviation evidence | ✅ |
| Behavioral Intelligence | Correlation-shift detection | ✅ |
| Behavioral Intelligence | Severity classification | ✅ |
| Behavioral Intelligence | Multi-window slow-drift analysis | ✅ |
| Behavioral Intelligence | Trend, persistence, monotonicity, cumulative-change signals | ✅ |
| Memory | Persistent behavioral event history | ✅ |
| Memory | Deviation and drift event recording | ✅ |
| Failure Intelligence | Historical failure fingerprint library | ✅ |
| Failure Intelligence | Failure trajectory matching | ✅ |
| Health | Machine health scoring | ✅ |
| Prediction | Predictive failure intelligence | ✅ |
| Explainability | Evidence and root-cause hints | ✅ |
| Maintenance | Maintenance decision intelligence | ✅ |
| Maintenance | Post-maintenance verification | ✅ |
| Maintenance | Intervention history and lifecycle tracking | ✅ |
| Maintenance | Before / after snapshots | ✅ |
| Maintenance | Verification result persistence | ✅ |
| Learning | Maintenance outcome learning | ✅ |
| Learning | Historical success rate and confidence | ✅ |
| Counterfactual | No-maintenance trajectory estimation | ✅ |
| Counterfactual | Candidate intervention comparison | ✅ |
| Counterfactual | Avoided risk / health loss / drift estimation | ✅ |
| Counterfactual | Evidence-adjusted intervention ranking | ✅ |
| Counterfactual | Historical support and confidence | ✅ |
| Fleet Intelligence | Cross-machine learning | ✅ |
| Fleet Intelligence | Fleet health / risk / prioritization | ✅ |
| Fleet Intelligence | Machine similarity and peer grouping | ✅ |
| Fleet Intelligence | Failure hotspots | ✅ |
| Plant Intelligence | Site-level intelligence | ✅ |
| Plant Intelligence | Fleet early warning | ✅ |
| Plant Intelligence | Fleet risk forecasting | ✅ |
| Plant Intelligence | Plant maintenance planning | ✅ |
| Streaming | In-memory event bus foundation | ✅ |
| Streaming | Kafka event-bus adapter | ✅ |
| Streaming | Intelligence event publishing | ✅ |
| Streaming | Real-time window processing | ✅ |
| Data Platform | Data-platform orchestration | ✅ |
| Analytics | Spark analytics jobs | ✅ |
| MLOps | Experiment tracking | ✅ |
| MLOps | Model registry and version lifecycle | ✅ |
| MLOps | Feature-store foundation | ✅ |
| MLOps | Model/data monitoring | ✅ |
| MLOps | Automated retraining control | ✅ |
| MLOps | Champion / challenger evaluation | ✅ |
| MLOps | Model serving abstraction | ✅ |
| MLOps | MLflow adapter | ✅ |
| MLOps | Airflow retraining adapter / DAG | ✅ |
| Hugging Face | Hub adapter and model inspection | ✅ |
| Hugging Face | Model metadata / model-card synchronization | ✅ |
| Hugging Face | Local model cache | ✅ |
| Hugging Face | Embedding adapter | ✅ |
| Hugging Face | PEFT / LoRA training adapter | ✅ |
| Hugging Face | Inference adapter | ✅ |
| Hugging Face | Provider-independent model gateway | ✅ |
| Hugging Face | Unified model platform API | ✅ |
| Industrial AI | Knowledge ingestion foundation | ✅ |
| Industrial AI | Structured knowledge store | ✅ |
| Industrial AI | Evidence-grounded engineer copilot | ✅ |
| Industrial AI | Machine-context construction | ✅ |
| Agentic AI | Tool registry and agent runtime | ✅ |
| Agentic AI | Maintenance planner foundation | ✅ |
| Enterprise | RBAC foundation | ✅ |
| Enterprise | Resilience controls | ✅ |
| Enterprise | Observability hooks | ✅ |
| Integrations | Vendor-independent Integration Gateway | ✅ |
| Integrations | Adapter abstraction for enterprise automation | ✅ |
| API | Industrial Intelligence API surface | ✅ |
| Automation | Enterprise automation control plane | ✅ |
| Automation | n8n adapter foundation | ✅ |
| Automation | Microsoft Power Automate adapter foundation | ✅ |
| Automation | Generic webhook support | ✅ |
| Automation | Retry / reliability foundations | ✅ |
| Multi-Tenancy | Tenant registry and tenant users | ✅ |
| Multi-Tenancy | Tenant RBAC | ✅ |
| Multi-Tenancy | Tenant API-key foundation | ✅ |
| Multi-Tenancy | Tenant-scoped integrations | ✅ |
| Multi-Tenancy | Tenant audit trail | ✅ |
| Production Runtime | Automation job lifecycle | ✅ |
| Production Runtime | Approval workflow foundation | ✅ |
| Production Runtime | HTTP workflow executor | ✅ |
| Production Runtime | Dead-letter / retry foundations | ✅ |
| Production AI | Model serving router | ✅ |
| Production AI | Drift-triggered retraining policy | ✅ |
| Production AI | Champion / challenger evaluation | ✅ |
| Production AI | Feature contracts and prediction envelopes | ✅ |
| Production AI | Failure-risk model foundation | ✅ |
| Production AI | Remaining-useful-life model foundation | ✅ |
| Production Data | Telemetry repository contract | ✅ |
| Production Data | Dataset catalog | ✅ |
| Production Data | Data-quality validation | ✅ |
| Production Data | Lineage foundation | ✅ |
| Production Data | Replay-plan model | ✅ |
| Production Data | Spark job specification | ✅ |
| Production Data | Fleet work partitioning | ✅ |
| Production Platform | Production control plane | ✅ |
| Production Platform | Readiness reporting | ✅ |
| Production Platform | Governance / security / persistence / observability foundations | ✅ |
| API | Enterprise Automation API surface | ✅ |
| API | Production Platform API surface | ✅ |

---

## End-to-End Intelligence Flow

```text
Machine Telemetry
      ↓
Machine DNA
      ↓
Behavioral Deviation
      ↓
Slow Drift Detection
      ↓
Behavioral Memory
      ↓
Failure Fingerprint Library
      ↓
Failure Trajectory Matching
      ↓
Machine Health Scoring
      ↓
Failure Prediction
      ↓
Explainability / Root-Cause Hints
      ↓
Maintenance Recommendation
      ↓
Maintenance Intervention
      ↓
Post-Maintenance Verification
      ↓
Maintenance History
      ↓
Maintenance Outcome Learning
      ↓
Counterfactual Maintenance Intelligence
      ↓
Evidence-Adjusted Intervention Recommendation
```

---

## Counterfactual Maintenance Intelligence

`v0.5.0` adds a new reasoning layer on top of the maintenance history and outcome-learning pipeline.

RedPulse now evaluates:

> **What is the estimated trajectory if no maintenance is performed?**

and:

> **Which historically supported intervention is expected to produce the strongest outcome?**

The counterfactual engine compares the current machine condition with:

```text
Current Machine State
        │
        ├── No Maintenance
        │      ↓
        │   Estimated Degradation
        │
        ├── Candidate Intervention A
        │      ↓
        │   Expected Outcome
        │
        ├── Candidate Intervention B
        │      ↓
        │   Expected Outcome
        │
        └── Candidate Intervention N
               ↓
            Expected Outcome
                  ↓
        Evidence-Adjusted Ranking
```

Representative outputs include:

```text
predicted_health_score
predicted_risk_score
predicted_deviation_score
predicted_drift_score
predicted_failure_match_score

expected_recovery_score

avoided_risk
avoided_health_loss
avoided_drift

estimated_intervention_benefit
confidence
historical_support
evidence_scope
recommended_intervention
```

Counterfactual results are explicitly treated as **estimated projections rather than guaranteed future states**.

Machine-type-specific intervention history is preferred when available. If the platform must fall back to global maintenance history, recommendation confidence is reduced.

---

## Fleet, Plant & Streaming Intelligence — v1.0.0

RedPulse v1.0.0 expands the intelligence scope beyond an individual machine. Historical machine behavior and maintenance evidence can now contribute to cross-machine reasoning, fleet-level health analysis, failure-hotspot detection, and maintenance prioritization.

At plant level, the platform adds site summaries, fleet early-warning signals, fleet risk forecasting, and plant maintenance planning. This allows machine-level evidence to be aggregated into operational views without removing the machine-specific context established by Machine DNA.

The data platform adds an event-driven foundation for higher telemetry volumes. It includes an in-memory event bus for local/test operation, an optional Kafka adapter, intelligence-event publishing, real-time window processing, and Spark analytics jobs. The unified data-platform API exposes event publication, recent-event retrieval, and analytics execution.

Representative v1.0.0 endpoints include:

```text
GET/POST  /api/v1/machines/{machine_id}/cross-machine-learning
GET       /api/v1/fleet/peer-groups
GET       /api/v1/fleet/health
GET       /api/v1/fleet/failure-hotspots
GET       /api/v1/fleet/maintenance-priorities
GET       /api/v1/plant/sites/summary
GET       /api/v1/plant/fleet-early-warning
GET       /api/v1/plant/fleet-risk-forecast
GET       /api/v1/plant/maintenance-plan
POST      /api/v1/data-platform/events/publish
GET       /api/v1/data-platform/events/recent
POST      /api/v1/data-platform/analytics/run
```

The streaming stack is intentionally optional: the core predictive-maintenance intelligence remains usable without Kafka or Spark.

---

## Production MLOps Platform — v1.2.0

RedPulse v1.2.0 adds a production-oriented MLOps control plane around the predictive-maintenance intelligence stack.

The platform includes experiment tracking, model registration and lifecycle management, feature-store foundations, model/data monitoring, automated retraining controls, champion/challenger evaluation, model serving abstractions, observability hooks, and adapters for MLflow and Airflow.

The MLOps layer is designed to keep model operations separate from the core machine-intelligence logic, so predictive-maintenance services can evolve without becoming tightly coupled to a single MLOps vendor.

Representative areas include:

```text
Experiments
Model Registry
Model Lifecycle
Feature Store
Monitoring
Retraining
Champion / Challenger
Serving
MLflow Adapter
Airflow Adapter
Observability
MLOps Control Plane
```

---

## Hugging Face Integration Platform — v1.3.0

RedPulse v1.3.0 introduces a dedicated Hugging Face integration layer for model discovery and future industrial-AI workloads.

The integration provides:

- Hugging Face Hub model inspection;
- model metadata and model-card synchronization;
- local model caching;
- embedding-model abstraction;
- inference-model abstraction;
- PEFT / LoRA training configuration;
- a provider-independent model gateway;
- a unified Hugging Face model platform and API.

Representative endpoints:

```text
POST  /api/v1/huggingface/models/inspect
POST  /api/v1/huggingface/models/pull
POST  /api/v1/huggingface/generate
```

The predictive-maintenance core remains independent of Hugging Face. The integration is an optional AI/model layer that can support later RAG, industrial copilots, local models, fine-tuning, and domain-specific inference.

---

## Industrial Intelligence Platform — v1.4.0

RedPulse v1.4.0 adds the first Industrial Intelligence layer on top of the predictive-maintenance, data-platform, MLOps, and model-platform foundations.

The release introduces:

- knowledge ingestion for industrial and maintenance context;
- structured knowledge models and an internal knowledge store;
- evidence-grounded engineer-copilot services;
- machine-context construction for contextual reasoning;
- an agentic runtime with tool registration and execution;
- a maintenance-planning agent foundation;
- enterprise RBAC, resilience, and observability foundations;
- a vendor-independent Integration Gateway and adapter abstraction.

Representative endpoints include:

```text
POST  /api/v1/industrial-ai/knowledge/ingest
POST  /api/v1/industrial-ai/copilot/ask
POST  /api/v1/industrial-ai/agents/runs
```

The Industrial Intelligence layer is intentionally separated from the predictive-maintenance core. LLM- or agent-based reasoning can therefore consume machine evidence without replacing the deterministic behavioral, failure, health, and maintenance intelligence pipeline.

The integration gateway establishes a common boundary for future automation systems such as n8n, Microsoft Power Automate, generic webhooks, and enterprise workflow tools. Individual external adapters can evolve independently from RedPulse core intelligence.

---

## Enterprise Automation & Multi-Tenant Platform — v1.6.0

RedPulse v1.6.0 extends the Integration Gateway into an executable enterprise-automation foundation and introduces tenant-aware platform controls.

The release includes:

- enterprise automation control-plane primitives;
- n8n and Microsoft Power Automate adapter foundations;
- generic webhook dispatch;
- retry and reliability primitives;
- tenant and tenant-user management;
- tenant RBAC;
- tenant API-key foundations;
- tenant-scoped integration registration;
- tenant audit records;
- Enterprise Automation service and API endpoints.

Representative endpoints:

```text
POST  /api/v1/enterprise-automation/tenants
POST  /api/v1/enterprise-automation/tenants/{tenant_id}/users
POST  /api/v1/enterprise-automation/integrations
GET   /api/v1/enterprise-automation/tenants/{tenant_id}/integrations
POST  /api/v1/enterprise-automation/dispatch
GET   /api/v1/enterprise-automation/tenants/{tenant_id}/audit
```

The adapters establish integration contracts and runtime foundations. They do **not** imply that a live external n8n, Microsoft 365, Teams, Outlook, Power Automate, Jira, CMMS, or ERP environment is currently connected.

---

## Production Industrial Intelligence Platform — v2.0.0

RedPulse v2.0.0 adds a production-oriented platform layer on top of the predictive-maintenance, MLOps, Industrial AI, automation, and multi-tenant foundations.

### Production Automation Runtime

The runtime adds:

- automation job lifecycle management;
- approval requests and approval decisions;
- HTTP workflow execution;
- retry handling;
- dead-letter foundations;
- tenant-aware execution context.

### Production Predictive AI

The production AI layer adds:

- model registration and champion routing;
- drift-signal evaluation;
- retraining policy decisions;
- champion/challenger comparison;
- feature-contract validation;
- prediction envelopes with evidence;
- failure-risk model foundations;
- remaining-useful-life model foundations.

### Production Data Controls

The production data layer adds:

- telemetry repository contracts;
- dataset registration and cataloging;
- data-quality validation;
- lineage records;
- replay-plan contracts;
- Spark job specifications;
- fleet work partitioning.

### Production Control Plane

The control plane consolidates production-readiness checks and platform-level foundations for governance, security, persistence, and observability.

Representative endpoints:

```text
GET   /api/v1/production-platform/readiness
POST  /api/v1/production-platform/approvals
POST  /api/v1/production-platform/approvals/{approval_id}/decision
POST  /api/v1/production-platform/jobs
POST  /api/v1/production-platform/ml/drift/evaluate
POST  /api/v1/production-platform/data/quality
POST  /api/v1/production-platform/fleet/partitions
```

> **Scope note:** v2.0.0 is a **production-oriented engineering milestone**. RedPulse remains an experimental engineering/research project and is not presented as a production safety system or as a platform already deployed in a real industrial plant.

---

## Maintenance Outcome Learning

Maintenance interventions are stored as persistent entities instead of temporary events.

A maintenance record can include:

```text
Machine
Failure Prediction Context
Maintenance Recommendation
Intervention Type
Lifecycle Status
Technician Notes
Before Snapshot
After Snapshot
Verification Result
Outcome Classification
Outcome Evidence
Start / Completion Time
```

Completed maintenance history is aggregated by intervention type.

Example:

```text
Bearing Replacement
      ↓
Average Recovery Score
Average Risk Reduction
Average Drift Reduction
Average Health Improvement
Success Rate
Historical Support
Confidence
      ↓
Learned Intervention Profile
```

This learned evidence becomes the input for counterfactual intervention comparison.

---

## Post-Maintenance Verification

RedPulse does not stop after recommending maintenance.

After an intervention, the platform can compare the machine's current behavior against the pre-maintenance snapshot and determine whether the intervention produced measurable recovery.

Verification considers signals such as:

```text
Health Improvement
Risk Reduction
Deviation Reduction
Drift Reduction
Failure-Match Reduction
```

The result is persisted in the maintenance history so later versions can learn which actions work under which machine conditions.

---

## Failure Intelligence

RedPulse maintains reusable historical failure knowledge.

### Failure Fingerprints

Historical degradation patterns can be stored as structured failure fingerprints containing behavioral and trajectory evidence.

### Failure Trajectory Matching

Current machine behavior can be compared against known historical failure trajectories to estimate whether the machine is evolving toward a previously observed failure pattern.

### Predictive Failure Intelligence

Trajectory evidence, machine health, deviation, drift, and historical failure similarity are combined into predictive failure signals.

### Explainability

Predictions are accompanied by evidence so maintenance decisions are not based on an opaque score alone.

---

## Machine DNA Example

A Machine DNA baseline is generated from synchronized telemetry and persisted for later comparison.

```json
{
  "baseline_version": "1",
  "sample_count": 1010,
  "sensor_features": {
    "vibration": {
      "mean": 2.1508,
      "std": 0.0832,
      "median": 2.149,
      "minimum": 1.875,
      "maximum": 2.382
    },
    "temperature": {
      "mean": 64.157,
      "std": 1.2313
    }
  },
  "correlations": {
    "current__load": 0.8667,
    "load__temperature": 0.8225,
    "rpm__vibration": 0.3433
  }
}
```

The baseline is not just a collection of independent thresholds. The correlations preserve part of the **relationship structure** between machine signals.

---

## CNC Telemetry Simulator

RedPulse includes a deterministic CNC simulator for development and validation.

It currently generates five signals:

```text
rpm
load
temperature
current
vibration
```

The signals are intentionally related. For example, load influences temperature and current, while RPM contributes to vibration.

Seeded generation makes experiments reproducible. The simulator also supports normal, moderate-degradation, and severe-degradation profiles so the intelligence pipeline can be validated against controlled deterioration scenarios.

---

## Behavioral Intelligence Example

With degradation telemetry, RedPulse can distinguish healthy operation from meaningful behavioral change.

A behavioral-memory event can preserve evidence such as:

```json
{
  "event_type": "drift",
  "severity": "anomalous",
  "score": 0.60999,
  "baseline_version": "3",
  "summary": "Slow behavioral drift detected with score 0.610 and state drifting",
  "evidence": {
    "state": "drifting",
    "top_signals": [
      {
        "signal": "vibration__mean_zscore",
        "score": 0.86,
        "state": "drifting"
      },
      {
        "signal": "overall_deviation",
        "score": 0.72,
        "state": "drifting"
      },
      {
        "signal": "current__mean_zscore",
        "score": 0.66,
        "state": "drifting"
      }
    ]
  }
}
```

Behavioral Memory converts individual analyses into structured historical evidence used by failure intelligence and maintenance reasoning.

---

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- asyncpg

### Data & Infrastructure

- PostgreSQL 17
- TimescaleDB
- Redis
- Apache Kafka
- Apache Spark
- Apache Airflow
- MLflow integration adapter
- Docker / Docker Compose

### Intelligence & Analytics

- statistical feature extraction
- multivariate behavioral fingerprints
- correlation analysis
- behavioral deviation scoring
- multi-window drift analysis
- failure trajectory matching
- health scoring
- evidence aggregation
- maintenance outcome learning
- counterfactual intervention comparison
- cross-machine learning and machine similarity
- fleet health, hotspots, and prioritization
- plant-level risk and maintenance planning
- real-time event/window processing
- large-scale Spark analytics
- experiment tracking and model lifecycle management
- model monitoring and automated retraining
- champion / challenger evaluation
- Hugging Face Hub / model caching
- embeddings and inference adapters
- PEFT / LoRA integration
- provider-independent model gateway
- evidence-grounded industrial knowledge retrieval
- engineer-copilot context construction
- agentic tool execution and maintenance planning
- enterprise RBAC / resilience / observability foundations
- vendor-independent integration gateway
- enterprise automation control plane
- n8n / Power Automate adapter foundations
- generic webhook workflows
- tenant-aware RBAC and API-key foundations
- production automation jobs and approvals
- model serving / drift / retraining policies
- champion / challenger evaluation
- failure-risk and RUL model foundations
- dataset catalog, data quality, lineage, replay, and partitioning
- governance, persistence, security, observability, and readiness foundations

### Quality

- pytest
- unit tests
- service-layer tests
- API / OpenAPI tests
- migration validation
- reproducible simulator tests

---

## Repository Structure

```text
redpulse-ai/
├── backend/
│   ├── alembic/
│   │   └── versions/
│   ├── app/
│   │   ├── api/v1/
│   │   ├── agents/
│   │   ├── automation/
│   │   ├── copilot/
│   │   ├── core/
│   │   ├── deviation/
│   │   ├── drift/
│   │   ├── enterprise/
│   │   ├── explainability/
│   │   ├── failure/
│   │   ├── features/
│   │   ├── fleet/
│   │   ├── health/
│   │   ├── integrations/
│   │   │   └── huggingface/
│   │   ├── integrations_gateway/
│   │   ├── knowledge/
│   │   ├── maintenance/
│   │   ├── memory/
│   │   ├── mlops/
│   │   ├── models/
│   │   ├── plant/
│   │   ├── prediction/
│   │   ├── production/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── streaming/
│   │   ├── tenancy/
│   │   └── data_platform/
│   └── tests/
├── analytics/
│   └── spark/
├── orchestration/
│   └── airflow/
│       └── dags/
├── simulator/
│   ├── profiles/
│   └── tests/
├── docs/
│   └── images/
├── docker-compose.yml
├── docker-compose.streaming.yml
├── backend/requirements-mlops.txt
├── backend/requirements-huggingface.txt
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/saeidkh96/redpulse-ai.git
cd redpulse-ai
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```powershell
pip install -r backend\requirements.txt
```

### 4. Start TimescaleDB and Redis

```powershell
docker compose up -d
docker ps
```

Development infrastructure:

```text
TimescaleDB / PostgreSQL : localhost:5433
Redis                    : localhost:6379
```

### 5. Apply database migrations

```powershell
cd backend
alembic upgrade head
```

### 6. Start the API

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

API root:

```text
http://127.0.0.1:8001/
```

Interactive API documentation:

```text
http://127.0.0.1:8001/docs
```

---

## Core API Flow

```text
Register Machine
      ↓
Ingest / Simulate Telemetry
      ↓
Build Machine DNA
      ↓
Analyze Behavioral Deviation
      ↓
Analyze Slow Drift
      ↓
Persist Behavioral Memory
      ↓
Build / Query Failure Intelligence
      ↓
Assess Machine Health
      ↓
Predict Failure Risk
      ↓
Explain Failure Evidence
      ↓
Generate Maintenance Recommendation
      ↓
Track Maintenance Intervention
      ↓
Verify Post-Maintenance Recovery
      ↓
Learn Maintenance Outcomes
      ↓
Analyze Counterfactual Maintenance Options
      ↓
Fleet / Plant Intelligence
      ↓
Streaming / Data Platform
      ↓
MLOps / Model Platform
      ↓
Industrial AI / Copilot
      ↓
Enterprise Automation / Multi-Tenancy
      ↓
Production Control Plane
```

Representative endpoint groups include:

```text
Machines
Telemetry
Machine DNA
Deviation
Drift
Behavioral Memory
Failure Fingerprints
Failure Matching
Machine Health
Failure Prediction
Failure Explanation
Maintenance Recommendation
Maintenance Verification
Maintenance Intervention History
Maintenance Outcome Learning
Counterfactual Maintenance
Fleet / Plant Intelligence
Data Platform
MLOps Platform
Hugging Face Platform
Industrial AI
Enterprise Automation
Production Platform
```

Representative maintenance endpoints include:

```text
POST   /api/v1/machines/{machine_id}/maintenance-interventions
GET    /api/v1/machines/{machine_id}/maintenance-interventions
GET    /api/v1/maintenance-interventions/{intervention_id}
POST   /api/v1/maintenance-interventions/{intervention_id}/complete

GET    /api/v1/maintenance-outcomes

POST   /api/v1/machines/{machine_id}/counterfactual-maintenance
```

Use the interactive FastAPI documentation at `/docs` for the complete current endpoint surface.

---

## Testing

Run the backend and simulator test suites from the repository root:

```powershell
python -m pytest backend\tests simulator\tests -q
```

At the `v2.0.0` milestone:

```text
210 passed
```

The suite covers:

- platform health and infrastructure;
- machine registry;
- telemetry ingestion and queries;
- simulator behavior and degradation profiles;
- feature extraction;
- Machine DNA generation and versioning;
- behavioral deviation scoring;
- slow-drift detection;
- Behavioral Memory;
- failure fingerprints and trajectory matching;
- machine health scoring;
- predictive failure intelligence;
- explainability;
- maintenance decision intelligence;
- post-maintenance verification;
- maintenance history and outcome learning;
- counterfactual maintenance intelligence;
- service-layer behavior;
- API / OpenAPI integration;
- Hugging Face model-platform integration;
- Industrial AI knowledge and copilot services;
- agentic runtime and maintenance-planning foundations;
- enterprise and integration-gateway foundations;
- enterprise automation and multi-tenant platform controls;
- n8n / Power Automate adapter foundations;
- production automation runtime and approvals;
- production predictive-AI operations;
- production data-quality, lineage, replay, and partitioning foundations;
- production control-plane and readiness APIs.

---

## Milestones

```text
v0.0.1  Platform Foundation
   ↓
v0.0.2  Data Infrastructure
   ↓
v0.0.3  Machine Registry
   ↓
v0.0.4  Telemetry Ingestion
   ↓
v0.0.5  CNC Simulator Baseline
   ↓
v0.1.0  Feature Engine + Machine DNA
   ↓
v0.1.1  Behavioral Deviation Engine
   ↓
v0.1.2  Slow Drift Detection
   ↓
v0.2.0  Behavioral Memory
   ↓
v0.2.1  Historical Failure Fingerprint Library
   ↓
v0.2.2  Failure Trajectory Matching
   ↓
v0.3.0  Machine Health Scoring
   ↓
v0.3.1  Predictive Failure Intelligence
   ↓
v0.3.2  Explainable Failure Intelligence
   ↓
v0.4.0  Maintenance Decision Intelligence
   ↓
v0.4.1  Post-Maintenance Verification
   ↓
v0.4.2  Maintenance History & Intervention Tracking
   ↓
v0.4.3  Maintenance Outcome Learning
   ↓
v0.5.0  Counterfactual Maintenance Intelligence
   ↓
v0.6.0  Cross-Machine Learning
   ↓
v0.7.0  Fleet Intelligence & Maintenance Prioritization
   ↓
v0.8.0  Plant Intelligence & Maintenance Planning
   ↓
v0.8.1  Streaming Foundation
   ↓
v0.8.2  Kafka Adapter
   ↓
v0.8.3  Intelligence Events
   ↓
v0.9.0  Real-Time Streaming
   ↓
v1.0.0  Streaming & Large-Scale Data Platform
   ↓
v1.2.0  Production MLOps Platform
   ↓
v1.3.0  Hugging Face Integration Platform
   ↓
v1.4.0  Industrial Intelligence Platform
   ↓
v1.6.0  Enterprise Automation & Multi-Tenant Platform
   ↓
v2.0.0  Production Industrial Intelligence Platform   ← current
```

---

## Roadmap

The project is intentionally evolving in layers. New infrastructure is added only when it has a concrete architectural use case.

### Completed in v1.0.0 — Fleet, Plant & Streaming Data Platform

The v1.0.0 milestone completes the planned cross-machine, fleet, plant, and initial distributed-data layers:

- cross-machine learning and shared historical evidence;
- machine similarity and peer grouping;
- fleet health, failure hotspots, and maintenance prioritization;
- plant/site intelligence, early warning, risk forecasting, and maintenance planning;
- event-streaming foundation with an optional Kafka adapter;
- real-time streaming windows and intelligence events;
- Spark analytics jobs for telemetry, features, and fleet analytics;
- data-platform orchestration and API endpoints.

### Completed in v1.2.0 — Production MLOps

- experiment tracking;
- model registry and model lifecycle management;
- feature-store foundation;
- data and model monitoring;
- automated retraining controls;
- champion / challenger evaluation;
- serving abstraction;
- MLflow integration adapter;
- Airflow retraining adapter and DAG;
- MLOps observability and control-plane services.

Important production metrics continue to include false-alert rate, precision / recall, early-warning lead time, and maintenance outcome quality.

### Completed in v1.3.0 — Hugging Face Integration Platform

The first model-platform layer is now implemented:

- Hugging Face Hub adapter;
- model metadata and model-card synchronization;
- local model cache;
- embeddings adapter;
- inference adapter;
- PEFT / LoRA adapter;
- provider-independent model gateway;
- unified Hugging Face model platform API.

### Completed in v1.4.0 — Industrial Intelligence Platform

The first Industrial AI / Engineer Copilot layer is now implemented:

- industrial knowledge ingestion and structured knowledge storage;
- evidence-grounded copilot foundation;
- machine-context construction;
- agentic runtime and tool registry;
- maintenance-planning agent foundation;
- enterprise RBAC, resilience, and observability foundations;
- vendor-independent Integration Gateway.

The predictive core remains independent of the LLM and agent layers. More advanced model serving, domain adaptation, prompt evaluation, and production-grade external automation remain future work.

### Completed in v1.6.0 — Enterprise Automation & Multi-Tenancy

The enterprise automation layer now includes:

- n8n adapter foundation;
- Microsoft Power Automate adapter foundation;
- generic webhooks;
- automation dispatch and reliability primitives;
- tenants and tenant users;
- tenant RBAC and API-key foundations;
- tenant-specific integrations;
- tenant audit records.

### Completed in v2.0.0 — Production Platform Foundation

The v2.0.0 milestone adds production-oriented operational building blocks:

- automation jobs, approvals, retries, and dead-letter foundations;
- production predictive-AI model routing and retraining policy;
- champion/challenger evaluation;
- failure-risk and remaining-useful-life model foundations;
- data-quality validation, dataset catalog, lineage, replay contracts, and fleet partitioning;
- governance, persistence, security, and observability foundations;
- production control-plane readiness reporting.

### Next Phase — Deployment & Production Hardening

Future work should deepen deployability and operational maturity rather than only adding more abstractions:

- persistent production storage for jobs, approvals, audit, and tenant state;
- stronger OAuth2 / OIDC identity and secrets management;
- live end-to-end validation against n8n / Power Automate / enterprise workflow targets;
- richer Prometheus / OpenTelemetry metrics, traces, alerts, and SLOs;
- load, failure, recovery, and chaos-style validation;
- Kubernetes / AKS and cloud deployment architecture;
- Terraform-based infrastructure as code;
- managed PostgreSQL, object storage, Key Vault, and Entra ID integration;
- scalable model serving such as vLLM where justified;
- GPU-backed or domain-adapted models only when they provide measurable value.

RedPulse should continue to preserve separation between its core machine intelligence and optional automation, LLM, MLOps, and cloud vendors.

---

## Vision

RedPulse AI is being developed around seven core ideas:

1. **Every machine has its own normal.**  
   Learn machine-specific behavior instead of relying only on universal thresholds.

2. **Relationships matter.**  
   A machine can change even when individual sensor values still look acceptable.

3. **Failures have trajectories.**  
   Historical degradation patterns can become reusable failure fingerprints.

4. **Predictions need evidence.**  
   Maintenance recommendations should show which signals, trends, and relationships changed.

5. **Maintenance should be verifiable.**  
   After intervention, the platform should determine whether the machine actually returned toward healthy behavior.

6. **Maintenance history should become reusable knowledge.**  
   Intervention outcomes should improve future maintenance decisions.

7. **Decisions should consider alternatives.**  
   The platform should estimate what may happen without intervention and compare historically supported maintenance options before recommending an action.

---

## Development Status

RedPulse AI is under active development and is currently an **experimental engineering/research project**, not a production safety system.

The current `v2.0.0` release extends the maintenance-learning loop with fleet/plant intelligence, streaming and large-scale analytics, production-oriented MLOps, Hugging Face model integration, Industrial Intelligence, enterprise automation, multi-tenancy, and a production-platform control plane:

```text
Machine Behavior
      ↓
Failure Intelligence
      ↓
Machine Health
      ↓
Failure Prediction
      ↓
Explainability
      ↓
Maintenance Decision
      ↓
Post-Maintenance Verification
      ↓
Maintenance History
      ↓
Outcome Learning
      ↓
Counterfactual Maintenance Intelligence
```

The next major stage is **deployment and deeper production hardening**: persistent runtime state, stronger identity and secrets, live external-integration validation, richer observability and SLOs, cloud/Kubernetes infrastructure, and scalable model serving where justified. The behavioral and predictive-maintenance core remains independent from optional LLM, automation, MLOps, and cloud vendors.

---

## Author

**Saeid Khalilian**

---

## License

See the repository license for usage terms.

<div align="center">

<strong>RedPulse AI</strong>

<em>Behavior. Insight. Uptime.</em>

</div>
