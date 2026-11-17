"""
Django settings for hms3 (Hospital Management System - Argentina & Delphix Demo)
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# --- CONFIGURACIÓN DE ENTORNO Y SEGURIDAD ---
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'hms3-default-development-secret-key-replace-in-env')
# DEBUG apagado por defecto: en una demo no queremos tracebacks en pantalla.
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

allowed_hosts_raw = os.getenv('ALLOWED_HOSTS', '*')
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_raw.split(',') if h.strip()] or ['*']

# Identificador de entorno ('prod' o 'test') y país ('AR', 'BR' o 'US').
# Se validan acá, una sola vez: el resto del código lee settings.HMS_ENV y
# settings.HMS_COUNTRY. Un valor inválido corta el arranque con un mensaje claro
# en lugar de caer en silencio al modelo de Argentina.
HMS_ENV = os.getenv('HMS_ENV', 'prod').strip().lower()
if HMS_ENV not in ('prod', 'test'):
    raise ImproperlyConfigured(f"HMS_ENV inválido: '{HMS_ENV}'. Valores permitidos: prod, test.")

HMS_COUNTRY = os.getenv('HMS_COUNTRY', 'AR').strip().upper()
if HMS_COUNTRY not in ('AR', 'BR', 'US'):
    raise ImproperlyConfigured(f"HMS_COUNTRY inválido: '{HMS_COUNTRY}'. Valores permitidos: AR, BR, US.")

# Commit con el que se construyó la imagen (lo carga hms-ctl.py build).
HMS_BUILD = os.getenv('HMS_BUILD', 'dev')
HOST_PORT = os.getenv('HOST_PORT', '8012' if HMS_ENV == 'prod' else '8013')

# --- AISLAMIENTO DE COOKIES ---
# Esto previene que al abrir Producción (8012) y Test (8013) en el mismo navegador,
# las cookies se pisen entre sí.
CSRF_COOKIE_NAME = f'hms3_csrf_{HMS_ENV}'

# Application definition
# La demo no usa admin, usuarios ni sesiones: no se instalan, así no dependen de
# tablas (auth_user, django_session) que los seeders no crean.
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Middleware anti-caché agresivo para demostraciones en vivo
    'hms_project.middleware.NoCacheMiddleware',
    # Base caída o sin seed: página amable con reintento en vez de un traceback
    'hms_project.middleware.DatabaseUnavailableMiddleware',
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
                'hms_project.middleware.demo_context_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'hms_project.wsgi.application'

# --- MIGRATIONS ---
# El schema de core (ESPECIALIDADES, MEDICOS, PACIENTES y equivalentes BR/US)
# lo crean los seeders (seed_argentina, seed_brazil, seed_usa), no Django.
# Con None, makemigrations/migrate no generan ni aplican migrations de core;
# los modelos además tienen managed = False.
MIGRATION_MODULES = {'core': None}

# --- CONFIGURACIÓN DE BASE DE DATOS (SQL SERVER / MSSQL) ---
DB_HOST = os.getenv('DB_HOST', '').strip()
_default_db_prefix = "hms3" if HMS_ENV == 'prod' else "vhms3"
_default_db = f"{_default_db_prefix}_{HMS_COUNTRY.lower()}"
DB_NAME = os.getenv('DB_NAME', _default_db)
DB_USER = os.getenv('DB_USER', 'sa')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_PORT = os.getenv('DB_PORT', '1433')
# Timeouts en segundos. Sin ellos, una base que no responde (por ejemplo una VDB
# en pleno refresh) deja colgados a los workers de gunicorn.
DB_CONNECT_TIMEOUT = int(os.getenv('DB_CONNECT_TIMEOUT', '5'))
DB_QUERY_TIMEOUT = int(os.getenv('DB_QUERY_TIMEOUT', '30'))

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
                'connection_timeout': DB_CONNECT_TIMEOUT,
                'query_timeout': DB_QUERY_TIMEOUT,
            },
        }
    }
elif os.getenv('HMS_ALLOW_SQLITE', '').lower() in ('true', '1', 't'):
    # Modo local sin SQL Server: solo para check, collectstatic y los smoke tests.
    DB_HOST = 'sqlite'
    DB_NAME = 'local_dev.sqlite3'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'local_dev.sqlite3',
        }
    }
else:
    raise ImproperlyConfigured(
        "Falta DB_HOST: no hay base de datos configurada. Revisá el archivo .env del "
        "contenedor (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD). Para correr sin SQL Server "
        "(check, collectstatic, tests) definí HMS_ALLOW_SQLITE=1."
    )

# --- INTERNACIONALIZACIÓN Y LOCALIZACIÓN ARGENTINA ---
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# --- ARCHIVOS ESTÁTICOS ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise sirve estáticos directamente (Bootstrap y Font Awesome están
# copiados en static/vendor: la demo no necesita internet).
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}
# Sirve también desde STATICFILES_DIRS, por si no se corrió collectstatic.
WHITENOISE_USE_FINDERS = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
