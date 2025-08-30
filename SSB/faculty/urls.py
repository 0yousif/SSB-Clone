from django.urls import path
from . import views

urlpatterns = [
    path('', views.faculty_dashboard, name='faculty_dashboard'),
    path('students/', views.student_lookup, name='student_lookup'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('attendance/', views.take_attendance, name='take_attendance'),
    path('enrolledsections/', views.tutor_sections, name='tutor_sections'),



]
