"""
response_times.py
-----------------
02225 DRTS — Mini-Project 1
Load a simulation log and plot avg/max response times per task.

Usage:
    python -m plots.response_times                          # uses latest log in logs/
    python -m plots.response_times --timestamp 20260324_180425 --algorithm DM
"""

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt

from analysis.log_loader import load_logs


def _latest_timestamp(log_dir: Path, algorithm: str) -> str:
    pattern = re.compile(rf"all_jobs_{algorithm}_(\d{{8}}_\d{{6}})\.csv")
    timestamps = [
        m.group(1)
        for f in log_dir.iterdir()
        if (m := pattern.match(f.name))
    ]
    if not timestamps:
        raise FileNotFoundError(f"No {algorithm} logs found in {log_dir}")
    return sorted(timestamps)[-1]


def plot_response_times(logs: dict, algorithm: str, timestamp: str):
    jobs = [j for j in logs["all_jobs"] if j["response_time"] is not None]

    by_task: dict[int, list[float]] = {}
    for j in jobs:
        by_task.setdefault(j["task_id"], []).append(j["response_time"])

    task_ids = sorted(by_task)
    avg_rt = [sum(by_task[t]) / len(by_task[t]) for t in task_ids]
    max_rt = [max(by_task[t]) for t in task_ids]
    labels = [f"τ_{t}" for t in task_ids]

    x = range(len(task_ids))
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar([i - 0.2 for i in x], avg_rt, width=0.4, label="avg R_i")
    ax.bar([i + 0.2 for i in x], max_rt, width=0.4, label="max R_i")

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_xlabel("Task")
    ax.set_ylabel("Response time (time units)")
    ax.set_title(f"{algorithm} — Response times  [{timestamp}]")
    ax.legend()
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-dir",   default="logs/")
    parser.add_argument("--algorithm", default="DM", choices=["DM", "EDF"])
    parser.add_argument("--timestamp", default=None)
    args = parser.parse_args()

    log_dir = Path(args.log_dir)
    ts = args.timestamp or _latest_timestamp(log_dir, args.algorithm)

    logs = load_logs(log_dir, algorithm=args.algorithm, timestamp=ts)
    plot_response_times(logs, algorithm=args.algorithm, timestamp=ts)
