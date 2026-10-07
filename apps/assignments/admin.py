from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Assignment, AssignmentSubmission, SubmissionStatus


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic_name', 'max_score', 'deadline_text', 'is_daily_featured', 'created_at')
    list_filter = ('is_daily_featured', 'topic__module__course')
    search_fields = ('title', 'description', 'topic__title')
    autocomplete_fields = ('topic',)

    @admin.display(description="Mavzu")
    def topic_name(self, obj):
        return f"{obj.topic.order}-Mavzu: {obj.topic.title}"


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'assignment', 'status_badge', 'score_display',
        'screenshot_preview', 'github_url_display', 'submitted_at', 'graded_at'
    )
    list_filter = ('status', 'assignment__topic__module__course')
    search_fields = (
        'student__email', 'student__first_name', 'student__last_name',
        'assignment__title', 'teacher_feedback'
    )
    readonly_fields = ('submitted_at', 'screenshot_large_preview')
    actions = ['approve_with_max_score', 'mark_rejected']

    fieldsets = (
        ("Topshiriq va O'quvchi", {
            'fields': ('assignment', 'student', 'submitted_at')
        }),
        ("O'quvchi yuborgan ish", {
            'fields': (
                'screenshot', 'screenshot_large_preview', 'submission_file',
                'github_url', 'code_text', 'student_comment'
            )
        }),
        ("O'qituvchi bahosi va taqrizi", {
            'fields': ('status', 'score', 'teacher_feedback', 'graded_by', 'graded_at')
        }),
    )

    @admin.display(description="Holat")
    def status_badge(self, obj):
        colors = {
            SubmissionStatus.APPROVED: '#38A169',
            SubmissionStatus.PENDING: '#ED8936',
            SubmissionStatus.REJECTED: '#E53E3E',
        }
        color = colors.get(obj.status, '#718096')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )

    @admin.display(description="Ball")
    def score_display(self, obj):
        if obj.score is not None:
            return format_html('<b>{}/{}</b>', obj.score, obj.assignment.max_score)
        return "-"

    @admin.display(description="Rasm")
    def screenshot_preview(self, obj):
        if obj.screenshot:
            return format_html('<img src="{}" style="width: 45px; height: 35px; object-fit: cover; border-radius: 4px;" />', obj.screenshot.url)
        return "-"

    @admin.display(description="To'liq rasm ko'rinishi")
    def screenshot_large_preview(self, obj):
        if obj.screenshot:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="max-width: 400px; max-height: 300px; border-radius: 6px;" /></a>', obj.screenshot.url, obj.screenshot.url)
        return "Rasm yuklanmagan"

    @admin.display(description="GitHub")
    def github_url_display(self, obj):
        if obj.github_url:
            return format_html('<a href="{}" target="_blank" rel="noopener">Havolani ochish ↗</a>', obj.github_url)
        return "-"

    @admin.action(description="Maksimal ball bilan qabul qilish (100 ball)")
    def approve_with_max_score(self, request, queryset):
        for sub in queryset:
            sub.status = SubmissionStatus.APPROVED
            sub.score = sub.assignment.max_score
            sub.graded_by = request.user
            sub.graded_at = timezone.now()
            sub.save()
            
            # O'quvchi profiliga ball qo'shish
            if hasattr(sub.student, 'student_profile'):
                profile = sub.student.student_profile
                profile.total_points += sub.score
                profile.completed_tasks_count += 1
                profile.save()

    @admin.action(description="Qayta ishlashga qaytarish")
    def mark_rejected(self, request, queryset):
        queryset.update(
            status=SubmissionStatus.REJECTED,
            graded_by=request.user,
            graded_at=timezone.now()
        )
