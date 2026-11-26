# Research foundations

Dubnium investigates reproducible engineering, reliable automation, resource management and safe AI-assisted work. This curated reading list is ranked by editorial relevance to those broad objectives: foundational systems research first, then reliability and execution, then AI engineering interfaces and evaluation. The order is not a measured impact score or implementation priority.

| Rank | Publication | Authors, venue and year | Research theme |
| --- | --- | --- | --- |
| 1 | [The Vision of Autonomic Computing](https://doi.org/10.1109/MC.2003.1160055) | Kephart and Chess; Computer, 2003 | Self-management and feedback |
| 2 | [NixOS: A Purely Functional Linux Distribution](https://doi.org/10.1145/1411204.1411255) | Dolstra and Löh; ICFP, 2008 | Reproducible environments |
| 3 | [Build Systems à la Carte: Theory and Practice](https://doi.org/10.1017/S0956796820000088) | Mokhov, Mitchell and Peyton Jones; JFP, 2020 | Dependencies and incremental builds |
| 4 | [Predictive and Adaptive Failure Mitigation to Avert Production Cloud VM Interruptions](https://www.usenix.org/conference/osdi20/presentation/levy) | Levy et al.; OSDI, 2020 | Reliability and recovery |
| 5 | [Gandalf: An Intelligent, End-to-End Analytics Service for Safe Deployment in Large-Scale Cloud Infrastructure](https://www.usenix.org/conference/nsdi20/presentation/li) | Li et al.; NSDI, 2020 | Deployment safety |
| 6 | [Nix: A Safe and Policy-Free System for Software Deployment](https://www.usenix.org/legacy/publications/library/proceedings/lisa04/tech/dolstra.html) | Dolstra, de Jonge and Visser; LISA, 2004 | Functional deployment |
| 7 | [How Amazon Web Services Uses Formal Methods](https://www.amazon.science/publications/how-amazon-web-services-uses-formal-methods) | Newcombe et al.; Communications of the ACM, 2015 | Correctness and assurance |
| 8 | [Dapper, a Large-Scale Distributed Systems Tracing Infrastructure](https://research.google/pubs/dapper-a-large-scale-distributed-systems-tracing-infrastructure/) | Sigelman et al.; Google technical report, 2010 | Distributed observability |
| 9 | [Fault-tolerant and Transactional Stateful Serverless Workflows](https://www.usenix.org/conference/osdi20/presentation/zhang-haoran) | Zhang et al.; OSDI, 2020 | Durable execution |
| 10 | [Dominant Resource Fairness: Fair Allocation of Multiple Resource Types](https://www.usenix.org/conference/nsdi11/dominant-resource-fairness-fair-allocation-multiple-resource-types) | Ghodsi et al.; NSDI, 2011 | Resource allocation |
| 11 | [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793v1) | Yang et al.; arXiv, 2024 | Engineering interfaces |
| 12 | [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html) | Debenedetti et al.; NeurIPS, 2024 | Defensive evaluation |

These publications identify research questions, not an inventory of adopted mechanisms. The list does not establish performance, safety, compatibility or production readiness. Future additions will follow literature review and disclosure review. Negative or inconclusive evaluation results are valuable.

See [Status and Direction](status.md) for the distinction between public evidence and future directions.
