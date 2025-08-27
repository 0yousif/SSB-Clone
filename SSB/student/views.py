from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# from .models import Profile
# Create your views here.


def redirect_user(request):
    profile_type = request.user.profile.user_type
    if (request.user.is_superuser):
        return redirect('/administrator')
    if (profile_type == 'student'):
        return redirect('dashboard')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def student_profile(request):
    profile = request.user.profile
    return render(request, 'student_profile.html', {'profile': profile})
