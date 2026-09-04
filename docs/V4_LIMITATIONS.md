# v4.0.0 Limitations and Non-Claims

RedPulse AI v4.0.0 is an engineering and research portfolio platform. The repository does not establish:

- a live production deployment in an industrial plant;
- functional-safety or machinery-safety certification;
- guaranteed failure prediction accuracy for arbitrary machines;
- exactly-once semantics for arbitrary external side effects;
- autonomous authorization to perform physical maintenance;
- a production identity provider or corporate tenant directory;
- a connected enterprise Databricks, n8n, Power Automate, Teams, Jira, or Hugging Face deployment unless separately configured;
- infinite-scale Kafka/Spark/Kubernetes capacity.

The in-repository streaming implementation is a deterministic local contract used to exercise schema, replay, offset, idempotency and lag semantics. Production Kafka adapters remain deployment integrations. Similar boundaries apply to MLOps, Spark/Airflow and enterprise workflow adapters.
