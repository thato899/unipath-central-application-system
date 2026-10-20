import base64
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.http import require_http_methods, require_POST
from django_otp import login as otp_login
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.forms import OTPAuthenticationForm
from django_otp.views import LoginView as OTPLoginView
from .models import DataConsent

User = get_user_model()

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Email address", widget=forms.EmailInput(attrs={"autocomplete": "email", "required": True}))
    consent = forms.BooleanField(label="I have read the privacy notice and agree to the stated use of my profile for this demo.", required=True)

    class Meta:
        model = User
        fields = ("email",)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("An account already exists for this email address.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class RegisterView(View):
    template_name = "auth/register.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("totp_setup" if not request.user.is_verified() else "home")
        return render(request, self.template_name, {"form": RegistrationForm()})

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form}, status=400)
        user = form.save()
        DataConsent.objects.create(user=user, policy_version=settings.DATA_POLICY_VERSION, purpose="account_and_application_demo")
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("totp_setup")

class EmailOTPAuthenticationForm(OTPAuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email address"
        self.fields["username"].widget.attrs.update({"type": "email", "autocomplete": "username", "required": True})

class SecureLoginView(OTPLoginView):
    template_name = "auth/login.html"
    authentication_form = EmailOTPAuthenticationForm

@require_http_methods(["GET", "POST"])
def setup_totp(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.user.is_verified():
        return redirect("home")
    if TOTPDevice.objects.filter(user=request.user, confirmed=True).exists():
        logout(request)
        messages.info(request, "Sign in with your password and authenticator code.")
        return redirect("login")
    device = TOTPDevice.objects.filter(user=request.user, confirmed=False).first()
    if device is None:
        device = TOTPDevice.objects.create(user=request.user, name="Authenticator", confirmed=False)
    raw_key = bytes.fromhex(device.key)
    secret = base64.b32encode(raw_key).decode("ascii").rstrip("=")
    if request.method == "POST":
        token = request.POST.get("token", "").strip()
        if device.verify_token(token):
            device.confirmed = True
            device.save(update_fields=["confirmed"])
            otp_login(request, device)
            messages.success(request, "Two-factor authentication is enabled.")
            return redirect("home")
        messages.error(request, "That authenticator code was not accepted. Check the code and try again.")
    return render(request, "auth/totp_setup.html", {"secret": secret, "config_url": device.config_url})

@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")
