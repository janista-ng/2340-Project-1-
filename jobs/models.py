from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    skills = models.TextField(
        help_text="Please list required skills here seperated by commas, eg. python, sql, java"
    )
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Please list the annual salary in USD here")
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=120, blank=True, default="")
    state = models.CharField(max_length=120, blank=True, default="")
    location = models.CharField(max_length=200, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    REMOTE_CHOICES = (('remote', 'Remote'), ('on_site', 'On-site'), ('hybrid', 'Hybrid'),)
    remote = models.CharField(max_length=10, choices=REMOTE_CHOICES, default='on_site')
    VISA_CHOICES = (('yes', 'Visa Sponsorship Available'), ('no', 'No Sponsorship Available'))
    visa_sponsorship = models.CharField(max_length=3, choices=VISA_CHOICES)
    is_active = models.BooleanField(default=True) 

    #Formats location off of city and state fields
    def save(self, *args, **kwargs):
        if self.city and self.state:
            self.location = f"{self.city}, {self.state}"
        elif self.city:
            self.location = self.city
        elif self.state:
            self.location = self.state
        else:
            self.location = ""
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class Application(models.Model):
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('review', 'Under Review'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('closed', 'Closed'),
    )

    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    cover_note = models.TextField(blank=True, default="", help_text="Optional personalized note for the recruiter")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('applicant', 'job')  

    def __str__(self):
        return f"{self.applicant.username} applied to {self.job.title}"

class SavedCandidateSearch(models.Model):
    recruiter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_candidate_searches",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="saved_searches",
    )

    name = models.CharField(max_length=120)

    q = models.CharField(max_length=120, blank=True, default="")
    skills = models.CharField(max_length=255, blank=True, default="")
    location = models.CharField(max_length=120, blank=True, default="")
    city = models.CharField(max_length=120, blank=True, default="")
    state = models.CharField(max_length=120, blank=True, default="")

    notify_on_new_matches = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.job.title})"

    def querystring(self):
        from urllib.parse import urlencode

        params = {}
        for key in ["q", "skills", "location", "city", "state"]:
            value = getattr(self, key, "")
            if value:
                params[key] = value
        return urlencode(params)

    def matches_application(self, application):
        if application.job_id != self.job_id:
            return False

        applicant = application.applicant
        profile = getattr(applicant, "profile", None)

        if self.q:
            q_lower = self.q.lower()
            haystacks = [
                applicant.username or "",
                applicant.first_name or "",
                applicant.last_name or "",
                applicant.email or "",
                getattr(profile, "display_name", "") or "",
            ]
            if not any(q_lower in value.lower() for value in haystacks if value):
                return False

        if self.skills:
            profile_skills = (getattr(profile, "skills", "") or "").lower()
            wanted_skills = [s.strip().lower() for s in self.skills.split(",") if s.strip()]
            for skill in wanted_skills:
                if skill not in profile_skills:
                    return False

        if self.location:
            profile_location = (getattr(profile, "location", "") or "").lower()
            if self.location.lower() not in profile_location:
                return False

        if self.city:
            profile_city = (getattr(profile, "city", "") or "").lower()
            if self.city.lower() not in profile_city:
                return False

        if self.state:
            profile_state = (getattr(profile, "state", "") or "").lower()
            if self.state.lower() not in profile_state:
                return False

        return True