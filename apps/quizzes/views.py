from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Quiz, Question, AnswerOption, QuizAttempt, StudentQuestionAnswer
from .serializers import QuizDetailSerializer, QuizSubmitSerializer
from apps.courses.models import Topic, TopicProgress, TopicStatus


class TopicQuizzesView(generics.ListAPIView):
    """
    Mavzuga tegishli mini-testlar ro'yxati (Figma 5-ekran).
    O'quvchining oldingi topshirgan javoblari (TO'G'RI / Qayta yechish) bilan birga qaytaradi.
    """
    serializer_class = QuizDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Quizzes'])
    def get_queryset(self):
        topic_id = self.kwargs.get('topic_id')
        return Quiz.objects.filter(topic_id=topic_id).prefetch_related('questions__options')


class QuizDetailView(generics.RetrieveAPIView):
    """
    Bitta test ma'lumotlari va savollari.
    """
    queryset = Quiz.objects.all()
    serializer_class = QuizDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Quizzes'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class QuizSubmitView(APIView):
    """
    Mini-test javoblarini topshirish va darhol natijani hisoblash.
    To'g'ri/noto'g'ri javoblarni ko'rsatadi, ball beradi va o'quvchi profiliga qo'shadi.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Quizzes'],
        request=QuizSubmitSerializer,
        responses={
            200: OpenApiResponse(description="Test natijasi muvaffaqiyatli hisoblandi")
        }
    )
    def post(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers_data = serializer.validated_data['answers']

        questions = {q.id: q for q in quiz.questions.all().prefetch_related('options')}
        total_questions = len(questions)
        correct_count = 0
        total_points_earned = 0
        results_breakdown = []

        with transaction.atomic():
            # Oldingi urinish sonini aniqlash
            previous_attempts_count = QuizAttempt.objects.filter(student=request.user, quiz=quiz).count()

            attempt = QuizAttempt.objects.create(
                student=request.user,
                quiz=quiz,
                attempt_number=previous_attempts_count + 1,
                total_questions=total_questions,
            )

            for item in answers_data:
                q_id = item['question_id']
                opt_id = item['selected_option_id']

                question = questions.get(q_id)
                if not question:
                    continue

                option = question.options.filter(id=opt_id).first()
                is_correct = bool(option and option.is_correct)

                if is_correct:
                    correct_count += 1
                    total_points_earned += question.points

                StudentQuestionAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_option=option,
                    is_correct=is_correct
                )

                results_breakdown.append({
                    'question_id': question.id,
                    'question_order': question.order,
                    'is_correct': is_correct,
                    'status_badge': "TO'G'RI" if is_correct else "NOTO'G'RI",
                    'explanation': question.explanation if not is_correct else "",
                })

            score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
            passed = score_percentage >= quiz.pass_percentage

            attempt.correct_answers = correct_count
            attempt.score_percentage = round(score_percentage, 2)
            attempt.points_earned = total_points_earned
            attempt.passed = passed
            attempt.save()

            # O'quvchi profiliga ball va test sonini qo'shish
            if hasattr(request.user, 'student_profile'):
                profile = request.user.student_profile
                profile.total_points += total_points_earned
                if passed:
                    profile.passed_quizzes_count += 1
                profile.save()

            # Mavzu progressini yangilash
            progress, _ = TopicProgress.objects.get_or_create(
                student=request.user,
                topic=quiz.topic
            )
            if passed and progress.progress_percentage < 50:
                progress.progress_percentage = 50
                progress.status = TopicStatus.IN_PROGRESS
                progress.save()

        return Response({
            'message': "Test tekshirildi",
            'attempt_id': attempt.id,
            'total_questions': total_questions,
            'correct_answers': correct_count,
            'score_percentage': attempt.score_percentage,
            'points_earned': total_points_earned,
            'passed': passed,
            'results': results_breakdown
        }, status=status.HTTP_200_OK)
