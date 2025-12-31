from django.db import models
from django.contrib.auth.models import User
import os
import secrets
import string
'''
class Clase(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clases_creadas')
    #imagen = models.ImageField(upload_to='clases/', null=True, blank=True)
    #organiza las fotos de portadas en la carpeta media/clases/clases_[id de la clase]/portada_[nombre del archivo]
    #Tengo que hacer que la foto de la portada se pasen a webm y se ajusten bien 

    imagen = models.ImageField(
        upload_to=lambda instance, filename: f'clases/clase_{instance.id}/portada_{filename}',
        null=True, 
        blank=True
    )

    students = models.ManyToManyField(User, related_name='clases_inscritas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

'''


def generar_id_clase():

    caracteres = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(10))

class Clase(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=10,
        default=generar_id_clase,
        editable=False,
        unique=True
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clases_creadas')
    imagen = models.ImageField(upload_to='clases/temp/', null=True, blank=True)
    students = models.ManyToManyField(
        User, 
        through='ClaseMembership',
        related_name='clases_inscritas', 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.name} ({self.id})"
    
    def save(self, *args, **kwargs):

        if not self.id:
            self.id = generar_id_clase()

            while Clase.objects.filter(id=self.id).exists():
                self.id = generar_id_clase()
        
        if self.id and not self.imagen:

            super().save(*args, **kwargs)
        elif self.id and self.imagen:

            file_extension = os.path.splitext(self.imagen.name)[1]
            new_filename = f'portada{file_extension}'
            self.imagen.name = f'clases/clase_{self.id}/{new_filename}'
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

class ClaseMembership(models.Model):
    ROLES = (
        ('student', 'Estudiante'),
        ('teacher', 'Profesor'),
        ('assistant', 'Asistente'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default='student')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'clase') 
    
    def __str__(self):
        return f"{self.user.username} - {self.clase.name} ({self.role})"