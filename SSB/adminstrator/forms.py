from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Profile
from django import forms


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')


class ProfileForm(ModelForm):

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'dob',  'gender', 'department_id', 'profession',
                  'user_type', 'major', 'school', 'current_semester',  'status', 'avatar')
