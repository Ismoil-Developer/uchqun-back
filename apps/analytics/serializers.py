from rest_framework import serializers
from .models import Attendance, AchievementBadge, StudentBadge
from apps.accounts.models import User, StudentProfile


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.full_name')
    group_name = serializers.ReadOnlyField(source='group.name')
    topic_title = serializers.ReadOnlyField(source='topic.title')
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id', 'date', 'student', 'student_name', 'group', 'group_name',
            'topic', 'topic_title', 'status', 'status_label', 'teacher_note'
        ]


class LeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    student_id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.CharField()
    avatar = serializers.CharField(allow_null=True)
    group_name = serializers.CharField()
    total_points = serializers.IntegerField()
    attendance_rate = serializers.FloatField()
    completed_tasks_count = serializers.IntegerField()
    passed_quizzes_count = serializers.IntegerField()
    is_current_user = serializers.BooleanField()


class AchievementBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AchievementBadge
        fields = ['id', 'name', 'description', 'icon', 'points_required']


class ParentChildSummarySerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.CharField()
    avatar = serializers.CharField(allow_null=True)
    group_name = serializers.CharField()
    total_points = serializers.IntegerField()
    attendance_rate = serializers.FloatField()
    completed_tasks_count = serializers.IntegerField()
