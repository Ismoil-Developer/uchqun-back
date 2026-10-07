from rest_framework import serializers
from .models import Assignment, AssignmentSubmission, SubmissionStatus


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.full_name')
    graded_by_name = serializers.ReadOnlyField(source='graded_by.full_name')
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'assignment', 'student', 'student_name',
            'screenshot', 'submission_file', 'github_url', 'code_text',
            'student_comment', 'status', 'status_label', 'score',
            'teacher_feedback', 'graded_by_name', 'submitted_at', 'graded_at'
        ]
        read_only_fields = ['id', 'student', 'status', 'score', 'teacher_feedback', 'graded_by', 'submitted_at', 'graded_at']


class AssignmentDetailSerializer(serializers.ModelSerializer):
    topic_title = serializers.ReadOnlyField(source='topic.title')
    module_title = serializers.ReadOnlyField(source='topic.module.title')
    course_title = serializers.ReadOnlyField(source='topic.module.course.title')
    my_submission = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id', 'topic', 'topic_title', 'module_title', 'course_title',
            'title', 'description', 'max_score', 'deadline_text',
            'due_date', 'is_daily_featured', 'banner_subtitle',
            'attachment', 'my_submission'
        ]

    def get_my_submission(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user or not user.is_authenticated:
            return None
        submission = AssignmentSubmission.objects.filter(assignment=obj, student=user).first()
        if submission:
            request = self.context.get('request')
            return AssignmentSubmissionSerializer(submission, context={'request': request}).data
        return None


class SubmitAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ['screenshot', 'submission_file', 'github_url', 'code_text', 'student_comment']

    def validate(self, attrs):
        # Kamida bitta isbot yuborilishi kerak (rasm, fayl, github yoki kod)
        if not any([
            attrs.get('screenshot'),
            attrs.get('submission_file'),
            attrs.get('github_url'),
            attrs.get('code_text')
        ]):
            raise serializers.ValidationError("Kamida bitta topshiriq isboti (rasm, havola, kod yoki fayl) yuklanishi shart.")
        return attrs


class GradeSubmissionSerializer(serializers.Serializer):
    score = serializers.IntegerField(required=True, min_value=0)
    teacher_feedback = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=[SubmissionStatus.APPROVED, SubmissionStatus.REJECTED],
        default=SubmissionStatus.APPROVED
    )
