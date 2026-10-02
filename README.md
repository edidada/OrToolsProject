# README
OR-Tools 的 Python 库（`ortools`）是 Google 开源的一套**运筹学优化工具包**，你可以把它理解为一个功能更强大的“超级 PuLP”。它比 PuLP 支持的问题类型更多，内置的求解器也更强大。

### 它包含什么？

OR-Tools 不是单一求解器，而是一个包含多种算法的工具箱：

- **线性与混合整数规划**：这是最基础的优化。它的 `pywraplp` 封装了 GLOP（Google 的线性优化求解器），也支持调用 CBC、SCIP 等外部求解器。
- **约束规划（CP-SAT）**：`ortools.sat.python.cp_model` 是它的招牌功能，专门解决那些约束条件很复杂、无法用线性方程简单描述的问题（比如排班、调度中的“要么…要么…”逻辑）。
- **路由与图算法**：内置了车辆路径规划、最大流、最小费用流、指派问题等经典算法的专用求解器。
- **背包问题**：`knapsack_solver` 可以处理各种资源分配下的打包问题。

### 和你之前问的 PuLP 有何不同？

| 特性 | **PuLP** | **OR-Tools** |
| :--- | :--- | :--- |
| **定位** | 专注于**线性/整数规划**的建模工具 | **综合性的运筹学工具箱** |
| **求解器** | 自身不计算，调用 CBC 等外部求解器 | **内置多个求解器**（如 GLOP、CP-SAT），也支持外部求解器 |
| **擅长领域** | 标准的线性、整数规划问题 | 线性规划、**约束规划**、**路由问题**、图算法等 |
| **上手难度** | 相对简单，API 很直观 | 功能多，API 相对复杂一些 |

### 💡 什么时候用 OR-Tools？

当你遇到 PuLP 难以描述的问题时，就该考虑它了：

- **逻辑约束复杂**：比如“如果 A 发生，则 B 必须发生”这种逻辑关系，用 PuLP 的线性表达式很难写，但在 CP-SAT 里很自然。
- **问题类型特殊**：需要解决**车辆路径规划（VRP）** 或**复杂的排班/调度**问题时，OR-Tools 有专门的高效模块。
- **追求求解性能**：对于大规模问题，OR-Tools 内置的求解器和算法通常比 PuLP 默认的 CBC 更快、更强。

### 简单代码示例（线性规划）

看一个和你之前 PuLP 例子目标类似的简单问题（最大化 3x + y）：

```python
from ortools.linear_solver import pywraplp

# 1. 声明求解器（这里用 GLOP）
solver = pywraplp.Solver.CreateSolver("GLOP")
if not solver:
    print("无法创建求解器")
    exit()

# 2. 创建变量
x = solver.NumVar(0, 1, "x")
y = solver.NumVar(0, 2, "y")

# 3. 定义约束：x + y <= 2
constraint = solver.Constraint(-solver.infinity(), 2, "ct")
constraint.SetCoefficient(x, 1)
constraint.SetCoefficient(y, 1)

# 4. 定义目标函数：最大化 3x + y
objective = solver.Objective()
objective.SetCoefficient(x, 3)
objective.SetCoefficient(y, 1)
objective.SetMaximization()

# 5. 求解
status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    print(f"目标值 = {objective.Value()}")
    print(f"x = {x.solution_value()}, y = {y.solution_value()}")
else:
    print("未找到最优解")
```

如果你正在处理的问题涉及到复杂的排班、路径规划，或者纯线性模型搞不定，OR-Tools 会是更合适的选择。