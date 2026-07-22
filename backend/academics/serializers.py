from rest_framework import serializers

from academics.models import Mark, Student
from academics.services.aggregations import student_average, student_total

def _marks_list(student):
    """Collect mark values for a student (uses prefetched marks when available)."""
    return [mark.marks_obtained for mark in student.marks.all()]


def _average_to_json(average):
    """Convert Decimal averages to JSON numbers; keep None for no scored marks."""
    if average is None:
        return None
    return float(average)


class MarkSerializer(serializers.ModelSerializer):
    marks = serializers.IntegerField(source='marks_obtained', allow_null=True)

    class Meta:
        model = Mark
        fields = ['subject', 'marks']


class StudentListSerializer(serializers.ModelSerializer):
    dob = serializers.DateField(source='date_of_birth')
    average = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'admission_no',
            'name',
            'student_class',
            'section',
            'dob',
            'average',
        ]

    def get_average(self, student):
        return _average_to_json(student_average(_marks_list(student)))

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['class'] = data.pop('student_class')
        return data


class StudentDetailSerializer(serializers.ModelSerializer):
    dob = serializers.DateField(source='date_of_birth')
    marks = MarkSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    average = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'admission_no',
            'name',
            'student_class',
            'section',
            'dob',
            'marks',
            'total',
            'average',
        ]

    def get_total(self, student):
        return student_total(_marks_list(student))

    def get_average(self, student):
        return _average_to_json(student_average(_marks_list(student)))

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['class'] = data.pop('student_class')
        return data


class CorrectionSerializer(serializers.Serializer):
    admission_no = serializers.CharField()
    subject = serializers.ChoiceField(choices=Mark.SUBJECT_CHOICES)
    marks = serializers.IntegerField(min_value=0, max_value=100)

    def validate_admission_no(self, admission_no):
        admission_no = admission_no.strip()
        if not Student.objects.filter(pk=admission_no).exists():
            raise serializers.ValidationError(
                f'student with admission_no {admission_no!r} does not exist'
            )
        return admission_no
