# Mini-Project 1 — 02225 Distributed Real-Time Systems

<p align="center">
  <img src="https://www.dtu.dk/-/media/dtudk/om-dtu/campus/dtu_logo_corporate_red_rgb.png"
       alt="DTU Logo" width="260" />
</p>

<p align="center">
  <strong>Course:</strong> 02225 — Distributed Real-Time Systems &nbsp;|&nbsp;
  <strong>Institution:</strong> Technical University of Denmark (DTU)
</p>

<p align="center">
  <strong>Collaborators:</strong>
  Alejandro Garcia Bejarano &nbsp;·&nbsp;
  Marco Cola &nbsp;·&nbsp;
  Alexandru Jurj &nbsp;·&nbsp;
  Dumitrita Macarenco &nbsp;·&nbsp;
  Farhiya Mohamoud Adan Yusuf &nbsp;·&nbsp;
</p>

<p align="center">
  <a href="https://www.overleaf.com/read/qjbbwgrktjdr#6bb4c4">
    📄 Overleaf Report
  </a>
</p>

---

## Table of Contents

- [Section 1.0 — Quick Start](#10--quick-start)
- [Section 2.0 — Example Runs](#20--example-runs)
- [Section 3.0 — Log File Structure](#30--log-file-structure)
- [Section 4.0 — Building a Custom Dataset](#40--building-a-custom-dataset)
- [Section 5.0 — Logs & Notebooks](#50--logs--notebooks)

---

## Project Structure

```
mini-project-1/
├── main.py                        # CLI entry point
├── requirements.txt               # Python dependencies
├── examples/                      # Sample task set CSVs
├── examples_modeling/             # Standalone model demos
├── models/
│   ├── scheduling/                # Task, Job, TaskSet dataclasses
│   └── simulation/                # Event types & structures
├── simulation/
│   └── engine.py                  # Event-driven simulator (DM / EDF)
├── analysis/
│   ├── response_time_analysis.py  # DM RTA + EDF DBF analysis
│   ├── workload_analyzer.py       # Workload & demand bound functions
│   └── log_loader.py              # Load simulation CSVs back into memory
├── plots/
│   ├── response_times.py          # Bar chart: avg/max response times
│   └── workload_staircase.py      # W(t) staircase plot
├── taskset_files/
│   ├── automotive/                # Real automotive task sets (0.10–1.00 util)
│   └── uunifast/                  # Synthetic UUniFast task sets (0.10–1.00 util)
└── notebooks/                     # Jupyter analysis notebooks
```

### Notation (Buttazzo Chapter 4)

| Symbol | Meaning |
|--------|---------|
| `Γ` | Task set `{τ_1, ..., τ_n}` |
| `τ_i` | Periodic task |
| `C_i` | Worst-Case Execution Time (WCET) |
| `T_i` | Period |
| `D_i` | Relative deadline (`C_i ≤ D_i ≤ T_i`) |
| `Φ_i` | Phase (release time of first instance) |
| `H` | Hyperperiod = `lcm(T_1, ..., T_n)` |
| `U` | Processor utilization = `Σ C_i / T_i` |
| `R_i` | Worst-case response time of `τ_i` |
| `τ_{i,j}` | j-th job instance of `τ_i` |
| `r_{i,j}` | Release time of `τ_{i,j}` |
| `d_{i,j}` | Absolute deadline = `r_{i,j} + D_i` |
| `R_{i,j}` | Response time = `f_{i,j} - r_{i,j}` |

---

## 1.0 — Quick Start

### Python Version

Python **3.13** is recommended. Download from [python.org](https://www.python.org/downloads/).

### Virtual Environment

```bash
# Create the venv
python3.13 -m venv .venv

# Activate (macOS / Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Running the Simulator

```bash
python main.py --taskset <path/to/taskset.csv> [OPTIONS]
```

#### Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--taskset` | `str` | *(required)* | Path to the task set CSV file |
| `--use-wcet` | flag | `False` | Always use WCET (deterministic, no jitter) |
| `--log-dir` | `str` | `None` | Directory to save simulation CSV logs |

### Task Set File Locations

Pre-built task sets are organised by benchmark family and utilisation level:

```
taskset_files/
├── automotive/
│   ├── 0.10-util/    ← ~100 files: automotive_0.csv … automotive_99.csv
│   ├── 0.20-util/
│   ├── ...
│   └── 1.00-util/
└── uunifast/
    ├── 0.10-util/    ← ~100 files: uniform-discrete_0.csv … uniform-discrete_99.csv
    ├── 0.20-util/
    ├── ...
    └── 1.00-util/
```

---

## 2.0 — Example Runs

The commands below run the full analytical + simulation pipeline for automotive task sets at three representative utilisation levels. Logs are saved to `logs/`.

### Automotive — 10% utilisation

```bash
python main.py \
  --taskset taskset_files/automotive/0.10-util/automotive_0.csv \
  --log-dir logs/my_run
```

### Automotive — 50% utilisation

```bash
python main.py \
  --taskset taskset_files/automotive/0.50-util/automotive_0.csv \
  --log-dir logs/my_run
```

### Automotive — 90% utilisation

```bash
python main.py \
  --taskset taskset_files/automotive/0.90-util/automotive_0.csv \
  --log-dir logs/my_run
```

> **Tip:** add `--use-wcet` to any command for a fully deterministic run (no random execution-time sampling).

---

## 3.0 — Log File Structure

Each run with `--log-dir` produces **four CSV files per algorithm** (DM and EDF) inside the target directory:

```
logs/my_run/
├── schedule_trace_DM_<timestamp>.csv
├── preemption_log_DM_<timestamp>.csv
├── all_jobs_DM_<timestamp>.csv
├── completed_jobs_DM_<timestamp>.csv
├── schedule_trace_EDF_<timestamp>.csv
├── preemption_log_EDF_<timestamp>.csv
├── all_jobs_EDF_<timestamp>.csv
└── completed_jobs_EDF_<timestamp>.csv
```

---

### `all_jobs_DM` / `all_jobs_EDF`

Every job instance released during the simulation, regardless of whether it completed or missed its deadline.

| Column | Type | Description |
|--------|------|-------------|
| `task_id` | `int` | Task index |
| `job_id` | `int` | Instance index within the task |
| `release_time` | `float` | Activation time |
| `absolute_deadline` | `float` | Hard deadline (`release_time + D_i`) |
| `execution_time` | `float` | Execution time used for this instance |
| `remaining_time` | `float` | Remaining execution time at end of simulation |
| `start_time` | `float \| None` | First time the job ran on CPU (`None` if never started) |
| `finish_time` | `float \| None` | Completion time (`None` if not completed) |
| `preemtion_count` | `int` | Number of times the job was preempted |
| `response_time` | `float \| None` | `finish_time - release_time` (`None` if missed) |
| `missed_deadline` | `bool` | `True` if the job exceeded its deadline |
| `is_completed` | `bool` | `True` if the job finished before its deadline |

---

### `completed_jobs_DM` / `completed_jobs_EDF`

Same schema as `all_jobs`, filtered to only rows where `is_completed = True`. Useful for response-time analysis without having to filter manually.

---

### `schedule_trace_DM` / `schedule_trace_EDF`

A slot-by-slot record of which task held the CPU at each point in time.

| Column | Type | Description |
|--------|------|-------------|
| `start` | `float` | Start of the CPU slot |
| `end` | `float` | End of the CPU slot |
| `task_id` | `int` | Task that ran during `[start, end)` |

---

### `preemption_log_DM` / `preemption_log_EDF`

One row per preemption event. Each row contains the timestamp plus a full snapshot of both the preempted job and the job that caused the preemption, using the `preempted_` and `by_` column prefixes respectively.

| Column | Type | Description |
|--------|------|-------------|
| `time` | `float` | Simulation time at which the preemption occurred |
| `preempted_task_id` | `int` | Task ID of the preempted job |
| `preempted_job_id` | `int` | Job ID of the preempted job |
| `preempted_release_time` | `float` | Release time of the preempted job |
| `preempted_response_time` | `float \| None` | Response time if already completed, else `None` |
| `preempted_remaining_time` | `float` | Remaining execution time at preemption |
| `preempted_missed_deadline` | `bool` | Whether the preempted job eventually missed its deadline |
| `by_task_id` | `int` | Task ID of the preempting job |
| `by_job_id` | `int` | Job ID of the preempting job |
| `by_release_time` | `float` | Release time of the preempting job |
| `by_remaining_time` | `float` | Remaining execution time of the preempting job |
| *(+ all other `by_` fields)* | | Same fields as `preempted_*` for the preempting job |

---

## 4.0 — Building a Custom Dataset

### CSV Format

Task set files follow a simple tabular format. Each row represents one periodic task:

```csv
TaskID,Jitter,BCET,WCET,Period,Deadline,PE
T0,0,100,500,1000,1000,0
T1,0,200,800,2000,2000,0
T2,0,50,200,4000,4000,0
```

| Column | Description |
|--------|-------------|
| `TaskID` | Task label (e.g. `T0`, `T1`, …) |
| `Jitter` | Activation jitter — set to `0` for standard periodic tasks |
| `BCET` | Best-Case Execution Time |
| `WCET` | Worst-Case Execution Time |
| `Period` | Task period `T_i` |
| `Deadline` | Relative deadline `D_i` (typically equal to `Period`) |
| `PE` | Processing element — use `0` for single-processor |

> Constraints: `BCET ≤ WCET`, `WCET ≤ Deadline ≤ Period`.

Save your file anywhere convenient, for example `examples/my_taskset.csv`.

### Running Your Own Task Set

```bash
python main.py \
  --taskset examples/my_taskset.csv \
  --log-dir logs/my_run
```

### Generating Task Sets Programmatically

For large-scale experiments you can generate task sets automatically using the
[real-time-task-generators](https://github.com/porya-gohary/real-time-task-generators?tab=readme-ov-file)
repository by Pouya Gohary.
It supports UUniFast, RandFixedSum, and automotive benchmark generators
and exports files in the same CSV format used here.

---

## 5.0 — Logs & Notebooks

### How Logs Are Registered and Stored

Every time you pass `--log-dir`, the simulator writes **four CSV files** per algorithm per replication into that directory:

```
logs/my_run/
├── schedule_trace_DM_20260327_140000.csv       # (start, end, task_id) per slot
├── preemption_log_DM_20260327_140000.csv       # every preemption event
├── all_jobs_DM_20260327_140000.csv             # every job (complete or not)
├── completed_jobs_DM_20260327_140000.csv       # only finished jobs
├── schedule_trace_EDF_20260327_140000.csv
├── preemption_log_EDF_20260327_140000.csv
├── all_jobs_EDF_20260327_140000.csv
└── completed_jobs_EDF_20260327_140000.csv
```

#### Job log fields

| Field | Description |
|-------|-------------|
| `task_id` | Task index |
| `job_id` | Instance index within the task |
| `release_time` | Activation time |
| `absolute_deadline` | Hard deadline |
| `execution_time` | Sampled execution time for this instance |
| `start_time` | First time the job ran on CPU |
| `finish_time` | Completion time (`None` if not completed) |
| `preemtion_count` | Number of times the job was preempted |
| `response_time` | `finish_time - release_time` (`None` if missed) |
| `missed_deadline` | `True` if the job exceeded its deadline |
| `is_completed` | `True` if the job finished |

### Loading Logs in Python

Use the `log_loader` utility from `analysis/log_loader.py` to bring logs back into memory for custom analysis:

```python
from analysis.log_loader import load_logs

logs = load_logs(
    log_dir="logs/my_run",
    algorithm="DM",
    timestamp="20260327_140000",
    # replication=1   # uncomment for multi-replication runs
)

# logs["schedule_trace"]  → list of {start, end, task_id}
# logs["preemption_log"]  → list of {time, preempted: job_dict, by: job_dict}
# logs["all_jobs"]        → list of job dicts
# logs["completed_jobs"]  → list of job dicts

# Example: all deadline misses for task 0
misses = [j for j in logs["all_jobs"] if j["task_id"] == 0 and j["missed_deadline"]]

# Example: scheduling slots longer than 5 time units
long_slots = [s for s in logs["schedule_trace"] if s["end"] - s["start"] > 5]
```

### Building Your Own Notebook

The `notebooks/` directory contains the analysis notebooks for this project.
To create a new notebook:

1. Activate your venv and launch Jupyter:

```bash
source .venv/bin/activate
jupyter notebook          # or: jupyter lab
```

2. Create a new notebook inside `notebooks/`.

3. Use the standard import pattern at the top of your notebook to ensure Python can resolve the project modules:

```python
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path.cwd().parent))

from analysis.log_loader import load_logs
import pandas as pd
import matplotlib.pyplot as plt
```

4. Load a log and start exploring:

```python
logs = load_logs("../logs/my_run", algorithm="DM", timestamp="20260327_140000")
df   = pd.DataFrame(logs["all_jobs"])

df.groupby("task_id")["response_time"].describe()
```

> **Note:** `*.ipynb` files are tracked in this repository. Do not commit notebooks that contain large embedded outputs — clear cell outputs before committing (`Kernel → Restart & Clear Output`).
