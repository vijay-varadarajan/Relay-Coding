from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User

@login_required(login_url='/login')
def home(request):
    return render(request, "portal/home.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
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
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        username = request.POST["username"]
        email = request.POST["email"]
        
        password = request.POST["password"]
        retype_password = request.POST["retype_password"]
        
        if password != retype_password:
            return render(request, "portal/register.html", {
                "message": "Passwords must match!"
            })
        
        try:
            user = User.objects.create_user(firstname=firstname, lastname=lastname, username=username, email=email, password=password)
            user.save()
        except IntegrityError:
            return render(request, "portal/register.html", {
                "message": "Username/Email already taken!"
            })
        
        # here i need to log the user in as well
        login(request, user)
        return HttpResponseRedirect(reverse("home"))
    
    return render(request, "portal/register.html")
