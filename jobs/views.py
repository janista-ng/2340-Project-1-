from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.db.models import Q
from home.models import Profile
from .models import Job, Application, SavedCandidateSearch
from .forms import JobForm, ApplicationForm


def _save_city_state_from_form(job, form, request=None):
    """Extract city/state from django-cities-light City selection and optional pin-drop. Save to job."""
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
        job.city = city.name
        job.state = city.region.geoname_code or city.region.name if city.region else ''
        lat = request.POST.get('latitude') if request else None
        lng = request.POST.get('longitude') if request else None
        if lat and lng:
            try:
                job.latitude = float(lat)
                job.longitude = float(lng)
            except (TypeError, ValueError):
                if city.latitude and city.longitude:
                    job.latitude = city.latitude
                    job.longitude = city.longitude
        elif city.latitude and city.longitude:
            job.latitude = city.latitude
            job.longitude = city.longitude
    except City.DoesNotExist:
        pass


def job_list(request):
    jobs = Job.objects.filter(is_active=True)

    query = request.GET.get("q", "")
    other_query = request.GET.get("other", "")
    focus_field = request.GET.get("focus", "")
    if focus_field not in ("q", "other"):
        focus_field = ""
    min_salary = request.GET.get("min_salary")
    max_salary = request.GET.get("max_salary")
    radius_miles = request.GET.get("radius_miles")

    remote_filter = request.GET.get("remote")
    onsite_filter = request.GET.get("onsite")
    hybrid_filter = request.GET.get("hybrid")
    visa_filter = request.GET.get("visa")

    if query:
        jobs = jobs.filter(title__icontains=query)
    if other_query:
        jobs = jobs.filter(
            Q(description__icontains=other_query)
            | Q(skills__icontains=other_query)
            | Q(company__icontains=other_query)
            | Q(city__icontains=other_query)
            | Q(state__icontains=other_query)
            | Q(location__icontains=other_query)
        )
    if min_salary:
        jobs = jobs.filter(salary__gte=int(min_salary))
    if max_salary:
        jobs = jobs.filter(salary__lte=int(max_salary))

    remote_values = []
    if remote_filter:
        remote_values.append("remote")
    if onsite_filter:
        remote_values.append("on_site")
    if hybrid_filter:
        remote_values.append("hybrid")
    if remote_values:
        jobs = jobs.filter(remote__in=remote_values)
    if visa_filter:
        jobs = jobs.filter(visa_sponsorship="yes")

    # Distance filter (commute radius) for seekers with profile location
    filter_lat = request.GET.get("filter_lat")
    filter_lng = request.GET.get("filter_lng")
    if filter_lat and filter_lng and radius_miles and request.user.is_authenticated:
        try:
            clat, clng = float(filter_lat), float(filter_lng)
            radius = float(radius_miles)
            if radius > 0:
                jobs_with_loc = jobs.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
                filtered = [j for j in jobs_with_loc if _haversine_miles(clat, clng, j.latitude, j.longitude) <= radius]
                job_pks = [j.pk for j in filtered]
                jobs = Job.objects.filter(pk__in=job_pks) if job_pks else Job.objects.none()
        except (TypeError, ValueError):
            pass

    user_lat = user_lng = None
    user_profile = None
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        user_profile = request.user.profile
        if user_profile.latitude is not None and user_profile.longitude is not None:
            user_lat, user_lng = float(user_profile.latitude), float(user_profile.longitude)

    jobs_count = jobs.count()
    total_jobs = Job.objects.filter(is_active=True).count()

    context = {
        "jobs": jobs,
        "jobs_count": jobs_count,
        "total_jobs": total_jobs,
        "query": query,
        "other_query": other_query,
        "focus_field": focus_field,
        "min_salary": int(min_salary) if min_salary else 0,
        "max_salary": int(max_salary) if max_salary else 200000,
        "remote": remote_filter,
        "onsite": onsite_filter,
        "hybrid": hybrid_filter,
        "visa": visa_filter,
        "radius_miles": int(float(radius_miles)) if radius_miles else 0,
        "user_lat": user_lat,
        "user_lng": user_lng,
        "user_profile": user_profile,
    }

    return render(request, "jobs/job_list.html", context)


def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if not job.is_active and not (
        request.user.is_authenticated and (request.user == job.recruiter or request.user.is_superuser)
    ):
        return HttpResponseForbidden("This job listing is not available.")

    already_applied = False
    if request.user.is_authenticated:
        already_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    return render(request, "jobs/job_detail.html", {"job": job, "already_applied": already_applied})


def cities_by_region(request):
    """AJAX endpoint: return cities for a given region (state), with lat/lng for pin-drop maps."""
    from cities_light.models import City
    region_id = request.GET.get('region_id')
    if not region_id:
        return JsonResponse({'cities': []})
    try:
        cities = list(City.objects.filter(region_id=region_id).order_by('name').values(
            'id', 'name', 'latitude', 'longitude'
        ))
        for c in cities:
            lat, lng = c.get('latitude'), c.get('longitude')
            c['lat'] = float(lat) if lat is not None else None
            c['lng'] = float(lng) if lng is not None else None
            del c['latitude']
            del c['longitude']
        return JsonResponse({'cities': cities})
    except Exception:
        return JsonResponse({'cities': []})


def _haversine_miles(lat1, lon1, lat2, lon2):
    """Distance in miles between two points (as-the-crow-flies)."""
    import math
    R = 3959  # Earth radius in miles
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(min(1, a)))
    return R * c


def map_markers(request):
    """
    JSON endpoint for map markers. Returns jobs (and optionally applicant profiles)
    with latitude/longitude for geolocation-based maps.
    Query params: job_id (recruiter applicants), lat/lng/radius_miles (distance filter).
    """
    jobs = (
        Job.objects.filter(is_active=True)
        .exclude(latitude__isnull=True)
        .exclude(longitude__isnull=True)
        .select_related('recruiter')
    )
    center_lat = request.GET.get('lat')
    center_lng = request.GET.get('lng')
    radius_miles = request.GET.get('radius_miles')
    if center_lat and center_lng and radius_miles:
        try:
            clat, clng = float(center_lat), float(center_lng)
            radius = float(radius_miles)
            filtered = []
            for job in jobs:
                if _haversine_miles(clat, clng, job.latitude, job.longitude) <= radius:
                    filtered.append(job)
            jobs = filtered
        except (TypeError, ValueError):
            pass
    job_pk = request.GET.get('job_id', '').strip()
    recruiter_applicants_only = request.GET.get('recruiter_applicants') and request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter'
    markers = []
    if not recruiter_applicants_only:
        for job in jobs:
            markers.append({
                'type': 'job',
                'id': job.pk,
                'title': job.title,
                'company': job.company,
                'location': job.location or f"{job.city}, {job.state}".strip(', '),
                'lat': float(job.latitude),
                'lng': float(job.longitude),
                'url': f'/jobs/{job.pk}/',
            })
    if request.user.is_authenticated:
        from home.models import Profile
        if job_pk:
            try:
                job = Job.objects.get(pk=int(job_pk), recruiter=request.user)
                for app in job.applications.select_related('applicant').all():
                    profile = Profile.objects.filter(user=app.applicant).first()
                    if profile and profile.latitude and profile.longitude:
                        markers.append({
                            'type': 'applicant',
                            'id': profile.user_id,
                            'title': profile.display_name or app.applicant.username,
                            'location': profile.location or '',
                            'lat': float(profile.latitude),
                            'lng': float(profile.longitude),
                            'url': f'/profiles/{profile.user_id}/',
                        })
            except (Job.DoesNotExist, ValueError):
                pass
        elif request.GET.get('recruiter_applicants') and hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # All applicants across recruiter's jobs
            seen = set()
            for job in Job.objects.filter(recruiter=request.user):
                for app in job.applications.select_related('applicant').all():
                    if app.applicant_id in seen:
                        continue
                    seen.add(app.applicant_id)
                    profile = Profile.objects.filter(user=app.applicant).first()
                    if profile and profile.latitude and profile.longitude:
                        markers.append({
                            'type': 'applicant',
                            'id': profile.user_id,
                            'title': profile.display_name or app.applicant.username,
                            'location': profile.location or '',
                            'lat': float(profile.latitude),
                            'lng': float(profile.longitude),
                            'url': f'/profiles/{profile.user_id}/',
                        })
    return JsonResponse({'markers': markers})


@login_required
def job_create(request):
    if request.user.profile.role != 'recruiter':
        return redirect('home.index')
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            _save_city_state_from_form(job, form, request)
            job.save()
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm()
    return render(request, 'jobs/job_form.html', {'form': form})

@login_required
def apply_to_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    existing_application = Application.objects.filter(
        job=job,
        applicant=request.user
    ).first()
    if existing_application:
        messages.warning(request, "You have already applied to this job.")
        return redirect('jobs:job_detail', pk=job.pk)
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Application submitted successfully.")
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = ApplicationForm()
    return render(request, 'jobs/application_form.html', {'form': form, 'job': job})

@login_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if request.user != job.recruiter:
        return HttpResponseForbidden("You are not allowed to edit this job.")

    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save(commit=False)
            _save_city_state_from_form(job, form, request)
            job.save()
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/job_edit.html', {'form': form, 'job': job})

@login_required
def my_applications(request):
    apps = Application.objects.filter(applicant=request.user).select_related('job').order_by('-applied_at')
    return render(request, 'jobs/my_applications.html', {'applications': apps})

@login_required
def save_candidate_search(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if request.user != job.recruiter:
        return HttpResponseForbidden("Not allowed.")

    if request.method != "POST":
        return redirect("jobs:job_applications", pk=job.pk)

    filters = {
        "q": request.POST.get("q", "").strip(),
        "skills": request.POST.get("skills", "").strip(),
        "location": request.POST.get("location", "").strip(),
        "city": request.POST.get("city", "").strip(),
        "state": request.POST.get("state", "").strip(),
    }

    raw_name = request.POST.get("name", "").strip()
    active_bits = [value for value in filters.values() if value]
    default_name = "Candidate search"
    if active_bits:
        default_name = " / ".join(active_bits[:2])[:120]

    saved_search = SavedCandidateSearch.objects.create(
        recruiter=request.user,
        job=job,
        name=raw_name or default_name,
        **filters,
    )

    messages.success(request, f'Saved search "{saved_search.name}".')

    url = f"/jobs/{job.pk}/applications/"
    qs = saved_search.querystring()
    if qs:
        url = f"{url}?{qs}"
    return redirect(url)


@login_required
def delete_candidate_search(request, pk, search_id):
    job = get_object_or_404(Job, pk=pk)

    if request.user != job.recruiter:
        return HttpResponseForbidden("Not allowed.")

    search = get_object_or_404(
        SavedCandidateSearch,
        pk=search_id,
        recruiter=request.user,
        job=job,
    )

    if request.method == "POST":
        search.delete()
        messages.success(request, "Saved search deleted.")

    return redirect("jobs:job_applications", pk=job.pk)

@login_required
def job_applications(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if request.user != job.recruiter:
        return HttpResponseForbidden("Not allowed.")

    applications = (
        Application.objects
        .filter(job=job)
        .select_related("applicant", "applicant__profile")
        .order_by("-applied_at")
    )

    q = request.GET.get("q", "").strip()
    skills = request.GET.get("skills", "").strip()
    location = request.GET.get("location", "").strip()
    city = request.GET.get("city", "").strip()
    state = request.GET.get("state", "").strip()

    if q:
        applications = applications.filter(
            Q(applicant__username__icontains=q) |
            Q(applicant__first_name__icontains=q) |
            Q(applicant__last_name__icontains=q) |
            Q(applicant__email__icontains=q) |
            Q(applicant__profile__display_name__icontains=q)
        )

    if skills:
        parts = [s.strip() for s in skills.split(",") if s.strip()]
        for s in parts:
            applications = applications.filter(applicant__profile__skills__icontains=s)

    if location:
        applications = applications.filter(applicant__profile__location__icontains=location)
    if city:
        applications = applications.filter(applicant__profile__city__icontains=city)
    if state:
        applications = applications.filter(applicant__profile__state__icontains=state)

    saved_searches = SavedCandidateSearch.objects.filter(
        recruiter=request.user,
        job=job,
    )

    return render(request, "jobs/job_applications.html", {
        "job": job,
        "applications": applications,
        "q": q,
        "skills": skills,
        "location": location,
        "city": city,
        "state": state,
        "saved_searches": saved_searches,
    })


@login_required
def update_application_status(request, app_id):
    application = get_object_or_404(Application, pk=app_id)
    if request.user != application.job.recruiter:
        return HttpResponseForbidden("You are not allowed to update this application.")

    if request.method == "POST":
        new_status = request.POST.get("status", "")
        valid = dict(Application.STATUS_CHOICES).keys()
        if new_status in valid:
            application.status = new_status
            application.save(update_fields=["status", "updated_at"])
            messages.success(request, "Status updated.")
        else:
            messages.error(request, "Invalid status.")
    return redirect('jobs:job_applications', pk=application.job.pk)
