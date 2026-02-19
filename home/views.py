from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm
from .forms import ProfileForm, PrivacyForm


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm

@login_required(login_url="login")
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Save edits
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
        edit_mode = True
    else:
        form = ProfileForm(instance=profile)
        edit_mode = (request.GET.get("edit") == "1")

    return render(request, "home/profile.html", {
        "profile": profile,
        "form": form,
        "edit_mode": edit_mode,
    })

def index(request):
    return render(request, "home/index.html")

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        form.fields["password1"].help_text = None
        form.fields["password2"].help_text = None
        if form.is_valid():
            user = form.save()
            
            role = request.POST.get("role", "job_seeker") 
            Profile.objects.create(user=user, role=role)
            
            login(request, user)
            return redirect("profile")
    else:
        form = UserCreationForm()
        form.fields["password1"].help_text = None
        form.fields["password2"].help_text = None

    return render(request, "home/signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home.index")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "home/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login") #all code above is for sign in and sign up with redirects

@login_required(login_url="login")
def privacy_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = PrivacyForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = PrivacyForm(instance=profile)

    return render(request, "home/privacy.html", {"form": form})

@login_required(login_url="login")
def public_profile_view(request, user_id):
    target = Profile.objects.select_related("user").get(user__id=user_id)

    # allow viewing your own profile always
    if request.user.id == user_id:
        return redirect("profile")

    # only recruiters can view seekers 
    viewer_profile, _ = Profile.objects.get_or_create(user=request.user)
    if viewer_profile.role != "recruiter":
        return redirect("home.index")

    return render(request, "home/public_profile.html", {"profile": target})

