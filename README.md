# mini-project-1
First mini project for the Distibuted Real-time Systems course (02225) at DTU


## Notation (Buttazzo Chapter 4)

```
Γ       : Task set {τ_1, ..., τ_n}
τ_i     : Periodic task
C_i     : Worst-Case Execution Time (WCET)
T_i     : Period
D_i     : Relative deadline (C_i ≤ D_i ≤ T_i)
Φ_i     : Phase (release time of first instance)
H       : Hyperperiod = lcm(T_1, ..., T_n)
U       : Processor utilization = Σ C_i / T_i
R_i     : Worst-case response time of τ_i
τ_{i,j} : j-th instance (job) of τ_i
r_{i,j} : Release time of τ_{i,j}
d_{i,j} : Absolute deadline = r_{i,j} + D_i
f_{i,j} : Finish time of τ_{i,j}
R_{i,j} : Response time = f_{i,j} - r_{i,j}
U_i     : Utilization Factor
```

## Modeling Specifications

### Task Model
Represents a periodic real-time task from a task set.This tasks will go under the assumptions of:

+ `A1`: The instances of a periodic task are regularly activated at a constant rate. The interval. Ti between two consecutive activations is the period of the task.
+ `A2`: All instances of a periodic task have the same worst-case execution time.
+ `A3 (soft)`: All instances of a periodic task have the same relative deadline . Di, which
is equal to the period. Ti.
+ `A4`: All tasks in . 𝚪 are independent; that is, there are no precedence relations and
no resource constraints.
