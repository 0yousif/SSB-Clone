from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from adminstrator.models import Profile

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

