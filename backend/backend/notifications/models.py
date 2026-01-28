from django.db import models
from django.contrib.auth.models import User
from clases.models import Clase


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('sent', 'Enviado'),
        ('received', 'Recibido'),
    ]
    
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='received')

    def __str__(self):
        return self.subject