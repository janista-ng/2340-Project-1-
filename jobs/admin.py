from django.contrib import admin
from .models import Job, Application
from proj2.admin_utils import export_as_csv

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title", "company", "recruiter", "city", "state",
        "remote", "visa_sponsorship", "is_active", "created_at"
    )
    search_fields = ("title", "company", "skills", "city", "state", "recruiter__username")
    list_filter = ("is_active", "remote", "visa_sponsorship", "created_at")
    actions = ("deactivate_jobs", "activate_jobs", "export_selected_jobs")

    @admin.action(description="Deactivate selected jobs (hide from job list)")
    def deactivate_jobs(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Activate selected jobs (show in job list)")
    def activate_jobs(self, request, queryset):
        queryset.update(is_active=True)
    
    @admin.action(description="Export selected jobs to CSV")
    def export_selected_jobs(self, request, queryset):
        return export_as_csv(self, request, queryset)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'applied_at')
    search_fields = ('job__title', 'applicant__username')
    list_filter = ('status',)
    actions = ("export_selected_applications",)

    @admin.action(description="Export selected applications to CSV")
    def export_selected_applications(self, request, queryset):
        return export_as_csv(self, request, queryset)