import copy
from math import ceil
from math import floor

from models.scheduling.taskset import TaskSet
from models.scheduling.task import Task


def workload(taskset: TaskSet, schedule_type="DM"):
    if schedule_type == "DM":
        return workload_dm(taskset)
    else:
        return workload_edf(taskset)


# =============================================================================
#  EDF — Demand Bound Function
# =============================================================================

def calculate_dbf(taskset, t: int):
    total = 0

    for task in taskset.tasks:
        C = task.wcet
        T = task.period
        D = task.deadline

        jobs = floor((t + T - D) / T)
        jobs = max(0, jobs)

        total += jobs * C

    return total


def workload_EDF_helper(taskset):
    points = set()
    max_t = sum(task.period for task in taskset.tasks)

    for task in taskset.tasks:
        k = 0
        while True:
            t = k * task.period + task.deadline

            if t > max_t:
                break

            if t > 0:
                points.add(t)

            k += 1

    return sorted(points)


def workload_edf(taskset):
    print("EDF Demand Bound Function Analysis:")
    is_schedulable = True

    for t in workload_EDF_helper(taskset):
        demand = calculate_dbf(taskset, t)
        accepted = demand <= t
        print(f"t = {t} | dbf(t) = {demand} | {'ACCEPTED' if accepted else 'FAILED'}")
        is_schedulable &= accepted

    print("Taskset is schedulable under EDF" if is_schedulable
        else "Taskset is NOT schedulable under EDF")

    return is_schedulable


# =============================================================================
#  DM — Workload Function
# =============================================================================

def workload_dm_helper(tasks: list[Task]):
    last_task = tasks[-1]
    previous_tasks = tasks[:-1]

    # multiple time per period until t reaches the H
    test_points = set()
    test_points.add(last_task.deadline)

    # Take into a count each task period before big task
    for p_task in previous_tasks:
        k = 1
        while k * p_task.period <= last_task.deadline:
            test_points.add(k * p_task.period)
            k += 1

    # Check each point W(i)
    for t in sorted(test_points):
        interference = sum(
            ceil(t / p_task.period) * p_task.wcet for p_task in previous_tasks
        )
        w = last_task.wcet + interference
        # Compare if the Workload < Time
        if w <= t:
            return w

    return -1


def workload_dm(taskset: TaskSet):
    taskset.sorted_by_deadline()
    tasks: list[Task] = [copy.copy(t) for t in taskset.tasks]

    result = []
    for i in range(1, len(tasks) + 1):
        workload_i = workload_dm_helper(tasks[:i])
        result.append(workload_i)

    return result


def workload_at_deadline_dm(taskset: TaskSet) -> list[int]:
    """
    Compute W_i(D_i) for every task — always evaluates at the deadline,
    no early exit.  The existing algorithm is untouched; this is additive.
    """
    taskset.sorted_by_deadline()
    tasks: list[Task] = [copy.copy(t) for t in taskset.tasks]

    result = []
    for i in range(1, len(tasks) + 1):
        last_task      = tasks[i - 1]
        previous_tasks = tasks[:i - 1]
        t              = last_task.deadline
        interference   = sum(
            ceil(t / p.period) * p.wcet for p in previous_tasks
        )
        result.append(last_task.wcet + interference)

    return result


# =============================================================================
#  LOG-BASED WORKLOAD TRACE
# =============================================================================

def workload_trace_from_logs(logs: dict, taskset: TaskSet, task_id: int) -> dict:
    """
    Replay the simulation schedule_trace and build the W_i(t) step-through
    table up to the first deadline D_i of the target task.

    Under DM: higher priority ↔ smaller deadline (D_h < D_i).

    @Returns dict with:
        rows        : list of slot dicts (see below)
        W_final     : accumulated workload at t = D_i
        D_i         : first deadline of τ_task_id
        C_i         : WCET of τ_task_id
        slack       : D_i − W_final  (positive = schedulable)
        higher_ids  : set of higher-priority task ids
    """
    target = taskset.get_task(task_id)
    D_i = target.deadline
    C_i = target.wcet

    # DM: higher priority = strictly smaller deadline
    higher_ids = {t.id for t in taskset if t.deadline < D_i}

    rows = []
    w = 0.0

    for slot in logs["schedule_trace"]:
        if slot["start"] >= D_i:
            break

        start  = slot["start"]
        end    = min(slot["end"], D_i)
        tid    = slot["task_id"]
        delta  = end - start

        is_target   = tid == task_id
        is_higher   = tid in higher_ids
        contributes = is_target or is_higher

        if contributes:
            w += delta

        rows.append({
            "start":       start,
            "end":         end,
            "task_id":     tid,
            "delta":       delta,
            "w":           w if contributes else None,
            "is_target":   is_target,
            "is_higher":   is_higher,
            "contributes": contributes,
        })

    return {
        "rows":        rows,
        "W_final":     w,
        "D_i":         D_i,
        "C_i":         C_i,
        "slack":       D_i - w,
        "higher_ids":  higher_ids,
    }


