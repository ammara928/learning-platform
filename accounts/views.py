from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from courses.models import Course, Enrollment, LessonProgress, Lesson

from .forms import RegisterForm


def register_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            messages.success(
                request,
                'Account created successfully! Please login.'
            )

            return redirect('login')

    else:
        form = RegisterForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )


def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('dashboard')

        else:

            messages.error(
                request,
                'Invalid username or password.'
            )

    return render(
        request,
        'accounts/login.html'
    )


@login_required
def dashboard(request):

    if request.user.role == 'teacher':
        return redirect('teacher_dashboard')

    return redirect('student_dashboard')



@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        messages.error(request, "You are not authorized to access the teacher dashboard.")
        return redirect('student_dashboard')
    courses = Course.objects.filter(
        teacher=request.user
    )

    total_students = Enrollment.objects.filter(
        course__teacher=request.user
    ).values('student').distinct().count()

    total_lessons = Lesson.objects.filter(
        course__teacher=request.user
    ).count()

    context = {
        'courses': courses,
        'total_students': total_students,
        'total_lessons': total_lessons,
    }

    return render(
        request,
        'accounts/teacher_dashboard.html',
        context
    )


@login_required
def student_dashboard(request):

    if request.user.role != 'student':
        messages.error(
            request,
            'You do not have permission to access this page.'
        )

        return redirect('teacher_dashboard')

    enrollments = request.user.enrollments.select_related(
        'course'
    )

    return render(
        request,
        'accounts/student_dashboard.html',
        {'enrollments': enrollments}
    )


def logout_view(request):

    if request.method == 'POST':
        logout(request)
        return redirect('login')

    return redirect('dashboard')


@login_required
def course_students(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id,
        teacher=request.user
    )

    enrollments = Enrollment.objects.filter(
        course=course
    ).select_related('student')

    total_lessons = course.lessons.count()

    students = []

    for enrollment in enrollments:

        student = enrollment.student

        completed_lessons = LessonProgress.objects.filter(
            student=student,
            lesson__course=course,
            completed=True
        ).count()

        if total_lessons > 0:
            progress = int(
                (completed_lessons / total_lessons) * 100
            )
        else:
            progress = 0

        students.append({
            'student': student,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
            'progress': progress,
        })

    return render(
        request,
        'accounts/course_students.html',
        {
            'course': course,
            'students': students,
            'total_lessons': total_lessons,
        }
    )
