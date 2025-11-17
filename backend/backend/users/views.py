from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, UserInfoSerializer, TokenUserInfoSerializer

from rest_framework.authtoken.models import Token

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Obtención del usuario
            user = serializer.save()
            # Obtención del token
            token, _ = Token.objects.get_or_create(user=user)
            # Mensajes de Error y Creación
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    def post(self, request):
        # Obtención del nombre de usuario y contraseña
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Buscar usuario por email
        try:
            user_by_email = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'Error': 'Credenciales incorrectas'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Autentificarse
        user = authenticate(username=user_by_email.username, password=password)
        
        
        #Revisa si es valido
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            #Me acabo de dar cuenta de que el username esta mal, deberia ser name, pero ya lo arreglare en un futuro
            return Response({'token': token.key, 'name': user.username, 'last_name': user.last_name}, status=status.HTTP_200_OK)
        return Response({'Error': 'Credenciales incorrectas'}, status=status.HTTP_401_UNAUTHORIZED)

class userNameInfo(APIView): 
    def post(self, request):
        name = request.data.get('name')
        try:
            user = User.objects.get(username=name)
            serializer = UserInfoSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'Error': 'User doesn\'t exist'}, status=status.HTTP_404_NOT_FOUND)

def get_user_from_token(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return None
    
class userToken(APIView):
    def get(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        token_key = auth_header
        user = get_user_from_token(token_key)
            
        if user:
            serializer = TokenUserInfoSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        
    #return Response({'Error': 'Token no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)


# Notificaciones

class  createMensaje(APIView):
    def post(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        User = get_user_from_token(header)

        sendTo = request.data.get('sendTo')
        asunto = request.data.get('password')
        description = request.data.get('password')
        #SIN TERMINAR, TERMINAR EN EL FUTURO



        
