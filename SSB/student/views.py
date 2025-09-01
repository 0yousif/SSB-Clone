from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from adminstrator.models import Profile, Section, Course, Departments, Semester, Location, Time, Section_schedules, Student_registration, Configurations
import datetime
from django.http import HttpResponse
from django.views.generic.edit import CreateView
from django.urls import reverse
from django.contrib import messages


from adminstrator.models import Admissions


def home(request):
    return render(request, 'home.html')


def redirect_user(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        return redirect('admin_home')

    profile_type = request.user.profile.user_type
    if (request.user.is_superuser):
        return redirect('admin_home')
    if (profile_type == 'student'):
        return redirect('dashboard')
    if profile_type == 'tutor':
        return redirect('faculty_dashboard')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


def getUserSections(request,):

    registeredSections = Section.objects.filter(
        crn__in=Student_registration.objects.filter(
            student=request.user).values_list('crn')
    )
    unregisteredSections = Section.objects.exclude(
        crn__in=Student_registration.objects.filter(
            student=request.user).values_list('crn')
    )

    return [registeredSections, unregisteredSections]


def registration(request):
    if Profile.objects.get(user=request.user).user_type != "student":
        return HttpResponse("Unauthorized")
    registeredSections, unregisteredSections = getUserSections(request)
    configs = Configurations.objects.first()
    return render(request, 'registration.html', {
        "unregisteredSections": unregisteredSections,
        "registeredSections": registeredSections,
        "configs": configs
    })


def isRegistered(request, section_id):
    sectionObj = Section.objects.get(crn=section_id)
    if Student_registration.objects.filter(student=request.user, crn=sectionObj).exists():
        return True
    else:
        return False


def isSectionFilled(section_id, max):
    return Student_registration.objects.filter(crn=section_id).count() >= max


def doesHaveEnoughCredits(request, newCredits, max):
    return (Profile.objects.get(user=request.user).total_credits_earned + newCredits) <= max


def section_register(request, section_id, user_id):
    currentUserProfile = Profile.objects.get(user=request.user)
    if currentUserProfile.user_type != "student":
        return HttpResponse("Unauthorized")
    configs = Configurations.objects.first()
    section = Section.objects.get(crn=section_id)
    course_credits = Course.objects.get(
        course_id=section.course_id).credit_hours
    now = datetime.datetime.now()

    # if the user is not already registered and there is a space in the section and the user has enough credits, if so the system will accept the registration

    if not isRegistered(request=request, section_id=section_id) and not isSectionFilled(section_id=section_id, max=configs.Section_limit) and doesHaveEnoughCredits(request=request, newCredits=course_credits, max=configs.credits_limit):
        Student_registration.objects.create(student=request.user, registration_status='registered',
                                            registered_date=f'{now.year}-{now.month}-{now.day}', crn=section)
        currentUserProfile.total_credits_earned += course_credits
        currentUserProfile.save()

    registeredSections, unregisteredSections = getUserSections(request)

    return render(request, 'registration.html', {"unregisteredSections": unregisteredSections, "registeredSections": registeredSections,
                                                 "configs": configs
                                                 })


def section_deregister(request, section_id, user_id):
    if Profile.objects.get(user=request.user).user_type != "student":
        return HttpResponse("Unauthorized")
    if isRegistered(request=request, section_id=section_id):
        Student_registration.objects.filter(
            student=request.user, crn=section_id).delete()
        course_credits = Course.objects.get(
            course_id=Section.objects.get(crn=section_id).course_id).credit_hours
        user_profile = Profile.objects.get(user=request.user)
        user_profile.total_credits_earned -= course_credits
        user_profile.save()

    registeredSections, unregisteredSections = getUserSections(request)

    configs = Configurations.objects.first()
    return render(request, 'registration.html', {"unregisteredSections": unregisteredSections, "registeredSections": registeredSections,
                                                 "configs": configs
                                                 })


def week_at_glance(request):
    return render(request, 'week_at_glance.html')


def enrolle_courses(request):
    registeredSections, unregisteredSections = getUserSections(request)
    configs = Configurations.objects.first()
    return render(request, 'enrolled_courses.html', {"registeredSections": registeredSections, "configs": configs})


@login_required
def student_profile(request):
    profile = request.user.profile
    return render(request, 'student_profile.html', {'profile': profile})


class admissionCreate(CreateView):
    model = Admissions
    fields = '__all__'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Your admission was submitted successfully!")
        return response


    def get_success_url(self):
        return reverse('student_login')
