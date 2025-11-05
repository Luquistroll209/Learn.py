from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Almacena las clases como lista JSON para poder usarlas en el futuro
    clases = models.JSONField(default=list, blank=True) 

    def __str__(self):
        return f"{self.user.username} - Profile"