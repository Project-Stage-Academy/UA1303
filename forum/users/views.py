import os
import requests

from rest_framework.decorators import api_view
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse

from forum.forum import settings
from forum.users.serializers import PasswordResetSerializer

RATE_LIMIT_KEY = os.getenv("RATE_LIMIT_KEY", "ip")
RATE_LIMIT_RATE = os.getenv("RATE_LIMIT_RATE", "5/m")
RATE_LIMIT_BLOCK = os.getenv("RATE_LIMIT_BLOCK", "True").lower() == "true"


def verify_captcha(captcha_response):
    payload = {'secret': settings.RECAPTCHA_PRIVATE_KEY, 'response': captcha_response}
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
    return r.json().get('success', False)


@ratelimit(key=RATE_LIMIT_KEY, rate=RATE_LIMIT_RATE, block=RATE_LIMIT_BLOCK)
@api_view(['POST'])
def password_reset_with_captcha(request):
    captcha_response = request.data.get('g-recaptcha-response')
    if not verify_captcha(captcha_response):
        return JsonResponse({"detail": "Invalid captcha."}, status=400)

    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        return JsonResponse({"detail": "If the email exists, a reset link was sent."}, status=200)
    return JsonResponse({"errors": serializer.errors}, status=400)
