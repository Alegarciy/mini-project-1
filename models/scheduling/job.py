import warnings
from dataclasses import dataclass
from typing import Optional


@dataclass
class Job:
    """
    @Details: Periodic sequences called instances.
    @Note: Notation is τ_{i,j}, J notation in Butazzo is reserved for aperiodic jobs.
    @Author: Alejandro Garcia Bejarano
    """

    # Initialization Parameters
    task_id: int
    job_id: int
    release_time: float
    absolute_deadline: float
    execution_time: float
    remaining_time: float
    # Attributes filled in simulation
    start_time: Optional[float] = None  # First start
    finish_time: Optional[float] = None  # First start
    preemtion_count: int = 0

    @property
    def response_time(self) -> Optional[float]:
        """
        R_{i,j} = f_{i,j} - r_{i,j}
        """
        if self.finish_time is None:
            # warnings.warn(
            #     f"📝 Warning line ~33, job.py: J({self.task_id},{self.job_id})"
            #     f"\nfinish time = None, job hasn't finish yet"
            # )
            return None

        if self.finish_time - self.release_time < 0:
            raise ValueError(
                f"🧨 ValueError line ~41, job.py: J({self.task_id},{self.job_id})"
                f"\nfinish_time={self.finish_time}, release_time={self.release_time}"
                f"\nfinish time <= release_time, job finishe before relase time"
            )

        return self.finish_time - self.release_time

    @property
    def is_completed(self) -> bool:
        # No warning needed, that is the checkup
        if self.finish_time is None:
            return False

        if self.finish_time - self.release_time < 0:
            raise ValueError(
                f"🧨 ValueError line ~57, job.py: J({self.task_id},{self.job_id})"
                f"\nfinish_time={self.finish_time}, release_time={self.release_time}"
                f"\nfinish time <= release_time, job finishe before relase time"
            )

        return True

    @property
    def missed_deadline(self) -> bool:
        """
        Feasible: f_{i,j} > d{i,j}
        """
        if self.finish_time is None:
            # Unfinished means that is still executing
            # while checking, so its analagous of Missed
            return True
        return self.finish_time > self.absolute_deadline

    def __repr__(self) -> str:
        status = f"f={self.finish_time:.1f}" if self.is_completed else f"rem={self.remaining_time:.1f}"
        return (
            f"τ_{self.task_id},{self.job_id}"
            f"(r={self.release_time:.1f}, d={self.absolute_deadline:.1f}, {status})"
        )
