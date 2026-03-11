from django.shortcuts import render
from django.urls import reverse
from notifications.models import Notification
from jobs.models import Job
from .services import recommend_candidates, recommend_jobs

# Create your views here.

def recommendations_page(request):
    if not request.user.is_authenticated:
        return render(request, "recommendations/recommendations.html", {
            "user_profile": None,
            "job_recommendations": [],
            "job_results": []
        })
    
    profile = request.user.profile

    if profile.role == "recruiter":
        jobs = Job.objects.filter(recruiter=request.user)
        job_recommendations = []

        for job in jobs:
            candidates = recommend_candidates(job)
            job_recommendations.append({
                "job": job,
                "candidates": candidates
            })
        
        return render(request, "recommendations/recommendations.html", {
            "user_profile": profile,
            "job_recommendations": job_recommendations,
            "job_results": []
        })
    
    else:
        job_results = recommend_jobs(profile)
        return render(request, "recommendations/recommendations.html", {
            "user_profile": profile,
            "job_recommendations": [],
            "job_results": job_results
        })
    
def recommendations(request):
    recommended_jobs = []
    if request.user.is_authenticated:
        ids = [str(j.id) for j in recommended_jobs] 
        fingerprint = ",".join(ids)
        last_fp = request.session.get("last_recs_fp")
        if fingerprint and fingerprint != last_fp:
            Notification.objects.create(
                recipient=request.user,
                notif_type="recommendation",
                title="New recommendation",
                body=f"You have {len(ids)} new recommended jobs.",
                url=reverse("recommendations"),
            )
            request.session["last_recs_fp"] = fingerprint
    return render(request, "recommendations/recommendations.html")
