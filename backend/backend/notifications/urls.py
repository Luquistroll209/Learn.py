from django.urls import path
from .views import createNotification, obtainNotifications

urlpatterns = [
    #URLs
    path('createNotification/', createNotification.as_view(), name='createNotification'),

    #obtener las notificasciones de todas las del usuario o unicamente una notificación
    path('obtainNotifications/<int:id>', obtainNotifications.as_view(), name='obtainNotifications'),
    path('obtainNotifications/', obtainNotifications.as_view(), name='obtainNotifications'),

]
