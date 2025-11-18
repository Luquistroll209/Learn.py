from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

#obtener cosas de la app de usuarios
from users.views import get_user_from_token

#funcion para crear un mensaje 

#SIN TERMINAR TENGO QUE TERMINARLO
class CreateClassView(APIView):
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
        to = request.data.get('to')
        message = request.data.get('message')
        
        if not name:
            return Response({'Error': 'El nombre de la clase es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Creacion de clase
        clase = Clase.objects.create(
            name=name,
            description=description or '',
            created_by=user
        )
        
        # Agrega al usuario(Maestro) a la clase
        clase.students.add(user)
        
        serializer = ClaseSerializer(clase)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
