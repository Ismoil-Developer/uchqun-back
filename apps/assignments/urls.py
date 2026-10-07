from django.urls import path
from .views import (
    DailyFeaturedAssignmentView,
    TopicAssignmentView,
    AssignmentDetailView,
    SubmitAssignmentView,
    MySubmissionsListView,
    GradeSubmissionView
)

urlpatterns = [
    path('assignments/daily-featured/', DailyFeaturedAssignmentView.as_view(), name='assignment-daily-featured'),
    path('topics/<int:topic_id>/assignment/', TopicAssignmentView.as_view(), name='topic-assignment'),
    path('assignments/<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('assignments/<int:pk>/submit/', SubmitAssignmentView.as_view(), name='assignment-submit'),
    path('assignments/my-submissions/', MySubmissionsListView.as_view(), name='my-submissions'),
    path('submissions/<int:pk>/grade/', GradeSubmissionView.as_view(), name='grade-submission'),
]
