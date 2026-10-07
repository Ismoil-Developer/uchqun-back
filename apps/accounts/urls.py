from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, UserProfileView, ChangePasswordView, GroupListView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/me/', UserProfileView.as_view(), name='user-profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('groups/', GroupListView.as_view(), name='groups-list'),
]
