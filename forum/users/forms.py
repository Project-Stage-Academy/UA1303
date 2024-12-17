from django import forms
from captcha.fields import ReCaptchaField


class PasswordResetForm(forms.Form):
    email = forms.EmailField()
    captcha = ReCaptchaField()
