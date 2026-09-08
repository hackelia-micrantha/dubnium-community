# Observability and Evidence

Dubnium treats observability as part of the workstation contract: an environment should be able to explain what it expected, what it observed, what failed, and what evidence supports that conclusion.

## Host observability

Local host observability should answer questions such as:

- what should be active;
- what is actually active;
- what failed, restarted, or became degraded;
- whether resource or storage pressure is affecting work;
- whether the endpoint's security and exposure posture matches expectations;
- what changed recently enough to investigate.

The specific implementation may use operating-system service state, structured logs, runtime metrics, and local diagnostic tools. The public contract is the ability to inspect locally rather than dependence on a central dashboard.

## Organizational observability

A managed environment may publish a bounded projection of endpoint posture to an organization. Useful categories can include configuration identity, update state, critical service health, security posture, resource pressure, and record freshness.

This is not a requirement to stream every workstation log. Central collection should be purpose-limited, freshness-qualified, and additive to local diagnosis.

## Personal observability

The same evidence model can support private daily reports, journals, and retrospectives for the operator.

Personal observability is a separate plane from organizational telemetry. A useful default avoids covert collection of keystrokes, clipboard contents, screenshots, complete shell history, arbitrary browser activity, message bodies, or arbitrary file contents.

Even metadata can be sensitive. Repository names, work times, project activity, and failure patterns need explicit purpose, visibility, retention, and sharing rules.

## Evidence before narrative

A reporting pipeline should prefer:

```text
authoritative domain state
+ bounded runtime evidence
-> deterministic structured summary
-> optional narrative synthesis
-> explicit publication or sharing
```

An AI-generated summary should not hide missing evidence or invent success. The structured report should remain useful without a model.

## Logs are evidence, not universal state

Logs and journals are valuable for runtime events and diagnosis. Workflows, approvals, deployments, and other stateful domains should retain their own durable records rather than require later reconstruction from log text.
