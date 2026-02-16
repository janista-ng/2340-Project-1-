from django.contrib import admin
from .models import Job, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'poster', 'city', 'state', 'remote', 'visa_sponsorship', 'created_at')
    search_fields = ('title', 'company', 'skills', 'city', 'state')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'applied_at')
    search_fields = ('job__title', 'applicant__username')
    list_filter = ('status',)
