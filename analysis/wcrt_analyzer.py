from math import ceil

from models.scheduling.task import Task
from models.scheduling.taskset import TaskSet


def rta_dm(taskset: TaskSet) -> dict[int, dict]:
    """
    Analytical Worst-Case Response Time (WCRT) for every task under
    Deadline Monotonic (DM) scheduling.

    Algorithm — Audsley et al. (1993):
        Priority order : shortest deadline first (DM rule).
        Initial guess  : R_i^(0) = C_i
        Iteration      : R_i^(s) = C_i + Σ_{h ∈ hp(i)} ⌈ R_i^(s-1) / T_h ⌉ · C_h
        Stop when      : R_i^(s) = R_i^(s-1)  → converged, WCRT = R_i
                         R_i^(s) > D_i         → unschedulable

    @Returns:
        A dict keyed by task id.  Each value is:
            wcrt        : float | None   — WCRT, or None if unschedulable
            schedulable : bool
            iterations  : list[float]    — R_i^(0), R_i^(1), ... (convergence trace)
    """
    tasks: list[Task] = sorted(taskset.tasks, key=lambda t: t.deadline)
    result = {}

    for i, task in enumerate(tasks):
        hp = tasks[:i]   # higher-priority tasks under DM (shorter deadlines)

        R = float(task.wcet)   # R_i^(0) = C_i
        trace = [R]

        while True:
            # Interference from all higher-priority tasks in window [0, R)
            interference = sum(ceil(R / h.period) * h.wcet for h in hp)
            R_new = task.wcet + interference

            trace.append(R_new)

            if R_new > task.deadline:
                # Response time exceeded deadline — task is not schedulable
                result[task.id] = {
                    "wcrt":        None,
                    "schedulable": False,
                    "iterations":  trace,
                }
                break

            if R_new == R:
                # Fixed point reached — this is the exact WCRT
                result[task.id] = {
                    "wcrt":        R,
                    "schedulable": True,
                    "iterations":  trace,
                }
                break

            R = R_new

    return result
