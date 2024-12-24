import os
import requests

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse

import logging
from forum import settings
from .serializers import PasswordResetSerializer, LogoutSerializer

RATE_LIMIT_KEY = os.getenv("RATE_LIMIT_KEY", "ip")
RATE_LIMIT_RATE = os.getenv("RATE_LIMIT_RATE", "5/m")
RATE_LIMIT_BLOCK = os.getenv("RATE_LIMIT_BLOCK", "True").lower() == "true"

logger = logging.getLogger('app')


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
    