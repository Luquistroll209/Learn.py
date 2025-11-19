from django.urls import path
from .views import obtainClass, CreateClassView, inviteUser, JoinClassAutoView

urlpatterns = [
    #URLs
    path('obtainClass/', obtainClass.as_view(), name='obtainClass'),
    path('createClass/', CreateClassView.as_view(), name='createClass'),

    #Invitaciones y unirse a clases
    path('invite/', inviteUser.as_view(), name='invite-user'),
    path('join/<int:clase_id>/', JoinClassAutoView.as_view(), name='join-class-auto'),
]
