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

from models.scheduling.task import Task

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
#  SINGLE TASK CONSTRUCTION
# =========================================================================
header("STANDARD TASK REPRESENTATION")

tau = Task(id=0, name="T0", bcet=1, wcet=3, period=10, deadline=10)
print(f"  {BOLD}{YELLOW}{tau}{RESET}")

label("Utilization U_i = C_i/T_i", f"{tau.utilization:.4f}")
label(
    "Constrained? D_i < T_i   ",
    f"{tau.has_contrained_deadline}",
    RED if tau.has_contrained_deadline else GREEN,
)

# =========================================================================
#   N SEQUENCING STEPS
# =========================================================================
header("TASK SEQUENCING EXAMPLE")
print(f"\n  {BOLD}{WHITE}{'k':<6}  {'r_{{i,k}}':<14}  {'d_{{i,k}}':<14}{RESET}")
print(f"  {DIM}{'─' * 36}{RESET}")

for k in range(1, 5):
    r = tau.release_time(k)
    d = tau.absolute_deadline_of(k)
    print(
        f"  {CYAN}{k:<6}{RESET}  {GREEN}{r:<14.1f}{RESET}  {MAGENTA}{d:<14.1f}{RESET}"
    )

# =========================================================================
#   CONSTRAINT DEADLINE EVALUATION
# =========================================================================
header("CONSTRAINED DEADLINE (D_i < T_i)")
tau_c = Task(id=1, name="T1", bcet=2, wcet=5, period=20, deadline=15)
print(f"  {BOLD}{YELLOW}{tau_c}{RESET}")

label(
    "Constrained? D_i < T_i ",
    f"{tau_c.has_contrained_deadline}",
    RED if tau_c.has_contrained_deadline else GREEN,
)

print(
    f"  {DIM}D_i={MAGENTA}15{DIM} < T_i= {GREEN}20{DIM} → "
    f"job must finish before deadline, not next period{RESET}"
)

# ── Validation guard ─────────────────────────────────────────────────────
header("VALIDATION: BCET > WCET")

try:
    bad = Task(id=99, name="T99", bcet=10, wcet=5, period=20, deadline=20)
except ValueError as e:
    print(f"  {RED}✗ Caught ValueError{RESET}")
    print(f"  {DIM}{e}{RESET}")

print()
