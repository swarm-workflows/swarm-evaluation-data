# Conference paper (gossip consensus + contextual bandit delegation): collected run data

Collector output for the frozen campaign (SwarmAgents tag `isc27-freeze`, 0bceb349) and for the review
ablations (tag `isc27-freeze-15`, d3755e2b). These are the per-run, per-job and per-decision tables that
every number in the paper is computed from. The per-cell summary, the figures and the scripts live in the
SwarmAgents repository under `docs/results/isc27-frozen-0bceb349/`.

| File | Contents | Unpacked |
|---|---|---|
| `collect-frozen.tgz` | `collect-frozen/<source>/{runs_wide,runs_tidy,config_agg,decisions,job_rtt,events_summary}.csv` for the 521 frozen runs, the RTT-bin tables (`e3a-*`), the real-workflow comparison (`t6`) and the collection logs | about 0.9 GB |
| `collect-review.tgz` | The same collector output for the 63 review-ablation runs: `partA` (Snow instance limit 64/256), `partB` (PBFT Mesh-180, larger send pool), `partC/<cell>` (arrival-rate sweep, limit 16), `sweep64/<cell>` and `sweep64p7` (sweep at limit 64), `control` (same-session control at 16) | about 0.2 GB |
| `workloads.tgz` | The job sets the runs replayed: `replay-golden` (2,222 records, the source of every simulated set), the per-fleet sets `jobs_600` to `jobs_8000`, the job-mix-shift set, and the job records of the two mixed real-workflow sets. Its own `README.md` gives how each was built | about 115 MB |

Produced on the deployment's database node by `evaluation/paper/collect_frozen.sh` and by
`evaluation/collect.py --root <campaign out-dir> --out <dir>`.

To rebuild the paper's tables and figures:

```bash
cd SwarmAgents
tar xzf ../swarmplus-evaluation-data/isc27-gossip-bandit/collect-frozen.tgz -C runs
.venv/bin/python evaluation/paper/build.py --manifest evaluation/paper/manifest_frozen.yml
.venv/bin/python evaluation/paper/fig_ablation.py   docs/results/isc27-frozen-0bceb349 /tmp/out
.venv/bin/python evaluation/paper/fig_f3_compact.py docs/results/isc27-frozen-0bceb349 /tmp/out
```

Not included: the code, inputs and container images of the three real workflows, and the raw run trees (agent logs, per-level job CSVs, `run_meta.json`, `rtt_matrix.json` per
run). They are on the database node under `/root/SwarmAgents/runs/frozen-0bceb349/` and
`runs/campaign-review-*-d3755e2b/`.
