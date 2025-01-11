import logging

import jwt
import requests
from django.conf import settings
from rest_framework.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


def get_user_role_from_token(request):
    """
    Decodes the JWT token from the Authorization header and retrieves the user's role

    Args:
        request (HttpRequest): The HTTP request containing the Authorization header

    Returns:
        str: The role of the user extracted from the token

    Raises:
        PermissionDenied: If the token is missing, invalid, or expired
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise PermissionDenied("Token not provided.")

    token = auth_header.split(' ')[1]
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_token.get('role')
    except jwt.ExpiredSignatureError:
        raise PermissionDenied("Token has expired.")
    except jwt.InvalidTokenError:
        raise PermissionDenied("Invalid token.")


def verify_captcha(captcha_response):
    """
    Verifies the CAPTCHA response with Google's reCAPTCHA API.

    Args:
        captcha_response (str): The CAPTCHA response from the client.

    Returns:
        bool: True if CAPTCHA verification succeeds, False otherwise.
    """
    if settings.DEBUG:
        return True

    payload = {
        'secret': settings.RECAPTCHA_PRIVATE_KEY,
        'response': captcha_response,
    }

    try:
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=payload
        )
        result = response.json()
        if result.get('success', False):
            logger.info("CAPTCHA verification succeeded.")
            return True
        else:
            logger.warning("CAPTCHA verification failed. Details: %s", result)
            return False
    except requests.RequestException as e:
        logger.error("Error during CAPTCHA verification: %s", e)
        return False
