# Quantum-Hybrid Scale Campaign — Results Summary

Weak-scaling (~18 jobs/agent) on the 84-VM FABRIC deployment. Hierarchical
cells use **hybrid consensus** (PBFT within level-0 groups + Snow across the
coordinator tier, Snow `beta=6`); flat mesh-84 cells use **Snow**. Agents are
uniform (32c/128g/1000d) so every pegasus job is feasible on every leaf.
Completion is end-to-end (jobs completed at a leaf / all jobs submitted,
deduped by id across every level) — so undelegated jobs count against it.

Note on hier-120-quantum (~85%): split quantum sub-jobs need a backend-owning
leaf *within their delegation subtree*; with 25% backends, some coordinator
groups lack one, so those quantum sub-jobs can't place. The flat mesh-84-quantum
cell (all backends reachable) completes 100% — confirming this is a hierarchy-
locality effect, not a scheduler fault. All cells ran with 0 real failures.

| Cell | Topology / consensus | Jobs | Completion (3 runs) | Median latency |
|------|----------------------|------|---------------------|----------------|
| hier-60-classical | hierarchical / hybrid | 1093 | 100%/100%/100% | 8.9s |
| hier-120-classical | hierarchical / hybrid | 2188 | 100%/100%/100% | 8.3s |
| hier-250-classical | hierarchical / hybrid | 4472 | 100%/100%/100% | 127.4s |
| mesh-84-classical | mesh / snow | 547 | 100%/100%/100% | 12.0s |
| mesh-84-quantum | mesh / snow(split) | 686 | 100%/100%/100% | 12.6s |
| hier-120-quantum | hierarchical / hybrid(split) | 2744 | 86%/86%/85% | 9.8s |

## Per-run detail

### hier-60-classical
- run01: 1093/1093 (100%) complete, median latency 8.7s
- run02: 1093/1093 (100%) complete, median latency 8.4s
- run03: 1094/1094 (100%) complete, median latency 9.6s

### hier-120-classical
- run01: 2188/2188 (100%) complete, median latency 8.2s
- run02: 2188/2188 (100%) complete, median latency 8.4s
- run03: 2188/2188 (100%) complete, median latency 8.4s

### hier-250-classical
- run01: 4457/4457 (100%) complete, median latency 115.6s
- run02: 4478/4478 (100%) complete, median latency 144.3s
- run03: 4472/4472 (100%) complete, median latency 122.4s

### mesh-84-classical
- run01: 547/547 (100%) complete, median latency 12.6s
- run02: 547/547 (100%) complete, median latency 11.7s
- run03: 547/547 (100%) complete, median latency 11.8s

### mesh-84-quantum
- run01: 686/686 (100%) complete, median latency 12.8s
- run02: 686/686 (100%) complete, median latency 12.4s
- run03: 686/686 (100%) complete, median latency 12.6s

### hier-120-quantum
- run01: 2354/2744 (86%) complete, median latency 10.1s
- run02: 2359/2744 (86%) complete, median latency 9.8s
- run03: 2331/2744 (85%) complete, median latency 9.5s
