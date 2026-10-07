from django.urls import path
from .views import (
    GroupLeaderboardView,
    MyAttendanceView,
    ParentChildrenListView,
    ParentChildDashboardView
)

urlpatterns = [
    path('analytics/leaderboard/', GroupLeaderboardView.as_view(), name='group-leaderboard'),
    path('analytics/my-attendance/', MyAttendanceView.as_view(), name='my-attendance'),
    path('parent/my-children/', ParentChildrenListView.as_view(), name='parent-children'),
    path('parent/child-dashboard/<int:student_id>/', ParentChildDashboardView.as_view(), name='parent-child-dashboard'),
]
