from django.contrib import admin
from django.urls import path,include
from . import views


urlpatterns = [
    path('redirect/', views.redirect_user, name='redirect'),
    path('',views.dashboard, name="dashboard"),
    path('profile/', views.student_profile, name='student_profile'),
    

]
