from django.urls import path
from .views import obtainClass, CreateClassView, inviteUser, JoinClassAutoView, obtainClassByID

urlpatterns = [
    #URLs - obtención de datos
    path('obtainClass/', obtainClass.as_view(), name='obtainClass'),
    path('obtainClassByID/<str:identifier>', obtainClassByID.as_view(), name='obtainClassByID'),
    #creación y gestion
    path('createClass/', CreateClassView.as_view(), name='createClass'),

    #Invitaciones y unirse a clases
    path('invite/', inviteUser.as_view(), name='invite-user'),
    path('join/<str:clase_id>/', JoinClassAutoView.as_view(), name='join-class-auto'),
]
