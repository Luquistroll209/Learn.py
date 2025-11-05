from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
#ver info de la gente
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'clases']