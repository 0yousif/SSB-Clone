from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


from adminstrator.models import Profile, Section, Course, Departments, Semester, Location, Time, Section_schedules,Student_registration,Configurations, Attendance, Transcript, Grades, GRADE_CHOICES
import datetime
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Value, F,ExpressionWrapper
from django.db.models.fields import BooleanField,IntegerField,CharField 
from .models import Student_plan
from .forms import StudentPlanForm
from django.views.generic.edit import CreateView
from django.urls import reverse
from django.contrib import messages
from django import forms
from SSB.decorators import role_permission


from adminstrator.models import Admissions



def home(request):
    return render(request, 'home.html')

@login_required
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
    return redirect('home_page')


@login_required
@role_permission('student')
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
@role_permission('student')
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
def getUserSections(request, chosen_student=None):
    if chosen_student is None:
        chosen_student = request.user


    currentSemester = Semester.objects.get(is_current=True)
    
    registeredSections = Section.objects.filter(
        crn__in=Student_registration.objects.filter(student=chosen_student).values_list('crn')
    ).filter(semester=currentSemester.semester)

    unregisteredSections = Section.objects.exclude(
        crn__in=Student_registration.objects.filter(student=chosen_student).values_list('crn')
        ).filter(semester=currentSemester.semester)

    for i in range(0, len(unregisteredSections)):
        unregisteredSections[i].conflict = conflictCheck(request,registeredSections,unregisteredSections[i])

    return [registeredSections, unregisteredSections]


@login_required
@role_permission('student')
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
    if Student_registration.objects.filter(student=request.user, crn=sectionObj).exists():
        return True
    else:
        return False


def isSectionFilled(section_id, max):
    return Student_registration.objects.filter(crn=section_id).count() >= max


def doesHaveEnoughCredits(request, newCredits, max):
    return (Profile.objects.get(user=request.user).total_credits_earned + newCredits) <= max


@login_required
@role_permission('student')
def section_register(request, section_id, user_id):
    currentUserProfile = Profile.objects.get(user=request.user) 
    currentSemester = Semester.objects.get(is_current=True)
    
    if currentUserProfile.user_type != "student":
        return HttpResponse("Unauthorized")    
    
    if currentSemester.registration_end  < datetime.date.today():
        return HttpResponse("Registration is not open currently")
    
    
    configs =  Configurations.objects.first()
    section = Section.objects.get(crn=section_id)
    course_credits = Course.objects.get(
        course_id=section.course_id).credit_hours
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

    registeredSections, unregisteredSections = getUserSections(request)

    configs = Configurations.objects.first()
    return render(request, 'registration.html', {"unregisteredSections": unregisteredSections, "registeredSections": registeredSections,"configs": configs})

def week_at_glance(request):
    return render(request, 'week_at_glance.html')

def enrolled_courses(request):
    registeredSections,unregisteredSections = getUserSections(request)
    configs =  Configurations.objects.first()
    return render(request,'enrolled_courses.html',{"registeredSections":registeredSections,"configs":configs})

@login_required
def student_profile(request):
    profile = request.user.profile

    
    registeredSections, unregisteredSections = getUserSections(request)
    configs = Configurations.objects.first()

    return render(request, 'student_profile.html', {'profile': profile, "registeredSections":registeredSections, 'configs':configs})

@login_required
def get_current_plan(request,planGet):
    if (planGet):
        if plans.get(plan_id=int(planGet)):
            return plans.get(plan_id=int(planGet))
        elif plans.get(plan_id=0):
            return plans.get(plan_id=0)
    else:
        try:
            if plans.get(plan_id=0):
                return plans.get(plan_id=0)
        except:
            return ''
    return ''

@login_required
def plan_ahead(request):
    courses = Course.objects.all()
    plans = Student_plan.objects.filter(student=request.user)
    newPlanForm = StudentPlanForm()
    currentPlan = ''

    if (request.GET.get('plan')):
        if plans.get(plan_id=int(request.GET.get('plan'))):
            currentPlan =  plans.get(plan_id=int(request.GET.get('plan')))
        elif plans.get(plan_id=0):
            currentPlan = plans.get(plan_id=0)
    else:
        try:
            if plans.get(plan_id=0):
                currentPlan =  plans.get(plan_id=0)
        except:
            currentPlan = ''

    return render(request, 'plan_ahead.html',{"courses":courses,"plans":plans,"newPlanForm":newPlanForm,'currentPlan':currentPlan})


@login_required
def new_plan(request):
    if request.method == 'POST':
        form = StudentPlanForm(request.POST)
        print(request.POST)
        if form.is_valid():
           new_plan_form = form.save(commit=False) 
           new_plan_form.student = request.user
           new_plan_form.save()
           print("plan created") 
    
    return redirect('plan_ahead')


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

@login_required
def plan_add_section(request,plan_id,crn):
    if Student_plan.objects.filter(plan_id=plan_id,student=request.user,sections=crn).exists():
        courses = Course.objects.all()
        plans = Student_plan.objects.filter(student=request.user)
        newPlanForm = StudentPlanForm()
        currentPlan = get_current_plan(plan_id)

        return render(request, 'plan_ahead.html',{"courses":courses,"plans":plans,"newPlanForm":newPlanForm,'currentPlan':currentPlan})
        Student_plan.objects.filter(plan_id=plan_id,student=request.user).sections.add(crn)
    courses = Course.objects.all()
    plans = Student_plan.objects.filter(student=request.user)
    newPlanForm = StudentPlanForm()
    currentPlan = get_current_plan(plan_id)

    return render(request, 'plan_ahead.html',{"courses":courses,"plans":plans,"newPlanForm":newPlanForm,'currentPlan':currentPlan})

        



@login_required
def plan_remove_section(request,plan_id,crn):
    print("section added to the plan")
    return redirect('plan_ahead')

class admissionCreate(CreateView):
    model = Admissions
    fields = '__all__'
    widgets = {
        'dob': forms.DateInput(attrs={'type': 'date'}),
    }

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, "Your admission was submitted successfully!")
        return response

    def get_success_url(self):
        return reverse('student_login')


@login_required
def student_attendance(request):

        user = request.user
        current_semester = Semester.objects.get(is_current=True)
        registrations = Student_registration.objects.filter(student=user, crn__semester=current_semester)

        attendance_data = []
        for registration in registrations:
            course = registration.crn.course
            total_classes = 24  
            total_absences = Attendance.objects.filter(registration=registration, status='A').count()
            absence_rate = (total_absences / total_classes) * 100 if total_classes > 0 else 0

            attendance_data.append({
                'course_code': course.code, 
                'course_name': course.name,
                'crn': registration.crn.crn,
                'absence_rate': round(absence_rate, 2),
                'total_absences': total_absences,
                'total_classes': total_classes
            })

        return render(request, 'student_attendance.html', {'attendance_data':attendance_data})


#FORMULA
#SGPA =	Total of Semester Grade Points (sum of all GPV x sum of all Course Credits attempted) / Total of all Course Credits for the Semester
#Cumulative CGPA =	Total of all Grade Points (sum of all GPV x sum of all Course Credits) / Total of All Course Credits of all Semesters


@login_required
def transcript(request):
    grades = Grades.objects.filter(
        registration__student=request.user
    ).select_related(
        'registration__crn__semester',
        'registration__crn__course',
        'registration__crn__course__department',
        'registration'
    ).order_by('-registration__crn__semester__semester_id')
    
    semesters = {}
    for grade in grades:
        semester_id = grade.registration.crn.semester.semester_id
        if semester_id not in semesters:
            semesters[semester_id] = {
                'id': semester_id,
                'year': grade.registration.registered_date.year,
                'grades': []
            }
        semesters[semester_id]['grades'].append(grade)
    
    semester_data = [{'id': data['id'], 'year': data['year'], 'grades': data['grades']} 
                    for data in semesters.values()]
    
    profile = Profile.objects.get(user=request.user)
    
    return render(request, 'transcript.html', {
        'semester_data': semester_data,
        'overall_gpa': profile.gpa,
        'overall_attempted_credits': profile.total_credits_attempted,
        'overall_passed_credits': profile.total_credits_earned
    })
