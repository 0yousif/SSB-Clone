from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from adminstrator.models import Profile, Section, Course, Departments, Semester, Location, Time, Section_schedules,Student_registration,Configurations
import datetime
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Value, F,ExpressionWrapper
from django.db.models.fields import BooleanField,IntegerField,CharField 
from .models import Student_plan
from .forms import StudentPlanForm
from django.urls import reverse

def redirect_user(request):
    profile_type = request.user.profile.user_type
    if (request.user.is_superuser):
        return redirect('/administrator')
    if (profile_type == 'student'):
        return redirect('dashboard')
    if profile_type == 'tutor':
        return redirect('faculty_dashboard')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def conflictCheck(request,registeredSections,unregisteredSection):
    unregisteredSchedules = Section_schedules.objects.filter(crn=unregisteredSection) 
    registeredSchedules = Section_schedules.objects.filter(crn__in=registeredSections.values_list('crn'))

    #  Checks if the end/start of the unregistered course is withing one of the registered ones
    for unregisteredSchedule in unregisteredSchedules:
        for registeredSchedule in registeredSchedules:
            if (registeredSchedule.time.start_time <= unregisteredSchedule.time.start_time and unregisteredSchedule.time.start_time <= registeredSchedule.time.end_time) or (registeredSchedule.time.start_time <= unregisteredSchedule.time.end_time and unregisteredSchedule.time.end_time <= registeredSchedule.time.end_time):      
                return True
    
    return False

@login_required
def getUserSections(request):
    currentSemester = Semester.objects.get(is_current=True)
    
    registeredSections = Section.objects.filter(
        crn__in=Student_registration.objects.filter(student=request.user).values_list('crn')
    ).filter(semester=currentSemester.semester)

    unregisteredSections = Section.objects.exclude(
        crn__in=Student_registration.objects.filter(student=request.user).values_list('crn')
        ).filter(semester=currentSemester.semester)

    for i in range(0, len(unregisteredSections)):
        unregisteredSections[i].conflict = conflictCheck(request,registeredSections,unregisteredSections[i])

    return [registeredSections,unregisteredSections]


@login_required
def registration(request):
    if Profile.objects.get(user=request.user).user_type != "student":
        return HttpResponse("Unauthorized")
    registeredSections,unregisteredSections = getUserSections(request)
    
    # Paginator set up 
    unregisteredSectionsPaginator = Paginator(unregisteredSections,10)
    pageNumber = request.GET.get('page')
    unregisteredSectionsPageObject = unregisteredSectionsPaginator.get_page(pageNumber)
    
    configs =  Configurations.objects.first()
    return render(request, 'registration.html', {
        "unregisteredSections":unregisteredSectionsPageObject,
        "registeredSections":registeredSections,
        "configs": configs
    })

def isRegistered(request,section_id):
    sectionObj = Section.objects.get(crn=section_id)
    if Student_registration.objects.filter(student = request.user, crn=sectionObj).exists():
        return True
    else:
        return False

def isSectionFilled(section_id,max):
    return Student_registration.objects.filter(crn=section_id).count() >= max 

def doesHaveEnoughCredits(request,newCredits, max):
    return (Profile.objects.get(user=request.user).total_credits_earned + newCredits ) <= max

@login_required
def section_register(request, section_id, user_id):
    currentUserProfile = Profile.objects.get(user=request.user) 
    currentSemester = Semester.objects.get(is_current=True)
    
    if currentUserProfile.user_type != "student":
        return HttpResponse("Unauthorized")    
    
    if currentSemester.registration_end  < datetime.date.today():
        return HttpResponse("Registration is not open currently")
    
    
    configs =  Configurations.objects.first()
    section = Section.objects.get(crn=section_id)
    course_credits = Course.objects.get(course_id=section.course_id).credit_hours
    now = datetime.datetime.now()
    # if the user is not already registered and there is a space in the section and the user has enough credits, if so the system will accept the registration

    registeredSections,unregisteredSections = getUserSections(request)
    if not isRegistered(request=request,section_id=section_id) and not isSectionFilled(section_id=section_id,max=configs.Section_limit) and doesHaveEnoughCredits(request=request,newCredits=course_credits,max=configs.credits_limit) and not conflictCheck(request,registeredSections,section_id) and section.semester == currentSemester.semester and currentSemester.registration_end  > datetime.date.today():
        Student_registration.objects.create(student = request.user, registration_status='registered',registered_date=f'{now.year}-{now.month}-{now.day}',crn=section)
        currentUserProfile.total_credits_earned += course_credits
        currentUserProfile.save()

    registeredSections,unregisteredSections = getUserSections(request)
    return render(request, 'registration.html', {"unregisteredSections":unregisteredSections,"registeredSections":registeredSections,
    "configs":configs
    })



@login_required
def section_deregister(request,section_id,user_id):
    currentSemester = Semester.objects.get(is_current=True)
    if Profile.objects.get(user=request.user).user_type != "student":
        return HttpResponse("Unauthorized")
    
    if currentSemester.registration_end  < datetime.date.today():
        return HttpResponse("Registration is not open currently")

    section = Section.objects.get(crn=section_id)
    
    if isRegistered(request=request,section_id=section_id) and section.semester == currentSemester.semester and currentSemester.registration_end  > datetime.date.today():
        Student_registration.objects.filter(student=request.user,crn=section_id).delete()
        course_credits = Course.objects.get(course_id=Section.objects.get(crn=section_id).course_id).credit_hours    
        user_profile =  Profile.objects.get(user=request.user)
        user_profile.total_credits_earned -= course_credits
        user_profile.save()
    
    registeredSections,unregisteredSections = getUserSections(request)
    
    configs =  Configurations.objects.first()
    return render(request, 'registration.html', {"unregisteredSections":unregisteredSections,"registeredSections":registeredSections,
    "configs": configs
    })

def week_at_glance(request):
    return render(request,'week_at_glance.html')

def enrolled_courses(request):
    registeredSections,unregisteredSections = getUserSections(request)
    configs =  Configurations.objects.first()
    return render(request,'enrolled_courses.html',{"registeredSections":registeredSections,"configs":configs})

@login_required
def student_profile(request):
    profile = request.user.profile
    return render(request, 'student_profile.html', {'profile': profile})

@login_required
def plan_ahead(request):
    courses = Course.objects.all()
    plans = Student_plan.objects.filter(student=request.user)
    newPlanForm = StudentPlanForm()
    currentPlan = ''
    if (request.GET.get('plan')):
        if plans.get(plan_id=int(request.GET.get('plan'))):
            currentPlan = plans.get(plan_id=int(request.GET.get('plan')))
        elif plans.get(plan_id=0):
            currentPlan = plans.get(plan_id=0)
    else:
        try:
            if plans.get(plan_id=0):
                currentPlan = plans.get(plan_id=0)
        except:
            currentPlan = ''



    return render(request, 'plan_ahead.html',{"courses":courses,"plans":plans,"newPlanForm":newPlanForm,'currentPlan':currentPlan})


@login_required
def new_plan(request):
    courses = Course.objects.all()
    plans = Student_plan.objects.filter(student=request.user)
    newPlanForm = StudentPlanForm()

    if request.method == 'POST':
        form = StudentPlanForm(request.POST)
        print(request.POST)
        if form.is_valid():
           new_plan_form = form.save(commit=False) 
           new_plan_form.student = request.user
           new_plan_form.save()
           print("plan created") 

    return render(request, 'plan_ahead.html',{"courses":courses,"plans":plans,"newPlanForm":newPlanForm})

@login_required
def delete_plan(request, plan_id):
    courses = Course.objects.all()
    plans = Student_plan.objects.filter(student=request.user)
    newPlanForm = StudentPlanForm()
    request.GET.get('plan')
    plan_id
    try:
        plan_to_delete = Student_plan.objects.get(plan_id=plan_id)
        if plan_to_delete.student == request.user:
            plan_to_delete.delete()
    except:
        return redirect('plan_ahead')
    
    return redirect('plan_ahead')
