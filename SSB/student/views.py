from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from adminstrator.models import Profile, Section, Course, Departments, Semester, Location, Time, Section_schedules,Student_registration,Configurations, Attendance, Transcript, Grades, GRADE_CHOICES
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
#TGPA =	Total of Semester Grade Points (sum of all GPV x sum of all Course Credits attempted) / Total of all Course Credits for the Semester

# Cumulative CGPA =	Total of all Grade Points (sum of all GPV x sum of all Course Credits) / Total of All Course Credits of all Semesters


@login_required
def transcript(request):
    grade_dict = dict(GRADE_CHOICES)
    
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
        course_credits = grade.registration.crn.course.credit_hours
        registration_year = grade.registration.registered_date.year
        
        if semester_id not in semesters:
            semesters[semester_id] = {
                'id': semester_id,
                'year': registration_year,  
                'grades': [],
                'total_grade_points': 0,
                'total_attempted_credits': 0,
                'total_passed_credits': 0,
                'gpa': 0
            }
        
        grade_point = grade_dict.get(grade.grade, 0)
        gpv = grade_point * course_credits
        
        semesters[semester_id]['grades'].append(grade)
        semesters[semester_id]['total_grade_points'] += gpv
        semesters[semester_id]['total_attempted_credits'] += course_credits
        
        if grade.grade != 'F':
            semesters[semester_id]['total_passed_credits'] += course_credits
    
    semester_data = []
    cumulative_grade_points = 0
    overall_attempted_credits = 0
    overall_passed_credits = 0
    
    for semester_id, data in sorted(semesters.items(), reverse=True):
        semester_gpa = data['total_grade_points'] / data['total_attempted_credits'] if data['total_attempted_credits'] > 0 else 0
        
        semester_data.append({
            'id': data['id'],
            'year': data['year'],  
            'grades': data['grades'],
            'gpa': semester_gpa,
            'total_attempted_credits': data['total_attempted_credits'],
            'total_passed_credits': data['total_passed_credits']
        })
        
        cumulative_grade_points += data['total_grade_points']
        overall_attempted_credits += data['total_attempted_credits']
        overall_passed_credits += data['total_passed_credits']
    
    overall_gpa = cumulative_grade_points / overall_attempted_credits if overall_attempted_credits > 0 else 0

    return render(request, 'transcript.html', {
        'semester_data': semester_data,
        'overall_gpa': overall_gpa,
        'overall_attempted_credits': overall_attempted_credits,
        'overall_passed_credits': overall_passed_credits
    })

