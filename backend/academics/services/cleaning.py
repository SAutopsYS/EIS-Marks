from typing import Optional

from academics.models import Mark

ALLOWED_SUBJECTS = {value for value, _label in Mark.SUBJECT_CHOICES}


def clean_name(raw_name: object) -> str:
    """Trim, collapse whitespace, and Title Case a student name."""
    parts = str(raw_name).strip().split()
    return ' '.join(parts).title()


def clean_marks(raw_marks: object) -> Optional[int]:
    """Blank marks mean Absent (None). Otherwise return an int."""
    if raw_marks is None:
        return None

    text = str(raw_marks).strip()
    if text == '':
        return None

    return int(text)


def validate_subject(raw_subject: object, row_number: int) -> str:
    """Return a canonical subject name, or raise if not allowed."""
    subject = str(raw_subject).strip()
    if subject not in ALLOWED_SUBJECTS:
        raise ValueError(
            f'Row {row_number}: invalid subject {subject!r}. '
            f'Allowed: {sorted(ALLOWED_SUBJECTS)}'
        )
    return subject
