"""Tests for the runnable CP-SAT scheduling demonstration."""

from ortools_project.examples.cp_sat_schedule import DAYS, EMPLOYEES, SHIFTS, solve_schedule


def test_schedule_covers_every_shift_and_rotates_employees():
    schedule = solve_schedule()

    assert set(schedule) == set(DAYS)
    for day in DAYS:
        assert set(schedule[day]) == set(SHIFTS)
        assert set(schedule[day].values()) == set(EMPLOYEES)

    for day in range(len(DAYS) - 1):
        for shift in SHIFTS:
            assert schedule[day][shift] != schedule[day + 1][shift]
