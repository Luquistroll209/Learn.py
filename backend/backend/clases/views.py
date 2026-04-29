from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import uuid
import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Q, Count, Max
from django.db.models.functions import Coalesce
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
    AnnouncementComment,
    Task,
    TaskSubmission,
    TaskSubmissionFile,
)
from .serializers import (
    ClaseSerializer,
    AnnouncementSerializer,
    AnnouncementCommentSerializer,
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


def quantize_grade(value):
    if value is None:
        return None
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def grade_average_to_response(total, count):
    if not count:
        return None
    return grade_to_response_value(quantize_grade(total / Decimal(count)))


def parse_grade_input(raw_grade):
    if raw_grade in (None, ''):
        return None
    try:
        grade = Decimal(str(raw_grade))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError('grade debe ser numérico')

    if grade < 0 or grade > 10:
        raise ValueError('grade debe estar entre 0 y 10')

    return quantize_grade(grade)


def build_class_dashboard_payload(clase):
    memberships = list(
        ClaseMembership.objects
        .filter(clase=clase)
        .select_related('user')
        .order_by('joined_at')
    )
    students = [m for m in memberships if m.role == 'student']
    teachers = [m for m in memberships if m.role in ('teacher', 'assistant')]

    tasks = list(
        Task.objects
        .filter(clase=clase)
        .order_by('-created_at')
        .prefetch_related('submissions')
    )

    total_students = len(students)
    total_tasks = len(tasks)

    submissions = list(
        TaskSubmission.objects
        .filter(task__in=tasks)
        .select_related('task', 'student')
    )
    submissions_by_task = {}
    submissions_by_student = {}
    for submission in submissions:
        submissions_by_task.setdefault(submission.task_id, []).append(submission)
        submissions_by_student.setdefault(submission.student_id, []).append(submission)

    now = timezone.now()
    task_rows = []
    delivered_submissions = 0
    graded_submissions = 0
    pending_grading_submissions = 0
    overdue_tasks = 0
    active_tasks = 0
    next_due_at = None
    class_grade_total = Decimal('0')
    class_grade_count = 0

    for task in tasks:
        task_submissions = submissions_by_task.get(task.id, [])
        delivered_count = len(task_submissions)
        graded_count = sum(1 for sub in task_submissions if sub.grade is not None)
        to_grade_count = delivered_count - graded_count
        pending_count = max(total_students - delivered_count, 0)

        task_grade_total = Decimal('0')
        task_grade_count = 0
        for sub in task_submissions:
            if sub.grade is not None:
                task_grade_total += Decimal(sub.grade)
                task_grade_count += 1
                class_grade_total += Decimal(sub.grade)
                class_grade_count += 1

        delivered_submissions += delivered_count
        graded_submissions += graded_count
        pending_grading_submissions += to_grade_count

        is_overdue = bool(task.due_at and task.due_at < now)
        if is_overdue:
            overdue_tasks += 1
        else:
            active_tasks += 1

        if task.due_at and task.due_at >= now:
            if not next_due_at or task.due_at < next_due_at:
                next_due_at = task.due_at

        task_rows.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'due_at': task.due_at,
            'status': 'cerrada' if is_overdue else 'activa',
            'delivered_count': delivered_count,
            'pending_count': pending_count,
            'graded_count': graded_count,
            'to_grade_count': to_grade_count,
            'total_students': total_students,
            'average_grade': grade_average_to_response(task_grade_total, task_grade_count),
            'created_at': task.created_at,
        })

    student_rows = []
    for membership in students:
        user = membership.user
        student_submissions = submissions_by_student.get(user.id, [])
        delivered_tasks = len(student_submissions)
        graded_tasks = sum(1 for sub in student_submissions if sub.grade is not None)
        pending_tasks = max(total_tasks - delivered_tasks, 0)
        pending_grading_tasks = max(delivered_tasks - graded_tasks, 0)

        student_total = Decimal('0')
        student_count = 0
        for sub in student_submissions:
            if sub.grade is not None:
                student_total += Decimal(sub.grade)
                student_count += 1

        if total_tasks == 0:
            status = 'sin_tareas'
        elif delivered_tasks == 0:
            status = 'sin_entregas'
        elif pending_tasks == 0 and pending_grading_tasks == 0:
            status = 'al_dia'
        elif pending_grading_tasks > 0 and pending_tasks == 0:
            status = 'por_calificar'
        else:
            status = 'pendiente'

        average_grade = grade_average_to_response(student_total, student_count)
        average_percentage = None
        if average_grade is not None:
            average_percentage = str(int(round((Decimal(average_grade) / Decimal('10')) * 100)))

        student_rows.append({
            **get_user_info(user, role=membership.role),
            'joined_at': membership.joined_at,
            'delivered_tasks': delivered_tasks,
            'graded_tasks': graded_tasks,
            'pending_tasks': pending_tasks,
            'pending_grading_tasks': pending_grading_tasks,
            'average_grade': average_grade,
            'average_percentage': average_percentage,
            'status': status,
        })

    expected_submissions = total_tasks * total_students
    pending_submissions = max(expected_submissions - delivered_submissions, 0)
    delivery_rate = 0
    if expected_submissions > 0:
        delivery_rate = int(round((delivered_submissions / expected_submissions) * 100))

    return {
        'teachers': [get_user_info(item.user, role=item.role) for item in teachers],
        'students': student_rows,
        'tasks': task_rows,
        'stats': {
            'total_students': total_students,
            'total_tasks': total_tasks,
            'delivered_submissions': delivered_submissions,
            'pending_submissions': pending_submissions,
            'graded_submissions': graded_submissions,
            'pending_grading_submissions': pending_grading_submissions,
            'expected_submissions': expected_submissions,
            'delivery_rate': delivery_rate,
            'active_tasks': active_tasks,
            'overdue_tasks': overdue_tasks,
            'next_due_at': next_due_at,
            'class_average_grade': grade_average_to_response(class_grade_total, class_grade_count),
        }
    }


def can_manage_announcement(user, announcement, membership=None):
    if announcement.created_by_id == user.id:
        return True
    return is_teacher_in_class(user, announcement.clase, membership=membership)


def can_manage_task(user, task, membership=None):
    if task.created_by_id == user.id:
        return True
    return is_teacher_in_class(user, task.clase, membership=membership)


def can_manage_announcement_comment(user, comment, membership=None):
    if comment.author_id == user.id:
        return True
    return is_teacher_in_class(user, comment.announcement.clase, membership=membership)


def delete_task_submission_files(task):
    submission_files = TaskSubmissionFile.objects.filter(
        submission__task=task
    ).select_related('submission')
    for submission_file in submission_files:
        if submission_file.file:
            submission_file.file.delete(save=False)


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


class ObtainClassDashboardView(APIView):
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

        membership = get_membership(user, clase)
        if not is_teacher_in_class(user, clase, membership=membership):
            return Response(
                {'Error': 'Solo el profesor puede ver el dashboard de esta clase'},
                status=status.HTTP_403_FORBIDDEN
            )

        clase_data = ClaseSerializer(clase, context={'request': request}).data
        dashboard = build_class_dashboard_payload(clase)
        return Response(
            {
                'is_teacher': True,
                'clase': clase_data,
                **dashboard,
            },
            status=status.HTTP_200_OK
        )


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


class UpdateClassSettingsView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def patch(self, request, clase_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            clase = Clase.objects.get(id=clase_id)
        except Clase.DoesNotExist:
            return Response({'Error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        membership = get_membership(user, clase)
        if not is_teacher_in_class(user, clase, membership=membership):
            return Response(
                {'Error': 'Solo el profesor puede modificar esta clase'},
                status=status.HTTP_403_FORBIDDEN
            )

        if 'name' in request.data:
            new_name = str(request.data.get('name', '')).strip()
            if not new_name:
                return Response({'Error': 'name no puede estar vacío'}, status=status.HTTP_400_BAD_REQUEST)
            clase.name = new_name

        if 'description' in request.data:
            clase.description = str(request.data.get('description', '')).strip()

        remove_banner = parse_bool(request.data.get('remove_banner'), default=False)
        if remove_banner and clase.imagen:
            clase.imagen.delete(save=False)
            clase.imagen = None

        new_image = request.FILES.get('imagen')
        if new_image:
            try:
                saved_path = save_image_as_webp(
                    new_image,
                    relative_directory=f"clases/clase_{clase.id}",
                    filename_prefix='portada'
                )
            except ValueError as exc:
                return Response({'Error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            clase.imagen = saved_path

        clase.save()
        serializer = ClaseSerializer(clase, context={'request': request})
        return Response(
            {
                'message': 'Clase actualizada correctamente',
                'clase': serializer.data
            },
            status=status.HTTP_200_OK
        )


class RemoveClassMemberView(APIView):
    def delete(self, request, clase_id, user_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            clase = Clase.objects.get(id=clase_id)
        except Clase.DoesNotExist:
            return Response({'Error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        membership = get_membership(user, clase)
        if not is_teacher_in_class(user, clase, membership=membership):
            return Response(
                {'Error': 'Solo el profesor puede expulsar alumnos'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            member = ClaseMembership.objects.select_related('user').get(clase=clase, user_id=user_id)
        except ClaseMembership.DoesNotExist:
            return Response({'Error': 'Miembro no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if member.role == 'teacher' or member.user_id == clase.teacher_id:
            return Response({'Error': 'No puedes expulsar al profesor'}, status=status.HTTP_400_BAD_REQUEST)

        clase.students.remove(member.user)
        member.delete()
        return Response(
            {'message': 'Miembro expulsado correctamente', 'user_id': user_id},
            status=status.HTTP_200_OK
        )


class LeaveClassView(APIView):
    def post(self, request, clase_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            clase = Clase.objects.get(id=clase_id)
        except Clase.DoesNotExist:
            return Response({'Error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        membership = get_membership(user, clase)
        if not membership:
            return Response({'Error': 'No perteneces a esta clase'}, status=status.HTTP_404_NOT_FOUND)
        if membership.role == 'teacher' or clase.teacher_id == user.id:
            return Response(
                {'Error': 'El profesor no puede abandonar la clase sin transferirla primero'},
                status=status.HTTP_400_BAD_REQUEST
            )

        clase.students.remove(user)
        membership.delete()
        return Response(
            {'message': 'Has abandonado la clase correctamente', 'clase_id': clase_id},
            status=status.HTTP_200_OK
        )


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
            response_serializer = AnnouncementSerializer(
                announcement,
                context={'request': request, 'user': user}
            )
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

        sort_mode = str(request.query_params.get('sort', 'activity')).strip().lower()

        announcements = (
            Announcement.objects
            .filter(clase=clase)
            .annotate(
                comments_count_annotated=Count('comments', distinct=True),
                last_comment_at=Max('comments__created_at')
            )
            .annotate(last_activity_at_annotated=Coalesce('last_comment_at', 'updated_at'))
        )

        if sort_mode == 'new':
            announcements = announcements.order_by('-created_at')
        elif sort_mode == 'top':
            announcements = announcements.order_by('-comments_count_annotated', '-last_activity_at_annotated')
        else:
            announcements = announcements.order_by('-last_activity_at_annotated', '-created_at')

        serializer = AnnouncementSerializer(
            announcements,
            many=True,
            context={'request': request, 'user': user}
        )
        return Response(
            {'announcements': serializer.data, 'sort': sort_mode},
            status=status.HTTP_200_OK
        )


class ObtainAnnouncementDetailView(APIView):
    def get(self, request, announcement_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            announcement = (
                Announcement.objects
                .select_related('clase', 'created_by')
                .get(id=announcement_id)
            )
        except Announcement.DoesNotExist:
            return Response({'Error': 'Anuncio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if not is_user_in_class(user, announcement.clase):
            return Response({'Error': 'No perteneces a esta clase'}, status=status.HTTP_403_FORBIDDEN)

        comments = (
            AnnouncementComment.objects
            .filter(announcement=announcement)
            .select_related('author')
            .annotate(replies_count_annotated=Count('replies', distinct=True))
            .order_by('created_at')
        )

        announcement_data = AnnouncementSerializer(
            announcement,
            context={'request': request, 'user': user}
        ).data
        comments_data = AnnouncementCommentSerializer(
            comments,
            many=True,
            context={'request': request, 'user': user}
        ).data

        return Response(
            {
                'announcement': announcement_data,
                'comments': comments_data,
                'is_teacher': is_teacher_in_class(user, announcement.clase),
            },
            status=status.HTTP_200_OK
        )


class ManageAnnouncementView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def patch(self, request, announcement_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            announcement = (
                Announcement.objects
                .select_related('clase', 'created_by')
                .get(id=announcement_id)
            )
        except Announcement.DoesNotExist:
            return Response({'Error': 'Anuncio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        membership = get_membership(user, announcement.clase)
        if not can_manage_announcement(user, announcement, membership=membership):
            return Response(
                {'Error': 'No tienes permisos para editar este anuncio'},
                status=status.HTTP_403_FORBIDDEN
            )

        raw_data = request.data.copy()
        data = {}

        if 'title' in raw_data:
            title = str(raw_data.get('title', '')).strip()
            if not title:
                return Response({'Error': 'title no puede estar vacío'}, status=status.HTTP_400_BAD_REQUEST)
            data['title'] = title

        if 'description' in raw_data:
            description = str(raw_data.get('description', '')).strip()
            if not description:
                return Response({'Error': 'description no puede estar vacío'}, status=status.HTTP_400_BAD_REQUEST)
            data['description'] = description

        if 'urls' in raw_data:
            data['urls'] = [item for item in parse_list(raw_data.get('urls')) if isinstance(item, str)]

        if 'photos' in raw_data:
            existing_photos = [item for item in parse_list(raw_data.get('photos')) if isinstance(item, str)]
        else:
            existing_photos = list(announcement.photos or [])

        uploaded_files = []
        uploaded_files.extend(request.FILES.getlist('photos'))
        uploaded_files.extend(request.FILES.getlist('photos[]'))
        photos_urls = []
        for image in uploaded_files:
            try:
                saved_path = save_image_as_webp(
                    image,
                    relative_directory=f"announcements/clase_{announcement.clase_id}",
                    filename_prefix=f"photo_{uuid.uuid4().hex}"
                )
            except ValueError as exc:
                return Response({'Error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            photos_urls.append(request.build_absolute_uri(default_storage.url(saved_path)))

        if uploaded_files or 'photos' in raw_data:
            data['photos'] = existing_photos + photos_urls

        serializer = AnnouncementSerializer(
            announcement,
            data=data,
            partial=True,
            context={'request': request, 'user': user}
        )
        if not serializer.is_valid():
            return Response(
                {'Error': 'Datos inválidos', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated = serializer.save()
        response_serializer = AnnouncementSerializer(
            updated,
            context={'request': request, 'user': user}
        )
        return Response(
            {'message': 'Anuncio actualizado', 'announcement': response_serializer.data},
            status=status.HTTP_200_OK
        )

    def delete(self, request, announcement_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            announcement = Announcement.objects.select_related('clase', 'created_by').get(id=announcement_id)
        except Announcement.DoesNotExist:
            return Response({'Error': 'Anuncio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        membership = get_membership(user, announcement.clase)
        if not can_manage_announcement(user, announcement, membership=membership):
            return Response(
                {'Error': 'No tienes permisos para eliminar este anuncio'},
                status=status.HTTP_403_FORBIDDEN
            )

        announcement.delete()
        return Response(
            {'message': 'Anuncio eliminado correctamente', 'announcement_id': announcement_id},
            status=status.HTTP_200_OK
        )


class CreateAnnouncementCommentView(APIView):
    def post(self, request, announcement_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            announcement = Announcement.objects.select_related('clase').get(id=announcement_id)
        except Announcement.DoesNotExist:
            return Response({'Error': 'Anuncio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if not is_user_in_class(user, announcement.clase):
            return Response({'Error': 'No perteneces a esta clase'}, status=status.HTTP_403_FORBIDDEN)

        content = str(request.data.get('content', '')).strip()
        if not content:
            return Response({'Error': 'content es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        parent_comment = None
        parent_id = request.data.get('parent_id')
        if parent_id not in (None, ''):
            try:
                parent_comment = AnnouncementComment.objects.get(
                    id=parent_id,
                    announcement=announcement
                )
            except AnnouncementComment.DoesNotExist:
                return Response(
                    {'Error': 'Comentario padre no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )

        comment = AnnouncementComment.objects.create(
            announcement=announcement,
            author=user,
            parent=parent_comment,
            content=content
        )
        serializer = AnnouncementCommentSerializer(comment, context={'request': request, 'user': user})
        return Response(
            {'message': 'Comentario publicado', 'comment': serializer.data},
            status=status.HTTP_201_CREATED
        )


class ManageAnnouncementCommentView(APIView):
    def patch(self, request, comment_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            comment = (
                AnnouncementComment.objects
                .select_related('announcement__clase', 'author')
                .get(id=comment_id)
            )
        except AnnouncementComment.DoesNotExist:
            return Response({'Error': 'Comentario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        membership = get_membership(user, comment.announcement.clase)
        if not can_manage_announcement_comment(user, comment, membership=membership):
            return Response(
                {'Error': 'No tienes permisos para editar este comentario'},
                status=status.HTTP_403_FORBIDDEN
            )

        content = str(request.data.get('content', '')).strip()
        if not content:
            return Response({'Error': 'content es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        comment.content = content
        comment.save(update_fields=['content', 'updated_at'])
        serializer = AnnouncementCommentSerializer(comment, context={'request': request, 'user': user})
        return Response(
            {'message': 'Comentario actualizado', 'comment': serializer.data},
            status=status.HTTP_200_OK
        )

    def delete(self, request, comment_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            comment = (
                AnnouncementComment.objects
                .select_related('announcement__clase')
                .get(id=comment_id)
            )
        except AnnouncementComment.DoesNotExist:
            return Response({'Error': 'Comentario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        membership = get_membership(user, comment.announcement.clase)
        if not can_manage_announcement_comment(user, comment, membership=membership):
            return Response(
                {'Error': 'No tienes permisos para eliminar este comentario'},
                status=status.HTTP_403_FORBIDDEN
            )

        comment.delete()
        return Response(
            {'message': 'Comentario eliminado', 'comment_id': comment_id},
            status=status.HTTP_200_OK
        )


class CreateTaskView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request, clase_id=None):
        #return Response({'Error', clase_id}, status=status.HTTP_200_OK)
        user = get_authenticated_user(request)
        if not request.META.get('HTTP_AUTHORIZATION', ''):
            return Response({'Error': 'Token no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        raw_data = request.data.copy()
        """
        clase_id = raw_data.get('clase_id')
        
        if not clase_id:
            return Response({'Error': 'clase_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        """
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

        serializer = TaskSerializer(
               data=data,
               context={'user': user, 'request': request, 'clase': clase}
        )           
        if not serializer.is_valid():
            return Response(
                {'Error': 'Datos inválidos', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        task = serializer.save()
        response_data = TaskSerializer(task, context={'request': request}).data
        response_data.update(build_teacher_task_participants(task, request=request))

        return Response(
            {'message': 'Tarea creada exitosamente', 'clase':clase_id, 'task': response_data},
            status=status.HTTP_201_CREATED
        )


class ManageTaskView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def patch(self, request, task_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            task = Task.objects.select_related('clase', 'created_by').get(id=task_id)
        except Task.DoesNotExist:
            return Response({'Error': 'Tarea no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        membership = get_membership(user, task.clase)
        if not can_manage_task(user, task, membership=membership):
            return Response(
                {'Error': 'No tienes permisos para editar esta tarea'},
                status=status.HTTP_403_FORBIDDEN
            )

        raw_data = request.data.copy()
        data = {}

        if 'title' in raw_data:
            title = str(raw_data.get('title', '')).strip()
            if not title:
                return Response({'Error': 'title no puede estar vacío'}, status=status.HTTP_400_BAD_REQUEST)
            data['title'] = title

        if 'description' in raw_data:
            description = str(raw_data.get('description', '')).strip()
            if not description:
                return Response({'Error': 'description no puede estar vacío'}, status=status.HTTP_400_BAD_REQUEST)
            data['description'] = description

        if 'due_at' in raw_data:
            due_at = raw_data.get('due_at')
            data['due_at'] = due_at or None

        allow_any_file_type = task.allow_any_file_type
        if 'allow_any_file_type' in raw_data:
            allow_any_file_type = parse_bool(raw_data.get('allow_any_file_type'), default=task.allow_any_file_type)

        allowed_extensions = normalize_extensions(task.allowed_extensions)
        if 'allowed_extensions' in raw_data:
            allowed_extensions = normalize_extensions(raw_data.get('allowed_extensions'))

        if not allow_any_file_type and not allowed_extensions:
            return Response(
                {'Error': 'Debes indicar al menos una extensión permitida'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data['allow_any_file_type'] = allow_any_file_type
        data['allowed_extensions'] = allowed_extensions

        try:
            if 'max_files' in raw_data:
                data['max_files'] = parse_positive_int(
                    raw_data.get('max_files'),
                    'max_files',
                    default_value=task.max_files,
                    min_value=1,
                    max_value=50
                )
            if 'max_file_size_mb' in raw_data:
                data['max_file_size_mb'] = parse_positive_int(
                    raw_data.get('max_file_size_mb'),
                    'max_file_size_mb',
                    default_value=task.max_file_size_mb,
                    min_value=1,
                    max_value=1024
                )
        except ValueError as exc:
            return Response({'Error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if 'urls' in raw_data:
            data['urls'] = [item for item in parse_list(raw_data.get('urls')) if isinstance(item, str)]

        if 'photos' in raw_data:
            existing_photos = [item for item in parse_list(raw_data.get('photos')) if isinstance(item, str)]
        else:
            existing_photos = list(task.photos or [])

        uploaded_files = []
        uploaded_files.extend(request.FILES.getlist('photos'))
        uploaded_files.extend(request.FILES.getlist('photos[]'))
        photos_urls = []

        for image in uploaded_files:
            try:
                saved_path = save_image_as_webp(
                    image,
                    relative_directory=f"clases/clase_{task.clase_id}/task_assets",
                    filename_prefix=f"photo_{uuid.uuid4().hex}"
                )
            except ValueError as exc:
                return Response({'Error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            photos_urls.append(request.build_absolute_uri(default_storage.url(saved_path)))

        if uploaded_files or 'photos' in raw_data:
            data['photos'] = existing_photos + photos_urls

        serializer = TaskSerializer(task, data=data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response(
                {'Error': 'Datos inválidos', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_task = serializer.save()
        response_data = TaskSerializer(updated_task, context={'request': request}).data
        response_data.update(build_teacher_task_participants(updated_task, request=request))
        return Response(
            {'message': 'Tarea actualizada', 'task': response_data},
            status=status.HTTP_200_OK
        )

    def delete(self, request, task_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            task = Task.objects.select_related('clase', 'created_by').get(id=task_id)
        except Task.DoesNotExist:
            return Response({'Error': 'Tarea no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        membership = get_membership(user, task.clase)
        if not can_manage_task(user, task, membership=membership):
            return Response(
                {'Error': 'No tienes permisos para eliminar esta tarea'},
                status=status.HTTP_403_FORBIDDEN
            )

        delete_task_submission_files(task)
        task.delete()
        return Response(
            {'message': 'Tarea eliminada', 'task_id': task_id},
            status=status.HTTP_200_OK
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

        clear_grade = parse_bool(request.data.get('clear_grade'), default=False)
        raw_grade = request.data.get('grade')
        feedback_input = request.data.get('feedback', None)

        if clear_grade:
            next_grade = None
        else:
            if raw_grade in (None, ''):
                if feedback_input is None:
                    return Response(
                        {'Error': 'grade es requerido si no envías feedback o clear_grade'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                next_grade = submission.grade
            else:
                try:
                    next_grade = parse_grade_input(raw_grade)
                except ValueError as exc:
                    return Response({'Error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        update_fields = []
        if submission.grade != next_grade:
            submission.grade = next_grade
            update_fields.append('grade')

        if feedback_input is not None:
            feedback_text = str(feedback_input).strip()
            if submission.feedback != feedback_text:
                submission.feedback = feedback_text
                update_fields.append('feedback')

        if update_fields:
            update_fields.append('updated_at')
            submission.save(update_fields=update_fields)

        serializer = TaskSubmissionSerializer(submission, context={'request': request})
        dashboard = build_class_dashboard_payload(task.clase)
        student_summary = next(
            (item for item in dashboard['students'] if item['id'] == student_membership.user_id),
            None
        )
        task_summary = next(
            (item for item in dashboard['tasks'] if item['id'] == task.id),
            None
        )
        return Response(
            {
                'message': 'Calificación guardada',
                'submission': serializer.data,
                'student_summary': student_summary,
                'task_summary': task_summary,
            },
            status=status.HTTP_200_OK
        )
