from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Assignment, AssignmentSubmission, SubmissionStatus
from .serializers import (
    AssignmentDetailSerializer,
    AssignmentSubmissionSerializer,
    SubmitAssignmentSerializer,
    GradeSubmissionSerializer
)
from apps.courses.models import TopicProgress, TopicStatus
from apps.accounts.models import UserRole


class DailyFeaturedAssignmentView(APIView):
    """
    Dashboarddagi bugungi asosiy vazifa banneri (Figma 3-ekran).
    'Bugungi vazifa: Portfolio loyihasini yakunlash'
    'Haftalik amaliy topshiriq topshirish vaqti tugashiga 1 kun qoldi.'
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Assignments'],
        responses={200: OpenApiResponse(description="Bugungi bosh vazifa banneri")}
    )
    def get(self, request):
        featured = Assignment.objects.filter(is_daily_featured=True).first()
        if not featured:
            featured = Assignment.objects.first()

        if not featured:
            return Response({'has_featured': False, 'assignment': None})

        serializer = AssignmentDetailSerializer(featured, context={'request': request})
        return Response({
            'has_featured': True,
            'assignment': serializer.data
        })


class TopicAssignmentView(APIView):
    """
    Mavzuga biriktirilgan amaliy topshiriq (Figma 5-ekran o'ng tomon).
    [100 BALL] [Muddat: 1 kun qoldi]
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Assignments'], responses={200: AssignmentDetailSerializer})
    def get(self, request, topic_id):
        assignment = Assignment.objects.filter(topic_id=topic_id).first()
        if not assignment:
            return Response({'detail': "Ushbu mavzuda hali amaliy vazifa kiritilmagan."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignmentDetailSerializer(assignment, context={'request': request})
        return Response(serializer.data)


class AssignmentDetailView(generics.RetrieveAPIView):
    """
    Amaliy topshiriqning to'liq tafsilotlari.
    """
    queryset = Assignment.objects.all()
    serializer_class = AssignmentDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Assignments'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SubmitAssignmentView(APIView):
    """
    Vazifani topshirish (Figma 5-ekran 'Vazifani topshirish' tugmasi).
    O'quvchi topshiriq natijasini rasm (skrinshot), fayl, GitHub havola yoki kod sifatida yuklaydi.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        tags=['Assignments'],
        request=SubmitAssignmentSerializer,
        responses={200: OpenApiResponse(description="Vazifa muvaffaqiyatli topshirildi")}
    )
    def post(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)

        # Oldingi topshirilgan bo'lsa yangilash yoki yangi yaratish
        submission, created = AssignmentSubmission.objects.get_or_create(
            assignment=assignment,
            student=request.user,
        )

        serializer = SubmitAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if 'screenshot' in request.FILES:
            submission.screenshot = request.FILES['screenshot']
        if 'submission_file' in request.FILES:
            submission.submission_file = request.FILES['submission_file']
        if 'github_url' in data:
            submission.github_url = data['github_url']
        if 'code_text' in data:
            submission.code_text = data['code_text']
        if 'student_comment' in data:
            submission.student_comment = data['student_comment']

        submission.status = SubmissionStatus.PENDING
        submission.submitted_at = timezone.now()
        submission.save()

        # Topic progressini yangilash
        progress, _ = TopicProgress.objects.get_or_create(
            student=request.user,
            topic=assignment.topic
        )
        if progress.progress_percentage < 75:
            progress.progress_percentage = 75
            progress.status = TopicStatus.IN_PROGRESS
            progress.save()

        return Response({
            'message': "Topshiriq muvaffaqiyatli yuborildi. O'qituvchi tekshiruvidan so'ng baholanadi.",
            'submission_id': submission.id,
            'status': submission.status,
            'status_label': submission.get_status_display()
        }, status=status.HTTP_200_OK)


class MySubmissionsListView(generics.ListAPIView):
    """
    O'quvchining barcha topshirgan uy ishlari ro'yxati (Figma Topshiriqlar bo'limi).
    """
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Assignments'])
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return AssignmentSubmission.objects.none()
        return AssignmentSubmission.objects.filter(student=self.request.user).order_by('-submitted_at')


class GradeSubmissionView(APIView):
    """
    O'qituvchi yoki admin tomonidan o'quvchining vazifasini baholash va izoh qoldirish.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Assignments'],
        request=GradeSubmissionSerializer,
        responses={200: OpenApiResponse(description="Vazifa baholandi")}
    )
    def post(self, request, pk):
        if request.user.role not in [UserRole.ADMIN, UserRole.TEACHER] and not request.user.is_staff:
            return Response({'detail': "Faqat o'qituvchilar va adminlar vazifani baholashi mumkin."}, status=status.HTTP_403_FORBIDDEN)

        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        serializer = GradeSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        submission.score = data['score']
        submission.teacher_feedback = data.get('teacher_feedback', '')
        submission.status = data['status']
        submission.graded_by = request.user
        submission.graded_at = timezone.now()
        submission.save()

        # O'quvchi profiliga ball qo'shish
        if submission.status == SubmissionStatus.APPROVED and hasattr(submission.student, 'student_profile'):
            profile = submission.student.student_profile
            profile.total_points += submission.score
            profile.completed_tasks_count += 1
            profile.save()

            # Mavzuni 100% tugallangan qilish
            progress, _ = TopicProgress.objects.get_or_create(
                student=submission.student,
                topic=submission.assignment.topic
            )
            progress.progress_percentage = 100
            progress.status = TopicStatus.COMPLETED
            progress.save()

        return Response({
            'message': "Vazifa muvaffaqiyatli baholandi.",
            'score': submission.score,
            'status': submission.status
        }, status=status.HTTP_200_OK)
