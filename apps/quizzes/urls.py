from django.urls import path
from .views import TopicQuizzesView, QuizDetailView, QuizSubmitView

urlpatterns = [
    path('topics/<int:topic_id>/quizzes/', TopicQuizzesView.as_view(), name='topic-quizzes'),
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<int:pk>/submit/', QuizSubmitView.as_view(), name='quiz-submit'),
]
