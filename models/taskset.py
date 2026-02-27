import copy
import csv
import math
from functools import reduce
from pathlib import Path
from typing import Iterator

# Custom
from models.task import Task

class TaskSet:
    """
    @Details: A task set Γ containg periodic task set.
    @Author: Alejandro Garcia Bejarano
    """

    def __init__(self, tasks: list[Task]) -> None:
        # Shallow copy, nothing implies task modification
        self._tasks: dict[int,Task] = {
            t.id: copy.copy(t) for t in tasks
        }

    @property
    def n(self) -> int:
        return len(self._tasks)

    # == Hyperperiods Methods ==

    @property
    def hyperperiod(self) -> int:
        """
        H = lcm(T_1,...,T_n)
        Defines the window of repetition between periods
        """
        periods = [t.period for t in self._tasks.values()]
        return reduce(math.lcm,periods) if periods else 0

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
