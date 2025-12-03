from rest_framework import serializers
from django.contrib.auth.models import User
from clases.models import Clase


class ClaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clase
        fields = ['id', 'name', 'description', 'teacher', 'imagen']
