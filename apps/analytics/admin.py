from django.contrib import admin
from django.utils.html import format_html
from .models import Attendance, AttendanceStatus, AchievementBadge, StudentBadge


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'student', 'group', 'status_badge', 'topic', 'teacher_note', 'recorded_by')
    list_filter = ('status', 'group', 'date')
    search_fields = ('student__first_name', 'student__last_name', 'student__email', 'group__name')
    date_hierarchy = 'date'
    actions = ['mark_present', 'mark_absent']

    @admin.display(description="Davomat holati")
    def status_badge(self, obj):
        colors = {
            AttendanceStatus.PRESENT: '#38A169',
            AttendanceStatus.ABSENT: '#E53E3E',
            AttendanceStatus.EXCUSED: '#3182CE',
            AttendanceStatus.LATE: '#ED8936',
        }
        color = colors.get(obj.status, '#718096')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )

    @admin.action(description="Tanlanganlarni 'Qatnashdi (Kelgan)' deb belgilash")
    def mark_present(self, request, queryset):
        queryset.update(status=AttendanceStatus.PRESENT, recorded_by=request.user)

    @admin.action(description="Tanlanganlarni 'Qatnashmadi (Kelmagan)' deb belgilash")
    def mark_absent(self, request, queryset):
        queryset.update(status=AttendanceStatus.ABSENT, recorded_by=request.user)


@admin.register(AchievementBadge)
class AchievementBadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_required', 'icon')
    search_fields = ('name', 'description')


@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    list_display = ('student', 'badge', 'awarded_at')
    list_filter = ('badge', 'awarded_at')
    search_fields = ('student__first_name', 'student__last_name', 'student__email')
