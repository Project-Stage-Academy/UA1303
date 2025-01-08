import jwt
from django.conf import settings
from rest_framework.exceptions import PermissionDenied


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
