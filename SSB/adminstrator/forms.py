from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Profile, Section, Section_schedules
from django import forms
from django.forms import ModelChoiceField

from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm):
    choices = (('student', 'student'), ('tutor', 'tutor'))
    user_type = forms.ChoiceField(choices=choices, required=True)

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta(UserCreationForm):
        model = User
        # fields = '__all__'
        fields = ("username", "first_name", "last_name",
                  "password1", "password2", "user_type")


class StudentProfile(ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'dob',  'gender', 'department_id', "major", "school", "personal_email",
                  "current_semester", "status", "avatar")
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }


class TutorProfile(ModelForm):
    class Meta:

        model = Profile
        fields = ("first_name", "last_name", "dob", "gender",
                  "profession", "avatar")
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }


class studentLogin(forms.Form):
    academic_number = forms.IntegerField(label="Academic ID")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class TutorLogin(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class Sections(ModelForm):
    class Meta:
        model = Section

        fields = ['course', 'tutor', 'schedule_type', 'semester']

        print(fields)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tutor'].queryset = User.objects.filter(
            profile__user_type='tutor')

# https://stackoverflow.com/questions/22390416/setting-initial-django-form-field-value-in-the-init-method

# https://forum.djangoproject.com/t/about-lookups-that-span-relationships/2837

# django Spanning Relationships in Queries


class SectionSchedule(ModelForm):
    class Meta:
        model = Section_schedules
        fields = ['day_of_week', 'location', 'time']
