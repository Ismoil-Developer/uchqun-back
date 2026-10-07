from rest_framework import serializers
from .models import Course, CourseEnrollment, Module, Topic, TopicProgress, EnrollmentStatus, TopicStatus


class CourseListSerializer(serializers.ModelSerializer):
    enrollment_status = serializers.SerializerMethodField()
    is_accessible = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'icon',
            'technologies', 'order', 'enrollment_status',
            'is_accessible', 'status_label', 'progress_percentage'
        ]

    def _get_enrollment(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user or not user.is_authenticated:
            return None
        # Use prefetched or query
        return CourseEnrollment.objects.filter(student=user, course=obj).first()

    def get_enrollment_status(self, obj):
        enrollment = self._get_enrollment(obj)
        return enrollment.status if enrollment else None

    def get_is_accessible(self, obj):
        enrollment = self._get_enrollment(obj)
        return bool(enrollment and enrollment.status == EnrollmentStatus.OPEN)

    def get_status_label(self, obj):
        enrollment = self._get_enrollment(obj)
        if not enrollment:
            return "Ruxsat berilmagan"
        return enrollment.get_status_display()

    def get_progress_percentage(self, obj):
        enrollment = self._get_enrollment(obj)
        return float(enrollment.progress_percentage) if enrollment else 0.0


class TopicListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    has_presentation = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            'id', 'order', 'title', 'lessons_count', 'duration_hours',
            'status', 'progress_percentage', 'has_presentation'
        ]

    def _get_progress(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user or not user.is_authenticated:
            return None
        return TopicProgress.objects.filter(student=user, topic=obj).first()

    def get_status(self, obj):
        progress = self._get_progress(obj)
        if progress:
            return progress.status
        # Default status: birinchi mavzu bo'lsa BOSHLANMAGAN, keyingilari YOPIQ
        return TopicStatus.NOT_STARTED if obj.order == 1 else TopicStatus.LOCKED

    def get_progress_percentage(self, obj):
        progress = self._get_progress(obj)
        return progress.progress_percentage if progress else 0

    def get_has_presentation(self, obj):
        return bool(obj.presentation_file)


class ModuleSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    topics = TopicListSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'order',
            'lessons_count_display', 'topics_count_display',
            'status', 'progress_percentage', 'topics'
        ]

    def get_progress_percentage(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user or not user.is_authenticated:
            return 0
        topics = obj.topics.all()
        if not topics.exists():
            return 0
        progresses = TopicProgress.objects.filter(student=user, topic__in=topics)
        if not progresses.exists():
            return 0
        total_p = sum(p.progress_percentage for p in progresses)
        return round(total_p / topics.count())

    def get_status(self, obj):
        p = self.get_progress_percentage(obj)
        if p >= 100:
            return "TUGALLANDI"
        elif p > 0 or obj.order == 1:
            return "FAOLLASHGAN"
        return "YOPIQ"


class TopicDetailSerializer(serializers.ModelSerializer):
    module_title = serializers.ReadOnlyField(source='module.title')
    course_title = serializers.ReadOnlyField(source='module.course.title')
    presentation_file_url = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    quizzes_count = serializers.SerializerMethodField()
    assignments_count = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            'id', 'order', 'title', 'module_title', 'course_title',
            'lessons_count', 'duration_hours', 'description',
            'presentation_title', 'presentation_file_url', 'slides_count',
            'source_code_url', 'source_code_snippet', 'video_url',
            'user_progress', 'quizzes_count', 'assignments_count'
        ]

    def get_presentation_file_url(self, obj):
        request = self.context.get('request')
        if obj.presentation_file:
            if request:
                return request.build_absolute_uri(obj.presentation_file.url)
            return obj.presentation_file.url
        return None

    def get_user_progress(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user or not user.is_authenticated:
            return None
        progress = TopicProgress.objects.filter(student=user, topic=obj).first()
        if progress:
            return {
                'status': progress.status,
                'progress_percentage': progress.progress_percentage,
                'slides_viewed': progress.slides_viewed,
                'is_presentation_downloaded': progress.is_presentation_downloaded,
            }
        return {
            'status': TopicStatus.NOT_STARTED if obj.order == 1 else TopicStatus.LOCKED,
            'progress_percentage': 0,
            'slides_viewed': 0,
            'is_presentation_downloaded': False,
        }

    def get_quizzes_count(self, obj):
        return obj.quizzes.count()

    def get_assignments_count(self, obj):
        return obj.assignments.count()


class UpdateTopicProgressSerializer(serializers.Serializer):
    slides_viewed = serializers.IntegerField(required=False, min_value=0)
    is_presentation_downloaded = serializers.BooleanField(required=False)
    progress_percentage = serializers.IntegerField(required=False, min_value=0, max_value=100)
    status = serializers.ChoiceField(choices=TopicStatus.choices, required=False)
