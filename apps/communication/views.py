from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Announcement, Notification
from .serializers import AnnouncementSerializer, NotificationSerializer


class AnnouncementListView(generics.ListAPIView):
    """
    E'lonlar va muloqot markazi xabarlari (Figma Muloqot markazi).
    """
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Communication'])
    def get_queryset(self):
        user = self.request.user
        group = getattr(user, 'student_profile', None)
        user_group = group.group if group else None

        # Hammaga tegishli e'lonlar yoki o'z guruhiga tegishli e'lonlar
        return Announcement.objects.filter(
            Q(group__isnull=True) | Q(group=user_group)
        ).order_by('-is_pinned', '-created_at')


class NotificationListView(generics.ListAPIView):
    """
    Foydalanuvchining shaxsiy bildirishnomalari (Figma tepa o'ngdagi qo'ng'iroqcha belgisi).
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Communication'])
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        unread_count = queryset.filter(is_read=False).count()
        serializer = self.get_serializer(queryset[:20], many=True)
        return Response({
            'unread_count': unread_count,
            'notifications': serializer.data
        })


class MarkNotificationReadView(APIView):
    """
    Bildirishnomani o'qilgan deb belgilash.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Communication'],
        request=None,
        responses={200: OpenApiResponse(description="O'qilgan deb belgilandi")}
    )
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({'message': "Bildirishnoma o'qildi deb belgilandi."}, status=status.HTTP_200_OK)


class MarkAllNotificationsReadView(APIView):
    """
    Barcha bildirishnomalarni o'qilgan deb belgilash.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Communication'],
        request=None,
        responses={200: OpenApiResponse(description="Barchasi o'qildi")}
    )
    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'message': "Barcha bildirishnomalar o'qildi."}, status=status.HTTP_200_OK)
