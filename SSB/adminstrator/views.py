from django.shortcuts import render, redirect
from .models import Profile
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm


from .forms import UserForm, ProfileForm


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


def adminregstudent(request, user_id):
    # print("request.user.profile", request.user)
    userProfile = Profile.objects.get(user_id=user_id)
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=userProfile)
        if profile_form.is_valid():
            print("__HERE_____________________________!!!!!!")
            print(userProfile.user_id)
            # print(profile_form)

            # profile_form.save(commit=False)
            # profile_form.user_id = userProfile.user_id
            profile_form.save()

            return redirect('admindex')
    else:
        profile_form = ProfileForm()

    return render(request, 'registration/registerprofile.html', {'profile_form': profile_form})


def adminhome(request):
    return render(request, 'home.html')


# def adminreg(request):
#     if request.method == 'POST':
#         user_form = UserForm(request.POST)
#         profile_form = ProfileForm(request.POST)

#         if user_form.is_valid() and profile_form.is_valid():
#             user = user_form.save(commit=False)
#             # to hash the password from the input place
#             user.set_password(user.password)

#             user.save()

#             profile = profile_form.save(commit=False)
#             profile.user = user
#             # profile.save()

#             return redirect('admindex')
#     else:
#         user_form = UserForm()
#         profile_form = ProfileForm()

#     return render(request, 'registration/register.html', {'user_form': user_form, 'profile_form': profile_form})


def admindex(request):
    profiles = Profile.objects.all()
    users = User.objects.all()

    return render(request, 'index.html', {'users': users, 'profiles': profiles})
