from django.urls import path
from . import views

urlpatterns = [
    path('', views.settings_view, name='settings'),
    path('backup/', views.backup_database, name='backup_database'),
    path('mark-backup-done/', views.mark_backup_done, name='mark_backup_done'),
]