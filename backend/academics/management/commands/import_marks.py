from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from academics.services.import_service import import_students_marks


class Command(BaseCommand):
    help = 'Wipe and reload students/marks from the ERP CSV export.'

    def add_arguments(self, parser):
        default_csv = Path(settings.BASE_DIR).parent / 'data' / 'students_marks.csv'
        parser.add_argument(
            '--csv',
            dest='csv_path',
            default=str(default_csv),
            help='Path to students_marks.csv',
        )

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        self.stdout.write(f'Importing from {csv_path}')

        try:
            result = import_students_marks(csv_path)
        except (OSError, ValueError) as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS(
            'Import complete: '
            f"rows_read={result['rows_read']}, "
            f"students={result['students_created']}, "
            f"marks={result['marks_created']}, "
            f"absents={result['absents']}"
        ))
