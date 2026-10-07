from rest_framework import serializers
from .models import Announcement, Notification


class AnnouncementSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.full_name')
    group_name = serializers.ReadOnlyField(source='group.name')

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'group', 'group_name', 'author_name', 'is_pinned', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'link', 'is_read', 'created_at']
