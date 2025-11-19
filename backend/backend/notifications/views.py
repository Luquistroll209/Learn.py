from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User

from .models import Notification
from .serializers import NotificationSerializer

#obtener cosas de la app de usuarios
from users.views import get_user_from_token
from users.serializers import TokenUserInfoSerializer

#funcion para crear un mensaje 
class createNotification(APIView):
    def post(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        token_key = header
        
        #Mensajes de errores
        if not token_key:
            return Response({'Error': 'Token no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_user_from_token(token_key)
        
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)
        
        
        subject = request.data.get('subject')
        to_email = request.data.get('to')
        message = request.data.get('message')
        

        # más mensajes de errores
        if not subject:
            return Response({'Error': 'El subject de la clase es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        if not to_email:
            return Response({'Error': 'To es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        if not message:
            return Response({'Error': 'Es requerido un mensaje'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener el usuario destinatario por email
        try:
            to_user = User.objects.get(email=to_email)
        except User.DoesNotExist:
            return Response({'Error': 'Usuario destinatario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # Creacion de notificación
        notificación = Notification.objects.create(
            to=to_user,
            subject=subject,
            message=message or '',
            created_by=user
        )
        
        serializer = NotificationSerializer(notificación)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class obtainNotifications(APIView):
    def get(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        Token = header
        user = get_user_from_token(Token)

        if user:
            serializer = TokenUserInfoSerializer(user)
            clases_data = serializer.data['notifications']
            return Response({'notifications': clases_data}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)