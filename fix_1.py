# Fix #1
from dataclasses import dataclass
@dataclass
class T:
    name: str; period: int; deadline: int; wcet: int

def edf(tasks, hp):
    return [(t, min(tasks, key=lambda x:x.deadline).name) for t in range(hp)]
