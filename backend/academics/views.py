from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from academics.models import Mark, Student
from academics.serializers import (
    CorrectionSerializer,
    StudentDetailSerializer,
    StudentListSerializer,
)
from academics.services.aggregations import (
    student_total,
    subject_average,
    top_student_by_total,
)


def _first_error_message(errors):
    """Flatten serializer errors into one clear detail string."""
    if isinstance(errors, dict):
        for value in errors.values():
            return _first_error_message(value)
    if isinstance(errors, list):
        return str(errors[0])
    return str(errors)


class StudentListAPIView(generics.ListAPIView):
    serializer_class = StudentListSerializer

    def get_queryset(self):
        queryset = Student.objects.prefetch_related('marks').order_by('admission_no')
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class StudentDetailAPIView(generics.RetrieveAPIView):
    serializer_class = StudentDetailSerializer
    queryset = Student.objects.prefetch_related('marks')
    lookup_field = 'admission_no'


class SummaryAPIView(APIView):
    def get(self, request):
        subject_averages = {}
        for subject, _label in Mark.SUBJECT_CHOICES:
            marks = Mark.objects.filter(subject=subject).values_list(
                'marks_obtained',
                flat=True,
            )
            average = subject_average(marks)
            subject_averages[subject] = float(average) if average is not None else None

        student_rows = []
        students = Student.objects.prefetch_related('marks').order_by('admission_no')
        for student in students:
            marks = [mark.marks_obtained for mark in student.marks.all()]
            student_rows.append({
                'admission_no': student.admission_no,
                'name': student.name,
                'total': student_total(marks),
            })

        return Response(
            {
                'subject_averages': subject_averages,
                'top_student': top_student_by_total(student_rows),
            },
            status=status.HTTP_200_OK,
        )


class CorrectionAPIView(APIView):
    def post(self, request):
        serializer = CorrectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'detail': _first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        try:
            mark = Mark.objects.get(
                student_id=data['admission_no'],
                subject=data['subject'],
            )
        except Mark.DoesNotExist:
            return Response(
                {
                    'detail': (
                        f"no mark record for {data['admission_no']!r} "
                        f"in subject {data['subject']!r}"
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        mark.marks_obtained = data['marks']
        mark.save(update_fields=['marks_obtained'])

        return Response(
            {
                'admission_no': data['admission_no'],
                'subject': data['subject'],
                'marks': data['marks'],
            },
            status=status.HTTP_200_OK,
        )
