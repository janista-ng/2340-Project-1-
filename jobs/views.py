from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.db.models import Q
from home.models import Profile
from .models import Job, Application
from .forms import JobForm, ApplicationForm


def _save_city_state_from_form(job, form):
    """Extract city/state from django-cities-light City selection and save to job."""
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
        if city.latitude and city.longitude:
            job.latitude = city.latitude
            job.longitude = city.longitude
    except City.DoesNotExist:
        pass


def job_list(request):
    jobs = Job.objects.filter(is_active=True)

    query = request.GET.get("q", "")
    skills_query = request.GET.get("skills", "")
    city_query = request.GET.get("city", "")
    state_query = request.GET.get("state", "")
    min_salary = request.GET.get("min_salary")
    max_salary = request.GET.get("max_salary")

    remote_filter = request.GET.get("remote")
    onsite_filter = request.GET.get("onsite")
    hybrid_filter = request.GET.get("hybrid")
    visa_filter = request.GET.get("visa")

    if query:
        jobs = jobs.filter(title__icontains=query)
    if skills_query:
        jobs = jobs.filter(skills__icontains=skills_query)
    if city_query:
        jobs = jobs.filter(city__icontains=city_query)
    if state_query:
        jobs = jobs.filter(state__icontains=state_query)
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

    context = {
        "jobs": jobs,
        "query": query,
        "skills_query": skills_query,
        "city_query": city_query,
        "state_query": state_query,
        "min_salary": int(min_salary) if min_salary else 0,
        "max_salary": int(max_salary) if max_salary else 200000,
        "remote": remote_filter,
        "onsite": onsite_filter,
        "hybrid": hybrid_filter,
        "visa": visa_filter,
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
    """AJAX endpoint: return cities for a given region (state)."""
    from cities_light.models import City
    region_id = request.GET.get('region_id')
    if not region_id:
        return JsonResponse({'cities': []})
    try:
        cities = City.objects.filter(region_id=region_id).order_by('name').values('id', 'name')
        return JsonResponse({'cities': list(cities)})
    except Exception:
        return JsonResponse({'cities': []})


@login_required
def job_create(request):
    if request.user.profile.role != 'recruiter':
        return redirect('home.index')
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            _save_city_state_from_form(job, form)
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
            _save_city_state_from_form(job, form)
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

    return render(request, "jobs/job_applications.html", {
        "job": job,
        "applications": applications,
        "q": q,
        "skills": skills,
        "location": location,
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
