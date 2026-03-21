import copy
from math import ceil
from math import floor
from math import lcm

from models.scheduling.taskset import TaskSet
from models.scheduling.task import Task


def workload(taskset: TaskSet, schedule_type="EDF"):

    if schedule_type == "DM":
        return 0
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
    max_t = lcm(*(task.period for task in taskset.tasks))
    # max_t = sum(task.period for task in taskset.tasks)

    for task in taskset.tasks:
        k = 1
        while True:
            t = k * task.period + task.deadline

            if t > max_t:
                break

            if t > 0:
                points.add(t)

            k += 1

    return sorted(points)

def workload_edf(taskset):

    test_points = workload_EDF_helper(taskset)

    print("EDF Demand Bound Function Analysis:")
    print("----------------------------------")

    is_schedulable = True

    for t in test_points:
        demand = calculate_dbf(taskset, t)

        # Result for each t
        print(f"t = {t:4d} | dbf(t) = {demand:4d} | ", end="")

        if demand <= t:
            print("OK")
        else:
            print("FAIL")
            is_schedulable = False

    if is_schedulable:
        print("Task set is schedulable under EDF")
    else:
        print("Task set is NOT schedulable under EDF")

    return is_schedulable

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
