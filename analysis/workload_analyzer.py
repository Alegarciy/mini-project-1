import copy
from math import ceil

from models.scheduling.taskset import TaskSet
from models.scheduling.task import Task


def workload(taskset: TaskSet, schedule_type="DM"):

    if schedule_type == "DM":
        return 0
    else:  # EDF

        # taskset.sorted_by_period()
        return 0

def workload_dm_helper(tasks: list[Task]):

    # self._tasks: dict[int, Task] = {t.id: copy.copy(t) for t in tasks}
    last_period = tasks[-1]
    previous_tasks = tasks[:-1]
    workload_sum = 0

    period_last_task = (
        last_period.period
    )  # multiple time per period until t reaches the H
    for p_task in previous_tasks:
        workload_sum += ceil(period_last_task / p_task.period) * p_task.wcet

    total_workload = last_period.wcet + workload_sum
    return total_workload


## Rewritting the workload_dm_helper
# def workload_dm_helper(tasks:list[Task]):
#
#     evaluated_task = tasks[-1]
#     intereferences = tasks[:-1]



def workload_dm(taskset: TaskSet):

    taskset.sorted_by_deadline()
    tasks: list[Task] = [copy.copy(t) for t in taskset.tasks]

    result = []
    for i in range(len(taskset) + 1):
        workload_i = workload_dm_helper(tasks[:i])
        result.append(workload_i)

    return 0
