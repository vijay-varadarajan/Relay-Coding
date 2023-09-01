from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass
    def __str__(self):
        return f"{self.id} ({self.username})"
    

class Team(models.Model):
    team_name = models.CharField(max_length=128, unique=True)
    team_passcode = models.CharField(max_length=128)
    members_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.team_name}: {self.members_count} members"
    

class UserStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    in_team = models.BooleanField(default=False)
    joined_team = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name="joined_team", blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.in_team} - {self.joined_team}"


class Submission(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team")
    title = models.CharField(max_length=128)
    track = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    github_link = models.URLField(max_length=256, blank=True, null=True)
    drive_link = models.URLField(max_length=256, blank=True, null=True)

    def __str__(self):
        return f"{self.team} - {self.title}"

    