"""
Helpers for justifying and reporting the simulation horizon.
"""

from models.scheduling.taskset import TaskSet


def simulation_length_report(taskset: TaskSet) -> dict:
    """
    Return the same default simulation-length formulation used by the engine.

    Current repository assumptions:
    - zero jitter
    - zero phase
    - constrained deadlines (D_i <= T_i)

    Under these assumptions, the periodic release pattern repeats after one
    hyperperiod, so the simulation horizon is one hyperperiod.
    """
    return {
        "hyperperiod": taskset.hyperperiod,
        "D_max": taskset.D_max,
        "jitterless": taskset.is_jitterless,
        "synchronous": taskset.is_synchronous,
        "simulation_hyperperiods": taskset.simulation_hyperperiods,
        "simulation_length": taskset.simulation_length,
        "length_formula": (
            f"{taskset.simulation_hyperperiods} x {taskset.hyperperiod} "
            f"= {taskset.simulation_length}"
        ),
    }
