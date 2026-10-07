from django.urls import path
from .views import (
    CourseListView,
    CourseModulesView,
    ModuleTopicsView,
    TopicDetailView,
    UpdateTopicProgressView
)

urlpatterns = [
    path('courses/', CourseListView.as_view(), name='courses-list'),
    path('courses/<slug:slug>/modules/', CourseModulesView.as_view(), name='course-modules'),
    path('modules/<int:module_id>/topics/', ModuleTopicsView.as_view(), name='module-topics'),
    path('topics/<int:pk>/', TopicDetailView.as_view(), name='topic-detail'),
    path('topics/<int:pk>/progress/', UpdateTopicProgressView.as_view(), name='topic-progress-update'),
]
