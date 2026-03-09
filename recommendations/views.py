from django.shortcuts import render
from home.models import Profile
from django.urls import reverse
from notifications.models import Notification
from jobs.models import Job

# Create your views here.

def parse_skills(skill_string):
    if not skill_string:
        return set()
    return set(
        s.strip().lower()
        for s in skill_string.split(",")
        if s.strip()
    )

def recommend_candidates(job):
    seekers = Profile.objects.filter(role="job_seeker") 
    ranked = []
    job_skills = parse_skills(job.skills)

    for s in seekers:
        score = 0

        user_skills = parse_skills(s.skills)
        skill_matches = user_skills & job_skills
        score += len(skill_matches) * 2

        if s.location and job.location:
            if s.location.lower() in job.location.lower():
                score += 1

        if score > 0:
            ranked.append((s, score))
    
    return sorted(ranked, key=lambda x: x[1], reverse=True)

def recommend_jobs(profile, limit=10):
    user_skills = parse_skills(profile.skills)
    jobs = Job.objects.all()
    recommendations = []

    for job in jobs:
        job_skills = parse_skills(job.skills)

        overlap = user_skills.intersection(job_skills)
        score = len(overlap)

        if profile.location and job.location:
            if profile.location.lower() in job.location.lower():
                score += 2
        
        if job.remote == "remote":
            score += 1

        if score > 0:
            recommendations.append((job, score))
        
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations[:limit]  
    

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
