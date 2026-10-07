from django.db import models
from django.conf import settings
from apps.accounts.models import Group
from apps.courses.models import Topic


class AttendanceStatus(models.TextChoices):
    PRESENT = 'PRESENT', 'Qatnashdi (Kelgan)'
    ABSENT = 'ABSENT', 'Qatnashmadi (Kelmagan)'
    EXCUSED = 'EXCUSED', 'Sababli'
    LATE = 'LATE', 'Kechikdi'


class Attendance(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="O'quvchi"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="Guruh"
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances',
        verbose_name="O'tilgan dars/mavzu"
    )
    date = models.DateField(verbose_name="Sana")
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
        verbose_name="Davomat holati"
    )
    teacher_note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="O'qituvchi izohi"
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_attendances',
        verbose_name="Belgilagan ustoz"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Davomat qaydi"
        verbose_name_plural = "Davomat qaydlari"
        unique_together = ('student', 'date', 'group')
        ordering = ['-date', 'student__first_name']

    def __str__(self):
        return f"{self.date} | {self.student.full_name} - {self.get_status_display()}"


class AchievementBadge(models.Model):
    name = models.CharField(max_length=100, verbose_name="Yutuq nishoni nomi")
    description = models.TextField(verbose_name="Qanday erishiladi")
    icon = models.CharField(max_length=50, default="award", verbose_name="Icon nomi")
    points_required = models.PositiveIntegerField(default=100, verbose_name="Kerakli ball")

    class Meta:
        verbose_name = "Yutuq nishoni"
        verbose_name_plural = "Yutuq nishonlari"

    def __str__(self):
        return self.name


class StudentBadge(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='badges'
    )
    badge = models.ForeignKey(AchievementBadge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "O'quvchi yutug'i"
        verbose_name_plural = "O'quvchilar yutuqlari"
        unique_together = ('student', 'badge')
