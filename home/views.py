from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm

from django.http import JsonResponse
from django.template.loader import render_to_string
from recommendations.services import recommend_candidates, recommend_jobs
from django.core.cache import cache
from jobs.models import Job

from django.http import JsonResponse
from django.template.loader import render_to_string
from recommendations.services import recommend_candidates, recommend_jobs
from django.core.cache import cache
from jobs.models import Job

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm

def _save_city_state_from_profile(profile, form, request=None):
    """Extract city/state/lat/long from cities_light City selection and optional pin-drop. Save to profile."""
    from cities_light.models import City
    city_id = form.cleaned_data.get('city')
    if not city_id:
        return
    try:
        city_id = int(city_id)
    except (TypeError, ValueError):
        return
    try:
        city = City.objects.get(pk=city_id)
        profile.city = city.name
        profile.state = city.region.geoname_code or city.region.name if city.region else ''
        lat = request.POST.get('latitude') if request else None
        lng = request.POST.get('longitude') if request else None
        if lat and lng:
            try:
                profile.latitude = float(lat)
                profile.longitude = float(lng)
            except (TypeError, ValueError):
                if city.latitude and city.longitude:
                    profile.latitude = city.latitude
                    profile.longitude = city.longitude
        elif city.latitude and city.longitude:
            profile.latitude = city.latitude
            profile.longitude = city.longitude
    except City.DoesNotExist:
        pass


@login_required(login_url="login")
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            _save_city_state_from_profile(profile, form, request)
            profile.save()
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
    job_results = []
    job_recommendations = []
    profile = None

    if request.user.is_authenticated:
        profile, created = Profile.objects.get_or_create(user=request.user)

        if profile.role == "recruiter":
            jobs = Job.objects.filter(recruiter=request.user)

            for job in jobs:
                candidates = recommend_candidates(job)
                job_recommendations.append({
                    "job": job,
                    "candidates": candidates
                })

        elif profile.role == "job_seeker":
            cache_key = f"job_recs_user_{request.user.id}"
            job_results = cache.get(cache_key)

            if job_results is None:
                job_results = recommend_jobs(profile)
                cache.set(cache_key, job_results, timeout=300)

            job_results = job_results[:10] 

    return render(request, "home/index.html", {
        "user_profile": profile,
        "job_results": job_results,
        "job_recommendations": job_recommendations
    })

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        form.fields["password1"].help_text = None
        form.fields["password2"].help_text = None
        if form.is_valid():
            user = form.save()
            
            role = request.POST.get("role", "seeker") 
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
    return redirect("login") 


@login_required(login_url="login")
def public_profile_view(request, user_id):
    target = Profile.objects.select_related("user").get(user__id=user_id)

    if request.user.id == user_id:
        return redirect("profile")

    viewer_profile, _ = Profile.objects.get_or_create(user=request.user)
    if viewer_profile.role != "recruiter":
        return redirect("home.index")

    return render(request, "home/public_profile.html", {"profile": target})

@login_required(login_url="login")
def load_more_jobs(request):
    offset = int(request.GET.get("offset", 0))
    limit = 10

    profile = Profile.objects.get(user=request.user)

    if profile.role != "job_seeker":
        return JsonResponse({"error": "not allowed"}, status=403)

    cache_key = f"job_recs_user_{request.user.id}"
    jobs_with_scores = cache.get(cache_key)

    if jobs_with_scores is None:
        jobs_with_scores = recommend_jobs(profile)  
        cache.set(cache_key, jobs_with_scores, timeout=300)

    jobs_slice = jobs_with_scores[offset:offset+limit]
    next_offset = offset + len(jobs_slice)

    html = render_to_string(
        "home/partials/job_cards.html",
        {"job_results": jobs_slice},
        request=request
    )

    return JsonResponse({
        "html": html,
        "next_offset": next_offset
    })
