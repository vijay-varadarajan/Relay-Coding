from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login_view"),
    path("register/", views.register_view, name="register_view"),
    path("logout/", views.logout_view, name="logout_view"),
    path("create/", views.create_team_view, name="create_team_view"),
    path("join/", views.join_team_view, name="join_team_view"),
    path("leave/", views.leave_team_view, name="leave_team_view"),
]
