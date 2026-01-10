from rest_framework import serializers
from django.contrib.auth.models import User
from clases.models import Clase, ClaseMembership, Announcement

#serializer para los anuncios de clase
class AnnouncementSerializer(serializers.ModelSerializer):
    creator_info = serializers.SerializerMethodField()
    is_teacher = serializers.SerializerMethodField()
    clase_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 
            'title', 
            'clase_id',
            'description', 
            'photos', 
            'urls', 
            'creator_info',
            'is_teacher',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        clase_id = validated_data.pop('clase_id')
        clase = Clase.objects.get(id=clase_id)
        user = self.context['user']
        
        announcement = Announcement.objects.create(
            clase=clase,
            created_by=user,
            **validated_data
        )
        return announcement
    
    def get_creator_info(self, obj):
        creator = obj.created_by
        return {
            'id': creator.id,
            'username': creator.username,
            'first_name': creator.first_name or '',
            'last_name': creator.last_name or '',
            'email': creator.email
        }
    
    def get_is_teacher(self, obj):
        try:
            membership = ClaseMembership.objects.get(
                user=obj.created_by,
                clase=obj.clase
            )
            return membership.role == 'teacher'
        except ClaseMembership.DoesNotExist:
            return False
        
class ClaseSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(required=False, allow_null=True, write_only=True)
    imagen_url = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    #students = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    students_info = serializers.SerializerMethodField()
    announcements = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Clase
        fields = ['id', 'name', 'description', 'teacher', 'teacher_name', 'imagen', 'imagen_url', 'created_at', 'students_info', 'announcements']
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
    
    def get_students_info(self, obj):
        memberships = ClaseMembership.objects.filter(clase=obj)
        members_data = []
        for membership in memberships:
            members_data.append({
                'user_id': membership.user.id,
                'username': membership.user.username,
                'email': membership.user.email,
                'role': membership.role,
                'joined_at': membership.joined_at
            })
        return members_data