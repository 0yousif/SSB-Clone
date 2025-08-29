from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from adminstrator.models import Profile, Attendance, Student_registration, Section
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

def simple_attendance(request):
    tutor_sections = Section.objects.filter(tutor=request.user)
    students = []
    
    if request.method == 'POST':
        section_id = request.POST.get('section')
        date = request.POST.get('date')
        
        if section_id and date:
            try:
                section = Section.objects.get(crn=section_id, tutor=request.user)
                students = Student_registration.objects.filter(crn=section)
                
                # Save attendance
                for student in students:
                    status = request.POST.get(f'status_{student.registration}')
                    if status:
                        Attendance.objects.update_or_create(
                            date=date,
                            registration_id=student,
                            defaults={'status': status, 'tutor': request.user}
                        )
                
                return redirect('attendance_success')
                
            except Section.DoesNotExist:
                pass
    
    return render(request, 'simple_attendance.html', {
        'sections': tutor_sections,
        'students': students
    })