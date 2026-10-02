"""A small, runnable CP-SAT employee scheduling demonstration."""

from ortools.sat.python import cp_model


EMPLOYEES = ("Alice", "Bob")
SHIFTS = ("早班", "晚班")
DAYS = range(20)


def solve_schedule() -> dict[int, dict[str, str]]:
    """Build and solve a balanced schedule with daily shift rotation."""
    model = cp_model.CpModel()
    works = {
        (employee, day, shift): model.new_bool_var(f"{employee}_{day}_{shift}")
        for employee in EMPLOYEES
        for day in DAYS
        for shift in SHIFTS
    }

    for day in DAYS:
        for shift in SHIFTS:
            model.add_exactly_one(works[employee, day, shift] for employee in EMPLOYEES)
        for employee in EMPLOYEES:
            model.add_at_most_one(works[employee, day, shift] for shift in SHIFTS)

    # 防止员工连续两天被分到相同班次。原模型中两位员工完全对称，
    # 因此求解器可以合法地让同一人永远上早班、另一人永远上晚班。
    # 该约束使两人每天轮换早、晚班。
    for day in range(len(DAYS) - 1):
        for employee in EMPLOYEES:
            for shift in SHIFTS:
                model.add(works[employee, day, shift] + works[employee, day + 1, shift] <= 1)

    totals = [
        sum(works[employee, day, shift] for day in DAYS for shift in SHIFTS)
        for employee in EMPLOYEES
    ]
    difference = model.new_int_var(0, len(DAYS) * len(SHIFTS), "shift_difference")
    model.add_abs_equality(difference, totals[0] - totals[1])
    model.minimize(difference)

    solver = cp_model.CpSolver()
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("未找到可行排班")

    return {
        day: {
            shift: employee
            for shift in SHIFTS
            for employee in EMPLOYEES
            if solver.value(works[employee, day, shift])
        }
        for day in DAYS
    }


def main() -> None:
    """Print the solved schedule for use as a Poetry console command."""
    for day, assignments in solve_schedule().items():
        summary = "，".join(f"{shift}: {employee}" for shift, employee in assignments.items())
        print(f"第 {day + 1} 天，{summary}")


if __name__ == "__main__":
    main()
