from django.urls import path
from .views import (
    AnnouncementListView,
    NotificationListView,
    MarkNotificationReadView,
    MarkAllNotificationsReadView
)

urlpatterns = [
    path('communication/announcements/', AnnouncementListView.as_view(), name='announcements-list'),
    path('communication/notifications/', NotificationListView.as_view(), name='notifications-list'),
    path('communication/notifications/<int:pk>/read/', MarkNotificationReadView.as_view(), name='notification-mark-read'),
    path('communication/notifications/read-all/', MarkAllNotificationsReadView.as_view(), name='notifications-read-all'),
]
