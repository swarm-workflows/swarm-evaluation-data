# SwarmPlus Evaluation Data

This repository contains experimental evaluation data and analysis scripts for the SwarmPlus distributed job scheduling system. The data supports research publications and provides reproducible results for performance, scalability, and resilience studies.

## Directory Structure

```
swarmplus-evaluation-data/
├── ccgrid-26/                          # CCGrid 2026 paper evaluation data
│   ├── single-site/                    # Single-site experiments
│   │   ├── run-mesh-10-100/           # Format: run-<topology>-<agents>-<jobs>
│   │   ├── run-ring-30-500/
│   │   └── ...
│   ├── multi-site/                     # Multi-site distributed experiments
│   │   ├── run-hierarchical-110-1000/
│   │   ├── run-mesh-30-500/
│   │   └── ...
│   ├── resilience/                     # Failure recovery experiments
│   │   ├── catastrophic-failure/
│   │   ├── dynamic-bucket-01/         # Dynamic agent addition scenarios
│   │   ├── dynamic-jobs-01/
│   │   ├── dynamic-time-01/
│   │   ├── fail-site/                 # Site failure scenarios
│   │   └── figures/
│   └── compare_failure_scenarios.py   # Analysis script
├── plot_multi_run_results.py          # Multi-run comparison plots
├── plot_paper_evaluation.py           # Paper figure generation
├── compare_ccgrid_vs_v2.py            # Version comparison analysis
├── plot_ccgrid_comparison.py          # CCGrid data visualization
└── ccgrid-26.tgz                      # Compressed archive of all data

```

## Experiment Categories

### 1. Single-Site Experiments

Tests conducted on a single computational site with varying:
- **Topologies**: Ring, Mesh, Hierarchical
- **Scales**: 10-990 agents, 100-3000 jobs
- **Purpose**: Baseline performance, consensus efficiency, topology comparison

Example configurations:
- `run-mesh-10-100`: 10 agents in mesh topology, 100 jobs
- `run-hierarchical-250-1000`: 250 agents in hierarchical topology, 1000 jobs

### 2. Multi-Site Experiments

Distributed experiments across multiple geographical sites:
- **Network latency**: Realistic inter-site delays
- **Cross-site consensus**: Wide-area coordination
- **Purpose**: Geographic distribution, WAN performance

### 3. Resilience Experiments

Failure handling and recovery scenarios:

#### Dynamic Agent Addition
- `dynamic-time-01`: Time-based agent scaling
- `dynamic-bucket-01`: Load-based agent addition
- `dynamic-jobs-01`: Job-completion-triggered scaling

#### Failure Scenarios
- `fail-site`: Complete site failure recovery
- `catastrophic-failure`: Multiple simultaneous agent failures

## Data Format

Each experiment directory (`run-*`) contains:

```
run-<topology>-<agents>-<jobs>/
├── all_jobs.csv              # Consolidated job execution data (V2 format)
├── agent-<id>.csv            # Per-agent job data (legacy format)
├── agent-<id>.log            # Agent execution logs
├── metrics.json              # Aggregated performance metrics
├── consensus_votes.json      # Consensus round details (if saved)
└── config_swarm_multi.yml    # Configuration used for this run
```

### all_jobs.csv Schema

| Column | Description |
|--------|-------------|
| `job_id` | Unique job identifier |
| `agent_id` | Agent that executed the job |
| `started_at` | Job start timestamp |
| `finished_at` | Job completion timestamp |
| `latency` | End-to-end execution time (seconds) |
| `status` | `completed`, `failed`, or `timeout` |

### metrics.json Structure

```json
{
  "total_jobs": 500,
  "completed_jobs": 495,
  "failed_jobs": 5,
  "avg_latency": 12.34,
  "p50_latency": 10.5,
  "p95_latency": 25.8,
  "p99_latency": 45.2,
  "consensus_rounds": 150,
  "agent_failures": 2,
  "job_reassignments": 12
}
```

## Analysis Scripts

### plot_multi_run_results.py

Comprehensive multi-run analysis and visualization:

```bash
./plot_multi_run_results.py --base-dir ccgrid-26/single-site --output-dir ccgrid-26/single-site/plots

# Generates:
# - Latency CDF comparisons across topologies
# - Throughput vs scale plots
# - Job completion timelines
# - Statistical significance tests
```

**Key Features:**
- Handles missing/zero started_at timestamps
- Compares topologies (ring, mesh, hierarchical)
- Statistical analysis with confidence intervals
- Aggregate metrics across multiple runs

### plot_paper_evaluation.py

Publication-quality figure generation:

```bash
./plot_paper_evaluation.py

# Creates paper figures with proper formatting:
# - Scalability plots
# - Performance comparisons
# - Topology evaluation charts
```

### compare_ccgrid_vs_v2.py

Compare legacy CCGrid format with V2 consolidated format:

```bash
./compare_ccgrid_vs_v2.py --ccgrid-dir ccgrid-26/single-site/run-mesh-10-100 --v2-dir ../SwarmAgents/runs/v2-test

# Validates data consistency between formats
# Useful for migration verification
```

### plot_ccgrid_comparison.py

CCGrid-specific visualization and analysis:

```bash
./plot_ccgrid_comparison.py --input-dir ccgrid-26/single-site

# CCGrid paper-specific plots
# Format matching publication requirements
```

### ccgrid-26/compare_failure_scenarios.py

Resilience and failure recovery analysis:

```bash
cd ccgrid-26
./compare_failure_scenarios.py

# Analyzes failure scenarios:
# - Agent dropout handling
# - Job reassignment efficiency
# - Recovery time metrics
# - Availability during failures
```

## Usage Examples

### Analyzing a Single Run

```bash
# Navigate to experiment directory
cd ccgrid-26/single-site/run-mesh-30-500

# Inspect metrics
cat metrics.json | python -m json.tool

# View job completion data
head -20 all_jobs.csv

# Check for failures
grep -i "failed\|error" agent-*.log
```

### Comparing Multiple Configurations

```python
from plot_multi_run_results import MultiRunAnalyzer

analyzer = MultiRunAnalyzer(
    base_dir="ccgrid-26/single-site",
    output_dir="ccgrid-26/single-site/plots"
)
analyzer.load_all_runs()
analyzer.plot_topology_comparison()
analyzer.plot_scalability()
analyzer.generate_summary_report()
```

### Reproducing Paper Figures

```bash
# Generate all paper figures
./plot_paper_evaluation.py

# Output: Publication-ready PDFs in ccgrid-26/single-site/plots/
```

## Key Metrics Explained

- **Latency**: Time from job submission to completion
- **Throughput**: Jobs completed per unit time
- **Consensus Rounds**: Number of PBFT-like agreement cycles
- **Agent Failures**: Detected agent dropouts during execution
- **Job Reassignments**: Jobs rescheduled due to agent failures
- **Availability**: Percentage of time system accepts new jobs

## Experiment Naming Convention

Format: `run-<topology>-<agents>-<jobs>`

Examples:
- `run-ring-30-500`: Ring topology, 30 agents, 500 jobs
- `run-mesh-10-100`: Mesh topology, 10 agents, 100 jobs
- `run-hierarchical-110-1000`: Hierarchical topology, 110 agents, 1000 jobs

## Data Collection Methodology

All experiments conducted using:
- **SwarmAgents**: Production PBFT-based scheduling system
- **Test Runner**: `SwarmAgents/run_test_v2.py`
- **Redis**: Shared job queue (localhost or distributed)
- **Job Generator**: Synthetic workloads with realistic resource requirements

Configuration parameters stored in each run's `config_swarm_multi.yml`.

## Reproducing Experiments

To reproduce any experiment:

```bash
cd ../SwarmAgents

# Extract configuration from archived run
TOPOLOGY=$(echo run-mesh-30-500 | cut -d'-' -f2)
AGENTS=$(echo run-mesh-30-500 | cut -d'-' -f3)
JOBS=$(echo run-mesh-30-500 | cut -d'-' -f4)

# Run with same parameters
python run_test_v2.py \
  --mode local \
  --agent-type resource \
  --agents $AGENTS \
  --topology $TOPOLOGY \
  --jobs $JOBS \
  --db-host localhost \
  --run-dir runs/reproduce-$(date +%s)
```

## Dependencies

Analysis scripts require:

```bash
pip install pandas numpy matplotlib seaborn scipy
```

For data collection (from parent repo):

```bash
cd ../SwarmAgents
pip install -r requirements.txt
```

## Related Documentation

- `../SwarmAgents/README.md`: System architecture and implementation
- `../CLAUDE.md`: Developer guide and testing procedures
- `../SwarmAgents/DYNAMIC_AGENTS_USAGE.md`: Dynamic scaling documentation
- `../SwarmAgents/AGENT_FAILURE_HANDLING.md`: Resilience mechanisms

## Publication References

This data supports:
- **CCGrid 2026**: "SwarmPlus: Distributed Multi-Agent Job Scheduling with PBFT Consensus"
- Performance, scalability, and resilience evaluation

## Archive Management

Large datasets compressed as `.tgz` files:
- `ccgrid-26.tgz`: All CCGrid 2026 evaluation data

To extract:

```bash
tar -xzf ccgrid-26.tgz
```

## Contact

For questions about the data or analysis:
- Check experiment logs in individual `run-*/` directories
- Review configuration files: `config_swarm_multi.yml`
- See parent repository documentation: `../SwarmAgents/`
