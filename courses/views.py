from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Lesson
from .models import Course, Lesson, Enrollment, LessonProgress
from .forms import LessonForm
from django.utils import timezone
from notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()




def course_list(request):

    courses = Course.objects.all().order_by('-created_at')

    return render(request, 'courses/course_list.html', {
        'courses': courses
    })


@login_required
def create_course(request):

    # Only teachers can create courses
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can create courses.')
        return redirect('course_list')

    if request.method == 'POST':

        title = request.POST.get('title')
        description = request.POST.get('description')

        Course.objects.create(
            teacher=request.user,
            title=title,
            description=description
        )


         # Create notification for all students
        students = User.objects.filter(role='student')

        for student in students:

            Notification.objects.create(
                recipient=student,
                notification_type=Notification.COURSE_CREATED,
                message=f'New course "{course.title}" has been created.'
            )
        messages.success(request, 'Course created successfully!')

        return redirect('teacher_dashboard')

    return render(request, 'courses/create_course.html')


def course_detail(request, course_id):

    course = get_object_or_404(Course, id=course_id)

    is_enrolled = False

    if request.user.is_authenticated and request.user.role == 'student':

        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course
        ).exists()

    return render(
        request,
        'courses/course_detail.html',
        {
            'course': course,
            'is_enrolled': is_enrolled,
        }
    )

@login_required
def update_course(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id,
        teacher=request.user
    )

    if request.method == 'POST':

        course.title = request.POST.get('title')
        course.description = request.POST.get('description')

        course.save()

        messages.success(request, 'Course updated successfully!')
        return redirect('course_detail', course_id=course.id)

    return render(request, 'courses/create_course.html', {
        'course': course,
        'update': True
    })

@login_required
def delete_course(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id,
        teacher=request.user
    )

    if request.method == 'POST':
        course.delete()

        messages.success(request, 'Course deleted successfully!')
        return redirect('course_list')

    return redirect('course_detail', course_id=course.id)


@login_required
def enroll_course(request, course_id):

    # Only students can enroll
    if request.user.role != 'student':
        messages.error(request, 'Only students can enroll in courses.')
        return redirect('course_detail', course_id=course_id)

     # Get the course
    course = get_object_or_404(
        Course,
        id=course_id
    )
     # Only allow POST
    if request.method != 'POST':
        return redirect(
            'course_detail',
            course_id=course.id
        )

    # Check if already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )
    Notification.objects.create(
    recipient=course.teacher,
    notification_type=Notification.STUDENT_ENROLLED,
    message=f'{request.user.username} enrolled in "{course.title}".'
)

    if created:
        messages.success(
            request,
            f'You successfully enrolled in "{course.title}".'
        )
    else:
        messages.info(
            request,
            f'You are already enrolled in "{course.title}".'
        )

    return redirect('student_dashboard')

@login_required
def lesson_create(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    # Only the teacher who owns the course
    # can create lessons
    if request.user != course.teacher:
        messages.error(
            request,
            'You are not allowed to add lessons to this course.'
        )

        return redirect(
            'course_detail',
            course.id
        )

    if request.method == 'POST':

        form = LessonForm(request.POST)

        if form.is_valid():

            lesson = form.save(commit=False)

            lesson.course = course

            lesson.save()

            messages.success(
                request,
                'Lesson created successfully!'
            )

            return redirect(
                'course_detail',
                course.id
            )

    else:

        form = LessonForm()

    return render(
        request,
        'courses/lesson_create.html',
        {
            'form': form,
            'course': course
        }
    )
@login_required
def lesson_detail(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    # Teacher can view their own lesson
    if request.user == lesson.course.teacher:
        return render(
            request,
            'courses/lesson_detail.html',
            {
                'lesson': lesson
            }
        )

    # Student must be enrolled in the course
    if request.user.role == 'student':

        get_object_or_404(
            Enrollment,
            student=request.user,
            course=lesson.course
        )

        return render(
            request,
            'courses/lesson_detail.html',
            {
                'lesson': lesson
            }
        )

    messages.error(
        request,
        'You are not allowed to access this lesson.'
    )

    return redirect('course_list')

@login_required
def lesson_update(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    # Only the teacher who owns the course
    # can update the lesson
    if request.user != lesson.course.teacher:

        messages.error(
            request,
            'You are not allowed to update this lesson.'
        )

        return redirect(
            'course_detail',
            course_id=lesson.course.id
        )

    if request.method == 'POST':

        form = LessonForm(
            request.POST,
            instance=lesson
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Lesson updated successfully!'
            )

            return redirect(
                'lesson_detail',
                lesson_id=lesson.pk
            )

    else:
        form = LessonForm(
            instance=lesson
        )

    return render(
        request,
        'courses/lesson_update.html',
        {
            'form': form,
            'lesson': lesson
        }
    )


@login_required
def lesson_delete(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    course_id = lesson.course.id

    # Only course teacher can delete
    if request.user != lesson.course.teacher:

        messages.error(
            request,
            'You are not allowed to delete this lesson.'
        )

        return redirect(
            'course_detail',
            course_id
        )

    if request.method == 'POST':

        lesson.delete()

        messages.success(
            request,
            'Lesson deleted successfully!'
        )

        return redirect(
            'course_detail',
            course_id
        )

    return render(
        request,
        'courses/lesson_delete.html',
        {
            'lesson': lesson
        }
    )

@login_required
def student_learning(request, course_id):

    # Get course
    course = get_object_or_404(
        Course,
        id=course_id
    )

    # Student must be enrolled
    enrollment = get_object_or_404(
        Enrollment,
        student=request.user,
        course=course
    )

    # Get all lessons
    lessons = course.lessons.all().order_by('created_at')

    # Selected lesson
    lesson_id = request.GET.get('lesson')

    selected_lesson = None

    if lesson_id:
        selected_lesson = get_object_or_404(
            Lesson,
            id=lesson_id,
            course=course
        )

    # Mark lesson as complete
    if request.method == 'POST':

        lesson_id = request.POST.get('lesson_id')

        lesson = get_object_or_404(
            Lesson,
            id=lesson_id,
            course=course
        )

        LessonProgress.objects.update_or_create(
            student=request.user,
            lesson=lesson,
            defaults={
                'completed': True,
                'completed_at': timezone.now()
            }
        )
        Notification.objects.create(
    recipient=lesson.course.teacher,
    notification_type=Notification.COURSE_COMPLETED,
    message=(
        f'{request.user.username} completed '
        f'"{lesson.course.title}".'
    )
)

        return redirect(
            f'/learn/{course.id}/?lesson={lesson.id}'
        )

    # Get completed lessons
    completed_lessons = LessonProgress.objects.filter(
        student=request.user,
        lesson__course=course,
        completed=True
    )
    completed_lesson_ids = completed_lessons.values_list(
    'lesson_id',
    flat=True
    )

    completed_count = completed_lessons.count()
    total_lessons = lessons.count()

    # Calculate progress
    if total_lessons > 0:
        progress = int(
            (completed_count / total_lessons) * 100
        )
    else:
        progress = 0

    # Render page
    return render(
        request,
        'courses/student_learning.html',
        {
            'course': course,
            'lessons': lessons,
            'selected_lesson': selected_lesson,
            'enrollment': enrollment,
            'completed_lessons': completed_lessons,
            'completed_lesson_ids': completed_lesson_ids,
            'completed_count': completed_count,
            'total_lessons': total_lessons,
            'progress': progress,
        }
    )

