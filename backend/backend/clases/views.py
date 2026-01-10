from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from users.serializers import TokenUserInfoSerializer
from users.models import User
from rest_framework.response import Response
from clases.models import Clase
from rest_framework import status
from .serializers import ClaseSerializer, AnnouncementSerializer
from .models import ClaseMembership, Announcement
from users.views import get_user_from_token
from django.conf import settings

#Funciones de mensajeria
from notifications.views import enviarMensaje

#Funcion para crear una clase 
class CreateClassView(APIView):
    def post(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        token_key = header
        
        # Mensajes de errores
        if not token_key:
            return Response({'Error': 'Token no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_user_from_token(token_key)
        
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()

        if 'id' in data:
            del data['id']    
        
        serializer = ClaseSerializer(
            data=data,
            context={
                'request': request,
                'teacher': user
            }
        )       
        
        if serializer.is_valid():
            clase = serializer.save()
            ClaseMembership.objects.create(
                user=user,
                clase=clase,
                role='teacher'
            )
            
            clase.students.add(user)

            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Errores del serializador:", serializer.errors)
            return Response(
                {'Error': 'Datos inválidos', 'details': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )



#funcion para obtener todas las clases del usuario mediante el token de este
class obtainClass(APIView):
    def get(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        Token = header
        user = get_user_from_token(Token)

        if user:
            serializer = TokenUserInfoSerializer(user)
            clases_data = serializer.data['clases']
            return Response({'clases': clases_data}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)

class obtainClassByID(APIView):
    def get(self, request, identifier=None):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        user = get_user_from_token(header)

        if not user:
            return Response({'Error': 'Token incorrecto'}, status=status.HTTP_401_UNAUTHORIZED)

        if not identifier:
            return Response(
                {'Error': 'Se requiere una ID de una clase'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TokenUserInfoSerializer(user)
        clases_data = serializer.data['clases']

        clase = next(
            (c for c in clases_data if c['id'] == identifier),
            None
        )

        if not clase:
            return Response(
                {'Error': 'Clase no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(clase, status=status.HTTP_200_OK)

        

class inviteUser(APIView):
    def post(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        token = header
        user = get_user_from_token(token)

        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Obtener datos
        clase_id = request.data.get('clase_id')
        email = request.data.get('email')
        
        # Mensajes de erores
        if not clase_id:
            return Response({'Error': 'clase_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not email:
            return Response({'Error': 'email es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Busca el id de la clase
            clase = Clase.objects.get(id=clase_id)
            
            # Verificaciones
            if clase.teacher != user:
                return Response({'Error': 'Solo el profesor puede invitar usuarios'}, status=status.HTTP_403_FORBIDDEN)
            
            user_to_invite = User.objects.get(email=email)

            if clase.students.filter(id=user_to_invite.id).exists():
                return Response({'Error': 'El usuario ya está en esta clase'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear enlace de invitación
            join_url = settings.IP + f"/api/class/join/{clase.id}/" 
            
            # Mesnaje a enviar
            mensaje_invitacion = f"""
            ¡Has sido invitado a unirte a la clase "{clase.name}"!
            
            Profesor: {user.get_full_name() or user.email}
            
            Para unirte a la clase, haz clic en el siguiente enlace:
            {join_url}
            
            Descripción: {clase.description}
            """
            
            asunto = f"Invitación a la clase: {clase.name}"
            
            #enviar mensaje al correo y guardado en la base de datos 
            notificacion_data = enviarMensaje(
                asunto=asunto,
                mensaje=mensaje_invitacion,
                destinario=user_to_invite,
                email=email,
                user=user
            )
            
            return Response({
                'message': f'Invitación enviada a {email}',
                'notificacion': notificacion_data
            }, status=status.HTTP_200_OK)
            
        except Clase.DoesNotExist:
            return Response({'Error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

#Funcion para invitar a un usuario mediante el email
class inviteUser(APIView):
    def post(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        token = header
        user = get_user_from_token(token)

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
            
            # Verificaciones
            if clase.teacher != user:
                return Response({'Error': 'Solo el profesor puede invitar usuarios'}, status=status.HTTP_403_FORBIDDEN)
            
            user_to_invite = User.objects.get(email=email)

            if clase.students.filter(id=user_to_invite.id).exists():
                return Response({'Error': 'El usuario ya está en esta clase'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear enlace de invitación con el nuevo ID
            join_url = settings.IP + f"/api/class/join/{clase.id}/" 
            
            # Mensaje a enviar
            mensaje_invitacion = f"""
            ¡Has sido invitado a unirte a la clase "{clase.name}"!
            
            ID de la clase: {clase.id}
            
            Profesor: {user.get_full_name() or user.email}
            
            Para unirte a la clase, haz clic en el siguiente enlace:
            {join_url}
            
            Descripción: {clase.description}
            """
            
            asunto = f"Invitación a la clase: {clase.name}"
            
            # enviar mensaje al correo y guardado en la base de datos 
            notificacion_data = enviarMensaje(
                asunto=asunto,
                mensaje=mensaje_invitacion,
                destinario=user_to_invite,
                email=email,
                user=user
            )
            
            return Response({
                'message': f'Invitación enviada a {email}',
                'notificacion': notificacion_data,
                'class_id': clase.id
            }, status=status.HTTP_200_OK)
            
        except Clase.DoesNotExist:
            return Response({'Error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


class JoinClassAutoView(APIView):
    def get(self, request, clase_id):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        token = header
        user = get_user_from_token(token)

        # verificaciones
        if not user:
            return Response({'Error': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            clase = Clase.objects.get(id=clase_id)
            if clase.students.filter(id=user.id).exists():
                try:
                    membership = ClaseMembership.objects.get(user=user, clase=clase)
                    serializer = ClaseSerializer(clase)

                    student_info = next(
                        (s for s in serializer.data['students_info'] 
                        if s['user_id'] == user.id),
                        None
                    )
                    
                    return Response({
                        'message': 'Ya estás en esta clase',
                        'unionDate': student_info['joined_at'] if student_info else None,
                        'role': membership.role,
                        'teacherName': serializer.data['teacher_name'],
                        'className': serializer.data['name'],

                        #'clase': serializer.data,
                        
                    }, status=status.HTTP_200_OK)
                except ClaseMembership.DoesNotExist:
                    pass
            clase_membership = ClaseMembership.objects.create(
                user=user,
                clase=clase,
                role='student'  # Rol por defecto
            )
            # agregación del usuario a la clase
            clase.students.add(user)
            
            serializer = ClaseSerializer(clase)

            return Response({
                'message': 'Te has unido a la clase exitosamente',
                'clase': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Clase.DoesNotExist:
            return Response({'Error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)

#para añadir anuncios
class CreateAnnouncementView(APIView):
    def post(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        token_key = header
        
        if not token_key:
            return Response(
                {'Error': 'Token no proporcionado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_user_from_token(token_key)
        
        if not user:
            return Response(
                {'Error': 'Usuario no encontrado'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        data = request.data.copy()
        
        if 'clase_id' not in data:
            return Response(
                {'Error': 'clase_id es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if 'title' not in data or not data['title']:
            return Response(
                {'Error': 'title es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if 'description' not in data or not data['description']:
            return Response(
                {'Error': 'description es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if 'photos' not in data:
            data['photos'] = []
        
        if 'urls' not in data:
            data['urls'] = []

        serializer = AnnouncementSerializer(
            data=data,
            context={'user': user, 'request': request}
        )
        
        if serializer.is_valid():
            announcement = serializer.save()
            response_serializer = AnnouncementSerializer(
                announcement, 
                context={'request': request}
            )
            
            return Response({
                'message': 'Anuncio creado exitosamente',
                'announcement': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            """    
            except serializers.ValidationError as e:
                return Response(
                    {'Error': 'Error de validación', 'details': e.detail}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            """
        else:
            return Response(
                {'Error': 'Datos inválidos', 'details': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )