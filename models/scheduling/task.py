from dataclasses import dataclass
# from enum import Enum

# class Utilization(Enum):
#     wcet = 1
#     bcet = 2
#     random = 3 # interval between [wcet, bcet]


@dataclass
class Task:
    """
    @Details: A periodic real-time task τ_i ∈ Γ [Butazzo notation]
    @Author: Alejandro Garcia Bejarano
    """

    id: int
    name: str
    bcet: int
    wcet: int
    period: int  # T_i
    deadline: int  # D_i
    phase: int = 0  # Φ_i
    jitter: int = 0

    def __post_init__(self):
        """
        Validate Basic Constraints based on Butazzo
        """
        if self.bcet > self.wcet:
            raise ValueError(f"τ_{self.id}: BCET ({self.bcet}) > WCET ({self.wcet})")
        if self.wcet > self.deadline:
            raise ValueError(f"τ_{self.id}: C_i ({self.wcet}) > D_i ({self.wcet})")
        if self.deadline > self.period:
            raise ValueError(
                f"τ_{self.id}: C_i ({self.deadline}) > D_i ({self.period})"
            )

    @property
    def utilization(self) -> float:
        """
        Computes Utilization Factor (only one task) [Section 4.1.1]
        """
        # TODO: Utilization always the worst case scenario?
        return self.wcet / self.period

    @property
    def has_contrained_deadline(self) -> bool:
        """
        Validation: D_i < T_i
        A3 relaxed: "All instances of a τi have the same Di, for Ti."
        """
        return self.deadline < self.period

    def release_time(self, k: int) -> float:
        """
        r_{i,k} = Φ_i + (k-1) * T_i
        Realease time of the k-th instance
        A6 strict: All tasks are realease as soon as they arrive
        """
        return self.phase + (k - 1) * self.period

    def absolute_deadline_of(self, k: int) -> float:
        """
        d_{i,k} = r_{i,k} + D_i = Φ_i + (k-1) * T_i + D_i
        """
        return self.phase + (k - 1) * self.period + self.deadline

    def __repr__(self) -> str:
        return (
            f"τ_{self.id} (C={self.wcet}, T={self.period}, "
            f"D={self.deadline}, BCET={self.bcet})"
        )

    # TODO: compare tasks gr and eq?
