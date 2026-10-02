"""A runnable PuLP production-planning example."""

from pulp import LpInteger, LpMaximize, LpProblem, LpStatus, LpVariable, value


def production_planning_example() -> None:
    """Solve and print a small integer production-planning problem."""
    prob = LpProblem("Production_Planning", LpMaximize)
    product_a = LpVariable("Product_A", 0, None, LpInteger)
    product_b = LpVariable("Product_B", 0, None, LpInteger)

    prob += 30 * product_a + 20 * product_b, "Total_Profit"
    prob += 2 * product_a + product_b <= 100, "Labor_Hours"
    prob += product_a + 3 * product_b <= 120, "Material_Units"
    prob += product_a + product_b <= 80, "Machine_Hours"

    prob.solve()

    print("=" * 50)
    print("生产计划优化结果")
    print("=" * 50)
    print(f"求解状态: {LpStatus[prob.status]}")
    print(f"最大利润: {value(prob.objective)} 元")
    print(f"产品A生产数量: {product_a.varValue} 个")
    print(f"产品B生产数量: {product_b.varValue} 个")

    print("\n资源使用情况:")
    for name, constraint in prob.constraints.items():
        # PuLP stores the right-hand side as the negated constant, while
        # value() returns the residual (left-hand side minus right-hand side).
        limit = -constraint.constant
        used = constraint.value() + limit
        print(f"{name}: 使用 {used} / 限制 {limit}")


def main() -> None:
    """Run the example through ``poetry run pulp-example``."""
    production_planning_example()
