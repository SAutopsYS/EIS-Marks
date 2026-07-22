import csv
from pathlib import Path

from django.db import transaction

from academics.models import Mark, Student
from academics.services.cleaning import clean_marks, clean_name, validate_subject
from academics.services.parsing import parse_class, parse_date


def _better_marks(current, new):
    """Keep the higher mark. Any numeric mark beats Absent (None)."""
    if current is None:
        return new
    if new is None:
        return current
    return max(current, new)


def _clean_row(row, row_number):
    admission_no = str(row['admission_no']).strip()
    name = clean_name(row['student_name'])
    student_class = parse_class(row['class'], row_number)
    section = str(row['section']).strip()
    date_of_birth = parse_date(row['date_of_birth'], row_number)
    subject = validate_subject(row['subject'], row_number)

    try:
        marks_obtained = clean_marks(row['marks_obtained'])
    except ValueError as exc:
        raise ValueError(
            f'Row {row_number}: invalid marks_obtained {row["marks_obtained"]!r}'
        ) from exc

    return {
        'admission_no': admission_no,
        'name': name,
        'student_class': student_class,
        'section': section,
        'date_of_birth': date_of_birth,
        'subject': subject,
        'marks_obtained': marks_obtained,
    }


def _ensure_consistent_profile(profiles, cleaned, row_number):
    admission_no = cleaned['admission_no']
    profile = {
        'name': cleaned['name'],
        'student_class': cleaned['student_class'],
        'section': cleaned['section'],
        'date_of_birth': cleaned['date_of_birth'],
    }

    existing = profiles.get(admission_no)
    if existing is None:
        profiles[admission_no] = profile
        return

    for field in ('name', 'student_class', 'section', 'date_of_birth'):
        if existing[field] != profile[field]:
            raise ValueError(
                f'Row {row_number}: conflicting {field} for {admission_no}: '
                f'{existing[field]!r} vs {profile[field]!r}'
            )


def _read_and_prepare(csv_path):
    profiles = {}
    marks_by_key = {}
    rows_read = 0

    with open(csv_path, newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            rows_read += 1
            cleaned = _clean_row(row, row_number)
            _ensure_consistent_profile(profiles, cleaned, row_number)

            key = (cleaned['admission_no'], cleaned['subject'])
            if key in marks_by_key:
                marks_by_key[key] = _better_marks(
                    marks_by_key[key],
                    cleaned['marks_obtained'],
                )
            else:
                marks_by_key[key] = cleaned['marks_obtained']

    return rows_read, profiles, marks_by_key


def import_students_marks(csv_path):
    """Wipe and reload Student/Mark tables from a cleaned CSV export."""
    csv_path = Path(csv_path)
    if not csv_path.is_file():
        raise FileNotFoundError(f'CSV file not found: {csv_path}')

    rows_read, profiles, marks_by_key = _read_and_prepare(csv_path)

    students = [
        Student(
            admission_no=admission_no,
            name=profile['name'],
            student_class=profile['student_class'],
            section=profile['section'],
            date_of_birth=profile['date_of_birth'],
        )
        for admission_no, profile in profiles.items()
    ]

    marks = [
        Mark(
            student_id=admission_no,
            subject=subject,
            marks_obtained=marks_obtained,
        )
        for (admission_no, subject), marks_obtained in marks_by_key.items()
    ]

    with transaction.atomic():
        Mark.objects.all().delete()
        Student.objects.all().delete()
        Student.objects.bulk_create(students)
        Mark.objects.bulk_create(marks)

    absent_count = sum(1 for marks_obtained in marks_by_key.values() if marks_obtained is None)

    return {
        'rows_read': rows_read,
        'students_created': len(students),
        'marks_created': len(marks),
        'absents': absent_count,
    }
