"""
Django settings for Start-Up Sahay Portal project.
Built for Start-Up Sahay Private Limited — Service Inquiry & Lead Maturity Portal.
"""
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from django.contrib.messages import constants as messages_constants
from config.env import load_env_file, get_bool_env, get_int_env, get_list_env

# Base Directory: root of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment variables from .env file
load_env_file(BASE_DIR / '.env')

# Security: Secret Key
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    # Safe default strictly for development; production enforces explicit SECRET_KEY
    if os.environ.get('DEBUG', 'True').lower() in ('false', '0', 'no'):
        raise ImproperlyConfigured("SECRET_KEY environment variable must be set in production mode.")
    SECRET_KEY = 'django-insecure-startup-sahay-local-development-secret-key-replace-in-prod'

# Debug flag
DEBUG = get_bool_env('DEBUG', default=True)

# Allowed hosts
ALLOWED_HOSTS = get_list_env('ALLOWED_HOSTS', default='127.0.0.1,localhost,testserver,.onrender.com,.ngrok-free.app,.ngrok.io,.loca.lt')
if DEBUG and '*' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('*')

# CSRF Trusted Origins for tunneling (ngrok, localtunnel), Render, and remote testing
CSRF_TRUSTED_ORIGINS = get_list_env(
    'CSRF_TRUSTED_ORIGINS',
    default='https://*.onrender.com,https://*.ngrok-free.app,https://*.ngrok-free.dev,https://*.ngrok.io,https://*.loca.lt,http://127.0.0.1,http://localhost'
)

# Reverse proxy SSL header (essential for Render, Heroku, AWS, etc.)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local application modules
    'inquiries.apps.InquiriesConfig',
    'dashboard.apps.DashboardConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
# Local SQLite by default for development and assignment demonstration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise storage for production static files compression and caching
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = 'dashboard:login'
LOGIN_REDIRECT_URL = 'dashboard:overview'
LOGOUT_REDIRECT_URL = 'dashboard:login'

# Session and Cookie Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Production security controls
if not DEBUG:
    SESSION_COOKIE_SECURE = get_bool_env('SESSION_COOKIE_SECURE', False)
    CSRF_COOKIE_SECURE = get_bool_env('CSRF_COOKIE_SECURE', False)
    SECURE_SSL_REDIRECT = get_bool_env('SECURE_SSL_REDIRECT', False)
    SECURE_HSTS_SECONDS = get_int_env('SECURE_HSTS_SECONDS', 0)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Messages framework tag mapping to Bootstrap 5 alert classes
MESSAGE_TAGS = {
    messages_constants.DEBUG: 'secondary',
    messages_constants.INFO: 'info',
    messages_constants.SUCCESS: 'success',
    messages_constants.WARNING: 'warning',
    messages_constants.ERROR: 'danger',
}

# Rate Limiting configuration for inquiry submissions
INQUIRY_RATE_LIMIT_MAX_REQUESTS = get_int_env('INQUIRY_RATE_LIMIT_MAX_REQUESTS', 5)
INQUIRY_RATE_LIMIT_WINDOW_SECONDS = get_int_env('INQUIRY_RATE_LIMIT_WINDOW_SECONDS', 600)
