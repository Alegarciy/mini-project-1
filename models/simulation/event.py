from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional


class EventType(IntEnum):
    """
    @Details: Lower Values are processed first, instant tie breaker
    @Author: Alejandro Garcia Bejarano
    """

    COMPLETION = 0  # first check
    ARRIVAL = 1
    DEADLINE = 2  # last check


@dataclass(order=True)
class Event:
    """
    @Details:
        Data Structure: Event Heap (earliest time first).
        Sort Key: (time, event_type, task_id)
    @Note: Review [Banks,Ch 1] for Event-scheduling 
    @Author: Alejandro Garcia Bejarano
    """

    # Note: time skips, is not linear time processing
    time: float
    event_type: EventType
    task_id: int = field(compare=True)
    job_id: Optional[int] = field(default=None, compare=False)

    def __repr__(self) -> str:
        j = f",{self.job_id}" if self.job_id is not None else ""
        return f"Event({self.event_type.name}, t={self.time:.1f}, τ_{self.task_id}{j})"
