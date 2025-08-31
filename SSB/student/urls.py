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
    path('enrolle_courses/',views.enrolle_courses, name='enrolle_courses')
]
