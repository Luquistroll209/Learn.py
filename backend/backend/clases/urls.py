from django.urls import path
from .views import obtainClass, CreateClassView

urlpatterns = [
    #URLs
    path('obtainClass/', obtainClass.as_view(), name='obtainClass'),
    path('createClass/', CreateClassView.as_view(), name='createClass'),
]
