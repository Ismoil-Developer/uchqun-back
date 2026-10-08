"""
Django settings for UCHQUN project.
UCHQUN - Yosh bilimdonlar uyi.
"""

from pathlib import Path
from datetime import timedelta
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'uchqun-super-secret-key-senior-architecture-2026')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    
    # Third party packages
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'django_filters',
    
    # Uchqun local apps
    'apps.accounts.apps.AccountsConfig',
    'apps.courses.apps.CoursesConfig',
    'apps.quizzes.apps.QuizzesConfig',
    'apps.assignments.apps.AssignmentsConfig',
    'apps.analytics.apps.AnalyticsConfig',
    'apps.communication.apps.CommunicationConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6}
    },
]

AUTH_USER_MODEL = 'accounts.User'

LANGUAGE_CODE = 'uz'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS & CSRF Headers
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://*.up.railway.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:3000',
    'http://localhost:5173',
]
if os.getenv('CSRF_TRUSTED_ORIGINS'):
    CSRF_TRUSTED_ORIGINS += os.getenv('CSRF_TRUSTED_ORIGINS').split(',')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
}

# Simple JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# OpenAPI / Swagger Documentation settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'UCHQUN API - Yosh bilimdonlar uyi',
    'DESCRIPTION': (
        "UCHQUN platformasi uchun REST API.\n"
        "O'quvchilar, ota-onalar nazorati, kurslar, mavzular, taqdimotlar (PDF), "
        "mini-testlar, amaliy topshiriqlar va guruh reyting tizimini to'liq qamrab oladi."
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'Auth', 'description': 'Tizimga kirish (Login) va Token yangilash'},
        {'name': 'Profile', 'description': 'Foydalanuvchi profili maʼlumotlari'},
        {'name': 'Courses', 'description': 'Kurslar va foydalanuvchiga ruxsat etilgan dasturlar'},
        {'name': 'Modules & Topics', 'description': 'Modullar, mavzular, taqdimotlar va oʻzlashtirish'},
        {'name': 'Quizzes', 'description': 'Mavzu boʻyicha mini-testlar va natijalar'},
        {'name': 'Assignments', 'description': 'Amaliy topshiriqlar va uy vazifalarini topshirish (rasm, kod, fayl)'},
        {'name': 'Leaderboard & Analytics', 'description': 'Guruh reytingi va oʻquvchi koʻrsatkichlari'},
        {'name': 'Parent Monitoring', 'description': 'Ota-onalar uchun farzandini nazorat qilish paneli'},
        {'name': 'Communication', 'description': 'Eʼlonlar va shaxsiy bildirishnomalar'},
    ],
}

# Jazzmin Admin Panel Customization
JAZZMIN_SETTINGS = {
    "site_title": "UCHQUN Admin",
    "site_header": "UCHQUN - Yosh bilimdonlar uyi",
    "site_brand": "UCHQUN LMS",
    "welcome_sign": "UCHQUN boshqaruv paneliga xush kelibsiz!",
    "copyright": "UCHQUN Startup © 2026",
    "search_model": ["accounts.User", "courses.Course", "accounts.Group"],
    "user_avatar": "avatar",
    "topmenu_links": [
        {"name": "Bosh sahifa", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Swagger Hujjatlari", "url": "/api/docs/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "accounts.User": "fas fa-user-circle",
        "accounts.Group": "fas fa-users",
        "accounts.StudentProfile": "fas fa-user-graduate",
        "accounts.ParentProfile": "fas fa-user-shield",
        "courses.Course": "fas fa-laptop-code",
        "courses.CourseEnrollment": "fas fa-user-check",
        "courses.Module": "fas fa-layer-group",
        "courses.Topic": "fas fa-book-reader",
        "courses.TopicProgress": "fas fa-chart-line",
        "quizzes.Quiz": "fas fa-question-circle",
        "quizzes.Question": "fas fa-list-ol",
        "quizzes.QuizAttempt": "fas fa-poll-h",
        "assignments.Assignment": "fas fa-tasks",
        "assignments.AssignmentSubmission": "fas fa-file-upload",
        "analytics.Attendance": "fas fa-calendar-check",
        "communication.Announcement": "fas fa-bullhorn",
        "communication.Notification": "fas fa-bell",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-file",
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-warning",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
