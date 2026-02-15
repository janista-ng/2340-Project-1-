from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=80, blank=True)
    school_or_job = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=120, blank=True)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    about_me = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    about_me = models.TextField(blank=True)


    def __str__(self):
        return f"{self.user.username} Profile"