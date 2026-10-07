from django.contrib import admin
from django.utils.html import format_html
from .models import Quiz, Question, AnswerOption, QuizAttempt, StudentQuestionAnswer


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 4
    fields = ('order', 'text', 'is_correct')


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ('order', 'text', 'points', 'explanation')
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic_name', 'questions_count', 'pass_percentage', 'created_at')
    search_fields = ('title', 'topic__title')
    list_filter = ('topic__module__course',)
    inlines = [QuestionInline]

    @admin.display(description="Mavzu")
    def topic_name(self, obj):
        return f"{obj.topic.order}-Mavzu: {obj.topic.title}"

    @admin.display(description="Savollar soni")
    def questions_count(self, obj):
        return obj.questions.count()


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('order', 'text', 'quiz', 'points', 'options_count')
    list_filter = ('quiz__topic__module__course', 'quiz')
    search_fields = ('text', 'quiz__title')
    inlines = [AnswerOptionInline]

    @admin.display(description="Variantlar soni")
    def options_count(self, obj):
        return obj.options.count()


class StudentAnswerInline(admin.TabularInline):
    model = StudentQuestionAnswer
    extra = 0
    readonly_fields = ('question', 'selected_option', 'is_correct')
    can_delete = False


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'quiz', 'score_percentage_badge', 'correct_answers',
        'total_questions', 'points_earned', 'passed_badge', 'completed_at'
    )
    list_filter = ('passed', 'quiz__topic__module__course')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'quiz__title')
    inlines = [StudentAnswerInline]

    @admin.display(description="Natija")
    def score_percentage_badge(self, obj):
        color = '#38A169' if obj.passed else '#E53E3E'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            obj.score_percentage
        )

    @admin.display(description="Holat")
    def passed_badge(self, obj):
        if obj.passed:
            return format_html('<span style="color: #38A169; font-weight: bold;">✓ Muvaffaqiyatli</span>')
        return format_html('<span style="color: #E53E3E; font-weight: bold;">✗ Oʻtolmadi</span>')
