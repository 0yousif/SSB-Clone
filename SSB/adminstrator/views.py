from django.shortcuts import render, redirect
from .models import Profile, Semester
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


from .forms import UserForm, ProfileForm


@login_required
def signupUser(request):
    error_message = ""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_id = user.id
            return redirect('admin_reg_profile', user_id=user_id)
        else:
            error_message = 'Invalid Signup - Try Again...'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/register.html', context)

# Create your views here.


@login_required
def adminregstudent(request, user_id):
    # print("request.user.profile", request.user)
    userProfile = Profile.objects.get(user_id=user_id)
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=userProfile)
        if profile_form.is_valid():
            profile_form.save()

            return redirect('admindex')
    else:
        profile_form = ProfileForm()

    return render(request, 'registration/registerprofile.html', {'profile_form': profile_form, 'profile': userProfile})


@login_required
def adminhome(request):
    return render(request, 'home.html')


@login_required
def admindex(request):
    profiles = Profile.objects.all()
    users = User.objects.all()

    return render(request, 'index.html', {'users': users, 'profiles': profiles})


class SemesterCreate(CreateView):
    model = Semester
    fields = '__all__'


class SemesterUpdate(UpdateView):
    model = Semester
    fields = '__all__'
    success_url = '/administrator/'


class SemesterList(ListView):
    model = Semester


class SemesterDetail(DetailView):
    model = Semester


class SemesterDelete(DeleteView):
    model = Semester
    success_url = '/administrator/semester/list'
