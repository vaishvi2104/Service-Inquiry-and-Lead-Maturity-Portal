"""
Django settings for Start-Up Sahay Portal project.
Built for Start-Up Sahay Private Limited — Service Inquiry & Lead Maturity Portal.
"""
import os
import sys
import urllib.parse
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from django.contrib.messages import constants as messages_constants
from config.env import load_env_file, get_bool_env, get_int_env, get_list_env

# Base Directory: root of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment variables from .env file
load_env_file(BASE_DIR / '.env')

# Check if currently running automated test suite
IS_TESTING = 'test' in sys.argv

# Debug flag: Defaults strictly to False for security
DEBUG = get_bool_env('DEBUG', default=False)

# Security: Secret Key
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if not DEBUG and not IS_TESTING:
        raise ImproperlyConfigured("SECRET_KEY environment variable must be set in production mode.")
    SECRET_KEY = 'django-insecure-startup-sahay-local-development-secret-key-replace-in-prod'

# Allowed hosts: Strictly configured via environment variables
default_hosts = '127.0.0.1,localhost,testserver' if (DEBUG or IS_TESTING) else ''
ALLOWED_HOSTS = get_list_env('ALLOWED_HOSTS', default=default_hosts)

# CSRF Trusted Origins: Explicitly configured, no wildcard testing origins
default_csrf = 'http://127.0.0.1,http://localhost' if (DEBUG or IS_TESTING) else ''
CSRF_TRUSTED_ORIGINS = get_list_env('CSRF_TRUSTED_ORIGINS', default=default_csrf)

# Reverse proxy configurations
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_FOR = get_bool_env('USE_X_FORWARDED_FOR', default=False)

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


# Database Configuration
def _configure_database() -> dict:
    """Configure database settings dynamically supporting PostgreSQL & SQLite."""
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        parsed = urllib.parse.urlparse(database_url)
        scheme = parsed.scheme.lower()
        if scheme in ('sqlite', 'sqlite3'):
            path = parsed.path
            if path.startswith('///'):
                db_path = Path(path[3:])
            elif path.startswith('/'):
                db_path = BASE_DIR / path[1:]
            elif not path or path == ':memory:':
                return {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}
            else:
                db_path = BASE_DIR / path
            return {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': db_path,
            }
        elif scheme in ('postgres', 'postgresql', 'pgsql'):
            return {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': parsed.path.lstrip('/'),
                'USER': parsed.username or '',
                'PASSWORD': urllib.parse.unquote(parsed.password or ''),
                'HOST': parsed.hostname or '',
                'PORT': str(parsed.port or 5432),
            }

    # Fallback to discrete parameters or default SQLite
    engine = os.environ.get('DATABASE_ENGINE', 'django.db.backends.sqlite3')
    db_name = os.environ.get('DATABASE_NAME')
    if engine == 'django.db.backends.sqlite3':
        db_path = BASE_DIR / (db_name or 'db.sqlite3')
        return {
            'ENGINE': engine,
            'NAME': db_path,
        }
    return {
        'ENGINE': engine,
        'NAME': db_name or 'startupsahay_db',
        'USER': os.environ.get('DATABASE_USER', ''),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', ''),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    }


DATABASES = {
    'default': _configure_database()
}


# Shared Caching Backend (Supports Redis or LocMem fallback)
def _configure_cache() -> dict:
    redis_url = os.environ.get('REDIS_URL') or os.environ.get('CACHE_URL')
    if redis_url:
        return {
            'default': {
                'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                'LOCATION': redis_url,
            }
        }
    return {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'startupsahay-cache-default',
        }
    }


CACHES = _configure_cache()


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

# Fast password hasher for test execution speed
if IS_TESTING:
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
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

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

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
    SESSION_COOKIE_SECURE = get_bool_env('SESSION_COOKIE_SECURE', default=not IS_TESTING)
    CSRF_COOKIE_SECURE = get_bool_env('CSRF_COOKIE_SECURE', default=not IS_TESTING)
    SECURE_SSL_REDIRECT = get_bool_env('SECURE_SSL_REDIRECT', default=not IS_TESTING)
    SECURE_HSTS_SECONDS = get_int_env('SECURE_HSTS_SECONDS', default=31536000 if not IS_TESTING else 0)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = get_bool_env('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=not IS_TESTING)
    SECURE_HSTS_PRELOAD = get_bool_env('SECURE_HSTS_PRELOAD', default=not IS_TESTING)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
else:
    SESSION_COOKIE_SECURE = get_bool_env('SESSION_COOKIE_SECURE', default=False)
    CSRF_COOKIE_SECURE = get_bool_env('CSRF_COOKIE_SECURE', default=False)
    SECURE_SSL_REDIRECT = get_bool_env('SECURE_SSL_REDIRECT', default=False)
    SECURE_HSTS_SECONDS = get_int_env('SECURE_HSTS_SECONDS', default=0)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Messages framework tag mapping to Bootstrap alert classes
MESSAGE_TAGS = {
    messages_constants.DEBUG: 'secondary',
    messages_constants.INFO: 'info',
    messages_constants.SUCCESS: 'success',
    messages_constants.WARNING: 'warning',
    messages_constants.ERROR: 'danger',
}

# Rate Limiting configuration for inquiry submissions
INQUIRY_RATE_LIMIT_MAX_REQUESTS = get_int_env('INQUIRY_RATE_LIMIT_MAX_REQUESTS', default=5)
INQUIRY_RATE_LIMIT_WINDOW_SECONDS = get_int_env('INQUIRY_RATE_LIMIT_WINDOW_SECONDS', default=600)

# Login brute-force protection
LOGIN_MAX_ATTEMPTS = get_int_env('LOGIN_MAX_ATTEMPTS', default=5)
LOGIN_LOCKOUT_SECONDS = get_int_env('LOGIN_LOCKOUT_SECONDS', default=300)
