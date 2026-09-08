from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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
        messages.error(
            request,
            'You do not have permission to access this page.'
        )

        return redirect('student_dashboard')

    courses = request.user.courses.all()

    return render(
        request,
        'accounts/teacher_dashboard.html',
        {'courses': courses}
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
