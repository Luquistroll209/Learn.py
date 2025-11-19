from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'subject', 'message', 'to', 'created_by', 'is_read', 'created_at']