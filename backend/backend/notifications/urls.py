from django.urls import path
from .views import createNotification, obtainNotifications

urlpatterns = [
    #URLs
    path('createNotification/', createNotification.as_view(), name='createNotification'),
    path('obtainNotifications/', obtainNotifications.as_view(), name='obtainNotifications'),

]
