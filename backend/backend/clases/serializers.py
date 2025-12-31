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
        teacher = obj.teacher
        if hasattr(teacher, 'last_name') and teacher.last_name:
            if hasattr(teacher, 'name') and teacher.name:
                return f"{teacher.last_name} {teacher.name}"
            elif hasattr(teacher, 'first_name') and teacher.first_name:
                return f"{teacher.last_name} {teacher.first_name}"
        return teacher.username or str(teacher)
    
    def create(self, validated_data):
        imagen = validated_data.pop('imagen', None)
        
        teacher = self.context.get('teacher') or self.context['request'].user
        validated_data['teacher'] = teacher
        clase = Clase.objects.create(**validated_data)
        

        if imagen:
            clase.imagen = imagen
            clase.save()
        
        return clase