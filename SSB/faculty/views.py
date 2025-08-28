from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def faculty_dashboard(request):
    if request.user.profile.user_type != 'tutor':
        if request.user.profile.user_type == 'student':
            return redirect('dashboard')
        elif request.user.is_superuser:
            return redirect('/administrator')
    
    return render(request, 'faculty/dashboard.html')

# Create your views here.

