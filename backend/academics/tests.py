import tempfile
from datetime import date
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from academics.models import Mark, Student
from academics.services.aggregations import student_average
from academics.services.import_service import import_students_marks
from academics.views import CorrectionAPIView


class DuplicateMarkImportTests(TestCase):
    def test_duplicate_rows_keep_higher_mark(self):
        csv_text = (
            'admission_no,student_name,class,section,date_of_birth,'
            'subject,marks_obtained,max_marks\n'
            'EIS-1001,Test Student,6,A,2014-01-15,Maths,64,100\n'
            'EIS-1001,Test Student,6,A,2014-01-15,Maths,78,100\n'
        )
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.csv',
            delete=False,
            encoding='utf-8',
        ) as handle:
            handle.write(csv_text)
            csv_path = handle.name

        import_students_marks(csv_path)

        mark = Mark.objects.get(student_id='EIS-1001', subject='Maths')
        self.assertEqual(mark.marks_obtained, 78)
        self.assertEqual(Mark.objects.count(), 1)


class AverageCalculationTests(TestCase):
    def test_absent_marks_excluded_from_average(self):
        average = student_average([80, None, 90])
        self.assertEqual(average, Decimal('85.0'))


class CorrectionValidationTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        student = Student.objects.create(
            admission_no='EIS-1007',
            name='Vivaan Pandey',
            student_class=6,
            section='A',
            date_of_birth=date(2014, 10, 16),
        )
        Mark.objects.create(
            student=student,
            subject='Maths',
            marks_obtained=54,
        )

    def test_corrections_api_rejects_invalid_marks(self):
        request = self.factory.post(
            '/api/marks/corrections/',
            {
                'admission_no': 'EIS-1007',
                'subject': 'Maths',
                'marks': 105,
            },
            format='json',
        )
        response = CorrectionAPIView.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)
        self.assertEqual(
            Mark.objects.get(student_id='EIS-1007', subject='Maths').marks_obtained,
            54,
        )
