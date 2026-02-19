from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='seeker')
    display_name = models.CharField(max_length=80, blank=True)
    school_or_job = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=120, blank=True)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    about_me = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    skills = models.TextField(blank=True, default="")
    headline = models.CharField(max_length=160, blank=True, default="")
    education = models.TextField(blank=True, default="")
    work_experience = models.TextField(blank=True, default="")
    linkedin_url = models.URLField(blank=True, default="")
    github_url = models.URLField(blank=True, default="") 
    portfolio_url = models.URLField(blank=True, default="") 

    show_contact_email = models.BooleanField(default=True)
    show_contact_phone = models.BooleanField(default=True)
    show_location = models.BooleanField(default=True)
    show_school_or_job = models.BooleanField(default=True)
    show_about_me = models.BooleanField(default=True)
    show_skills = models.BooleanField(default=True)
    show_education = models.BooleanField(default=True)
    show_work_experience = models.BooleanField(default=True)
    show_links = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.user.username} Profile"