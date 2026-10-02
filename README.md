# README
OR-Tools 的 Python 库（`ortools`）是 Google 开源的一套运筹学优化工具包，你可以把它理解为一个功能更强大的“超级 PuLP”。它比 PuLP 支持的问题类型更多，内置的求解器也更强大。

### 它包含什么？

OR-Tools 不是单一求解器，而是一个包含多种算法的工具箱：

- 线性与混合整数规划：这是最基础的优化。它的 `pywraplp` 封装了 GLOP（Google 的线性优化求解器），也支持调用 CBC、SCIP 等外部求解器。
- 约束规划（CP-SAT）：`ortools.sat.python.cp_model` 是它的招牌功能，专门解决那些约束条件很复杂、无法用线性方程简单描述的问题（比如排班、调度中的“要么…要么…”逻辑）。
- 路由与图算法：内置了车辆路径规划、最大流、最小费用流、指派问题等经典算法的专用求解器。
- 背包问题：`knapsack_solver` 可以处理各种资源分配下的打包问题。

### 和你之前问的 PuLP 有何不同？

| 特性 | PuLP | OR-Tools |
| :--- | :--- | :--- |
| 定位 | 专注于线性/整数规划的建模工具 | 综合性的运筹学工具箱 |
| 求解器 | 自身不计算，调用 CBC 等外部求解器 | 内置多个求解器（如 GLOP、CP-SAT），也支持外部求解器 |
| 擅长领域 | 标准的线性、整数规划问题 | 线性规划、约束规划、路由问题、图算法等 |
| 上手难度 | 相对简单，API 很直观 | 功能多，API 相对复杂一些 |

### 💡 什么时候用 OR-Tools？

当你遇到 PuLP 难以描述的问题时，就该考虑它了：

- 逻辑约束复杂：比如“如果 A 发生，则 B 必须发生”这种逻辑关系，用 PuLP 的线性表达式很难写，但在 CP-SAT 里很自然。
- 问题类型特殊：需要解决车辆路径规划（VRP） 或复杂的排班/调度问题时，OR-Tools 有专门的高效模块。
- 追求求解性能：对于大规模问题，OR-Tools 内置的求解器和算法通常比 PuLP 默认的 CBC 更快、更强。

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

### 运行项目示例（Poetry）

CP-SAT 排班演示实现于 `src/ortools_project/examples/cp_sat_schedule.py`。它为两名员工安排 20 天的早、晚班，保证每个班次恰好一人、每人每天至多一个班次，并要求员工每天轮换早、晚班。

使用 Poetry 安装锁定依赖后，通过项目定义的命令运行示例与测试：

```bash
poetry install
poetry run cp-sat-schedule
poetry run pulp-example
poetry run pytest test_pulp.py -v
```

OR-Tools 在工业界落地的三类高价值场景：用 CP-SAT 解决多技能工排班（意大利 Magni 伸缩臂叉装车产线）、用 Routing 解决多中心铁路商品车配送（中国铁路特货运北京分公司，2021 年试运行）、用 GLOP/PDLP 解决大规模生产计划（智利 CMPC 锯木厂，需求满足率提升 7%）。

---

### 复杂排班：CP-SAT 解决多技能工产线平衡

真实案例：意大利 Magni Telescopic Handlers 装配线平衡

意大利伸缩臂叉装车制造商 Magni 的装配线面临一个典型痛点：手工排产导致工位负荷严重不均，部分操作员超载、部分闲置。他们将问题建模为 Assembly Line Balancing Problem（装配线平衡问题），使用 OR-Tools 的 CP-SAT 求解器，用三维布尔变量同时描述“任务-操作员-工位”的分配关系，并加入了预置工位约束、辅助任务约束、同组任务必须分配给同一操作员约束、以及非同时性约束。

落地效果（量化）：
- Smoothness Index 从 7.61 降至 2.87（降低 62%）
- 工位负荷均匀化到 89-90 分钟区间，标准差降低 94%
- 完全消除了过载工位

这个案例的价值在于：装配线平衡的约束逻辑（“某些任务必须在一起”“某些任务不能同时进行”）用线性规划写会非常别扭，但 CP-SAT 的全局约束天然适合表达这类规则。

另一个可参考的开源实现：GitHub 上的 Employee-Scheduler 项目用 OR-Tools CP-Solver 自动生成排班表，已实现的硬约束包括“每人每天最多一个班次”“具备相应技能”“同班次只能同团队”“每周最多 5 个工作日”“班次间至少 16 小时休息”“每周按早-晚-夜循环”等。这些规则直接来自真实排班的合规要求，可以直接参考其约束建模方式。

OR-Tools 官方也提供了护士排班的完整教程，核心约束包括：每个班次恰好分配一名护士、每名护士每天最多工作一个班次、班次分配尽可能均匀（每人在周期内至少 min_shifts_per_nurse 次、最多 max_shifts_per_nurse 次），用 `add_exactly_one` 和 `add_at_most_one` 表达。


### 路径规划：多中心铁路商品车配送

真实案例：中国铁路特货运北京分公司

该公司的业务是从多个配送中心向北京地区的 4S 店配送商品车。约束包括：每个中心可用车辆数有限、车辆必须从同一中心出发并返回、所有客户点必须被服务、禁止在配送中心之间运输。

技术方案（混合求解策略）：
- 系统同时运行 OR-Tools、遗传算法、蚁群算法、自定义启发式，输出多条路线方案供用户选择
- OR-Tools 算法运行时间 平均不到 5 分钟
- 自 2021 年试运行至今，已稳定处理北京分公司的日常配送需求

这个案例的工业意义在于：它不是追求单一“最优解”，而是提供多算法并行的方案池，让调度人员根据当天实际情况（临时订单、道路状况）做最终决策。OR-Tools 在其中承担了“快速生成高质量可行解”的角色。

OR-Tools 官方的 VRPTW 教程覆盖了配送路径优化的标准约束：时间窗（`time_windows`）、车辆数（`num_vehicles`）、旅行时间矩阵（`time_matrix`），通过 `AddDimension` 添加时间维度，并设置每个节点的累计时间变量范围。对于多仓库场景，还需要为每个车辆设置不同的起点和终点，并确保路径连续性。


### 纯线性模型（GLOP/PDLP）：大规模生产计划

真实案例：智利 CMPC Maderas 锯木厂生产计划优化

CMPC 是智利重要的木材企业，其锯木厂的生产计划长期依赖计划员的经验和历史数据，导致订单分配次优、计划耗时过长。他们将问题建模为线性规划模型，用 OR-Tools 求解器（GLOP/PDLP）解决，决策变量包括：每个工厂需要履行的订单数量、每个订单的生产周期、以及每个工序在具体机器上的执行时间。

落地效果（量化）：
- 需求满足率平均提升 7%
- 计划时间显著缩短
- 资源利用率和库存预判能力均有改善

这个案例的模型结构是典型的多工厂、多周期、多机器分配问题，约束涉及产能上限、时间限制、原材料用量，目标是满足需求的同时优化资源使用。OR-Tools 的 GLOP 求解器专门处理这类“变量为连续值（订单量、时间）的线性问题”。

OR-Tools 官方对求解器选型有明确指引：CP-SAT 擅长“何个、何物、何时”的整数决策问题；GLOP 擅长“比率、数量”的连续分配问题；PDLP 则面向“数百万级变量和约束”的超大规模线性问题。CMPC 的案例处于 GLOP 的典型适用区间。


### 三个 OR-Tools 求解器的工业选型速查

| 求解器 | 工业场景 | 核心优势 |
|---|---|---|
| CP-SAT | 排班、装配线平衡、任务分配 | 复杂逻辑约束（互斥、同组、非同时）表达自然 |
| Routing | 配送路径、多中心 VRP、带时间窗 VRP | 内置 VRP 专用算法，支持时间窗/容量/多起点终点 |
| GLOP/PDLP | 生产计划、资源分配、物料配比 | 连续变量线性规划，PDLP 支持超大规模 |

一句话总结：规则复杂逻辑强，用 CP-SAT；路径约束带时间窗，用 Routing；连续分配追求数学最优，用 GLOP。
