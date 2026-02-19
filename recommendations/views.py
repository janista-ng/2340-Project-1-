from django.shortcuts import render
from home.models import Profile
from django.urls import reverse
from notifications.models import Notification

# Create your views here.

#------------------------------------------------------------
#   Right now this is a lot of shell code and temp variable/references.
# This is because I currently need the job model to be created. I also need
# Profiles and Jobs to have lists of skills for ranking. Profile roles are also
# needed for differentiating between a job seeker and a recruiter. 
#
# Once this is done I'll also need to test around and see if these should be login
# required. 
#-------------------------------------------------------------

#Shell code for getting job seekers
def recommend_candidates(job):
    seekers = Profile.objects.filter(role = "jobseeker") #Profile needs a role variable that allows to Find JS/R
    ranked = []

    for s in seekers:
        score = 0

        skill_matches = set(s.skills) & set(job.required_skills) #Need list of skills on both User and Job Postings
        score += len(skill_matches) * 2

        if s.location == job.location:
            score += 1

        ranked.append((s, score))
    
    return sorted(ranked, key=lambda x: x[1], reverse=True)

def recommend_jobs(profile):
    jobs = 1 
    ranked = []

    for job in jobs:
        score = 0

        seeker_skills = set(profile.skills)
        job_skills = set(job.required_skills)
        skill_matches = seeker_skills & job_skills
        score += len(skill_matches) * 2

        if profile.location and job.location:
            if profile.location.lower() == job.location.lower():
                score += 1
        
        ranked.append((job, score))
    
    return sorted(ranked, key=lambda x: x[1], reverse=True)
    

def recommendations_page(request):
    profile = request.user.profile

    if profile.role == "recruiter":
        jobs = 1 
        job_recommendations = []

        for job in jobs:
            candidates = recommend_candidates(job)
            job_recommendations.append({
                "job": job,
                "candidates": candidates
            })
        
        return render(request, "recommendations.html", {
            "user_profile": profile,
            "job_recommendations": job_recommendations,
            "job_results": []
        })
    
    else:
        job_results = recommend_jobs(profile)
        return render(request, "recommendations.html", {
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
