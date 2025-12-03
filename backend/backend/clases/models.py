from django.db import models
from django.contrib.auth.models import User

class Clase(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clases_creadas')
    imagen = models.ImageField(upload_to='clases/', null=True, blank=True)
    students = models.ManyToManyField(User, related_name='clases_inscritas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name