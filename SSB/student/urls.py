from django.contrib import admin
from django.urls import path,include
from . import views


urlpatterns = [
    path('registration/',views.registration, name="student-registration"),
    path('redirect/', views.redirect_user, name='redirect'),
    path('dashboard/',views.dashboard, name="dashboard"),
    path('',views.home, name="home_page"),
    path('profile/', views.student_profile, name='student_profile'),
    path('registration/section/<int:section_id>/add/<int:user_id>', views.section_register, name="section_register"),
    path('registration/section/<int:section_id>/remove/<int:user_id>', views.section_deregister, name="section_deregister"),
    path('week_at_glance/',views.week_at_glance, name='week_at_glance'),
    path('enrolled_courses/',views.enrolled_courses, name='enrolled_courses'),
    path('plan_ahead/',views.plan_ahead, name='plan_ahead'),
    path('plan_ahead/new_plan',views.new_plan, name='new_plan'),
    path('plan_ahead/delete_plan/<int:plan_id>',views.delete_plan, name='delete_plan'),
    path('apply/', views.admissionCreate.as_view(), name='admission'),
    path('attendance/', views.student_attendance, name='attendance_report'),
]
