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

from pathlib import Path

import pandas as pd

from models.scheduling.task import Task
from models.scheduling.taskset import TaskSet


_JOB_FIELDS = [
    "task_id", "job_id", "release_time", "absolute_deadline",
    "execution_time", "remaining_time", "start_time", "finish_time",
    "preemtion_count", "response_time", "missed_deadline", "is_completed",
]

# These fields are legitimately absent (None) before a job starts/finishes
_NULLABLE = {"start_time", "finish_time", "response_time"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _jobs_df_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert a job DataFrame to list-of-dicts, preserving None for nullable fields."""
    for col in ("task_id", "job_id", "preemtion_count"):
        df[col] = df[col].astype(int)
    records = df.to_dict("records")
    for row in records:
        for k in _NULLABLE:
            if pd.isna(row[k]):
                row[k] = None
    return records


def _parse_job_cols(row: pd.Series, prefix: str) -> dict:
    """Extract and type-cast a prefixed job block from a preemption-log row."""
    d = {k: row[f"{prefix}{k}"] for k in _JOB_FIELDS}
    for col in ("task_id", "job_id", "preemtion_count"):
        d[col] = int(d[col])
    for k in _NULLABLE:
        if pd.isna(d[k]):
            d[k] = None
    d["missed_deadline"] = bool(d["missed_deadline"])
    d["is_completed"] = bool(d["is_completed"])
    return d


# ── Loaders ───────────────────────────────────────────────────────────────────

def _load_schedule_trace(path: Path) -> list[dict]:
    df = pd.read_csv(path)
    df["task_id"] = df["task_id"].astype(int)
    return df.to_dict("records")


def _load_preemption_log(path: Path) -> list[dict]:
    df = pd.read_csv(path, true_values=["True"], false_values=["False"])
    return [
        {
            "time":      row["time"],
            "preempted": _parse_job_cols(row, "preempted_"),
            "by":        _parse_job_cols(row, "by_"),
        }
        for _, row in df.iterrows()
    ]


def _load_jobs(path: Path) -> list[dict]:
    df = pd.read_csv(path, true_values=["True"], false_values=["False"])
    return _jobs_df_to_records(df)


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
    df = pd.DataFrame(logs["all_jobs"])

    tasks = []
    for tid, group in df.groupby("task_id"):
        group_sorted = group.sort_values("job_id")
        D_i  = int(group_sorted.iloc[0]["absolute_deadline"])
        T_i  = int(group_sorted.iloc[1]["release_time"]) if len(group_sorted) > 1 else D_i
        wcet = int(group["execution_time"].max())
        bcet = int(group["execution_time"].min())
        tasks.append(Task(id=tid, name=f"tau_{tid}", bcet=bcet, wcet=wcet,
                          period=T_i, deadline=D_i))

    return TaskSet(tasks)
