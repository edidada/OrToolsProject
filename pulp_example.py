from pulp import *

def production_planning_example():
    """
    生产计划问题：
    公司生产两种产品A和B，每个产品需要不同的资源
    目标：最大化利润
    """
    # 创建问题实例（最大化问题）
    prob = LpProblem("Production_Planning", LpMaximize)

    # 定义决策变量（产品A和B的生产数量）
    x1 = LpVariable("Product_A", 0, None, LpInteger)  # 产品A，非负整数
    x2 = LpVariable("Product_B", 0, None, LpInteger)  # 产品B，非负整数

    # 目标函数：最大化利润
    # 产品A利润30元/个，产品B利润20元/个
    prob += 30 * x1 + 20 * x2, "Total_Profit"

    # 约束条件
    prob += 2 * x1 + 1 * x2 <= 100, "Labor_Hours"  # 劳动力约束：100小时
    prob += 1 * x1 + 3 * x2 <= 120, "Material_Units"  # 材料约束：120单位
    prob += x1 + x2 <= 80, "Machine_Hours"  # 机器时间约束：80小时

    # 求解问题
    prob.solve()

    # 输出结果
    print("=" * 50)
    print("生产计划优化结果")
    print("=" * 50)
    print(f"求解状态: {LpStatus[prob.status]}")
    print(f"最大利润: {value(prob.objective)} 元")
    print(f"产品A生产数量: {x1.varValue} 个")
    print(f"产品B生产数量: {x2.varValue} 个")

    # 打印约束条件的使用情况
    print("\n资源使用情况:")
    for name, constraint in prob.constraints.items():
        print(f"{name}: 使用 {constraint.value()} / 限制 {constraint.constant}")


if __name__ == "__main__":
    production_planning_example()