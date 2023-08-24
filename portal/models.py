from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name = models.CharField(max_length=128)
    username = models.CharField(max_length=128, unique=True)
    email = models.EmailField(max_length=128, unique=True)
    password = models.CharField(max_length=128)
    in_team = models.BooleanField(default=False)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',  # Change this to a unique name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # Change this to a unique name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return f"{self.name} ({self.username})"
    

class Team(models.Model):
    team_name = models.CharField(max_length=128, unique=True)
    team_passcode = models.CharField(max_length=128)
    member1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="member1")
    member2 = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="member2", blank=True, null=True)
    member3 = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="member3", blank=True, null=True)
    member4 = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="member4", blank=True, null=True)
    submission = models.ForeignKey('Submission', on_delete=models.SET_NULL, related_name="submission", blank=True, null=True)

    def __str__(self):
        return f"{self.team_name} 1. {self.member1} 2. {self.member2} 3. {self.member3} 4. {self.member4}"
    

class Submission(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team")
    title = models.CharField(max_length=128)
    track = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    github_link = models.URLField(max_length=256, blank=True, null=True)
    drive_link = models.URLField(max_length=256, blank=True, null=True)

    def __str__(self):
        return f"{self.team} - {self.title}"

    