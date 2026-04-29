from django.urls import path
from .views import (
    obtainClass,
    CreateClassView,
    inviteUser,
    JoinClassAutoView,
    obtainClassByID,
    ObtainClassDashboardView,
    UpdateClassSettingsView,
    RemoveClassMemberView,
    LeaveClassView,
    CreateAnnouncementView,
    ObtainAnnouncementsView,
    ObtainAnnouncementDetailView,
    ManageAnnouncementView,
    CreateAnnouncementCommentView,
    ManageAnnouncementCommentView,
    CreateTaskView,
    ManageTaskView,
    SubmitTaskView,
    ObtainPendingTasksView,
    ObtainTaskDetailView,
    GradeTaskSubmissionView,
)

urlpatterns = [
    #URLs - obtención de datos
    path('obtainClass/', obtainClass.as_view(), name='obtainClass'),
    path('obtainClassByID/<str:identifier>', obtainClassByID.as_view(), name='obtainClassByID'),
    path('obtainClassDashboard/<str:clase_id>/', ObtainClassDashboardView.as_view(), name='obtain-class-dashboard'),
    #creación y gestion
    path('createClass/', CreateClassView.as_view(), name='createClass'),
    path('updateClassSettings/<str:clase_id>/', UpdateClassSettingsView.as_view(), name='update-class-settings'),

    #Invitaciones y unirse a clases
    path('invite/', inviteUser.as_view(), name='invite-user'),
    path('join/<str:clase_id>/', JoinClassAutoView.as_view(), name='join-class-auto'),
    path('leaveClass/<str:clase_id>/', LeaveClassView.as_view(), name='leave-class'),
    path('removeMember/<str:clase_id>/<int:user_id>/', RemoveClassMemberView.as_view(), name='remove-member'),

    #Post de clases
    path('createAnnouncement/', CreateAnnouncementView.as_view(), name='create-announcement'),
    path('obtainAnnouncements/<str:clase_id>/', ObtainAnnouncementsView.as_view(), name='obtain-announcements'),
    path('obtainAnnouncementDetail/<int:announcement_id>/', ObtainAnnouncementDetailView.as_view(), name='obtain-announcement-detail'),
    path('manageAnnouncement/<int:announcement_id>/', ManageAnnouncementView.as_view(), name='manage-announcement'),
    path('createAnnouncementComment/<int:announcement_id>/', CreateAnnouncementCommentView.as_view(), name='create-announcement-comment'),
    path('manageAnnouncementComment/<int:comment_id>/', ManageAnnouncementCommentView.as_view(), name='manage-announcement-comment'),

    #Tareas
    path('createTask/<str:clase_id>/', CreateTaskView.as_view(), name='create-task'),
    path('manageTask/<int:task_id>/', ManageTaskView.as_view(), name='manage-task'),
    path('submitTask/<int:task_id>/', SubmitTaskView.as_view(), name='submit-task'),
    path('obtainPendingTasks/<str:clase_id>/', ObtainPendingTasksView.as_view(), name='obtain-pending-tasks'),
    path('obtainTaskDetail/<int:task_id>/', ObtainTaskDetailView.as_view(), name='obtain-task-detail'),
    path('gradeTaskSubmission/<int:task_id>/', GradeTaskSubmissionView.as_view(), name='grade-task-submission'),

]
