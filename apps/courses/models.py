from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Kurs nomi")
    slug = models.SlugField(max_length=220, unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Kurs tavsifi")
    icon = models.CharField(max_length=50, default="code", verbose_name="Icon nomi (masalan: code, database, mobile)")
    technologies = models.JSONField(
        default=list,
        blank=True,
        verbose_name="O'rgatiladigan texnologiyalar (masalan: ['HTML', 'CSS', 'JavaScript', 'React'])"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami")
    is_active = models.BooleanField(default=True, verbose_name="Tizimda faolmi")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class EnrollmentStatus(models.TextChoices):
    OPEN = 'OPEN', 'Ochiq'
    WAITING = 'WAITING', 'Yopiq (Navbat kutilmoqda)'
    COMPLETED = 'COMPLETED', 'Yakunlangan'


class CourseEnrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_enrollments',
        verbose_name="O'quvchi"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Kurs"
    )
    status = models.CharField(
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.WAITING,
        verbose_name="Holati"
    )
    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name="Kurs taraqqiyoti (%)"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name="Yozilgan sana")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Tugatilgan sana")

    class Meta:
        verbose_name = "Kursga yozilish (Ruxsat)"
        verbose_name_plural = "Kurslarga yozilishlar (Ruxsatlar)"
        unique_together = ('student', 'course')
        ordering = ['-status', 'course__order']

    def clean(self):
        # Tizim cheklovi: Bir vaqtda bir o'quvchida maksimum 2 ta faol (OPEN) kurs bo'lishi mumkin.
        if self.status == EnrollmentStatus.OPEN:
            active_count = CourseEnrollment.objects.filter(
                student=self.student,
                status=EnrollmentStatus.OPEN
            ).exclude(pk=self.pk).count()
            if active_count >= 2:
                raise ValidationError("Bir vaqtda faqatgina 1-2 ta kurs ochiq bo'lishi mumkin. Yangi kursni ochish uchun avvalgisini yakunlang.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.full_name} -> {self.course.title} [{self.get_status_display()}]"


class Module(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name="Qaysi kursga tegishli"
    )
    title = models.CharField(max_length=200, verbose_name="Modul nomi (masalan: HTML Asoslari)")
    description = models.TextField(blank=True, verbose_name="Modul tavsifi")
    order = models.PositiveIntegerField(default=1, verbose_name="Tartibi")
    lessons_count_display = models.PositiveIntegerField(default=12, verbose_name="Darslar soni (ko'rinishi)")
    topics_count_display = models.PositiveIntegerField(default=24, verbose_name="Mavzular soni (ko'rinishi)")

    class Meta:
        verbose_name = "Kurs Moduli"
        verbose_name_plural = "Kurs Modullari"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.course.title} / {self.title}"


class TopicStatus(models.TextChoices):
    LOCKED = 'LOCKED', 'Yopiq'
    NOT_STARTED = 'NOT_STARTED', 'Boshlanmagan'
    IN_PROGRESS = 'IN_PROGRESS', "O'rganilmoqda"
    COMPLETED = 'COMPLETED', 'Tugallangan'


class Topic(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='topics',
        verbose_name="Modul"
    )
    title = models.CharField(max_length=200, verbose_name="Mavzu nomi (masalan: Metateglar va Semantika)")
    order = models.PositiveIntegerField(default=1, verbose_name="Mavzu tartib raqami")
    lessons_count = models.PositiveIntegerField(default=4, verbose_name="Darslar soni")
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1.5, verbose_name="Davomiyligi (soat)")
    description = models.TextField(blank=True, verbose_name="Mavzu matni / konspekt")
    
    # Prezentatsiya (Figma dizayndagi slaydlar va PDF yuklash)
    presentation_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Dars Prezentatsiyasi sarlavhasi (masalan: Metateglar va SEO asoslari)"
    )
    presentation_file = models.FileField(
        upload_to='presentations/',
        null=True,
        blank=True,
        verbose_name="Taqdimot fayli (.pdf)"
    )
    slides_count = models.PositiveIntegerField(default=18, verbose_name="Jami slaydlar soni")
    
    # Manba kodi va qo'shimcha materiallar
    source_code_url = models.URLField(blank=True, null=True, verbose_name="Kod havolasi (GitHub)")
    source_code_snippet = models.TextField(blank=True, verbose_name="Namunaviy kod matni")
    video_url = models.URLField(blank=True, null=True, verbose_name="Video tushuntirish havolasi")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mavzu (Darslik)"
        verbose_name_plural = "Mavzular (Darsliklar)"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.module.title} -> {self.order}-Mavzu: {self.title}"


class TopicProgress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='topic_progresses',
        verbose_name="O'quvchi"
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='progresses',
        verbose_name="Mavzu"
    )
    status = models.CharField(
        max_length=20,
        choices=TopicStatus.choices,
        default=TopicStatus.NOT_STARTED,
        verbose_name="O'zlashtirish holati"
    )
    progress_percentage = models.PositiveIntegerField(default=0, verbose_name="O'zlashtirish foizi (0-100%)")
    slides_viewed = models.PositiveIntegerField(default=0, verbose_name="Ko'rilgan slaydlar soni")
    is_presentation_downloaded = models.BooleanField(default=False, verbose_name="PDF yuklab olinganmi")
    last_accessed = models.DateTimeField(auto_now=True, verbose_name="Oxirgi kirish vaqti")

    class Meta:
        verbose_name = "Mavzu o'zlashtirish progressi"
        verbose_name_plural = "Mavzular o'zlashtirish progresslari"
        unique_together = ('student', 'topic')

    def __str__(self):
        return f"{self.student.full_name} - {self.topic.title}: {self.progress_percentage}% ({self.get_status_display()})"
