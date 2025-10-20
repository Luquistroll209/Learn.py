from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        #Esto es lo que pide el request al cliente para que sea correcto
        fields = ('username', 'password', 'email');
        extra_kwargs = {'password': {'write_only': True}}

        #Crea las variables y el usuario en la base de datos 
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user