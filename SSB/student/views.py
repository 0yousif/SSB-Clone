from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# from .models import Profile
# Create your views here.


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def student_profile(request):
    profile = request.user.profile
    return render(request, 'student_profile.html', {'profile': profile})
