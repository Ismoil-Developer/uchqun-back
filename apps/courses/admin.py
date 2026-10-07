from django.contrib import admin
from django.utils.html import format_html
from .models import Course, CourseEnrollment, Module, Topic, TopicProgress, EnrollmentStatus, TopicStatus


class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1
    fields = ('title', 'order', 'lessons_count_display', 'topics_count_display', 'description')


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1
    fields = ('order', 'title', 'lessons_count', 'duration_hours', 'presentation_title', 'slides_count')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order', 'modules_count', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]

    @admin.display(description="Modullar soni")
    def modules_count(self, obj):
        return obj.modules.count()


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status_badge', 'progress_percentage', 'enrolled_at', 'completed_at')
    list_filter = ('status', 'course')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'course__title')
    autocomplete_fields = ('student', 'course')
    actions = ['activate_enrollment', 'waitlist_enrollment', 'complete_enrollment']

    @admin.display(description="Holati")
    def status_badge(self, obj):
        colors = {
            EnrollmentStatus.OPEN: '#38A169',      # Yashil (OCHIQ)
            EnrollmentStatus.WAITING: '#ED8936',   # Sariq/Olovrang (Navbat kutilmoqda)
            EnrollmentStatus.COMPLETED: '#3182CE'  # Ko'k (Yakunlangan)
        }
        color = colors.get(obj.status, '#718096')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )

    @admin.action(description="Tanlanganlarni 'Ochiq' holatiga o'tkazish")
    def activate_enrollment(self, request, queryset):
        queryset.update(status=EnrollmentStatus.OPEN)

    @admin.action(description="Tanlanganlarni 'Yopiq (Navbat kutilmoqda)' holatiga o'tkazish")
    def waitlist_enrollment(self, request, queryset):
        queryset.update(status=EnrollmentStatus.WAITING)

    @admin.action(description="Tanlanganlarni 'Yakunlangan' holatiga o'tkazish")
    def complete_enrollment(self, request, queryset):
        queryset.update(status=EnrollmentStatus.COMPLETED)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'topics_count', 'lessons_count_display')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    inlines = [TopicInline]

    @admin.display(description="Mavzular soni")
    def topics_count(self, obj):
        return obj.topics.count()


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = (
        'order', 'title', 'module_course', 'lessons_count',
        'duration_hours', 'presentation_title', 'slides_count', 'has_pdf'
    )
    list_filter = ('module__course', 'module')
    search_fields = ('title', 'module__title', 'presentation_title')
    autocomplete_fields = ('module',)

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('module', 'order', 'title', 'lessons_count', 'duration_hours', 'description')
        }),
        ("Dars Prezentatsiyasi (PDF & Slaydlar)", {
            'fields': ('presentation_title', 'presentation_file', 'slides_count'),
            'description': "O'quvchi darsni o'qishi va PDF shaklida yuklab olishi uchun materiallar."
        }),
        ("Dastur kodi va video", {
            'fields': ('source_code_url', 'source_code_snippet', 'video_url'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description="Kurs va Modul")
    def module_course(self, obj):
        return f"{obj.module.course.title} -> {obj.module.title}"

    @admin.display(description="PDF bormi", boolean=True)
    def has_pdf(self, obj):
        return bool(obj.presentation_file)


@admin.register(TopicProgress)
class TopicProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'topic', 'status_badge', 'progress_percentage', 'slides_viewed', 'last_accessed')
    list_filter = ('status', 'topic__module__course')
    search_fields = ('student__email', 'student__first_name', 'topic__title')

    @admin.display(description="Holati")
    def status_badge(self, obj):
        colors = {
            TopicStatus.COMPLETED: '#38A169',
            TopicStatus.IN_PROGRESS: '#ED8936',
            TopicStatus.NOT_STARTED: '#A0AEC0',
            TopicStatus.LOCKED: '#E53E3E',
        }
        color = colors.get(obj.status, '#718096')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
