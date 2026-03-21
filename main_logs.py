from analysis.log_loader import load_logs, taskset_from_logs
from analysis.workload_analyzer import print_workload_trace

logs = load_logs("logs/", algorithm="DM", timestamp="20260320_163625")
taskset = taskset_from_logs(logs)

# ── Workload step-through for a specific task ─────────────────────────────
# Change the task_id to evaluate a different task.
TARGET_TASK_ID = 2

print_workload_trace(logs, taskset, TARGET_TASK_ID)

