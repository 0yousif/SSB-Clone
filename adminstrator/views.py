from django.shortcuts import render, redirect
from .models import Profile, Semester, Course, Section, Admissions
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models import Q
from django.contrib.auth import authenticate, login

from .forms import UserForm, StudentProfile, TutorProfile, studentLogin, TutorLogin


@login_required
def signupUser(request):
    error_message = ""
    admission_data = request.session.get('admission_data')
    print("Admission data from session:", admission_data)
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            user.first_name = form.cleaned_data.get("first_name")
            user.last_name = form.cleaned_data.get("last_name")

            user.save()

            user_type = form.cleaned_data['user_type']
            # user_id = user.id

            profile = Profile.objects.create(
                user=user,
                user_type=user_type,
                first_name=user.first_name,
                last_name=user.last_name,
            )

            if (user_type == 'student'):
                return redirect('admin_reg_student_profile', user_id=user.id)
            elif (user_type == 'tutor'):
                return redirect('admin_reg_tutor_profile', user_id=user.id)
            else:
                return redirect('admindex')
        else:
            error_message = 'Invalid Signup - Try Again...'
    elif admission_data:
        form = UserForm(initial=admission_data)
    else:
        form = UserForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/register.html', context)

# Create your views here.


@login_required
def adminregstudent(request, user_id):
    # print("request.user.profile", request.user)

    admission_data = request.session.get('admission_data')
    userProfile = Profile.objects.get(user_id=user_id)
    if request.method == 'POST':
        profile_form = StudentProfile(
            request.POST, request.FILES, instance=userProfile)
        if profile_form.is_valid():
            profile_form.save()
            if  admission_data is not None:
                admission = Admissions.objects.get(
                    id=request.session['admission_data']['id'])
                admission.delete()
                del request.session['admission_data']
            return redirect('admindex')
    elif admission_data is not None:
        profile_form = StudentProfile(initial=admission_data)

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
    if 'admission_data' in request.session:
        del request.session['admission_data']

    return render(request, 'admin_home.html')


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


def student_login(request):
    error_message = ""
    if request.method == 'POST':
        form = studentLogin(request.POST)
        if form.is_valid():
            academic_number = form.cleaned_data['academic_number']
            password = form.cleaned_data['password']
            try:
                profile = Profile.objects.get(academic_number=academic_number)
            except Profile.DoesNotExist:
                error_message = "ID not found"
                context = {"form": form, "error_message": error_message}
                return render(request, 'auth/student_login.html', context)

            user = profile.user
            user = authenticate(
                request, username=user.username, password=password)
            if user:
                login(request, user)
                return redirect('redirect')
            else:
                error_message = 'Error logging in'
    else:
        form = studentLogin()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'auth/student_login.html', context)


class AdmissionsList(ListView):
    model = Admissions


def admission_session(request, admission_id):
    admission = Admissions.objects.get(id=admission_id)

    request.session['admission_data'] = {
        'id': admission.id,
        'username': admission.CPR,
        'first_name': admission.first_name,
        'last_name': admission.last_name,
        'personal_email': admission.email,
        'password1': admission.CPR,
        'school': admission.school,
        'gender': admission.gender,
        'dob': (admission.dob).isoformat(),
    }
    print("Admission from session:", request.session['admission_data'])
    print("Admission_____:", request.session['admission_data']['id'])

    return redirect('admin_reg')


########################## CBVs ###################################
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

class CourseCreate(CreateView):
    model = Course
    fields = '__all__'
    success_url = '/administrator/'


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
    success_url = '/administrator/'


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
