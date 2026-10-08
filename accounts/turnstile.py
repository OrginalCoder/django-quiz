import os
import requests
from django.conf import settings

def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def verify_turnstile(token, remote_ip=None):
    if getattr(settings, 'TESTING', False):
        return True
    secret_key = os.environ.get('CLOUDFLARE_TURNSTILE_SECRET_KEY', '')
    if not secret_key:
        return True
    if not token:
        return False
    data = {
        'secret': secret_key,
        'response': token,
    }
    if remote_ip:
        data['remoteip'] = remote_ip
    try:
        response = requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data=data,
            timeout=5
        )
        return bool(response.json().get('success'))
    except Exception:
        return True
