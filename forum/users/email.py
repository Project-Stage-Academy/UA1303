from djoser import email
from django.conf import settings


class PasswordResetEmail(email.PasswordResetEmail):
    template_name = "email/password_reset.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["domain"] = settings.DOMAIN_NAME
        context["protocol"] = "https" if settings.SECURE_SSL_REDIRECT else "http"
        return context
