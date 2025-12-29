from rest_framework import serializers
from django.contrib.auth.models import User
from clases.models import Clase

class ClaseSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(required=False, allow_null=True, write_only=True)
    imagen_url = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Clase
        fields = ['id', 'name', 'description', 'teacher', 'teacher_name', 'imagen', 'imagen_url', 'created_at']
        read_only_fields = ['id', 'teacher', 'created_at', 'imagen_url']
    
    def get_imagen_url(self, obj):
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None
    
    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name() or obj.teacher.username
    
    def create(self, validated_data):
        imagen = validated_data.pop('imagen', None)
        
        teacher = self.context.get('teacher') or self.context['request'].user
        validated_data['teacher'] = teacher
        clase = Clase.objects.create(**validated_data)
        

        if imagen:
            clase.imagen = imagen
            clase.save()
        
        return clase