"""
example_taskset.py
------------------
Demonstrates TaskSet construction, properties, and CSV loading.

Run:
    python example_taskset.py
    python example_taskset.py --csv data/taskset.csv   (optional)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.task import Task
from models.taskset import TaskSet

# ── Build a small task set manually ───────────────────────────────────────────
#
#   τ_0: C=1,  T=4,   D=4
#   τ_1: C=2,  T=6,   D=6
#   τ_2: C=3,  T=12,  D=12
#
#   Classic example from Buttazzo §4 — Liu & Layland bound: U ≤ n(2^(1/n) - 1)

tasks = [
    Task(id=0, name="T0", bcet=1, wcet=1, period=4,  deadline=4),
    Task(id=1, name="T1", bcet=1, wcet=2, period=6,  deadline=6),
    Task(id=2, name="T2", bcet=2, wcet=3, period=12, deadline=12),
]

gamma = TaskSet(tasks)
print("── Task Set ──────────────────────────────────────────────")
print(gamma)
print()

# ── Individual tasks ───────────────────────────────────────────────────────────
print("── Tasks (sorted by id) ──────────────────────────────────")
for t in gamma:
    print(f"  {t}  U_i={t.utilization:.4f}")
print()

# ── Set-level properties ───────────────────────────────────────────────────────
print("── Properties ────────────────────────────────────────────")
print(f"  n (task count)      = {gamma.n}")
print(f"  U (total util.)     = {gamma.utilization:.4f}")
print(f"  H (hyperperiod)     = {gamma.hyperperiod}")
print(f"  D_max               = {gamma.D_max}")
print(f"  Constrained?        = {gamma.has_constrained_deadlines}")
print()

# ── Scheduling order examples ──────────────────────────────────────────────────
print("── Rate Monotonic priority order (shortest period first) ──")
for rank, t in enumerate(gamma.sorted_by_period(), start=1):
    print(f"  [{rank}] {t}")

print()
print("── Deadline Monotonic priority order (shortest deadline first) ──")
for rank, t in enumerate(gamma.sorted_by_deadline(), start=1):
    print(f"  [{rank}] {t}")

# ── Liu & Layland utilization bound ───────────────────────────────────────────
import math
n = gamma.n
ll_bound = n * (2 ** (1 / n) - 1)
print()
print("── Liu & Layland Bound ───────────────────────────────────")
print(f"  U_lub = n(2^(1/n) - 1) = {ll_bound:.4f}")
print(f"  U     = {gamma.utilization:.4f}  →  {'✓ schedulable' if gamma.utilization <= ll_bound else '✗ not guaranteed by RM'}")

# ── Optional: load from CSV ────────────────────────────────────────────────────
if "--csv" in sys.argv:
    csv_path = Path(sys.argv[sys.argv.index("--csv") + 1])
    print(f"\n── Loading from CSV: {csv_path} ──────────────────────────")
    gamma_csv = TaskSet.from_csv(csv_path)
    print(gamma_csv)
    for t in gamma_csv:
        print(f"  {t}  U_i={t.utilization:.4f}")
    n_csv = gamma_csv.n
    ll_csv = n_csv * (2 ** (1 / n_csv) - 1)
    print(f"\n  U={gamma_csv.utilization:.4f}  U_lub={ll_csv:.4f}  "
          f"→  {'✓ schedulable' if gamma_csv.utilization <= ll_csv else '✗ not guaranteed by RM'}")
