import pandas as pd

from analysis.log_loader import load_logs, taskset_from_logs

# ── ANSI ──────────────────────────────────────────────────────────────────────
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"
CYAN    = "\033[36m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
RED     = "\033[31m"
MAGENTA = "\033[35m"
WHITE   = "\033[37m"
BG_BLUE = "\033[40m"


def header(text):
    print(f"\n{BOLD}{BG_BLUE}{WHITE} {text} {RESET}")


def label(name, value, color=GREEN):
    print(f"  {DIM}{name}{RESET} = {color}{value}{RESET}")


def compute_stats(logs: dict) -> dict:
    df = pd.DataFrame(logs["all_jobs"])
    stats = {}
    for tid, group in df.groupby("task_id"):
        rts = group["response_time"].dropna()
        stats[tid] = {
            "max_R_i":      rts.max() if len(rts) else 0.0,
            "avg_R_i":      rts.mean() if len(rts) else 0.0,
            "total_missed": int(group["missed_deadline"].sum()),
        }
    return stats


def print_taskset_summary(taskset, name: str):
    header(f"TASK SET — {name}")
    print(f"  {BOLD}{YELLOW}{taskset}{RESET}\n")
    label("n           ", f"{taskset.n}", CYAN)
    label("U           ", f"{taskset.utilization:.4f}")
    label("H           ", f"{taskset.hyperperiod}", CYAN)
    label("D_max       ", f"{taskset.D_max}", MAGENTA)
    label("Constrained?", f"{taskset.has_constrained_deadlines}",
          RED if taskset.has_constrained_deadlines else GREEN)

    n        = taskset.n
    ll_bound = n * (2 ** (1 / n) - 1)
    label("U_lub (LL)  ", f"{ll_bound:.4f}", CYAN)

    if taskset.utilization <= ll_bound:
        print(f"\n  {GREEN}✓ U ≤ U_lub → guaranteed schedulable by RM/DM{RESET}")
    elif taskset.utilization <= 1.0:
        print(f"\n  {YELLOW}? U_lub < U ≤ 1.0 → inconclusive, need RTA/dbf{RESET}")
    else:
        print(f"\n  {RED}✗ U > 1.0 → overloaded{RESET}")


def print_sim_results(stats: dict, taskset, algorithm: str):
    header(f"SIMULATION — {algorithm}")
    print(
        f"\n  {BOLD}{WHITE}{'τ_i':<6}  {'max R_i':<10}  {'avg R_i':<10}  "
        f"{'D_i':<10}  {'missed':<8}{RESET}"
    )
    print(f"  {DIM}{'─' * 52}{RESET}")

    for tid in sorted(stats):
        a            = stats[tid]
        t            = taskset.get_task(tid)
        missed_color = RED if a["total_missed"] > 0 else GREEN
        print(
            f"  {YELLOW}τ_{tid:<4}{RESET}  "
            f"{CYAN}{a['max_R_i']:<10.1f}{RESET}  "
            f"{DIM}{a['avg_R_i']:<10.1f}{RESET}  "
            f"{MAGENTA}{t.deadline:<10}{RESET}  "
            f"{missed_color}{a['total_missed']:<8}{RESET}"
        )

    total_missed = sum(a["total_missed"] for a in stats.values())
    if total_missed == 0:
        print(f"\n  {GREEN}✓ All deadlines met{RESET}")
    else:
        print(f"\n  {RED}✗ {total_missed} total deadline misses{RESET}")


def print_comparison(dm_stats: dict, edf_stats: dict, taskset):
    header("COMPARISON — DM vs EDF (max R_i)")
    print(
        f"\n  {BOLD}{WHITE}{'τ_i':<6}  {'DM R_i':<10}  {'EDF R_i':<10}  "
        f"{'D_i':<10}  {'winner':<8}{RESET}"
    )
    print(f"  {DIM}{'─' * 52}{RESET}")

    for tid in sorted(dm_stats):
        t     = taskset.get_task(tid)
        dm_r  = dm_stats[tid]["max_R_i"]
        edf_r = edf_stats[tid]["max_R_i"]

        if dm_r < edf_r:
            winner = f"{CYAN}DM{RESET}"
        elif edf_r < dm_r:
            winner = f"{MAGENTA}EDF{RESET}"
        else:
            winner = f"{DIM}tie{RESET}"

        print(
            f"  {YELLOW}τ_{tid:<4}{RESET}  "
            f"{CYAN}{dm_r:<10.1f}{RESET}  "
            f"{MAGENTA}{edf_r:<10.1f}{RESET}  "
            f"{DIM}{t.deadline:<10}{RESET}  "
            f"{winner}"
        )


# ── Load logs ─────────────────────────────────────────────────────────────────

TIMESTAMP = "20260320_163625"

dm_logs  = load_logs("logs/", algorithm="DM",  timestamp=TIMESTAMP)
edf_logs = load_logs("logs/", algorithm="EDF", timestamp=TIMESTAMP)
taskset  = taskset_from_logs(dm_logs)

# ── Run ───────────────────────────────────────────────────────────────────────

print_taskset_summary(taskset, name=TIMESTAMP)

dm_stats  = compute_stats(dm_logs)
edf_stats = compute_stats(edf_logs)

print_sim_results(dm_stats,  taskset, "DM")
print_sim_results(edf_stats, taskset, "EDF")
print_comparison(dm_stats, edf_stats, taskset)
