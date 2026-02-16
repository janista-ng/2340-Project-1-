from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    id = models.Autofield(primary_key=True)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    skills = models.TextField(help_text="Please list required skills here")
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Please list the annual salary in USD here")
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
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
