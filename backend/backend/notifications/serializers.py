from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notification

class SafeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class NotificationSerializer(serializers.ModelSerializer):
    # Usa SerializerMethodField que es más seguro
    to_info = serializers.SerializerMethodField()
    created_by_info = serializers.SerializerMethodField()
    
    def get_to_info(self, obj):
        if obj.to:
            return {
                'id': obj.to.id,
                'username': obj.to.username,
                'email': obj.to.email,
                'last_name': obj.to.last_name
            }
        return None
    
    def get_created_by_info(self, obj):
        if obj.created_by:
            return {
                'id': obj.created_by.id,
                'username': obj.created_by.username,
                'email': obj.created_by.email,
                'last_name': obj.created_by.last_name
            }
        return None
    
    class Meta:
        model = Notification
        fields = [
            'id', 'subject', 'message', 
            'to', 'to_info',
            'created_by', 'created_by_info', 
            'is_read', 'created_at', 'notification_type'
        ]