from analysis.log_loader import load_logs, taskset_from_logs
from analysis.workload_analyzer import print_workload_trace

TIMESTAMP = "20260320_163625"

dm_logs = load_logs("logs/", algorithm="DM", timestamp=TIMESTAMP)
taskset = taskset_from_logs(dm_logs)

TARGET_TASK_ID = 2
print_workload_trace(dm_logs, taskset, TARGET_TASK_ID)
