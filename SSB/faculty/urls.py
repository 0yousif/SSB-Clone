from django.urls import path
from . import views

urlpatterns = [
    path('', views.faculty_dashboard, name='faculty_dashboard'),
    path('students/', views.student_lookup, name='student_lookup'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('attendance/', views.take_attendance, name='take_attendance'),
    path('sections/', views.tutor_sections, name='tutor_sections'),
    path('sections/students/<int:crn>/', views.section_students, name='section_students'),



]
