from jobs.models import Job
from home.models import Profile
import math

def parse_skills(skill_string):
    if not skill_string:
        return set()
    return set(
        s.strip().lower()
        for s in skill_string.split(",")
        if s.strip()
    )

def distance_miles(lat1, lon1, lat2, lon2):
    R = 3959

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

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

        if (
            job.latitude is None or
            job.longitude is None
        ) :
            continue

        job_skills = parse_skills(job.skills)

        overlap = user_skills.intersection(job_skills)
        score = len(overlap)

        distance = distance_miles(
            profile.latitude,
            profile.longitude,
            job.latitude,
            job.longitude
        )
        if distance > profile.commute_radius:
            continue
        else:
            score += 3
        
        if job.remote == "remote":
            score += 1

        if score > 0:
            recommendations.append((job, score))
        
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations  
    