# Fix for Issue #1 - EDF Scheduler Enhancement
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class Task:
    name: str
    period: int
    deadline: int
    wcet: int  # worst-case execution time
    remaining: int = 0

    def __post_init__(self):
        self.remaining = self.wcet

def edf_schedule(tasks: List[Task], hyperperiod: int) -> List[Tuple[int, str]]:
    schedule = []
    jobs = []
    for t in tasks:
        for release in range(0, hyperperiod, t.period):
            jobs.append((release, release + t.deadline, t.wcet, t.name))
    jobs.sort(key=lambda j: j[1])  # sort by deadline

    for time_slot in range(hyperperiod):
        available = [j for j in jobs if j[0] <= time_slot and j[2] > 0]
        if available:
            earliest = min(available, key=lambda j: j[1])
            schedule.append((time_slot, earliest[3]))
            earliest_list = list(earliest)
            earliest_list[2] -= 1
            jobs[jobs.index(earliest)] = tuple(earliest_list)
        else:
            schedule.append((time_slot, "IDLE"))
    return schedule
