from rest_framework import serializers
from .models import Quiz, Question, AnswerOption, QuizAttempt, StudentQuestionAnswer


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ['id', 'order', 'text']


class QuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True, read_only=True)
    user_status = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'order', 'text', 'points', 'options', 'user_status']

    def get_user_status(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user or not user.is_authenticated:
            return None
        last_answer = StudentQuestionAnswer.objects.filter(
            attempt__student=user,
            question=obj
        ).order_by('-attempt__completed_at').first()

        if last_answer:
            return {
                'has_answered': True,
                'selected_option_id': last_answer.selected_option_id,
                'selected_option_text': last_answer.selected_option.text if last_answer.selected_option else None,
                'is_correct': last_answer.is_correct,
                'status_badge': "TO'G'RI" if last_answer.is_correct else "NOTO'G'RI",
                'action_label': "Qayta yechish"
            }
        return {
            'has_answered': False,
            'selected_option_id': None,
            'selected_option_text': None,
            'is_correct': None,
            'status_badge': None,
            'action_label': "Yechishni boshlash"
        }


class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    questions_count = serializers.IntegerField(source='questions.count', read_only=True)
    last_attempt = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            'id', 'topic', 'title', 'description',
            'pass_percentage', 'questions_count', 'questions', 'last_attempt'
        ]

    def get_last_attempt(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user or not user.is_authenticated:
            return None
        attempt = QuizAttempt.objects.filter(student=user, quiz=obj).order_by('-completed_at').first()
        if attempt:
            return {
                'id': attempt.id,
                'score_percentage': float(attempt.score_percentage),
                'correct_answers': attempt.correct_answers,
                'total_questions': attempt.total_questions,
                'points_earned': attempt.points_earned,
                'passed': attempt.passed,
                'completed_at': attempt.completed_at
            }
        return None


class SubmitAnswerItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=True)
    selected_option_id = serializers.IntegerField(required=True)


class QuizSubmitSerializer(serializers.Serializer):
    answers = SubmitAnswerItemSerializer(many=True, required=True)
