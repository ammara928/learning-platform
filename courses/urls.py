from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('create/', views.create_course, name='create_course'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/update/', views.update_course, name='update_course'),
    path('course/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    # path('<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),


    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('course/<int:course_id>/lessons/create/', views.lesson_create, name='lesson_create'),

    path('lesson/<int:lesson_id>/edit/', views.lesson_update, name='lesson_update'),

    path('lesson/<int:lesson_id>/delete/', views.lesson_delete, name='lesson_delete'),

    


path('learn/<int:course_id>/', views.student_learning, name='student_learning'),


]


    

    # path('lessons/create/', views.lesson_create, name='lesson_create'),

    # path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),

    # path('lessons/<int:lesson_id>/edit/', views.lesson_update, name='lesson_update'),

    # path('lessons/<int:lesson_id>/delete/', views.lesson_delete, name='lesson_delete'),
