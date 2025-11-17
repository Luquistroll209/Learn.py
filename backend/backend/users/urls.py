from django.urls import path
from .views import RegisterView, LoginView, userNameInfo, userToken

urlpatterns = [
    #URLs
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('usernameInfo/', userNameInfo.as_view(), name='usernameInfo'),
    path('userToken/', userToken.as_view(), name='userToken'),
]
