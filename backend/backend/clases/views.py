from decimal import Decimal, InvalidOperation
import uuid
import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, serializers as drf_serializers
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.views import enviarMensaje
from users.models import User
from users.serializers import TokenUserInfoSerializer
from users.views import get_user_from_token

from .models import (
    Clase,
    ClaseMembership,
    Announcement,
    Task,
    TaskSubmission,
    TaskSubmissionFile,
)
from .serializers import (
    ClaseSerializer,
    AnnouncementSerializer,
    TaskSerializer,
    TaskSubmissionSerializer,
)
from .utils import (
    HARD_MAX_UPLOAD_BYTES,
    normalize_extensions,
    parse_bool,
    parse_list,
    save_image_as_webp,
)


def get_authenticated_user(request):
    token_key = request.META.get('HTTP_AUTHORIZATION', '')
    if not token_key:
        return None
    return get_user_from_token(token_key)


def get_membership(user, clase):
    return ClaseMembership.objects.filter(user=user, clase=clase).select_related('user').first()


def is_teacher_in_class(user, clase, membership=None):
    if clase.teacher_id == user.id:
        return True
    membership = membership or get_membership(user, clase)
    return bool(membership and membership.role == 'teacher')


def is_user_in_class(user, clase):
    if clase.teacher_id == user.id:
        return True
    return ClaseMembership.objects.filter(user=user, clase=clase).exists()


def parse_positive_int(raw_value, field_name, default_value, min_value, max_value):
    if raw_value in (None, ''):
        return default_value
    try:
        parsed_value = int(raw_value)
    except (TypeError, ValueError):
        raise ValueError(f'{field_name} debe ser un número entero.')

    if parsed_value < min_value or parsed_value > max_value:
        raise ValueError(
            f'{field_name} debe estar entre {min_value} y {max_value}.'
        )
    return parsed_value


def flatten_request_data(raw_data):
    if hasattr(raw_data, 'dict'):
        return raw_data.dict()
    return dict(raw_data)


def get_user_info(user, role=None):
    data = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name or '',
        'last_name': user.last_name or '',
        'email': user.email,
    }
    if role is not None:
        data['role'] = role
    return data


def grade_to_response_value(value):
    if value is None:
        return None
    return str(value)


def get_task_submissions_by_student(task):
    submissions = (
        task.submissions
        .select_related('student')
        .prefetch_related('files')
    )
    return {submission.student_id: submission for submission in submissions}


def build_teacher_task_participants(task, request=None):
    memberships = (
        ClaseMembership.objects
        .filter(clase=task.clase)
        .select_related('user')
        .order_by('joined_at')
    )
    submissions_map = get_task_submissions_by_student(task)

    class_members = []
    delivered_students = []
    pending_students = []
    grades = []

    for membership in memberships:
        user_info = get_user_info(membership.user, membership.role)
        class_members.append(user_info)

        if membership.role == 'teacher':
            continue

        submission = submissions_map.get(membership.user_id)
        if submission:
            submission_files = []
            for submission_file in submission.files.all():
                file_url = submission_file.file.url
                if request:
                    file_url = request.build_absolute_uri(file_url)
                submission_files.append({
                    'id': submission_file.id,
                    'file_url': file_url,
                    'original_name': submission_file.original_name,
                    'extension': submission_file.extension,
                    'size_bytes': submission_file.size_bytes,
                    'uploaded_at': submission_file.uploaded_at,
                })

            item = {
                **user_info,
                'submission_id': submission.id,
                'delivered_at': submission.delivered_at,
                'grade': grade_to_response_value(submission.grade),
                'feedback': submission.feedback,
                'files_count': len(submission_files),
                'files': submission_files,
            }
            delivered_students.append(item)
            grades.append({
                'student_id': membership.user_id,
                'grade': grade_to_response_value(submission.grade),
            })
        else:
            pending_students.append(user_info)
            grades.append({
                'student_id': membership.user_id,
                'grade': None,
            })

    return {
        'class_members': class_members,
        'delivered_students': delivered_students,
        'pending_students': pending_students,
        'grades': grades,
        'delivered_count': len(delivered_students),
        'pending_count': len(pending_students),
        'total_students': len(delivered_students) + len(pending_students),
    }


def get_pending_tasks_queryset(clase):
    now = timezone.now()
    return (
        Task.objects
        .filter(clase=clase)
        .filter(Q(due_at__isnull=True) | Q(due_at__gte=now))
        .order_by('due_at', '-created_at')
    )


class CreateClassView(APIView):
    def post(self, request):
        user = get_authenticated_user(request)

        if not request.META.get('HTTP_AUTHORIZATION', ''):
            return Response({'Error': 'Token no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()
        if 'id' in data:
            if hasattr(data, '_mutable'):
                data._mutable = True
                del data['id']
                data._mutable = False
            else:
                del data['id']

        serializer = ClaseSerializer(
            data=data,
            context={'request': request, 'teacher': user}
        )

        if serializer.is_valid():
            try:
                clase = serializer.save()
            except drf_serializers.ValidationError as exc:
                return Response(
                    {'Error': 'Datos inválidos', 'details': exc.detail},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ClaseMembership.objects.create(user=user, clase=clase, role='teacher')
            clase.students.add(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {'Error': 'Datos inválidos', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class obtainClass(APIView):
    def get(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = TokenUserInfoSerializer(user)
        clases_data = serializer.data['clases']
        return Response({'clases': clases_data}, status=status.HTTP_200_OK)


class obtainClassByID(APIView):
    def get(self, request, identifier=None):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Token incorrecto'}, status=status.HTTP_401_UNAUTHORIZED)

        if not identifier:
            return Response({'Error': 'Se requiere una ID de una clase'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TokenUserInfoSerializer(user)
        clases_data = serializer.data['clases']
        clase = next((c for c in clases_data if c['id'] == identifier), None)

        if not clase:
            return Response({'Error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(clase, status=status.HTTP_200_OK)


class inviteUser(APIView):
    def post(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        clase_id = request.data.get('clase_id')
        email = request.data.get('email')
        if not clase_id:
            return Response({'Error': 'clase_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({'Error': 'email es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            clase = Clase.objects.get(id=clase_id)
            if clase.teacher != user:
                return Response({'Error': 'Solo el profesor puede invitar usuarios'}, status=status.HTTP_403_FORBIDDEN)

            user_to_invite = User.objects.get(email=email)
            if clase.students.filter(id=user_to_invite.id).exists():
                return Response({'Error': 'El usuario ya está en esta clase'}, status=status.HTTP_400_BAD_REQUEST)

            join_url = settings.IP + f"/api/class/join/{clase.id}/"
            mensaje_invitacion = f"""
            ¡Has sido invitado a unirte a la clase "{clase.name}"!

            ID de la clase: {clase.id}

            Profesor: {user.get_full_name() or user.email}

            Para unirte a la clase, haz clic en el siguiente enlace:
            {join_url}

            Descripción: {clase.description}
            """

            asunto = f"Invitación a la clase: {clase.name}"
            notificacion_data = enviarMensaje(
                asunto=asunto,
                mensaje=mensaje_invitacion,
                destinario=user_to_invite,
                email=email,
                user=user
            )

            return Response(
                {
                    'message': f'Invitación enviada a {email}',
                    'notificacion': notificacion_data,
                    'class_id': clase.id
                },
                status=status.HTTP_200_OK
            )
        except Clase.DoesNotExist:
            return Response({'Error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


class JoinClassAutoView(APIView):
    def get(self, request, clase_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            clase = Clase.objects.get(id=clase_id)
            if clase.students.filter(id=user.id).exists():
                membership = get_membership(user, clase)
                serializer = ClaseSerializer(clase, context={'request': request})
                student_info = next(
                    (s for s in serializer.data['students_info'] if s['user_id'] == user.id),
                    None
                )
                return Response(
                    {
                        'message': 'Ya estás en esta clase',
                        'unionDate': student_info['joined_at'] if student_info else None,
                        'role': membership.role if membership else 'student',
                        'teacherName': serializer.data['teacher_name'],
                        'className': serializer.data['name'],
                    },
                    status=status.HTTP_200_OK
                )

            ClaseMembership.objects.create(user=user, clase=clase, role='student')
            clase.students.add(user)

            serializer = ClaseSerializer(clase, context={'request': request})
            return Response(
                {'message': 'Te has unido a la clase exitosamente', 'clase': serializer.data},
                status=status.HTTP_200_OK
            )
        except Clase.DoesNotExist:
            return Response({'Error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)


class CreateAnnouncementView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request):
        user = get_authenticated_user(request)
        if not request.META.get('HTTP_AUTHORIZATION', ''):
            return Response({'Error': 'Token no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        raw_data = request.data.copy()
        clase_id = raw_data.get('clase_id')
        if not clase_id:
            return Response({'Error': 'clase_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        if not raw_data.get('title'):
            return Response({'Error': 'title es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        if not raw_data.get('description'):
            return Response({'Error': 'description es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            clase = Clase.objects.get(id=clase_id)
        except Clase.DoesNotExist:
            return Response({'Error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        if not is_user_in_class(user, clase):
            return Response({'Error': 'No perteneces a esta clase'}, status=status.HTTP_403_FORBIDDEN)

        urls_list = [item for item in parse_list(raw_data.get('urls')) if isinstance(item, str)]
        existing_photos = [item for item in parse_list(raw_data.get('photos')) if isinstance(item, str)]

        uploaded_files = []
        uploaded_files.extend(request.FILES.getlist('photos'))
        uploaded_files.extend(request.FILES.getlist('photos[]'))
        photos_urls = []

        for image in uploaded_files:
            try:
                saved_path = save_image_as_webp(
                    image,
                    relative_directory=f"announcements/clase_{clase_id}",
                    filename_prefix=f"photo_{uuid.uuid4().hex}"
                )
            except ValueError as exc:
                return Response({'Error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            photos_urls.append(request.build_absolute_uri(default_storage.url(saved_path)))

        data = flatten_request_data(raw_data)
        data['photos'] = existing_photos + photos_urls
        data['urls'] = urls_list

        serializer = AnnouncementSerializer(
            data=data,
            context={'user': user, 'request': request}
        )

        if serializer.is_valid():
            announcement = serializer.save()
            response_serializer = AnnouncementSerializer(announcement, context={'request': request})
            return Response(
                {
                    'message': 'Anuncio creado exitosamente',
                    'announcement': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'Error': 'Datos inválidos', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class ObtainAnnouncementsView(APIView):
    def get(self, request, clase_id=None):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)
        if not clase_id:
            return Response({'Error': 'clase_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            clase = Clase.objects.get(id=clase_id)
        except Clase.DoesNotExist:
            return Response({'Error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        if not is_user_in_class(user, clase):
            return Response({'Error': 'No perteneces a esta clase'}, status=status.HTTP_403_FORBIDDEN)

        announcements = Announcement.objects.filter(clase=clase).order_by('-created_at')
        serializer = AnnouncementSerializer(announcements, many=True, context={'request': request})
        return Response({'announcements': serializer.data}, status=status.HTTP_200_OK)


class CreateTaskView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request):
        user = get_authenticated_user(request)
        if not request.META.get('HTTP_AUTHORIZATION', ''):
            return Response({'Error': 'Token no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        raw_data = request.data.copy()
        clase_id = raw_data.get('clase_id')
        if not clase_id:
            return Response({'Error': 'clase_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        if not raw_data.get('title'):
            return Response({'Error': 'title es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        if not raw_data.get('description'):
            return Response({'Error': 'description es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            clase = Clase.objects.get(id=clase_id)
        except Clase.DoesNotExist:
            return Response({'Error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        membership = get_membership(user, clase)
        if not is_teacher_in_class(user, clase, membership=membership):
            return Response(
                {'Error': 'Solo el profesor puede crear tareas en esta clase'},
                status=status.HTTP_403_FORBIDDEN
            )

        allow_any_file_type = parse_bool(raw_data.get('allow_any_file_type'), default=True)
        allowed_extensions = normalize_extensions(raw_data.get('allowed_extensions'))

        try:
            max_files = parse_positive_int(
                raw_data.get('max_files'),
                'max_files',
                default_value=1,
                min_value=1,
                max_value=50
            )
            max_file_size_mb = parse_positive_int(
                raw_data.get('max_file_size_mb'),
                'max_file_size_mb',
                default_value=100,
                min_value=1,
                max_value=1024
            )
        except ValueError as exc:
            return Response({'Error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        urls_list = [item for item in parse_list(raw_data.get('urls')) if isinstance(item, str)]
        existing_photos = [item for item in parse_list(raw_data.get('photos')) if isinstance(item, str)]

        uploaded_files = []
        uploaded_files.extend(request.FILES.getlist('photos'))
        uploaded_files.extend(request.FILES.getlist('photos[]'))
        photos_urls = []

        for image in uploaded_files:
            try:
                saved_path = save_image_as_webp(
                    image,
                    relative_directory=f"clases/clase_{clase_id}/task_assets",
                    filename_prefix=f"photo_{uuid.uuid4().hex}"
                )
            except ValueError as exc:
                return Response({'Error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            photos_urls.append(request.build_absolute_uri(default_storage.url(saved_path)))

        data = flatten_request_data(raw_data)
        data['allow_any_file_type'] = allow_any_file_type
        data['allowed_extensions'] = allowed_extensions
        data['max_files'] = max_files
        data['max_file_size_mb'] = max_file_size_mb
        data['photos'] = existing_photos + photos_urls
        data['urls'] = urls_list

        serializer = TaskSerializer(data=data, context={'user': user, 'request': request})
        if not serializer.is_valid():
            return Response(
                {'Error': 'Datos inválidos', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        task = serializer.save()
        response_data = TaskSerializer(task, context={'request': request}).data
        response_data.update(build_teacher_task_participants(task, request=request))

        return Response(
            {'message': 'Tarea creada exitosamente', 'task': response_data},
            status=status.HTTP_201_CREATED
        )


class SubmitTaskView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request, task_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            task = Task.objects.select_related('clase').get(id=task_id)
        except Task.DoesNotExist:
            return Response({'Error': 'Tarea no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        membership = get_membership(user, task.clase)
        if not is_user_in_class(user, task.clase):
            return Response({'Error': 'No perteneces a esta clase'}, status=status.HTTP_403_FORBIDDEN)
        if is_teacher_in_class(user, task.clase, membership=membership):
            return Response(
                {'Error': 'El profesor no puede entregar esta tarea como alumno'},
                status=status.HTTP_403_FORBIDDEN
            )

        uploaded_files = []
        uploaded_files.extend(request.FILES.getlist('files'))
        uploaded_files.extend(request.FILES.getlist('files[]'))

        if not uploaded_files:
            return Response({'Error': 'Debes adjuntar al menos un archivo'}, status=status.HTTP_400_BAD_REQUEST)
        if len(uploaded_files) > task.max_files:
            return Response(
                {'Error': f'Solo puedes subir hasta {task.max_files} archivo(s)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        allowed_extensions = normalize_extensions(task.allowed_extensions)
        per_file_limit = min(task.max_file_size_mb * 1024 * 1024, HARD_MAX_UPLOAD_BYTES)

        for uploaded_file in uploaded_files:
            extension = os.path.splitext(uploaded_file.name)[1].lower().lstrip('.')
            if not task.allow_any_file_type and extension not in allowed_extensions:
                return Response(
                    {'Error': f'Tipo de archivo no permitido: {extension or "sin extensión"}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if uploaded_file.size > per_file_limit:
                return Response(
                    {'Error': f'Cada archivo debe pesar como máximo {task.max_file_size_mb} MB'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        submission, _ = TaskSubmission.objects.get_or_create(task=task, student=user)
        submission.delivered_at = timezone.now()
        submission.save(update_fields=['delivered_at', 'updated_at'])

        previous_files = list(submission.files.all())
        for previous_file in previous_files:
            if previous_file.file:
                previous_file.file.delete(save=False)
            previous_file.delete()

        for uploaded_file in uploaded_files:
            extension = os.path.splitext(uploaded_file.name)[1].lower().lstrip('.')
            TaskSubmissionFile.objects.create(
                submission=submission,
                file=uploaded_file,
                original_name=uploaded_file.name,
                extension=extension,
                size_bytes=uploaded_file.size,
            )

        serializer = TaskSubmissionSerializer(submission, context={'request': request})
        return Response(
            {
                'message': 'Tarea entregada correctamente',
                'task_id': task.id,
                'is_delivered': True,
                'grade': grade_to_response_value(submission.grade),
                'submission': serializer.data
            },
            status=status.HTTP_200_OK
        )


class ObtainPendingTasksView(APIView):
    def get(self, request, clase_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            clase = Clase.objects.get(id=clase_id)
        except Clase.DoesNotExist:
            return Response({'Error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        membership = get_membership(user, clase)
        if not is_user_in_class(user, clase):
            return Response({'Error': 'No perteneces a esta clase'}, status=status.HTTP_403_FORBIDDEN)

        user_is_teacher = is_teacher_in_class(user, clase, membership=membership)
        tasks = list(
            get_pending_tasks_queryset(clase).prefetch_related('submissions__files', 'submissions__student')
        )

        if user_is_teacher:
            tasks_data = []
            for task in tasks:
                data = TaskSerializer(task, context={'request': request}).data
                data.update(build_teacher_task_participants(task, request=request))
                tasks_data.append(data)

            return Response(
                {
                    'is_teacher': True,
                    'clase_id': clase_id,
                    'tasks': tasks_data
                },
                status=status.HTTP_200_OK
            )

        submissions_map = {
            submission.task_id: submission
            for submission in TaskSubmission.objects.filter(
                task__in=tasks,
                student=user
            ).prefetch_related('files')
        }

        tasks_data = []
        for task in tasks:
            submission = submissions_map.get(task.id)
            tasks_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'due_at': task.due_at,
                'photos': task.photos,
                'urls': task.urls,
                'is_delivered': bool(submission),
                'grade': grade_to_response_value(submission.grade) if submission else None,
                'submission_id': submission.id if submission else None,
                'delivered_at': submission.delivered_at if submission else None,
            })

        return Response(
            {
                'is_teacher': False,
                'clase_id': clase_id,
                'tasks': tasks_data
            },
            status=status.HTTP_200_OK
        )


class ObtainTaskDetailView(APIView):
    def get(self, request, task_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            task = (
                Task.objects
                .select_related('clase')
                .prefetch_related('submissions__files', 'submissions__student')
                .get(id=task_id)
            )
        except Task.DoesNotExist:
            return Response({'Error': 'Tarea no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        membership = get_membership(user, task.clase)
        if not is_user_in_class(user, task.clase):
            return Response({'Error': 'No perteneces a esta clase'}, status=status.HTTP_403_FORBIDDEN)

        user_is_teacher = is_teacher_in_class(user, task.clase, membership=membership)
        base_task = TaskSerializer(task, context={'request': request}).data

        if user_is_teacher:
            base_task.update(build_teacher_task_participants(task, request=request))
            return Response(
                {
                    'is_teacher': True,
                    'task': base_task
                },
                status=status.HTTP_200_OK
            )

        submission = TaskSubmission.objects.filter(task=task, student=user).prefetch_related('files').first()
        submission_data = None
        if submission:
            submission_data = TaskSubmissionSerializer(submission, context={'request': request}).data

        response_data = {
            **base_task,
            'is_delivered': bool(submission),
            'grade': grade_to_response_value(submission.grade) if submission else None,
            'submission': submission_data,
        }
        return Response(
            {
                'is_teacher': False,
                'task': response_data
            },
            status=status.HTTP_200_OK
        )


class GradeTaskSubmissionView(APIView):
    def post(self, request, task_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            task = Task.objects.select_related('clase').get(id=task_id)
        except Task.DoesNotExist:
            return Response({'Error': 'Tarea no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        membership = get_membership(user, task.clase)
        if not is_teacher_in_class(user, task.clase, membership=membership):
            return Response({'Error': 'Solo el profesor puede calificar'}, status=status.HTTP_403_FORBIDDEN)

        student_id = request.data.get('student_id')
        if not student_id:
            return Response({'Error': 'student_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        raw_grade = request.data.get('grade')
        if raw_grade in (None, ''):
            return Response({'Error': 'grade es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            grade = Decimal(str(raw_grade))
        except (InvalidOperation, TypeError, ValueError):
            return Response({'Error': 'grade debe ser numérico'}, status=status.HTTP_400_BAD_REQUEST)

        if grade < 0 or grade > 10:
            return Response({'Error': 'grade debe estar entre 0 y 10'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student_membership = ClaseMembership.objects.select_related('user').get(
                clase=task.clase,
                user_id=student_id
            )
        except ClaseMembership.DoesNotExist:
            return Response({'Error': 'El usuario no pertenece a esta clase'}, status=status.HTTP_404_NOT_FOUND)

        if student_membership.role == 'teacher':
            return Response({'Error': 'No se puede calificar al profesor'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            submission = TaskSubmission.objects.get(task=task, student_id=student_id)
        except TaskSubmission.DoesNotExist:
            return Response({'Error': 'El alumno aún no ha entregado esta tarea'}, status=status.HTTP_404_NOT_FOUND)

        submission.grade = grade
        submission.feedback = request.data.get('feedback', submission.feedback)
        submission.save(update_fields=['grade', 'feedback', 'updated_at'])

        serializer = TaskSubmissionSerializer(submission, context={'request': request})
        return Response(
            {
                'message': 'Calificación guardada',
                'submission': serializer.data
            },
            status=status.HTTP_200_OK
        )
