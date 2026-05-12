import copy
import csv
import math
from functools import reduce
from pathlib import Path
from typing import Iterator

# Custom
from models.scheduling.task import Task


class TaskSet:
    """
    @Details: A task set Γ containg periodic task set.
    @Author: Alejandro Garcia Bejarano
    """

    def __init__(self, tasks: list[Task]) -> None:
        # Shallow copy, nothing implies task modification
        self._tasks: dict[int, Task] = {t.id: copy.copy(t) for t in tasks}

    @property
    def n(self) -> int:
        return len(self._tasks)

    # == Hyperperiods Methods ==

    @property
    def hyperperiod(self) -> int:
        """
        H = lcm(T_1,...,T_n)
        Defines the window of repetition between periods.

        In this project, all tasks are loaded with zero jitter and zero phase,
        so the release pattern repeats every hyperperiod.
        """
        periods = [t.period for t in self._tasks.values()]
        return reduce(math.lcm, periods) if periods else 0

    @property
    def simulation_length(self) -> int:
        """
        Simulation horizon used by the event-driven engine.

        Rationale:
        - tasks are periodic and jitterless in this repository
        - all first releases happen at time 0 (phase = 0)
        - deadlines are constrained by Task.__post_init__ (D_i <= T_i)
        - therefore the job-release pattern repeats after one hyperperiod H
        - every job released in [0, H) also has its deadline within [0, H]

        Hence, simulating one hyperperiod is sufficient for the current model.
        """
        return self.hyperperiod

    @property
    def simulation_hyperperiods(self) -> int:
        """Number of hyperperiods used by the default simulation horizon."""
        return 1

    @property
    def is_jitterless(self) -> bool:
        """True when all tasks have zero jitter."""
        return all(t.jitter == 0 for t in self._tasks.values())

    @property
    def is_synchronous(self) -> bool:
        """True when all tasks have zero phase."""
        return all(t.phase == 0 for t in self._tasks.values())

    # == Methods Generalization for Set ==

    @property
    def utilization(self) -> float:
        """
        U = Σ C_i / T_i
        Computes Utilization Factor Entire Set [Section 4.1.1]
        """
        return sum(t.utilization for t in self._tasks.values())

    @property
    def has_constrained_deadlines(self) -> bool:
        """
        True if any task has D_i < T_i.
        Note: A3 is soft, despite Chapter 04 axioms
        """
        return any(t.has_contrained_deadline for t in self._tasks.values())

    @property
    def D_max(self) -> int:
        return max(t.deadline for t in self._tasks.values())

    # == Getters/Setters ==

    def get_task(self, id: int) -> Task:
        return self._tasks[id]

    @property
    def tasks(self) -> list[Task]:
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def sorted_by_deadline(self) -> list[Task]:
        """
        Shortest Deadline <=> Higher Priority
        Note: This is convenient for Deadline Monotonic (DM)
        """
        return sorted(self._tasks.values(), key=lambda t: (t.deadline, t.id))

    def sorted_by_period(self) -> list[Task]:
        """
        Shortest Period <=> Higher Priority
        Note: This is conveinent for Rate Monotonic
        """
        return sorted(self._tasks.values(), key=lambda t: (t.period, t.id))

    # == Class Iterators ==

    def __iter__(self) -> Iterator[Task]:
        return iter(self.tasks)

    def __len__(self) -> int:
        return self.n

    def __repr__(self) -> str:
        return (
            f"Γ(n={self.n}, U={self.utilization:.4f}, "
            f"H={self.hyperperiod}, "
            f"constrained={'yes' if self.has_constrained_deadlines else 'no'})"
        )

    # == I/O ==
    
    @classmethod
    def from_csv(cls, filepath: str | Path) -> "TaskSet":
        """
        Load a task set from CSV.

        Expected format:
            Name, Jitter, BCET, WCET, Period, Deadline, PE
        """
        filepath = Path(filepath)
        tasks = []

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            for row in reader:
                raw = (row.get("Name") or row.get("Task") or row.get("TaskID") or "").strip()
                if not raw:
                    continue

                # Extract numeric ID from name like "T0", "T1", "T10"
                id_str = raw.lstrip("Tt").lstrip("_").strip()
                task_id = int(id_str)
                name = f"T{task_id}"

                tasks.append(Task(
                    id=task_id,
                    name=name,
                    # TODO: If we want to load tasks with jitter
                    # jitter=int(row.get("Jitter", 0)),
                    jitter=0,
                    bcet=int(row["BCET"]),
                    wcet=int(row["WCET"]),
                    period=int(row["Period"]),
                    deadline=int(row["Deadline"]),
                ))

        if not tasks:
            raise ValueError(f"No tasks loaded from {filepath}")

        print(f"Loaded {len(tasks)} tasks from {filepath.name}")
        return cls(tasks)
