import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


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
