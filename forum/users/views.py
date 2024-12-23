from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
from .serializers import LogoutSerializer
from rest_framework.permissions import IsAuthenticated


logger = logging.getLogger('app')

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
    
               
            
