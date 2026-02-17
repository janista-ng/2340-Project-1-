from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Job, Application
from .forms import JobForm, ApplicationForm
from django.db import IntegrityError
from django.urls import reverse
from django.http import HttpResponseForbidden


def job_list(request):
    query = request.GET.get("q", "")
    if query:
        jobs = Job.objects.filter(
            title__icontains=query
        ) | Job.objects.filter(
            company__icontains=query
        ) | Job.objects.filter(
            location__icontains=query
        )
    else:
        jobs = Job.objects.all()

    return render(request, "jobs/job_list.html", {
        "jobs": jobs,
        "query": query,
    })

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)

    already_applied = False
    if request.user.is_authenticated:
        already_applied = Application.objects.filter(applicant=request.user, job=job).exists()

    context = {
        "job": job,
        "already_applied": already_applied,
        "applied": request.GET.get("applied") == "1",
        "already_applied_msg": request.GET.get("already_applied") == "1",
    }
    return render(request, "jobs/job_detail.html", context)


@login_required
def job_create(request):
    if request.user.profile.role != 'recruiter':
        return redirect('home.index')
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.poster = request.user
            job.save()
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm()
    return render(request, 'jobs/job_form.html', {'form': form})

@login_required
def apply_to_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    
    if request.method != "POST":
        # Essentially, if someone visits /apply/ directly, we send 'em back
        return redirect('jobs:job_detail', pk=job.pk)
    
    cover_note = request.POST.get("cover_note", "").strip()

    try:
        application, created = Application.objects.get_or_create(
            applicant=request.user,
            job=job,
            defaults={"cover_note": cover_note},
        )
        # If already applied, you can decide whether to update the note.
        if not created and cover_note:
            application.cover_note = cover_note
            application.save(update_fields=["cover_note", "updated_at"])
    except IntegrityError:
        created = False

    suffix = "?applied=1" if created else "?already_applied=1"
    return redirect(reverse('jobs:job_detail', kwargs={"pk": job.pk}) + suffix)



# def apply_to_job(request, pk):
#     job = get_object_or_404(Job, pk=pk)
#     if request.method == 'POST':
#         form = ApplicationForm(request.POST)
#         if form.is_valid():
#             application = form.save(commit=False)
#             application.job = job
#             application.applicant = request.user
#             application.save()
#             return redirect('jobs:job_detail', pk=job.pk)
#     else:
#         form = ApplicationForm()
#     return render(request, 'jobs/application_form.html', {'form': form, 'job': job})
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
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
            form.save()
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/job_edit.html', {'form': form, 'job': job})
