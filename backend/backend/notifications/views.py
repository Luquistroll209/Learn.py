import smtplib
import socket

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.serializers import TokenUserInfoSerializer

# obtener cosas de la app de usuarios
from users.views import get_user_from_token

from .models import Notification
from .serializers import NotificationSerializer


# Funcion para mandar emails al correo
def enviar_email_super_basico(asunto, mensaje, destinatario, contexto=None):
    try:
        if contexto is None:
            contexto = {}

        # Asegurar que el contexto tenga los campos necesarios
        contexto["subject"] = asunto
        contexto["message"] = mensaje

        # Si no hay nombre en el contexto, intentar obtenerlo del destinatario
        if "nombre" not in contexto and hasattr(destinatario, "first_name"):
            if isinstance(destinatario, str):
                # Si destinatario es un email string
                contexto["nombre"] = ""
            else:
                # Si destinatario es un objeto User
                nombre_completo = (
                    f"{destinatario.first_name} {destinatario.last_name}".strip()
                )
                contexto["nombre"] = (
                    nombre_completo if nombre_completo else destinatario.username
                )

        # Renderizar el HTML
        html_content = render_to_string("email_base.html", contexto)

        # Crear el email
        email = EmailMultiAlternatives(
            subject=f"[Learn.py] {asunto}",
            body=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destinatario.email if hasattr(destinatario, "email") else destinatario],
        )

        email.attach_alternative(html_content, "text/html")

        # Enviar con manejo de timeout
        email.send(fail_silently=False)

        print(f"Email enviado a: {destinatario}")
        return True

    except (smtplib.SMTPException, socket.timeout, ConnectionError) as e:
        print(f"Error enviando email: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False


def enviarMensaje(asunto, mensaje, destinario, email, user, extra_context=None):
    """
    Envía una notificación y email con formato mejorado

    Args:
        asunto: Asunto del mensaje
        mensaje: Mensaje en texto plano
        destinario: Objeto User destinatario
        email: Email del destinatario
        user: Usuario que envía
        extra_context: Diccionario con información adicional (class_id, class_name, invitation_link, etc.)
    """
    # Creación de notificaciones
    notificacion_sent = Notification.objects.create(
        to=user,
        subject=asunto,
        message=mensaje or "",
        created_by=user,
        notification_type="sent",
    )

    notificacion_received = Notification.objects.create(
        to=destinario,
        subject=asunto,
        message=mensaje or "",
        created_by=user,
        notification_type="received",
    )

    # Preparar contexto para el email
    email_context = {
        "subject": asunto,
        "message": mensaje,
        "nombre": f"{destinario.first_name} {destinario.last_name}".strip()
        or destinario.username,
    }

    # Agregar contexto adicional si existe
    if extra_context:
        email_context.update(extra_context)

    # Enviar email con el contexto mejorado
    enviar_email_super_basico(
        asunto=asunto, mensaje=mensaje, destinatario=destinario, contexto=email_context
    )

    serializer = NotificationSerializer(notificacion_sent)
    return serializer.data


# funcion para crear un mensaje
class createNotification(APIView):
    def post(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        token_key = header

        # Mensajes de errores
        if not token_key:
            return Response(
                {"Error": "Token no proporcionado"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = get_user_from_token(token_key)

        if not user:
            return Response(
                {"Error": "Usuario no encontrado"}, status=status.HTTP_401_UNAUTHORIZED
            )

        subject = request.data.get("subject")
        to_email = request.data.get("to")
        message = request.data.get("message")

        # más mensajes de errores
        if not subject:
            return Response(
                {"Error": "El subject de la clase es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not to_email:
            return Response(
                {"Error": "To_email es requerido"}, status=status.HTTP_400_BAD_REQUEST
            )
        if not message:
            return Response(
                {"Error": "Es requerido un mensaje"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener el usuario destinatario por email
        try:
            to_user = User.objects.get(email=to_email)
        except User.DoesNotExist:
            return Response(
                {"Error": "Usuario destinatario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Creacion de notificación
        """
        notificación = Notification.objects.create(
            to=to_user,
            subject=subject,
            message=message or '',
            created_by=user
        )
        #Enviar mensaje al correo
        enviar_email_super_basico(
                asunto="Nuevo correo recivido de Learn.py: " + subject,
                mensaje=message,
                destinatario=to_email
            )
        serializer = NotificationSerializer(notificación)
        """

        return Response(
            enviarMensaje(subject, message, to_user, to_email, user),
            status=status.HTTP_201_CREATED,
        )


# obtener las notificasciones de todas las del usuario o unicamente una notificación
class obtainNotifications(APIView):
    def get(self, request, id=None):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        Token = header
        user = get_user_from_token(Token)

        if not user:
            return Response(
                {"Error": "Usuario no encontrado"}, status=status.HTTP_401_UNAUTHORIZED
            )

        notifications_sent = Notification.objects.filter(
            to=user, notification_type="sent"
        )
        notifications_received = Notification.objects.filter(
            to=user, notification_type="received"
        )

        all_notifications = notifications_sent | notifications_received
        all_notifications = all_notifications.order_by("-created_at")

        serializer = NotificationSerializer(all_notifications, many=True)

        if not id:
            # Obtener todas las notificaciones

            return Response(
                {"notifications": serializer.data}, status=status.HTTP_200_OK
            )
        else:
            # Obtener 1 notificación en concreto

            notification = next((n for n in serializer.data if n["id"] == id), None)

            if not notification:
                return Response(
                    {"Error": "Notificación no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(notification, status=status.HTTP_200_OK)


"""
class visto(APIView):
    def get(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        user = get_user_from_token(header)

        if user:
"""
