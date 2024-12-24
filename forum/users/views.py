import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)

class RegisterUserView(APIView):
    """
    View for user registration.
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
                        f"User successfully registered. User ID: {user.user_id}, Email: {user.email}")
                
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