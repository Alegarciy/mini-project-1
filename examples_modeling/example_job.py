"""
example_job.py
--------------
Demonstrates Job (τ_{i,j}) lifecycle: creation, execution, preemption,
completion, and deadline misses.

Uses Buttazzo Table 4.3:
    τ_0: C=1, T=4, D=3
    τ_1: C=1, T=5, D=4
    τ_2: C=2, T=6, D=5
    τ_3: C=1, T=11, D=10

Run:
    python example_job.py

@Author: AI GENERATED SCRIPT
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.scheduling.job import Job

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
#  JOB CREATION — τ_{2,1}
# =========================================================================

header("JOB CREATION — τ_{2,1}")

# Task τ_2 has C=2, T=6, D=5. First instance released at t=0.
job = Job(
    task_id=2,
    job_id=1,                       # j=1 (Buttazzo 1-indexed)
    release_time=0.0,               # r_{2,1} = Φ_2 + (1-1)·T_2 = 0
    absolute_deadline=0.0 + 5.0,    # d_{2,1} = r_{2,1} + D_2 = 5
    execution_time=2.0,             # sampled from [BCET, WCET]
    remaining_time=2.0,             # all work ahead
)

print(f"  {BOLD}{YELLOW}{job}{RESET}")

label("r_{2,1}              ", f"{job.release_time}")
label("d_{2,1}              ", f"{job.absolute_deadline}", MAGENTA)
label("execution_time       ", f"{job.execution_time}", CYAN)
label("remaining_time       ", f"{job.remaining_time}", CYAN)
label("is_completed         ", f"{job.is_completed}", RED)
label("response_time        ", f"{job.response_time}", DIM)

# =========================================================================
#  JOB STARTS EXECUTING — s_{2,1} = 2
# =========================================================================

header("STARTS EXECUTING AT t=2")

print(f"  {DIM}After τ_0 and τ_1 finish, τ_{{2,1}} gets the processor{RESET}")

job.start_time = 2.0

label("s_{2,1}              ", f"{job.start_time}")

# =========================================================================
#  JOB PREEMPTION AT t=3
# =========================================================================

header("PREEMPTED AT t=3")

print(f"  {DIM}Higher-priority τ_0 arrives, τ_{{2,1}} loses the processor{RESET}")

elapsed = 3.0 - job.start_time  # ran for 1 unit
job.remaining_time -= elapsed
job.preemtion_count += 1

label("elapsed              ", f"{elapsed}", YELLOW)
label("remaining_time       ", f"{job.remaining_time}", CYAN)
label("preemption_count     ", f"{job.preemtion_count}", RED)

# =========================================================================
#  JOB RESUMES AND COMPLETES — f_{2,1} = 5
# =========================================================================

header("RESUMES AT t=4, COMPLETES AT t=5")

print(f"  {DIM}τ_0 finishes at t=4, τ_{{2,1}} resumes with remaining=1{RESET}")

job.finish_time = 5.0
job.remaining_time = 0.0

print(f"\n  {BOLD}{YELLOW}{job}{RESET}")

label("f_{2,1}              ", f"{job.finish_time}")
label("R_{2,1} = f - r      ", f"{job.response_time}")
label("is_completed         ", f"{job.is_completed}", GREEN)
label("missed_deadline      ", f"{job.missed_deadline}", GREEN)

print(f"\n  {GREEN}✓ f_{{2,1}}={job.finish_time} ≤ d_{{2,1}}={job.absolute_deadline} → on time{RESET}")

# =========================================================================
#  DEADLINE MISS — τ_{3,1}
# =========================================================================

header("DEADLINE MISS — τ_{3,1}")

print(f"  {DIM}Suppose τ_{{3,1}} suffers heavy interference, doesn't run until t=11{RESET}")

late_job = Job(
    task_id=3,
    job_id=1,
    release_time=0.0,
    absolute_deadline=10.0,         # d_{3,1} = 0 + D_3 = 10
    execution_time=1.0,
    remaining_time=1.0,
)

# Simulating late execution
late_job.start_time = 11.0
late_job.finish_time = 12.0
late_job.remaining_time = 0.0

print(f"  {BOLD}{YELLOW}{late_job}{RESET}")

label("d_{3,1}              ", f"{late_job.absolute_deadline}", MAGENTA)
label("f_{3,1}              ", f"{late_job.finish_time}", RED)
label("R_{3,1}              ", f"{late_job.response_time}", RED)
label("missed_deadline      ", f"{late_job.missed_deadline}", RED)
label("how late             ", f"{late_job.finish_time - late_job.absolute_deadline:.1f} time units", RED)

print(f"\n  {RED}✗ f_{{3,1}}={late_job.finish_time} > d_{{3,1}}={late_job.absolute_deadline} → missed by {late_job.finish_time - late_job.absolute_deadline:.0f}{RESET}")

# =========================================================================
#  TASK vs JOB — WHY BOTH EXIST
# =========================================================================

header("TASK vs JOB — CONCEPTUAL SUMMARY")

print(f"""
  {BOLD}{WHITE}Task (τ_i){RESET}                       {BOLD}{WHITE}Job (τ_{{i,j}}){RESET}
  {DIM}{'─' * 30}{RESET}      {DIM}{'─' * 30}{RESET}
  {DIM}Static template{RESET}                   {DIM}Runtime instance{RESET}
  {DIM}C_i, T_i, D_i fixed{RESET}               {DIM}r_{{i,j}}, d_{{i,j}} computed per job{RESET}
  {DIM}No state{RESET}                           {DIM}remaining_time, start, finish{RESET}
  {DIM}Analysis reasons about tasks{RESET}       {DIM}Simulation runs jobs{RESET}
  {DIM}One per task set{RESET}                   {DIM}Many per hyperperiod{RESET}
""")

print()
