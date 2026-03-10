from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile
from proj2.admin_utils import export_as_csv


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    extra = 0


class CustomUserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "get_role")
    actions = [export_as_csv]

    def get_role(self, obj):
        try:
            return obj.profile.role
        except Profile.DoesNotExist:
            return "No profile"
    get_role.short_description = "Role"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "display_name", "school_or_job", "location")
    search_fields = ("user__username", "user__email", "display_name", "location")
    list_filter = ("role",)
    actions = [export_as_csv]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)