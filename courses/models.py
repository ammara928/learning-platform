from django.db import models
from django.conf import settings


class Course(models.Model):

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses'
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )

    title = models.CharField(max_length=200)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Enrollment(models.Model):

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


class LessonProgress(models.Model):

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress'
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progress'
    )

    completed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('student', 'lesson')

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"




