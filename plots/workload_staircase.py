"""
workload_staircase.py
---------------------
02225 DRTS — Mini-Project 1
Staircase workload plot W_i(t) for the lowest-priority task under DM.

Usage:
    python -m plots.workload_staircase --taskset path/to/taskset.csv
"""

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt

from models.scheduling.task import Task
from models.scheduling.taskset import TaskSet


# ── Workload helpers ─────────────────────────────────────────────────────────

def _testing_points(task: Task, hp: list[Task]) -> list[float]:
    """Multiples of every HP period up to D_i, plus D_i itself."""
    pts = {float(task.deadline)}
    for h in hp:
        k = 1
        while k * h.period <= task.deadline:
            pts.add(float(k * h.period))
            k += 1
    return sorted(pts)


def _workload(task: Task, hp: list[Task], t: float) -> float:
    """W_i(t) = C_i + Σ ⌈t / T_h⌉ · C_h   (Buttazzo Eq. 4.31)"""
    return task.wcet + sum(math.ceil(t / h.period) * h.wcet for h in hp)


# ── Plot ─────────────────────────────────────────────────────────────────────

def plot_staircase(task: Task, hp: list[Task]) -> None:
    pts = _testing_points(task, hp)
    ws  = [_workload(task, hp, t) for t in pts]

    # First t* where W_i(t*) ≤ t*  →  critical (schedulable) moment
    critical = next(((t, w) for t, w in zip(pts, ws) if w <= t), None)
    schedulable = critical is not None

    title_color = "#1D9E75" if schedulable else "#E24B4A"
    verdict     = "SCHEDULABLE" if schedulable else "NOT SCHEDULABLE"
    t_max       = task.deadline * 1.15

    fig, ax = plt.subplots(figsize=(10, 5))

    # y = t diagonal
    ax.plot([0, t_max], [0, t_max],
            color="gray", linestyle="--", linewidth=1, alpha=0.6, label="y = t")

    # deadline marker
    ax.axvline(task.deadline, color="#E24B4A", linestyle=":",
               linewidth=1.2, label=f"D = {task.deadline}")

    # staircase W(t)
    ax.step(pts, ws, where="post",
            color="#185FA5", linewidth=2.2, label="W(t)", zorder=3)

    # testing-set dots
    ax.scatter(pts, ws, color="#EF9F27", s=40, zorder=4,
               edgecolors="white", linewidths=0.5, label="Testing set")

    # critical moment annotation
    if critical:
        t_star, w_star = critical
        ax.scatter([t_star], [w_star], color="#1D9E75", s=160, zorder=5,
                   edgecolors="white", linewidths=2,
                   label=f"t* = {t_star:.0f}  (W = {w_star:.0f} ≤ t*)")
        ax.annotate(
            f"  t* = {t_star:.0f}\n  W  = {w_star:.0f}",
            xy=(t_star, w_star),
            xytext=(t_star + t_max * 0.05, w_star + t_max * 0.06),
            fontsize=9, color="#1D9E75",
            arrowprops=dict(arrowstyle="->", color="#1D9E75", lw=1.2),
        )

    ax.set_title(
        f"τ_{task.id}   C={task.wcet}  T={task.period}  D={task.deadline}"
        f"   —   {verdict}",
        fontsize=12, fontweight="bold", color=title_color,
    )
    ax.set_xlabel("t")
    ax.set_ylabel("W(t)")
    ax.set_xlim(0, t_max)
    ax.set_ylim(0)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.15)
    fig.tight_layout()
    plt.show()


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--taskset", required=True, help="Path to task set CSV")
    args = parser.parse_args()

    taskset  = TaskSet.from_csv(args.taskset)
    dm_order = taskset.sorted_by_deadline()   # shortest deadline = highest priority

    task = dm_order[-1]     # lowest-priority task (most interesting workload)
    hp   = dm_order[:-1]    # all higher-priority tasks

    plot_staircase(task, hp)
