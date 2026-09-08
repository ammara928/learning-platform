from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Lesson
from .forms import LessonForm

from .models import Course, Enrollment


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

        messages.success(request, 'Course created successfully!')
        return redirect('course_list')

    return render(request, 'courses/create_course.html')


def course_detail(request, course_id):

    course = get_object_or_404(Course, id=course_id)

    return render(request, 'courses/course_detail.html', {
        'course': course
    })

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

    return render(
        request,
        'courses/lesson_detail.html',
        {
            'lesson': lesson
        }
    )

@login_required
def lesson_update(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)

        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully!")
            return redirect('lesson_detail', lesson_id=lesson.pk)

    else:
        form = LessonForm(instance=lesson)

    return render(request, 'courses/lesson_update.html', {
        'form': form,   'lesson': lesson,
    })


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

    # Get the course
    course = get_object_or_404(
        Course,
        id=course_id
    )

    # Check that the student is enrolled
    enrollment = get_object_or_404(
        Enrollment,
        student=request.user,
        course=course
    )

    # Get all lessons of this course
    lessons = course.lessons.all().order_by('created_at')

    # Get selected lesson from URL
    lesson_id = request.GET.get('lesson')

    selected_lesson = None

    if lesson_id:
        selected_lesson = get_object_or_404(
            Lesson,
            id=lesson_id,
            course=course
        )

    return render(
        request,
        'courses/student_learning.html',
        {
            'course': course,
            'lessons': lessons,
            'selected_lesson': selected_lesson,
            'enrollment': enrollment,
        }
    )

