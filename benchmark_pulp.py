#!/usr/bin/env python3
"""
PuLP 性能基准测试模块
用于评估优化算法的性能和效率
"""

from pulp import *
import time
import psutil
import os
import statistics
from typing import Dict, List, Tuple
import json


class PulpBenchmark:
    """PuLP 性能基准测试类"""

    def __init__(self):
        self.results = {}

    def measure_memory_usage(self) -> float:
        """测量当前内存使用量（MB）"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024

    def benchmark_basic_production(self, iterations: int = 100) -> Dict:
        """基准测试基础生产计划问题"""
        print("🔧 运行基础生产计划基准测试...")

        times = []
        memories = []
        objectives = []

        for i in range(iterations):
            # 测量内存和时间的基准
            memory_before = self.measure_memory_usage()
            start_time = time.time()

            # 运行生产计划优化
            prob = LpProblem("Benchmark_Production", LpMaximize)

            x1 = LpVariable("Product_A", 0, None, LpInteger)
            x2 = LpVariable("Product_B", 0, None, LpInteger)

            prob += 30 * x1 + 20 * x2, "Total_Profit"
            prob += 2 * x1 + 1 * x2 <= 100, "Labor_Hours"
            prob += 1 * x1 + 3 * x2 <= 120, "Material_Units"
            prob += x1 + x2 <= 80, "Machine_Hours"

            prob.solve()

            end_time = time.time()
            memory_after = self.measure_memory_usage()

            # 记录结果
            times.append(end_time - start_time)
            memories.append(memory_after - memory_before)
            objectives.append(value(prob.objective))

        return {
            'time_avg': statistics.mean(times),
            'time_std': statistics.stdev(times),
            'time_min': min(times),
            'time_max': max(times),
            'memory_avg': statistics.mean(memories),
            'memory_max': max(memories),
            'objective_avg': statistics.mean(objectives),
            'iterations': iterations
        }

    def benchmark_large_scale(self) -> Dict:
        """基准测试大规模问题"""
        print("🚀 运行大规模问题基准测试...")

        memory_before = self.measure_memory_usage()
        start_time = time.time()

        # 创建大规模问题
        prob = LpProblem("Large_Scale_Production", LpMaximize)

        # 创建更多产品和约束
        num_products = 50
        products = []

        # 定义产品变量
        for i in range(num_products):
            product = LpVariable(f"Product_{i}", 0, 100, LpInteger)
            products.append(product)

        # 目标函数：最大化总利润
        profit_coefficients = [10 + i * 2 for i in range(num_products)]  # 不同利润
        prob += lpSum(profit_coefficients[i] * products[i] for i in range(num_products))

        # 添加多个资源约束
        num_constraints = 20
        for j in range(num_constraints):
            constraint_coeffs = [1 + (i + j) % 5 for i in range(num_products)]
            prob += lpSum(constraint_coeffs[i] * products[i] for i in range(num_products)) <= 500 * (j + 1)

        # 求解
        prob.solve()

        end_time = time.time()
        memory_after = self.measure_memory_usage()

        return {
            'solve_time': end_time - start_time,
            'memory_used': memory_after - memory_before,
            'num_variables': num_products,
            'num_constraints': num_constraints,
            'objective_value': value(prob.objective),
            'status': LpStatus[prob.status]
        }

    def benchmark_different_solvers(self) -> Dict:
        """基准测试不同求解器性能"""
        print("⚡ 比较不同求解器性能...")

        solvers = [
            ('PULP_CBC_CMD', 'CBC'),
            ('GLPK_CMD', 'GLPK'),
        ]

        solver_results = {}

        for solver_name, display_name in solvers:
            try:
                start_time = time.time()

                prob = LpProblem("Solver_Comparison", LpMaximize)
                x1 = LpVariable("x1", 0, 100, LpInteger)
                x2 = LpVariable("x2", 0, 100, LpInteger)
                prob += 3 * x1 + 2 * x2
                prob += 2 * x1 + x2 <= 100
                prob += x1 + x2 <= 80

                solver = getSolver(solver_name)
                prob.solve(solver)

                end_time = time.time()

                solver_results[display_name] = {
                    'solve_time': end_time - start_time,
                    'objective_value': value(prob.objective),
                    'status': LpStatus[prob.status],
                    'available': True
                }

            except PulpSolverError as e:
                solver_results[display_name] = {
                    'solve_time': None,
                    'objective_value': None,
                    'status': 'Unavailable',
                    'available': False,
                    'error': str(e)
                }

        return solver_results

    def run_all_benchmarks(self) -> Dict:
        """运行所有基准测试"""
        print("=" * 60)
        print("🎯 开始 PuLP 性能基准测试")
        print("=" * 60)

        self.results['basic_production'] = self.benchmark_basic_production(iterations=50)
        self.results['large_scale'] = self.benchmark_large_scale()
        self.results['solver_comparison'] = self.benchmark_different_solvers()

        self.generate_report()
        return self.results

    def generate_report(self):
        """生成性能测试报告"""
        print("\n" + "=" * 60)
        print("📊 性能测试报告")
        print("=" * 60)

        # 基础生产测试报告
        basic = self.results['basic_production']
        print(f"🔧 基础生产测试 (50次迭代):")
        print(f"  平均求解时间: {basic['time_avg']:.6f} 秒")
        print(f"  时间标准差: {basic['time_std']:.6f} 秒")
        print(f"  最快求解: {basic['time_min']:.6f} 秒")
        print(f"  最慢求解: {basic['time_max']:.6f} 秒")
        print(f"  平均内存使用: {basic['memory_avg']:.2f} MB")
        print(f"  最大内存使用: {basic['memory_max']:.2f} MB")
        print(f"  平均目标值: {basic['objective_avg']:.2f}")

        # 大规模问题报告
        large = self.results['large_scale']
        print(f"\n🚀 大规模问题测试:")
        print(f"  求解时间: {large['solve_time']:.3f} 秒")
        print(f"  内存使用: {large['memory_used']:.2f} MB")
        print(f"  变量数量: {large['num_variables']}")
        print(f"  约束数量: {large['num_constraints']}")
        print(f"  目标值: {large['objective_value']:.2f}")
        print(f"  求解状态: {large['status']}")

        # 求解器比较报告
        solvers = self.results['solver_comparison']
        print(f"\n⚡ 求解器性能比较:")
        for solver_name, result in solvers.items():
            if result['available']:
                print(f"  {solver_name}: {result['solve_time']:.3f} 秒, 目标值: {result['objective_value']}")
            else:
                print(f"  {solver_name}: 不可用")

        # 保存结果到文件
        with open('benchmark_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 详细结果已保存到: benchmark_results.json")


def performance_score_calculation(results: Dict) -> float:
    """计算性能得分 (0-100分)"""
    score = 100

    # 基础生产测试评分
    basic = results['basic_production']
    if basic['time_avg'] > 0.1:
        score -= 20
    elif basic['time_avg'] > 0.05:
        score -= 10

    if basic['memory_max'] > 50:
        score -= 10

    # 大规模问题评分
    large = results['large_scale']
    if large['solve_time'] > 5.0:
        score -= 15
    elif large['solve_time'] > 2.0:
        score -= 5

    # 求解器可用性评分
    solvers = results['solver_comparison']
    available_count = sum(1 for r in solvers.values() if r['available'])
    if available_count < 1:
        score -= 20

    return max(0, score)


if __name__ == "__main__":
    # 运行性能基准测试
    benchmark = PulpBenchmark()
    results = benchmark.run_all_benchmarks()

    # 计算性能得分
    performance_score = performance_score_calculation(results)
    print(f"\n🎯 性能得分: {performance_score:.1f}/100")

    # 根据得分给出评价
    if performance_score >= 90:
        print("✅ 优秀性能!")
    elif performance_score >= 70:
        print("⚠️ 良好性能，有优化空间")
    else:
        print("❌ 性能需要优化")

    # 退出码基于性能得分
    exit(0 if performance_score >= 60 else 1)