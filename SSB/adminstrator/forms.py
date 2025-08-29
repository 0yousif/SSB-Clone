from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Profile
from django import forms
from django.contrib.auth.forms import UserCreationForm


# class UserForm(ModelForm):
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password', 'first_name', 'last_name')

class UserForm(UserCreationForm):
    choices = (('student', 'student'), ('tutor', 'tutor'))
    user_type = forms.ChoiceField(choices=choices, required=True)

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=False)

    class Meta(UserCreationForm):
        model = User
        fields = '__all__'


# class ProfileForm(ModelForm):

#     class Meta:
#         model = Profile
#         fields = ('first_name', 'last_name', 'dob',  'gender', 'department_id', 'profession',
#                   'user_type', 'major', 'school', 'current_semester',  'status', 'avatar')

class StudentProfile(ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'dob',  'gender', 'department_id', "major", "school",
                  "current_semester", "status", "avatar")


class TutorProfile(ModelForm):
    class Meta:

        model = Profile
        fields = ("first_name", "last_name", "dob", "gender",
                  "department_id", "profession", "status", "avatar")
