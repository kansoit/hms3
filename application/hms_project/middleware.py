import logging

from django.conf import settings
from django.db import Error as DatabaseError
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

logger = logging.getLogger(__name__)


class NoCacheMiddleware:
    """
    Middleware estricto para evitar cualquier almacenamiento en caché del navegador.
    Indispensable para demostraciones en vivo de Delphix Continuous Compliance.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # No modificamos estáticos administrados por whitenoise
        if request.path.startswith(settings.STATIC_URL):
            return response

        # Cabeceras anti-caché universales compatibles con HTTP/1.1 y HTTP/1.0
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, post-check=0, pre-check=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        response['X-Accel-Expires'] = '0'
        return response


class DatabaseUnavailableMiddleware:
    """
    Si una vista falla por la base de datos (SQL Server caído, VDB en pleno
    refresh/rewind, tablas sin crear), responde 503 con una página que reintenta
    sola, o con JSON para /api/. Evita mostrar un traceback en plena demo.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if not isinstance(exception, DatabaseError):
            return None
        logger.error("Base de datos no disponible en %s: %s", request.path, exception)
        if request.path.startswith('/api/'):
            return JsonResponse({
                'status': 'error',
                'message': 'Database not available.',
            }, status=503)
        return render(request, 'db_unavailable.html', status=503)


def demo_context_processor(request):
    """
    Inyecta metadatos del entorno y la base de datos en todas las plantillas.
    Permite mostrar banners visuales de Producción vs VDB Enmascarada y timestamp exacto.
    """
    from core.i18n import get_country_text
    return {
        'HMS_ENV': settings.HMS_ENV,
        'HMS_COUNTRY': settings.HMS_COUNTRY,
        'HMS_BUILD': settings.HMS_BUILD,
        'IS_MASKED': settings.HMS_ENV == 'test',
        'DB_NAME': settings.DB_NAME,
        'DB_HOST': settings.DB_HOST,
        'DB_PORT': settings.DB_PORT,
        'HOST_PORT': settings.HOST_PORT,
        'SERVER_TIMESTAMP': timezone.now().strftime('%H:%M:%S.%f')[:-3],
        'txt': get_country_text(),
    }
