from django.contrib import admin
from .models import User, Team, Submission, UserStatus

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name", "is_staff", "is_active", "is_superuser")

class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "team_name", "members_count")


class UserStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "in_team", "joined_team")

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "team", "title", "track", "description", "github_link", "drive_link")

admin.site.register(User, UserAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(UserStatus, UserStatusAdmin)
admin.site.register(Submission, SubmissionAdmin)
