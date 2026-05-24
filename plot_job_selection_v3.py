#!/usr/bin/env python3
"""Recreate the Hierarchical Job Selection diagram with Level 1 / Level 0 labels."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "SWARM_Escience26_Consensus", "figures")


def draw_stick_figure(ax, x, y, color="navy", scale=1.0):
    """Draw a simple stick figure at (x, y)."""
    s = scale
    # Head
    head = plt.Circle((x, y + 0.18 * s), 0.06 * s, fill=False, edgecolor=color, linewidth=1.5)
    ax.add_patch(head)
    # Body
    ax.plot([x, x], [y + 0.12 * s, y - 0.05 * s], color=color, linewidth=1.5)
    # Arms
    ax.plot([x - 0.08 * s, x + 0.08 * s], [y + 0.06 * s, y + 0.06 * s], color=color, linewidth=1.5)
    # Legs
    ax.plot([x, x - 0.06 * s], [y - 0.05 * s, y - 0.18 * s], color=color, linewidth=1.5)
    ax.plot([x, x + 0.06 * s], [y - 0.05 * s, y - 0.18 * s], color=color, linewidth=1.5)


def draw_rounded_box(ax, x, y, w, h, text, fontsize=11, facecolor="#B3E5FC",
                     edgecolor="black", linewidth=1.5, fontstyle="normal", fontweight="bold"):
    """Draw a rounded rectangle with centered text."""
    box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                          boxstyle="round,pad=0.05",
                          facecolor=facecolor, edgecolor=edgecolor,
                          linewidth=linewidth)
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            fontweight=fontweight, fontstyle=fontstyle)


def draw_dashed_ellipse(ax, cx, cy, rx, ry, color="#1565C0", linewidth=1.8):
    """Draw a dashed ellipse."""
    theta = np.linspace(0, 2 * np.pi, 200)
    xs = cx + rx * np.cos(theta)
    ys = cy + ry * np.sin(theta)
    ax.plot(xs, ys, color=color, linestyle="--", linewidth=linewidth)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    fig, ax = plt.subplots(1, 1, figsize=(10, 7.5))
    ax.set_xlim(-1.5, 9.5)
    ax.set_ylim(-3.5, 5.5)
    ax.set_aspect("equal")
    ax.axis("off")

    # ── Title ──
    ax.text(-1.2, 5.0, "Hierarchical\nJob Selection", fontsize=16, fontweight="bold",
            va="top", ha="left")

    # ── Global Dynamic Workload Pool ──
    draw_rounded_box(ax, 4.0, 4.8, 2.8, 0.7, "Global Dynamic\nWorkload Pool",
                     fontsize=11, facecolor="#B3E5FC")

    # "Set of jobs" label and arrow down
    ax.annotate("", xy=(4.0, 3.55), xytext=(4.0, 4.45),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.5))
    ax.text(4.4, 4.15, "Set of jobs", fontsize=10, fontstyle="italic", ha="left",
            bbox=dict(facecolor="white", edgecolor="none", pad=1))

    # ── Level 1: Coordinator Agents ──
    coord_y = 3.0
    coord_positions = {
        "A1": (1.5, coord_y + 0.35),
        "A2": (0.5, coord_y - 0.5),
        "A3": (2.5, coord_y - 0.7),
        "Ai": (4.0, coord_y + 0.15),
        "Aj": (5.5, coord_y - 0.7),
        "A5": (7.5, coord_y - 0.5),
        "AN": (6.5, coord_y + 0.35),
    }

    coord_color = "navy"
    for label, (cx, cy) in coord_positions.items():
        draw_stick_figure(ax, cx, cy, color=coord_color, scale=0.8)
        # Subscript label
        if label == "Ai":
            ax.text(cx + 0.15, cy + 0.30, r"$A_i$", fontsize=12, color=coord_color, ha="left")
        elif label == "Aj":
            ax.text(cx + 0.15, cy + 0.30, r"$A_j$", fontsize=12, color=coord_color, ha="left")
        elif label == "A1":
            ax.text(cx + 0.15, cy + 0.30, r"$A_1$", fontsize=12, color=coord_color, ha="left")
        elif label == "A2":
            ax.text(cx + 0.15, cy + 0.30, r"$A_2$", fontsize=12, color=coord_color, ha="left")
        elif label == "A3":
            ax.text(cx + 0.15, cy + 0.30, r"$A_3$", fontsize=12, color=coord_color, ha="left")
        elif label == "A5":
            ax.text(cx + 0.15, cy + 0.30, r"$A_5$", fontsize=12, color=coord_color, ha="left")
        elif label == "AN":
            ax.text(cx + 0.15, cy + 0.30, r"$A_N$", fontsize=12, color=coord_color, ha="left")

    # Dashed ellipse around coordinator agents
    draw_dashed_ellipse(ax, 4.0, coord_y - 0.1, 4.0, 1.2, color="#1565C0")

    # Right-side annotation for Level 1
    ax.text(8.5, coord_y + 0.8, "CoordinatorAgents'\ndecision: which jobs\nto select for execution",
            fontsize=9.5, ha="left", va="top")

    # ── LEVEL LABELS ──
    # Level 1 label (left side, next to coordinator ellipse)
    ax.text(-1.3, coord_y - 0.1, "Level 1", fontsize=13, fontweight="bold",
            color="#1565C0", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#E3F2FD", edgecolor="#1565C0",
                      linewidth=1.5, alpha=0.9))

    # ── Arrows from Ai and Aj down to local pools ──
    # "Set of jobs selected by CoordinatorAgent Ai"
    ax.annotate("", xy=(2.0, 0.8), xytext=(3.8, coord_y - 0.9),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.5))
    ax.text(0.3, 1.6, "Set of jobs selected by\n" + r"$CoordinatorAgent\ A_i$",
            fontsize=9, fontstyle="italic", ha="center", va="top")

    ax.annotate("", xy=(6.0, 0.8), xytext=(5.5, coord_y - 0.9),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.5))
    ax.text(7.5, 1.6, "Set of jobs selected by\n" + r"$CoordinatorAgent\ A_j$",
            fontsize=9, fontstyle="italic", ha="center", va="top")

    # ── Local Job Pools ──
    draw_rounded_box(ax, 2.0, 0.3, 1.8, 0.55, "Local Job Pool",
                     fontsize=10, facecolor="#B3E5FC")
    draw_rounded_box(ax, 6.0, 0.3, 1.8, 0.55, "Local Job Pool",
                     fontsize=10, facecolor="#B3E5FC")

    # ── Level 0: Resource Agents ──
    res_color = "#00ACC1"  # cyan-ish
    # Left group (a1, a2, an)
    left_agents = {
        "a1": (0.8, -1.5),
        "a2": (2.0, -1.8),
        "an": (3.2, -1.5),
    }
    for label, (rx, ry) in left_agents.items():
        draw_stick_figure(ax, rx, ry, color=res_color, scale=0.8)
        if label == "a1":
            ax.text(rx - 0.2, ry + 0.30, r"$a_1$", fontsize=11, color=res_color, ha="right")
        elif label == "a2":
            ax.text(rx + 0.15, ry + 0.30, r"$a_2$", fontsize=11, color=res_color, ha="left")
        elif label == "an":
            ax.text(rx + 0.15, ry + 0.30, r"$a_n$", fontsize=11, color=res_color, ha="left")

    draw_dashed_ellipse(ax, 2.0, -1.5, 1.6, 0.8, color="#00ACC1")

    # Right group (b1, b2, bm)
    right_agents = {
        "b1": (4.8, -1.5),
        "b2": (6.0, -1.8),
        "bm": (7.2, -1.5),
    }
    for label, (rx, ry) in right_agents.items():
        draw_stick_figure(ax, rx, ry, color=res_color, scale=0.8)
        if label == "b1":
            ax.text(rx - 0.2, ry + 0.30, r"$b_1$", fontsize=11, color=res_color, ha="right")
        elif label == "b2":
            ax.text(rx + 0.15, ry + 0.30, r"$b_2$", fontsize=11, color=res_color, ha="left")
        elif label == "bm":
            ax.text(rx + 0.15, ry + 0.30, r"$b_m$", fontsize=11, color=res_color, ha="left")

    draw_dashed_ellipse(ax, 6.0, -1.5, 1.6, 0.8, color="#00ACC1")

    # Right-side annotation for Level 0
    ax.text(8.5, -1.2, "ResourceAgents'\ndecision: which\njobs to select\nfor resources",
            fontsize=9.5, ha="left", va="top")

    # Level 0 label (left side, next to resource ellipse)
    ax.text(-1.3, -1.5, "Level 0", fontsize=13, fontweight="bold",
            color="#00ACC1", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#E0F7FA", edgecolor="#00ACC1",
                      linewidth=1.5, alpha=0.9))

    plt.tight_layout()

    out_pdf = os.path.join(OUT_DIR, "Job-Selection-v3.pdf")
    out_png = os.path.join(OUT_DIR, "Job-Selection-v3.png")
    fig.savefig(out_pdf, bbox_inches="tight", dpi=300)
    fig.savefig(out_png, bbox_inches="tight", dpi=150)
    print(f"Saved: {out_pdf}")
    print(f"Saved: {out_png}")
    plt.close()


if __name__ == "__main__":
    main()
