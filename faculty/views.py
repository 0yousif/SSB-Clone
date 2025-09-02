from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from adminstrator.models import Profile, Attendance, Student_registration, Section, Semester, Grades, Transcript
from django.utils import timezone

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
    
    return render(request, 'faculty/student_lookup.html', {'students': students})

@login_required
def student_detail(request, student_id):
    student = Profile.objects.get(student_detail_id=student_id, user_type='student')
    return render(request, 'student_profile.html', {'profile': student})

@login_required
def take_attendance(request):
    sections = Section.objects.filter(tutor=request.user)
    today = timezone.now().date()
    selected_section = None
    students = []
    attendance_submitted = False
    
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
    
    return render(request, 'faculty/attendance.html', {
        'sections': sections,
        'students': students,
        'today': today,
        'selected_section': selected_section,
        'attendance_submitted': attendance_submitted
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
    grades_submitted = Grades.objects.filter(registration_id__crn=section).exists()
    
    if request.method == 'POST' and not grades_submitted:
        for student in students:
            grade_value = request.POST.get(f'grade_{student.registration}')
            if grade_value:
                Grades.objects.update_or_create(
                    registration_id=student,
                    defaults={'grade': grade_value}
                )
                
                if grade_value == 'F':
                    student.registration_status = 'failed'
                    
                    profile = student.student.profile
                    course_credits = section.course.credit_hours 
                    profile.total_credits_earned = max(0, profile.total_credits_earned - course_credits)
                    profile.save()
                
                elif student.registration_status == 'failed':
                    student.registration_status = 'active'
                
                student.save()
        
        grades_submitted = True
    
    return render(request, 'faculty/grade_students.html', {
        'section': section, 
        'students': students,
        'grades_submitted': grades_submitted,
    })

@login_required
def grade_sections(request):
    current_semester = Semester.objects.get(is_current=True)
    sections = Section.objects.filter(tutor=request.user, semester=current_semester)
    return render(request, 'faculty/grade_sections.html', {
        'sections': sections,
        'current_semester': current_semester,

    })