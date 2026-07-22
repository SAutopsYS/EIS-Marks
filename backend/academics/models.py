from django.db import models


class Student(models.Model):
    admission_no = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    student_class = models.PositiveSmallIntegerField()
    section = models.CharField(max_length=5)
    date_of_birth = models.DateField()

    def __str__(self):
        return f'{self.admission_no} - {self.name}'


class Mark(models.Model):
    SUBJECT_ENGLISH = 'English'
    SUBJECT_HINDI = 'Hindi'
    SUBJECT_MATHS = 'Maths'
    SUBJECT_SCIENCE = 'Science'
    SUBJECT_SOCIAL_SCIENCE = 'Social Science'

    SUBJECT_CHOICES = [
        (SUBJECT_ENGLISH, 'English'),
        (SUBJECT_HINDI, 'Hindi'),
        (SUBJECT_MATHS, 'Maths'),
        (SUBJECT_SCIENCE, 'Science'),
        (SUBJECT_SOCIAL_SCIENCE, 'Social Science'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='marks',
    )
    subject = models.CharField(max_length=32, choices=SUBJECT_CHOICES)
    # NULL means the student was absent for this exam.
    marks_obtained = models.IntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'subject'],
                name='unique_student_subject',
            ),
        ]

    def __str__(self):
        marks = self.marks_obtained if self.marks_obtained is not None else 'Absent'
        return f'{self.student.admission_no} - {self.subject}: {marks}'
