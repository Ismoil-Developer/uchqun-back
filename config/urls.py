"""
URL configuration for UCHQUN LMS project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    # Boshqaruv paneli (Admin)
    path('admin/', admin.site.urls),

    # OpenAPI Schema va Swagger Hujjatlari (Frontend & Mobile uchun)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # REST API v1
    path('api/v1/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.courses.urls')),
    path('api/v1/', include('apps.quizzes.urls')),
    path('api/v1/', include('apps.assignments.urls')),
    path('api/v1/', include('apps.analytics.urls')),
    path('api/v1/', include('apps.communication.urls')),
]

# Media fayllarni har doim serve qilish (WhiteNoise static fayllarni o'z zimmasiga oladi)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "UCHQUN - Yosh bilimdonlar uyi"
admin.site.site_title = "UCHQUN LMS Admin"
admin.site.index_title = "O'quv tizimini boshqarish markazi"
