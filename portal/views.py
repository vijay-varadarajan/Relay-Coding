from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Team, Submission, UserStatus

@login_required(login_url='/login')
def userhome(request):
    user = request.user
    user_status = UserStatus.objects.get(user=user)
    
    if user_status.in_team:
        team = Team.objects.get(team_name=user_status.joined_team.team_name)

        # complete team members functionality
        # get the usernames from user table of all users in user_status where joined_team matches team
        members_ids = []
        for qset in UserStatus.objects.filter(joined_team = team):
            members_ids.append(qset.user.id)

        members = []
        for member_id in members_ids:
            members.append(User.objects.get(id = member_id))

        submissions = Submission.objects.get(team=user_status.joined_team)

        return render(request, "portal/userhome.html", {
            'in_team': True, 'members': members, 'submissions':submissions, 'team':team , 'message': '',
        })
    
    return HttpResponseRedirect(reverse("create_team_view"))


@login_required(login_url='/login')
def submission_view(request):
    if request.method == "POST":
        
        user = User.objects.get(username=request.user.username)
        user_status = UserStatus.objects.get(user=user)

        project_title = request.POST["project_title"]
        if not project_title:
            return render(request, "portal/userhome.html", {
                'message': "Project title cannot be empty!", 'user': request.user, 'user_status':user_status,
            })
        
        try:
            track = request.POST["track"]
        except:
            return render(request, "portal/userhome.html", {
                'message': "Track cannot be empty!", 'user': request.user, 'user_status':user_status,
            })
        
        project_description = request.POST["project_description"]
        if not project_description:
            return render(request, "portal/userhome.html", {
                'message': "Project description cannot be empty!", 'user': request.user,'user_status':user_status,
            })
        
        github_link = request.POST["github_link"]
        
        drive_link = request.POST["drive_link"]

        # check if user is in a team
        if not user_status.in_team:
            return render(request, "portal/userhome.html", {
                'message': "Create or join a team to submit idea!", 'user': request.user, 'user_status':user_status,
            })
        
        print(project_title, track, project_description, github_link, drive_link)
        
        submissions = Submission.objects.get(team=user_status.joined_team)
        submissions.title = project_title
        submissions.track = track
        submissions.description = project_description
        submissions.github_link = github_link
        submissions.drive_link = drive_link
        submissions.save()
        
        submissions = Submission.objects.get(team=user_status.joined_team)

        return HttpResponseRedirect(reverse("userhome") + '#submit', {
            'user': request.user, 'submissions':submissions, 'message': 'Submitted successfully!', 'user_status':user_status,   
        })

    else:
        user = User.objects.get(username=request.user.username)
        user_status = UserStatus.objects.get(user=user)

        if not user_status.in_team:
            return HttpResponseRedirect(reverse("userhome") + "#submit")
        
        return HttpResponseRedirect(reverse("userhome") + "#submit")

@login_required(login_url='/login')
def create_team_view(request):
    if request.method == "POST":
        # check if userstatus.in_team is true for user id from user table
        user = User.objects.get(username=request.user.username)
        user_status = UserStatus.objects.get(user=user)
        print(user_status)

        if user_status.in_team:
            return render(request, "portal/create_team.html", {
                'message': "You are already in a team!",
            })

        message = ''
        team_name = request.POST["team_name"]
        team_passcode = request.POST["team_passcode"]
        repeat_passcode = request.POST["repeat_passcode"]

        print(team_name, team_passcode, repeat_passcode)

        if team_passcode != repeat_passcode:
            message = "Passcodes are not the same"
            return render(request, "portal/create_team.html", {
                'message': message, 'user': request.user,
            })

        if not team_name:
            message = "Team name cannot be empty!"
            return render(request, "portal/create_team.html", {
                'message': message, 'user': request.user,
            })
        if not team_passcode:
            message = "Team passcode cannot be empty!"
            return render(request, "portal/create_team.html", {
                'message': message, 'user': request.user,
            })
        
        
        # update database
        new_team = Team(team_name=team_name, team_passcode=team_passcode)
        print("new team created")

        user_status.in_team = True
        user_status.joined_team = new_team
        print("user status updated")
        
        new_team.save()
        user_status.save()
        print("saved")

        try:
            submissions = Submission.objects.get(team=new_team)
        except:
            submissions = Submission(team=new_team, title="", track="", description="", github_link="", drive_link="")
            submissions.save()

        print("checked submissions")

        message = "Team created successfully!"
    
        return HttpResponseRedirect(reverse("userhome"))
    
    user = request.user
    user_status = UserStatus.objects.get(user=user)
    if user_status.in_team:
        return HttpResponseRedirect(reverse("userhome"))
    
    return render(request, "portal/create_team.html", {
        'message': '', 'user': request.user,
    })  


def join_team_view(request):
    if request.method == "POST":
        
        user_status = UserStatus.objects.get(user=request.user)
        if user_status.in_team:
            return HttpResponseRedirect(reverse("userhome"))
        
        team_name = request.POST["team_name"]
        team_passcode = request.POST["team_passcode"]

        # check if team name exists
        try:
            team = Team.objects.get(team_name=team_name)
        except:
            return render(request, "portal/join_team.html", {
                'message': "Team does not exist!", 'user': request.user,
            })
        
        # check if team passcode matches
        if team.team_passcode != team_passcode:
            return render(request, "portal/join_team.html", {
                'message': "Incorrect passcode!", 'user': request.user,
            })
        
        if team.members_count == 4:
            return render(request, "portal/join_team.html", {
                'message': "Team is full!", 'user': request.user,
            })

        # update userstatus with teamname and joined team
        user_status = UserStatus.objects.get(user=request.user)
        user_status.in_team = True
        user_status.joined_team = team
        user_status.save()

        # update members_count in teams
        team.members_count += 1
        team.save()
        
        return HttpResponseRedirect(reverse("userhome"))
    
    user = request.user
    user_status = UserStatus.objects.get(user=user)
    if user_status.in_team:
        return HttpResponseRedirect(reverse("userhome"))
    
    return render(request, "portal/join_team.html", {
        'message': '', 'user': request.user,
    })


def leave_team_view(request):

    user = User.objects.get(username=request.user.username)
    user_status = UserStatus.objects.get(user=user)

    team = Team.objects.get(team_name=user_status.joined_team.team_name)
    team.members_count -= 1


    user_status.in_team = False
    user_status.joined_team = None
    user_status.save()

    if team.members_count == 0:
        team.delete()
    else:
        team.save()

    return HttpResponseRedirect(reverse("userhome"))


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
        
        user_status = UserStatus.objects.get(user=user)
        if user_status.in_team:
            return HttpResponseRedirect(reverse("userhome"))
        return render(request, "portal/create_team.html", {
            'user': request.user, 'message': 'Create or join an existing team!',
        })
    
    return render(request, "portal/login.html")


def register_view(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        
        username = request.POST["username"]
        email = request.POST["email"]
        
        password = request.POST["password"]
        retype_password = request.POST["retype_password"]
        
        if password != retype_password:
            return render(request, "portal/register.html", {
                "message": "Passwords must match!"
            })
        
        try:
            user = User.objects.create_user(first_name=first_name, username=username, email=email, password=password)
            user.save()
            
        except IntegrityError:
            return render(request, "portal/register.html", {
                "message": "Username/Email already taken!"
            })
        
        # update user status table
        user_status = UserStatus.objects.create(user=user)
        user_status.save()
        
        # here i need to log the user in as well
        login(request, user)
        return HttpResponseRedirect(reverse("userhome"))
    
    return render(request, "portal/register.html")


def home(request):
    return render(request, "portal/home.html", {
        'user': request.user, 'message': '',
    })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))
