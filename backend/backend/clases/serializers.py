from rest_framework import serializers
from django.contrib.auth.models import User
from clases.models import (
    Clase,
    ClaseMembership,
    Announcement,
    Task,
    TaskSubmission,
    TaskSubmissionFile,
)
from clases.utils import normalize_extensions, save_image_as_webp

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
            try:
                saved_path = save_image_as_webp(
                    imagen,
                    relative_directory=f"clases/clase_{clase.id}",
                    filename_prefix='portada'
                )
            except ValueError as exc:
                clase.delete()
                raise serializers.ValidationError({'imagen': str(exc)})
            clase.imagen = saved_path
            clase.save(update_fields=['imagen'])

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


class TaskSubmissionFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = TaskSubmissionFile
        fields = ['id', 'file_url', 'original_name', 'extension', 'size_bytes', 'uploaded_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url


class TaskSubmissionSerializer(serializers.ModelSerializer):
    files = TaskSubmissionFileSerializer(many=True, read_only=True)
    student_info = serializers.SerializerMethodField()

    class Meta:
        model = TaskSubmission
        fields = [
            'id',
            'student_info',
            'grade',
            'feedback',
            'delivered_at',
            'created_at',
            'updated_at',
            'files',
        ]

    def get_student_info(self, obj):
        student = obj.student
        return {
            'id': student.id,
            'username': student.username,
            'first_name': student.first_name or '',
            'last_name': student.last_name or '',
            'email': student.email,
        }


class TaskSerializer(serializers.ModelSerializer):
    creator_info = serializers.SerializerMethodField()
    is_teacher = serializers.SerializerMethodField()
    #clase_id = serializers.CharField(write_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'clase_id',
            'due_at',
            'allow_any_file_type',
            'allowed_extensions',
            'max_files',
            'max_file_size_mb',
            'photos',
            'urls',
            'creator_info',
            'is_teacher',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'creator_info', 'is_teacher']

    def validate_allowed_extensions(self, value):
        return normalize_extensions(value)

    def validate(self, attrs):
        allow_any = attrs.get('allow_any_file_type', True)
        allowed_extensions = attrs.get('allowed_extensions', [])
        if not allow_any and not allowed_extensions:
            raise serializers.ValidationError(
                {'allowed_extensions': 'Debes indicar al menos una extensión permitida.'}
            )
        return attrs

    def create(self, validated_data):
        #clase_id = validated_data.pop('clase_id')
        clase = self.context['clase']
        #clase = Clase.objects.get(id=clase_id)
        user = self.context['user']
        return Task.objects.create(
            clase=clase,
            created_by=user,
            **validated_data
        )

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
