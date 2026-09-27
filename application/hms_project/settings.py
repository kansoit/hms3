"""
Django settings for hms3 (Hospital Management System - Argentina & Delphix Demo)
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- CONFIGURACIÓN DE ENTORNO Y SEGURIDAD ---
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'hms3-default-development-secret-key-replace-in-env')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

allowed_hosts_raw = os.getenv('ALLOWED_HOSTS', '*')
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_raw.split(',') if h.strip()] or ['*']

# Identificador de entorno: 'prod' o 'test'
HMS_ENV = os.getenv('HMS_ENV', 'prod').lower()
HMS_COUNTRY = os.getenv('HMS_COUNTRY', 'AR').upper()

# --- AISLAMIENTO DE SESIONES Y COOKIES ---
# Esto previene que al abrir Producción (8012) y Test (8013) en el mismo navegador,
# las cookies se pisen entre sí.
SESSION_COOKIE_NAME = f'hms3_session_{HMS_ENV}'
CSRF_COOKIE_NAME = f'hms3_csrf_{HMS_ENV}'
SESSION_COOKIE_AGE = 86400  # 1 día
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
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
    # Middleware anti-caché agresivo para demostraciones en vivo
    'hms_project.middleware.NoCacheMiddleware',
    'hms_project.middleware.EnvironmentContextMiddleware',
]

ROOT_URLCONF = 'hms_project.urls'

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
                'hms_project.middleware.demo_context_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'hms_project.wsgi.application'

# --- CONFIGURACIÓN DE BASE DE DATOS (SQL SERVER / MSSQL) ---
DB_HOST = os.getenv('DB_HOST')
_default_db_prefix = "hms3" if HMS_ENV == 'prod' else "vhms3"
_default_db = f"{_default_db_prefix}_{HMS_COUNTRY.lower()}"
DB_NAME = os.getenv('DB_NAME', _default_db)
DB_USER = os.getenv('DB_USER', 'sa')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_PORT = os.getenv('DB_PORT', '1433')

if DB_HOST:
    DATABASES = {
        'default': {
            'ENGINE': 'mssql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
            'OPTIONS': {
                'driver': 'ODBC Driver 18 for SQL Server',
                'extra_params': 'TrustServerCertificate=yes;',
            },
        }
    }
else:
    # Modo local offline/dummy para ejecutar migraciones o check en frío sin DB
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'local_dev.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- INTERNACIONALIZACIÓN Y LOCALIZACIÓN ARGENTINA ---
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# --- ARCHIVOS ESTÁTICOS ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise sirve estáticos directamente
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
