#!/usr/bin/env python3
"""Generate resilience comparison figure for the SWARM+ eScience paper.

Produces a two-panel figure:
  Top:    Per-run job completion percentage (grouped bar + mean line)
  Bottom: Selection time box plots per scenario

Reads data from: runs/hier110-resilience/{baseline,distributed-10,distributed-20,site-outage}/run-{1..5}/all_jobs.csv
Outputs:         ../SWARM_Escience26_Consensus/figures/resilience_comparison.pdf
"""

import csv
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

DATA_ROOT = os.path.join(os.path.dirname(__file__), "runs", "hier110-resilience")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "SWARM_Escience26_Consensus", "figures")

SCENARIOS = [
    ("baseline",       "Baseline\n(no failure)", "#4CAF50"),
    ("distributed-10", "Distributed-10\n(10 killed)", "#2196F3"),
    ("distributed-20", "Distributed-20\n(~18 killed)", "#FF9800"),
    ("site-outage",    "Site Outage\n(11 killed)", "#F44336"),
]

NUM_RUNS = 5


def load_scenario(scenario_dir):
    """Return per-run (completion_pct, sel_times) for a scenario."""
    run_completions = []
    run_sel_times = []

    for r in range(1, NUM_RUNS + 1):
        csv_path = os.path.join(DATA_ROOT, scenario_dir, f"run-{r}", "all_jobs.csv")
        jobs = {}       # job_id -> completed?
        sel_times = []  # selection times for completed jobs

        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                jid = row["job_id"]
                completed = float(row["completed_at"]) > 0
                ss = float(row["selection_started_at"])
                aa = float(row["assigned_at"])

                if completed and ss > 0 and aa > 0:
                    sel_times.append(aa - ss)

                if jid not in jobs:
                    jobs[jid] = completed
                else:
                    jobs[jid] = jobs[jid] or completed

        total = len(jobs)
        done = sum(1 for v in jobs.values() if v)
        pct = 100.0 * done / total if total else 0
        run_completions.append(pct)
        run_sel_times.append(sel_times)

    return run_completions, run_sel_times


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5.5),
                                    gridspec_kw={"height_ratios": [1, 1.2]})

    all_data = {}
    for sc_dir, sc_label, sc_color in SCENARIOS:
        completions, sel_times = load_scenario(sc_dir)
        all_data[sc_dir] = {
            "label": sc_label,
            "color": sc_color,
            "completions": completions,
            "sel_times": sel_times,
        }

    # ── Top panel: completion percentage per run ──
    x = np.arange(NUM_RUNS)
    bar_width = 0.18
    offsets = np.arange(len(SCENARIOS)) - (len(SCENARIOS) - 1) / 2

    for i, (sc_dir, sc_label, sc_color) in enumerate(SCENARIOS):
        d = all_data[sc_dir]
        bars = ax1.bar(x + offsets[i] * bar_width, d["completions"],
                       bar_width, label=sc_label.replace("\n", " "),
                       color=sc_color, alpha=0.85, edgecolor="white",
                       linewidth=0.5)
        # mean line
        mean_val = np.mean(d["completions"])
        ax1.hlines(mean_val,
                    x[0] + offsets[i] * bar_width - bar_width / 2,
                    x[-1] + offsets[i] * bar_width + bar_width / 2,
                    colors=sc_color, linewidth=1.5, linestyle="--", alpha=0.7)

    ax1.set_ylabel("Job Completion (%)", fontsize=13)
    ax1.set_xlabel("Run", fontsize=13)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"Run {r+1}" for r in range(NUM_RUNS)], fontsize=11)
    ax1.set_ylim(88, 101)
    ax1.tick_params(axis="y", labelsize=11)
    ax1.legend(loc="lower left", fontsize=9.5, ncol=2, framealpha=0.9)
    ax1.grid(axis="y", alpha=0.3)
    ax1.set_title("(a) Job Completion Rate per Run", fontsize=13, fontweight="bold")

    # ── Bottom panel: selection time box plots ──
    positions = []
    bp_data = []
    colors = []
    tick_positions = []
    tick_labels_list = []

    group_width = 1.0
    gap = 0.6
    pos = 0
    for i, (sc_dir, sc_label, sc_color) in enumerate(SCENARIOS):
        d = all_data[sc_dir]
        # Aggregate all selection times across runs
        all_sel = []
        for st in d["sel_times"]:
            all_sel.extend(st)
        bp_data.append(all_sel)
        positions.append(pos)
        colors.append(sc_color)
        tick_positions.append(pos)
        tick_labels_list.append(sc_label)
        pos += group_width + gap

    bp = ax2.boxplot(bp_data, positions=positions, widths=0.7,
                     patch_artist=True, showfliers=True,
                     flierprops=dict(marker=".", markersize=2, alpha=0.3),
                     medianprops=dict(color="black", linewidth=1.5),
                     whiskerprops=dict(linewidth=1),
                     capprops=dict(linewidth=1))

    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax2.set_xticks(tick_positions)
    ax2.set_xticklabels(tick_labels_list, fontsize=10)
    ax2.set_ylabel("Selection Time (s)", fontsize=13)
    ax2.tick_params(axis="y", labelsize=11)
    # Fixed y-axis to leave room for annotations at top
    y_max = 14
    ax2.set_ylim(0, y_max)
    ax2.grid(axis="y", alpha=0.3)
    ax2.set_title("(b) Selection Time Distribution", fontsize=13, fontweight="bold")

    # Add mean + P95 annotations in top region
    for pos_val, data, color in zip(positions, bp_data, colors):
        mean_val = np.mean(data)
        p95_val = np.percentile(data, 95)
        ax2.annotate(f"μ={mean_val:.2f}s  P95={p95_val:.1f}s",
                     xy=(pos_val, y_max * 0.82),
                     ha="center", va="bottom", fontsize=9, fontweight="bold",
                     color="black",
                     bbox=dict(boxstyle="round,pad=0.2", facecolor=color,
                               alpha=0.2, edgecolor="none"))

    plt.tight_layout()

    out_pdf = os.path.join(OUT_DIR, "resilience_comparison.pdf")
    out_png = os.path.join(OUT_DIR, "resilience_comparison.png")
    fig.savefig(out_pdf, bbox_inches="tight", dpi=300)
    fig.savefig(out_png, bbox_inches="tight", dpi=150)
    print(f"Saved: {out_pdf}")
    print(f"Saved: {out_png}")
    plt.close()


if __name__ == "__main__":
    main()
