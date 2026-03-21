"""
log_loader.py
-------------
02225 DRTS — Mini-Project 1
Utilities to load simulation CSVs back into memory for post-run analysis.

Example usage:
    from analysis.log_loader import load_logs

    logs = load_logs("logs/", algorithm="DM", timestamp="20260320_143512")

    # All jobs for task 1 that missed their deadline
    misses = [j for j in logs["all_jobs"] if j["task_id"] == 1 and j["missed_deadline"]]

    # Scheduling segments longer than 5 time units
    long_slots = [s for s in logs["schedule_trace"] if s["end"] - s["start"] > 5]

@Author: Claude Generated
"""

import csv
from pathlib import Path

from models.scheduling.task import Task
from models.scheduling.taskset import TaskSet


# ── Field type coercions ──────────────────────────────────────────────────────
# CSV stores everything as strings; these helpers restore the original types.

def _to_float_or_none(val: str):
    return None if val == "" or val == "None" else float(val)


def _to_int(val: str) -> int:
    return int(float(val))


def _to_bool(val: str) -> bool:
    return val.strip().lower() == "true"


def _cast_job_row(row: dict) -> dict:
    return {
        "task_id":           _to_int(row["task_id"]),
        "job_id":            _to_int(row["job_id"]),
        "release_time":      float(row["release_time"]),
        "absolute_deadline": float(row["absolute_deadline"]),
        "execution_time":    float(row["execution_time"]),
        "remaining_time":    float(row["remaining_time"]),
        "start_time":        _to_float_or_none(row["start_time"]),
        "finish_time":       _to_float_or_none(row["finish_time"]),
        "preemtion_count":   _to_int(row["preemtion_count"]),
        "response_time":     _to_float_or_none(row["response_time"]),
        "missed_deadline":   _to_bool(row["missed_deadline"]),
        "is_completed":      _to_bool(row["is_completed"]),
    }


# ── Loaders ───────────────────────────────────────────────────────────────────

def _load_schedule_trace(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return [
            {
                "start":   float(row["start"]),
                "end":     float(row["end"]),
                "task_id": _to_int(row["task_id"]),
            }
            for row in csv.DictReader(f)
        ]


def _load_preemption_log(path: Path) -> list[dict]:
    JOB_FIELDS = [
        "task_id", "job_id", "release_time", "absolute_deadline",
        "execution_time", "remaining_time", "start_time", "finish_time",
        "preemtion_count", "response_time", "missed_deadline", "is_completed",
    ]
    with open(path, newline="") as f:
        rows = []
        for row in csv.DictReader(f):
            rows.append({
                "time":      float(row["time"]),
                "preempted": _cast_job_row({k: row[f"preempted_{k}"] for k in JOB_FIELDS}),
                "by":        _cast_job_row({k: row[f"by_{k}"] for k in JOB_FIELDS}),
            })
        return rows


def _load_jobs(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return [_cast_job_row(row) for row in csv.DictReader(f)]


# ── Public API ────────────────────────────────────────────────────────────────

def load_logs(log_dir: str | Path, algorithm: str, timestamp: str, replication: int = None) -> dict:
    """
    Load the four simulation CSV logs for a given run back into memory.

    @Params:
        log_dir     : Directory where logs were saved (--log-dir value)
        algorithm   : "DM" or "EDF"
        timestamp   : Timestamp string from the run, e.g. "20260320_143512"
        replication : Replication index (1-based) when --replications > 1.
                      Leave None for single-replication runs.

    @Returns: dict with keys:
        "schedule_trace"  : list of {start, end, task_id}
        "preemption_log"  : list of {time, preempted: job_dict, by: job_dict}
        "all_jobs"        : list of job dicts
        "completed_jobs"  : list of job dicts

    @Author: Claude Generated
    """
    log_dir = Path(log_dir)
    rep_suffix = f"_rep{replication}" if replication is not None else ""
    base = f"{algorithm}_{timestamp}{rep_suffix}"

    return {
        "schedule_trace": _load_schedule_trace(log_dir / f"schedule_trace_{base}.csv"),
        "preemption_log": _load_preemption_log(log_dir / f"preemption_log_{base}.csv"),
        "all_jobs":       _load_jobs(log_dir / f"all_jobs_{base}.csv"),
        "completed_jobs": _load_jobs(log_dir / f"completed_jobs_{base}.csv"),
    }


def taskset_from_logs(logs: dict) -> TaskSet:
    """
    Reconstruct a TaskSet from the all_jobs log.

    Infers per-task parameters without needing the original CSV:
        T_i   = release_time of the second job of τ_i  (since phase=0)
        D_i   = absolute_deadline of the first job      (= D_i when phase=0)
        WCET  = max execution_time across all jobs of τ_i
        BCET  = min execution_time across all jobs of τ_i

    @Author: Claude Generated
    """
    from collections import defaultdict

    by_task: dict[int, list[dict]] = defaultdict(list)
    for job in logs["all_jobs"]:
        by_task[job["task_id"]].append(job)

    tasks = []
    for tid, jobs in sorted(by_task.items()):
        jobs_sorted = sorted(jobs, key=lambda j: j["job_id"])

        D_i  = int(jobs_sorted[0]["absolute_deadline"])
        T_i  = int(jobs_sorted[1]["release_time"]) if len(jobs_sorted) > 1 else D_i
        wcet = int(max(j["execution_time"] for j in jobs_sorted))
        bcet = int(min(j["execution_time"] for j in jobs_sorted))

        tasks.append(Task(id=tid, name=f"tau_{tid}", bcet=bcet, wcet=wcet,
                          period=T_i, deadline=D_i))

    return TaskSet(tasks)
