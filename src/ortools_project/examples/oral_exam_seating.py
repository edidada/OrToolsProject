"""Create sequential computer-room seating plans for oral English exams."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from ortools.sat.python import cp_model


DEFAULT_CONFIG_PATH = Path("config/oral_exam_seating.json")


@dataclass(frozen=True)
class ExamConfig:
    """Input values read from the seating-plan configuration file."""

    class_count: int
    students_per_class: int
    seat_count: int

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> "ExamConfig":
        """Validate the required n, m and x values from a JSON object."""
        try:
            n, m, x = (values[key] for key in ("n", "m", "x"))
        except KeyError as error:
            raise ValueError("配置文件必须包含 n、m 和 x") from error

        if any(isinstance(value, bool) or not isinstance(value, int) for value in (n, m, x)):
            raise ValueError("n、m 和 x 必须是正整数")
        if n <= 0 or m <= 0 or x <= 0:
            raise ValueError("n、m 和 x 必须是正整数")
        return cls(class_count=n, students_per_class=m, seat_count=x)


@dataclass(frozen=True)
class ExamSession:
    """One consecutive exam session for a single class."""

    session_number: int
    class_number: int
    round_number: int
    assignments: tuple[tuple[int, str], ...]


def load_config(path: Path) -> ExamConfig:
    """Read and validate a JSON configuration file."""
    try:
        values = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"找不到配置文件：{path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"配置文件不是有效 JSON：{error.msg}") from error

    if not isinstance(values, dict):
        raise ValueError("配置文件的根节点必须是 JSON 对象")
    return ExamConfig.from_mapping(values)


def assign_seats(student_names: Sequence[str], seat_count: int) -> tuple[tuple[int, str], ...]:
    """Use CP-SAT to assign every student in one session a distinct seat."""
    model = cp_model.CpModel()
    seat_vars = [
        model.new_int_var(1, seat_count, f"seat_{student_index}")
        for student_index in range(len(student_names))
    ]
    model.add_all_different(seat_vars)

    # Prefer low-numbered students in low-numbered seats.  The descending
    # weights make the printed plan deterministic and leave unused seats at
    # the end of the room.
    model.minimize(
        sum((len(student_names) - student_index) * seat_var for student_index, seat_var in enumerate(seat_vars))
    )

    solver = cp_model.CpSolver()
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("无法为本场次生成座位")

    return tuple(
        sorted(
            ((solver.value(seat_var), student_name) for seat_var, student_name in zip(seat_vars, student_names)),
            key=lambda assignment: assignment[0],
        )
    )


def build_seating_plan(config: ExamConfig) -> list[ExamSession]:
    """Schedule each class completely before creating sessions for the next class."""
    sessions: list[ExamSession] = []
    session_number = 1

    for class_number in range(1, config.class_count + 1):
        students = [f"{class_number}班-学生{student_number:02d}" for student_number in range(1, config.students_per_class + 1)]
        for round_index, start in enumerate(range(0, len(students), config.seat_count), start=1):
            current_students = students[start : start + config.seat_count]
            sessions.append(
                ExamSession(
                    session_number=session_number,
                    class_number=class_number,
                    round_number=round_index,
                    assignments=assign_seats(current_students, config.seat_count),
                )
            )
            session_number += 1

    return sessions


def format_seating_plan(config: ExamConfig, sessions: Sequence[ExamSession]) -> str:
    """Render a human-readable, seat-by-seat exam plan."""
    lines = [
        "英语机房口语考试座位安排",
        f"班级数: {config.class_count}；每班人数: {config.students_per_class}；机房座位: {config.seat_count}",
    ]
    for session in sessions:
        lines.append(f"\n第 {session.session_number} 场：{session.class_number} 班，第 {session.round_number} 轮")
        assigned_students = dict(session.assignments)
        for seat_number in range(1, config.seat_count + 1):
            student = assigned_students.get(seat_number, "空闲")
            lines.append(f"  座位 {seat_number:02d}: {student}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse the optional JSON configuration path."""
    parser = argparse.ArgumentParser(description="生成英语口语考试机房座位表")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="包含 n、m、x 的 JSON 配置文件")
    return parser.parse_args()


def main() -> None:
    """Load configuration and print the consecutive class-by-class seating plan."""
    args = parse_args()
    config = load_config(args.config)
    print(format_seating_plan(config, build_seating_plan(config)))


if __name__ == "__main__":
    main()
