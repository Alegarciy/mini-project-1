
"""
response_time_analysis.py
-------------
@Author: Dumitrita 
"""

from math import ceil, floor
from models.scheduling.taskset import TaskSet
from models.scheduling.task import Task


# =========================
# DM — RESPONSE TIME ANALYSIS
# =========================

def response_time_dm_helper(tasks: list[Task]) -> dict:
    """
    Computes the worst-case response time of the last task in `tasks`
    assuming all previous tasks are higher-priority tasks under DM.
    """

    if not tasks:
        raise ValueError("response_time_dm_helper received an empty task list")

    task_i = tasks[-1]
    hp_tasks = tasks[:-1]

    R_i = task_i.wcet
    steps = [R_i]
    print(f'Taskset to evaluate RTA Scheduability: {[t.wcet for t in tasks]}')

    while True:
        R_old = R_i

        interference = 0
        for hp in hp_tasks:

            interference += ceil(R_old / hp.period) * hp.wcet

        R_i = task_i.wcet + interference
        steps.append(R_i)

        if R_i > task_i.deadline:
            return {
                "task": task_i,
                "response_time": R_i,
                "schedulable": False,
                "steps": steps,
                "analysis": "DM-RTA",
            }

        # if R_i != R_old and R_old != task_i.wcet:
        #     print(f'Not Stable because of jump of interference: {R_i-R_old}')
        #     print('Previous Interference:', R_old)
        #     print('New Interference Leap:', R_i)
        # elif R_i == R_old and R_old != task_i.wcet:
        #     print(f'Stable because of jump was: {R_i-R_old}')
        #     print(f'Constant R_i on:{R_i}')


        if R_i == R_old:
            return {
                "task": task_i,
                "response_time": R_i,
                "schedulable": True,
                "steps": steps,
                "analysis": "DM-RTA",
            }


def response_time_dm(taskset: TaskSet) -> list[dict]:
    """
    Performs Deadline Monotonic Response Time Analysis on the whole task set.
    """
    tasks = taskset.sorted_by_deadline()
    results = []

    for i in range(len(tasks)):
        result_i = response_time_dm_helper(tasks[: i + 1])
        results.append(result_i)

        if not result_i["schedulable"]:
            break

    return results


# =========================
# EDF — DEMAND / WORKLOAD ANALYSIS
# =========================

def edf_demand_bound_at_t(taskset: TaskSet, t: int) -> dict:
    """
    Computes the EDF demand bound function at time t:

        dbf(t) = sum( floor((t + T_i - D_i) / T_i) * C_i )

    For implicit deadlines (D_i = T_i), this becomes:
        dbf(t) = sum( floor(t / T_i) * C_i )
    """

    total_demand = 0
    per_task = []

    for task in taskset:
        jobs = floor((t + task.period - task.deadline) / task.period)
        jobs = max(0, jobs)
        contribution = jobs * task.wcet
        total_demand += contribution

        per_task.append({
            "task": task,
            "jobs": jobs,
            "contribution": contribution,
        })

    return {
        "t": t,
        "demand": total_demand,
        "schedulable": total_demand <= t,
        "details": per_task,
        "analysis": "EDF-DBF",
    }


def edf_analysis(taskset: TaskSet) -> list[dict]:
    """
    Runs EDF analytical schedulability checks for a set of candidate time points.

    For your task set, using deadlines as candidate points is a simple and
    readable approach.
    """
    candidate_ts = sorted({task.deadline for task in taskset})
    results = []

    for t in candidate_ts:
        result_t = edf_demand_bound_at_t(taskset, t)
        results.append(result_t)

        if not result_t["schedulable"]:
            break

    return results


# =========================
# DISPATCHER
# =========================

def response_time_analysis(taskset: TaskSet, schedule_type="DM"):
    """
    Unified entry point for analytical checks.

    DM  -> exact Response Time Analysis
    EDF -> demand/workload analysis
    """
    if schedule_type == "DM":
        return response_time_dm(taskset)
    elif schedule_type == "EDF":
        return edf_analysis(taskset)
    else:
        raise NotImplementedError(
            f"Analytical response-time/workload analysis not implemented for {schedule_type}"
        )
