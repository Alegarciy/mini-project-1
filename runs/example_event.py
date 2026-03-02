"""
example_event.py
----------------
Demonstrates Event model: types, ordering, heap mechanics,
and the stale completion problem.

Uses Buttazzo Table 4.3:
    τ_0: C=1, T=4, D=3
    τ_1: C=1, T=5, D=4
    τ_2: C=2, T=6, D=5
    τ_3: C=1, T=11, D=10

Run:
    python example_event.py

@Author: AI GENERATED SCRIPT
"""

import sys
import heapq
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.simulation.event import Event, EventType

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
#  EVENT TYPES — COMPLETION(0) < ARRIVAL(1) < DEADLINE(2)
# =========================================================================

header("EVENT TYPES AND PRIORITY VALUES")

for et in EventType:
    color = {
        EventType.COMPLETION: GREEN,
        EventType.ARRIVAL: CYAN,
        EventType.DEADLINE: MAGENTA,
    }[et]
    print(f"  {color}{et.name:<12}{RESET}  value = {BOLD}{et.value}{RESET}")

print(f"\n  {DIM}Lower value = processed first on time ties{RESET}")
print(f"  {DIM}COMPLETION before ARRIVAL prevents ghost-job bug{RESET}")

# =========================================================================
#  EVENT CREATION
# =========================================================================

header("EVENT CREATION")

arrival = Event(time=0.0, event_type=EventType.ARRIVAL, task_id=0)
completion = Event(time=1.0, event_type=EventType.COMPLETION, task_id=0, job_id=1)
deadline = Event(time=3.0, event_type=EventType.DEADLINE, task_id=0, job_id=1)

print(f"  {CYAN}{arrival}{RESET}")
print(f"  {GREEN}{completion}{RESET}")
print(f"  {MAGENTA}{deadline}{RESET}")

print(f"\n  {DIM}Events compare as tuples: (time, event_type, task_id){RESET}")
print(f"  {DIM}@dataclass(order=True) enables < > == for heap sorting{RESET}")

# =========================================================================
#  EVENT ORDERING AT t=4 — WHY IT MATTERS
# =========================================================================

header("EVENT ORDERING AT t=4 — THREE SIMULTANEOUS EVENTS")

print(f"  {DIM}At t=4: τ_{{2,1}} finishes, τ_0 arrives, d_{{2,1}} checked{RESET}")

events = [
    Event(time=4.0, event_type=EventType.ARRIVAL, task_id=0),
    Event(time=4.0, event_type=EventType.DEADLINE, task_id=2, job_id=1),
    Event(time=4.0, event_type=EventType.COMPLETION, task_id=2, job_id=1),
]

print(f"\n  {BOLD}{WHITE}{'Unsorted (as generated)':<40}{RESET}")
print(f"  {DIM}{'─' * 50}{RESET}")
for e in events:
    print(f"  {YELLOW}{e}{RESET}")

sorted_events = sorted(events)

print(f"\n  {BOLD}{WHITE}{'Sorted (heap order)':<40}  {'priority'}{RESET}")
print(f"  {DIM}{'─' * 58}{RESET}")
for e in sorted_events:
    color = {
        EventType.COMPLETION: GREEN,
        EventType.ARRIVAL: CYAN,
        EventType.DEADLINE: MAGENTA,
    }[e.event_type]
    print(f"  {color}{str(e):<48}{RESET}  {BOLD}{e.event_type.value}{RESET}")

print(f"\n  {DIM}Processing order:{RESET}")
print(f"  {GREEN}1. COMPLETION(τ_{{2,1}}){RESET} {DIM}→ record f_{{2,1}}, free processor{RESET}")
print(f"  {CYAN}2. ARRIVAL(τ_0){RESET}       {DIM}→ create τ_{{0,2}}, call _schedule(){RESET}")
print(f"  {MAGENTA}3. DEADLINE(τ_{{2,1}}){RESET}  {DIM}→ check feasibility (already done ✓){RESET}")

# =========================================================================
#  HEAP WALKTHROUGH — FIRST 2 POPS (DM, Table 4.3)
# =========================================================================

header("HEAP WALKTHROUGH — INITIAL STATE (DM, Table 4.3)")

heap: list[Event] = []
tasks_info = [
    {"id": 0, "C": 1, "T": 4, "D": 3},
    {"id": 1, "C": 1, "T": 5, "D": 4},
    {"id": 2, "C": 2, "T": 6, "D": 5},
    {"id": 3, "C": 1, "T": 11, "D": 10},
]

for t in tasks_info:
    heapq.heappush(
        heap, Event(time=0.0, event_type=EventType.ARRIVAL, task_id=t["id"])
    )

print(f"  {DIM}Synchronous activation: all Φ_i = 0 (critical instant){RESET}")
print(f"\n  {BOLD}{WHITE}Initial heap ({len(heap)} events){RESET}")
print(f"  {DIM}{'─' * 50}{RESET}")
for e in sorted(heap):
    print(f"  {CYAN}{e}{RESET}")

# Pop #1
first = heapq.heappop(heap)
print(f"\n  {BOLD}{YELLOW}Pop #{1}{RESET} → {CYAN}{first}{RESET}")
print(f"  {DIM}τ_0 arrives → create τ_{{0,1}}, push 3 new events:{RESET}")

heapq.heappush(
    heap, Event(time=1.0, event_type=EventType.COMPLETION, task_id=0, job_id=1)
)
heapq.heappush(
    heap, Event(time=3.0, event_type=EventType.DEADLINE, task_id=0, job_id=1)
)
heapq.heappush(heap, Event(time=4.0, event_type=EventType.ARRIVAL, task_id=0))

print(f"    {GREEN}COMPLETION(τ_{{0,1}}) at t=1{RESET}")
print(f"    {MAGENTA}DEADLINE(τ_{{0,1}})   at t=3{RESET}")
print(f"    {CYAN}ARRIVAL(τ_0)       at t=4{RESET}")

print(f"\n  {BOLD}{WHITE}Heap now ({len(heap)} events){RESET}")
print(f"  {DIM}{'─' * 50}{RESET}")
for e in sorted(heap):
    color = {
        EventType.COMPLETION: GREEN,
        EventType.ARRIVAL: CYAN,
        EventType.DEADLINE: MAGENTA,
    }[e.event_type]
    print(f"  {color}{e}{RESET}")

# Pop #2
second = heapq.heappop(heap)
print(f"\n  {BOLD}{YELLOW}Pop #{2}{RESET} → {CYAN}{second}{RESET}")
print(f"  {DIM}Still t=0 — remaining arrivals processed in task_id order{RESET}")

# =========================================================================
#  STALE COMPLETION EVENTS
# =========================================================================

header("STALE COMPLETION EVENTS — WHY THE GUARD EXISTS")

print(f"  {DIM}When a job is preempted, its old COMPLETION stays in the heap.{RESET}")
print(f"  {DIM}If it resumes later, a NEW COMPLETION is pushed → two in heap.{RESET}")

stale_heap: list[Event] = []

print(f"\n  {BOLD}{WHITE}{'time':<8}  {'action':<50}{RESET}")
print(f"  {DIM}{'─' * 58}{RESET}")

# t=2: job starts
heapq.heappush(
    stale_heap,
    Event(time=4.0, event_type=EventType.COMPLETION, task_id=2, job_id=1),
)
print(
    f"  {CYAN}t=2{RESET}     "
    f"τ_{{2,1}} starts, push {YELLOW}COMPLETION at t=4{RESET}  "
    f"{RED}← will become stale{RESET}"
)

# t=3: preempted
print(
    f"  {CYAN}t=3{RESET}     "
    f"τ_{{2,1}} preempted, remaining: {YELLOW}2 → 1{RESET}  "
    f"{DIM}(COMPLETION t=4 still in heap){RESET}"
)

# t=5: resumes
heapq.heappush(
    stale_heap,
    Event(time=6.0, event_type=EventType.COMPLETION, task_id=2, job_id=1),
)
print(
    f"  {CYAN}t=5{RESET}     "
    f"τ_{{2,1}} resumes, push {GREEN}COMPLETION at t=6{RESET}  "
    f"{GREEN}← real one{RESET}"
)

print(f"\n  {BOLD}{WHITE}Heap now — two completions for same job:{RESET}")
print(f"  {DIM}{'─' * 58}{RESET}")
for e in sorted(stale_heap):
    if e.time == 4.0:
        print(f"  {RED}{e}  ← STALE ✗{RESET}")
    else:
        print(f"  {GREEN}{e}  ← VALID ✓{RESET}")

print(f"\n  {BOLD}{WHITE}_handle_completion guard:{RESET}")
print(f"  {DIM}expected = running_since + remaining{RESET}")

print(f"\n  {RED}t=4:{RESET}  expected = 5.0 + 1.0 = {CYAN}6.0{RESET}")
print(f"        event.time = {CYAN}4.0{RESET}")
print(f"        6.0 ≠ 4.0 → {RED}STALE, return early{RESET}")

print(f"\n  {GREEN}t=6:{RESET}  expected = 5.0 + 1.0 = {CYAN}6.0{RESET}")
print(f"        event.time = {CYAN}6.0{RESET}")
print(f"        6.0 = 6.0 → {GREEN}VALID, record f_{{2,1}} = 6.0 ✓{RESET}")

# =========================================================================
#  EVENT LIFECYCLE SUMMARY
# =========================================================================

header("EVENT LIFECYCLE SUMMARY")

print(f"""
  {BOLD}{CYAN}ARRIVAL{RESET}        {DIM}→ created at r_{{i,j}} = Φ_i + (j-1)·T_i{RESET}
  {DIM}                 creates Job, pushes COMPLETION + DEADLINE{RESET}
  {DIM}                 schedules next ARRIVAL at r_{{i,j+1}}{RESET}
  {DIM}                 calls _schedule() for preemption check{RESET}

  {BOLD}{GREEN}COMPLETION{RESET}     {DIM}→ created at r_{{i,j}} + remaining_time{RESET}
  {DIM}                 may be STALE after preemption (guard filters){RESET}
  {DIM}                 records f_{{i,j}}, frees processor{RESET}
  {DIM}                 calls _schedule() for next job{RESET}

  {BOLD}{MAGENTA}DEADLINE{RESET}       {DIM}→ created at d_{{i,j}} = r_{{i,j}} + D_i{RESET}
  {DIM}                 pure observer — no state change{RESET}
  {DIM}                 hook for logging/abort extensions{RESET}
""")

print()
