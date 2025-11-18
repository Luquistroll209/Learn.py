from django.db import models
from django.contrib.auth.models import User
from clases.models import Clase
from clases.serializers import ClaseSerializer

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Almacena las clases como lista JSON para poder usarlas en el futuro
    clases = ClaseSerializer(many=True, read_only=True, source='clases_inscritas') 
    notifications = models.JSONField(default=list, blank=True)
    def __str__(self):
        return f"{self.user.username} - Profile"