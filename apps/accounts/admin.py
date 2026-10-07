from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import User, UserRole, Group, StudentProfile, ParentProfile
from apps.courses.models import CourseEnrollment


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    fk_name = 'user'
    can_delete = False
    verbose_name = "O'quvchi qo'shimcha ma'lumotlari"
    verbose_name_plural = "O'quvchi qo'shimcha ma'lumotlari"
    extra = 0
    fields = ('group', 'parent', 'total_points', 'attendance_rate', 'bio')


class CourseEnrollmentInline(admin.TabularInline):
    model = CourseEnrollment
    fk_name = 'student'
    extra = 1
    verbose_name = "Kursga ruxsat (Enrollment)"
    verbose_name_plural = "Kurslarga ruxsatlar (Qaysi kurs ochiqligi)"
    fields = ('course', 'status', 'progress_percentage')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role_badge', 'phone_number', 'get_group', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)
    
    fieldsets = (
        ("Asosiy hisob ma'lumotlari", {
            'fields': ('email', 'password')
        }),
        ("Shaxsiy ma'lumotlar", {
            'fields': ('first_name', 'last_name', 'phone_number', 'role', 'avatar')
        }),
        ('Ruxsatlar va status', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ("Muhim sanalar", {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        ("Yangi foydalanuvchi / o'quvchi qo'shish", {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'role', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'last_login')
    inlines = [StudentProfileInline, CourseEnrollmentInline]

    @admin.display(description="Rol")
    def role_badge(self, obj):
        colors = {
            UserRole.ADMIN: '#E53E3E',
            UserRole.TEACHER: '#3182CE',
            UserRole.STUDENT: '#38A169',
            UserRole.PARENT: '#D69E2E',
        }
        color = colors.get(obj.role, '#718096')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_role_display()
        )

    @admin.display(description="Guruhi")
    def get_group(self, obj):
        if hasattr(obj, 'student_profile') and obj.student_profile.group:
            return obj.student_profile.group.name
        return "-"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'students_count', 'created_at')
    search_fields = ('name', 'teacher__first_name', 'teacher__last_name')
    list_filter = ('teacher', 'created_at')

    @admin.display(description="O'quvchilar soni")
    def students_count(self, obj):
        return obj.students.count()


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'parent', 'total_points', 'attendance_rate', 'completed_tasks_count')
    list_filter = ('group', 'attendance_rate')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'group__name')
    autocomplete_fields = ('user', 'group', 'parent')


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telegram_chat_id', 'receive_notifications', 'children_list')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')

    @admin.display(description="Farzandlari")
    def children_list(self, obj):
        children = obj.user.children.all()
        return ", ".join([c.user.full_name for c in children]) or "Biriktirilmagan"
