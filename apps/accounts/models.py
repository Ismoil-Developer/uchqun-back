from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Foydalanuvchini email orqali yaratish menejeri."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("E-mail kiritilishi shart")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser is_staff=True boʻlishi kerak.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser is_superuser=True boʻlishi kerak.')

        return self.create_user(email, password, **extra_fields)


class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrator'
    TEACHER = 'TEACHER', "O'qituvchi / Mentor"
    STUDENT = 'STUDENT', "O'quvchi / Bilimdon"
    PARENT = 'PARENT', 'Ota-ona'


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="E-mail")
    first_name = models.CharField(max_length=150, verbose_name="Ism")
    last_name = models.CharField(max_length=150, verbose_name="Familiya")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon raqam")
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
        verbose_name="Rol"
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Profil rasmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ['-id']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Group(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Guruh nomi (masalan: F-2401)")
    description = models.TextField(blank=True, verbose_name="Guruh haqida tavsif")
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': UserRole.TEACHER},
        related_name='mentored_groups',
        verbose_name="Mentor / O'qituvchi"
    )
    telegram_group_url = models.URLField(blank=True, null=True, verbose_name="Telegram guruhi havolasi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ochilgan vaqti")

    class Meta:
        verbose_name = "O'quv guruhi"
        verbose_name_plural = "O'quv guruhlari"
        ordering = ['name']

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name="O'quvchi foydalanuvchisi"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name="Guruh"
    )
    parent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': UserRole.PARENT},
        related_name='children',
        verbose_name="Biriktirilgan Ota-ona"
    )
    total_points = models.PositiveIntegerField(default=0, verbose_name="Umumiy to'plangan ballar")
    completed_tasks_count = models.PositiveIntegerField(default=0, verbose_name="Muvaffaqiyatli topshirilgan vazifalar")
    passed_quizzes_count = models.PositiveIntegerField(default=0, verbose_name="Yechilgan testlar soni")
    attendance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.0,
        verbose_name="Davomat ko'rsatkichi (%)"
    )
    bio = models.TextField(blank=True, verbose_name="O'quvchi haqida qisqacha")

    class Meta:
        verbose_name = "O'quvchi profili"
        verbose_name_plural = "O'quvchilar profillari"

    def __str__(self):
        group_name = self.group.name if self.group else "Guruhsiz"
        return f"{self.user.full_name} [{group_name}]"


class ParentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='parent_profile',
        verbose_name="Ota-ona foydalanuvchisi"
    )
    telegram_chat_id = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="Telegram Chat ID (bildirishnomalar uchun)"
    )
    receive_notifications = models.BooleanField(default=True, verbose_name="Bildirishnomalarni qabul qilish")

    class Meta:
        verbose_name = "Ota-ona profili"
        verbose_name_plural = "Ota-onalar profillari"

    def __str__(self):
        return f"Ota-ona: {self.user.full_name}"
