from django.shortcuts import render, redirect
from .models import Profile, Semester, Course, Section
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models import Q


from .forms import UserForm, StudentProfile, TutorProfile


@login_required
def signupUser(request):
    error_message = ""
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            user.first_name = form.cleaned_data.get("first_name")
            user.last_name = form.cleaned_data.get("last_name")
            user.email = form.cleaned_data.get("email")

            user.save()

            user_type = form.cleaned_data['user_type']
            # user_id = user.id

            profile = Profile.objects.create(
                user=user,
                user_type=user_type,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,)

            if (user_type == 'student'):
                return redirect('admin_reg_student_profile', user_id=user.id)
            elif (user_type == 'tutor'):
                return redirect('admin_reg_tutor_profile', user_id=user.id)
            else:
                return redirect('admindex')
        else:
            error_message = 'Invalid Signup - Try Again...'
    else:
        form = UserForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/register.html', context)

# Create your views here.


@login_required
def adminregstudent(request, user_id):
    # print("request.user.profile", request.user)
    userProfile = Profile.objects.get(user_id=user_id)
    if request.method == 'POST':
        profile_form = StudentProfile(
            request.POST, request.FILES, instance=userProfile)
        if profile_form.is_valid():
            profile_form.save()

            return redirect('admindex')
    else:
        profile_form = StudentProfile(instance=userProfile)

    return render(request, 'registration/registerprofile.html', {'profile_form': profile_form, 'profile': userProfile})


@login_required
def adminregtutor(request, user_id):
    # print("request.user.profile", request.user)
    userProfile = Profile.objects.get(user_id=user_id)
    if request.method == 'POST':
        profile_form = TutorProfile(
            request.POST, request.FILES, instance=userProfile)
        if profile_form.is_valid():
            profile_form.save()

            return redirect('admindex')
    else:
        profile_form = TutorProfile(instance=userProfile)

    return render(request, 'registration/registerprofile.html', {'profile_form': profile_form, 'profile': userProfile})


@login_required
def adminhome(request):
    return render(request, 'home.html')


@login_required
def admindex(request):
    query = request.GET.get('q', '')
    if query:
        profiles = Profile.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(user_type__icontains=query) |
            Q(profession__icontains=query) |
            Q(academic_number__icontains=query)
        )
    else:
        profiles = Profile.objects.all()

    users = User.objects.all()

    return render(request, 'index.html', {'users': users, 'profiles': profiles})


class SemesterCreate(CreateView):
    model = Semester
    fields = '__all__'


class SemesterUpdate(UpdateView):
    model = Semester
    fields = '__all__'
    success_url = '/administrator/'


class SemesterList(ListView):
    model = Semester


class SemesterDetail(DetailView):
    model = Semester


class SemesterDelete(DeleteView):
    model = Semester
    success_url = '/administrator/semester/list'

# courses


class CourseCreate(CreateView):
    model = Course
    fields = '__all__'


class CourseUpdate(UpdateView):
    model = Course
    fields = '__all__'
    success_url = '/administrator/'


class CourseList(ListView):
    model = Course


class CourseDetail(DetailView):
    model = Course


class CourseDelete(DeleteView):
    model = Course
    success_url = '/administrator/course/list/'

#######################################################


class SectionCreate(CreateView):
    model = Section
    fields = '__all__'


class SectionUpdate(UpdateView):
    model = Section
    fields = '__all__'
    success_url = '/administrator/'


class SectionList(ListView):
    model = Section


class SectionDetail(DetailView):
    model = Section


class SectionDelete(DeleteView):
    model = Section
    success_url = '/administrator/section/list/'
