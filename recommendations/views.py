from django.shortcuts import render
from home.models import Profile
from jobs.models import Job


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
    # print("SEEKER COUNT:", seekers.count())
    # print("SEEKERS:", list(Profile.objects.values("role", "skills")))
    # print("JOBS:", list(Job.objects.values("skills")))
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

        # print("MATCH:", s.user.username, skill_matches, "SCORE:", score)

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

    # print("ROLE:", profile.role)
    if profile.role == "recruiter":
        # print("JOB COUNT:", Job.objects.all().count())
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
