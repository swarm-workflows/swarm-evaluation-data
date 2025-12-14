# SwarmPlus Evaluation Data

This repository contains experimental evaluation data and analysis scripts for the SwarmPlus distributed job scheduling system. The data supports research publications and provides reproducible results for performance, scalability, and resilience studies.

## Directory Structure

```
swarmplus-evaluation-data/
├── runs/                               # All experimental runs
│   ├── ccgrid-25/                     # CCGrid 2025 baseline data
│   └── ccgrid-26/                     # CCGrid 2026 paper evaluation data
│       ├── single-site/               # Single-site experiments
│       │   ├── run-mesh-10-100/      # Format: run-<topology>-<agents>-<jobs>
│       │   ├── run-ring-30-500/
│       │   ├── run-hierarchical-110-1000/
│       │   └── ...
│       ├── multi-site/                # Multi-site distributed experiments
│       │   ├── run-hierarchical-110-1000/
│       │   ├── run-mesh-30-500/
│       │   └── ...
│       └── resilience/                # Failure recovery & dynamic scaling
│           ├── grpc/                  # gRPC-based failure detection
│           │   ├── single-agent/     # Single agent failure (3.3% loss)
│           │   │   ├── run01/
│           │   │   ├── run02/
│           │   │   ├── run03/
│           │   │   ├── run04/
│           │   │   └── run05/
│           │   ├── multiple-agents/  # Multiple agent failures (26.7% loss)
│           │   │   └── run01-05/
│           │   └── catastrophic/     # Catastrophic failure (50% loss)
│           │       └── run01-05/
│           ├── redis/                 # Redis-based failure detection
│           │   ├── single-agent/
│           │   ├── multiple-agents/
│           │   └── catastrophic/
│           ├── dynamic-bucket-01/     # Load-based dynamic agent addition
│           ├── dynamic-jobs-01/       # Job-completion-based scaling
│           ├── dynamic-time-01/       # Time-based agent scaling
│           ├── create_availability_figure_v2.py  # Multi-run aggregation
│           └── plot_dynamic_scaling.py
├── plot_multi_run_results.py          # Multi-run comparison plots
├── plot_paper_evaluation.py           # Paper figure generation
├── compare_ccgrid_vs_v2.py            # Version comparison analysis
├── plot_ccgrid_comparison.py          # CCGrid data visualization
└── runs.tgz                           # Compressed archive of all runs

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

Failure handling and recovery scenarios with multiple runs (n=5) for statistical robustness:

#### Failure Detection Comparison (gRPC vs Redis)

**gRPC-based Detection:**
- Near-instantaneous failure detection via bidirectional streaming channels
- 5 runs per scenario: `run01/` through `run05/`
- Scenarios:
  - `single-agent/`: 1/30 agents failed (3.3% capacity loss)
  - `multiple-agents/`: 8/30 agents failed (26.7% capacity loss)
  - `catastrophic/`: 15/30 agents failed (50% capacity loss)

**Redis-based Detection:**
- Timer-based heartbeat monitoring (45s threshold ±10% jitter)
- 5 runs per scenario matching gRPC scenarios
- Same failure scenarios for direct comparison

**Analysis:**
- `create_availability_figure_v2.py`: Aggregates multiple runs, computes mean±std statistics
- Generates comparison plots with error bars showing variance across runs

#### Dynamic Agent Addition
- `dynamic-time-01`: Time-based agent scaling (20→30 agents at t=30s)
- `dynamic-bucket-01`: Load-based agent addition (triggered when queue depth > 50)
- `dynamic-jobs-01`: Job-completion-triggered scaling (add agents after 100 jobs complete)

## Data Format

### Standard Run Directory

Each experiment directory (`run-*`) contains:

```
run-<topology>-<agents>-<jobs>/
├── all_jobs.csv              # Consolidated job execution data (V2 format)
├── agent-<id>.csv            # Per-agent job data (legacy format)
├── agent-<id>.log            # Agent execution logs
├── agent_<id>_load_trace.csv # Per-agent resource utilization over time
├── metrics.json              # Aggregated performance metrics
├── consensus_votes.json      # Consensus round details (if saved)
└── config_swarm_multi.yml    # Configuration used for this run
```

### Resilience Run Directory (Failure Scenarios)

Failure detection experiments include additional files:

```
resilience/grpc/single-agent/run01/
├── all_jobs.csv                           # Job execution data
├── agent-<id>.csv                         # Per-agent job data
├── agent-<id>.log                         # Agent execution logs
├── failed_agents.csv                      # Detected failed agents with timestamps
├── killed_agents.csv                      # Intentionally terminated agents
├── fault_tolerance_metrics_summary.csv    # Recovery metrics
├── reassigned_jobs.csv                    # Jobs reassigned after failures (if any)
└── config_swarm_multi.yml                 # Configuration
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

### failed_agents.csv Schema (Resilience Experiments)

| Column | Description |
|--------|-------------|
| `agent_id` | ID of failed agent |
| `first_detected_at` | Timestamp when failure was first detected |
| `first_detected_by` | Detection mechanism (`grpc` or `redis`) |
| `grpc_detections` | Number of peers detecting via gRPC |
| `redis_detections` | Number of peers detecting via Redis |
| `avg_detection_latency` | Average detection latency across peers (seconds) |
| `true_detection_latency` | Actual latency from kill to detection (if available) |

### fault_tolerance_metrics_summary.csv Schema

| Column | Description |
|--------|-------------|
| `total_jobs` | Total jobs in workload |
| `completed_jobs` | Successfully completed jobs |
| `failed_jobs` | Jobs that failed |
| `completion_rate_pct` | Job completion percentage |
| `system_availability_pct` | System availability during failures |
| `recovery_time_seconds` | Time to recover from failures |
| `jobs_reassigned` | Number of jobs reassigned to surviving agents |
| `agents_failed` | Number of agents that failed |

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

### runs/ccgrid-26/resilience/create_availability_figure_v2.py

**Multi-run failure detection comparison (gRPC vs Redis):**

```bash
cd runs/ccgrid-26/resilience

# Compare gRPC vs Redis across all failure scenarios
python create_availability_figure_v2.py \
    --grpc-scenarios grpc/single-agent/ grpc/multiple-agents/ grpc/catastrophic/ \
    --redis-scenarios redis/single-agent/ redis/multiple-agents/ redis/catastrophic/ \
    --output comparison_multirun.png \
    --killed-only \
    --pdf

# Generates:
# - Aggregated statistics across 5 runs per scenario (mean ± std)
# - Grouped bar charts with error bars
# - Detection latency comparison (~3900× speedup for gRPC)
# - Job completion rates under different failure scenarios
# - Statistical summary printed to console
```

**Key Features:**
- Automatically discovers all `run01/` through `run05/` directories
- Computes mean, std, min, max across runs
- Displays error bars showing variance
- Includes run count (n=5) in labels
- Outputs detailed statistical summary

**Output Statistics:**
```
Detection Latency (mean ± std):
  gRPC:
    Single Agent: 0.0 ± 0.0s (range: 0.0--0.0s, n=5)
    Multiple Agents: 0.0 ± 0.0s (range: 0.0--0.0s, n=5)
    Catastrophic: 0.0 ± 0.0s (range: 0.0--0.0s, n=5)
  Redis:
    Single Agent: 54.2 ± 0.5s (range: 53.3--54.9s, n=5)
    Multiple Agents: 54.0 ± 0.3s (range: 53.6--54.5s, n=5)
    Catastrophic: 54.3 ± 0.4s (range: 53.7--54.9s, n=5)

Availability (Jobs Completed %, mean ± std):
  Single Agent (1/30, 3.3% agent loss):
    gRPC:  99.8 ± 0.2% (range: 99.6--100.0%, n=5)
    Redis: 99.2 ± 0.7% (range: 98.2--100.0%, n=5)
  ...
```

## Usage Examples

### Analyzing a Single Run

```bash
# Navigate to experiment directory
cd runs/ccgrid-26/single-site/run-mesh-30-500

# Inspect metrics
cat metrics.json | python -m json.tool

# View job completion data
head -20 all_jobs.csv

# Check for failures
grep -i "failed\|error" agent-*.log
```

### Analyzing Resilience Multi-Run Data

```bash
# Navigate to a specific scenario
cd runs/ccgrid-26/resilience/grpc/single-agent

# Check all runs
ls -la run*/failed_agents.csv

# Compare metrics across runs
for run in run0{1..5}; do
  echo "=== $run ==="
  cat $run/fault_tolerance_metrics_summary.csv
done

# Generate aggregated comparison
cd ../..  # Back to resilience/
python create_availability_figure_v2.py \
    --grpc-scenarios grpc/*/ \
    --redis-scenarios redis/*/ \
    --output comparison.png \
    --pdf
```

### Comparing Multiple Configurations

```python
from plot_multi_run_results import MultiRunAnalyzer

analyzer = MultiRunAnalyzer(
    base_dir="runs/ccgrid-26/single-site",
    output_dir="runs/ccgrid-26/single-site/plots"
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

# Output: Publication-ready PDFs in runs/ccgrid-26/single-site/plots/
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

## Archive Management

Large datasets compressed as `.tgz` files:
- `runs.tgz`: All experimental runs (ccgrid-25 and ccgrid-26)

To extract:

```bash
# Extract all runs
tar -xzf runs.tgz
```

**Note:** The repository uses Git LFS (Large File Storage) for `.tgz` archives. Ensure Git LFS is installed:

```bash
git lfs install
git lfs pull
```

## Key Findings Summary

### Resilience Experiments (n=5 runs per scenario)

**Failure Detection Performance:**
- **gRPC Detection:** Near-instantaneous (0.0s ± 0.0s)
- **Redis Detection:** 54.2 ± 0.5s average latency
- **Speedup:** gRPC is ~3900× faster than Redis

**System Availability Under Failures:**

| Scenario | Agent Loss | gRPC Availability | Redis Availability |
|----------|-----------|-------------------|-------------------|
| Single Agent | 3.3% (1/30) | 99.8 ± 0.2% | 99.2 ± 0.7% |
| Multiple Agents | 26.7% (8/30) | 94.9 ± 2.7% | 98.2 ± 1.4% |
| Catastrophic | 50.0% (15/30) | 93.7 ± 1.0% | 92.5 ± 3.3% |

**Key Insights:**
- Both detection mechanisms maintain >99% availability under single agent failures
- Redis achieves higher availability (98.2% vs 94.9%) under multiple-agent failures, suggesting slower detection allows more stable quorum recalculation
- Graceful degradation: System maintains 92-99% job completion even under 50% agent loss
- Incomplete jobs are primarily due to resource constraints on surviving agents, not failure detection mechanisms

### Topology Scalability

**Best Performers:**
- **Small Scale (<50 agents):** Mesh topology - 0.34s mean selection (Mesh-10)
- **Medium Scale (50-250 agents):** Hierarchical topology - 0.93-1.01s mean selection
- **Large Scale (>250 agents):** Hierarchical topology scales to 990 agents (46.12s mean selection)

**WAN Overhead (Multi-Site):**
- Hierarchical-30: 1.28× slowdown (best WAN resilience)
- Mesh-30: 2.07× slowdown
- Hierarchical-110: 3.73× slowdown (10 geographic sites)

