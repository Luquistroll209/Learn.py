from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import get_valid_filename
import os
import secrets
import string
import uuid
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
    imagen = models.ImageField(upload_to='clases/', null=True, blank=True)
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

#Funcion para los anuncios de la tabla de las clases
class Announcement(models.Model):
    clase = models.ForeignKey(
        Clase, 
        on_delete=models.CASCADE, 
        related_name='announcements'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='announcements_created'
    )
    #Para las urls de las fotos almacenadas en el backd (no funciona aun y terminar)
    photos = models.JSONField(default=list, blank=True)
    #Para las urls
    urls = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.clase.name}"


def task_submission_file_upload_to(instance, filename):
    safe_name = get_valid_filename(filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    return (
        f"tasks/clase_{instance.submission.task.clase_id}/"
        f"task_{instance.submission.task_id}/"
        f"user_{instance.submission.student_id}/{unique_name}"
    )


class Task(models.Model):
    clase = models.ForeignKey(
        Clase,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks_created'
    )
    due_at = models.DateTimeField(null=True, blank=True)
    allow_any_file_type = models.BooleanField(default=True)
    allowed_extensions = models.JSONField(default=list, blank=True)
    max_files = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    max_file_size_mb = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1), MaxValueValidator(1024)]
    )
    photos = models.JSONField(default=list, blank=True)
    urls = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.clase.name}"


class TaskSubmission(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='task_submissions'
    )
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    feedback = models.TextField(blank=True, default='')
    delivered_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('task', 'student')

    def __str__(self):
        return f"Entrega {self.task_id} - {self.student.username}"


class TaskSubmissionFile(models.Model):
    submission = models.ForeignKey(
        TaskSubmission,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(upload_to=task_submission_file_upload_to)
    original_name = models.CharField(max_length=255)
    extension = models.CharField(max_length=20, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.original_name} ({self.submission_id})"
