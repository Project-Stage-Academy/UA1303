from djoser import email
from django.contrib.sites.shortcuts import get_current_site


class PasswordResetEmail(email.PasswordResetEmail):
    template_name = "email/password_reset.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["domain"] = get_current_site(self.context["request"]).domain
        context["protocol"] = "https" if self.context["request"].is_secure() else "http"
        return context
