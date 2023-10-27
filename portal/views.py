from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib import messages
from django.template.loader import render_to_string

import regex as re

from .tokens import account_activation_token
from .models import User, Team, Submission, UserStatus


@login_required(login_url='/login')
def userhome(request):
    user = request.user
    user_status = UserStatus.objects.get(user=user)
    
    if user_status.in_team:
        team = Team.objects.get(team_name=user_status.joined_team.team_name)

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
            messages.error(request, "Project title cannot be empty!")
            return HttpResponseRedirect(reverse("userhome") + '#submit')
        
        try:
            track = request.POST["track"]
        except:
            messages.error(request, "Select a track!")
            return HttpResponseRedirect(reverse("userhome") + '#submit')
        
        project_description = request.POST["project_description"]
        if not project_description:
            messages.error(request, "Project description cannot be empty!")
            return HttpResponseRedirect(reverse("userhome") + '#submit')
        
        github_link = request.POST["github_link"]
        
        drive_link = request.POST["drive_link"]

        # check if user is in a team
        if not user_status.in_team:
            messages.error(request, "You are not in a team!")
            return HttpResponseRedirect(reverse('create_team_view'))
        
        print(project_title, track, project_description, github_link, drive_link)
        
        submissions = Submission.objects.get(team=user_status.joined_team)
        submissions.title = project_title
        submissions.track = track
        submissions.description = project_description
        submissions.github_link = github_link
        submissions.drive_link = drive_link
        submissions.save()
        
        submissions = Submission.objects.get(team=user_status.joined_team)

        messages.success(request, "Idea submitted successfully!")
        return HttpResponseRedirect(reverse("userhome") + '#submit', {
            'user': request.user, 'submissions':submissions, 'message': 'Submitted successfully!', 'user_status':user_status,   
        })

    else:
        user = User.objects.get(username=request.user.username)
        user_status = UserStatus.objects.get(user=user)

        if not user_status.in_team:
            messages.error(request, "You are not in a team!")
            return HttpResponseRedirect(reverse("userhome") + "#submit")
        
        return HttpResponseRedirect(reverse("userhome") + "#submit")


@login_required(login_url='/login')
def create_team_view(request):
    if request.method == "POST":

        user = User.objects.get(username=request.user.username)
        user_status = UserStatus.objects.get(user=user)
        print(user_status)

        if user_status.in_team:
            messages.error(request, "You are already in a team!")
            return HttpResponseRedirect(reverse("userhome"))

        message = ''
        team_name = request.POST["team_name"]
        team_passcode = request.POST["team_passcode"]
        repeat_passcode = request.POST["repeat_passcode"]

        print(team_name, team_passcode, repeat_passcode)

        if team_passcode != repeat_passcode:
            messages.error(request, "Passcodes do not match!")
            return HttpResponseRedirect(reverse("create_team_view"))

        if not team_name:
            messages.error(request, "Team name cannot be empty!")
            return HttpResponseRedirect(reverse("create_team_view"))
        
        if not team_passcode:
            messages.error(request, "Passcode cannot be empty!")
            return HttpResponseRedirect(reverse("create_team_view"))
        
        # update database
        new_team = Team(team_name=team_name, team_passcode=team_passcode, members_count=1)

        user_status.in_team = True
        user_status.joined_team = new_team
        
        new_team.save()
        user_status.save()

        try:
            submissions = Submission.objects.get(team=new_team)
        except:
            submissions = Submission(team=new_team, title="", track="", description="", github_link="", drive_link="")
            submissions.save()
    
        return HttpResponseRedirect(reverse("userhome"))
    
    user = request.user
    user_status = UserStatus.objects.get(user=user)
    if user_status.in_team:
        return HttpResponseRedirect(reverse("userhome"))
    
    return render(request, "portal/create_team.html", {
        'message': '', 'user': request.user,
    })  


@login_required(login_url='/login')
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
            messages.error(request, "Team does not exist!")
            return HttpResponseRedirect(reverse("join_team_view"))
        
        # check if team passcode matches
        if team.team_passcode != team_passcode:
            messages.error(request, "Incorrect passcode!")
            return HttpResponseRedirect(reverse("join_team_view"))
        
        if team.members_count == 4:
            messages.error(request, "Team is full!")
            return HttpResponseRedirect(reverse("join_team_view"))

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


@login_required(login_url='/login')
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
            messages.error(request, "Username cannot be empty!")
            return HttpResponseRedirect(reverse("login_view"))
        
        if not password:
            messages.error(request, "Password cannot be empty!")
            return HttpResponseRedirect(reverse("login_view"))
        
        # authenticate user
        user = authenticate(request, username=username, password=password)
        print(user)

        # Check if authentication successful
        if user is not None:
            login(request, user)
        else:
            try:
                if not User.objects.get(username=username).is_active:
                    messages.error(request, "Account not activated, check your email for activation link.")
                    return HttpResponseRedirect(reverse("login_view"))
            except:
                pass

            messages.error(request, "Invalid username and/or password.")
            return HttpResponseRedirect(reverse("login_view"))
        
        user_status = UserStatus.objects.get(user=user)
        
        if user_status.in_team:
            return HttpResponseRedirect(reverse("userhome"))
        
        return HttpResponseRedirect(reverse("create_team_view"))
    
    return render(request, "portal/login.html")


def register_view(request):
    if request.method == "POST":
        first_name = request.POST["first_name"].strip()

        username = request.POST["username"].strip()
        if not len(str(username)) > 2:
            messages.error(request, "Username must be atleast 3 characters long!")
            return HttpResponseRedirect(reverse("register_view"))
        
        email = request.POST["email"].strip().lower()
        
        if not email:
            messages.error(request, "Email cannot be empty!")
            return HttpResponseRedirect(reverse("register_view"))
        
        # check if email matches regex
        if not re.match(r"^[a-zA-Z]+\.[a-zA-Z]+[0-9]{4}@vitstudent.ac.in$", email):
            messages.error(request, "Must provide VIT email ID")
            return HttpResponseRedirect(reverse("register_view"))

        try:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email ID already registered, try logging in or register with a different Email ID.")
                return HttpResponseRedirect(reverse("register_view"))
        except:
            pass

        password = request.POST["password"].strip()
        # regex to validate password
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{4,}$", password):
            messages.error(request, "Password must be atleast 4 characters long and contain atleast 1 uppercase letter, 1 lowercase letter, 1 number, no whitespace and no symbols!")
            return HttpResponseRedirect(reverse("register_view"))   
        
        retype_password = request.POST["retype_password"].strip()
        
        if password != retype_password:
            messages.error(request, "Passwords must match!")
            return HttpResponseRedirect(reverse("register_view"))
        
        try:
            user = User.objects.create_user(first_name=first_name, username=username, email=email, password=password, is_active=False)
            user.save()
            
        except IntegrityError:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken, try logging in.")
                return HttpResponseRedirect(reverse("register_view"))
            
            else:
                messages.error(request, "Error creating account, try again.")
                return HttpResponseRedirect(reverse("register_view"))
        
        # update user status table
        user_status = UserStatus.objects.create(user=user)
        user_status.save()  

        print("user status created")

        activateEmail(request, user, email)
        
        messages.success(request, "Account created successfully! Check your email for activation link.")
        return HttpResponseRedirect(reverse("login_view"))
    
    return render(request, "portal/register.html")


def activateEmail(request, user, to_email):
    mail_subject = 'Activate your account.'
    message = render_to_string('portal/activate_email.html', {
        'user': user.username, 
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })

    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        print("Email sent")
    else:
        print("Error sending Email")


def activate(request, uidb64, token):
    try:
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Account activated successfully!")
        return HttpResponseRedirect(reverse("login_view"))
    
    messages.error(request, "Activation link expired!")
    return HttpResponseRedirect(reverse("login_view"))


def home(request):
    return render(request, "portal/home.html", {
        'user': request.user, 'message': '',
    })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))


def password_reset_email_form_view(request):
    if request.method == "POST":
        email = request.POST["email"].strip().lower()

        if not email:
            messages.error(request, "Email cannot be empty!")
            return HttpResponseRedirect(reverse("password_reset_email_form_view"))
        
        # check if email matches regex
        if not re.match(r"^[a-zA-Z]+\.[a-zA-Z]+[0-9]{4}@vitstudent.ac.in$", email):
            messages.error(request, "Must provide VIT email ID")
            return HttpResponseRedirect(reverse("password_reset_email_form_view"))
        
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "Email not registered")
            return HttpResponseRedirect(reverse("password_reset_email_form_view"))
        
        if user:
            subject = "Password reset request"
            message = render_to_string('portal/password_reset_email.html', {
                'user': user.username, 
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http',
            })

            email = EmailMessage(subject, message, to=[user.email])
            if email.send():
                print("Reset password Email sent")
                messages.success(request, "Password reset link sent to your email!")
            else:
                print("Error sending Reset password Email")
                messages.error(request, "Error sending password reset link!")

        return HttpResponseRedirect(reverse("login_view"))

    return render(request, "portal/password_reset_email_form.html")


def reset(request, uidb64, token):
    try:
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
    except:
        user = None

    print(user)

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == "POST":
            password = request.POST["password"]

            # regex to validate password
            if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{4,}$", password):
                messages.error(request, "Password must be atleast 4 characters long and contain atleast 1 uppercase, 1 lowercase, 1 number and no whitespace!")
                return HttpResponseRedirect(reverse("reset", args=(uidb64, token)))
            
            retype_password = request.POST["retype_password"]
            
            if password != retype_password:
                messages.error(request, "Passwords must match!")
                return HttpResponseRedirect(reverse("reset", args=(uidb64, token)))
            
            user.set_password(password)
            user.save()

            print("Password reset successful")

            messages.success(request, "Password reset successful!")
            return HttpResponseRedirect(reverse("login_view"))
        
        return render(request, "portal/password_reset.html")
    
    messages.error(request, "Password reset link expired!")
    return HttpResponseRedirect(reverse("password_reset_email_form_view"))
