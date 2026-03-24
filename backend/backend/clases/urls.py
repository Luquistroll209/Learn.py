from django.urls import path
from .views import (
    obtainClass,
    CreateClassView,
    inviteUser,
    JoinClassAutoView,
    obtainClassByID,
    CreateAnnouncementView,
    ObtainAnnouncementsView,
    CreateTaskView,
    SubmitTaskView,
    ObtainPendingTasksView,
    ObtainTaskDetailView,
    GradeTaskSubmissionView,
)

urlpatterns = [
    #URLs - obtención de datos
    path('obtainClass/', obtainClass.as_view(), name='obtainClass'),
    path('obtainClassByID/<str:identifier>', obtainClassByID.as_view(), name='obtainClassByID'),
    #creación y gestion
    path('createClass/', CreateClassView.as_view(), name='createClass'),

    #Invitaciones y unirse a clases
    path('invite/', inviteUser.as_view(), name='invite-user'),
    path('join/<str:clase_id>/', JoinClassAutoView.as_view(), name='join-class-auto'),

    #Post de clases
    path('createAnnouncement/', CreateAnnouncementView.as_view(), name='create-announcement'),
    path('obtainAnnouncements/<str:clase_id>/', ObtainAnnouncementsView.as_view(), name='obtain-announcements'),

    #Tareas
    path('createTask/<str:clase_id>/', CreateTaskView.as_view(), name='create-task'),
    path('submitTask/<int:task_id>/', SubmitTaskView.as_view(), name='submit-task'),
    path('obtainPendingTasks/<str:clase_id>/', ObtainPendingTasksView.as_view(), name='obtain-pending-tasks'),
    path('obtainTaskDetail/<int:task_id>/', ObtainTaskDetailView.as_view(), name='obtain-task-detail'),
    path('gradeTaskSubmission/<int:task_id>/', GradeTaskSubmissionView.as_view(), name='grade-task-submission'),

]
