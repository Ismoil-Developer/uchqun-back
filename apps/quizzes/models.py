from django.db import models
from django.conf import settings
from apps.courses.models import Topic


class Quiz(models.Model):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name="Mavzu"
    )
    title = models.CharField(max_length=200, verbose_name="Mini-test sarlavhasi")
    description = models.TextField(blank=True, verbose_name="Qisqa izoh")
    pass_percentage = models.PositiveIntegerField(default=60, verbose_name="O'tish foizi (%)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mini-test"
        verbose_name_plural = "Mini-testlar"
        ordering = ['id']

    def __str__(self):
        return f"{self.topic.title} - {self.title}"

    @property
    def questions_count(self):
        return self.questions.count()


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Test"
    )
    order = models.PositiveIntegerField(default=1, verbose_name="Savol tartibi (#1, #2...)")
    text = models.CharField(max_length=500, verbose_name="Savol matni")
    explanation = models.TextField(blank=True, verbose_name="To'g'ri javob izohi")
    points = models.PositiveIntegerField(default=10, verbose_name="Beriladigan ball")

    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"
        ordering = ['order', 'id']

    def __str__(self):
        return f"Savol #{self.order}: {self.text[:50]}"


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="Savol"
    )
    order = models.PositiveIntegerField(default=1, verbose_name="Tartibi")
    text = models.CharField(max_length=300, verbose_name="Variant matni (masalan: A) UTF-8)")
    is_correct = models.BooleanField(default=False, verbose_name="To'g'ri variantmi")

    class Meta:
        verbose_name = "Javob varianti"
        verbose_name_plural = "Javob variantlari"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.text} {'(Toʻgʻri)' if self.is_correct else ''}"


class QuizAttempt(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name="O'quvchi"
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name="Test"
    )
    attempt_number = models.PositiveIntegerField(default=1, verbose_name="Urinish tartibi")
    total_questions = models.PositiveIntegerField(default=0, verbose_name="Jami savollar")
    correct_answers = models.PositiveIntegerField(default=0, verbose_name="To'g'ri javoblar")
    score_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="To'plangan foiz")
    points_earned = models.PositiveIntegerField(default=0, verbose_name="Qo'lga kiritilgan ball")
    passed = models.BooleanField(default=False, verbose_name="O'tdimi")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Yechilgan sana")

    class Meta:
        verbose_name = "Test topshirish natijasi"
        verbose_name_plural = "Test topshirish natijalari"
        ordering = ['-completed_at']

    def __str__(self):
        status = "Oʻtdi" if self.passed else "Oʻtolmadi"
        return f"{self.student.full_name} - {self.quiz.title}: {self.score_percentage}% ({status})"


class StudentQuestionAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = "O'quvchi savol javobi"
        verbose_name_plural = "O'quvchi savol javoblari"
