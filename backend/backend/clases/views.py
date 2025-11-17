from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from users.serializers import UserInfoSerializer
from users.models import User
from rest_framework.response import Response
from clases.models import Clase
from rest_framework import status
from .serializers import ClaseSerializer

def get_user_from_token(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return None


class CreateClassView(APIView):
    def post(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        token_key = header
        
        if not token_key:
            return Response({'Error': 'Token no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_user_from_token(token_key)
        
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)
        
        name = request.data.get('name')
        description = request.data.get('description')
        
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



class obtainClass(APIView):
    def get(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        Token = header
        user = get_user_from_token(Token)

        if user:
            serializer = UserInfoSerializer(user)
            clases_data = serializer.data['clases']
            return Response({'clases': clases_data}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)
