from math import ceil
from math import floor
from models.scheduling.taskset import TaskSet
from models.scheduling.task import Task

def response_time_dm_helper(tasks: list[Task]) -> dict:
    """
    Computes the exact worst-case response time of the last task in `tasks`
    assuming all previous tasks are higher-priority tasks under DM scheduling.
    Which is true in our case, because we sort the task set by period before calling this function.

    Based on Buttazzo, Chapter 4.5.2:
        R_i = C_i + sum( ceil(R_i / T_h) * C_h )
    """
    if not tasks: 
        raise ValueError("response_time_analysis_dm received an empty task list")
    
    task_i = tasks[-1]
    hp_tasks = tasks[:-1]

    R_i = task_i.wcet
    steps = [R_i]

    while True:
        R_old = R_i

        interference = 0
        for hp in hp_tasks:
            interference += ceil(R_old/ hp.period) * hp.wcet

        R_i = task_i.wcet + interference
        steps.append(R_i)

        if R_i > task_i.deadline:
            return {
                "task":  task_i,
                "response_time": R_i,
                "steps": steps,
                "schedulable": False
            }
        
        if R_i == R_old:
            return {
                "task":  task_i,
                "response_time": R_i,
                "steps": steps,
                "schedulable": True
            }
        
def response_time_dm(taskset: TaskSet) -> list[dict]:
    """
    Performs Deadline Monotonic Response Time Analysis on the whole task set.
    Tasks are analyzed in increasing deadline order.
    """

    tasks = taskset.sorted_by_deadline()
    results = []

    for i in range(len(tasks)):
        result_i = response_time_dm_helper(tasks[: i + 1])
        results.append(result_i)

        if not result_i["schedulable"]:
            break

    return results

def response_time_analysis(taskset: TaskSet, schedule_type="DM"):
    if schedule_type == "DM":
        return response_time_dm(taskset)
    else:
        raise NotImplementedError(f"Response Time Analysis not implemented for {schedule_type}")