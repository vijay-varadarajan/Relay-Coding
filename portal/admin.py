from django.contrib import admin
from .models import User, Team, Submission

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "username", "email", "in_team", "date_joined")

class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "team_name", "member1", "member2", "member3", "member4")

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "team", "title", "track", "description", "github_link", "drive_link")

admin.site.register(User, UserAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Submission, SubmissionAdmin)
