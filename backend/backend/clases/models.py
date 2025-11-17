from django.db import models
from django.contrib.auth.models import User

class Clase(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clases_creadas')
    students = models.ManyToManyField(User, related_name='clases_inscritas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name