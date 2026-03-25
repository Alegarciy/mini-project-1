"""
main.py
-------
02225 DRTS — Mini-Project 1
Entry point: loads task set, runs DM/EDF simulations, prints results.

Run:
    python main.py --taskset path/to/taskset.csv
    python main.py --taskset path/to/taskset.csv --use-wcet
    python main.py --taskset path/to/taskset.csv --replications 5 --seed 42

@Author: Alejandro Garcia Bejarano + AI Generated Assistance
"""

import argparse
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.scheduling.taskset import TaskSet
from simulation.engine import SimulationEngine

# TODO: Code the analysis
# from analysis.dm_analysis import (
#     perform_dm_analysis,
#     check_ll_bound,
#     check_hyperbolic_bound
# )

# =========================================================================
#  ANSI Colors
# =========================================================================

BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
WHITE = "\033[37m"
BG_BLUE = "\033[40m"


def header(text):
    print(f"\n{BOLD}{BG_BLUE}{WHITE} {text} {RESET}")


def label(name, value, color=GREEN):
    print(f"  {DIM}{name}{RESET} = {color}{value}{RESET}")


# =========================================================================
#  EVALUATE THE DATASET ANALYTICALLY
# =========================================================================

# TODO: Evaluate the dataset analytically


# =========================================================================
#  SIMULATION PHASE
# =========================================================================


def _save_logs(engine, algorithm: str, log_dir: Path, timestamp: str, rep_suffix: str):
    """
    Write the four simulation logs to log_dir as CSV files.
    Filenames: {log_type}_{algorithm}_{timestamp}{rep_suffix}.csv

    @Author: Claude Generated
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    base = f"{algorithm}_{timestamp}{rep_suffix}"

    JOB_FIELDS = [
        "task_id", "job_id", "release_time", "absolute_deadline",
        "execution_time", "remaining_time", "start_time", "finish_time",
        "preemtion_count", "response_time", "missed_deadline", "is_completed",
    ]

    def job_to_row(job):
        d = asdict(job)
        d["response_time"] = job.response_time
        d["missed_deadline"] = job.missed_deadline
        d["is_completed"] = job.is_completed
        return d

    # schedule_trace
    pd.DataFrame(
        [{"start": s, "end": e, "task_id": tid} for s, e, tid in engine.schedule_trace]
    ).to_csv(log_dir / f"schedule_trace_{base}.csv", index=False)

    # preemption_log — flatten preempted/by job fields with a prefix
    preemption_rows = []
    for t, pj, bj in engine.preemption_log:
        row = {"time": t}
        row.update({f"preempted_{k}": v for k, v in job_to_row(pj).items()})
        row.update({f"by_{k}": v for k, v in job_to_row(bj).items()})
        preemption_rows.append(row)
    pd.DataFrame(preemption_rows).to_csv(log_dir / f"preemption_log_{base}.csv", index=False)

    # all_jobs / completed_jobs
    pd.DataFrame([job_to_row(j) for j in engine.all_jobs])[JOB_FIELDS].to_csv(
        log_dir / f"all_jobs_{base}.csv", index=False
    )
    pd.DataFrame([job_to_row(j) for j in engine.completed_jobs])[JOB_FIELDS].to_csv(
        log_dir / f"completed_jobs_{base}.csv", index=False
    )


def run_simulation(
    taskset: TaskSet,
    algorithm: str,
    num_replication: int = 1,
    seed: int = 14,
    use_wcet: bool = False,
    log_dir: Optional[Path] = None,
    timestamp: str = "",
) -> dict:
    """
    Run simulation for a given algorithm with optional replications.

    @Returns: aggregated statistics per task
    @Author: Alejandro Garcia Bejarano + AI Generated Assistance
    """
    all_R_i: dict[int, list[float]] = {t.id: [] for t in taskset}
    all_missed: dict[int, int] = {t.id: 0 for t in taskset}

    # This replication loop is if we wanted
    # to experiment with jitter
    for rep in range(num_replication):
        engine = SimulationEngine(
            taskset=taskset,
            algorithm=algorithm,
            seed=seed + rep,
            use_wcet=use_wcet,
        )
        engine.run()
        stats = engine.get_statistics()

        if log_dir is not None:
            rep_suffix = f"_rep{rep + 1}" if num_replication > 1 else ""
            _save_logs(engine, algorithm, log_dir, timestamp, rep_suffix)

        for tid, s in stats.items():
            all_R_i[tid].append(s["R_i"])
            all_missed[tid] += s["missed"]

    aggregated = {}
    for task in taskset:
        wcrts = all_R_i[task.id]
        aggregated[task.id] = {
            "max_R_i": max(wcrts) if wcrts else 0.0,
            "avg_R_i": sum(wcrts) / len(wcrts) if wcrts else 0.0,
            "min_R_i": min(wcrts) if wcrts else 0.0,
            "total_missed": all_missed[task.id],
        }

    return aggregated


# =========================================================================
#  START PROGRAM
# =========================================================================


def main():
    parser = argparse.ArgumentParser(description="02225 DRTS — Mini-Project 1")
    parser.add_argument("--taskset", required=True, help="Path to task set CSV")
    parser.add_argument(
        "--replications",
        type=int,
        default=1,
        help="Number of simulation replications",
    )
    parser.add_argument("--seed", type=int, default=42, help="Base random seed")
    parser.add_argument(
        "--use-wcet",
        action="store_true",
        help="Always use WCET (no randomness, for validation)",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=None,
        help="Directory to store simulation logs (schedule_trace, preemption_log, all_jobs, completed_jobs)",
    )
    args = parser.parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── 1. Load Γ ──
    taskset = TaskSet.from_csv(args.taskset)

    # ── 2. Simulation ──
    mode = "WCET" if args.use_wcet else f"random (seed={args.seed})"

    run_simulation(
        taskset, "DM", args.replications, args.seed, args.use_wcet,
        log_dir=args.log_dir, timestamp=timestamp,
    )
    run_simulation(
        taskset, "EDF", args.replications, args.seed, args.use_wcet,
        log_dir=args.log_dir, timestamp=timestamp,
    )

if __name__ == "__main__":
    main()
