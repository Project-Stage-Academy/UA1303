from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django_ratelimit.decorators import ratelimit
from .forms import PasswordResetForm
from django.http import JsonResponse


@ratelimit(key='ip', rate='5/m', block=True)
@api_view(['POST'])
def password_reset_with_captcha(request):
    form = PasswordResetForm(data=request.data)
    if form.is_valid():
        email = form.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            return JsonResponse({"detail": "If the email exists, a reset link was sent."}, status=200)
        return JsonResponse({"detail": "Invalid email."}, status=404)
    return Response(form.errors, status=400)
