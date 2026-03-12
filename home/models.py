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
    city = models.CharField(max_length=120, blank=True, default="")
    state = models.CharField(max_length=120, blank=True, default="")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    commute_radius = models.IntegerField(default=50)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    about_me = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    skills = models.TextField(
        blank=True,
        default="", 
        help_text="Please list required skills here seperated by commas, eg. Python, SQL, JAVA"
    )
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

    def save(self, *args, **kwargs):
        """Sync location display string from city/state when set."""
        if self.city and self.state:
            self.location = f"{self.city}, {self.state}"
        elif self.city:
            self.location = self.city
        elif self.state:
            self.location = self.state
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} Profile"