from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile
from clases.serializers import ClaseSerializer

class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, source='username')
    clases = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    
    class Meta:
        model = User
        #Variables del usuario
        fields = ('name', 'last_name', 'password', 'email', 'clases')
        extra_kwargs = {
                        'name' : {'required': True},
            'last_name' : {'required': True},
            'password': {'write_only': True},
            'email': {'required': True}
        }

    # Función para verificar si el usuario ya existe
    #def validate_name(self, value):
    #    if User.objects.filter(username=value).exists():
    #        raise serializers.ValidationError("Este usuario ya existe")
    #    return value

    # Función para verificar si el email ya existe
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado")
        return value

    # Crea el usuario en la base de datos
    def create(self, validated_data):
        clases = validated_data.pop('clases', [])
        notificaciones = validated_data.pop('notificaciones', [])
        
        user = User.objects.create_user(
            username=validated_data['username'],
            last_name=validated_data['last_name'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        
        return user


class UserInfoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='username')
    
    class Meta:
        model = User
        fields = ('id', 'name', 'last_name', 'email', 'date_joined', 'is_active')
        read_only_fields = fields

class TokenUserInfoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='username')
    clases = serializers.SerializerMethodField()
    notifications = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'name', 'last_name', 'email', 'date_joined', 'is_active', 'clases', 'notifications')
        read_only_fields = fields

    #obtener notificaciones
    def get_clases(self, obj):
        try:
            user_clases = obj.clases_inscritas.all()
            return ClaseSerializer(user_clases, many=True).data
        except:
            return []

    #Obtener notificaciones del usuario
    def get_notifications(self, obj):
        from notifications.models import Notification
        from notifications.serializers import NotificationSerializer
        
        notifications = Notification.objects.filter(to=obj)
        return NotificationSerializer(notifications, many=True).data