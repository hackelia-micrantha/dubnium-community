# Event Contract v1alpha synthetic examples

Status: experimental
Content: informative
Canonical source: this file
Generated: no

These examples are synthetic and contain no production topology, repositories,
credentials, prompts, memory contents, or operational evidence.

The machine-readable conformance cases live in
`conformance/fixtures/events-v1/fixtures.json`.

## JIT runner start

```json
{
  "specversion": "1.0",
  "id": "evt-01J8SYNTHRUNNER0001",
  "source": "urn:dubnium:github-runner-controller",
  "type": "org.micrantha.dubnium.github.runner.started.v1",
  "time": "2026-10-05T12:00:00Z",
  "subject": "runner/synthetic-worker-01",
  "datacontenttype": "application/json",
  "data": {
    "severity": "info",
    "repository_key": "synthetic-repository",
    "worker_id": "synthetic-worker-01"
  }
}
```

## Supervisor run with trace context

```json
{
  "specversion": "1.0",
  "id": "evt-01J8SYNTHSUPERVISOR1",
  "source": "urn:dubnium:supervisor-gateway",
  "type": "org.micrantha.dubnium.supervisor.run.started.v1",
  "time": "2026-10-05T12:00:01Z",
  "subject": "run/synthetic-run-01",
  "datacontenttype": "application/json",
  "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
  "data": {
    "severity": "info",
    "run_id": "synthetic-run-01"
  }
}
```

## Other initial event families

The same profile applies to synthetic examples such as:

- `org.micrantha.dubnium.llm.inference.completed.v1`;
- `org.micrantha.dubnium.memory.retrieval.completed.v1`;
- `org.micrantha.dubnium.capability.request.denied.v1`;
- `org.micrantha.dubnium.scheduler.job.failed.v1`.

Domain-specific schemas may later narrow their `data` fields without changing
the common CloudEvents envelope.
