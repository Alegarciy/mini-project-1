import copy
from math import ceil
from math import floor
from math import lcm

from models.scheduling.taskset import TaskSet
from models.scheduling.task import Task

# ── ANSI ─────────────────────────────────────────────────────────────────────
_BOLD   = "\033[1m"
_DIM    = "\033[2m"
_RESET  = "\033[0m"
_CYAN   = "\033[36m"
_GREEN  = "\033[32m"
_YELLOW = "\033[33m"
_RED    = "\033[31m"
_MAGENTA= "\033[35m"
_WHITE  = "\033[37m"


def workload(taskset: TaskSet, schedule_type="DM"):
    if schedule_type == "DM":
        return workload_dm(taskset)
    else:  # EDF
        workload_edf(taskset)
        # taskset.sorted_by_period()
        return 0
    
def calculate_dbf(taskset, t: int):
    total = 0

    for task in taskset.tasks:
        C = task.wcet
        T = task.period
        D = task.deadline

        jobs = floor((t + T - D) / T)
        jobs = max(0, jobs) 

        total += jobs * C

    return total

def workload_EDF_helper(taskset):
    points = set()
    #max_t = lcm(*(task.period for task in taskset.tasks))
    max_t = sum(task.period for task in taskset.tasks)

    for task in taskset.tasks:
        k = 0
        while True:
            t = k * task.period + task.deadline 

            if t > max_t:
                break

            if t > 0:
                points.add(t)

            k += 1

    return sorted(points)

def edfGraph(taskset):
    points = workload_EDF_helper(taskset)
    graph = []

    for t in points:
        demand = calculate_dbf(taskset, t)
        graph.append((t, demand))  
        print(t, demand)

    return graph

def workload_edf(taskset):
    print("EDF Demand Bound Function Analysis:")
    is_schedulable = True

    for t in workload_EDF_helper(taskset):
        demand = calculate_dbf(taskset, t)
        accepted = demand <= t
        print(f"t = {t} | dbf(t) = {demand} | {'ACCEPTED' if accepted else 'FAILED'}")
        is_schedulable &= accepted

    print("Taskset is schedulable under EDF" if is_schedulable
        else "Taskset is NOT schedulable under EDF")

    return is_schedulable


def workload_dm_helper(tasks: list[Task]):
    # self._tasks: dict[int, Task] = {t.id: copy.copy(t) for t in tasks}
    last_task = tasks[-1]
    previous_tasks = tasks[:-1]

    # multiple time per period until t reaches the H
    test_points = set()
    test_points.add(last_task.deadline)

    # Take into a count each task period before big task
    for p_task in previous_tasks:
        k = 1
        while k * p_task.period <= last_task.deadline:
            test_points.add(k * p_task.period)
            k += 1

    # Check each point W(i)
    for t in sorted(test_points):
        interference = sum(
            ceil(t / p_task.period) * p_task.wcet for p_task in previous_tasks
        )
        w = last_task.wcet + interference
        # Compare if the Workload < Time
        if w <= t:
            return w

    return -1


def workload_dm(taskset: TaskSet):
    taskset.sorted_by_deadline()
    tasks: list[Task] = [copy.copy(t) for t in taskset.tasks]

    result = []
    for i in range(1, len(tasks) + 1):
        workload_i = workload_dm_helper(tasks[:i])
        result.append(workload_i)

    return result


def workload_at_deadline_dm(taskset: TaskSet) -> list[int]:
    """
    Compute W_i(D_i) for every task — always evaluates at the deadline,
    no early exit.  The existing algorithm is untouched; this is additive.
    """
    taskset.sorted_by_deadline()
    tasks: list[Task] = [copy.copy(t) for t in taskset.tasks]

    result = []
    for i in range(1, len(tasks) + 1):
        last_task      = tasks[i - 1]
        previous_tasks = tasks[:i - 1]
        t              = last_task.deadline
        interference   = sum(
            ceil(t / p.period) * p.wcet for p in previous_tasks
        )
        result.append(last_task.wcet + interference)

    return result


def print_workload_analysis(taskset: TaskSet) -> None:
    """
    Print both workload results side by side:
      - W_i (first pass) : from workload_dm  — earliest t where W ≤ t
      - W_i (D_i)        : from workload_at_deadline_dm — always at deadline
    """
    first_pass   = workload_dm(taskset)
    at_deadline  = workload_at_deadline_dm(taskset)

    taskset.sorted_by_deadline()
    tasks = list(taskset.tasks)

    print(f"\n  {_BOLD}{_WHITE}"
          f"{'τ_i':<6}  {'D_i':<8}  {'W_i (first pass)':<18}  {'W_i (D_i)':<12}  schedulable"
          f"{_RESET}")
    print(f"  {_DIM}{'─' * 62}{_RESET}")

    for task, w_fp, w_dl in zip(tasks, first_pass, at_deadline):
        sched    = w_fp != -1
        fp_str   = f"{w_fp}" if sched else f"{_RED}FAIL{_RESET}"
        s_color  = _GREEN if sched else _RED
        verdict  = f"{s_color}✓{_RESET}" if sched else f"{_RED}✗{_RESET}"

        print(
            f"  {_YELLOW}τ_{task.id:<4}{_RESET}"
            f"  {_MAGENTA}{task.deadline:<8}{_RESET}"
            f"  {_CYAN}{fp_str:<18}{_RESET}"
            f"  {_BOLD}{w_dl:<12}{_RESET}"
            f"  {verdict}"
        )


# =========================================================================
#  LOG-BASED WORKLOAD TRACE
# =========================================================================


def workload_trace_from_logs(logs: dict, taskset: TaskSet, task_id: int) -> dict:
    """
    Replay the simulation schedule_trace and build the W_i(t) step-through
    table up to the first deadline D_i of the target task.

    Under DM: higher priority ↔ smaller deadline (D_h < D_i).

    @Returns dict with:
        rows        : list of slot dicts (see below)
        W_final     : accumulated workload at t = D_i
        D_i         : first deadline of τ_task_id
        C_i         : WCET of τ_task_id
        slack       : D_i − W_final  (positive = schedulable)
        higher_ids  : set of higher-priority task ids
    """
    target = taskset.get_task(task_id)
    D_i = target.deadline
    C_i = target.wcet

    # DM: higher priority = strictly smaller deadline
    higher_ids = {t.id for t in taskset if t.deadline < D_i}

    rows = []
    w = 0.0

    for slot in logs["schedule_trace"]:
        if slot["start"] >= D_i:
            break

        start  = slot["start"]
        end    = min(slot["end"], D_i)
        tid    = slot["task_id"]
        delta  = end - start

        is_target   = tid == task_id
        is_higher   = tid in higher_ids
        contributes = is_target or is_higher

        if contributes:
            w += delta

        rows.append({
            "start":       start,
            "end":         end,
            "task_id":     tid,
            "delta":       delta,
            "w":           w if contributes else None,
            "is_target":   is_target,
            "is_higher":   is_higher,
            "contributes": contributes,
        })

    return {
        "rows":        rows,
        "W_final":     w,
        "D_i":         D_i,
        "C_i":         C_i,
        "slack":       D_i - w,
        "higher_ids":  higher_ids,
    }


def print_workload_trace(logs: dict, taskset: TaskSet, task_id: int) -> None:
    """
    Print a colour-coded step-through table of W_i(t) built from simulation
    logs.  Mirrors the DM analytical workload formula (Eq. 4.31) visually.
    """
    data = workload_trace_from_logs(logs, taskset, task_id)
    rows       = data["rows"]
    W_final    = data["W_final"]
    D_i        = data["D_i"]
    C_i        = data["C_i"]
    slack      = data["slack"]
    higher_ids = data["higher_ids"]

    target = taskset.get_task(task_id)
    hp_names = ", ".join(f"τ_{hid}" for hid in sorted(higher_ids)) or "none"

    print(f"\n{_BOLD}{_WHITE}Workload Trace — τ_{task_id}  "
          f"(D_i = {D_i}, C_i = {C_i}){_RESET}")
    print(f"  {_DIM}Higher-priority tasks under DM: {hp_names}{_RESET}")
    print(f"  {_DIM}Showing schedule up to t = {D_i}{_RESET}\n")

    # ── header ──
    H = f"{'t_start':>8}  {'t_end':>6}  {'τ':>5}  {'Δt':>5}  {'W_i(t)':>8}  note"
    print(f"  {_BOLD}{_WHITE}{H}{_RESET}")
    print(f"  {_DIM}{'─' * 55}{_RESET}")

    for r in rows:
        tid   = r["task_id"]
        start = r["start"]
        end   = r["end"]
        delta = r["delta"]
        w_val = r["w"]

        if r["is_target"]:
            color = _CYAN
            note  = f"{_DIM}← C_i{_RESET}"
        elif r["is_higher"]:
            color = _YELLOW
            note  = f"{_DIM}← higher priority{_RESET}"
        else:
            color = _DIM
            note  = f"{_DIM}(lower priority, excluded){_RESET}"

        w_str = f"{w_val:>8.1f}" if w_val is not None else f"{'—':>8}"

        print(
            f"  {color}{start:>8.1f}  {end:>6.1f}  "
            f"τ_{tid:<3}  {delta:>5.1f}  "
            f"{_RESET}{_BOLD}{w_str}{_RESET}  {note}"
        )

    # ── summary ──
    print(f"\n  {_DIM}{'─' * 55}{_RESET}")
    sched_ok = slack >= 0
    s_color  = _GREEN if sched_ok else _RED
    verdict  = "schedulable ✓" if sched_ok else "deadline miss ✗"

    print(f"\n  W_i(D_i={D_i}) = {_BOLD}{_CYAN}{W_final:.1f}{_RESET}  "
          f"{'≤' if sched_ok else '>'} D_i = {D_i}  "
          f"→  {s_color}{verdict}{_RESET}")
    print(f"  Slack  S_i = D_i − R_i = {s_color}{slack:.1f}{_RESET}\n")
