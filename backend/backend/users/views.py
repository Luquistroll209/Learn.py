from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            #Obtencion del usuario
            user = serializer.save()
            #Obtencion del token
            token, _ = Token.objects.get_or_create(user=user)
            #Mensajes de Error y Creación
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response({'Error': 'Credetials error'}, status=status.HTTP_401_UNAUTHORIZED)
    
class LoginView(APIView):
    def post(self,request):
        #obtencion del usuario y la contrasñea
        username = request.data.get('username')
        password = request.data.get('password')
        #Autentificación del usuario con esta linea de codigo
        user = authenticate(username=username, password=password)

        #Revisa si es valido y manda los diferentes status, si esta OK manda tambien el token 
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'Error': 'Credetials error'}, status=status.HTTP_401_UNAUTHORIZED)
