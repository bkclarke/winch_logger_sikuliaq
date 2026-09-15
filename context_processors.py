from django.contrib.auth.models import User
from wwdb.models import Cast

def cast_context(request):
    return {'last': Cast.objects.last()}

import subprocess


SERVICES = [
    'mysql',
    'nginx',
    'gunicorn',
    'listen_write.service',
]


def check_service_status(service_name):
    """
    Return True if the systemd service is currently active.
    Return False if it is stopped, failed, missing, or cannot be checked.
    """
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', '--quiet', service_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception:
        return False


def service_status(request):
    """
    Make service status available to all templates.
    """
    service_errors = []

    for service_name in SERVICES:
        if not check_service_status(service_name):
            # Remove .service from the display name
            display_name = service_name.removesuffix('.service')
            service_errors.append(display_name)

    return {
        'service_errors': service_errors,
    }