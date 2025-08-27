from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.dashboard, name="dashboard"),
    path('registration',views.registration, name="student-registration")
]
