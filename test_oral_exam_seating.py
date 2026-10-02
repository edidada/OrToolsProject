"""Tests for the oral English exam seating-plan generator."""

from ortools_project.examples.oral_exam_seating import ExamConfig, build_seating_plan


def test_classes_are_completed_in_order_and_seats_do_not_conflict():
    config = ExamConfig(class_count=3, students_per_class=10, seat_count=6)
    sessions = build_seating_plan(config)

    assert [(session.class_number, session.round_number) for session in sessions] == [
        (1, 1),
        (1, 2),
        (2, 1),
        (2, 2),
        (3, 1),
        (3, 2),
    ]
    assert [len(session.assignments) for session in sessions] == [6, 4, 6, 4, 6, 4]

    for session in sessions:
        seats = [seat for seat, _ in session.assignments]
        assert len(seats) == len(set(seats))
        assert all(1 <= seat <= config.seat_count for seat in seats)
