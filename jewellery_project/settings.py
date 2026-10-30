"""
Django settings for jewellery_project - works locally (.env + PostgreSQL) and on Render.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")          # local only; on Render real environment variables are used
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


def _env(name, default=None):
    return os.environ.get(name, default)


# =========================
# CORE
# =========================

SECRET_KEY = _env("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("Set SECRET_KEY (in .env locally, or in Render environment).")

# Local: DEBUG=True in .env.  Render: DEBUG=False (set in render.yaml).
DEBUG = _env("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = []

RENDER_HOST = _env("RENDER_EXTERNAL_HOSTNAME")
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)
    CSRF_TRUSTED_ORIGINS.append("https://" + RENDER_HOST)

# Your own domain later:  EXTRA_HOSTS=www.example.com,example.com
for _host in (_env("EXTRA_HOSTS", "") or "").split(","):
    _host = _host.strip()
    if _host:
        ALLOWED_HOSTS.append(_host)
        CSRF_TRUSTED_ORIGINS.append("https://" + _host)

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# =========================
# APPS / MIDDLEWARE
# =========================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',          # <- the comma was missing here before
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jewellery_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop.context_processors.user_role',
            ],
        },
    },
]

WSGI_APPLICATION = 'jewellery_project.wsgi.application'


# =========================
# DATABASE
# Render gives DATABASE_URL.  Locally the DB_* values from .env are used.
# =========================

if _env("DATABASE_URL"):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=60, ssl_require=not DEBUG)
    }
else:
    if not _env("DB_NAME") or not _env("DB_USER"):
        raise ImproperlyConfigured(
            "Set DATABASE_URL (Render) or DB_NAME, DB_USER and DB_PASSWORD in the .env file."
        )
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': _env('DB_NAME'),
            'USER': _env('DB_USER'),
            'PASSWORD': _env('DB_PASSWORD', ''),
            'HOST': _env('DB_HOST', 'localhost'),
            'PORT': (_env('DB_PORT', '5432') or '5432').split()[0],
            'CONN_MAX_AGE': 60,
            'OPTIONS': {'sslmode': _env('DB_SSLMODE', 'prefer')},
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# =========================
# STATIC FILES (served by WhiteNoise)
# =========================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}


# =========================
# MEDIA (uploaded product images)
# Local: media/ folder.  Render: Cloudinary (set CLOUDINARY_URL), because
# Render's disk is erased on every deploy.
# =========================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

if _env("CLOUDINARY_URL"):
    INSTALLED_APPS = ['cloudinary_storage'] + INSTALLED_APPS + ['cloudinary']
    STORAGES["default"] = {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"}


# =========================
# EMAIL - GMAIL
# NOTE: Render's FREE plan blocks SMTP ports, so emails (order confirmation,
# OTP, forgot password) will fail there unless you use a paid plan or an
# email service with an HTTP API.
# =========================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10

EMAIL_HOST_USER = _env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = _env("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = f"NIKI Jewels <{EMAIL_HOST_USER}>"


# =========================
# OTP SETTINGS
# =========================

OTP_TTL_SECONDS = 300
OTP_MAX_ATTEMPTS = 5

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
