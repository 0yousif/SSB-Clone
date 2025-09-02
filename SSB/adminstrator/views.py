from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Profile, Semester, Course, Section, Admissions, Section_schedules, Time, Location
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from SSB.settings import EMAIL_HOST_USER
from .forms import UserForm, StudentProfile, TutorProfile, studentLogin, Sections, SectionSchedule
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


@login_required
def signupUser(request):
    error_message = ""
    admission_data = request.session.get('admission_data')
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

    admission_data = request.session.get('admission_data')
    userProfile = Profile.objects.get(user_id=user_id)
    if request.method == 'POST':
        profile_form = StudentProfile(
            request.POST, request.FILES, instance=userProfile)
        if profile_form.is_valid():
            profile_form.save()

            # Email
            subject = 'Acceptance of Admission'
            message = f"""
            Dear {userProfile.first_name} {userProfile.last_name},
            Your academic number is: {userProfile.academic_number}
            Your password is: {userProfile.user.username}

            """
            address = str(userProfile.personal_email)
            send_mail(subject, message, EMAIL_HOST_USER,
                      [address], fail_silently=False)

            if admission_data is not None:

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


@login_required
def admission_session(request, admission_id):
    admission = Admissions.objects.get(id=admission_id)

    request.session['admission_data'] = {
        'id': admission.id,
        'username': admission.CPR,
        'first_name': admission.first_name,
        'last_name': admission.last_name,
        'personal_email': admission.email,
        'password': admission.CPR,
        'password2': admission.CPR,
        'school': admission.school,
        'gender': admission.gender,
        'dob': (admission.dob).isoformat(),
        'major': admission.major,
    }

    return redirect('admin_reg')


@login_required
def section_schedule(request, pk):
    section = Section.objects.get(pk=pk)

    try:
        schedule = Section_schedules.objects.get(crn=pk)
    except Section_schedules.DoesNotExist:
        schedule = None

    if request.method == 'POST':
        form = SectionSchedule(request.POST)

        if form.is_valid():
            set_schedule = form.save(commit=False)
            set_schedule.crn = section
            set_schedule.save()
            return redirect('section_detail', pk=section.crn)
    else:
        form = SectionSchedule(instance=schedule)

    return render(request, 'edit_section_schedule.html', {'form': form, 'section': section})


################## CBVs #################
class SemesterCreate(LoginRequiredMixin, CreateView):
    model = Semester
    fields = '__all__'
    success_url = '/administrator/semester/list'

    

class SemesterUpdate(LoginRequiredMixin, UpdateView):

    model = Semester
    fields = '__all__'
    success_url = '/administrator/semester/list'


class SemesterList(LoginRequiredMixin, ListView):
    model = Semester


class SemesterDetail(LoginRequiredMixin, DetailView):
    model = Semester


class SemesterDelete(LoginRequiredMixin, DeleteView):
    model = Semester
    success_url = '/administrator/semester/list'

# courses


class CourseCreate(LoginRequiredMixin, CreateView):
    model = Course
    fields = '__all__'
    success_url = '/administrator/course/list'


class CourseUpdate(LoginRequiredMixin, UpdateView):
    model = Course
    fields = '__all__'
    success_url = '/administrator/course/list'


class CourseList(LoginRequiredMixin, ListView):
    model = Course


class CourseDetail(LoginRequiredMixin, DetailView):
    model = Course


class CourseDelete(LoginRequiredMixin, DeleteView):
    model = Course
    success_url = '/administrator/course/list'

#######################################################


class SectionCreate(LoginRequiredMixin, CreateView):
    model = Section
    form_class = Sections
    success_url = '/administrator/section/list'



class SectionUpdate(LoginRequiredMixin, UpdateView):
    model = Section
    fields = '__all__'
    success_url = '/administrator/section/list'


class SectionList(LoginRequiredMixin, ListView):
    model = Section


class SectionDetail(LoginRequiredMixin, DetailView):
    model = Section


class SectionDelete(LoginRequiredMixin, DeleteView):
    model = Section
    success_url = '/administrator/section/list'

##### Time and place ###


class TimeEdit(LoginRequiredMixin, CreateView):
    model = Time
    fields = '__all__'

    def get_success_url(self):
        return self.request.GET.get('next', '/administrator/section/list')


class LocationEdit(LoginRequiredMixin, CreateView):
    model = Location
    fields = '__all__'

    def get_success_url(self):
        return self.request.GET.get('next', '/administrator/section/list')
