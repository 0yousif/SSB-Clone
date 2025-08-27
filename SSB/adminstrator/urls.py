from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.adminhome, name='admin_home'),

    # CBV
    path('register/', views.signupUser, name='admin_reg'),


    path('register/<int:user_id>', views.adminregstudent, name='admin_reg_profile'),

    # # TEMP just to easily see all registered users for now
    path('index', views.admindex, name='admindex')

]
