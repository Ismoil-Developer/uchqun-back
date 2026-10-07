from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import Course, Module, Topic, TopicProgress, CourseEnrollment, EnrollmentStatus, TopicStatus
from .serializers import (
    CourseListSerializer,
    ModuleSerializer,
    TopicListSerializer,
    TopicDetailSerializer,
    UpdateTopicProgressSerializer
)


class CourseListView(generics.ListAPIView):
    """
    Ruxsat etilgan dasturlar va kurslar ro'yxati (Figma 2-ekran).
    Foydalanuvchiga qaysi kurslar OCHIQ va qaysilari YOPIQ (Navbat kutilmoqda) ekanligini qaytaradi.
    Tizim cheklovi: Maksimum 1-2 ta kurs ochiq bo'lishi mumkin.
    """
    serializer_class = CourseListSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Courses'])
    def get_queryset(self):
        return Course.objects.filter(is_active=True).order_by('order', 'id')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        # Frontend uchun tizim cheklovi va xush kelibsiz matni
        return Response({
            'greeting': f"Assalomu alaykum, {request.user.first_name or 'bilimdon'}! O'zingiz uchun ruxsat etilgan dasturni tanlang va ta'lim olishni boshlang.",
            'restriction_notice': "Tizim cheklovi: Bir vaqtda faqatgina 1-2 ta kurs ochiq bo'lishi mumkin. Qolgan kurslarni faollashtirish uchun ularni yakunlashingiz kerak.",
            'courses': response.data
        })


class CourseModulesView(APIView):
    """
    Tanlangan kursning modullari ro'yxati (Figma 3-ekran).
    Masalan: HTML Asoslari, CSS Visual Dizayn, JavaScript Dasturlash.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Modules & Topics'],
        parameters=[
            OpenApiParameter(name='slug', type=str, location=OpenApiParameter.PATH, description="Kursning slugi (masalan: frontend-dasturlash)")
        ],
        responses={200: ModuleSerializer(many=True)}
    )
    def get(self, request, slug):
        course = get_object_or_404(Course, slug=slug, is_active=True)
        # Ruxsat tekshirish (agar kurs ochiq bo'lmasa xabar berish)
        enrollment = CourseEnrollment.objects.filter(student=request.user, course=course).first()
        is_open = bool(enrollment and enrollment.status == EnrollmentStatus.OPEN) or request.user.is_staff

        modules = course.modules.all().prefetch_related('topics')
        serializer = ModuleSerializer(modules, many=True, context={'request': request})

        return Response({
            'course_id': course.id,
            'course_title': course.title,
            'course_slug': course.slug,
            'is_accessible': is_open,
            'enrollment_status': enrollment.status if enrollment else 'NONE',
            'modules': serializer.data
        })


class ModuleTopicsView(generics.ListAPIView):
    """
    Tanlangan modulning mavzular ro'yxati (Figma 4-ekran).
    Mavzular bo'yicha qidiruv (search) imkoniyati mavjud.
    """
    serializer_class = TopicListSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Modules & Topics'],
        parameters=[
            OpenApiParameter(name='module_id', type=int, location=OpenApiParameter.PATH, description="Modul ID raqami"),
            OpenApiParameter(name='search', type=str, location=OpenApiParameter.QUERY, description="Mavzu bo'yicha qidiruv"),
        ]
    )
    def get_queryset(self):
        module_id = self.kwargs.get('module_id')
        queryset = Topic.objects.filter(module_id=module_id).order_by('order', 'id')
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset

    def list(self, request, *args, **kwargs):
        module_id = self.kwargs.get('module_id')
        module = get_object_or_404(Module, id=module_id)
        response = super().list(request, *args, **kwargs)
        return Response({
            'module_id': module.id,
            'module_title': module.title,
            'course_title': module.course.title,
            'course_slug': module.course.slug,
            'topics': response.data
        })


class TopicDetailView(generics.RetrieveAPIView):
    """
    Mavzu tafsilotlari (Figma 5-ekran).
    Dars Prezentatsiyasi (PDF yuklab olish, slaydlar), dars kodi, mini-testlar va amaliy topshiriq ma'lumotlari.
    """
    queryset = Topic.objects.all()
    serializer_class = TopicDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Modules & Topics'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UpdateTopicProgressView(APIView):
    """
    O'quvchining mavzuni o'zlashtirish progressini yangilash.
    Slayd ko'rilganda yoki PDF yuklab olinganda chaqiriladi.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Modules & Topics'],
        request=UpdateTopicProgressSerializer,
        responses={200: OpenApiResponse(description="Progress yangilandi")}
    )
    def post(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        serializer = UpdateTopicProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        progress, created = TopicProgress.objects.get_or_create(
            student=request.user,
            topic=topic
        )

        if 'slides_viewed' in data:
            progress.slides_viewed = data['slides_viewed']
        if 'is_presentation_downloaded' in data:
            progress.is_presentation_downloaded = data['is_presentation_downloaded']
        if 'progress_percentage' in data:
            progress.progress_percentage = data['progress_percentage']
        if 'status' in data:
            progress.status = data['status']
        else:
            if progress.progress_percentage >= 100:
                progress.status = TopicStatus.COMPLETED
            elif progress.progress_percentage > 0 or progress.slides_viewed > 0:
                progress.status = TopicStatus.IN_PROGRESS

        progress.save()

        return Response({
            'message': "Progress yangilandi",
            'status': progress.status,
            'progress_percentage': progress.progress_percentage,
            'slides_viewed': progress.slides_viewed,
            'is_presentation_downloaded': progress.is_presentation_downloaded
        }, status=status.HTTP_200_OK)
