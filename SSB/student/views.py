from django.shortcuts import render
# from .models import Profile
# Create your views here.



def dashboard(request):
    return render(request, 'dashboard.html')

def student_profile(request):
    profile = request.user.profile
    return render(request, 'student_profile.html', {'profile': profile})