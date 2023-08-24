from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Team, Submission

@login_required(login_url='/login')
def home(request):
    user = request.user
        
    # Access the team information using the reverse relationships
    team = Team.objects.get(member1=user)
    
    print("Team Name:", team)
    
    return render(request, "portal/home.html", {
        'user': user, 'team': team, 'message': '',
    })


@login_required(login_url='/login')
def create_team_view(request):
    if request.method == "POST":
        joined_team = User.objects.get(username=request.user.username).in_team
        message = ''
        team_name = request.POST["team_name"]
        team_passcode = request.POST["team_passcode"]

        if not team_name:
            message = "Team name cannot be empty!"
            return render(request, "portal/create_team.html", {
                'message': message,
            })
        if not team_passcode:
            message = "Team passcode cannot be empty!"
            return render(request, "portal/create_team.html", {
                'message': message,
            })
        
        
        # update database
        new_team = Team(team_name=team_name, team_passcode=team_passcode, member1=request.user)
        new_team.save()
        
        user = User.objects.get(username=request.user.username)
        user.in_team = True
        user.save()

        message = "Team created successfully!"
    

        return HttpResponseRedirect(reverse("home"))
    return render(request, "portal/create_team.html", {
        'message': '',
    })


def join_team_view(request):
    if request.method == "POST":
        
        team_name = request.POST["team_name"]
        team_passcode = request.POST["team_passcode"]

        # check if team name and passcode in database matches
        try:
            team = Team.objects.get(team_name=team_name)
            if team.team_passcode != team_passcode:
                return render(request, "portal/join_team.html", {
                    'message': "Incorrect passcode!",
                })
            # update database
            user = User.objects.get(username=request.user.username)
            user.in_team = True
            user.save()

            team = Team.objects.get(team_name=team_name)
            if not team.member2:
                team.member2 = user
            elif not team.member3:
                team.member3 = user
            elif not team.member4:
                team.member4 = user
            else:
                return render(request, "portal/join_team.html", {
                    'message': "Team is full!",
                })
            team.save()
        except Team.DoesNotExist:
            return render(request, "portal/join_team.html", {
                'message': "Team does not exist!",
            })

        return HttpResponseRedirect(reverse("home"), {})
    return render(request, "portal/join_team.html")


def leave_team_view(request):
    if request.method == "POST":

        user = User.objects.get(username=request.user.username)
        user.in_team = False
        user.save()

        #tbd

    return HttpResponseRedirect(reverse("home"), {
        'user': user, 'message': '',
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        if not username:
            return render(request, "portal/login.html", {
                "message": "Username cannot be empty!"
            })
        if not password:
            return render(request, "portal/login.html", {
                "message": "Password cannot be empty!"
            })
        # authenticate user
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
        else:
            return render(request, "portal/login.html", {
                "message": "Invalid username and/or password."
            })
        return HttpResponseRedirect(reverse("home"))
    return render(request, "portal/login.html")


def register_view(request):
    if request.method == "POST":
        name = request.POST["name"]
        username = request.POST["username"]
        email = request.POST["email"]
        
        password = request.POST["password"]
        retype_password = request.POST["retype_password"]
        
        if password != retype_password:
            return render(request, "portal/register.html", {
                "message": "Passwords must match!"
            })
        
        try:
            user = User.objects.create_user(name=name, username=username, email=email, password=password)
            user.save()
        except IntegrityError:
            return render(request, "portal/register.html", {
                "message": "Username/Email already taken!"
            })
        
        # here i need to log the user in as well
        login(request, user)
        return HttpResponseRedirect(reverse("home"))
    
    return render(request, "portal/register.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))
