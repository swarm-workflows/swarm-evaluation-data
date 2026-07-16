#!/usr/bin/env python3
"""Comparison plots for the quantum-hybrid scale campaign.

Reads the per-run CSVs under runs/quantum-hybrid-scale/<cell>/run*/ and emits
publication-style comparison figures under .../plots/.

Metrics per job (from level_*_jobs.csv):
  - selection latency = assigned_at - selection_started_at  (consensus decision
    to place a job on its executor; measured at level0 = leaf placement)
  - end-to-end completion = job has completed_at at any level / all submitted
"""
import csv
import glob
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE = "runs/quantum-hybrid-scale"
OUT = os.path.join(BASE, "plots")
os.makedirs(OUT, exist_ok=True)

# palette
BLUE, GOLD, GREEN, RED, INK = "#2F6DB3", "#A87914", "#1F8A55", "#C24537", "#1C2433"

CELLS = {
    "hier-60-classical": dict(label="hier-60\n(hybrid)", agents=60, kind="classical", color=BLUE),
    "hier-120-classical": dict(label="hier-120\n(hybrid)", agents=120, kind="classical", color=BLUE),
    "hier-250-classical": dict(label="hier-250\n(hybrid)", agents=250, kind="classical", color=BLUE),
    "mesh-84-classical": dict(label="mesh-84\n(snow)", agents=84, kind="classical", color=GREEN),
    "mesh-84-quantum": dict(label="mesh-84-Q\n(snow)", agents=84, kind="quantum", color=GOLD),
    "hier-120-quantum": dict(label="hier-120-Q\n(hybrid)", agents=120, kind="quantum", color=RED),
}


def fnum(v):
    try:
        x = float(v)
        return x if x > 0 else None
    except (TypeError, ValueError):
        return None


def run_metrics(run_dir):
    """Return (selection_latencies list, completion_pct) for one run."""
    level_csvs = [s for s in glob.glob(os.path.join(run_dir, "level*_jobs.csv"))
                  if "pending" not in os.path.basename(s)]
    # selection latency from level0 (leaf placement); fall back to all_jobs for flat
    sel_src = os.path.join(run_dir, "level0_jobs.csv")
    if not os.path.exists(sel_src):
        sel_src = os.path.join(run_dir, "all_jobs.csv")
    sel = []
    if os.path.exists(sel_src):
        for r in csv.DictReader(open(sel_src)):
            a, s = fnum(r.get("assigned_at")), fnum(r.get("selection_started_at"))
            if a and s and a >= s:
                sel.append(a - s)
    # end-to-end completion: union ids across all levels, done if completed anywhere
    ids, done = set(), set()
    srcs = level_csvs or [os.path.join(run_dir, "all_jobs.csv")]
    for src in srcs:
        if not os.path.exists(src):
            continue
        for r in csv.DictReader(open(src)):
            jid = r.get("job_id")
            if jid is None:
                continue
            ids.add(jid)
            if fnum(r.get("completed_at")):
                done.add(jid)
    pct = 100.0 * len(done) / len(ids) if ids else 0.0
    return sel, pct


def cell_runs(cell):
    out = []
    for rd in sorted(glob.glob(os.path.join(BASE, cell, "run*"))):
        sel, pct = run_metrics(rd)
        if sel or pct:
            out.append((sel, pct))
    return out


data = {c: cell_runs(c) for c in CELLS}

# ---------------------------------------------------------------------------
# Fig 1: weak-scaling latency (hierarchical hybrid classical, 60/120/250)
# ---------------------------------------------------------------------------
scale_cells = ["hier-60-classical", "hier-120-classical", "hier-250-classical"]
xs = [CELLS[c]["agents"] for c in scale_cells]
med_mean, med_err, p90_mean = [], [], []
for c in scale_cells:
    per_run_med = [st.median(sel) for sel, _ in data[c] if sel]
    per_run_p90 = [np.percentile(sel, 90) for sel, _ in data[c] if sel]
    med_mean.append(np.mean(per_run_med))
    med_err.append(np.std(per_run_med))
    p90_mean.append(np.mean(per_run_p90))

fig, ax = plt.subplots(figsize=(7, 4.6))
ax.errorbar(xs, med_mean, yerr=med_err, marker="o", ms=8, lw=2, color=BLUE,
            capsize=5, label="median")
ax.plot(xs, p90_mean, marker="s", ms=7, lw=1.6, ls="--", color=GOLD, label="p90")
for x, y in zip(xs, med_mean):
    ax.annotate(f"{y:.1f}s", (x, y), textcoords="offset points", xytext=(0, 10),
                ha="center", fontsize=9, color=INK)
ax.set_xlabel("Agents (weak scaling, ~18 jobs/agent)")
ax.set_ylabel("Leaf-placement consensus latency (s)")
ax.set_title("Hierarchical hybrid consensus — weak-scaling latency\n(PBFT in groups + Snow across coordinators, β=6)")
ax.set_xticks(xs)
ax.grid(True, alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig1_weak_scaling_latency.png"), dpi=150)
plt.close(fig)

# ---------------------------------------------------------------------------
# Fig 2: end-to-end completion by cell
# ---------------------------------------------------------------------------
order = list(CELLS)
labels = [CELLS[c]["label"] for c in order]
colors = [CELLS[c]["color"] for c in order]
comp_mean = [np.mean([p for _, p in data[c]]) for c in order]
comp_err = [np.std([p for _, p in data[c]]) for c in order]

fig, ax = plt.subplots(figsize=(9, 4.6))
bars = ax.bar(range(len(order)), comp_mean, yerr=comp_err, color=colors,
              capsize=4, edgecolor="white")
for i, v in enumerate(comp_mean):
    ax.text(i, v + 1.5, f"{v:.0f}%", ha="center", fontsize=9, color=INK)
ax.set_xticks(range(len(order)))
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("End-to-end completion (%)")
ax.set_ylim(0, 108)
ax.axhline(100, color="#8B94A5", lw=0.8, ls=":")
ax.set_title("End-to-end job completion by scenario (mean ± std over 3 runs, 0 failures)")
ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig2_completion_by_cell.png"), dpi=150)
plt.close(fig)

# ---------------------------------------------------------------------------
# Fig 3: classical vs quantum at matched scales
# ---------------------------------------------------------------------------
pairs = [("mesh-84-classical", "mesh-84-quantum", "mesh-84 (snow)"),
         ("hier-120-classical", "hier-120-quantum", "hier-120 (hybrid)")]
fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.6))
grp = np.arange(len(pairs))
w = 0.35
cl_lat = [np.mean([st.median(s) for s, _ in data[c] if s]) for c, _, _ in pairs]
q_lat = [np.mean([st.median(s) for s, _ in data[q] if s]) for _, q, _ in pairs]
axL.bar(grp - w / 2, cl_lat, w, label="classical", color=GREEN)
axL.bar(grp + w / 2, q_lat, w, label="quantum-augmented", color=GOLD)
axL.set_xticks(grp)
axL.set_xticklabels([p[2] for p in pairs])
axL.set_ylabel("Median placement latency (s)")
axL.set_title("Latency: classical vs quantum")
axL.legend()
axL.grid(True, axis="y", alpha=0.3)

cl_c = [np.mean([p for _, p in data[c]]) for c, _, _ in pairs]
q_c = [np.mean([p for _, p in data[q]]) for _, q, _ in pairs]
axR.bar(grp - w / 2, cl_c, w, label="classical", color=GREEN)
axR.bar(grp + w / 2, q_c, w, label="quantum-augmented", color=GOLD)
for i, (a, b) in enumerate(zip(cl_c, q_c)):
    axR.text(i - w / 2, a + 1, f"{a:.0f}%", ha="center", fontsize=8)
    axR.text(i + w / 2, b + 1, f"{b:.0f}%", ha="center", fontsize=8)
axR.set_xticks(grp)
axR.set_xticklabels([p[2] for p in pairs])
axR.set_ylabel("End-to-end completion (%)")
axR.set_ylim(0, 108)
axR.set_title("Completion: classical vs quantum")
axR.legend()
axR.grid(True, axis="y", alpha=0.3)
fig.suptitle("Classical vs quantum-augmented workloads at matched scale", fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig3_classical_vs_quantum.png"), dpi=150)
plt.close(fig)

# ---------------------------------------------------------------------------
# Fig 4: placement-latency distribution by cell (pooled over 3 runs)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.6))
box_data, box_labels, box_colors = [], [], []
for c in order:
    pooled = [x for sel, _ in data[c] for x in sel]
    if pooled:
        box_data.append(pooled)
        box_labels.append(CELLS[c]["label"])
        box_colors.append(CELLS[c]["color"])
bp = ax.boxplot(box_data, tick_labels=box_labels, showfliers=False, patch_artist=True,
                medianprops=dict(color=INK, lw=1.5))
for patch, col in zip(bp["boxes"], box_colors):
    patch.set_facecolor(col)
    patch.set_alpha(0.6)
ax.set_ylabel("Placement consensus latency (s)")
ax.set_title("Placement-latency distribution by scenario (pooled, 3 runs, outliers hidden)")
ax.grid(True, axis="y", alpha=0.3)
plt.setp(ax.get_xticklabels(), fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig4_latency_distribution.png"), dpi=150)
plt.close(fig)

# ---------------------------------------------------------------------------
# console recap
# ---------------------------------------------------------------------------
print("Wrote 4 figures to", OUT)
print("\nWeak-scaling (hier hybrid): agents -> median placement latency")
for c, x, m, p in zip(scale_cells, xs, med_mean, p90_mean):
    print("  %-20s %3d agents: median %.2fs, p90 %.2fs" % (c, x, m, p))
print("\nCompletion by cell:")
for c in order:
    print("  %-20s %.0f%%  (median placement latency %.2fs)"
          % (c, np.mean([p for _, p in data[c]]),
             np.mean([st.median(s) for s, _ in data[c] if s] or [0])))
