from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable, Optional


ONE_PLACE = Decimal('0.1')


def filter_scored_marks(marks: Iterable[Optional[int]]) -> list[int]:
    """Return only non-absent marks (drop None)."""
    return [mark for mark in marks if mark is not None]


def student_total(marks: Iterable[Optional[int]]) -> int:
    """Sum of non-absent marks. Absents are ignored, not treated as zero."""
    return sum(filter_scored_marks(marks))


def student_average(marks: Iterable[Optional[int]]) -> Optional[Decimal]:
    """
    Mean of non-absent marks, rounded to one decimal place (ROUND_HALF_UP).
    Returns None when the student has no scored subjects.
    """
    scored = filter_scored_marks(marks)
    if not scored:
        return None

    average = Decimal(sum(scored)) / Decimal(len(scored))
    return average.quantize(ONE_PLACE, rounding=ROUND_HALF_UP)


def subject_average(marks: Iterable[Optional[int]]) -> Optional[Decimal]:
    """Class average for one subject. Same rules as student_average."""
    return student_average(marks)


def top_student_by_total(student_totals) -> Optional[dict]:
    """Pick highest total; ties break by lowest admission_no."""
    students = list(student_totals)
    if not students:
        return None

    return min(
        students,
        key=lambda item: (-item['total'], item['admission_no']),
    )
