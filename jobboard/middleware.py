
import time
import logging

logger = logging.getLogger(__name__)


class RequestLoggerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # capture start time before the view runs
        start_time = time.time()

        # pass request to the next layer
        response = self.get_response(request)

        # calculate duration after the view has run
        duration_ms = (time.time() - start_time) * 1000

        # log the request details
        logger.info(
            f'{request.method} {request.path} '
            f'→ {response.status_code} '
            f'[{duration_ms:.2f}ms] '
            f'user={request.user}'
        )

        return response
    


class MaintenanceModeMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.conf import settings
        from django.http import JsonResponse

        # check a setting in settings.py
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # allow admin through even during maintenance
            if not request.path.startswith('/admin/'):
                return JsonResponse(
                    {
                        'error': 'Service temporarily unavailable.',
                        'message': 'We are performing maintenance. Back soon.'
                    },
                    status=503
                )

        return self.get_response(request)
    


class RoleAuditMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    # API paths that require authentication
    PROTECTED_PREFIXES = [
        '/api/v1/jobs/',
        '/api/v1/accounts/',
        '/api/v1/applications/',
    ]

    def __call__(self, request):
        response = self.get_response(request)

        # only log API requests
        is_api = any(
            request.path.startswith(prefix)
            for prefix in self.PROTECTED_PREFIXES
        )

        if is_api:
            user = request.user
            role = user.role if user.is_authenticated else 'anonymous'

            logger.info(
                f'AUDIT | {role} | {request.method} {request.path} '
                f'| status={response.status_code}'
            )

        return response
    


import json
import traceback

class JsonExceptionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # process_exception is called when a view raises an exception
        # return None to let Django handle it normally
        # return a response to handle it yourself

        from django.conf import settings
        from django.http import JsonResponse

        # only handle API requests
        if not request.path.startswith('/api/'):
            return None

        logger.error(
            f'Unhandled exception on {request.path}: {exception}',
            exc_info=True
        )

        # in debug mode show the traceback
        if settings.DEBUG:
            return JsonResponse({
                'error': str(exception),
                'traceback': traceback.format_exc(),
            }, status=500)

        # in production hide the details
        return JsonResponse(
            {'error': 'An unexpected error occurred.'},
            status=500
        )
    


