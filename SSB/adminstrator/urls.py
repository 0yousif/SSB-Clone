from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.adminhome, name='admin_home'),
    path('register/', views.signupUser, name='admin_reg'),
    path('register/<int:user_id>', views.adminregstudent, name='admin_reg_profile'),

    # # TEMP just to easily see all registered users for now
    path('index', views.admindex, name='admindex'),

    path('semester/', views.SemesterCreate.as_view(), name='make_semester'),
    path('semester/<int:pk>/update',
         views.SemesterUpdate.as_view(), name='update_semester'),
    path('semester/list', views.SemesterList.as_view(), name='list_semester'),
    path('semester/<int:pk>', views.SemesterDetail.as_view(), name='see_semester'),
    path('semester/<int:pk>/delete',
         views.SemesterDelete.as_view(), name='delete_semester')


]
