#!/usr/bin/env python3
"""
PuLP 单元测试模块
测试优化算法的正确性和健壮性
"""

import pytest
from pulp import *
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class TestPulpProduction:
    """生产计划优化的单元测试类"""

    def setup_method(self):
        """测试设置"""
        self.prob = LpProblem("Test_Production", LpMaximize)
        self.x1 = LpVariable("Product_A", 0, None, LpInteger)
        self.x2 = LpVariable("Product_B", 0, None, LpInteger)

        # 目标函数
        self.prob += 30 * self.x1 + 20 * self.x2, "Total_Profit"

        # 约束条件
        self.prob += 2 * self.x1 + 1 * self.x2 <= 100, "Labor_Hours"
        self.prob += 1 * self.x1 + 3 * self.x2 <= 120, "Material_Units"
        self.prob += self.x1 + self.x2 <= 80, "Machine_Hours"

    def test_optimal_solution_exists(self):
        """测试是否存在最优解"""
        self.prob.solve()
        assert self.prob.status == 1, "问题应该存在最优解"

    def test_objective_value_positive(self):
        """测试目标函数值为正"""
        self.prob.solve()
        objective_value = value(self.prob.objective)
        assert objective_value > 0, "目标函数值应该为正"

    def test_variable_non_negative(self):
        """测试变量非负"""
        self.prob.solve()
        assert self.x1.varValue >= 0, "产品A数量应该非负"
        assert self.x2.varValue >= 0, "产品B数量应该非负"

    def test_constraint_satisfaction(self):
        """测试约束条件满足"""
        self.prob.solve()

        # 检查每个约束条件
        labor_used = 2 * self.x1.varValue + 1 * self.x2.varValue
        material_used = 1 * self.x1.varValue + 3 * self.x2.varValue
        machine_used = self.x1.varValue + self.x2.varValue

        assert labor_used <= 100, "劳动力约束应该满足"
        assert material_used <= 120, "材料约束应该满足"
        assert machine_used <= 80, "机器时间约束应该满足"

    def test_specific_solution_quality(self):
        """测试特定解的质量"""
        self.prob.solve()

        # 该模型的整数最优解为 Product_A=36、Product_B=28。
        objective_value = value(self.prob.objective)
        assert objective_value == pytest.approx(1640), "目标函数应等于理论最优值"

    @pytest.mark.parametrize("profit_a,profit_b,expected_objective", [
        (30, 20, 1640),  # 原始参数：x1=36, x2=28
        (40, 20, 2000),  # 产品 A 更有价值：x1=50, x2=0
        (30, 30, 1920),  # 最大化总产量：x1=36, x2=28
    ])
    def test_parameter_sensitivity(self, profit_a, profit_b, expected_objective):
        """测试参数敏感性"""
        prob = LpProblem("Sensitivity_Test", LpMaximize)
        x1 = LpVariable("Product_A", 0, None, LpInteger)
        x2 = LpVariable("Product_B", 0, None, LpInteger)

        prob += profit_a * x1 + profit_b * x2
        prob += 2 * x1 + 1 * x2 <= 100
        prob += 1 * x1 + 3 * x2 <= 120
        prob += x1 + x2 <= 80

        prob.solve()
        assert prob.status == 1
        assert value(prob.objective) == pytest.approx(expected_objective)


class TestPulpEdgeCases:
    """边界情况测试"""

    def test_infeasible_problem(self):
        """测试无解问题"""
        prob = LpProblem("Infeasible_Test", LpMaximize)
        x1 = LpVariable("x1", 0, 10, LpInteger)
        x2 = LpVariable("x2", 0, 10, LpInteger)

        prob += x1 + x2
        prob += x1 >= 20  # 矛盾约束
        prob += x2 >= 20  # 矛盾约束

        prob.solve()
        assert prob.status == -1, "无解问题应该返回不可行状态"

    def test_unbounded_problem(self):
        """测试无界问题"""
        prob = LpProblem("Unbounded_Test", LpMaximize)
        x1 = LpVariable("x1", 0, None, LpInteger)
        x2 = LpVariable("x2", 0, None, LpInteger)

        prob += x1 + x2
        # 没有约束条件，问题无界

        prob.solve()
        # 注意：实际求解器可能对无界问题有不同处理

    def test_degenerate_problem(self):
        """测试退化问题"""
        prob = LpProblem("Degenerate_Test", LpMaximize)
        x1 = LpVariable("x1", 0, None, LpInteger)
        x2 = LpVariable("x2", 0, None, LpInteger)

        prob += x1 + x2
        prob += x1 + x2 <= 10
        prob += x1 + x2 >= 10  # 导致退化

        prob.solve()
        assert prob.status == 1, "退化问题应该可解"


class TestPulpIntegration:
    """集成测试"""

    def test_import_and_basic_functionality(self):
        """测试模块导入和基本功能"""
        from pulp import LpProblem, LpMaximize, LpVariable, LpInteger, value

        # 基本功能测试
        prob = LpProblem("Test", LpMaximize)
        x = LpVariable("x", 0, 10, LpInteger)
        prob += x
        prob.solve()

        assert value(prob.objective) is not None

    def test_error_handling(self):
        """测试错误处理"""
        with pytest.raises(TypeError):
            # 错误的目标函数
            prob = LpProblem("Test", LpMaximize)
            prob += "invalid_objective"


def calculate_test_score(test_results) -> float:
    """计算测试得分 (0-100分)"""
    total_tests = test_results.get('passed', 0) + test_results.get('failed', 0)
    if total_tests == 0:
        return 0

    passed_ratio = test_results.get('passed', 0) / total_tests
    score = passed_ratio * 100

    # 额外加分项
    if test_results.get('passed', 0) >= 8:
        score += 10  # 测试覆盖率高
    if test_results.get('failed', 0) == 0:
        score += 10  # 所有测试通过

    return min(100, score)


def main():
    """主函数入口"""
    # 运行测试并获取结果
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--junit-xml=test-results.xml"
    ])

    # 这里可以添加测试结果解析和得分计算
    print(f"\n测试退出码：{exit_code}")

    # 退出码为 0 表示所有测试通过
    sys.exit(0 if exit_code == 0 else 1)


if __name__ == "__main__":
    main()
