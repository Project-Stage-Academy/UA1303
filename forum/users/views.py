import logging
import os

from django.conf import settings
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from djoser.views import UserViewSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from forum import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import APIException
from rest_framework import status, generics
from djoser.views import UserViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import verify_captcha
from .serializers import (
    PasswordResetSerializer,
    LogoutSerializer,
    CustomUserSerializer,
    RoleSerializer,
    GithubAccessTokenSerializer
)

from .models import Role
from .serializers import PasswordResetSerializer, LogoutSerializer, CustomUserSerializer
from .utils import verify_captcha

RATE_LIMIT_KEY = os.getenv("RATE_LIMIT_KEY", "ip")
RATE_LIMIT_RATE = os.getenv("RATE_LIMIT_RATE", "5/m")
RATE_LIMIT_BLOCK = os.getenv("RATE_LIMIT_BLOCK", "True").lower() == "true"

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method="post",
    operation_summary="Password reset with CAPTCHA",
    operation_description="This endpoint allows users to request a password reset with CAPTCHA verification.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(
                type=openapi.TYPE_STRING,
                format="email",
                description="User email address",
            ),
            "g-recaptcha-response": openapi.Schema(
                type=openapi.TYPE_STRING, description="ReCAPTCHA response token"
            ),
        },
        required=["email", "g-recaptcha-response"],
    ),
    responses={
        200: openapi.Response(description="Password reset email sent if email exists."),
        400: openapi.Response(description="Invalid captcha or email format."),
    },
)
@api_view(["POST"])
@ratelimit(key=RATE_LIMIT_KEY, rate=RATE_LIMIT_RATE, block=RATE_LIMIT_BLOCK)
def password_reset_with_captcha(request):
    """
    Temporarily bypass CAPTCHA validation.

    This function handles password reset requests but skips real CAPTCHA validation
    while the frontend is not implemented. When the frontend is ready, the CAPTCHA
    validation should be enabled by ensuring `verify_captcha` is called and not skipped
    in DEBUG mode.

    Steps to update when frontend is connected:
        1. Remove the `if settings.DEBUG` condition.
        2. Always validate the CAPTCHA using `verify_captcha(captcha_response)`.

    A JSON response with the password reset status:
            - {"detail": "Invalid captcha."} (status 400): If the CAPTCHA is invalid.
            - {"detail": "If the email exists, a reset link was sent."} (status 200):
              If the email is valid and a reset link is sent.
            - {"errors": {}} (status 400): If the email is invalid.
    """
    captcha_response = request.data.get("g-recaptcha-response")
    if settings.DEBUG:
        is_captcha_valid = True
    else:
        is_captcha_valid = verify_captcha(captcha_response)

    if not is_captcha_valid:
        return JsonResponse(
            {
                "errors": [
                    {"field": "g-recaptcha-response", "message": "Invalid CAPTCHA."}
                ]
            },
            status=400,
        )

    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        return JsonResponse(
            {"detail": "If the email exists, a reset link was sent."}, status=200
        )

    return JsonResponse(
        {
            "errors": [
                {"field": key, "message": value[0]}
                for key, value in serializer.errors.items()
            ]
        },
        status=400,
    )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout by blacklisting the provided refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Refresh token to be blacklisted',
                    example='your_refresh_token_here',
                ),
            },
            required=['refresh'],
        ),
        responses={
            200: "Logout successful",
            400: "Invalid or missing refresh token",
        }
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            logger.error(f"Validation error: {serializer.errors},  Request Data: {request.data}")
            return Response({"error": "Access denied."}, status=400)

        refresh_token = serializer.validated_data['refresh']

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info("User logged out successfully.")

            return Response({"detail": "Logged out successfully."}, status=200)
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            return Response({"error": "Access denied."}, status=403)


class RegisterUserView(APIView):
    """
    View for user registration
    """

    permission_classes = [AllowAny]

    def post(self, request):

        # Pass the incoming data to the serializer
        logger.info("User registration request received.")
        serializer = CustomUserSerializer(data=request.data)

        # Validate the data
        if serializer.is_valid():
            try:
                user = serializer.save()

                # Return a response with limited user data
                logger.info(
                    f"User successfully registered. User ID: {user.user_id}, Email: {user.email}"
                )

                response_data = {
                    "user_id": user.user_id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.get_role_display(),
                    "created_at": user.created_at,
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

            except APIException as e:
                logger.error(f"API error during signup: {e}")
                raise
            except Exception as e:
                logger.critical(f"Unexpected error during signup: {e}", exc_info=True)
                raise

        # Return validation errors
        logger.warning(
            f"User registration validation failed. Errors: {serializer.errors}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(UserViewSet):
    """Custom endpoint to modify default Djoser's /me endpoint"""
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        token_role_value = self.request.auth.get('role')
        token_role_name = Role(token_role_value).name
        return Response({**serializer.data, 'role_value': token_role_value, 'role_name': token_role_name})


class ChangeRoleView(generics.GenericAPIView):
    """Change role for authenticated user. Generates new JWT with updated role."""
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = serializer.validated_data["role"]
        refresh = RefreshToken.for_user(request.user)
        refresh["role"] = role
        return JsonResponse(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=200,
        )


class GithubAccessTokenView(generics.GenericAPIView):
    """Get GitHub access_token for OAuth"""
    serializer_class = GithubAccessTokenSerializer
    client_id = settings.SOCIAL_AUTH_GITHUB_KEY
    client_secret = settings.SOCIAL_AUTH_GITHUB_SECRET

    def post(self, request):
        code = request.data.get('code')
        redirect_url = request.data.get('redirect_url')

        # Prepare and send request to GitHub
        github_token_url = "https://github.com/login/oauth/access_token"
        headers = {"Accept": "application/json"}
        query_params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": redirect_url,
        }

        try:
            response = requests.post(github_token_url, headers=headers, params=query_params)
            response_data = response.json()

            if "error" in response_data:
                return Response(
                    {"error": response_data},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract the access token and return it
            access_token = response_data.get("access_token")
            if not access_token:
                return Response(
                    {"error": "Access token not found in GitHub response."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response({"github_access_token": access_token}, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response(
                {"error": f"Failed to fetch access token from GitHub: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
