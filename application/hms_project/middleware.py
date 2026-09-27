from django.conf import settings
from django.utils import timezone
import os

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


class EnvironmentContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)


def demo_context_processor(request):
    """
    Inyecta metadatos del entorno y la base de datos en todas las plantillas.
    Permite mostrar banners visuales de Producción vs VDB Enmascarada y timestamp exacto.
    """
    from core.i18n import get_country_text
    env_name = getattr(settings, 'HMS_ENV', 'prod')
    country = os.getenv('HMS_COUNTRY', 'AR').upper()
    is_masked = (env_name == 'test')

    return {
        'HMS_ENV': env_name,
        'HMS_COUNTRY': country,
        'IS_MASKED': is_masked,
        'DB_NAME': getattr(settings, 'DB_NAME', f"{('hms3' if env_name == 'prod' else 'vhms3')}_{country.lower()}"),
        'DB_HOST': getattr(settings, 'DB_HOST', 'localhost'),
        'DB_PORT': getattr(settings, 'DB_PORT', '1433'),
        'HOST_PORT': os.getenv('HOST_PORT', '8012' if env_name == 'prod' else '8013'),
        'SERVER_TIMESTAMP': timezone.now().strftime('%H:%M:%S.%f')[:-3],
        'txt': get_country_text(country),
    }
