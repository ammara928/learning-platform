from django.conf import settings
from django.db import models


class Notification(models.Model):

    COURSE_CREATED = 'course_created'
    STUDENT_ENROLLED = 'student_enrolled'
    COURSE_COMPLETED = 'course_completed'

    NOTIFICATION_TYPES = [
        (COURSE_CREATED, 'Course Created'),
        (STUDENT_ENROLLED, 'Student Enrolled'),
        (COURSE_COMPLETED, 'Course Completed'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES
    )

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message



