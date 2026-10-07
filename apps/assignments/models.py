from django.db import models
from django.conf import settings
from apps.courses.models import Topic


class Assignment(models.Model):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name="Mavzu"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Topshiriq nomi (masalan: Loyiha uchun asosiy metadasturlarni sozlash)"
    )
    description = models.TextField(
        verbose_name="Topshiriq sharti va talablari"
    )
    max_score = models.PositiveIntegerField(
        default=100,
        verbose_name="Maksimal ball (masalan: 100 BALL)"
    )
    deadline_text = models.CharField(
        max_length=100,
        default="1 kun qoldi",
        verbose_name="Muddat matni (masalan: Muddat: 1 kun qoldi)"
    )
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Topshirishning so'nggi muddati"
    )
    is_daily_featured = models.BooleanField(
        default=False,
        verbose_name="Bugungi bosh vazifa (Dashboard bannerida ko'rinadi)"
    )
    banner_subtitle = models.CharField(
        max_length=255,
        blank=True,
        default="Haftalik amaliy topshiriq topshirish vaqti tugashiga 1 kun qoldi.",
        verbose_name="Dashboard banner taglavhasi"
    )
    attachment = models.FileField(
        upload_to='assignments/materials/',
        null=True,
        blank=True,
        verbose_name="Biriktirilgan manba fayli / shablon"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Amaliy topshiriq (Uy ishi)"
        verbose_name_plural = "Amaliy topshiriqlar (Uy ishlari)"
        ordering = ['-is_daily_featured', '-id']

    def __str__(self):
        return f"{self.topic.title} -> {self.title} ({self.max_score} ball)"


class SubmissionStatus(models.TextChoices):
    PENDING = 'PENDING', "Kutilmoqda (Tekshirilmagan)"
    APPROVED = 'APPROVED', "Qabul qilindi va baholandi"
    REJECTED = 'REJECTED', "Qayta topshirishga qaytarildi"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name="Topshiriq"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
        verbose_name="O'quvchi"
    )
    screenshot = models.ImageField(
        upload_to='submissions/images/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Amaliy ish skrinshoti / rasmi (Natija isboti)"
    )
    submission_file = models.FileField(
        upload_to='submissions/files/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Topshirilgan fayl (.zip, .html, .py)"
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="GitHub havola"
    )
    code_text = models.TextField(
        blank=True,
        verbose_name="Topshirilgan kod yoki matn"
    )
    student_comment = models.TextField(
        blank=True,
        verbose_name="O'quvchi izohi"
    )
    status = models.CharField(
        max_length=20,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.PENDING,
        verbose_name="Holati"
    )
    score = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Qo'yilgan ball"
    )
    teacher_feedback = models.TextField(
        blank=True,
        verbose_name="O'qituvchi taqrizi va maslahati"
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_assignments',
        verbose_name="Baholagan o'qituvchi"
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Topshirilgan sana")
    graded_at = models.DateTimeField(null=True, blank=True, verbose_name="Baholangan sana")

    class Meta:
        verbose_name = "Topshirilgan vazifa"
        verbose_name_plural = "Topshirilgan vazifalar"
        ordering = ['-submitted_at']
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.full_name} -> {self.assignment.title} [{self.get_status_display()}]"
