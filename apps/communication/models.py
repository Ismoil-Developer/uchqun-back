from django.db import models
from django.conf import settings
from apps.accounts.models import Group


class Announcement(models.Model):
    title = models.CharField(max_length=255, verbose_name="E'lon sarlavhasi")
    content = models.TextField(verbose_name="E'lon matni")
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='announcements',
        verbose_name="Qaysi guruhga (bo'sh bo'lsa hammaga)"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_announcements',
        verbose_name="Muallif"
    )
    is_pinned = models.BooleanField(default=False, verbose_name="Yuqoriga qadab qo'yish")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Chop etilgan vaqti")

    class Meta:
        verbose_name = "E'lon"
        verbose_name_plural = "E'lonlar"
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        target = self.group.name if self.group else "Barcha o'quvchilar"
        return f"{self.title} ({target})"


class NotificationType(models.TextChoices):
    ASSIGNMENT = 'ASSIGNMENT', 'Vazifa xabarnomasi'
    QUIZ = 'QUIZ', 'Test xabarnomasi'
    ATTENDANCE = 'ATTENDANCE', 'Davomat xabarnomasi'
    RANKING = 'RANKING', 'Reyting oʻzgarishi'
    SYSTEM = 'SYSTEM', 'Tizim xabari'


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Qabul qiluvchi"
    )
    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    message = models.TextField(verbose_name="Xabar matni")
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        verbose_name="Turi"
    )
    link = models.CharField(max_length=255, blank=True, verbose_name="Yo'naltiruvchi havola")
    is_read = models.BooleanField(default=False, verbose_name="O'qilganmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqti")

    class Meta:
        verbose_name = "Bildirishnoma"
        verbose_name_plural = "Bildirishnomalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.email} - {self.title}"
