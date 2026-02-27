"""
example_task.py
---------------
Demonstrates basic usage of the Task dataclass (τ_i ∈ Γ).

Run:
    python example_task.py

@Author: AI GENERATED SCRIPT
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.task import Task

# ── Construct a single task ────────────────────────────────────────────────────
# τ_0: C=3, T=10, D=10  (implicit deadline equal to period)
tau = Task(id=0, name="T0", bcet=1, wcet=3, period=10, deadline=10)
print(tau)

# ── Core properties ────────────────────────────────────────────────────────────
print(f"  Utilization factor  U_i = C_i/T_i = {tau.utilization:.4f}")
print(f"  Constrained deadline?    D_i < T_i = {tau.has_contrained_deadline}")

# ── Release times and absolute deadlines for first 4 instances ────────────────
print("\n  Instance  |  Release r_{i,k}  |  Abs. Deadline d_{i,k}")
print("  " + "-" * 50)
for k in range(1, 5):
    r = tau.release_time(k)
    d = tau.absolute_deadline_of(k)
    print(f"  k={k}        |  {r:<17}  |  {d}")

# ── Constrained deadline example ───────────────────────────────────────────────
print("\n── Constrained-deadline task (D_i < T_i) ──")
tau_c = Task(id=1, name="T1", bcet=2, wcet=5, period=20, deadline=15)
print(tau_c)
print(f"  Constrained deadline?  {tau_c.has_contrained_deadline}")

# ── Validation guard ───────────────────────────────────────────────────────────
print("\n── Validation: BCET > WCET raises ValueError ──")
try:
    bad = Task(id=99, name="T99", bcet=10, wcet=5, period=20, deadline=20)
except ValueError as e:
    print(f"  Caught: {e}")
