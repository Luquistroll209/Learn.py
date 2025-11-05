from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, UserInfoSerializer  

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
        name = request.data.get('name')
        password = request.data.get('password')
        # Autentificación del usuario - usa 'username' internamente pero 'name' en la API
        user = authenticate(username=name, password=password)  # Internamente usa username

        # Revisa si es válido y manda los diferentes status, si está OK manda también el token
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
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

        