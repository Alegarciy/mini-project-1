"""
example_taskset.py
------------------
Demonstrates TaskSet (Γ) construction, properties, and CSV loading.
Run:
    python example_taskset.py
    python example_taskset.py --csv path/to/taskset.csv

@Author: AI GENERATED SCRIPT
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.scheduling.task import Task
from models.scheduling.taskset import TaskSet

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
#  TASK SET CONSTRUCTION (Buttazzo §4.1)
# =========================================================================

header("TASK SET Γ — MANUAL CONSTRUCTION")

tasks = [
    Task(id=0, name="T0", bcet=1, wcet=1, period=4, deadline=4),
    Task(id=1, name="T1", bcet=1, wcet=2, period=6, deadline=6),
    Task(id=2, name="T2", bcet=2, wcet=3, period=12, deadline=12),
]

gamma = TaskSet(tasks)
print(f"  {BOLD}{YELLOW}{gamma}{RESET}")

# =========================================================================
#  SET-LEVEL PROPERTIES (Section 4.1)
# =========================================================================

header("SET PROPERTIES")

label("n  (|Γ|)              ", f"{gamma.n}", CYAN)
label("U  (Σ C_i / T_i)     ", f"{gamma.utilization:.4f}")
label("H  (lcm of periods)  ", f"{gamma.hyperperiod}", CYAN)
label("D_max                 ", f"{gamma.D_max}", MAGENTA)
label(
    "Constrained? ∃ D_i<T_i",
    f"{gamma.has_constrained_deadlines}",
    RED if gamma.has_constrained_deadlines else GREEN,
)

# =========================================================================
#  PER-TASK BREAKDOWN
# =========================================================================

header("TASKS IN Γ")

print(f"\n  {BOLD}{WHITE}{'τ_i':<28}  {'U_i':<10}{RESET}")
print(f"  {DIM}{'─' * 40}{RESET}")

for t in gamma:
    print(f"  {YELLOW}{t}{RESET}  {GREEN}{t.utilization:.4f}{RESET}")

# =========================================================================
#  SCHEDULING PRIORITY ORDERS
# =========================================================================

header("RATE MONOTONIC ORDER (shortest T_i first)")

print(f"\n  {BOLD}{WHITE}{'rank':<6}  {'τ_i':<28}  {'T_i':<6}{RESET}")
print(f"  {DIM}{'─' * 44}{RESET}")

for rank, t in enumerate(gamma.sorted_by_period(), start=1):
    print(
        f"  {CYAN}{rank:<6}{RESET}  {YELLOW}{str(t):<28}{RESET}  "
        f"{GREEN}{t.period}{RESET}"
    )

header("DEADLINE MONOTONIC ORDER (shortest D_i first)")

print(f"\n  {BOLD}{WHITE}{'rank':<6}  {'τ_i':<28}  {'D_i':<6}{RESET}")
print(f"  {DIM}{'─' * 44}{RESET}")

for rank, t in enumerate(gamma.sorted_by_deadline(), start=1):
    print(
        f"  {CYAN}{rank:<6}{RESET}  {YELLOW}{str(t):<28}{RESET}  "
        f"{MAGENTA}{t.deadline}{RESET}"
    )

# =========================================================================
#  LIU & LAYLAND BOUND (Section 4.3.3, Eq. 4.9)
# =========================================================================

header("LIU & LAYLAND BOUND — U_lub = n(2^(1/n) - 1)")

n = gamma.n
ll_bound = n * (2 ** (1 / n) - 1)

label("U_lub                 ", f"{ll_bound:.4f}", CYAN)
label("U                     ", f"{gamma.utilization:.4f}")

if gamma.utilization <= ll_bound:
    print(f"\n  {GREEN}✓ U ≤ U_lub → schedulable by RM/DM{RESET}")
else:
    print(f"\n  {RED}✗ U > U_lub → inconclusive (need RTA){RESET}")

# =========================================================================
#  OPTIONAL: LOAD FROM CSV
# =========================================================================

header("LOAD CSV EXAMPLE")

p = Path('../')
for subdir in p.iterdir():
    if subdir.is_dir():
        print(subdir)

if "--csv" in sys.argv:
    csv_path = Path('./examples/' + sys.argv[sys.argv.index("--csv") + 1])

    header(f"CSV LOADING — {csv_path}")

    gamma_csv = TaskSet.from_csv(csv_path)
    print(f"  {BOLD}{YELLOW}{gamma_csv}{RESET}")

    print(f"\n  {BOLD}{WHITE}{'τ_i':<28}  {'U_i':<10}{RESET}")
    print(f"  {DIM}{'─' * 40}{RESET}")
    for t in gamma_csv:
        print(f"  {YELLOW}{t}{RESET}  {GREEN}{t.utilization:.4f}{RESET}")

    n_csv = gamma_csv.n
    ll_csv = n_csv * (2 ** (1 / n_csv) - 1)

    print()
    label("U                     ", f"{gamma_csv.utilization:.4f}")
    label("U_lub                 ", f"{ll_csv:.4f}", CYAN)

    if gamma_csv.utilization <= ll_csv:
        print(f"\n  {GREEN}✓ U ≤ U_lub → schedulable by RM/DM{RESET}")
    else:
        print(f"\n  {RED}✗ U > U_lub → inconclusive (need RTA){RESET}")

print()
