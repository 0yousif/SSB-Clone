from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from adminstrator.models import Profile, Attendance, Student_registration, Section, Semester, Grades, Transcript, GRADE_CHOICES, Configurations
from django.utils import timezone
from django.db.models import Q

from student.views import getUserSections


@login_required
def faculty_dashboard(request):
    if request.user.profile.user_type != 'tutor':
        if request.user.profile.user_type == 'student':
            return redirect('dashboard')
        elif request.user.is_superuser:
            return redirect('/administrator')
    
    return render(request, 'faculty/dashboard.html')

@login_required
def student_lookup(request):
    if request.user.profile.user_type != 'tutor':
        if request.user.profile.user_type == 'student':
            return redirect('dashboard')
        elif request.user.is_superuser:
            return redirect('/administrator')
    
    students = Profile.objects.filter(user_type='student').order_by('last_name', 'first_name') 
    q = request.GET.get('q')
    if q:
        students = students.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(academic_number__icontains=q)
        )

    return render(request, 'faculty/student_lookup.html', {'students': students, })

@login_required
def student_detail(request, student_id):
    profile = Profile.objects.get(student_detail_id=student_id, user_type='student')
    student = profile.user

    registeredSections, unregisteredSections = getUserSections(request, student)
    configs = Configurations.objects.first()

    return render(request, 'student_profile.html', {'profile': profile, "registeredSections":registeredSections, 'configs':configs})



@login_required
def take_attendance(request):
    sections = Section.objects.filter(tutor=request.user)
    today = timezone.now().date()
    selected_section = None
    students = []
    attendance_submitted = False
    student_attendance = []
    
    if request.method == 'POST':
        section_id = request.POST.get('section')
        
        if section_id:
                selected_section = Section.objects.get(crn=section_id, tutor=request.user)
                
                attendance_submitted = Attendance.objects.filter(
                    date=today,
                    registration__crn=selected_section
                ).exists()
                
                students = Student_registration.objects.filter(crn=selected_section)
                
                if 'submit_attendance' in request.POST and not attendance_submitted:
                    for student in students:
                        status = request.POST.get(f'status_{student.pk}', 'P')
                        Attendance.objects.create(
                            date=today,
                            status=status,
                            tutor=request.user,
                            registration=student
                        )
                    attendance_submitted = True
                
                attendance_records = Attendance.objects.filter(
                    date=today,
                    registration__in=students
                ).select_related('registration')
                
                attendance_dict = {record.registration_id: record for record in attendance_records}
                
                for student in students:
                    attendance = attendance_dict.get(student.pk)
                    if attendance:
                        student_attendance.append({
                            'student': student,
                            'status': attendance.status
                        })
                    else:
                        student_attendance.append({
                            'student': student,
                            'status': 'P'  
                        })
    
    return render(request, 'faculty/attendance.html', {
        'sections': sections,
        'students': students,
        'today': today,
        'selected_section': selected_section,
        'attendance_submitted': attendance_submitted,
        'student_attendance': student_attendance
    })

@login_required
def tutor_sections(request):
    current_semester = Semester.objects.get(is_current=True)
    
    if current_semester:
        sections = Section.objects.filter(
            tutor=request.user,
            semester=current_semester
        ).select_related('course', 'course__department')
    
    return render(request, 'faculty/tutor_sections.html',{'sections': sections , 'current_semester':current_semester,})


@login_required
def section_students(request, crn):
    section = Section.objects.get(crn=crn, tutor=request.user)
    students = Student_registration.objects.filter(crn=section)
    
    return render(request, 'faculty/section_students.html', {'section': section,
        'students': students,})


@login_required
def grade_students(request, crn):
    section = Section.objects.get(crn=crn, tutor=request.user)
    students = Student_registration.objects.filter(crn=section)

    # print(f" {students.count()} students {crn}")
    # for student in students:
    #     print(f"Student: {student.student.username} Registration {student.registration}")


    grades_submitted = Grades.objects.filter(registration_id__crn=section).exists()
    
    if request.method == 'POST' and not grades_submitted:
        grade_dict = dict(GRADE_CHOICES)
        
        for student in students:
            grade_value = request.POST.get(f'grade_{student.registration}')
            if grade_value:
                Grades.objects.update_or_create(
                    registration=student,
                    defaults={'grade': grade_value}
                )
                
                if grade_value == 'F':
                    student.registration_status = 'failed'
                elif student.registration_status == 'failed':
                    student.registration_status = 'active'
                
                student.save()
        update_student_gpas(section)
        grades_submitted = True
    
    student_grades = []
    for student in students:
            grade = Grades.objects.filter(registration=student).first()        
            student_grades.append({

            'student': student,
            'grade': grade.grade if grade else None
        })
    
    return render(request, 'faculty/grade_students.html', {
        'section': section,
        'student_grades': student_grades,
        'grades_submitted': grades_submitted
    })

def update_student_gpas(section):
    grade_dict = dict(GRADE_CHOICES)
    
    student_registrations = Student_registration.objects.filter(crn=section)
    
    for reg in student_registrations:
        student = reg.student
        all_grades = Grades.objects.filter(
            registration__student=student
        ).select_related(
            'registration__crn__course'
        )
        
        total_grade_points = 0
        total_attempted_credits = 0
        total_passed_credits = 0
        
        for grade in all_grades:
            course_credits = grade.registration.crn.course.credit_hours
            grade_point = grade_dict.get(grade.grade, 0)
            gpv = grade_point * course_credits
            
            total_grade_points += gpv
            total_attempted_credits += course_credits
            
            if grade.grade != 'F':
                total_passed_credits += course_credits
        
        overall_gpa = total_grade_points / total_attempted_credits if total_attempted_credits > 0 else 0
        
        profile = student.profile
        profile.gpa = round(overall_gpa, 2)
        profile.total_credits_attempted = total_attempted_credits
        profile.total_credits_earned = total_passed_credits
        profile.save()





@login_required
def grade_sections(request):
    current_semester = Semester.objects.get(is_current=True)
    sections = Section.objects.filter(tutor=request.user, semester=current_semester)
    return render(request, 'faculty/grade_sections.html', {
        'sections': sections,
        'current_semester': current_semester,

    })