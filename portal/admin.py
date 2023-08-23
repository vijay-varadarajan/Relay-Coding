from django.contrib import admin
from .models import User

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "firstname", "username", "email", "date_joined")

admin.site.register(User, UserAdmin)