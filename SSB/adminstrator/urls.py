from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.adminhome, name='admin_home'),
    path('register/', views.signupUser, name='admin_reg'),

    path('register/student/<int:user_id>', views.adminregstudent,
         name='admin_reg_student_profile'),
    path('register/tutor/<int:user_id>', views.adminregtutor,
         name='admin_reg_tutor_profile'),

    path('index', views.admindex, name='admindex'),

    path('login/student', views.student_login, name='student_login'),


    # semester CBVs
    path('semester/', views.SemesterCreate.as_view(), name='make_semester'),
    path('semester/<int:pk>/update',
         views.SemesterUpdate.as_view(), name='update_semester'),
    path('semester/list', views.SemesterList.as_view(), name='list_semesters'),
    path('semester/<int:pk>', views.SemesterDetail.as_view(), name='semester_detail'),
    path('semester/<int:pk>/delete',
         views.SemesterDelete.as_view(), name='delete_semester'),

    # courses CBVs
    path('courses/', views.CourseCreate.as_view(), name='make_course'),
    path('course/<int:pk>/update',
         views.CourseUpdate.as_view(), name='update_course'),
    path('course/list', views.CourseList.as_view(), name='List_courses'),
    path('course/<int:pk>', views.CourseDetail.as_view(), name='course_detail'),
    path('course/<int:pk>/delete',
         views.CourseDelete.as_view(), name='delete_course'),


    # Sections CBVs
    path('section/', views.SectionCreate.as_view(), name='make_section'),
    path('section/<int:pk>/update',
         views.SectionUpdate.as_view(), name='update_section'),
    path('section/list', views.SectionList.as_view(), name='list_sections'),
    path('section/<int:pk>', views.SectionDetail.as_view(), name='section_detail'),
    path('section/<int:pk>/delete',
         views.SectionDelete.as_view(), name='delete_section'),
    path('section/<int:pk>/schedules',
         views.section_schedule, name='edit_section_schedule'),

    # admissions CBVs
    path('admissions/', views.AdmissionsList.as_view(), name='admin_admission'),
    path("admissions/<int:admission_id>/",
         views.admission_session, name="admission_session"),

     path('locations/', views.LocationEdit.as_view(), name='edit_locations'),
     path('times/', views.TimeEdit.as_view(), name='edit_times'),

]
